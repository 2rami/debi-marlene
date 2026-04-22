"""ChimeInDecider — 솔로봇이 다른 봇/유저 대화에 끼어들지 판단.

하이브리드 게이트 (싼 것부터):
    1. 쿨다운 (COOLDOWN_SECONDS 이내 재진입 금지)
    2. 봇 연속 발화 캡 (유저 발화 이후 봇 턴이 MAX_BOT_STREAK 넘으면 스킵)
    3. decaying 확률 (첫 기회 40% → 점차 감소)
    4. Claude judge (실제로 끼어들지 + 한 줄 대사 생성)

채널 단위 상태. guild+channel을 키로 사용. 유저 발화 시 bot_streak=0 리셋.
"""

import asyncio
import logging
import random
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import anthropic

# "데비:" / "마를렌:" / "데비야:" / "마를렌아:" 같은 이름표·호격 prefix 제거용.
# haiku judge가 프롬프트 지시 무시하고 자기 이름 + 호격조사(야/나/아) + 콜론 붙이는 케이스까지 방어.
_PERSONA_PREFIX_RE = re.compile(
    r"^\s*(?:데비|마를렌)(?:야|나|아)?\s*:\s*",
    re.IGNORECASE,
)

# judge가 "1인칭 대사"가 아니라 "3인칭 추론 서술"을 뱉는 케이스 탐지.
# 예: "데비가 자랑하고 있고, momewomo가 사랑한다고 한 상황이네..."
# 예: "마를렌이 냉소적으로 끼어들기 좋은 타이밍이야"
# 이런 패턴이 발견되면 대사로 간주하지 않고 SKIP 처리.
_THIRD_PERSON_SELFREF_RE = re.compile(
    r"(?:데비|마를렌)(?:가|이|은|는|의)\s+"
    r"(?:말했|끼어들|반응|응답|판단|생각|출력|대답|느낌|상황|분위기|타이밍|순간)",
)
# 내러티브 종결 어미 ("~상황이네", "~타이밍이야", "~것 같아") — 3인칭 해설 티
_NARRATIVE_TAIL_RE = re.compile(
    r"(?:상황이네|타이밍이야|분위기야|것\s*같아|것\s*같은데|끼어들(?:어|기)\s*좋은)",
)

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 8.0
MAX_BOT_STREAK = 3
DECAY_PROBS = [0.40, 0.20, 0.08, 0.0]  # index = bot_streak 직전 값

# 3단계 확률 구조 (지정 채널 내에서 메시지 성격에 따라 분기):
#
#   1. KEYWORD — "데비야/마를렌아" 같은 호명 키워드 포함 → 거의 확실히 답
#   2. QUESTION — 의문형 ('?', '궁금', '어때', '왜', '뭐야' 등) → 중간 확률
#   3. RELAXED — 그 외 일반 채팅 → 아주 드물게
#
# 값이 낮을수록 조용한 봇. streak별로 감쇠해서 연속 발화 억제.

RELAXED_COOLDOWN_SECONDS = 15.0
RELAXED_PROBS = [0.10, 0.05, 0.02, 0.0]

QUESTION_COOLDOWN_SECONDS = 6.0
QUESTION_PROBS = [0.45, 0.25, 0.12, 0.05]

KEYWORD_COOLDOWN_SECONDS = 2.0
KEYWORD_PROBS = [0.98, 0.95, 0.85, 0.70]

# 키워드 매칭용 정규식 — identity별로 분리. "뎁마"는 둘 다 반응 (공동 호칭).
_DEBI_WORDS = ["데비야", "데비나", "데비아", "데비", "뎁마야", "뎁마아", "뎁마나", "뎁마"]
_MARLENE_WORDS = ["마를렌아", "마를렌야", "마를렌나", "마를렌", "뎁마야", "뎁마아", "뎁마나", "뎁마"]
_UNIFIED_WORDS = _DEBI_WORDS + _MARLENE_WORDS

_TRIGGER_RES = {
    "debi": re.compile("|".join(re.escape(w) for w in _DEBI_WORDS)),
    "marlene": re.compile("|".join(re.escape(w) for w in _MARLENE_WORDS)),
    "unified": re.compile("|".join(re.escape(w) for w in _UNIFIED_WORDS)),
}

