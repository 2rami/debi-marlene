"""
데비&마를렌 파인튜닝 데이터셋 v2

구조:
  Part 1: 말투 학습 (대사 원본 → 짧은 상황 + 캐릭터 응답)
  Part 2: Q&A 대화 (자연스러운 질문 → 캐릭터답게 대답)
  Part 3: 게임 지식 (아이템/스킬 질문 → 캐릭터 말투로 설명)

시스템 프롬프트: 짧게, 학습 데이터 전체에서 1종류만
"""

import json
import re
import random
import os
from pathlib import Path
from collections import defaultdict

random.seed(42)

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "raw_data"
OUTPUT_DIR = BASE_DIR / "dataset"
OUTPUT_DIR.mkdir(exist_ok=True)

# 시스템 프롬프트는 학습 데이터에 넣지 않음
# 추론 시에만 사용
# SYSTEM_FOR_INFERENCE = "너는 이터널 리턴의 쌍둥이 실험체야. 데비(언니)는 활발하고 직설적, 마를렌(동생)은 냉소적이고 간결해."

# ─────────────────────────────────────────────
# 나무위키 대사 파싱
# ─────────────────────────────────────────────

SKIP_LINES = {
    "[편집]", "파란색", "빨간색", "으로 표기.", "데비의 대사는",
    "마를렌의 대사는", "[더미]", "(대사 1)", "(대사 2)",
    "데비", "마를렌", "행동", "지역", "전투", "제작", "교전", "킬",
    "[목소리]", "공격",
}

# 카테고리 헤더로 인식할 패턴
CATEGORY_PATTERNS = [
    # 정확 일치
    "로비", "선택 시", "실험 시작", "하이퍼루프 이용", "하이퍼 루프 이용",
    "아군에게 하이퍼루프", "보안 콘솔 이용", "트랩 설치", "휴식", "해킹 시도",
    "소생 시작", "소생 성공", "부활 성공", "점령장치 점령", "원격드론 호출",
    "필요한 아이템 요청", "감정표현", "농담", "감정 표현", "도발", "감사",
    "Q 스킬 시전", "W 스킬 시전", "E 스킬 시전", "R 스킬 시전",
    "무기 스킬 습득", "양손검 - 빗겨 흘리기",
    "고급 등급 아이템 제작", "영웅 등급 아이템 제작",
    "전설 등급 아이템 제작", "초월 등급 아이템 제작",
    "고급 아이템 제작", "영웅 아이템 제작", "전설 아이템 제작",
    "적 처치", "아군 처치됨", "적 처치 시", "아군 처치 시", "사망 시",
    "사망", "처치", "승리", "패배", "최종 금지구역",
    "금지구역 이동", "금지구역 알림", "제작 관련", "상호 대사",
    "첫 킬", "멀티킬", "처치 지원", "선택 시", "실험 시작",
    # 지역
    "골목길", "양궁장", "묘지", "성당", "공장", "소방서", "숲",
    "주유소", "항구", "병원", "호텔", "경찰서", "학교", "연못",
    "모래사장", "고급 주택가", "번화가", "연구소", "연구소 외곽",
    # 스킨별 추가 지역
    "해변", "수영장", "펜션", "리조트",
]

# N명 처치 시 패턴
KILL_PATTERN = re.compile(r"^\d+명 처치 시$")
# 등수 패턴
RANK_PATTERN = re.compile(r"^(상위권|하위권|\d+등|꼴등)$")
# 채집 패턴
GATHER_PATTERN = re.compile(r"^.+\s?채집$")
# 섹션 번호 (9.1, 9.1.1, 9.2.1 등)
SECTION_NUM_PATTERN = re.compile(r"^\d+\.[\d.]*\d*$")


def is_category_header(line: str) -> bool:
    """카테고리 헤더인지 판별"""
    if line in CATEGORY_PATTERNS:
        return True
    if KILL_PATTERN.match(line):
        return True
    if RANK_PATTERN.match(line):
        return True
    if GATHER_PATTERN.match(line):
        return True
    if SECTION_NUM_PATTERN.match(line):
        return True
    return False


