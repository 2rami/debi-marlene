"""
CosyVoice3 학습 데이터 전처리 스크립트

fish_speech_data/{Debi,Marlene}/ 에서 .wav + .lab 파일을 읽어
CosyVoice3 학습에 필요한 Kaldi 포맷으로 변환합니다.

처리 과정:
  1. 텍스트 정규화 (숫자->한글, 영문->한글 발음)
  2. 오디오 정제 (silence trim, normalize, 24kHz 리샘플)
  3. 스타일 태그 자동 분류 (excited/sad/happy/calm)
  4. Kaldi 포맷 출력 (wav.scp, text, utt2spk, spk2utt)
  5. metadata.csv 생성

실행:
    python prepare_cosyvoice3_data.py
    # -> style_review.csv 확인/수정 후
    python prepare_cosyvoice3_data.py --apply-review style_review.csv
"""

import os
import re
import csv
import random
import argparse
import unicodedata
from pathlib import Path
from collections import defaultdict

import numpy as np

# ─────────────────────────────────────────────
# 설정
# ─────────────────────────────────────────────

SOURCE_DIR = Path(__file__).parent / "fish_speech_data"
OUTPUT_DIR = Path(__file__).parent / "cosyvoice3_data"
SPEAKERS = ["Debi", "Marlene"]
TARGET_SR = 24000
DEV_RATIO = 0.1  # 10% 홀드아웃

# ─────────────────────────────────────────────
# A) 텍스트 정규화
# ─────────────────────────────────────────────

# 숫자 -> 한글 변환 테이블
DIGIT_KO = {
    "0": "영", "1": "일", "2": "이", "3": "삼", "4": "사",
    "5": "오", "6": "육", "7": "칠", "8": "팔", "9": "구",
}

# 서수/카운터 숫자 (1~10)
COUNTER_KO = {
    "1": "한", "2": "두", "3": "세", "4": "네", "5": "다섯",
    "6": "여섯", "7": "일곱", "8": "여덟", "9": "아홉", "10": "열",
}

# 영문 약어 -> 한글 발음
ENGLISH_KO = {
    "OK": "오케이", "HP": "에이치피", "MP": "엠피",
    "CC": "시시", "PVP": "피브이피", "PVE": "피브이이",
    "GG": "지지", "MVP": "엠브이피", "DPS": "디피에스",
    "AP": "에이피", "AD": "에이디",
}


def normalize_numbers(text: str) -> str:
    """숫자를 한글 발음으로 변환"""
    # "N번" -> "N번" (서수)
    def replace_counter(m):
        num = m.group(1)
        if num in COUNTER_KO:
            return COUNTER_KO[num] + m.group(2)
        return num_to_korean(int(num)) + m.group(2)

    text = re.sub(r"(\d+)(번|개|명|마리|층)", replace_counter, text)

    # 남은 순수 숫자
    def replace_digit_seq(m):
        return "".join(DIGIT_KO.get(d, d) for d in m.group(0))

    text = re.sub(r"\d+", replace_digit_seq, text)
    return text


def num_to_korean(n: int) -> str:
    """정수를 한글로 변환 (간단 버전, 1~99)"""
    if n <= 0:
        return "영"
    if n <= 10:
        return COUNTER_KO.get(str(n), str(n))

    tens = n // 10
    ones = n % 10
    result = ""
    if tens > 1:
        result += DIGIT_KO[str(tens)]
    if tens >= 1:
        result += "십"
    if ones > 0:
        result += DIGIT_KO[str(ones)]
    return result


def normalize_english(text: str) -> str:
    """영문 약어를 한글 발음으로 변환"""
    for eng, ko in ENGLISH_KO.items():
        text = re.sub(rf"\b{eng}\b", ko, text, flags=re.IGNORECASE)
    return text


def normalize_text(text: str) -> str:
    """전체 텍스트 정규화 파이프라인"""
    text = text.strip()
    text = normalize_english(text)
    text = normalize_numbers(text)
    # 연속 공백 제거
    text = re.sub(r"\s+", " ", text)
    return text


# ─────────────────────────────────────────────
# B) 오디오 정제
# ─────────────────────────────────────────────

