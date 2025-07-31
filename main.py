#!/usr/bin/env python3
"""
데비&마를렌 디스코드 봇 - 메인 실행 파일
이터널리턴 전적 검색과 AI 채팅 기능을 제공하는 Discord 봇
"""

import sys
import asyncio
from run.discord_bot import run_bot
# 테스트
def main():
    """메인 실행 함수"""
    # 봇 실행
    print("🚀 데비&마를렌 봇을 시작합니다...")
    run_bot()

if __name__ == "__main__":
    main()