FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 최소화 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python 의존성 파일 복사
COPY requirements.txt .

# 경량 버전 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# 애플리케이션 파일 복사
COPY main.py .
COPY run/ ./run/
COPY assets/ ./assets/

# 불필요한 캐시 정리
RUN find /usr/local -name "*.pyc" -delete && \
    find /usr/local -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 봇 실행
CMD ["python", "main.py"]