def process_audio(input_path: str, output_path: str) -> bool:
    """
    오디오 파일을 정제합니다.
    - silence trim (top_db=30)
    - peak normalize (-1dB)
    - 24kHz 리샘플
    - 16-bit WAV 저장

    Returns:
        True if successful, False otherwise
    """
    import librosa
    import soundfile as sf

    try:
        # 원본 로드 (mono, 원본 SR)
        y, sr = librosa.load(input_path, sr=None, mono=True)

        # silence trim
        y_trimmed, _ = librosa.effects.trim(y, top_db=30)

        # 너무 짧은 오디오 스킵 (0.3초 미만)
        if len(y_trimmed) / sr < 0.3:
            print(f"  [SKIP] 너무 짧음: {input_path} ({len(y_trimmed)/sr:.2f}s)")
            return False

        # peak normalize (-1dB = 0.891)
        peak = np.max(np.abs(y_trimmed))
        if peak > 0:
            y_trimmed = y_trimmed * (0.891 / peak)

        # 24kHz 리샘플 (soxr_hq로 고주파 에일리어싱 방지)
        if sr != TARGET_SR:
            y_resampled = librosa.resample(
                y_trimmed, orig_sr=sr, target_sr=TARGET_SR, res_type="soxr_hq"
            )
        else:
            y_resampled = y_trimmed

        # 16-bit WAV 저장
        sf.write(output_path, y_resampled, TARGET_SR, subtype="PCM_16")
        return True

    except Exception as e:
        print(f"  [ERROR] 오디오 처리 실패: {input_path} - {e}")
        return False


# ─────────────────────────────────────────────
# C) 스타일 태그 분류
# ─────────────────────────────────────────────

# 카테고리 -> 스타일 매핑 (파일명의 카테고리 부분 기준)
STYLE_MAP = {
    # [excited] - 전투 승리, 레전드급 이벤트, 스킬, 무기, 가속
    "excited": [
        "battlearewin", "craftlegend", "craftepic", "craftrare",
        "skillq", "skillw", "skille", "skillr", "skillpassive",
        "weaponskill", "accelerationline",
        "readyultimate", "notreadyultimate",
        "getrskill", "kill", "finishenemyteam",
        "cobaltkilldrone", "cobaloccupation",
        "victory", "exitsucess", "taunt",
        "completefullroute", "completeroute",
    ],
    # [sad] - 죽음, 패배, 사과
    "sad": [
        "sorry", "killedby", "killedcommon", "killeddoppelganger",
        "cobaltimminentlose", "lost", "surrender",
    ],
    # [happy] - 긍정, 감사, 캠프파이어, 수집
    "happy": [
        "good", "thanks", "bonfire", "collect",
        "joke", "revive", "resurrection",
        "makedrink", "makefood", "rest",
    ],
    # [calm] - 나머지 전부 (이동, 핑, 정보, 일반)
}


def classify_style(filename: str) -> str:
    """파일명에서 카테고리를 추출하고 스타일을 분류합니다."""
    # "Debi_battleAreaWin_1_01_01" -> "battleareawin"
    parts = filename.split("_")
    if len(parts) < 2:
        return "[calm]"

    # 스피커 이름 제거, 카테고리 추출
    # Debi_battleAreaWin_1_01_01 -> battleAreaWin
    category = parts[1].lower()

    for style, keywords in STYLE_MAP.items():
        for kw in keywords:
            if category.startswith(kw):
                return f"[{style}]"

    return "[calm]"


# ─────────────────────────────────────────────
# D) utt_id 정규화
# ─────────────────────────────────────────────

def sanitize_utt_id(filename: str) -> str:
    """
    파일명을 Kaldi 호환 utt_id로 변환
    - 소문자
    - 한글/특수문자 제거
    - 공백 -> 언더스코어
    """
    # 확장자 제거
    name = Path(filename).stem
    # ASCII + 숫자 + 언더스코어만 남기기
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)
    name = name.lower()
    # 연속 언더스코어 정리
    name = re.sub(r"_+", "_", name)
    return name


# ─────────────────────────────────────────────
# 메인 처리
# ─────────────────────────────────────────────

