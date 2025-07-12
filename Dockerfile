FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY main.py .
COPY assets/ ./assets/

# 환경 변수 파일 복사 (선택사항) - 실제 운영시에는 docker-compose.yml에서 환경변수 설정
# COPY .env .env

# 포트 노출 (Discord 봇은 포트가 필요하지 않지만 헬스체크용으로 설정)
EXPOSE 8080

# 봇 실행
CMD ["python", "main.py"]