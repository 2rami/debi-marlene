import os
import glob
import pandas as pd
import whisper
import torch
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from trainer import Trainer, TrainerArgs

# PyTorch 2.6+ 호환성 패치 (weights_only=False 강제 적용)
# Coqui TTS가 내부적으로 torch.load를 호출할 때 weights_only 인자를 전달하지 않아 발생하는 오류 수정
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

# 설정
# Docker에서 실행 시 /app/dataset 등으로 마운트 가능
DATASET_DIR = os.getenv("DATASET_DIR", r"c:\TTs\debi-marlene-dataset\Debi&Marlene_KOR")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "assets/models/debi_marlene_finetuned")
METADATA_FILE = "metadata.csv"
BATCH_SIZE = 4
EPOCHS = 10  # 적절히 조절

def transcribe_dataset():
    """데이터셋의 오디오 파일들을 Whisper로 전사하여 메타데이터 생성"""
    print("Whisper 모델 로딩 중...")
    model = whisper.load_model("medium")  # 정확도를 위해 medium 이상 권장
    
    wav_files = glob.glob(os.path.join(DATASET_DIR, "*.wav"))
    data = []
    
    print(f"총 {len(wav_files)}개의 오디오 파일 발견. 자막 생성 시작...")
    
    for i, wav_path in enumerate(wav_files):
        try:
            # 전사 (Transcribe)
            result = model.transcribe(wav_path, language="ko")
            text = result["text"].strip()
            
            if text:
                # XTTS 학습 포맷: audio_file|text|speaker_name
                # 파일명에서 캐릭터 이름 추측 (Debi_... or Marlene_...)
                filename = os.path.basename(wav_path)
                if filename.lower().startswith("debi"):
                    speaker = "debi"
                elif filename.lower().startswith("marlene"):
                    speaker = "marlene"
                else:
                    speaker = "debi" # 기본값
                
                data.append({
                    "audio_file": wav_path,
                    "text": text,
                    "speaker_name": speaker,
                    "language": "ko"
                })
                print(f"[{i+1}/{len(wav_files)}] {speaker}: {text}")
        except Exception as e:
            print(f"오류 발생 ({wav_path}): {e}")

    # 메타데이터 저장
    df = pd.DataFrame(data)
    # XTTS 포맷에 맞게 csv 저장 (audio_file|text|speaker_name)
    # 구분자는 | 사용
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        for item in data:
            f.write(f"{item['audio_file']}|{item['text']}|{item['speaker_name']}\n")
            
    print(f"메타데이터 생성 완료: {METADATA_FILE}")
    return METADATA_FILE