def scan_data(speakers: list[str]) -> list[dict]:
    """모든 .wav + .lab 쌍을 스캔하고 메타데이터를 수집합니다."""
    entries = []

    for speaker in speakers:
        speaker_dir = SOURCE_DIR / speaker
        if not speaker_dir.exists():
            print(f"[WARNING] 디렉토리 없음: {speaker_dir}")
            continue

        # .wav 파일 목록
        wav_files = sorted(speaker_dir.glob("*.wav"))

        for wav_path in wav_files:
            lab_path = wav_path.with_suffix(".lab")

            if not lab_path.exists():
                print(f"  [WARNING] .lab 없음: {wav_path.name}")
                continue

            # .lab 읽기
            text = lab_path.read_text(encoding="utf-8").strip()
            if not text:
                print(f"  [WARNING] 빈 텍스트: {lab_path.name}")
                continue

            utt_id = sanitize_utt_id(wav_path.name)
            style = classify_style(wav_path.stem)

            entries.append({
                "speaker": speaker.lower(),
                "wav_path": str(wav_path),
                "lab_path": str(lab_path),
                "filename": wav_path.stem,
                "utt_id": utt_id,
                "text_raw": text,
                "text_normalized": normalize_text(text),
                "style": style,
            })

    return entries


def write_style_review(entries: list[dict], output_path: Path):
    """스타일 분류 검토용 CSV를 생성합니다."""
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(["filename", "speaker", "text", "style"])
        for e in entries:
            writer.writerow([e["filename"], e["speaker"], e["text_normalized"], e["style"]])

    print(f"\nstyle_review.csv 생성: {output_path}")
    print("  -> 스타일 분류를 확인/수정한 후 --apply-review 옵션으로 재실행하세요.")


def load_style_review(review_path: Path, entries: list[dict]) -> list[dict]:
    """수정된 style_review.csv를 적용합니다."""
    review_map = {}
    with open(review_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter="|")
        next(reader)  # 헤더 스킵
        for row in reader:
            if len(row) >= 4:
                filename, _, _, style = row[0], row[1], row[2], row[3]
                review_map[filename] = style.strip()

    changed = 0
    for e in entries:
        if e["filename"] in review_map:
            new_style = review_map[e["filename"]]
            if new_style != e["style"]:
                e["style"] = new_style
                changed += 1

    print(f"스타일 리뷰 적용: {changed}개 수정됨")
    return entries


def print_balance_report(entries: list[dict]):
    """스피커별 x 스타일별 개수 리포트를 출력합니다."""
    counts = defaultdict(lambda: defaultdict(int))
    for e in entries:
        counts[e["speaker"]][e["style"]] += 1

    all_styles = sorted(set(e["style"] for e in entries))

    print("\n=== 감정 태그 밸런스 리포트 ===")
    header = f"{'Speaker':<10}" + "".join(f"{s:<12}" for s in all_styles) + "Total"
    print(header)
    print("-" * len(header))

    for speaker in sorted(counts.keys()):
        row = f"{speaker:<10}"
        total = 0
        for style in all_styles:
            c = counts[speaker][style]
            total += c
            row += f"{c:<12}"
        row += str(total)
        print(row)
    print()


def build_kaldi_data(entries: list[dict], output_dir: Path):
    """Kaldi 포맷 파일들을 생성합니다."""
    import librosa

    # train/dev 분할 (스피커별 균등)
    random.seed(42)
    by_speaker = defaultdict(list)
    for e in entries:
        by_speaker[e["speaker"]].append(e)

    train_entries = []
    dev_entries = []

    for speaker, speaker_entries in by_speaker.items():
        random.shuffle(speaker_entries)
        n_dev = max(1, int(len(speaker_entries) * DEV_RATIO))
        dev_entries.extend(speaker_entries[:n_dev])
        train_entries.extend(speaker_entries[n_dev:])

    print(f"Train: {len(train_entries)}개, Dev: {len(dev_entries)}개")

    # utt_id 중복 체크 & 해결
    seen_ids = {}
    for entries_list in [train_entries, dev_entries]:
        for e in entries_list:
            uid = e["utt_id"]
            if uid in seen_ids:
                # 중복 시 숫자 접미사 추가
                i = 2
                while f"{uid}_{i}" in seen_ids:
                    i += 1
                e["utt_id"] = f"{uid}_{i}"
            seen_ids[e["utt_id"]] = True

    for split_name, split_entries in [("train", train_entries), ("dev", dev_entries)]:
        split_dir = output_dir / split_name
        wavs_dir = split_dir / "wavs"
        wavs_dir.mkdir(parents=True, exist_ok=True)

        wav_scp = []
        text_lines = []
        utt2spk = []
        spk2utt_map = defaultdict(list)

        processed = 0
        skipped = 0

        for e in split_entries:
            utt_id = e["utt_id"]
            speaker = e["speaker"]
            out_wav = wavs_dir / f"{utt_id}.wav"

            # 오디오 처리
            if not process_audio(e["wav_path"], str(out_wav)):
                skipped += 1
                continue

            # CosyVoice3 텍스트 포맷:
            # "You are a helpful assistant.<|endofprompt|>[style]텍스트"
            cosyvoice_text = (
                f"You are a helpful assistant.<|endofprompt|>"
                f"{e['style']}{e['text_normalized']}"
            )

            wav_scp.append(f"{utt_id} {out_wav}")
            text_lines.append(f"{utt_id} {cosyvoice_text}")
            utt2spk.append(f"{utt_id} {speaker}")
            spk2utt_map[speaker].append(utt_id)

            processed += 1

        # 파일 쓰기
        (split_dir / "wav.scp").write_text("\n".join(wav_scp) + "\n", encoding="utf-8")
        (split_dir / "text").write_text("\n".join(text_lines) + "\n", encoding="utf-8")
        (split_dir / "utt2spk").write_text("\n".join(utt2spk) + "\n", encoding="utf-8")

        spk2utt_lines = []
        for spk, utts in sorted(spk2utt_map.items()):
            spk2utt_lines.append(f"{spk} {' '.join(utts)}")
        (split_dir / "spk2utt").write_text("\n".join(spk2utt_lines) + "\n", encoding="utf-8")

        print(f"  {split_name}: {processed}개 처리, {skipped}개 스킵")

    return train_entries, dev_entries


