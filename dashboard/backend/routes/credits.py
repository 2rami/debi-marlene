"""크레딧 라우트 (이터널리턴 게임 재화 모티프).

엔드포인트:
- GET  /api/credits/me        — 내 잔고 + 출석 상태 + 최근 ledger
- POST /api/credits/check-in  — 일일 출석 (+10, streak 보너스)
- POST /api/credits/donate    — 개인 → 서버 공동 지갑 이체
- GET  /api/credits/guilds    — 내가 속한 서버들의 공동 지갑 잔고

services 계층(run/services/credits.py)에서 Firestore 트랜잭션 처리.
"""

from __future__ import annotations

import logging
import os
import sys
from functools import wraps

from flask import Blueprint, jsonify, request, session

# run.services.credits 임포트를 위해 프로젝트 루트 sys.path 보장.
# dashboard/backend → 프로젝트 루트 = 두 단계 위.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from run.services import credits as credits_service  # noqa: E402

logger = logging.getLogger(__name__)
credits_bp = Blueprint('credits', __name__)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper


@credits_bp.route('/me', methods=['GET'])
@login_required
def my_credits():
    user = session['user']
    user_id = str(user['id'])
    bal = credits_service.get_balance(user_id)
    ledger = credits_service.get_recent_ledger(user_id, limit=20)
    return jsonify({
        'balance': bal['personal'],
        'streak_days': bal['streak_days'],
        'last_check_in': bal['last_check_in'],
        'checked_in_today': bal['checked_in_today'],
        'daily_bet': bal['daily_bet'],
        'daily_bet_cap': credits_service.GACHA_DAILY_BET_CAP,
        'recent_ledger': ledger,
    })


@credits_bp.route('/check-in', methods=['POST'])
@login_required
def check_in():
    user = session['user']
    result = credits_service.check_attendance(str(user['id']))
    if not result.get('ok'):
        return jsonify(result), 503
    status = 200
    return jsonify(result), status


@credits_bp.route('/donate', methods=['POST'])
@login_required
def donate():
    user = session['user']
    body = request.get_json(silent=True) or {}
    guild_id = body.get('guild_id')
    amount = body.get('amount')

    if not guild_id:
        return jsonify({'ok': False, 'error': 'guild_id required'}), 400
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'amount must be integer'}), 400
    if amount <= 0:
        return jsonify({'ok': False, 'error': 'amount must be positive'}), 400

    # 사용자가 멤버인 길드인지 확인 — admin_servers 가 있으면 그것, 아니면 user.guilds 키로 fallback.
    user_guilds = set(str(g) for g in (user.get('admin_servers') or []))
    user_guilds |= set(str(g) for g in (user.get('guilds') or []))
    # admin_servers/guilds 정보가 없을 수도 — 없으면 길드 멤버 확인 스킵 (서버에서 막진 않음, race-friendly)
    if user_guilds and str(guild_id) not in user_guilds:
        return jsonify({'ok': False, 'error': 'not_member_of_guild'}), 403

    result = credits_service.donate(str(user['id']), str(guild_id), amount)
    if not result.get('ok'):
        # insufficient 는 200 + ok:false 로 — 프론트가 깔끔하게 처리.
        if result.get('reason') == 'insufficient':
            return jsonify(result), 200
        return jsonify(result), 400
    return jsonify(result), 200


@credits_bp.route('/gacha', methods=['POST'])
@login_required
def gacha():
    """베팅. body: { bet: int }. 일일 한도/잔고 부족 시 ok:false."""
    user = session['user']
    body = request.get_json(silent=True) or {}
    try:
        bet = int(body.get('bet'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'bet must be integer'}), 400
    if bet <= 0:
        return jsonify({'ok': False, 'error': 'bet must be positive'}), 400

    result = credits_service.gacha(str(user['id']), bet)
    # daily_cap / insufficient 도 200 + ok:false 로 클라가 깔끔히 처리
    return jsonify(result), 200


@credits_bp.route('/guild/<guild_id>', methods=['GET'])
@login_required
def guild_balance(guild_id):
    """단일 길드 공동 지갑 잔고 — 서버 헤더 뱃지용. 멤버십 체크 X (잔고 표시는 공개)."""
    return jsonify({
        'guild_id': str(guild_id),
        'balance': credits_service.get_guild_balance(str(guild_id)),
    })


@credits_bp.route('/guilds', methods=['GET'])
@login_required
def my_guild_balances():
    """내가 속한 서버들의 공동 지갑."""
    user = session['user']
    guild_ids: set[str] = set()
    for gid in (user.get('admin_servers') or []):
        guild_ids.add(str(gid))
    for gid in (user.get('guilds') or []):
        guild_ids.add(str(gid))

    balances = []
    for gid in guild_ids:
        balances.append({
            'guild_id': gid,
            'balance': credits_service.get_guild_balance(gid),
        })
    # 큰 잔고 순
    balances.sort(key=lambda x: x['balance'], reverse=True)
    return jsonify({'guilds': balances})
