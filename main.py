#!/usr/bin/env python3
"""
데비&마를렌 디스코드 봇 - 메인 실행 파일
이터널리턴 전적 검색과 AI 채팅 기능을 제공하는 Discord 봇
"""

import sys
import asyncio
from api_clients import test_dakgg_api_structure
from discord_bot import run_bot

def main():
    """메인 실행 함수"""
    # API 테스트 모드
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("DAKGG API 구조 테스트 모드")
        asyncio.run(test_dakgg_api_structure())
        return
    
    # 봇 실행
    print("🚀 데비&마를렌 봇을 시작합니다...")
    run_bot()

if __name__ == "__main__":
    main()