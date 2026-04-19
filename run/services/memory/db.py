"""SQLite 메모리 저장소 — corrections + sessions.

WAL 모드로 동시성 안전. discord.py 비동기 환경에서 호출마다 새 connection.
모듈 첫 사용 시 자동 초기화 (lazy + thread-safe).

테이블:
    corrections: 사용자가 봇한테 알려준 사실 (guild_id 단위, 캐릭터 페르소나 강화)
    sessions:    (guild_id, user_id) → Managed Agents session_id 영속 매핑

데이터 위치:
    BOT_DATA_DIR 환경변수 (기본값: ./data)
    VM에서는 /data 볼륨 마운트와 매칭
"""

import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

DB_DIR = Path(os.getenv("BOT_DATA_DIR", "./data"))
DB_PATH = DB_DIR / "memory.db"

_init_lock = threading.Lock()
_initialized = False

SCHEMA = """
CREATE TABLE IF NOT EXISTS corrections (
    guild_id   TEXT NOT NULL,
    text       TEXT NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    PRIMARY KEY (guild_id, text)
);

CREATE INDEX IF NOT EXISTS idx_corrections_guild
    ON corrections(guild_id, created_at DESC);

CREATE TABLE IF NOT EXISTS sessions (
    guild_id    TEXT NOT NULL,
    user_id     TEXT NOT NULL,
    session_id  TEXT NOT NULL,
    turn_count  INTEGER NOT NULL DEFAULT 0,
    summary     TEXT,
    created_at  INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    last_active INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    PRIMARY KEY (guild_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_last_active
    ON sessions(last_active);
"""


def _ensure_initialized() -> None:
    global _initialized
    if _initialized:
        return
    with _init_lock:
        if _initialized:
            return
        DB_DIR.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.executescript(SCHEMA)
        print(f"[MEMORY] SQLite 초기화 완료: {DB_PATH}", flush=True)
        _initialized = True


@contextmanager
def connect():
    """SQLite connection 컨텍스트 매니저.

    - row_factory=Row로 dict 형태 접근 가능 (row['guild_id'])
    - 정상 종료 시 자동 commit, 예외 발생 시 자동 rollback
    """
    _ensure_initialized()
    conn = sqlite3.connect(DB_PATH, isolation_level="DEFERRED")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
