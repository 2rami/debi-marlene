FROM python:3.11-slim-bullseye

WORKDIR /app

# 시스템 의존성 — 런타임 필수 + 빌드 시점만 필요한 거 분리.
# 빌드 deps 는 같은 RUN layer 안에서 purge 해서 image 에 안 남김.
#
# 런타임:
#   ffmpeg     : 음성 재생/변환
#   libsndfile1: 오디오 파일 처리
#   tini       : PID 1 SIGTERM 전달 (graceful shutdown)
#   libsodium23: PyNaCl SO (Discord voice)
#   libffi8    : libffi SO
# 빌드 시점:
#   gcc, g++, git, libffi-dev, libnacl-dev — pip wheel 빌드 후 purge
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ffmpeg libsndfile1 tini libsodium23 libffi7 \
        gcc g++ git libffi-dev libnacl-dev; \
    rm -rf /var/lib/apt/lists/*

# Python 의존성 (build deps 살아있는 동안 설치)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt; \
    # 빌드 도구 purge — 같은 layer 끝에 정리하면 image 에 안 남음.
    # 단, dpkg list 로 분리 layer 만들지 말고 단일 RUN.
    apt-get purge -y --auto-remove gcc g++ git libffi-dev libnacl-dev; \
    rm -rf /root/.cache /var/lib/apt/lists/*

# 봇 코드 (.dockerignore 가 dashboard/finetune/vlm_training/chrome_profile/png 등 제외)
COPY . .

EXPOSE 5001

# tini: PID 1 에서 SIGTERM 을 Python 에 전달 (graceful shutdown)
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "main.py"]
