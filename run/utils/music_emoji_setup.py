"""
음악 플레이어 커스텀 이모지 관리

봇 시작 시 음악 컨트롤용 커스텀 이모지가 없으면
Google Material Icons에서 다운로드하여 Discord에 업로드합니다.
"""

import asyncio
import aiohttp
import base64
import logging
from io import BytesIO
from typing import Dict

from PIL import Image

logger = logging.getLogger(__name__)

# Google Material Icons (white, 96x96 PNG)
MUSIC_ICONS = {
    "music_prev": "https://raw.githubusercontent.com/material-icons/material-icons-png/master/png/white/skip_previous/baseline-4x.png",
    "music_pause": "https://raw.githubusercontent.com/material-icons/material-icons-png/master/png/white/pause/baseline-4x.png",
    "music_play": "https://raw.githubusercontent.com/material-icons/material-icons-png/master/png/white/play_arrow/baseline-4x.png",
    "music_skip": "https://raw.githubusercontent.com/material-icons/material-icons-png/master/png/white/skip_next/baseline-4x.png",
    "music_stop": "https://raw.githubusercontent.com/material-icons/material-icons-png/master/png/white/stop/baseline-4x.png",
}


async def ensure_music_emojis(bot) -> Dict[str, str]:
    """
    음악 컨트롤 커스텀 이모지가 Discord에 있는지 확인하고,
    없으면 Material Icons에서 다운로드하여 업로드합니다.

    Returns:
        이모지 이름 -> Discord 이모지 문자열 매핑 (예: {"music_pause": "<:music_pause:123>"})
    """
    app_id = bot.application_id
    if not app_id:
        logger.error("Application ID가 없어 음악 이모지를 업로드할 수 없습니다.")
        return {}

    base_url = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {bot.http.token}",
        "Content-Type": "application/json",
    }

    result = {}

    async with aiohttp.ClientSession() as session:
        # 기존 Application Emojis 확인
        existing = {}
        try:
            async with session.get(
                f"{base_url}/applications/{app_id}/emojis",
                headers=headers,
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for emoji in data.get("items", []):
                        existing[emoji["name"]] = emoji["id"]
        except Exception as e:
            logger.error(f"이모지 목록 조회 실패: {e}")
            return {}

        for emoji_name, icon_url in MUSIC_ICONS.items():
            # 이미 존재하면 스킵
            if emoji_name in existing:
                emoji_id = existing[emoji_name]
                result[emoji_name] = f"<:{emoji_name}:{emoji_id}>"
                continue

            try:
                # 아이콘 다운로드
                async with session.get(icon_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        logger.error(f"[Music Emoji] {emoji_name} 다운로드 실패: HTTP {resp.status}")
                        continue
                    image_data = await resp.read()

                # 128x128로 리사이즈 (Discord 이모지 권장 크기)
                img = Image.open(BytesIO(image_data))
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                img = img.resize((128, 128), Image.Resampling.LANCZOS)

                output = BytesIO()
                img.save(output, "PNG", optimize=True)
                png_data = output.getvalue()

                # Base64 인코딩 후 Discord 업로드
                b64 = base64.b64encode(png_data).decode("utf-8")
                payload = {
                    "name": emoji_name,
                    "image": f"data:image/png;base64,{b64}",
                }

                async with session.post(
                    f"{base_url}/applications/{app_id}/emojis",
                    headers=headers,
                    json=payload,
                ) as resp:
                    if resp.status == 201:
                        emoji_data = await resp.json()
                        emoji_id = emoji_data["id"]
                        result[emoji_name] = f"<:{emoji_name}:{emoji_id}>"
                        logger.info(f"[Music Emoji] {emoji_name} 업로드 완료")
                    else:
                        text = await resp.text()
                        logger.error(f"[Music Emoji] {emoji_name} 업로드 실패: {resp.status} {text}")

                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"[Music Emoji] {emoji_name} 처리 오류: {e}")

    return result
