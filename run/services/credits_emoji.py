"""크레딧 application emoji 등록/조회.

discord.py 2.4+ `bot.create_application_emoji()` 사용.

이미지 소스: `assets/credit/credit.png` (이터널리턴 정식 크레딧 이미지, 256×142 RGBA).
이전 PIL 자동 생성 디스크는 'credit' 이름으로 등록되어 캐시됐을 수 있어 새 이름
'credit_v2' 로 등록 — 기존 'credit' 은 남겨둬도 충돌 없음.

캐싱: 모듈 레벨 변수. 첫 호출 시 fetch → 없으면 create. 이후 in-memory 만 참조.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import discord

logger = logging.getLogger(__name__)

# v3 — 거노 제공 84x84 PNG (라임 외곽 + 다크그린 안 + 라임 C). 이전 PNG 캐시 invalidate
EMOJI_NAME = "credit_v3"

# debi-marlene/run/services/credits_emoji.py → debi-marlene/assets/credit/credit.png
ASSET_PATH = Path(__file__).resolve().parents[2] / "assets" / "credit" / "credit.png"
ASSET_FILENAME = "credit.png"  # discord.File 첨부 시 동일 파일명 + view 의 attachment:// URI 와 일치
_ASSET_PATH = ASSET_PATH  # 하위 호환

_emoji_cache: discord.Emoji | None | bool = None  # None=untouched, False=실패, Emoji=ok


def _load_png() -> bytes:
    """정식 자산 PNG 읽기. 누락 시 PIL 폴백."""
    if _ASSET_PATH.is_file():
        return _ASSET_PATH.read_bytes()
    logger.warning("credit PNG asset 누락 (%s) — PIL 폴백 디스크 사용", _ASSET_PATH)
    return _fallback_png(96)


def _fallback_png(size: int = 96) -> bytes:
    """asset 누락 시 안전망 — 자동 생성 디스크. 정상 운영에선 호출되지 않음."""
    import io
    import math
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    pad = 1
    d.ellipse(
        (pad, pad, size - pad - 1, size - pad - 1),
        fill="#326D1B",
        outline="#E5FC8A",
        width=max(2, size // 32),
    )
    cx, cy = size / 2, size / 2
    r = size * 0.30
    pts = [
        (cx + r * math.cos(math.radians(-90 + 60 * i)),
         cy + r * math.sin(math.radians(-90 + 60 * i)))
        for i in range(6)
    ]
    stroke = max(2, size // 24)
    d.polygon(pts, outline="#E5FC8A", width=stroke)
    d.line([(cx, cy - r), (cx, cy)], fill="#E5FC8A", width=stroke)
    d.line([(cx, cy), pts[1]], fill="#E5FC8A", width=stroke)
    d.line([(cx, cy), pts[5]], fill="#E5FC8A", width=stroke)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


async def get_credit_emoji(bot: discord.Client) -> Optional[discord.Emoji]:
    """등록된 application emoji 반환. 없으면 등록 시도. 실패는 None.

    호출처는 None 일 때 fallback (텍스트 마크 [C] 등) 처리.
    """
    global _emoji_cache
    if _emoji_cache is not None:
        return _emoji_cache if _emoji_cache is not False else None

    try:
        try:
            existing = await bot.fetch_application_emojis()
        except AttributeError:
            existing = []
        for e in existing:
            if e.name == EMOJI_NAME:
                _emoji_cache = e
                return e

        png = _load_png()
        new = await bot.create_application_emoji(name=EMOJI_NAME, image=png)
        logger.info(
            "credit application emoji 등록 완료 (id=%s, %d bytes)", new.id, len(png),
        )
        _emoji_cache = new
        return new
    except Exception as e:
        logger.warning("credit application emoji 등록/조회 실패: %s", e)
        _emoji_cache = False
        return None


def format_emoji(emoji: Optional[discord.Emoji]) -> str:
    """메시지 본문용 문자열. 실패 시 텍스트 폴백."""
    if emoji is None:
        return "[C]"
    return str(emoji)