def train_model(metadata_path):
    """XTTS 모델 파인튜닝"""
    print("XTTS 파인튜닝 시작...")
    
    # 1. 기본 모델 및 설정 준비
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    print(f"기본 모델({model_name}) 다운로드 및 로드 중...")
    
    # 모델 매니저를 통해 경로 확인 (다운로드 유도)
    from TTS.utils.manage import ModelManager
    manager = ModelManager()
    model_path = manager.download_model(model_name)
    
    # download_model이 튜플을 반환하는 경우 처리
    if isinstance(model_path, tuple):
        model_path = model_path[0]
        
    # model_path가 파일(model.pth)을 가리키는 경우 디렉토리로 변환
    if os.path.isfile(model_path):
        model_dir = os.path.dirname(model_path)
    else:
        model_dir = model_path
        
    # 디버깅용 로그
    print(f"모델 경로: {model_path}")
    print(f"모델 디렉토리: {model_dir}")
    
    # 2. 설정(Config) 초기화
    config = XttsConfig()
    config.load_json(os.path.join(model_dir, "config.json"))
    
    # 3. 데이터셋 포맷터 정의
    def formatter(root_path, manifest_file, **kwargs):
        """metadata.csv 파일을 읽어서 TTS 학습 포맷으로 변환"""
        txt_file = os.path.join(root_path, manifest_file)
        items = []
        with open(txt_file, "r", encoding="utf-8") as f:
            for line in f:
                cols = line.strip().split("|")
                # audio_file|text|speaker_name
                wav_file = cols[0]
                text = cols[1]
                speaker_name = cols[2]
                items.append({
                    "text": text,
                    "audio_file": wav_file,
                    "speaker_name": speaker_name,
                    "language": "ko"
                })
        return items

    # 4. 학습 파라미터 설정
    # XTTS v2 Config 구조에 맞게 수정
    config.batch_size = BATCH_SIZE
    config.eval_batch_size = BATCH_SIZE
    # config.dataset_conf 대신 직접 속성 설정이 필요할 수 있음 (버전 차이)
    # 하지만 XTTS 학습은 보통 별도의 BaseDatasetConfig를 사용하거나 args로 전달함.
    # 여기서는 간단히 output_path와 에폭만 설정하고 나머지는 기본값 사용 시도
    
    config.output_path = OUTPUT_DIR
    config.train_epochs = EPOCHS
    
    # 학습 데이터 경로 설정 (TrainerArgs에 전달되므로 여기선 생략 가능할 수도 있으나 명시)
    # config에 직접 데이터셋 경로를 넣는 필드가 없을 수 있음.
    
    # 5. 모델 초기화
    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir=model_dir, eval=True)

    # 6. Trainer 초기화 및 실행
    print("Trainer 초기화 중...")

    # XTTS 모델에 get_criterion 메서드가 없어서 Trainer에서 오류가 발생함
    # 이를 해결하기 위해 더미 메서드 추가 (XTTS는 내부적으로 loss를 계산함)
    if not hasattr(model, "get_criterion"):
        model.get_criterion = lambda: None

    # TrainerArgs 설정
    trainer_args = TrainerArgs()
    trainer_args.restore_path = None
    trainer_args.skip_train_epoch = False
    trainer_args.print_step = 25
    trainer_args.plot_step = 100
    trainer_args.save_step = 1000
    trainer_args.save_n_checkpoints = 5
    trainer_args.save_checkpoints = True

    # Trainer 초기화
    trainer = Trainer(
        args=trainer_args,
        config=config,
        output_path=OUTPUT_DIR,
        model=model,
        train_samples=formatter(os.path.dirname(METADATA_FILE), os.path.basename(METADATA_FILE)),
        eval_samples=None  # 평가 데이터셋은 선택사항
    )

    # 학습 시작
    print("\n학습을 시작합니다...")
    print(f"출력 폴더: {OUTPUT_DIR}")
    print(f"에포크: {EPOCHS}")
    print(f"배치 크기: {BATCH_SIZE}")

    trainer.fit()

    print("\n학습 완료!")
    print(f"모델 저장 위치: {OUTPUT_DIR}")


if __name__ == "__main__":
    import sys

    # 명령줄 인자 확인
    if len(sys.argv) > 1:
        if sys.argv[1] == "transcribe":
            # 1. 자막 생성만 실행
            print("Whisper로 자막 생성을 시작합니다...")
            metadata_file = transcribe_dataset()
            print(f"\n자막 생성 완료: {metadata_file}")
            print("\n학습을 시작하려면:")
            print("python train_voice.py train")
        elif sys.argv[1] == "train":
            # 2. 학습만 실행 (메타데이터 파일이 이미 있다고 가정)
            if not os.path.exists(METADATA_FILE):
                print(f"오류: {METADATA_FILE} 파일이 없습니다.")
                print("먼저 자막을 생성하세요: python train_voice.py transcribe")
                sys.exit(1)
            print("\n학습을 시작합니다...")
            train_model(METADATA_FILE)
        else:
            print("사용법:")
            print("  python train_voice.py transcribe  # 자막 생성")
            print("  python train_voice.py train       # 모델 학습")
    else:
        # 인자 없으면 전체 프로세스 실행
        print("=== 전체 프로세스 시작 ===\n")

        # 1. 자막 생성 (메타데이터 파일이 없을 경우에만)
        if not os.path.exists(METADATA_FILE):
            print("[1/2] Whisper로 자막 생성 중...")
            metadata_file = transcribe_dataset()
        else:
            print(f"[1/2] 기존 메타데이터 파일 사용: {METADATA_FILE}")
            metadata_file = METADATA_FILE

        # 2. 학습
        print("\n[2/2] 모델 학습 시작...")
        train_model(metadata_file)
