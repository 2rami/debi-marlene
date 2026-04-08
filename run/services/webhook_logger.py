"""
Discord Webhook을 통한 봇 상태/에러 알림 서비스

봇이 살아있든 죽어있든 Webhook URL로 직접 HTTP 요청을 보내기 때문에
봇 프로세스 크래시 시에도 알림이 가능합니다.
"""

import aiohttp
import requests
import traceback
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

# .env에서 로드
_webhook_url = None


def _get_webhook_url():
    """Webhook URL을 가져옵니다 (lazy load)."""
    global _webhook_url
    if _webhook_url is None:
        import os
        _webhook_url = os.getenv("DISCORD_LOG_WEBHOOK", "")
    return _webhook_url


def _build_payload(title: str, description: str, color: int):
    """Webhook embed payload를 생성합니다."""
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    return {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {"text": now}
        }]
    }


# ========== 동기 전송 (봇이 죽었을 때 사용) ==========

def send_sync(title: str, description: str, color: int = 0xFF0000):
    """동기 방식으로 Webhook 전송 (봇 크래시 시 사용).

    asyncio 이벤트 루프가 없어도 동작합니다.
    """
    url = _get_webhook_url()
    if not url:
        return

    try:
        payload = _build_payload(title, description, color)
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass


# ========== 비동기 전송 (봇이 살아있을 때 사용) ==========

async def send_async(title: str, description: str, color: int = 0xFF0000):
    """비동기 방식으로 Webhook 전송 (봇 런타임 에러 시 사용)."""
    url = _get_webhook_url()
    if not url:
        return

    try:
        payload = _build_payload(title, description, color)
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10))
    except Exception:
        pass


# ========== 편의 함수 ==========

async def notify_bot_started():
    """봇 시작 알림."""
    await send_async(
        "[시작] 봇이 시작되었습니다",
        "데비&마를렌 봇이 정상적으로 시작되었습니다.\n\n"
        "[서포트 서버](https://discord.gg/aDemda3qC9) | "
        "[채팅 채널](https://discord.com/channels/1466273572115972149/1489047618020442194) | "
        "[봇 상태](https://debimarlene.com)",
        color=0x2ECC71  # 초록
    )


async def notify_bot_stopping():
    """봇 정상 종료 알림."""
    await send_async(
        "[종료] 봇이 종료됩니다",
        "데비&마를렌 봇이 정상적으로 종료됩니다.",
        color=0xF39C12  # 주황
    )


async def notify_error(error: Exception, context: str = ""):
    """런타임 에러 알림."""
    tb = traceback.format_exception(type(error), error, error.__traceback__)
    tb_text = "".join(tb)

    # Discord embed description 최대 4096자
    if len(tb_text) > 3500:
        tb_text = tb_text[:1750] + "\n...(중략)...\n" + tb_text[-1750:]

    desc = ""
    if context:
        desc += f"**위치:** {context}\n"
    desc += f"**에러:** {type(error).__name__}: {error}\n"
    desc += f"```\n{tb_text}\n```"

    await send_async(
        "[에러] 봇에서 에러가 발생했습니다",
        desc,
        color=0xFF0000  # 빨강
    )


def notify_crash(error: Exception):
    """봇 프로세스 크래시 알림 (동기).

    main.py에서 봇이 예외로 죽었을 때 호출합니다.
    이 시점에서는 asyncio 루프가 없으므로 동기 requests를 사용합니다.
    """
    tb = traceback.format_exception(type(error), error, error.__traceback__)
    tb_text = "".join(tb)

    if len(tb_text) > 3500:
        tb_text = tb_text[:1750] + "\n...(중략)...\n" + tb_text[-1750:]

    desc = f"**에러:** {type(error).__name__}: {error}\n"
    desc += f"```\n{tb_text}\n```"

    send_sync(
        "[크래시] 봇 프로세스가 종료되었습니다",
        desc,
        color=0xE74C3C  # 진한 빨강
    )
