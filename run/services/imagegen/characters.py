"""캐릭터 목록과 참조 이미지 — 원본은 dak.gg 이다.

이미지를 미리 받아 두지 않는다. 주소에 게임 버전이 박혀 있어(`.../12.2.0/...`)
패치가 나면 통째로 낡기 때문이다. 쓸 때 받아서 캐시하면 안 낡는다.
"""

from __future__ import annotations

import io
import os
import time
import hashlib
import asyncio
from typing import Optional

import aiohttp

from run.core.config import DAKGG_API_BASE

# 참조는 실루엣과 마감을 전달하는 역할이라 작아도 된다. 크게 보내면 게이트웨이가
# 413 으로 거절한다(실측: 1024px PNG 1.2MB 는 즉시 413, 512px JPEG 38KB 는 통과).
REF_MAX_PX = 512
REF_JPEG_QUALITY = 88

_LIST_TTL = 6 * 3600  # 캐릭터가 추가되는 건 패치 때뿐이라 자주 볼 필요가 없다
_list_cache: dict = {'at': 0.0, 'data': []}
_list_lock = asyncio.Lock()


def _cache_dir() -> str:
    base = os.getenv('BOT_DATA_DIR', './data')
    d = os.path.join(base, 'imgcache')
    os.makedirs(d, exist_ok=True)
    return d


async def _fetch_json(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=aiohttp.ClientTimeout(total=20)) as r:
        r.raise_for_status()
        return await r.json()


async def get_character_list() -> list[dict]:
    """[{id, name, skins:[{id, name, image_url}]}] — 캐시된다."""
    now = time.time()
    if _list_cache['data'] and now - _list_cache['at'] < _LIST_TTL:
        return _list_cache['data']

    async with _list_lock:
        # 락을 기다리는 동안 다른 코루틴이 채웠을 수 있다
        if _list_cache['data'] and time.time() - _list_cache['at'] < _LIST_TTL:
            return _list_cache['data']

        async with aiohttp.ClientSession() as session:
            data = await _fetch_json(session, f'{DAKGG_API_BASE}/data/characters?hl=ko')

        out = []
        for c in data.get('characters', []):
            skins = []
            for s in (c.get('skins') or []):
                url = s.get('imageUrl') or ''
                if not url:
                    continue
                if url.startswith('//'):
                    url = 'https:' + url
                skins.append({'id': s.get('id'), 'name': s.get('name') or '기본', 'image_url': url})
            if skins:
                out.append({'id': c.get('id'), 'name': c.get('name') or '', 'skins': skins})

        _list_cache['data'] = out
        _list_cache['at'] = time.time()
        return out


async def search_characters(query: str, limit: int = 25) -> list[dict]:
    """자동완성용. 앞글자 일치를 먼저 보여준다 — 목록이 90명이라 순서가 곧 사용성이다."""
    chars = await get_character_list()
    q = (query or '').strip().lower()
    if not q:
        return chars[:limit]
    starts = [c for c in chars if c['name'].lower().startswith(q)]
    contains = [c for c in chars if q in c['name'].lower() and c not in starts]
    return (starts + contains)[:limit]


async def find_character(name: str) -> Optional[dict]:
    for c in await get_character_list():
        if c['name'] == name:
            return c
    hits = await search_characters(name, limit=1)
    return hits[0] if hits else None


def _shrink(raw: bytes) -> bytes:
    """참조용으로 줄인다. 그라데이션이 든 그림은 PNG 가 안 줄어드니 JPEG 로 고정."""
    from PIL import Image

    im = Image.open(io.BytesIO(raw))
    if im.mode in ('RGBA', 'LA', 'P'):
        # 투명 배경을 흰색으로 깔아야 JPEG 로 갈 때 검게 뭉치지 않는다
        bg = Image.new('RGB', im.size, (255, 255, 255))
        im = im.convert('RGBA')
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert('RGB')
    im.thumbnail((REF_MAX_PX, REF_MAX_PX))
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=REF_JPEG_QUALITY)
    return buf.getvalue()


async def get_reference_image(image_url: str) -> bytes:
    """스킨 아트를 참조용 JPEG 로. 한 번 받으면 디스크에 남겨 재사용한다."""
    key = hashlib.sha256(image_url.encode()).hexdigest()[:20]
    path = os.path.join(_cache_dir(), f'{key}.jpg')
    if os.path.isfile(path):
        try:
            with open(path, 'rb') as f:
                return f.read()
        except OSError:
            pass

    async with aiohttp.ClientSession() as session:
        async with session.get(image_url, headers={'User-Agent': 'Mozilla/5.0'},
                               timeout=aiohttp.ClientTimeout(total=30)) as r:
            r.raise_for_status()
            raw = await r.read()

    small = await asyncio.get_running_loop().run_in_executor(None, _shrink, raw)
    try:
        with open(path, 'wb') as f:
            f.write(small)
    except OSError:
        pass  # 캐시 실패는 치명적이지 않다
    return small
