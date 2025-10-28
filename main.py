#!/usr/bin/env python3
"""
데비&마를렌 디스코드 봇 - 메인 실행 파일
이터널리턴 전적 검색과 AI 채팅 기능을 제공하는 Discord 봇
"""

import sys
import os
import asyncio

from run.core.bot import bot
from run.core import config
from run.commands import register_all_commands


async def setup():
    """봇 초기화 및 명령어 등록"""
    # 모든 명령어 등록
    await register_all_commands(bot)


def run_bot():
    """Discord 봇 실행"""
    DISCORD_TOKEN = config.DISCORD_TOKEN

    if not DISCORD_TOKEN:
        print("CRITICAL: DISCORD_TOKEN이 설정되지 않았습니다.")
        return

    # 명령어 등록
    asyncio.run(setup())

    # Discord 봇 실행
    bot.run(DISCORD_TOKEN)


def main():
    """메인 실행 함수"""
    print("[시작] 데비&마를렌 봇을 시작합니다...", flush=True)
    run_bot()


if __name__ == "__main__":
    main()