def parse_namuwiki(filepath: str) -> list[dict]:
    """나무위키에서 순수 대사만 추출 (speaker, text, category)"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    results = []
    in_quotes = False
    current_section = ""  # "debi" / "marlene" / "" (공유)
    current_category = ""
    line_idx = 0  # 카테고리 내 라인 인덱스

    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue

        # 대사 섹션 시작
        if "실험체 대사" in line and "스파클링" not in line and "방과" not in line:
            in_quotes = True
            current_section = ""
            continue
        if "스파클링 트윈즈 데비&마를렌 대사" in line:
            in_quotes = True
            current_section = ""
            continue
        if "방과 후 자유시간 데비&마를렌 대사" in line:
            in_quotes = True
            current_section = ""
            continue
        if "아나운서 대사" in line:
            # 아나운서는 스킵
            in_quotes = False
            continue

        if not in_quotes:
            continue

        # 대사 영역 종료 (9. 대사 섹션 밖의 대제목)
        if re.match(r"^\d+\.\s*$", line):
            num = int(line.split(".")[0])
            if num != 9:
                in_quotes = False
                continue

        # 섹션 번호 스킵 (9.3, 10.4 등)
        if re.match(r"^\d+\.\d", line):
            continue

        # 개별 캐릭터 섹션
        if line == "데비" and i + 1 < len(lines) and "[편집]" in lines[i + 1]:
            current_section = "debi"
            continue
        if line == "마를렌" and i + 1 < len(lines) and "[편집]" in lines[i + 1]:
            current_section = "marlene"
            continue

        # 스킵
        if line in SKIP_LINES:
            continue
        if line.startswith("[") and line.endswith("]"):
            continue

        # 카테고리 헤더
        if is_category_header(line):
            current_category = line
            line_idx = 0
            continue

        # 섹션 번호 스킵 (9.1, 9.1.1, 9.2.1 등)
        if re.match(r"^\d+\.[\d.]*\d*$", line):
            continue
        # ". 데비", ". 마를렌" 같은 하위섹션 제목
        if line.startswith(". "):
            continue

        # 너무 짧은 라인 스킵
        if len(line) < 2:
            continue
        # 순수 숫자 스킵 (10, 11 같은 목차 번호)
        if line.isdigit():
            continue
        # 메타 텍스트 잔류 스킵
        if ", 마를렌의 대사는" in line or ", 데비의 대사는" in line:
            continue

        # 화자 결정
        if current_section == "debi":
            speaker = "debi" if line_idx % 2 == 0 else "marlene"
        elif current_section == "marlene":
            speaker = "marlene" if line_idx % 2 == 0 else "debi"
        else:
            speaker = "debi" if line_idx % 2 == 0 else "marlene"

        results.append({
            "speaker": speaker,
            "text": line,
            "category": current_category,
        })
        line_idx += 1

    return results


def parse_tts_jsonl(filepath: str, speaker: str) -> list[dict]:
    """TTS JSONL에서 대사 추출"""
    results = []
    with open(filepath, "r", encoding="utf-8") as f:
        for l in f:
            if not l.strip():
                continue
            data = json.loads(l)
            results.append({
                "speaker": speaker,
                "text": data["text"],
                "category": "tts",
            })
    return results


# ─────────────────────────────────────────────
# 데이터셋 구성
# ─────────────────────────────────────────────

def build_part1_dialogue(all_quotes: list[dict]) -> list[dict]:
    """
    Part 1: 말투 학습
    연속된 데비-마를렌 대사를 대화 쌍으로 묶어서
    짧은 상황 설명 → 캐릭터 응답
    """
    dataset = []
    seen_texts = set()

    # 연속된 대사를 쌍으로 묶기
    i = 0
    while i < len(all_quotes):
        q = all_quotes[i]

        # 중복 체크
        if q["text"] in seen_texts:
            i += 1
            continue

        # 다음 대사가 다른 화자면 쌍으로 묶기
        if i + 1 < len(all_quotes) and all_quotes[i]["speaker"] != all_quotes[i + 1]["speaker"]:
            q2 = all_quotes[i + 1]
            if q2["text"] not in seen_texts:
                # 쌍 생성
                if q["speaker"] == "debi":
                    response = f"데비: {q['text']}\n마를렌: {q2['text']}"
                else:
                    response = f"마를렌: {q['text']}\n데비: {q2['text']}"

                dataset.append({
                    "conversations": [
                        {"from": "human", "value": q["category"] if q["category"] else "대화"},
                        {"from": "gpt", "value": response},
                    ]
                })
                seen_texts.add(q["text"])
                seen_texts.add(q2["text"])
                i += 2
                continue

        # 단독 대사
        speaker_name = "데비" if q["speaker"] == "debi" else "마를렌"
        dataset.append({
            "conversations": [
                {"from": "human", "value": q["category"] if q["category"] else "대화"},
                {"from": "gpt", "value": f"{speaker_name}: {q['text']}"},
            ]
        })
        seen_texts.add(q["text"])
        i += 1

    return dataset, seen_texts


def build_part2_qa() -> list[dict]:
    """
    Part 2: 자연스러운 Q&A 대화
    다양한 상황에서 캐릭터답게 대답하는 패턴
    """
    qa_pairs = [
        # 성격/소개
        ("너 누구야?", "데비: 데비 카를손! 이쪽은 내 쌍둥이 동생 마를렌~\n마를렌: 마를렌 카를손."),
        ("데비는 어떤 애야?", "데비: 나? 당연히 밝고 활발하지! 싸울 때도 정정당당하게!\n마를렌: ...시끄럽다는 뜻이야."),
        ("마를렌은 어떤 애야?", "데비: 동생은 좀 차가워 보여도 속은 따뜻해~\n마를렌: 쓸데없는 말 하지 마."),
        ("둘이 사이 좋아?", "데비: 세상에서 마를렌이 제일 소중하지!\n마를렌: ...떨어지면 죽으니까."),
        ("무기가 뭐야?", "데비: 양손검! 정정당당하게 칼로 싸우는 거지!\n마를렌: 난 투사체를 쓰는 편이야."),
        ("활 어때?", "데비: 활이든 총이든 낭만이 없다니깐! 비겁해!\n마를렌: 전략적인 무기야. 데비가 편견이 심한 거지."),
        ("성당 좋아해?", "데비: 짜증나는 기억이 떠올라...\n마를렌: 마찬가지야. 눈 먼 교리만큼 답 없는 무식이 없지."),
        ("어릴 때 뭐 했어?", "데비: 나한텐 일상이었어. 밀무역도 좀 했고~\n마를렌: ...쓸데없는 말 하지 마."),
        ("떨어지면 어떻게 돼?", "데비: 우린 떨어지면 죽거든!\n마를렌: 말 그대로야."),
        ("팀워크 좋아?", "데비: 우린 붙어 있을 때 최강이니깐!\n마를렌: 딱 붙어 있어. 해결은 내가 할 테니까."),
        ("나이가 몇이야?", "데비: 스무 살~! 마를렌이랑 같은 나이지 당연히.\n마를렌: 쌍둥이니까."),
        ("키가 몇이야?", "데비: 164! 마를렌이랑 똑같아~\n마를렌: 당연하지."),

        # 게임 결과 반응
        ("21킬 1등했어!", "데비: 21킬?! 말도 안 돼~!! 완전 대박이잖아!\n마를렌: ...그 킬수면 인정해야겠네."),
        ("오늘 처음 이겼어!", "데비: 진짜?! 너무 좋다!! 축하해~!!\n마를렌: 첫 승은 특별하지. 다음에도 이겨."),
        ("3킬밖에 못했어...", "데비: 3킬이면 충분하지! 다음엔 더 잘할 수 있어!\n마를렌: 킬보다 생존이 중요할 때도 있어."),
        ("계속 져...", "데비: 에이~ 그럴 수도 있지! 포기하면 안 돼!\n마를렌: 지는 게 습관이 되면 안 되긴 하지."),
        ("뭐 빌드해야 해?", "데비: 양손검 들고 들이받으면 되지!\n마를렌: ...상대에 따라 다르지만 공격력과 방어력 밸런스를 맞춰."),
        ("몇 등이면 잘한 거야?", "데비: 당연히 1등이지!\n마를렌: 상위 3등 안이면 괜찮은 거야."),
        ("데비마를렌 어떻게 해야 잘해?", "데비: 일단 붙어 있어야 돼! 우리가 같이 있을 때 제일 강하니까!\n마를렌: 태그 교체 타이밍이 중요해. 상황 판단을 잘 해야 해."),
        ("오늘 10킬 했어!", "데비: 10킬?! 대단한데~! 나도 그 정도는 하고 싶다!\n마를렌: 꽤 하네. 다음엔 더 효율적으로 해봐."),
        ("다음 시즌 언제야?", "데비: 몰라~ 빨리 왔으면 좋겠다!\n마를렌: 공지를 확인하는 게 가장 정확해."),
        ("심심해", "데비: 그러면 같이 한판 하자! 나 지금 딱 심심했거든~\n마를렌: ...또 시작이야."),
        ("안녕!", "데비: 안녕~! 오늘도 같이 해볼까?\n마를렌: 어서 와."),
        ("오늘 컨디션 어때?", "데비: 완전 좋아! 오늘은 1등 갈 수 있을 것 같은 느낌!\n마를렌: 매번 그렇게 말하잖아."),
        ("잘 자!", "데비: 잘 자~ 내일도 같이 하자!\n마를렌: 푹 쉬어."),
        ("고마워!", "데비: 아이고~ 별말씀을!\n마를렌: 당연한 걸 가지고."),

        # 일상
        ("학교 어때?", "데비: 수업시간에 잠만 자서 뭐... 히히.\n마를렌: 잠만 자 놓고선."),
        ("뭐 먹을까?", "데비: 맛있는 거! 아무거나 좋아~\n마를렌: 간단하게 먹자."),
        ("오늘 날씨 어때?", "데비: 완전 좋지 않아?! 나가고 싶다~\n마를렌: 밖에 나가면 일이 생기잖아."),
    ]

    dataset = []
    for q, a in qa_pairs:
        dataset.append({
            "conversations": [
                {"from": "human", "value": q},
                {"from": "gpt", "value": a},
            ]
        })
    return dataset


def build_part3_items(vlm_path: str, max_items: int = 200) -> list[dict]:
    """
    Part 3: 게임 지식
    아이템 정보를 캐릭터 말투로 대답
    """
    with open(vlm_path, "r", encoding="utf-8") as f:
        vlm_data = json.load(f)

    dataset = []
    random.shuffle(vlm_data)

    for item in vlm_data[:max_items]:
        original = item["conversations"][1]["value"]

        # "XX야." or "XX이야." 에서 이름 추출
        match = re.match(r"^(.+?)(이야|야)\.", original)
        if not match:
            continue
        name = match.group(1)
        rest = original[match.end():].strip()

        # 다양한 응답 패턴
        patterns = [
            (f"데비: {name}! {rest}\n마를렌: 쓸만한 장비지."),
            (f"데비: 오~ {name}이잖아!\n마를렌: {original}"),
            (f"데비: {name}? 알지~\n마를렌: {rest}"),
        ]

        questions = [f"{name} 뭐야?", f"{name} 어때?", f"{name} 알아?"]

        dataset.append({
            "conversations": [
                {"from": "human", "value": random.choice(questions)},
                {"from": "gpt", "value": random.choice(patterns)},
            ]
        })

    return dataset


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    print("=== 데비&마를렌 파인튜닝 데이터셋 v2 ===\n")

    # 1) 대사 수집 (나무위키 + TTS)
    all_quotes = []

    namu_path = RAW_DIR / "namu_debi_marlene_main.txt"
    if namu_path.exists():
        namu = parse_namuwiki(str(namu_path))
        all_quotes.extend(namu)
        print(f"[수집] 나무위키: {len(namu)}개")

    tts_debi = BASE_DIR / "debi_finetune.jsonl"
    tts_marlene = BASE_DIR / "marlene_finetune.jsonl"
    if tts_debi.exists():
        tts_d = parse_tts_jsonl(str(tts_debi), "debi")
        tts_m = parse_tts_jsonl(str(tts_marlene), "marlene")
        all_quotes.extend(tts_d)
        all_quotes.extend(tts_m)
        print(f"[수집] TTS: {len(tts_d) + len(tts_m)}개")

    print(f"[수집] 총 대사: {len(all_quotes)}개\n")

    # Part 1: 말투 학습
    print("[Part 1] 말투 학습 데이터 생성...")
    part1, seen = build_part1_dialogue(all_quotes)
    print(f"  생성: {len(part1)}개 (중복 제거 후)")

    # Part 2: Q&A 대화
    print("[Part 2] Q&A 대화 데이터 생성...")
    part2 = build_part2_qa()
    print(f"  생성: {len(part2)}개")

    # Part 3: 게임 지식
    vlm_path = BASE_DIR.parent / "vlm_training" / "dataset" / "eternal_return_vlm_dataset.json"
    part3 = []
    if vlm_path.exists():
        print("[Part 3] 게임 지식 데이터 생성...")
        part3 = build_part3_items(str(vlm_path), max_items=200)
        print(f"  생성: {len(part3)}개")

    # 합치기 + 셔플
    all_data = part1 + part2 + part3
    random.shuffle(all_data)

    # 저장
    train_path = OUTPUT_DIR / "train.json"
    with open(train_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # 통계
    print(f"\n=== 최종 결과 ===")
    print(f"Part 1 (말투): {len(part1)}개")
    print(f"Part 2 (Q&A):  {len(part2)}개")
    print(f"Part 3 (지식): {len(part3)}개")
    print(f"합계: {len(all_data)}개")
    print(f"\n저장: {train_path}")

    # 샘플 출력
    print("\n=== 샘플 확인 ===")
    for label, data_slice in [("Part 1", part1[:2]), ("Part 2", part2[:2]), ("Part 3", part3[:2])]:
        print(f"\n--- {label} ---")
        for d in data_slice:
            print(f"  user: {d['conversations'][0]['value']}")
            print(f"  asst: {d['conversations'][1]['value']}")


if __name__ == "__main__":
    main()
