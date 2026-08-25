"""오류가 난 서버로 건너뛰는 링크 구성.

훅 알림에 서버 이름만 적혀 있으면 어느 서버인지 알아도 거기 갈 방법이 없다.
관리자가 곧장 들어가거나 당사자에게 연락할 수 있도록 링크를 붙인다.

초대는 관리자가 그 서버에 없을 때만 만든다 — 이미 멤버면 채널 점프로 충분하고,
남의 서버에 오류마다 초대가 쌓이는 것은 그 자체로 민폐다.
"""

from __future__ import annotations

import os
import re
from typing import Optional

import discord

_JUMP = "https://discord.com/channels"
_PROFILE = "https://discord.com/users"

# 초대 유효기간 — 진단은 하루면 끝난다. 오래 살려두면 남의 서버에 구멍이 남는다.
_INVITE_MAX_AGE = 86400
_INVITE_MAX_USES = 1

_MD_UNSAFE = re.compile(r"[\[\]()`*_~|\\]")


def _label(text: str, limit: int = 24) -> str:
    """마크다운 링크 라벨로 안전한 문자열. 이름의 괄호가 링크를 깨뜨린다."""
    clean = _MD_UNSAFE.sub("", text or "").strip() or "이름없음"
    return clean[:limit]


def _admin_id() -> Optional[int]:
    raw = os.getenv("OWNER_ID")
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


async def _try_invite(guild: discord.Guild, channel) -> Optional[str]:
    """1회용 초대 링크. 권한이 없으면 None — 흔한 경우라 조용히 넘긴다."""
    me = guild.me
    if me is None:
        return None

    candidates = []
    if isinstance(channel, discord.TextChannel):
        candidates.append(channel)
    if guild.system_channel is not None:
        candidates.append(guild.system_channel)
    candidates.extend(guild.text_channels)

    for target in candidates:
        try:
            if not target.permissions_for(me).create_instant_invite:
                continue
            invite = await target.create_invite(
                max_age=_INVITE_MAX_AGE,
                max_uses=_INVITE_MAX_USES,
                unique=True,
                reason="봇 오류 진단 — 관리자 임시 접근",
            )
            return invite.url
        except Exception:
            continue
    return None


async def build_guild_links(
    guild: Optional[discord.Guild],
    *,
    user: Optional[discord.abc.User] = None,
    channel=None,
    guild_id: Optional[int] = None,
) -> list[str]:
    """오류 알림에 붙일 "[라벨](url)" 링크 목록.

    guild 가 None 이어도 guild_id 가 있으면(user-install 컨텍스트) 점프 링크는 만든다.
    """
    links: list[str] = []

    if user is not None:
        name = getattr(user, "display_name", None) or getattr(user, "name", "")
        links.append(f"[{_label(name)}]({_PROFILE}/{user.id})")

    gid = guild.id if guild is not None else guild_id
    if gid is None:
        return links

    if channel is not None and getattr(channel, "id", None):
        links.append(f"[문제의 채널]({_JUMP}/{gid}/{channel.id})")
    else:
        links.append(f"[서버 열기]({_JUMP}/{gid})")

    if guild is None:
        return links

    if guild.owner_id:
        links.append(f"[서버주]({_PROFILE}/{guild.owner_id})")

    # 관리자가 이미 멤버면 위 점프 링크로 바로 간다 — 초대를 만들 이유가 없다.
    admin = _admin_id()
    if admin is not None and guild.get_member(admin) is not None:
        return links

    invite = await _try_invite(guild, channel)
    if invite:
        links.append(f"[초대 링크]({invite})")

    return links
