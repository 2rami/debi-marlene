"""
CosyVoice3 파인튜닝 데이터 전처리 스크립트

Usage:
  python prepare_data.py step1 C:/Users/2rami/Downloads/Alex_KOR.zip
  # >> metadata.csv 검수/수정 <<
  python prepare_data.py step2 alex

Eternal Return 음성 파일 → CosyVoice3 학습 데이터 자동 변환
"""

import sys
import os
import re
import csv
import json
import shutil
import zipfile
import random
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR / "workspace"

# === Eternal Return 파일명 → 카테고리/스타일 매핑 ===

# 비대사 (기합, 비명, 웃음 등) → 제외
EXCLUDE_CATEGORIES = {
    "attack", "die", "laugh", "skillQ", "skillW", "skillE", "skillR",
    "weaponskill", "pa",
}

# 카테고리 → 스타일 태그 매핑
STYLE_MAP = {
    # [excited] - 흥분, 승리, 도발
    "killPlayer": "[excited]",
    "victory": "[excited]",
    "highlyPlaced": "[excited]",
    "taunt": "[excited]",
    # [happy] - 기쁨, 농담, 고급 제작
    "joke": "[happy]",
    "craftLegend": "[happy]",
    "craftEpic": "[happy]",
    # [sad] - 패배, 항복
    "surrender": "[sad]",
    "lost": "[sad]",
    # [calm] - 기본값 (이동, 수집, 관찰 등)
}
DEFAULT_STYLE = "[calm]"


def parse_category(filename: str, character: str) -> str:
    """파일명에서 카테고리 추출. Alex_moveInForest1.wav → moveInForest"""
    name = filename.replace(".wav", "")
    # {Character}_ 접두사 제거
    prefix = f"{character}_"
    if name.startswith(prefix):
        name = name[len(prefix):]
    # 끝의 숫자/언더스코어 제거 → 카테고리
    cat = re.sub(r"[\d_]+$", "", name)
    return cat


def get_style_tag(category: str) -> str:
    """카테고리에서 스타일 태그 결정"""
    # 정확한 매칭
    if category in STYLE_MAP:
        return STYLE_MAP[category]
    # 접두사 매칭 (taunt_Aya → taunt → [excited])
    for prefix, style in STYLE_MAP.items():
        if category.startswith(prefix):
            return style
    return DEFAULT_STYLE


def should_include(category: str) -> bool:
    """대사가 있는 파일인지 판단"""
    # 정확히 일치하면 제외
    if category in EXCLUDE_CATEGORIES:
        return False
    # 접두사가 제외 대상이면 제외 (attack_1 등)
    for exclude in EXCLUDE_CATEGORIES:
        if category.startswith(exclude):
            return False
    return True


def step1(zip_path: str):
    """ZIP 압축해제 → Whisper 전사 → metadata.csv 생성"""
    zip_path = Path(zip_path)
    if not zip_path.exists():
        print(f"파일 없음: {zip_path}")
        sys.exit(1)

    # 캐릭터 이름 추출 (Alex_KOR.zip → Alex)
    character = zip_path.stem.replace("_KOR", "").replace("_kor", "")
    char_lower = character.lower()
    work_dir = WORKSPACE / char_lower
    wavs_dir = work_dir / "wavs"

    print(f"=== Step 1: {character} ===")
    print(f"ZIP: {zip_path}")
    print(f"작업 폴더: {work_dir}")

    # 압축 해제
    if wavs_dir.exists():
        shutil.rmtree(wavs_dir)
    wavs_dir.mkdir(parents=True)

    with zipfile.ZipFile(zip_path) as zf:
        wav_files = [f for f in zf.namelist() if f.endswith(".wav")]
        for f in wav_files:
            # 폴더 구조 무시하고 wavs/에 풀기
            basename = os.path.basename(f)
            with zf.open(f) as src, open(wavs_dir / basename, "wb") as dst:
                dst.write(src.read())

    all_wavs = sorted([f for f in os.listdir(wavs_dir) if f.endswith(".wav")])
    print(f"압축 해제: {len(all_wavs)}개 wav 파일")

    # 카테고리 분류
    rows = []
    include_files = []
    for wav in all_wavs:
        cat = parse_category(wav, character)
        style = get_style_tag(cat)
        include = should_include(cat)
        rows.append({
            "filename": wav,
            "text": "",
            "category": cat,
            "style_tag": style if include else "",
            "include": "Y" if include else "N",
        })
        if include:
            include_files.append(wav)

    excluded = len(all_wavs) - len(include_files)
    print(f"대사 파일: {len(include_files)}개, 비대사 제외: {excluded}개")

    # Whisper 전사 (대사 파일만)
    if include_files:
        print(f"\n=== Whisper 전사 시작 ({len(include_files)}개) ===")
        try:
            import whisper
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Device: {device}")
            model = whisper.load_model("large-v3", device=device)

            transcripts = {}
            for i, wav in enumerate(include_files):
                wav_path = str(wavs_dir / wav)
                result = model.transcribe(
                    wav_path,
                    language="ko",
                    initial_prompt="이터널 리턴 게임 캐릭터 대사입니다.",
                )
                text = result["text"].strip()
                transcripts[wav] = text
                if (i + 1) % 10 == 0 or i == 0:
                    print(f"  [{i+1}/{len(include_files)}] {wav}: {text}")

            # 전사 결과 적용
            for row in rows:
                if row["filename"] in transcripts:
                    row["text"] = transcripts[row["filename"]]

            print(f"\nWhisper 전사 완료: {len(transcripts)}개")

        except ImportError:
            print("whisper 미설치. pip install openai-whisper 후 다시 실행하세요.")
            print("text 컬럼이 비어있는 CSV를 생성합니다.")

    # metadata.csv 저장
    csv_path = work_dir / "metadata.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "text", "category", "style_tag", "include"])
        writer.writeheader()
        writer.writerows(rows)

    # 통계
    style_counts = {}
    for row in rows:
        if row["include"] == "Y" and row["style_tag"]:
            style_counts[row["style_tag"]] = style_counts.get(row["style_tag"], 0) + 1

    print(f"\n=== metadata.csv 생성 완료 ===")
    print(f"경로: {csv_path}")
    print(f"스타일 분포: {style_counts}")
    print(f"\n다음 단계:")
    print(f"  1. {csv_path} 열어서 text/style_tag/include 검수")
    print(f"  2. python prepare_data.py step2 {char_lower}")


