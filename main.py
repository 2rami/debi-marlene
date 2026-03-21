#!/usr/bin/env python3
"""
데비&마를렌 디스코드 봇 - 메인 실행 파일
이터널리턴 전적 검색과 AI 채팅 기능을 제공하는 Discord 봇
"""

import sys
import os
import asyncio
import io

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from run.core.bot import bot
from run.core import config


def run_bot():
    """Discord 봇 실행"""
    DISCORD_TOKEN = config.DISCORD_TOKEN

    if not DISCORD_TOKEN:
        print("CRITICAL: DISCORD_TOKEN이 설정되지 않았습니다.")
        return

    # Discord 봇 실행 (Cog 등록은 setup_hook에서 자동 처리)
    bot.run(DISCORD_TOKEN)


def main():
    """메인 실행 함수"""
    print("[시작] 데비&마를렌 봇을 시작합니다...", flush=True)
    run_bot()


if __name__ == "__main__":
    main()