def write_metadata_csv(entries: list[dict], output_path: Path):
    """참조용 metadata.csv를 생성합니다."""
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(["wav_path", "speaker_id", "text", "style_prompt"])
        for e in entries:
            rel_wav = f"wavs/{e['utt_id']}.wav"
            writer.writerow([rel_wav, e["speaker"], e["text_normalized"], e["style"]])


def main():
    parser = argparse.ArgumentParser(description="CosyVoice3 데이터 전처리")
    parser.add_argument(
        "--apply-review",
        type=str,
        default=None,
        help="수정된 style_review.csv 경로 (스타일 태그 반영)",
    )
    parser.add_argument(
        "--review-only",
        action="store_true",
        help="style_review.csv + 밸런스 리포트만 생성 (오디오 처리 안 함)",
    )
    args = parser.parse_args()

    print("=== CosyVoice3 데이터 전처리 ===\n")

    # 1. 데이터 스캔
    print("[1/5] 데이터 스캔 중...")
    entries = scan_data(SPEAKERS)
    print(f"  총 {len(entries)}개 항목 발견\n")

    if not entries:
        print("데이터가 없습니다. SOURCE_DIR을 확인하세요.")
        return

    # 2. 스타일 리뷰 적용 (있으면)
    if args.apply_review:
        print("[2/5] 스타일 리뷰 적용 중...")
        entries = load_style_review(Path(args.apply_review), entries)
    else:
        print("[2/5] 스타일 리뷰 없음 (자동 분류 사용)")

    # 3. 밸런스 리포트
    print_balance_report(entries)

    # 4. style_review.csv 생성
    review_path = Path(__file__).parent / "style_review.csv"
    write_style_review(entries, review_path)

    if args.review_only:
        print("\n--review-only: 여기서 종료. style_review.csv를 확인하세요.")
        return

    # 5. Kaldi 포맷 빌드 + 오디오 처리
    print("\n[3/5] 오디오 처리 + Kaldi 포맷 생성 중...")
    train_entries, dev_entries = build_kaldi_data(entries, OUTPUT_DIR)

    # 6. metadata.csv 생성
    print("\n[4/5] metadata.csv 생성 중...")
    write_metadata_csv(
        train_entries + dev_entries,
        OUTPUT_DIR / "metadata.csv",
    )

    # 7. 완료 요약
    print("\n[5/5] 완료!")
    print(f"  출력 디렉토리: {OUTPUT_DIR}")
    print(f"  train/wav.scp, text, utt2spk, spk2utt")
    print(f"  dev/wav.scp, text, utt2spk, spk2utt")
    print(f"  metadata.csv")
    print(f"\n다음 단계:")
    print(f"  1. style_review.csv 확인 -> 필요시 수정")
    print(f"  2. python prepare_cosyvoice3_data.py --apply-review style_review.csv")
    print(f"  3. cosyvoice3_data/ 를 Google Drive에 업로드")
    print(f"  4. Colab에서 CosyVoice3_Docker_Finetune.ipynb 실행")


if __name__ == "__main__":
    main()
