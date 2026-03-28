"""
대시보드 액션 로거

설정 변경 등 대시보드에서 수행된 액션을 GCS에 기록
웹패널에서 dashboard_logs.json을 읽어 표시
"""
import json
from datetime import datetime, timezone, timedelta

import os
GCS_BUCKET = os.getenv('GCS_BUCKET_NAME', 'debi-marlene-settings')
GCS_DASHBOARD_LOGS_KEY = 'dashboard_logs.json'
KST = timezone(timedelta(hours=9))
MAX_LOGS = 500


def log_action(action_type, user_id=None, user_name=None, guild_id=None, guild_name=None, details=None):
    """대시보드 액션을 GCS에 기록"""
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_DASHBOARD_LOGS_KEY)

        # 기존 로그 로드
        logs = []
        if blob.exists():
            content = blob.download_as_text()
            logs = json.loads(content)

        # 새 로그 추가
        logs.insert(0, {
            'action': action_type,
            'user_id': str(user_id) if user_id else 'unknown',
            'user_name': user_name or 'unknown',
            'guild_id': str(guild_id) if guild_id else None,
            'guild_name': guild_name or None,
            'details': details or {},
            'timestamp': datetime.now(KST).isoformat(),
        })

        # 최대 개수 유지
        logs = logs[:MAX_LOGS]

        blob.upload_from_string(
            json.dumps(logs, ensure_ascii=False, indent=2),
            content_type='application/json'
        )
    except Exception as e:
        print(f"[Dashboard Logger] Failed to log action: {e}", flush=True)
