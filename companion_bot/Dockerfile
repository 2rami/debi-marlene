FROM python:3.12-slim

WORKDIR /app

# Layer 1: dependencies (캐시 잘 됨, 코드만 바뀌면 재설치 X)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: 봇 코드
COPY main.py .

# 런타임 사용자 (root 회피)
RUN useradd -m -u 1000 bot && chown -R bot:bot /app
USER bot

CMD ["python", "-u", "main.py"]
