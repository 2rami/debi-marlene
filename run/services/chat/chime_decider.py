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

# "데비:" / "마를렌:" 같은 이름표 prefix 제거용.
# haiku judge가 프롬프트 지시 무시하고 prefix 붙이는 케이스 방어.
_PERSONA_PREFIX_RE = re.compile(r"^\s*(?:데비|마를렌)\s*:\s*", re.IGNORECASE)

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 8.0
MAX_BOT_STREAK = 3
DECAY_PROBS = [0.40, 0.20, 0.08, 0.0]  # index = bot_streak 직전 값

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
    ) -> Optional[str]:
        """게이트 통과 시 대사 문자열 반환, 아니면 None."""
        st = self._state.setdefault(self._key(guild_id, channel_id), _ChannelState())
        now = time.time()

        # 게이트 1: 쿨다운
        if now - st.last_chime_ts < COOLDOWN_SECONDS:
            remain = COOLDOWN_SECONDS - (now - st.last_chime_ts)
            print(f"[CHIME:{self.identity}] skip cooldown (remain={remain:.1f}s)", flush=True)
            return None

        # 게이트 2: 봇 연속 발화 하드캡
        if st.bot_streak >= MAX_BOT_STREAK:
            print(f"[CHIME:{self.identity}] skip streak_cap (streak={st.bot_streak})", flush=True)
            return None

        # 게이트 3: decaying 확률
        idx = min(max(st.bot_streak, 0), len(DECAY_PROBS) - 1)
        prob = DECAY_PROBS[idx]
        roll = random.random()
        if prob <= 0 or roll > prob:
            print(
                f"[CHIME:{self.identity}] skip prob (streak={st.bot_streak} prob={prob:.2f} roll={roll:.2f})",
                flush=True,
            )
            return None

        print(
            f"[CHIME:{self.identity}] gates passed → judge (streak={st.bot_streak} prob={prob:.2f} roll={roll:.2f})",
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
            "- 끼어들 맥락이면: 1문장으로 짧게 대사만 출력 (캐릭터 이름 prefix 붙이지 마)",
            "- 어색하거나 관심 없으면: 'SKIP' 한 단어만 출력",
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
        if text:
            # 프롬프트에 "prefix 붙이지 마"라고 해도 haiku가 종종 "데비:" 붙여서 응답.
            # 방어적으로 앞쪽 이름표만 제거 (한 번).
            text = _PERSONA_PREFIX_RE.sub("", text, count=1).strip()
        return text or None
