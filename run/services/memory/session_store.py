"""(guild, user) → Managed Agents session_id 영속 매핑.

콜백 패턴: anthropic API 호출은 호출자가 주입한다. 이 모듈은 SQLite만 다룬다.

회전 (rotate) 정책:
    - turn_count >= 50 (자주 대화하는 채널)  → 컨텍스트 비대화 방지
    - 마지막 활동 후 6시간 경과            → 좀비 세션 정리

회전 시:
    1. 기존 session에서 summary 추출 (호출자의 summarize_fn)
    2. 기존 session archive (호출자의 archive_fn)
    3. 새 session 생성 (호출자의 create_fn). summary는 시스템 프롬프트에 inject 권장
"""

import logging
import time
from typing import Awaitable, Callable, Optional

from .db import connect

logger = logging.getLogger(__name__)

DEFAULT_MAX_TURNS = 50
DEFAULT_MAX_IDLE_SECONDS = 6 * 60 * 60


def _scope(guild_id, user_id) -> tuple[str, str]:
    g = str(guild_id) if guild_id else "dm"
    u = str(user_id) if user_id else "anon"
    # BOT_IDENTITY='debi'/'marlene' 솔로봇은 guild 스코프에 prefix 붙여 기존봇 행과 자연 격리.
    # 'unified'(기본)는 prefix 없음 → 기존 데이터/쿼리 무영향.
    from run.core import config
    if config.BOT_IDENTITY and config.BOT_IDENTITY != "unified":
        g = f"{config.BOT_IDENTITY}:{g}"
    return g, u


def get_session(guild_id, user_id) -> Optional[dict]:
    g, u = _scope(guild_id, user_id)
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE guild_id=? AND user_id=?", (g, u)
        ).fetchone()
        return dict(row) if row else None


def save_session(guild_id, user_id, session_id: str, summary: Optional[str] = None) -> None:
    """새 session_id 저장 또는 교체 (turn_count=0으로 리셋)."""
    g, u = _scope(guild_id, user_id)
    now = int(time.time())
    with connect() as conn:
        conn.execute(
            """INSERT INTO sessions (guild_id, user_id, session_id, turn_count, summary, created_at, last_active)
               VALUES (?, ?, ?, 0, ?, ?, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET
                   session_id=excluded.session_id,
                   turn_count=0,
                   summary=excluded.summary,
                   created_at=excluded.created_at,
                   last_active=excluded.last_active""",
            (g, u, session_id, summary, now, now),
        )


def bump_turn(guild_id, user_id) -> None:
    g, u = _scope(guild_id, user_id)
    now = int(time.time())
    with connect() as conn:
        conn.execute(
            "UPDATE sessions SET turn_count=turn_count+1, last_active=? WHERE guild_id=? AND user_id=?",
            (now, g, u),
        )


def should_rotate(
    guild_id,
    user_id,
    max_turns: int = DEFAULT_MAX_TURNS,
    max_idle_seconds: Optional[int] = DEFAULT_MAX_IDLE_SECONDS,
) -> bool:
    sess = get_session(guild_id, user_id)
    if sess is None:
        return False
    if sess["turn_count"] >= max_turns:
        return True
    if max_idle_seconds and (time.time() - sess["last_active"]) > max_idle_seconds:
        return True
    return False


def delete_session(guild_id, user_id) -> None:
    g, u = _scope(guild_id, user_id)
    with connect() as conn:
        conn.execute("DELETE FROM sessions WHERE guild_id=? AND user_id=?", (g, u))


async def get_or_rotate_session(
    guild_id,
    user_id,
    create_fn: Callable[[], Awaitable[str]],
    archive_fn: Callable[[str], Awaitable[None]],
    summarize_fn: Callable[[str], Awaitable[str]],
    max_turns: int = DEFAULT_MAX_TURNS,
    max_idle_seconds: Optional[int] = DEFAULT_MAX_IDLE_SECONDS,
) -> tuple[str, Optional[str]]:
    """세션 ID 가져오기 + 필요 시 회전. 호출자는 (session_id, summary_to_inject) 받는다.

    summary_to_inject 의미:
        None → 기존 세션 재사용 (Anthropic이 컨텍스트 자동 유지) 또는 새 세션 첫 시작
        str  → 회전 직후. 호출자는 다음 user.message 앞에 summary 텍스트를 prefix 권장

    summary inject는 호출자 책임. session_store는 SQLite 매핑만 담당.
    """
    sess = get_session(guild_id, user_id)

    if sess is None:
        new_id = await create_fn()
        save_session(guild_id, user_id, new_id, summary=None)
        return new_id, None

    if should_rotate(guild_id, user_id, max_turns, max_idle_seconds):
        old_id = sess["session_id"]
        try:
            summary = await summarize_fn(old_id)
        except Exception as e:
            logger.warning("session 요약 실패 — 이전 요약 유지: %s", e)
            summary = sess.get("summary")
        try:
            await archive_fn(old_id)
        except Exception as e:
            logger.warning("session archive 실패 (무시): %s", e)
        new_id = await create_fn()
        save_session(guild_id, user_id, new_id, summary=summary)
        logger.info(
            "session 회전: guild=%s user=%s old=%s new=%s turns=%d",
            guild_id, user_id, old_id, new_id, sess["turn_count"],
        )
        return new_id, summary

    return sess["session_id"], None
