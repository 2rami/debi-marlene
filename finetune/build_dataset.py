"""
데비&마를렌 파인튜닝 데이터셋 생성 스크립트

소스:
1. 나무위키 대사 (화자 구분 + 상황별 분류)
2. TTS JSONL (화자 확정 + 파일명 카테고리)
3. 나무위키 배경/성격 정보
4. VLM 아이템 데이터 (게임 지식)

출력: LLaMA-Factory용 JSON (Qwen2.5-Omni Thinker 파인튜닝)
"""

import json
import re
import random
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

random.seed(42)

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "raw_data"
OUTPUT_DIR = BASE_DIR / "dataset"
OUTPUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# 1. 나무위키 대사 파싱
# ─────────────────────────────────────────────

# 상황 카테고리 → 한국어 매핑 (행동 분류)
SITUATION_LABELS = {
    "로비": "로비",
    "선택 시": "캐릭터 선택",
    "실험 시작": "게임 시작",
    "하이퍼루프 이용": "이동",
    "하이퍼 루프 이용": "이동",
    "아군에게 하이퍼루프": "팀 지원",
    "보안 콘솔 이용": "탐색",
    "트랩 설치": "전략",
    "휴식": "휴식",
    "해킹 시도": "해킹",
    "농담": "도발",
    "감정 표현": "감정",
    "첫 킬": "처치",
    "멀티킬": "처치",
    "처치 지원": "처치",
    "금지구역 이동": "금지구역",
    "금지구역 알림": "금지구역",
    "아군 처치됨": "아군 사망",
    "제작 관련": "제작",
    "소생 시작": "소생",
    "소생 성공": "소생",
    "부활 성공": "부활",
    "점령장치 점령": "점령",
    "원격드론 호출": "드론",
    "필요한 아이템 요청": "아이템",
    # 지역
    "골목길": "골목길 이동",
    "양궁장": "양궁장 이동",
    "묘지": "묘지 이동",
    "성당": "성당 이동",
    "공장": "공장 이동",
    "소방서": "소방서 이동",
    "숲": "숲 이동",
    "주유소": "주유소 이동",
    "항구": "항구 이동",
    "병원": "병원 이동",
    "호텔": "호텔 이동",
    "경찰서": "경찰서 이동",
    "학교": "학교 이동",
    "연못": "연못 이동",
    "모래사장": "모래사장 이동",
    "고급 주택가": "고급 주택가 이동",
    "번화가": "번화가 이동",
    "연구소": "연구소 이동",
    # 전투
    "교전": "전투",
    "킬": "처치",
    "적 처치": "처치",
    "아군 처치됨": "아군 사망",
    "사망": "사망",
    "최종 금지구역": "최종 구역",
    "승리": "승리",
    "패배": "패배",
    # 감정
    "도발": "도발",
    "감사": "감사",
    # 제작
    "고급 아이템 제작": "제작",
    "영웅 아이템 제작": "제작",
    "전설 아이템 제작": "제작",
}

# 상황 카테고리로 인식할 키워드들
CATEGORY_KEYWORDS = set(SITUATION_LABELS.keys()) | {
    "지역", "행동", "전투", "제작", "감정표현", "제작 관련",
    "상호 대사", "적 처치 시", "아군 처치 시", "사망 시",
    "공격", "Q 스킬 시전", "W 스킬 시전", "E 스킬 시전", "R 스킬 시전",
    "무기 스킬 습득", "처치", "교전",
    "1명 처치 시", "2명 처치 시", "3명 처치 시", "4명 처치 시", "5명 처치 시",
    "상위권", "하위권", "1등", "2등", "꼴등",
    "꽃 채집", "고기 채집", "감자 채집", "물 채집",
    "고급 등급 아이템 제작", "영웅 등급 아이템 제작",
    "전설 등급 아이템 제작", "초월 등급 아이템 제작",
    "고급 아이템 제작", "영웅 아이템 제작", "전설 아이템 제작",
    "선택 시", "실험 시작",
    "적 처치", "아군 처치됨",
}

