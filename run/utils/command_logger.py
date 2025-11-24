"""
명령어 사용 로깅 유틸리티

Discord 봇의 모든 명령어 사용 내역을 GCS에 기록합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any


async def log_command_usage(
    command_name: str,
    user_id: int,
    user_name: str,
    guild_id: Optional[int] = None,
    guild_name: Optional[str] = None,
    args: Optional[Dict[str, Any]] = None
):
    """
    명령어 사용을 GCS에 로깅합니다.

    Args:
        command_name: 명령어 이름 (예: "전적", "통계", "설정")
        user_id: 사용자 Discord ID
        user_name: 사용자 이름
        guild_id: 서버 ID (DM일 경우 None)
        guild_name: 서버 이름 (DM일 경우 None)
        args: 명령어 인자 (dict 형식)
    """
    try:
        from run.core import config

        log_entry = {
            "command_name": command_name,
            "user_id": str(user_id),
            "user_name": user_name,
            "guild_id": str(guild_id) if guild_id else None,
            "guild_name": guild_name,
            "timestamp": datetime.now().isoformat(),
            "args": args or {}
        }

        config.save_command_log(log_entry)

    except Exception as e:
        # 로깅 실패해도 명령어 실행에는 영향 없도록
        print(f"[경고] 명령어 로깅 실패 ({command_name}): {e}", flush=True)
