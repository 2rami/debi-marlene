"""
대시보드 액션 로거

설정 변경 등 대시보드에서 수행된 액션을 Firestore `dashboard_logs` 컬렉션에 기록.
웹패널이 같은 컬렉션을 읽어 표시.
"""
import os
from datetime import datetime, timezone, timedelta

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')
KST = timezone(timedelta(hours=9))
DASHBOARD_LOGS_COLLECTION = 'dashboard_logs'

_firestore_client = None


def _get_firestore_client():
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client if _firestore_client is not False else None
    try:
        from google.cloud import firestore
        _firestore_client = firestore.Client(project=GCP_PROJECT_ID)
    except Exception as e:
        print(f"[Dashboard Logger] Firestore 클라이언트 생성 실패: {e}", flush=True)
        _firestore_client = False
    return _firestore_client if _firestore_client is not False else None


def log_action(action_type, user_id=None, user_name=None, guild_id=None, guild_name=None, details=None):
    """대시보드 액션을 Firestore 에 기록"""
    fs = _get_firestore_client()
    if not fs:
        return
    try:
        fs.collection(DASHBOARD_LOGS_COLLECTION).add({
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
