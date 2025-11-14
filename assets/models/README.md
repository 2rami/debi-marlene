# TTS 모델 파일

이 폴더에 미리 학습된 캐릭터별 TTS 모델을 넣어주세요.

## 폴더 구조

```
assets/models/
├── debi/
│   ├── model.pth      # 데비 캐릭터로 학습된 TTS 모델
│   └── config.json    # 모델 설정 파일
├── marlene/
│   ├── model.pth      # 마를렌 캐릭터로 학습된 TTS 모델
│   └── config.json    # 모델 설정 파일
└── default/
    ├── model.pth      # 기본 목소리 모델 (선택)
    └── config.json    # 모델 설정 파일 (선택)
```

## 모델 파일이 없을 경우

**걱정하지 마세요!** 모델 파일이 없어도 봇은 정상 작동합니다.

Coqui TTS의 기본 한국어 음성 모델(`tts_models/ko/kss/vits`)을 자동으로 사용합니다.
기본 음성도 품질이 준수하니 일단 테스트해보세요!

## TTS 모델 학습 방법

캐릭터 목소리로 TTS 모델을 학습하려면 별도의 작업이 필요합니다.

### 1. 학습 데이터 준비

- **음성 데이터**: 최소 30분~1시간 분량의 깨끗한 음성 (잡음 없음)
- **텍스트 스크립트**: 각 음성에 대응하는 텍스트
- **형식**: WAV 파일 (22050Hz 또는 48000Hz, mono)

### 2. Coqui TTS로 학습

로컬 GPU 환경에서 Coqui TTS를 사용해 모델을 fine-tuning합니다:

```bash
# 1. Coqui TTS 설치
pip install TTS

# 2. 학습 데이터셋 준비 (LJSpeech 형식)
# your_dataset/
#   ├── wavs/
#   │   ├── audio1.wav
#   │   ├── audio2.wav
#   │   └── ...
#   └── metadata.csv  # "audio1|텍스트 내용|텍스트 내용"

# 3. 학습 실행
tts-train --config_path path/to/config.json \
          --output_path output/path

# 4. 학습 완료 후 model.pth와 config.json 파일을 해당 캐릭터 폴더에 복사
```

### 3. 외부 서비스 사용

학습이 어렵다면 AI 음성 생성 서비스를 활용할 수 있습니다:

- **ElevenLabs**: Voice cloning 지원, 고품질 (유료)
- **Typecast**: 한국어 지원, 다양한 캐릭터 목소리
- **Resemble AI**: Custom voice 학습 서비스

## 모델 파일 크기 주의

- TTS 모델 파일은 보통 100MB~500MB 정도입니다
- Git에 커밋하지 마세요! (.gitignore에 이미 추가됨)
- GCS나 별도 스토리지에 보관하고 배포 시 다운로드하는 방식 권장

## 서버 설정에서 캐릭터 선택

향후 `/목소리설정` 명령어를 추가하면 서버별로 캐릭터를 선택할 수 있습니다:
- `debi` - 데비 목소리
- `marlene` - 마를렌 목소리
- `default` - 기본 목소리

## 테스트 방법

1. 모델 파일을 해당 캐릭터 폴더에 저장
2. 봇 재시작 (모델 로드에 1~2분 소요)
3. Discord에서 `/음성입장` 후 메시지 전송
4. 캐릭터 목소리로 읽어주는지 확인

## 참고 자료

- [Coqui TTS 문서](https://github.com/coqui-ai/TTS)
- [TTS 모델 학습 가이드](https://tts.readthedocs.io/en/latest/)
