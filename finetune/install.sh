#!/bin/bash

echo "🚀 데비&마를렌 파인튜닝 환경 설치 시작!"

# 가상환경 생성
echo "📦 가상환경 생성중..."
python -m venv finetune_env
source finetune_env/bin/activate

# PyTorch 설치 (CUDA 지원)
echo "🔥 PyTorch 설치중..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Unsloth 설치
echo "⚡ Unsloth 설치중..."
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps xformers

# 기타 라이브러리 설치
echo "📚 추가 라이브러리 설치중..."
pip install -r requirements.txt

echo "✅ 설치 완료!"
echo "사용 방법:"
echo "1. source finetune_env/bin/activate"
echo "2. python finetune_debi.py"
echo "3. python finetune_marlene.py"