"""대화 메모리 — corrections (사용자가 봇한테 알려준 사실).

guild 단위로 분리 저장. SQLite WAL 모드로 동시성 안전 (race condition 자동 해결).
2026-04-20: GCS chat_memory/{guild}.json → SQLite로 이전.

기존 호출처 영향 없도록 함수 시그니처 유지:
    detect_correction(message)             — 패턴 감지 (regex)
    add_correction(text, guild_id=None)    — 추가 (중복 자동 무시, MAX 50)
    get_corrections_prompt(guild_id=None)  — 시스템 프롬프트 추가 텍스트
    clear_corrections(guild_id=None)       — 전체 초기화
"""

import logging
import re
from typing import Optional, Union

from run.services.memory.db import connect

logger = logging.getLogger(__name__)

MAX_CORRECTIONS = 50

CORRECTION_PATTERNS = [
    re.compile(r".+(?:는|은)\s*(?:남자|여자|남캐|여캐)(?:야|임|이야|인데|거든|잖아)"),
    re.compile(r"^(?:아니야|아닌데|틀렸어|아니거든)[,.]?\s*.+"),
    re.compile(r".+(?:가|이)\s*아니라\s*.+(?:야|임|이야)"),
    re.compile(r".+(?:안|못)\s*(?:써|씀|쓰거든|쓰는데|쓴다고|함|해|하거든)"),
    re.compile(r".+(?:쓰는|하는|쓰거든|하거든)\s*(?:거야|거임|건데)"),
    re.compile(r".+(?:기억해|알아둬|외워|잊지마|기억하고)"),
]


def _scope(guild_id: Optional[Union[int, str]]) -> str:
    if guild_id is None or guild_id == "":
        return "dm"
    return str(guild_id)


def detect_correction(message: str) -> bool:
    for pattern in CORRECTION_PATTERNS:
        if pattern.search(message):
            return True
    return False


def add_correction(text: str, guild_id: Optional[Union[int, str]] = None) -> None:
    scope = _scope(guild_id)
    with connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO corrections(guild_id, text) VALUES (?, ?)",
            (scope, text),
        )
        count = conn.execute(
            "SELECT COUNT(*) FROM corrections WHERE guild_id=?", (scope,)
        ).fetchone()[0]
        excess = count - MAX_CORRECTIONS
        if excess > 0:
            conn.execute(
                """DELETE FROM corrections WHERE guild_id=? AND text IN (
                    SELECT text FROM corrections WHERE guild_id=?
                    ORDER BY created_at ASC LIMIT ?
                )""",
                (scope, scope, excess),
            )
        print(
            f"[메모리] 저장 완료 [scope={scope}] (총 {min(count, MAX_CORRECTIONS)}개)",
            flush=True,
        )


def get_corrections_prompt(guild_id: Optional[Union[int, str]] = None) -> str:
    scope = _scope(guild_id)
    with connect() as conn:
        rows = conn.execute(
            "SELECT text FROM corrections WHERE guild_id=? ORDER BY created_at ASC",
            (scope,),
        ).fetchall()
    if not rows:
        return ""
    items = "\n".join(f"- {r['text']}" for r in rows)
    return f"\n\n[사용자가 알려준 정보 - 반드시 지켜]\n{items}"


def clear_corrections(guild_id: Optional[Union[int, str]] = None) -> None:
    scope = _scope(guild_id)
    with connect() as conn:
        conn.execute("DELETE FROM corrections WHERE guild_id=?", (scope,))
