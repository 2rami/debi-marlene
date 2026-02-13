FROM python:3.11-slim-bullseye

WORKDIR /app

# 시스템 의존성 설치
# FFmpeg: 음성 재생용
# libffi-dev, libnacl-dev: PyNaCl 빌드용 (Discord 음성 연결)
# libsndfile1: 오디오 파일 처리
# espeak-ng: TTS 발음 엔진 (Coqui TTS 지원)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    ffmpeg \
    libffi-dev \
    libnacl-dev \
    libsndfile1 \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 포트 노출
EXPOSE 5001

# 봇 실행
CMD ["python", "main.py"]