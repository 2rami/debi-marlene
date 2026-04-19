"""봇 영속 메모리 저장소.

- `db.py`: SQLite 헬퍼 (WAL 모드, 컨텍스트 매니저)
- `session_store.py`: (guild, user) → Managed Agents session_id 매핑
- corrections: 사용자가 봇한테 알려준 사실 (구 `chat_memory.py` 대체)
"""
