# 🎮 데비&마를렌 로컬 LLM 파인튜닝 가이드

## 📋 준비사항

### 하드웨어 요구사항
- **최소**: 16GB RAM, 6GB+ GPU 메모리
- **권장**: 32GB RAM, 12GB+ GPU 메모리 (RTX 3060 이상)
- **없어도 됨**: CPU로도 가능하지만 매우 느림

### 소프트웨어 설치

```bash
# 1. 가상환경 생성
python -m venv finetune_env
source finetune_env/bin/activate  # Windows: finetune_env\Scripts\activate

# 2. CUDA 설치 (GPU 사용시)
# https://developer.nvidia.com/cuda-downloads 에서 설치

# 3. PyTorch 설치
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. Unsloth 설치
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps xformers

# 5. 추가 라이브러리
pip install datasets transformers trl accelerate
```

## 🏃‍♂️ 빠른 시작

### 1단계: 데이터 준비
이미 만들어진 데이터가 있어요:
- `training_data/debi_dataset.json` - 데비 학습 데이터
- `training_data/marlene_dataset.json` - 마를렌 학습 데이터

더 많은 데이터가 필요하면 각 파일에 대화 예시를 추가하세요!

### 2단계: 파인튜닝 실행

```bash
# 데비 파인튜닝 (20-30분 소요)
python finetune_debi.py

# 마를렌 파인튜닝 (20-30분 소요)  
python finetune_marlene.py
```

### 3단계: 디스코드 봇에 적용

`discord_bot.py`에서 다음 부분을 수정:

```python
# 기존 코드
from run.ai_utils import initialize_claude_api, generate_ai_response

# 새로운 코드로 변경
from run.local_ai_utils import initialize_local_models, generate_local_ai_response

# setup_hook에서
async def setup_hook(self):
    # await initialize_claude_api()  # 이 줄 주석처리
    await initialize_local_models()  # 이 줄 추가

# generate_ai_response를 generate_local_ai_response로 변경
```

## 📊 데이터셋 늘리기

더 정확한 캐릭터를 만들려면 데이터를 더 추가하세요:

```json
{
  "instruction": "You are Debi from Eternal Return. Respond as the cheerful, energetic older twin sister.",
  "input": "사용자 메시지",
  "output": "데비의 응답 (인게임 대사 포함하며 밝고 활발하게)"
}
```

### 데이터 수집 팁
1. **게임내 대사**: 이터널 리턴에서 실제 데비/마를렌 대사 수집
2. **상황별 대화**: 다양한 상황(전투, 일상, 감정 등)에 대한 응답
3. **양 vs 질**: 100개 고품질 > 1000개 저품질

## 🔧 파라미터 조정

### 트레이닝 시간 늘리기
`finetune_debi.py`에서:
```python
max_steps=30,  # 이걸 100-500으로 늘리기
```

### 메모리 부족시
```python
per_device_train_batch_size=1,  # 2에서 1로 줄이기
gradient_accumulation_steps=8,  # 4에서 8로 늘리기
```

## 🐛 문제 해결

### GPU 메모리 부족
```bash
# 더 작은 모델 사용
model_name="unsloth/llama-3.2-1b-instruct-bnb-4bit"
```

### 모델이 이상하게 대답할 때
1. 더 많은 데이터 추가
2. `max_steps` 늘리기 (100-500)
3. `temperature` 조정 (0.7 → 0.5)

### CUDA 에러
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 📈 성능 비교

| 방식 | 속도 | 비용 | 정확도 | 커스터마이징 |
|------|------|------|--------|-------------|
| Claude API | 빠름 | 유료 | 높음 | 제한적 |
| 로컬 파인튜닝 | 보통 | 무료 | 매우높음 | 완전자유 |
| 로컬 기본모델 | 빠름 | 무료 | 낮음 | 제한적 |

## 🎯 다음 단계

1. **더 많은 데이터** 수집해서 정확도 높이기
2. **다른 캐릭터** 추가하기  
3. **음성 생성** 추가하기
4. **이미지 생성** 연동하기

## 💡 팁

- **처음 하는 거면**: 작은 데이터로 먼저 테스트
- **GPU 없으면**: Colab이나 Kaggle 사용
- **시간 오래 걸리면**: 밤에 돌려놓고 자기
- **메모리 부족하면**: 모델 크기 줄이기

질문 있으면 언제든 물어보세요! 🚀