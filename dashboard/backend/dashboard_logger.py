"""
대시보드 액션 로거

설정 변경 등 대시보드에서 수행된 액션을 `dashboard_logs` 컬렉션(run/core/store.py)에 기록.
웹패널이 같은 컬렉션을 읽어 표시.
"""
import os
import sys
from datetime import datetime, timezone, timedelta

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from run.core import store  # noqa: E402

KST = timezone(timedelta(hours=9))
DASHBOARD_LOGS_COLLECTION = 'dashboard_logs'


def log_action(action_type, user_id=None, user_name=None, guild_id=None, guild_name=None, details=None):
    """대시보드 액션을 저장소에 기록"""
    try:
        store.client().collection(DASHBOARD_LOGS_COLLECTION).add({
            'action': action_type,
            'user_id': str(user_id) if user_id else 'unknown',
            'user_name': user_name or 'unknown',
            'guild_id': str(guild_id) if guild_id else None,
            'guild_name': guild_name or None,
            'details': details or {},
            'timestamp': datetime.now(KST).isoformat(),
        })
    except Exception as e:
        print(f"[Dashboard Logger] Failed to log action: {e}", flush=True)
