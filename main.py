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
    _identity = config.BOT_IDENTITY
    _label = {"debi": "Debi 솔로봇", "marlene": "Marlene 솔로봇"}.get(_identity, "데비&마를렌 봇")
    print(f"[시작] {_label}을(를) 시작합니다... (identity={_identity})", flush=True)
    try:
        run_bot()
    except KeyboardInterrupt:
        # Ctrl+C → asyncio 루프가 이미 깨진 상태. 동기 HTTP로 알림 전송 (fallback)
        # bot.close()의 async notify가 정상 실행됐으면 중복될 수 있지만, 못 보내는 것보단 나음
        print("[종료] 사용자 요청(Ctrl+C)으로 봇 종료", flush=True)
        try:
            from run.services.webhook_logger import notify_bot_stopping_sync
            notify_bot_stopping_sync()
        except Exception as e:
            print(f"[경고] 종료 알림 전송 실패: {e}", flush=True)
    except Exception as e:
        print(f"[크래시] 봇 프로세스가 예외로 종료되었습니다: {e}", flush=True)
        from run.services.webhook_logger import notify_crash
        notify_crash(e)
        raise


if __name__ == "__main__":
    main()