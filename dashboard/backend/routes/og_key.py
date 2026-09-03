"""OpenGateway API 키 등록 라우트 — 사용자가 자기 키를 봇에 맡긴다.

`/그림` 의 요금은 봇 운영자가 아니라 **키 주인**에게 청구된다. 그래서 사용자마다
자기 키를 등록해야 하고, 이 화면이 그 창구다.

엔드포인트:
- GET    /api/og-key  — 연결 상태 (키 자체는 절대 안 돌려준다. 끝 4자만)
- POST   /api/og-key  — {key} 등록. 저장 전에 게이트웨이에 물어 살아있는 키인지 확인
- DELETE /api/og-key  — 등록 해제

저장·암호화는 run/services/og_keys.py 가 한다. 여기서는 인증과 검증만.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from functools import wraps

from flask import Blueprint, jsonify, request, session

# run.services 임포트를 위해 프로젝트 루트 sys.path 보장.
# dashboard/backend/routes → 프로젝트 루트 = 세 단계 위.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from run.services import og_keys  # noqa: E402
from run.services.imagegen.gateway import verify_key  # noqa: E402

logger = logging.getLogger(__name__)
og_key_bp = Blueprint('og_key', __name__)

# 게이트웨이가 발급하는 키 접두사. 오타나 엉뚱한 값(예: 대시보드 URL)을 붙여넣었을 때
# 20초짜리 네트워크 확인을 돌리기 전에 즉시 돌려보낸다.
#
# 지금 발급되는 것은 `apik_` 이고 `sk-` 는 옛 형식이다. 옛 키가 아직 살아 있으므로 둘 다 받는다
# (2026-09-03 제보: apik_ 키를 정상 발급받은 사용자가 이 검사에 막혀 등록 자체를 못 했다).
KEY_PREFIXES = ('apik_', 'sk-')
KEY_MIN_LEN = 20


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper


def _user_id() -> str:
    return str(session['user']['id'])


def _iso(v):
    return v.isoformat() if hasattr(v, 'isoformat') else v


def _status_payload(user_id: str) -> dict:
    s = og_keys.get_status(user_id)
    # Firestore 타임스탬프는 그대로 jsonify 하면 HTTP date 문자열이 된다 — 프론트가
    # 파싱하기 쉽게 ISO 로 맞춘다.
    s['created_at'] = _iso(s.get('created_at'))
    s['last_used'] = _iso(s.get('last_used'))
    return s


@og_key_bp.route('', methods=['GET'])
@login_required
def get_og_key():
    try:
        return jsonify(_status_payload(_user_id()))
    except og_keys.KeyVaultError as e:
        return jsonify({'error': str(e)}), 503
    except Exception:
        logger.exception('OG 키 상태 조회 실패')
        return jsonify({'error': '상태를 불러오지 못했어요.'}), 500


@og_key_bp.route('', methods=['POST'])
@login_required
def put_og_key():
    body = request.get_json(silent=True) or {}
    key = (body.get('key') or '').strip()

    if not key:
        return jsonify({'ok': False, 'error': '키를 입력해 주세요.'}), 400
    if not key.startswith(KEY_PREFIXES) or len(key) < KEY_MIN_LEN:
        return jsonify({'ok': False, 'error': 'OpenGateway 키 형식이 아니에요. apik_ 로 시작하는 값을 붙여넣어 주세요.'}), 400

    # 저장 전에 확인한다. 틀린 키를 받아두면 사용자는 그림을 칠 때가 되어서야
    # 실패를 보고, 그때는 원인이 키라는 걸 알 수가 없다.
    try:
        ok, reason = asyncio.run(verify_key(key))
    except Exception:
        logger.exception('OG 키 확인 중 오류')  # 키 값은 절대 로그에 넣지 않는다
        return jsonify({'ok': False, 'error': '키를 확인하지 못했어요. 잠시 후 다시 시도해 주세요.'}), 502
    if not ok:
        return jsonify({'ok': False, 'error': reason or '키가 올바르지 않아요.'}), 400

    try:
        result = og_keys.save_key(_user_id(), key)
    except og_keys.KeyVaultError as e:
        return jsonify({'ok': False, 'error': str(e)}), 503
    except Exception:
        logger.exception('OG 키 저장 실패')
        return jsonify({'ok': False, 'error': '저장하지 못했어요.'}), 500

    if not result.get('ok'):
        return jsonify({'ok': False, 'error': '키를 저장하지 못했어요.'}), 400

    return jsonify({'ok': True, **_status_payload(_user_id())})


@og_key_bp.route('', methods=['DELETE'])
@login_required
def remove_og_key():
    try:
        removed = og_keys.delete_key(_user_id())
    except Exception:
        logger.exception('OG 키 삭제 실패')
        return jsonify({'ok': False, 'error': '해제하지 못했어요.'}), 500
    return jsonify({'ok': True, 'removed': removed, 'connected': False})
