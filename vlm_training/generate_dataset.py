"""
이터널리턴 VLM 파인튜닝용 데이터셋 생성 스크립트

emojis 폴더 이미지 + DAK.GG API 데이터를 합쳐서
SmolVLM2/Qwen2.5-VL 파인튜닝용 데이터셋 생성
"""

import json
import os
import random
import requests
from pathlib import Path
from typing import List, Dict, Any

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
EMOJIS_DIR = BASE_DIR / "emojis"
OUTPUT_DIR = Path(__file__).parent / "dataset"

# DAK.GG API
API_BASE = "https://er.dakgg.io/api/v1"


def fetch_api_data(endpoint: str) -> Dict:
    """DAK.GG API에서 데이터 가져오기"""
    url = f"{API_BASE}{endpoint}"
    print(f"  Fetching: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_items_data() -> List[Dict]:
    """아이템 데이터 가져오기"""
    data = fetch_api_data("/data/items?hl=ko")
    return data.get("items", [])


def get_characters_data() -> List[Dict]:
    """캐릭터 데이터 가져오기"""
    data = fetch_api_data("/data/characters?hl=ko")
    return data.get("characters", [])


def get_traits_data() -> List[Dict]:
    """특성 데이터 가져오기"""
    data = fetch_api_data("/data/trait-skills?hl=ko")
    return data.get("traitSkills", [])


def get_weapons_data() -> List[Dict]:
    """무기 데이터 가져오기"""
    data = fetch_api_data("/data/masteries?hl=ko")
    return data.get("masteries", [])


# =============================================================================
# 질문 템플릿
# =============================================================================

ITEM_QUESTIONS = [
    "이 아이템 뭐야?",
    "이거 스탯 알려줘",
    "이 아이템 정보 알려줘",
    "이거 어떤 아이템이야?",
    "이 아이템 효과가 뭐야?",
]

CHARACTER_QUESTIONS = [
    "이 캐릭터 누구야?",
    "이 캐릭터 정보 알려줘",
    "이거 누구야?",
    "이 캐릭터 어떤 캐릭터야?",
]

TRAIT_QUESTIONS = [
    "이 특성 뭐야?",
    "이 특성 효과가 뭐야?",
    "이거 어떤 특성이야?",
]


# =============================================================================
# 데이터 생성 함수
# =============================================================================

def parse_item_tooltip(tooltip: str) -> Dict[str, str]:
    """아이템 툴팁 파싱"""
    lines = tooltip.split('\n')
    result = {
        "grade": "",
        "type": "",
        "stats": [],
        "description": "",
    }

    if len(lines) > 0:
        # 첫 줄: 등급 / 타입
        first_line = lines[0]
        if '/' in first_line:
            parts = first_line.split('/')
            result["grade"] = parts[0].strip()
            result["type"] = parts[1].strip() if len(parts) > 1 else ""

    # 스탯 추출 (+ 또는 - 로 시작하는 줄)
    for line in lines[1:]:
        line = line.strip()
        if line and ('+' in line or line.startswith('-')):
            # HTML 태그 제거
            clean = line.replace('<color=#FFFF00>', '').replace('</color>', '')
            clean = clean.replace('<color=#F4FF63>', '').replace('</color>', '')
            result["stats"].append(clean)

    return result


def generate_item_answer(item: Dict) -> str:
    """아이템 답변 생성"""
    name = item.get("name", "알 수 없음")
    tooltip = item.get("tooltip", "")
    parsed = parse_item_tooltip(tooltip)

    answer_parts = [f"{name}."]

    if parsed["grade"] and parsed["type"]:
        answer_parts.append(f"{parsed['grade']} 등급 {parsed['type']}야.")

    if parsed["stats"]:
        stats_str = ", ".join(parsed["stats"][:5])  # 최대 5개 스탯
        answer_parts.append(f"스탯: {stats_str}")

    return " ".join(answer_parts)


def generate_character_answer(char: Dict) -> str:
    """캐릭터 답변 생성"""
    name = char.get("name", "알 수 없음")
    key = char.get("key", "")
    masteries = char.get("masteries", [])
    archetypes = char.get("charArcheTypes", [])

    answer_parts = [f"{name}야."]

    # 역할 추가
    role_map = {
        "Mage": "마법사",
        "Marksman": "원거리 딜러",
        "Fighter": "전사",
        "Tank": "탱커",
        "Support": "서포터",
        "Assassin": "암살자",
    }
    roles = [role_map.get(a, a) for a in archetypes if a in role_map]
    if roles:
        answer_parts.append(f"{'/'.join(roles)} 역할이야.")

    # 무기 추가
    weapon_map = {
        "Pistol": "권총",
        "AssaultRifle": "돌격소총",
        "SniperRifle": "저격소총",
        "TwoHandSword": "양손검",
        "Axe": "도끼",
        "Hammer": "망치",
        "Bat": "배트",
        "Whip": "채찍",
        "Glove": "글러브",
        "Dagger": "단검",
        "DualSword": "쌍검",
        "Spear": "창",
        "Nunchaku": "쌍절곤",
        "Bow": "활",
        "Crossbow": "석궁",
        "Shuriken": "표창",
        "Rapier": "레이피어",
        "Guitar": "기타",
        "Camera": "카메라",
        "Arcana": "아르카나",
        "VFArm": "VF의수",
    }
    weapons = [weapon_map.get(m, m) for m in masteries[:2]]
    if weapons:
        answer_parts.append(f"주로 {', '.join(weapons)} 써.")

    return " ".join(answer_parts)


def generate_trait_answer(trait: Dict) -> str:
    """특성 답변 생성"""
    name = trait.get("name", "알 수 없음")
    tooltip = trait.get("tooltip", "")
    group = trait.get("group", "")
    trait_type = trait.get("type", "")

    # HTML 태그 제거
    import re
    clean_tooltip = re.sub(r'<[^>]+>', '', tooltip)

    answer_parts = [f"{name} 특성이야."]

    # 그룹 정보 추가
    group_map = {
        "Havoc": "파괴",
        "Control": "제어",
        "Support": "지원",
        "Defense": "방어",
        "Utility": "유틸",
    }
    if group and group in group_map:
        answer_parts.append(f"{group_map[group]} 계열이고,")

    # 효과 설명
    if clean_tooltip:
        # 너무 길면 축약
        if len(clean_tooltip) > 100:
            clean_tooltip = clean_tooltip[:100] + "..."
        answer_parts.append(clean_tooltip)

    return " ".join(answer_parts)


def create_conversation(image_path: str, question: str, answer: str) -> Dict:
    """VLM 학습용 대화 형식 생성"""
    return {
        "id": f"{Path(image_path).stem}_{hash(question) % 10000}",
        "image": image_path,
        "conversations": [
            {
                "from": "human",
                "value": f"<image>\n{question}"
            },
            {
                "from": "gpt",
                "value": answer
            }
        ]
    }


# =============================================================================
# 메타 인식 & 캐릭터 로어 데이터
# =============================================================================

def generate_meta_conversations() -> List[Dict]:
    """메타 인식(4의 벽) 대화 데이터 생성"""
    meta_data = [
        {
            "question": "너 누구야?",
            "answer": "나는 데비야! 이터널리턴에서 온 캐릭터인데, 지금은 디스코드 봇으로 너희 도와주고 있어! 마를렌 동생이랑 같이!"
        },
        {
            "question": "마를렌은 어디있어?",
            "answer": "마를렌? 바로 옆에 있지! 우린 붙어있을 때 최강이니까. 원하면 마를렌한테 물어볼 수도 있어!"
        },
        {
            "question": "게임에서 직접 알려줘",
            "answer": "아~ 게임 안에서 만나면 직접 보여줄 수 있는데! 여기선 말로만 해야 해서 아쉽다. 그래도 최대한 자세히 설명해줄게!"
        },
        {
            "question": "너 봇이야?",
            "answer": "응! 원래는 게임 캐릭터인데 지금은 디스코드 봇으로 활동 중이야. 게임에서는 직접 싸우는데, 여기선 조언만 해줄 수 있어서 좀 답답하긴 해~"
        },
        {
            "question": "이터널리턴이 뭐야?",
            "answer": "이터널리턴! 내가 사는 게임이지! 배틀로얄 장르인데, 아이템 조합해서 장비 만들고 다른 실험체들이랑 싸우는 거야. 나랑 마를렌도 거기서 싸우고 있어!"
        },
        {
            "question": "데비랑 마를렌 뭐가 달라?",
            "answer": "나는 파란색이고 근거리 담당! 밝고 활발한 성격이야. 마를렌은 빨간색이고 원거리 담당인데, 좀 쿨하고 말이 없어. 근데 우린 쌍둥이라서 붙어있을 때 최강이야!"
        },
        {
            "question": "너희 스토리가 뭐야?",
            "answer": "우리는 쌍둥이야! 붙어있으면 강해지고 떨어지면 약해지는 초능력이 있어. 한때 떨어져 살았는데... 마를렌이 위험해져서 다시 합쳤어. 이제 절대 안 떨어져!"
        },
    ]

    conversations = []
    for item in meta_data:
        conversations.append({
            "id": f"meta_{hash(item['question']) % 10000}",
            "image": None,  # 텍스트만 있는 대화
            "conversations": [
                {"from": "human", "value": item["question"]},
                {"from": "gpt", "value": item["answer"]}
            ]
        })

    return conversations


# =============================================================================
# 메인 함수
# =============================================================================

def main():
    print("=" * 60)
    print("이터널리턴 VLM 데이터셋 생성 시작")
    print("=" * 60)

    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_conversations = []

    # 1. 아이템 데이터
    print("\n[1/4] 아이템 데이터 처리 중...")
    items = get_items_data()
    items_dir = EMOJIS_DIR / "items_graded"

    item_count = 0
    for item in items:
        item_id = item.get("id")
        image_file = items_dir / f"{item_id}.png"

        if image_file.exists():
            answer = generate_item_answer(item)
            # 랜덤하게 2-3개 질문 선택
            selected_questions = random.sample(ITEM_QUESTIONS, min(3, len(ITEM_QUESTIONS)))

            for question in selected_questions:
                conv = create_conversation(
                    str(image_file.relative_to(BASE_DIR)),
                    question,
                    answer
                )
                all_conversations.append(conv)
                item_count += 1

    print(f"  -> 아이템 대화 {item_count}개 생성")

    # 2. 캐릭터 데이터
    print("\n[2/4] 캐릭터 데이터 처리 중...")
    characters = get_characters_data()
    chars_dir = EMOJIS_DIR / "characters"

    char_count = 0
    for char in characters:
        key = char.get("key", "")  # 영어 이름 (Aya, Jackie 등)
        image_file = chars_dir / f"{key}.png"

        if image_file.exists():
            answer = generate_character_answer(char)
            selected_questions = random.sample(CHARACTER_QUESTIONS, min(2, len(CHARACTER_QUESTIONS)))

            for question in selected_questions:
                conv = create_conversation(
                    str(image_file.relative_to(BASE_DIR)),
                    question,
                    answer
                )
                all_conversations.append(conv)
                char_count += 1

    print(f"  -> 캐릭터 대화 {char_count}개 생성")

    # 3. 특성 데이터
    print("\n[3/4] 특성 데이터 처리 중...")
    traits = get_traits_data()
    traits_dir = EMOJIS_DIR / "traits"

    trait_count = 0
    for trait in traits:
        trait_id = trait.get("id")  # id 필드 사용
        image_file = traits_dir / f"{trait_id}.png"

        if image_file.exists():
            answer = generate_trait_answer(trait)
            selected_questions = random.sample(TRAIT_QUESTIONS, min(2, len(TRAIT_QUESTIONS)))

            for question in selected_questions:
                conv = create_conversation(
                    str(image_file.relative_to(BASE_DIR)),
                    question,
                    answer
                )
                all_conversations.append(conv)
                trait_count += 1

    print(f"  -> 특성 대화 {trait_count}개 생성")

    # 4. 메타 인식 & 캐릭터 로어
    print("\n[4/4] 메타 인식 데이터 추가 중...")
    meta_conversations = generate_meta_conversations()
    all_conversations.extend(meta_conversations)
    print(f"  -> 메타 대화 {len(meta_conversations)}개 생성")

    # 데이터 섞기
    random.shuffle(all_conversations)

    # JSON 저장
    output_file = OUTPUT_DIR / "eternal_return_vlm_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_conversations, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"데이터셋 생성 완료!")
    print(f"총 대화 수: {len(all_conversations)}")
    print(f"저장 위치: {output_file}")
    print("=" * 60)

    # 통계 출력
    print("\n[통계]")
    print(f"  - 아이템 관련: {item_count}개")
    print(f"  - 캐릭터 관련: {char_count}개")
    print(f"  - 특성 관련: {trait_count}개")
    print(f"  - 메타/로어: {len(meta_conversations)}개")


if __name__ == "__main__":
    main()
