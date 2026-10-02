"""거노 본인 전용 라우트.

- /api/me/feed       : daily_feeds 컬렉션(run/core/store.py) 최신 N일 조회
- /api/me/whoami     : owner 여부만 빠르게 확인 (프론트 가드용)

owner_id 외 접근 시 403. OWNER_ID 환경변수에서.
"""

from __future__ import annotations

import logging
import os
import sys
from functools import wraps

from flask import Blueprint, jsonify, request, session

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from run.core import store  # noqa: E402

logger = logging.getLogger(__name__)
me_bp = Blueprint('me', __name__)

DAILY_COLLECTION = 'daily_feeds'


def _get_owner_id() -> str | None:
    return os.getenv('OWNER_ID') or None


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


# 거노 결정: 로그인 없이 hidden URL 만 — 노출 시 인지 (security-by-obscurity).
# 메뉴/네비/sitemap/SEO 어디에도 링크 없음. 본인이 직접 입력하는 URL.
@me_bp.route('/feed')
def feed():
    """daily_feeds 최신 N일."""
    days = max(1, min(int(request.args.get('days', 14)), 60))
    try:
        docs = store.client().collection(DAILY_COLLECTION) \
            .order_by('date', direction=store.Query.DESCENDING) \
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