def step2(character: str):
    """metadata.csv → CosyVoice3 형식 변환 → ZIP"""
    char_lower = character.lower()
    work_dir = WORKSPACE / char_lower
    csv_path = work_dir / "metadata.csv"
    wavs_dir = work_dir / "wavs"

    if not csv_path.exists():
        print(f"metadata.csv 없음: {csv_path}")
        print(f"먼저 step1을 실행하세요.")
        sys.exit(1)

    print(f"=== Step 2: {character} → CosyVoice3 데이터 ===")

    # CSV 읽기
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 포함 대상만 필터
    included = [r for r in rows if r["include"].strip().upper() == "Y" and r["text"].strip()]
    if not included:
        print("포함할 데이터가 없습니다. metadata.csv의 include/text 컬럼을 확인하세요.")
        sys.exit(1)

    print(f"포함: {len(included)}개 / 전체: {len(rows)}개")

    # 24kHz 리샘플링
    try:
        import librosa
        import soundfile as sf
    except ImportError:
        print("pip install librosa soundfile 필요")
        sys.exit(1)

    output_dir = work_dir / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)

    # train/dev 분할 (90/10)
    random.seed(42)
    random.shuffle(included)
    dev_count = max(1, len(included) // 10)
    dev_data = included[:dev_count]
    train_data = included[dev_count:]

    print(f"train: {len(train_data)}개, dev: {len(dev_data)}개")

    for split, data in [("train", train_data), ("dev", dev_data)]:
        split_dir = output_dir / split
        split_wavs = split_dir / "wavs"
        split_wavs.mkdir(parents=True)

        wav_scp_lines = []
        text_lines = []

        for row in data:
            filename = row["filename"]
            text = row["text"].strip()
            style = row["style_tag"].strip()
            src = wavs_dir / filename

            if not src.exists():
                print(f"  SKIP (파일 없음): {filename}")
                continue

            # 24kHz 리샘플링
            audio, _ = librosa.load(str(src), sr=24000)
            dst = split_wavs / filename
            sf.write(str(dst), audio, 24000)

            # utterance ID: 파일명에서 .wav 제거
            utt_id = filename.replace(".wav", "")

            wav_scp_lines.append(f"{utt_id} wavs/{filename}")
            text_lines.append(f"{utt_id} {style}{text}")

        # wav.scp
        with open(split_dir / "wav.scp", "w", encoding="utf-8") as f:
            f.write("\n".join(wav_scp_lines) + "\n")

        # text
        with open(split_dir / "text", "w", encoding="utf-8") as f:
            f.write("\n".join(text_lines) + "\n")

        # instruct_text (text 복사)
        shutil.copy2(split_dir / "text", split_dir / "instruct_text")

        # utt2spk (make_parquet_list.py 필수)
        utt2spk_lines = [f"{utt_id} {char_lower}" for utt_id in
                         [line.split(" ", 1)[0] for line in wav_scp_lines]]
        with open(split_dir / "utt2spk", "w", encoding="utf-8") as f:
            f.write("\n".join(utt2spk_lines) + "\n")

        print(f"  {split}: {len(wav_scp_lines)}개 생성")

    # ZIP 생성
    zip_name = f"cosyvoice3_{char_lower}_data"
    zip_path = work_dir / f"{zip_name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = f"{zip_name}/{file_path.relative_to(output_dir)}"
                zf.write(file_path, arcname)

    print(f"\nZIP 생성: {zip_path} ({zip_path.stat().st_size / 1e6:.1f}MB)")

    # 노트북 복사 + 캐릭터 이름 치환 → workspace/{char}/ 폴더에 저장
    for gpu in ["A100", "T4"]:
        src_nb = SCRIPT_DIR / f"CosyVoice3_Finetune_{gpu}.ipynb"
        if not src_nb.exists():
            continue
        dst_nb = work_dir / f"CosyVoice3_Finetune_{gpu}_{character}.ipynb"

        with open(src_nb, "r", encoding="utf-8") as f:
            content = f.read()

        # CHARACTER 변수 치환
        content = content.replace(
            'CHARACTER = "alex"',
            f'CHARACTER = "{char_lower}"',
        )
        # 데이터 경로 치환 (ZIP에서 풀면 cosyvoice3_data 폴더가 나오므로 유지)
        content = content.replace("cosyvoice3_data", zip_name)

        with open(dst_nb, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"노트북 생성: {dst_nb.name}")

    # 스타일 통계
    style_counts = {}
    for row in included:
        s = row["style_tag"]
        style_counts[s] = style_counts.get(s, 0) + 1

    print(f"\n=== 완료 ===")
    print(f"스타일 분포: {style_counts}")
    print(f"ZIP: {zip_path}")
    print(f"다음 단계:")
    print(f"  1. ZIP을 Google Drive에 업로드")
    print(f"  2. {work_dir.name}/ 폴더의 노트북으로 Colab 학습")
    print(f"  3. 학습 완료 후 체크포인트를 workspace/{char_lower}/checkpoints/에 복사")
    print(f"  4. python prepare_data.py step3 {char_lower}")


def step3(character: str):
    """체크포인트 평균화 + 로컬 추론 테스트"""
    char_lower = character.lower()
    work_dir = WORKSPACE / char_lower
    ckpt_dir = work_dir / "checkpoints"
    wavs_dir = work_dir / "wavs"
    out_dir = work_dir / "test_outputs"

    COSYVOICE_DIR = Path(r"C:\Users\2rami\Desktop\TTS\CosyVoice")
    PRETRAINED = COSYVOICE_DIR / "pretrained_models" / "Fun-CosyVoice3-0.5B"

    if not PRETRAINED.exists():
        print(f"CosyVoice pretrained 모델 없음: {PRETRAINED}")
        sys.exit(1)

    # 체크포인트 찾기
    if not ckpt_dir.exists():
        ckpt_dir.mkdir(parents=True)
        print(f"체크포인트 폴더 생성됨: {ckpt_dir}")
        print(f"Colab에서 학습한 epoch_*_whole.pt 파일들을 여기에 복사하세요.")
        sys.exit(1)

    pt_files = sorted(ckpt_dir.glob("epoch_*_whole.pt"))
    if not pt_files:
        print(f"체크포인트 없음: {ckpt_dir}/epoch_*_whole.pt")
        print(f"Colab Drive에서 체크포인트를 이 폴더로 복사하세요.")
        sys.exit(1)

    print(f"=== Step 3: {character} 체크포인트 평균화 + 추론 ===")
    print(f"체크포인트: {[f.name for f in pt_files]}")

    # PYTHONPATH 설정
    sys.path.insert(0, str(COSYVOICE_DIR / "third_party" / "Matcha-TTS"))
    sys.path.insert(0, str(COSYVOICE_DIR))

    import torch
    import soundfile as sf

    # === 체크포인트 평균화 ===
    print(f"\n--- 체크포인트 평균화 ({len(pt_files)}개) ---")
    SKIP_KEYS = {"epoch", "step"}

    avg_state = torch.load(str(pt_files[0]), map_location="cpu", weights_only=True)
    model_keys = [k for k in avg_state if k not in SKIP_KEYS]

    for pt in pt_files[1:]:
        state = torch.load(str(pt), map_location="cpu", weights_only=True)
        for k in model_keys:
            avg_state[k] = avg_state[k] + state[k]

    for k in model_keys:
        avg_state[k] = avg_state[k] / len(pt_files)

    # 메타데이터 제거 + float32 변환
    for k in SKIP_KEYS:
        avg_state.pop(k, None)
    for k in list(avg_state.keys()):
        if avg_state[k].dtype in (torch.float16, torch.bfloat16):
            avg_state[k] = avg_state[k].float()

    avg_path = ckpt_dir / "llm_avg.pt"
    torch.save(avg_state, str(avg_path))
    print(f"평균화 저장: {avg_path} ({avg_path.stat().st_size / 1e6:.0f}MB)")

    # === 모델 로드 + 파인튜닝 적용 ===
    print(f"\n--- 모델 로드 ---")
    from cosyvoice.cli.cosyvoice import CosyVoice3

    cosyvoice = CosyVoice3(str(PRETRAINED), load_trt=False, fp16=True)

    # 파인튜닝 LLM 교체
    cosyvoice.model.llm.load_state_dict(avg_state, strict=True)
    cosyvoice.model.llm.to(cosyvoice.model.device).eval()
    print(f"파인튜닝 LLM 적용 완료")

    # === 레퍼런스 오디오 선택 ===
    # workspace에서 해당 캐릭터 wav 중 첫 번째 대사 파일 사용
    csv_path = work_dir / "metadata.csv"
    ref_path = None
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["include"].strip().upper() == "Y" and row["text"].strip():
                    candidate = wavs_dir / row["filename"]
                    if candidate.exists():
                        ref_path = str(candidate)
                        break

    if not ref_path:
        print("레퍼런스 오디오를 찾을 수 없습니다.")
        sys.exit(1)

    print(f"레퍼런스: {ref_path}")

    # === 추론 테스트 ===
    out_dir.mkdir(parents=True, exist_ok=True)
    import time

    # metadata.csv에서 스타일별 샘플 텍스트 추출
    test_texts = []
    seen_styles = set()
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["include"].strip().upper() != "Y":
                    continue
                style = row["style_tag"].strip()
                text = row["text"].strip()
                if style and text and style not in seen_styles and len(text) > 5:
                    test_texts.append((text, style))
                    seen_styles.add(style)

    # 기본 테스트도 추가
    test_texts.append(("안녕하세요 오늘 날씨가 좋네요", "[calm]"))

    print(f"\n--- 추론 테스트 ({len(test_texts)}개) ---")
    for i, (text, style) in enumerate(test_texts):
        instruct = "You are a helpful assistant.<|endofprompt|>"
        full_text = f"{style}{text}"
        print(f"\n[{i+1}] {style} \"{text}\"")

        t0 = time.time()
        out = None
        for r in cosyvoice.inference_instruct2(full_text, instruct, ref_path, stream=False):
            out = r["tts_speech"].numpy()
        elapsed = time.time() - t0

        if out is not None:
            out_path = out_dir / f"test_{i+1}_{style.strip('[]')}.wav"
            sf.write(str(out_path), out.flatten(), 24000)
            duration = len(out.flatten()) / 24000
            print(f"  {out_path.name} ({duration:.1f}s, {elapsed:.1f}s)")

    # 평균화된 llm.pt도 별도 저장 (배포용)
    export_path = work_dir / "llm.pt"
    shutil.copy2(str(avg_path), str(export_path))
    print(f"\n=== 완료 ===")
    print(f"평균화 모델: {export_path}")
    print(f"테스트 음성: {out_dir}")
    print(f"\n음성 확인 후 품질이 괜찮으면:")
    print(f"  - {export_path}를 HuggingFace에 업로드하거나")
    print(f"  - CosyVoice pretrained_models에 복사해서 사용")


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python prepare_data.py step1 <zip_path>    # 압축해제 + Whisper + CSV")
        print("  python prepare_data.py step2 <character>   # CSV → CosyVoice3 ZIP + 노트북")
        print("  python prepare_data.py step3 <character>   # 체크포인트 평균화 + 로컬 추론")
        print()
        print("Example:")
        print("  python prepare_data.py step1 C:/Users/2rami/Downloads/Alex_KOR.zip")
        print("  # >> metadata.csv 검수 <<")
        print("  python prepare_data.py step2 alex")
        print("  # >> Colab 학습 후 체크포인트를 workspace/alex/checkpoints/에 복사 <<")
        print("  python prepare_data.py step3 alex")
        sys.exit(1)

    command = sys.argv[1]
    if command == "step1":
        step1(sys.argv[2])
    elif command == "step2":
        step2(sys.argv[2])
    elif command == "step3":
        step3(sys.argv[2])
    else:
        print(f"알 수 없는 명령: {command}")
        print("step1, step2, step3 중 하나를 사용하세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