# 질문 감지 정규식: 의문 부호 또는 의문형 어휘.
_QUESTION_RE = re.compile(
    r"[?？]|"
    r"궁금|알려줘|알려줄래|어때|어떠|뭐야|뭔데|몰라|모르겠|"
    r"왜\s|어떻게|언제|어디|누구|어느|얼마나|무슨"
)


def has_keyword(text: str, identity: str = "unified") -> bool:
    """메시지에 **해당 identity용** 봇 호명 키워드 포함 여부.

    - identity='debi': '데비야/데비' 등만 True (마를렌 호명은 무시)
    - identity='marlene': '마를렌아/마를렌' 등만 True (데비 호명은 무시)
    - identity='unified': 전부 True
    - '뎁마'는 debi/marlene 둘 다 True (공동 호칭)
    """
    pattern = _TRIGGER_RES.get(identity, _TRIGGER_RES["unified"])
    return bool(pattern.search(text or ""))


def is_question(text: str) -> bool:
    """메시지가 질문 성격(? 또는 의문형 어휘)인지 판별."""
    return bool(_QUESTION_RE.search(text or ""))

JUDGE_MODEL = "claude-haiku-4-5-20251001"
JUDGE_MAX_TOKENS = 120

_PERSONA_BRIEF = {
    "debi": "너는 데비야. 활발하고 직설적인 10대 소녀 말투. 친근하게 끼어들어.",
    "marlene": "너는 마를렌이야. 냉소적이고 짧게 말하는 10대 소녀. '...' 자주 써. 무심한 듯 끼어들어.",
}


@dataclass
class _ChannelState:
    last_chime_ts: float = 0.0
    bot_streak: int = 0  # 유저 발화 이후 누적된 봇 메시지 수 (누구든)


