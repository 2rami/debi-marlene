"""거노 본인 전용 라우트.

- /api/me/feed       : daily_feeds Firestore 컬렉션 최신 N일 조회
- /api/me/whoami     : owner 여부만 빠르게 확인 (프론트 가드용)

owner_id 외 접근 시 403. OWNER_ID 환경변수 또는 Secret Manager 에서.
"""

from __future__ import annotations

import logging
import os
import subprocess
from functools import wraps

from flask import Blueprint, jsonify, request, session

logger = logging.getLogger(__name__)
me_bp = Blueprint('me', __name__)

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')
DAILY_COLLECTION = 'daily_feeds'

_owner_id_cache: str | None = None
_firestore_client = None


def _get_owner_id() -> str | None:
    global _owner_id_cache
    if _owner_id_cache is not None:
        return _owner_id_cache
    val = os.getenv('OWNER_ID')
    if not val:
        try:
            val = subprocess.run(
                ['gcloud', 'secrets', 'versions', 'access', 'latest',
                 '--secret=owner-id', f'--project={GCP_PROJECT_ID}'],
                capture_output=True, text=True, check=True, timeout=5,
            ).stdout.strip()
        except Exception as e:
            logger.error(f'owner-id Secret Manager fetch 실패: {e}')
            val = None
    _owner_id_cache = val
    return val


def _get_firestore():
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client
    try:
        from google.cloud import firestore
        _firestore_client = firestore.Client(project=GCP_PROJECT_ID)
    except Exception as e:
        logger.error(f'Firestore 클라이언트 실패: {e}')
        _firestore_client = False
    return _firestore_client if _firestore_client is not False else None


def owner_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = session.get('user')
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        owner_id = _get_owner_id()
        if not owner_id or str(user.get('id')) != str(owner_id):
            return jsonify({'error': 'Forbidden'}), 403
        return f(*args, **kwargs)
    return wrapper


@me_bp.route('/whoami')
def whoami():
    """owner 여부만 빠르게 — 프론트가 라우트 가드용으로 호출."""
    user = session.get('user')
    if not user:
        return jsonify({'is_owner': False, 'authenticated': False})
    owner_id = _get_owner_id()
    is_owner = owner_id is not None and str(user.get('id')) == str(owner_id)
    return jsonify({'is_owner': is_owner, 'authenticated': True})


@me_bp.route('/feed')
@owner_required
def feed():
    """daily_feeds 최신 N일."""
    days = max(1, min(int(request.args.get('days', 14)), 60))
    db = _get_firestore()
    if db is None:
        return jsonify({'error': 'Firestore unavailable'}), 503

    try:
        from google.cloud import firestore as fs
        docs = db.collection(DAILY_COLLECTION) \
            .order_by('date', direction=fs.Query.DESCENDING) \
            .limit(days) \
            .stream()
        feeds = []
        for d in docs:
            data = d.to_dict()
            feeds.append({
                'date': data.get('date'),
                'sent_at': data.get('sent_at').isoformat() if data.get('sent_at') else None,
                'selected_count': data.get('selected_count', 0),
                'raw_count': data.get('raw_count', 0),
                'new_count': data.get('new_count', 0),
                'items': data.get('items', []),
            })
        return jsonify({'feeds': feeds})
    except Exception as e:
        logger.exception('feed query 실패')
        return jsonify({'error': str(e)}), 500