# 메타데이터 라인 (무시할 것들)
SKIP_PATTERNS = {
    "[편집]", "파란색", "빨간색", "으로 표기.", "데비의 대사는",
    "마를렌의 대사는", "[더미]", "(대사 1)", "(대사 2)",
    "데비", "마를렌",  # 섹션 제목으로 쓰일 때
    "행동", "지역", "전투", "제작", "교전", "킬",
    # 하위 카테고리 헤더들
    "공격", "Q 스킬 시전", "W 스킬 시전", "E 스킬 시전", "R 스킬 시전",
    "[목소리]", "무기 스킬 습득", "양손검 - 빗겨 흘리기",
    "1명 처치 시", "2명 처치 시", "3명 처치 시", "4명 처치 시", "5명 처치 시",
    "상위권", "하위권", "1등", "2등", "꼴등",
    "꽃 채집", "고기 채집", "감자 채집", "물 채집",
    "고급 등급 아이템 제작", "영웅 등급 아이템 제작",
    "전설 등급 아이템 제작", "초월 등급 아이템 제작",
}


def parse_namuwiki_quotes(filepath: str) -> List[Dict]:
    """나무위키에서 대사를 파싱해서 (speaker, text, situation, skin) 리스트로 반환"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    results = []
    current_skin = "기본"
    current_section = ""  # 데비/마를렌 개별 섹션인지
    current_situation = ""
    in_quotes = False
    line_index_in_situation = 0

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue

        # 대사 섹션 시작 감지
        if "실험체 대사" in line and "스파클링" not in line and "방과" not in line:
            in_quotes = True
            current_skin = "기본"
            current_section = ""
            continue
        if "스파클링 트윈즈 데비&마를렌 대사" in line:
            in_quotes = True
            current_skin = "스파클링 트윈즈"
            current_section = ""
            continue
        if "방과 후 자유시간 데비&마를렌 대사" in line:
            in_quotes = True
            current_skin = "방과 후 자유시간"
            current_section = ""
            continue
        if "아나운서 대사" in line:
            in_quotes = True
            current_skin = "아나운서"
            current_section = ""
            continue

        if not in_quotes:
            continue

        # 섹션 번호 (9.1.1. 등) 감지
        if re.match(r"^\d+\.\d+", line):
            continue

        # 개별 캐릭터 섹션 감지
        if line == "데비" and i + 1 < len(lines) and "[편집]" in lines[i + 1]:
            current_section = "debi"
            continue
        if line == "마를렌" and i + 1 < len(lines) and "[편집]" in lines[i + 1]:
            current_section = "marlene"
            continue

        # 메타 라인 스킵
        if line in SKIP_PATTERNS:
            continue
        if line.startswith("[") and line.endswith("]"):
            continue

        # 새로운 대사 섹션 끝 감지 (다른 큰 섹션으로 넘어갈 때)
        if re.match(r"^\d+\.$", line):
            # "10." 같은 새 대제목 → 대사 영역 종료 가능
            # 단, "9.1." 같은 건 스킨 하위섹션이라 계속
            if not re.match(r"^9\.", line):
                in_quotes = False
                continue

        # 상황 카테고리 감지
        is_category = False
        for keyword in CATEGORY_KEYWORDS:
            if line == keyword or line.startswith(keyword + " "):
                current_situation = SITUATION_LABELS.get(line, line)
                line_index_in_situation = 0
                is_category = True
                break
        # 지역명 감지 (한글 2-5글자 + 다음줄이 대사)
        if not is_category and line in SITUATION_LABELS:
            current_situation = SITUATION_LABELS[line]
            line_index_in_situation = 0
            is_category = True

        if is_category:
            continue

        # 대사 라인
        if len(line) < 2:
            continue

        # 화자 결정
        if current_skin == "기본" and current_section == "":
            # 기본 스킨: 홀수줄=데비, 짝수줄=마를렌 (각 상황 내에서)
            speaker = "debi" if line_index_in_situation % 2 == 0 else "marlene"
        elif current_section == "debi":
            # 데비 개별 섹션: 홀수=데비, 짝수=마를렌(응답)
            speaker = "debi" if line_index_in_situation % 2 == 0 else "marlene"
        elif current_section == "marlene":
            speaker = "marlene" if line_index_in_situation % 2 == 0 else "debi"
        elif current_skin == "아나운서":
            speaker = "announcer"
        else:
            # 공유 섹션: 홀수=데비, 짝수=마를렌
            speaker = "debi" if line_index_in_situation % 2 == 0 else "marlene"

        results.append({
            "speaker": speaker,
            "text": line,
            "situation": current_situation,
            "skin": current_skin,
        })
        line_index_in_situation += 1

    return results


# ─────────────────────────────────────────────
# 2. TTS JSONL 파싱
# ─────────────────────────────────────────────

# 파일명 카테고리 → 상황 매핑
FILENAME_TO_SITUATION = {
    "accelerationLine": "이동",
    "airSupply": "보급",
    "battleStart": "전투 시작",
    "collect": "수집",
    "completeRoute": "루트 완성",
    "craftEpic": "제작",
    "craftLegend": "제작",
    "craftUncommon": "제작",
    "death": "사망",
    "firstMove": "게임 시작",
    "item": "아이템",
    "joke": "도발",
    "kill": "처치",
    "moveInAlley": "골목길 이동",
    "moveInArchery": "양궁장 이동",
    "moveInCemetary": "묘지 이동",
    "moveInChurch": "성당 이동",
    "moveInFactory": "공장 이동",
    "moveInFireStation": "소방서 이동",
    "moveInForest": "숲 이동",
    "moveInGasStation": "주유소 이동",
    "moveInHarbour": "항구 이동",
    "moveInHospital": "병원 이동",
    "moveInHotel": "호텔 이동",
    "moveInPoliceStation": "경찰서 이동",
    "moveInSandyBeach": "모래사장 이동",
    "moveInSchool": "학교 이동",
    "moveInStream": "연못 이동",
    "moveInUptown": "고급 주택가 이동",
    "orderPing": "핑",
    "rest": "휴식",
    "revival": "부활",
    "reviving": "소생",
    "security": "탐색",
    "skillE": "스킬",
    "skillPassive": "스킬",
    "skillQ": "스킬",
    "skillR": "스킬",
    "skillW": "스킬",
    "taunt": "도발",
    "thanks": "감사",
    "trap": "전략",
    "victory": "승리",
    "weaponskill1": "무기 스킬",
    "weaponskill2": "무기 스킬",
    "weaponskill3": "무기 스킬",
}


def parse_tts_jsonl(filepath: str, speaker: str) -> List[Dict]:
    """TTS JSONL에서 대사 추출"""
    results = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            text = data["text"]
            audio_path = data["audio"]

            # 파일명에서 카테고리 추출
            filename = os.path.basename(audio_path)
            situation = "기타"
            for key, sit in FILENAME_TO_SITUATION.items():
                if key in filename:
                    situation = sit
                    break

            results.append({
                "speaker": speaker,
                "text": text,
                "situation": situation,
                "skin": "기본",
                "source": "tts",
            })
    return results


# ─────────────────────────────────────────────
# 3. 배경/성격 정보 파싱
# ─────────────────────────────────────────────

def parse_background(filepath: str) -> Dict:
    """나무위키에서 배경 스토리, 성격 정보 추출"""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # 배경 스토리 섹션 추출 (대략적으로)
    bg_start = text.find("배경 스토리")
    bg_end = text.find("실험체 대사")
    background = text[bg_start:bg_end] if bg_start > 0 and bg_end > 0 else ""

    return {
        "background": background,
        "full_text": text,
    }


# ─────────────────────────────────────────────
# 4. Q&A 생성
# ─────────────────────────────────────────────

SYSTEM_PROMPT_BOTH = """너는 이터널 리턴의 실험체 데비&마를렌이야.
데비(파란색, 언니): 활발하고 천진난만한 성격. 정정당당한 걸 좋아하고, 원거리 무기를 싫어해. 장난스럽고 직설적인 말투.
마를렌(빨간색, 동생): 냉소적이고 신중한 성격. 실용주의자이며, 간결하고 차분한 말투. 가끔 한숨을 쉼.
둘은 쌍둥이 자매로, 항상 함께 행동해. 대답할 때 데비와 마를렌 둘 다 말해야 해.
데비의 대사는 "데비:" 로, 마를렌의 대사는 "마를렌:" 으로 시작해."""

SYSTEM_PROMPT_DEBI = """너는 이터널 리턴의 실험체 데비야.
활발하고 천진난만한 성격. 정정당당한 걸 좋아하고, 원거리 무기를 싫어해. 장난스럽고 직설적인 말투를 써.
마를렌이라는 쌍둥이 동생이 있고, 항상 같이 다녀."""

SYSTEM_PROMPT_MARLENE = """너는 이터널 리턴의 실험체 마를렌이야.
냉소적이고 신중한 성격. 실용주의자이며, 간결하고 차분한 말투를 써. 가끔 한숨을 쉼.
데비라는 쌍둥이 언니가 있고, 항상 같이 다녀."""


def build_dialogue_pairs(quotes: List[Dict]) -> List[Dict]:
    """연속된 데비-마를렌 대사를 대화 쌍으로 묶기"""
    pairs = []

    # 상황별로 그룹화
    by_situation = defaultdict(list)
    for q in quotes:
        if q["speaker"] in ("debi", "marlene"):
            by_situation[(q["situation"], q["skin"])].append(q)

    for (situation, skin), group in by_situation.items():
        # 연속 대사를 쌍으로 묶기
        i = 0
        while i < len(group):
            if i + 1 < len(group) and group[i]["speaker"] != group[i + 1]["speaker"]:
                # 대화 쌍
                pairs.append({
                    "debi": group[i]["text"] if group[i]["speaker"] == "debi" else group[i + 1]["text"],
                    "marlene": group[i + 1]["text"] if group[i + 1]["speaker"] == "marlene" else group[i]["text"],
                    "situation": situation,
                    "skin": skin,
                })
                i += 2
            else:
                # 단독 대사
                pairs.append({
                    group[i]["speaker"]: group[i]["text"],
                    "situation": situation,
                    "skin": skin,
                })
                i += 1

    return pairs


# 상황별 질문 템플릿
QUESTION_TEMPLATES = {
    "로비": ["안녕!", "오늘도 해볼까?", "준비됐어?"],
    "캐릭터 선택": ["같이 하자!", "오늘은 어떻게 할 거야?"],
    "게임 시작": ["게임 시작이다!", "시작하자!"],
    "이동": ["빨리 가자!", "어디로 가야 해?"],
    "전투": ["적이다!", "싸우자!", "전투 시작!"],
    "처치": ["잡았다!", "하나 처치!", "적 처치했어!"],
    "사망": ["졌어...", "죽었어..."],
    "승리": ["이겼다!", "우리가 1등!", "승리!"],
    "패배": ["아쉽다...", "졌네..."],
    "휴식": ["쉬자!", "잠깐 쉬어도 돼?"],
    "제작": ["아이템 만들었어!", "이거 뭐 만든 거야?"],
    "도발": ["이리 와 봐!", "도발 한번 해봐!"],
    "탐색": ["주변을 살펴볼까?", "뭐가 있을까?"],
    "전략": ["트랩 설치할까?", "함정 놓자!"],
    "소생": ["살려줘!", "도와줘!"],
    "부활": ["다시 살아났어!", "부활이다!"],
    "스킬": ["스킬 써!", "스킬 발동!"],
}

# 지역 이동용 질문
LOCATION_QUESTIONS = {
    "골목길 이동": ["골목길이다", "여기 좀 좁은데?"],
    "양궁장 이동": ["양궁장이네", "활 쏘는 데가 있네?"],
    "묘지 이동": ["묘지다...", "여기 좀 무섭지 않아?"],
    "성당 이동": ["성당이네", "여기 교회 같은 데야?"],
    "공장 이동": ["공장이다", "여기서 뭐 만들었을까?"],
    "소방서 이동": ["소방서다", "소방차가 있네?"],
    "숲 이동": ["숲이다", "나무가 많네"],
    "주유소 이동": ["주유소다", "기름 냄새나"],
    "항구 이동": ["항구네", "바다다!"],
    "병원 이동": ["병원이다", "약 있을까?"],
    "호텔 이동": ["호텔이네", "여기서 쉴 수 있을까?"],
    "경찰서 이동": ["경찰서다", "누가 있을까?"],
    "학교 이동": ["학교다", "학교 왔네?"],
    "연못 이동": ["연못이다", "물이 있네"],
    "모래사장 이동": ["모래사장이다", "바다다!"],
    "고급 주택가 이동": ["고급 주택가네", "여기 좀 좋은 동네인데?"],
}

QUESTION_TEMPLATES.update(LOCATION_QUESTIONS)

# 일반 대화 질문 (성격/배경)
PERSONALITY_QA = [
    {"q": "데비는 어떤 성격이야?", "a": "데비: 나? 당연히 밝고 활발하지! 싸울 때도 정정당당하게!\n마를렌: ...시끄럽다는 뜻이야."},
    {"q": "마를렌은 어떤 성격이야?", "a": "데비: 동생은 좀 차가워 보여도 속은 따뜻해~\n마를렌: 쓸데없는 말 하지 마."},
    {"q": "둘의 관계가 어때?", "a": "데비: 세상에서 마를렌이 제일 소중하지!\n마를렌: ...떨어지면 죽으니까."},
    {"q": "무기가 뭐야?", "a": "데비: 양손검! 정정당당하게 칼로 싸우는 거지!\n마를렌: 난 검을 던지거나 투사체를 쓰는 편이야."},
    {"q": "원거리 무기는 어때?", "a": "데비: 활이든 총이든 낭만이 없다니깐! 비겁해!\n마를렌: 전략적인 무기야. 데비가 편견이 심한 거지."},
    {"q": "성당 좋아해?", "a": "데비: 짜증나는 기억이 떠올라...\n마를렌: 마찬가지야. 눈 먼 교리만큼 답 없는 무식이 없지."},
    {"q": "어릴 때 뭐 했어?", "a": "데비: 나한텐 일상이었어. 밀무역도 좀 했고~\n마를렌: ...쓸데없는 말 하지 마."},
    {"q": "떨어지면 어떻게 돼?", "a": "데비: 우린 떨어지면 죽거든!\n마를렌: 말 그대로야."},
    {"q": "팀워크가 좋아?", "a": "데비: 우린 붙어 있을 때 최강이니깐!\n마를렌: 딱 붙어 있어. 해결은 내가 할 테니까."},
    {"q": "이름이 뭐야?", "a": "데비: 데비 카를손! 이쪽은 내 쌍둥이 동생 마를렌~\n마를렌: 마를렌 카를손."},
]

# 게임 결과 반응
GAME_RESULT_QA = [
    {"q": "21킬 1등했어!", "a": "데비: 21킬?! 말도 안 돼~!! 완전 대박이잖아!\n마를렌: ...그 킬수면 인정해야겠네."},
    {"q": "오늘 처음 이겼어!", "a": "데비: 진짜?! 너무 좋다!! 축하해~!!\n마를렌: 첫 승은 특별하지. 다음에도 이겨."},
    {"q": "3킬밖에 못했어...", "a": "데비: 3킬이면 충분하지! 다음엔 더 잘할 수 있어!\n마를렌: 킬보다 생존이 중요할 때도 있어."},
    {"q": "계속 져...", "a": "데비: 에이~ 그럴 수도 있지! 포기하면 안 돼!\n마를렌: 지는 게 습관이 되면 안 되긴 하지."},
    {"q": "뭐 빌드해야 해?", "a": "데비: 양손검 들고 들이받으면 되지!\n마를렌: ...상대에 따라 다르지만, 기본적으로 공격력과 방어력 밸런스를 맞춰."},
    {"q": "몇 등이면 잘한 거야?", "a": "데비: 당연히 1등이지!\n마를렌: 상위 3등 안이면 괜찮은 거야. 1등이 아니어도."},
]


def generate_qa_from_pairs(pairs: List[Dict]) -> List[Dict]:
    """대화 쌍에서 Q&A 데이터 생성"""
    qa_list = []

    for pair in pairs:
        situation = pair.get("situation", "기타")
        skin = pair.get("skin", "기본")
        debi_text = pair.get("debi", "")
        marlene_text = pair.get("marlene", "")

        # 질문 선택
        templates = QUESTION_TEMPLATES.get(situation, ["뭐 해?", "어떤 상황이야?"])
        question = random.choice(templates)

        # 스킨에 따라 상황 맥락 추가
        if skin != "기본" and skin != "아나운서":
            question = f"[{skin} 스킨] {question}"

        # 응답 생성
        if debi_text and marlene_text:
            answer = f"데비: {debi_text}\n마를렌: {marlene_text}"
            system = SYSTEM_PROMPT_BOTH
        elif debi_text:
            answer = f"데비: {debi_text}"
            system = SYSTEM_PROMPT_DEBI
        elif marlene_text:
            answer = f"마를렌: {marlene_text}"
            system = SYSTEM_PROMPT_MARLENE
        else:
            continue

        qa_list.append({
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ],
            "meta": {"situation": situation, "skin": skin, "source": "namuwiki_dialogue"},
        })

    return qa_list


def generate_qa_from_singles(quotes: List[Dict]) -> List[Dict]:
    """단독 대사에서 Q&A 생성 (TTS 데이터 등)"""
    qa_list = []

    for q in quotes:
        situation = q.get("situation", "기타")
        speaker = q["speaker"]
        text = q["text"]

        if speaker not in ("debi", "marlene"):
            continue

        templates = QUESTION_TEMPLATES.get(situation, ["뭐 해?"])
        question = random.choice(templates)

        if speaker == "debi":
            answer = f"데비: {text}"
            system = SYSTEM_PROMPT_DEBI
        else:
            answer = f"마를렌: {text}"
            system = SYSTEM_PROMPT_MARLENE

        qa_list.append({
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ],
            "meta": {"situation": situation, "skin": q.get("skin", "기본"), "source": q.get("source", "namuwiki")},
        })

    return qa_list


def generate_personality_qa() -> List[Dict]:
    """성격/배경 Q&A 생성"""
    qa_list = []
    for item in PERSONALITY_QA + GAME_RESULT_QA:
        qa_list.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_BOTH},
                {"role": "user", "content": item["q"]},
                {"role": "assistant", "content": item["a"]},
            ],
            "meta": {"situation": "일반 대화", "skin": "기본", "source": "handcrafted"},
        })
    return qa_list


def generate_item_qa(vlm_path: str, max_items: int = 300) -> List[Dict]:
    """VLM 아이템 데이터에서 게임 지식 Q&A 생성"""
    with open(vlm_path, "r", encoding="utf-8") as f:
        vlm_data = json.load(f)

    qa_list = []
    random.shuffle(vlm_data)

    for item in vlm_data[:max_items]:
        # 원본 응답에서 아이템 정보 추출
        original_answer = item["conversations"][1]["value"]

        # 아이템 이름 추출
        name = original_answer.split("야.")[0] if "야." in original_answer else original_answer.split("이야")[0]
        name = name.strip()

        # 데비&마를렌 말투로 변환
        debi_responses = [
            f"데비: {name}! {original_answer.replace(name + '야.', '').replace(name + '이야.', '').strip()}",
            f"데비: 오~ {name}이잖아!",
            f"데비: {name}? 알지알지~",
        ]
        marlene_responses = [
            f"마를렌: {original_answer}",
            f"마를렌: {name}. 쓸만한 장비지.",
        ]

        answer = f"{random.choice(debi_responses)}\n{random.choice(marlene_responses)}"

        questions = [
            f"{name} 뭐야?",
            f"{name} 어때?",
            f"{name} 좋아?",
        ]

        qa_list.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_BOTH},
                {"role": "user", "content": random.choice(questions)},
                {"role": "assistant", "content": answer},
            ],
            "meta": {"situation": "게임 지식", "skin": "기본", "source": "vlm_items"},
        })

    return qa_list


# ─────────────────────────────────────────────
# 5. 메인
# ─────────────────────────────────────────────

def main():
    print("=== 데비&마를렌 파인튜닝 데이터셋 생성 ===\n")

    all_qa = []

    # 1) 나무위키 대사 파싱
    namu_path = RAW_DIR / "namu_debi_marlene_main.txt"
    if namu_path.exists():
        print("[1] 나무위키 대사 파싱...")
        namu_quotes = parse_namuwiki_quotes(str(namu_path))
        print(f"    파싱 완료: {len(namu_quotes)}개 대사")

        # 통계
        debi_count = sum(1 for q in namu_quotes if q["speaker"] == "debi")
        marlene_count = sum(1 for q in namu_quotes if q["speaker"] == "marlene")
        skins = set(q["skin"] for q in namu_quotes)
        print(f"    데비: {debi_count}, 마를렌: {marlene_count}")
        print(f"    스킨: {skins}")

        # 대화 쌍 생성
        pairs = build_dialogue_pairs(namu_quotes)
        print(f"    대화 쌍: {len(pairs)}개")

        qa_from_pairs = generate_qa_from_pairs(pairs)
        all_qa.extend(qa_from_pairs)
        print(f"    Q&A 생성: {len(qa_from_pairs)}개")
    else:
        print("[1] 나무위키 파일 없음, 스킵")

    # 2) TTS JSONL 파싱
    tts_debi = BASE_DIR / "debi_finetune.jsonl"
    tts_marlene = BASE_DIR / "marlene_finetune.jsonl"
    tts_quotes = []
    if tts_debi.exists():
        print("\n[2] TTS JSONL 파싱...")
        tts_quotes.extend(parse_tts_jsonl(str(tts_debi), "debi"))
        tts_quotes.extend(parse_tts_jsonl(str(tts_marlene), "marlene"))
        print(f"    TTS 대사: {len(tts_quotes)}개")

        # 나무위키와 중복 제거
        namu_texts = set(q["text"] for q in namu_quotes) if namu_path.exists() else set()
        tts_unique = [q for q in tts_quotes if q["text"] not in namu_texts]
        print(f"    나무위키 중복 제거 후: {len(tts_unique)}개")

        qa_from_tts = generate_qa_from_singles(tts_unique)
        all_qa.extend(qa_from_tts)
        print(f"    Q&A 생성: {len(qa_from_tts)}개")

    # 3) 성격/배경/게임 결과 Q&A
    print("\n[3] 성격/배경/게임 결과 Q&A 생성...")
    personality_qa = generate_personality_qa()
    all_qa.extend(personality_qa)
    print(f"    Q&A 생성: {len(personality_qa)}개")

    # 4) VLM 아이템 데이터
    vlm_path = BASE_DIR.parent / "vlm_training" / "dataset" / "eternal_return_vlm_dataset.json"
    if vlm_path.exists():
        print("\n[4] VLM 아이템 데이터 변환...")
        item_qa = generate_item_qa(str(vlm_path), max_items=300)
        all_qa.extend(item_qa)
        print(f"    Q&A 생성: {len(item_qa)}개")

    # 5) 셔플 + 저장
    random.shuffle(all_qa)

    # LLaMA-Factory용 (meta 제거)
    llama_data = [{"messages": qa["messages"]} for qa in all_qa]
    llama_path = OUTPUT_DIR / "train.json"
    with open(llama_path, "w", encoding="utf-8") as f:
        json.dump(llama_data, f, ensure_ascii=False, indent=2)

    # 메타데이터 포함 (디버깅용)
    debug_path = OUTPUT_DIR / "train_with_meta.json"
    with open(debug_path, "w", encoding="utf-8") as f:
        json.dump(all_qa, f, ensure_ascii=False, indent=2)

    # 통계
    print(f"\n=== 최종 결과 ===")
    print(f"총 Q&A: {len(all_qa)}개")

    source_counts = defaultdict(int)
    for qa in all_qa:
        source_counts[qa["meta"]["source"]] += 1
    for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {src}: {cnt}개")

    print(f"\n저장 완료:")
    print(f"  LLaMA-Factory용: {llama_path}")
    print(f"  디버깅용: {debug_path}")


if __name__ == "__main__":
    main()
