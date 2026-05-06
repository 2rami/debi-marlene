"""기능 차단 (블랙리스트) 라우트.

엔드포인트 (모두 admin_required):
- GET    /api/servers/<guild_id>/blocked-users
- POST   /api/servers/<guild_id>/blocked-users        body: { user_id, features: [str] }
- DELETE /api/servers/<guild_id>/blocked-users/<user_id>

services/blocklist.py 가 Firestore 트랜잭션 처리.
"""

from __future__ import annotations

import logging
import os
import sys
from functools import wraps

from flask import Blueprint, jsonify, request, session

# run.* 임포트 sys.path 보정
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from run.services import blocklist as blocklist_service  # noqa: E402

logger = logging.getLogger(__name__)
blocked_bp = Blueprint('blocked_users', __name__)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """guild_id URL 파라미터 + session.user.admin_servers 비교."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = session.get('user')
        guild_id = kwargs.get('guild_id')
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        if guild_id and str(guild_id) not in (user.get('admin_servers') or []):
            return jsonify({'error': 'Forbidden'}), 403
        return f(*args, **kwargs)
    return wrapper


@blocked_bp.route('/servers/<guild_id>/blocked-users', methods=['GET'])
@login_required
@admin_required
def list_blocked(guild_id):
    blocked = blocklist_service.list_blocked(guild_id)
    # dict → list 형태로 프론트 다루기 쉽게
    items = [
        {
            'user_id': uid,
            'features': entry.get('features', []),
            'blocked_at': entry.get('blocked_at'),
            'blocked_by': entry.get('blocked_by'),
        }
        for uid, entry in blocked.items()
    ]
    items.sort(key=lambda x: x.get('blocked_at') or '', reverse=True)
    return jsonify({'guild_id': str(guild_id), 'items': items})


@blocked_bp.route('/servers/<guild_id>/blocked-users', methods=['POST'])
@login_required
@admin_required
def upsert_blocked(guild_id):
    user = session['user']
    body = request.get_json(silent=True) or {}
    user_id = body.get('user_id')
    features = body.get('features') or []

    if not user_id or not isinstance(user_id, str):
        return jsonify({'ok': False, 'error': 'user_id required'}), 400
    if not isinstance(features, list):
        return jsonify({'ok': False, 'error': 'features must be array'}), 400

    entry = blocklist_service.set_blocked(
        guild_id, user_id, features, blocked_by=user['id'],
    )
    return jsonify({
        'ok': True,
        'guild_id': str(guild_id),
        'user_id': str(user_id),
        'entry': entry,
    })


@blocked_bp.route('/servers/<guild_id>/blocked-users/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_blocked(guild_id, user_id):
    blocklist_service.unblock(guild_id, user_id)
    return jsonify({'ok': True, 'guild_id': str(guild_id), 'user_id': str(user_id)})