class ChimeInDecider:
    """솔로봇용. 프로세스당 1개 인스턴스. 내부 상태는 (guild_id, channel_id) 키."""

    def __init__(self, identity: str, anthropic_client: anthropic.AsyncAnthropic):
        self.identity = identity
        self._client = anthropic_client
        self._state: dict[tuple, _ChannelState] = {}
        self._persona_brief = _PERSONA_BRIEF.get(identity, "")

    def _key(self, guild_id, channel_id) -> tuple:
        return (str(guild_id or "dm"), str(channel_id))

    def on_user_message(self, guild_id, channel_id) -> None:
        """유저 발화 시 봇 streak 리셋."""
        st = self._state.setdefault(self._key(guild_id, channel_id), _ChannelState())
        st.bot_streak = 0

    def on_bot_message(self, guild_id, channel_id) -> None:
        """다른 봇/자기 봇 메시지 감지 시 streak 증가 (chime 판단 여부와 무관)."""
        st = self._state.setdefault(self._key(guild_id, channel_id), _ChannelState())
        st.bot_streak += 1

    async def maybe_chime(
        self,
        guild_id,
        channel_id,
        recent_context: list[str],
        triggering_author: str,
        relaxed: bool = False,
        keyword_hit: bool = False,
        question_hit: bool = False,
    ) -> Optional[str]:
        """게이트 통과 시 대사 문자열 반환, 아니면 None.

        우선순위: keyword_hit > question_hit > relaxed > normal
        - keyword_hit: 호명 키워드 ('데비야' 등) — 거의 확실히 답
        - question_hit: 의문형 메시지 (?, 궁금, 어때 등) — 중간 확률
        - relaxed: 지정 채널 일반 채팅 — 드물게
        - 그 외: 비지정 채널 폴백 (현재 설계에선 호출 안 됨)
        """
        st = self._state.setdefault(self._key(guild_id, channel_id), _ChannelState())
        now = time.time()

        if keyword_hit:
            cooldown = KEYWORD_COOLDOWN_SECONDS
            probs = KEYWORD_PROBS
            mode = "keyword"
        elif question_hit:
            cooldown = QUESTION_COOLDOWN_SECONDS
            probs = QUESTION_PROBS
            mode = "question"
        elif relaxed:
            cooldown = RELAXED_COOLDOWN_SECONDS
            probs = RELAXED_PROBS
            mode = "relaxed"
        else:
            cooldown = COOLDOWN_SECONDS
            probs = DECAY_PROBS
            mode = "normal"

        # 게이트 1: 쿨다운
        if now - st.last_chime_ts < cooldown:
            remain = cooldown - (now - st.last_chime_ts)
            print(f"[CHIME:{self.identity}:{mode}] skip cooldown (remain={remain:.1f}s)", flush=True)
            return None

        # 게이트 2: 봇 연속 발화 하드캡 (relaxed에서도 안전장치 유지)
        if st.bot_streak >= MAX_BOT_STREAK:
            print(f"[CHIME:{self.identity}:{mode}] skip streak_cap (streak={st.bot_streak})", flush=True)
            return None

        # 게이트 3: decaying 확률
        idx = min(max(st.bot_streak, 0), len(probs) - 1)
        prob = probs[idx]
        roll = random.random()
        if prob <= 0 or roll > prob:
            print(
                f"[CHIME:{self.identity}:{mode}] skip prob (streak={st.bot_streak} prob={prob:.2f} roll={roll:.2f})",
                flush=True,
            )
            return None

        print(
            f"[CHIME:{self.identity}:{mode}] gates passed → judge (streak={st.bot_streak} prob={prob:.2f} roll={roll:.2f})",
            flush=True,
        )

        # 게이트 4: Claude judge (가장 비쌈 — 여기까지 온 경우만)
        reply = await self._judge(recent_context, triggering_author)
        if not reply or reply.strip().upper().startswith("SKIP"):
            print(f"[CHIME:{self.identity}] judge SKIP: {reply!r}", flush=True)
            return None

        print(f"[CHIME:{self.identity}] judge FIRE: {reply[:80]!r}", flush=True)
        st.last_chime_ts = now
        st.bot_streak += 1  # 내가 곧 발화할 것
        return reply.strip()

    async def _judge(self, recent_context: list[str], triggering_author: str) -> Optional[str]:
        prompt_lines = [
            "[최근 대화]",
            *recent_context,
            "",
            f"[방금 '{triggering_author}'이(가) 말함]",
            "",
            "여기에 네가 자연스럽게 한마디 끼어들 만한 상황이야?",
            "",
            "출력 규칙 (엄격):",
            "- 끼어들 맥락이면: 네가 하는 **1인칭 대사 한 줄**만 써. 따옴표도 붙이지 마.",
            "  예시 (데비): 어 그거 나도 해봤어 ㅋㅋ",
            "  예시 (마를렌): ...그런 거 뻔하지.",
            "- 어색하거나 관심 없으면: 'SKIP' 한 단어만 써.",
            "",
            "절대 금지:",
            "- 너 자신을 3인칭으로 부르지 마. '데비가 ~', '마를렌이 ~' 이런 거 금지.",
            "- 상황 해설/판단 서술 금지. '~상황이네', '~타이밍이야', '~것 같아' 같은 메타 설명 금지.",
            "- 생각 과정을 적지 마. 바로 대사 또는 SKIP만 출력해.",
            "- 캐릭터 이름 접두사('데비:', '마를렌:', '데비야:', '마를렌아:') 금지.",
        ]
        try:
            resp = await asyncio.wait_for(
                self._client.messages.create(
                    model=JUDGE_MODEL,
                    max_tokens=JUDGE_MAX_TOKENS,
                    system=self._persona_brief,
                    messages=[{"role": "user", "content": "\n".join(prompt_lines)}],
                ),
                timeout=8.0,
            )
        except asyncio.TimeoutError:
            logger.warning("chime judge 타임아웃 — 스킵")
            return None
        except Exception as e:
            logger.warning("chime judge 실패: %s", e)
            return None

        parts = getattr(resp, "content", []) or []
        text = "".join(getattr(b, "text", "") for b in parts).strip()
        if not text:
            return None

        # 프롬프트에 "prefix 붙이지 마"라고 해도 haiku가 종종 "데비:" / "데비야:" 붙여서 응답.
        # 방어적으로 앞쪽 이름표·호격 prefix 제거 (한 번).
        text = _PERSONA_PREFIX_RE.sub("", text, count=1).strip()

        if not text:
            return None

        # judge가 대사 대신 "3인칭 추론 서술"을 뱉은 케이스 방어.
        # 예: "데비가 자랑하고 있고 ... 마를렌이 끼어들기 좋은 타이밍이야"
        # 이런 응답은 사용자에게 노출되면 안 되므로 SKIP으로 변환.
        if _THIRD_PERSON_SELFREF_RE.search(text) or _NARRATIVE_TAIL_RE.search(text):
            logger.info(
                "chime judge: narrative/3rd-person selfref detected, 강제 SKIP: %r",
                text[:120],
            )
            return "SKIP"

        return text
