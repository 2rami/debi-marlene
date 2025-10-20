#!/usr/bin/env python3
"""
데비&마를렌 디스코드 봇 - 메인 실행 파일
이터널리턴 전적 검색과 AI 채팅 기능을 제공하는 Discord 봇
"""

import sys
import asyncio
import os
from run.discord_bot import run_bot
# 테스트
def main():
    """메인 실행 함수"""
    print("🚀 데비&마를렌 봇을 시작합니다...", flush=True)
    sys.stdout.flush()
    print(f"🔧 환경변수 체크:", flush=True)
    sys.stdout.flush()
    print(f"  - DISCORD_TOKEN: {'설정됨' if os.getenv('DISCORD_TOKEN') else '없음'}", flush=True)
    sys.stdout.flush()
    print(f"  - YOUTUBE_API_KEY: {'설정됨' if os.getenv('YOUTUBE_API_KEY') else '없음'}", flush=True)
    sys.stdout.flush()
    print(f"  - YOUTUBE_API_KEY 길이: {len(os.getenv('YOUTUBE_API_KEY', ''))}", flush=True)
    sys.stdout.flush()
    
    # 봇 실행
    print("🔧 run_bot() 함수를 호출합니다...", flush=True)
    sys.stdout.flush()
    run_bot()

if __name__ == "__main__":
    main()