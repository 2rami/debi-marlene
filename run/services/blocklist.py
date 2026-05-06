"""기능 차단 (블랙리스트) 서비스.

데이터 모델 — Firestore `guilds/{guild_id}` 문서에 `blocked_users` 맵:

    blocked_users = {
        "<user_id_str>": {
            "features": ["chat", "solo_chat", "tts"],
            "blocked_at": "2026-05-06T...",
            "blocked_by": "<admin_user_id_str>",
        },
        ...
    }

기능 키:
- "chat"       : /대화 슬래시 + ChatCog on_message (호명 응답)
- "solo_chat"  : ChimeInCog 자율 끼어들기 (솔로봇)
- "tts"        : voice.handle_tts_message
- "credits"    : 크레딧/도박 (잔고 봉인 — 향후 확장)

가드: 모든 함수는 Firestore blocking — caller 가 to_thread 로 감쌈.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Iterable

from run.core import config as bot_config

logger = logging.getLogger(__name__)


VALID_FEATURES = ("chat", "solo_chat", "tts", "credits")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_features(features: Iterable[str]) -> list[str]:
    out = []
    for f in features:
        s = str(f).strip()
        if s in VALID_FEATURES and s not in out:
            out.append(s)
    return out


def is_blocked(guild_id, user_id, feature: str) -> bool:
    """단일 (guild, user, feature) 차단 여부."""
    if guild_id is None or user_id is None:
        return False
    fs = bot_config.get_firestore_client()
    if fs is None:
        return False
    try:
        doc = fs.collection("guilds").document(str(guild_id)).get()
        if not doc.exists:
            return False
        blocked = (doc.to_dict() or {}).get("blocked_users", {}) or {}
        entry = blocked.get(str(user_id))
        if not entry:
            return False
        return feature in (entry.get("features", []) or [])
    except Exception as e:
        logger.warning("blocklist 조회 실패 (guild=%s user=%s): %s", guild_id, user_id, e)
        return False


def list_blocked(guild_id) -> dict:
    """guild 의 전체 blocked_users 맵 반환. 없으면 {}."""
    if guild_id is None:
        return {}
    fs = bot_config.get_firestore_client()
    if fs is None:
        return {}
    try:
        doc = fs.collection("guilds").document(str(guild_id)).get()
        if not doc.exists:
            return {}
        return (doc.to_dict() or {}).get("blocked_users", {}) or {}
    except Exception as e:
        logger.warning("blocklist 목록 조회 실패 (guild=%s): %s", guild_id, e)
        return {}


def set_blocked(guild_id, user_id, features: Iterable[str], blocked_by) -> dict:
    """user_id 의 차단 기능 목록을 features 로 설정 (overwrite). 빈 리스트면 삭제와 동치.

    Returns: 갱신된 entry dict (삭제된 경우 {})
    """
    if guild_id is None or user_id is None:
        return {}
    fs = bot_config.get_firestore_client()
    if fs is None:
        return {}

    norm = _normalize_features(features)
    if not norm:
        return unblock(guild_id, user_id)

    try:
        guild_ref = fs.collection("guilds").document(str(guild_id))
        snap = guild_ref.get()
        existing = (snap.to_dict() or {}) if snap.exists else {}
        blocked_map = dict(existing.get("blocked_users", {}) or {})
        entry = {
            "features": norm,
            "blocked_at": _now_iso(),
            "blocked_by": str(blocked_by) if blocked_by is not None else None,
        }
        blocked_map[str(user_id)] = entry
        guild_ref.set({"blocked_users": blocked_map}, merge=True)
        return entry
    except Exception as e:
        logger.warning("blocklist 저장 실패: %s", e)
        return {}


def unblock(guild_id, user_id) -> dict:
    """user_id entry 제거. 없는 경우 {}."""
    if guild_id is None or user_id is None:
        return {}
    fs = bot_config.get_firestore_client()
    if fs is None:
        return {}
    try:
        guild_ref = fs.collection("guilds").document(str(guild_id))
        snap = guild_ref.get()
        if not snap.exists:
            return {}
        existing = snap.to_dict() or {}
        blocked_map = dict(existing.get("blocked_users", {}) or {})
        if str(user_id) not in blocked_map:
            return {}
        blocked_map.pop(str(user_id), None)
        guild_ref.set({"blocked_users": blocked_map}, merge=True)
        return {}
    except Exception as e:
        logger.warning("blocklist 해제 실패: %s", e)
        return {}
