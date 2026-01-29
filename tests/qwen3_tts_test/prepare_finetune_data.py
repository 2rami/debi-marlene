"""
Qwen3-TTS 파인튜닝용 데이터 준비 스크립트

voice_transcripts.json에서 Debi 음성만 추출하여
Qwen3-TTS 파인튜닝 형식(JSONL)으로 변환
"""

import json
import os

# 경로 설정
TRANSCRIPT_PATH = "/Users/kasa/Desktop/momewomo/debi-marlene/tts_training/voice_transcripts.json"
AUDIO_BASE_DIR = "/Users/kasa/Desktop/momewomo/debi-marlene/Debi&Marlene_KOR/Debi"
OUTPUT_DIR = "/Users/kasa/Desktop/momewomo/debi-marlene/tests/qwen3_tts_test/finetune_data"

# 참조 오디오 (파인튜닝 시 모든 샘플에 같은 ref_audio 사용)
REF_AUDIO = "Debi_airSupply_2_01.wav"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    # 트랜스크립트 로드
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        transcripts = json.load(f)

    # Debi 음성만 필터링
    debi_data = [t for t in transcripts if t["character"] == "Debi"]
    print(f"전체 데이터: {len(transcripts)}개")
    print(f"Debi 데이터: {len(debi_data)}개")

    # 제외할 파일 패턴 (비대사: 기합, 웃음, 비명 등)
    EXCLUDE_PATTERNS = ['attack', 'die', 'laugh']

    # 유효한 데이터만 필터링
    valid_data = []
    skipped = {"no_file": 0, "short_text": 0, "non_speech": 0}

    for item in debi_data:
        audio_path = os.path.join(AUDIO_BASE_DIR, item["file"])
        filename_lower = item["file"].lower()

        # 파일 존재 확인
        if not os.path.exists(audio_path):
            skipped["no_file"] += 1
            continue

        # 비대사 파일 제외
        if any(pattern in filename_lower for pattern in EXCLUDE_PATTERNS):
            skipped["non_speech"] += 1
            continue

        # 너무 짧은 텍스트 제외 (감탄사 등)
        if len(item["text"]) <= 2:
            skipped["short_text"] += 1
            continue

        valid_data.append({
            "audio": audio_path,
            "text": item["text"],
            "ref_audio": os.path.join(AUDIO_BASE_DIR, REF_AUDIO)
        })

    print(f"\n유효한 데이터: {len(valid_data)}개")
    print(f"스킵된 데이터: 파일없음={skipped['no_file']}, 비대사={skipped['non_speech']}, 짧은텍스트={skipped['short_text']}")

    # JSONL로 저장
    output_path = os.path.join(OUTPUT_DIR, "debi_finetune.jsonl")
    with open(output_path, "w", encoding="utf-8") as f:
        for item in valid_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n저장 완료: {output_path}")

    # 샘플 출력
    print("\n=== 샘플 데이터 (처음 5개) ===")
    for item in valid_data[:5]:
        print(f"  text: {item['text']}")
        print(f"  audio: {os.path.basename(item['audio'])}")
        print()

    # 총 음성 길이 계산
    try:
        import librosa
        total_duration = 0
        for item in valid_data:
            duration = librosa.get_duration(path=item["audio"])
            total_duration += duration
        print(f"총 음성 길이: {total_duration/60:.1f}분 ({total_duration:.0f}초)")
    except Exception as e:
        print(f"음성 길이 계산 실패: {e}")


if __name__ == "__main__":
    main()
