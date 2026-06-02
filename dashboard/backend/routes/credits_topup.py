"""크레딧 충전 결제 라우트 (Toss Payments).

엔드포인트 (prefix /api/credits/topup):
- GET  /packages  — 충전 패키지 목록
- POST /checkout   — 주문 생성 (orderId 발급 + pending 저장)
- POST /confirm    — 결제 승인 (서버가 금액 결정, Toss confirm, 멱등 적립)
- POST /webhook    — Toss PAYMENT_STATUS_CHANGED (결제 재조회로 검증 + 멱등 적립)
- POST /refund     — 미사용분 환불 (7일 이내)

보안 원칙:
- 결제 금액은 절대 클라이언트를 신뢰하지 않는다. 서버가 orderId→패키지→금액을 결정.
- 중복 적립은 credits_service.apply_topup 의 트랜잭션 멱등성으로 차단.
- Toss webhook 은 표준 서명이 없으므로 paymentKey 로 결제를 재조회해 진위를 확인한다.
"""

from __future__ import annotations

import base64
import logging
import os
import sys
from datetime import datetime, timezone
from functools import wraps

import requests
from flask import Blueprint, jsonify, request, session

# run.services.credits 임포트를 위해 프로젝트 루트 sys.path 보장.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from run.services import credits as credits_service  # noqa: E402

logger = logging.getLogger(__name__)
credits_topup_bp = Blueprint('credits_topup', __name__)

TOSS_API_URL = 'https://api.tosspayments.com/v1'

# 충전 패키지 — 점증 보너스형. krw = 결제 금액, credits = 지급 크레딧.
# 이 정의가 금액·크레딧의 단일 진실. checkout/confirm 모두 여기서만 읽는다.
TOPUP_PACKAGES = {
    'pkg_1k':  {'krw': 1000,  'credits': 100,  'label': '100 크레딧',          'bonus': 0},
    'pkg_5k':  {'krw': 5000,  'credits': 600,  'label': '600 크레딧 (+20%)',   'bonus': 20},
    'pkg_10k': {'krw': 10000, 'credits': 1300, 'label': '1,300 크레딧 (+30%)', 'bonus': 30},
    'pkg_30k': {'krw': 30000, 'credits': 4500, 'label': '4,500 크레딧 (+50%)', 'bonus': 50},
}


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper


def _toss_auth_header() -> dict:
    """Toss Basic 인증 헤더. 시크릿은 요청 시점에만 읽고 로그에 남기지 않는다."""
    secret = os.getenv('TOSS_SECRET_KEY')
    if not secret:
        raise RuntimeError('TOSS_SECRET_KEY not configured')
    encoded = base64.b64encode(f'{secret}:'.encode()).decode()
    return {'Authorization': f'Basic {encoded}'}


def _toss_get_payment(payment_key: str) -> dict | None:
    """paymentKey 로 결제 조회. webhook 진위 확인용."""
    try:
        resp = requests.get(
            f'{TOSS_API_URL}/payments/{payment_key}',
            headers=_toss_auth_header(),
            timeout=10,
        )
        if resp.ok:
            return resp.json()
        logger.error('Toss payment lookup failed: %s', resp.status_code)
    except (requests.RequestException, RuntimeError) as e:
        logger.error('Toss payment lookup error: %s', e)
    return None


def _topup_live_ready() -> bool:
    """프로덕션에서 테스트 키로 무료 크레딧을 무한 충전하는 악용을 차단.
    라이브 키(live_)이거나 개발 환경(FLASK_ENV=development)일 때만 충전 허용한다.
    테스트 키는 결제 금액이 0원이라, 프로덕션에 노출되면 누구나 테스트카드로 공짜 적립이 가능하다."""
    secret = os.getenv('TOSS_SECRET_KEY', '') or ''
    if secret.startswith('live_'):
        return True
    if os.getenv('FLASK_ENV') == 'development':
        return True
    return False


@credits_topup_bp.route('/packages', methods=['GET'])
def packages():
    """충전 패키지 목록 (비로그인도 조회 가능 — 가격 안내용)."""
    return jsonify({
        'packages': [
            {'id': pid, 'krw': p['krw'], 'credits': p['credits'],
             'label': p['label'], 'bonus': p['bonus']}
            for pid, p in TOPUP_PACKAGES.items()
        ]
    })


@credits_topup_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """주문 생성. orderId 발급 + Firestore pending 저장. 금액은 서버가 결정."""
    if not _topup_live_ready():
        return jsonify({'error': '크레딧 충전은 정식 오픈 준비 중입니다. 곧 만나요!'}), 503
    user = session['user']
    body = request.get_json(silent=True) or {}
    pkg_id = body.get('package_id')
    pkg = TOPUP_PACKAGES.get(pkg_id)
    if not pkg:
        return jsonify({'error': 'invalid_package'}), 400

    user_id = str(user['id'])
    ts = int(datetime.now(timezone.utc).timestamp())
    order_id = f'topup_{user_id}_{pkg_id}_{ts}'

    res = credits_service.create_topup_order(
        user_id, order_id, pkg_id, pkg['krw'], pkg['credits'])
    if not res.get('ok'):
        logger.error('create_topup_order failed: %s', res.get('reason'))
        return jsonify({'error': 'order_create_failed'}), 503

    return jsonify({
        'orderId': order_id,
        'amount': pkg['krw'],
        'orderName': f"데비마를렌 {pkg['credits']} 크레딧",
        'customerKey': f'ckey_{user_id}',
    })


@credits_topup_bp.route('/confirm', methods=['POST'])
@login_required
def confirm():
    """결제 승인. 클라가 보낸 amount 는 무시하고 서버가 orderId 로 금액을 결정."""
    if not _topup_live_ready():
        return jsonify({'error': '크레딧 충전은 정식 오픈 준비 중입니다.'}), 503
    user = session['user']
    body = request.get_json(silent=True) or {}
    payment_key = body.get('paymentKey')
    order_id = body.get('orderId')
    if not payment_key or not order_id:
        return jsonify({'error': 'missing_fields'}), 400

    order = credits_service.get_topup_order(order_id)
    if not order:
        return jsonify({'error': 'order_not_found'}), 404
    if str(order.get('user_id')) != str(user['id']):
        return jsonify({'error': 'forbidden'}), 403

    # 이미 적립된 주문 — 멱등 응답 (재적립 없음).
    if order.get('status') == 'completed':
        return jsonify({'success': True, 'already': True,
                        'credits': order.get('credits')}), 200
    if order.get('status') != 'pending':
        return jsonify({'error': f"order_{order.get('status')}"}), 409

    # 서버가 결정한 금액만 사용 (클라이언트 amount 무시).
    amount = int(order['krw'])

    try:
        resp = requests.post(
            f'{TOSS_API_URL}/payments/confirm',
            headers={**_toss_auth_header(), 'Content-Type': 'application/json'},
            json={'paymentKey': payment_key, 'orderId': order_id, 'amount': amount},
            timeout=10,
        )
    except RuntimeError:
        logger.error('TOSS_SECRET_KEY missing on confirm')
        return jsonify({'error': 'config_error'}), 500
    except requests.RequestException as e:
        logger.error('Toss confirm request failed: %s', e)
        return jsonify({'error': 'payment_request_failed'}), 502

    if not resp.ok:
        err = resp.json() if resp.content else {}
        logger.error('Toss confirm failed: %s %s', err.get('code'), err.get('message'))
        return jsonify({'error': err.get('message', 'payment_failed'),
                        'code': err.get('code')}), 400

    # 승인 성공(=결제 완료, 돈 수취) → 멱등 적립.
    res = credits_service.apply_topup(order_id, payment_key=payment_key)
    if not res.get('ok'):
        # 결제는 성공했으나 적립 실패. webhook 이 백업 경로지만 best-effort 이고
        # Firestore 상관 장애면 함께 실패할 수 있어 자동 복구가 보장되지 않는다.
        # 수동 복구를 위해 결제 정보를 로깅하고 주문에 적립실패(paid_unapplied)를 마킹한다.
        logger.error('CRITICAL apply_topup failed after PAID: order=%s paymentKey=%s res=%s '
                     '-- manual credit needed', order_id, payment_key, res)
        try:
            credits_service.mark_topup_apply_failed(order_id, payment_key)
        except Exception:
            pass
        return jsonify({
            'error': 'credit_apply_failed',
            'message': '결제는 완료됐으나 크레딧 적립이 지연되고 있습니다. 잠시 후 잔고를 확인하시고, 반영되지 않으면 문의해 주세요.',
        }), 500

    return jsonify({'success': True,
                    'credits': res.get('credits'),
                    'balance': res.get('balance'),
                    'already': res.get('already', False)}), 200


@credits_topup_bp.route('/webhook', methods=['POST'])
def webhook():
    """Toss PAYMENT_STATUS_CHANGED. 서명이 없으므로 paymentKey 재조회로 검증."""
    data = request.get_json(silent=True) or {}
    event_type = data.get('eventType')
    if event_type != 'PAYMENT_STATUS_CHANGED':
        return jsonify({'status': 'ignored'}), 200

    payment = data.get('data', {})
    order_id = payment.get('orderId')
    payment_key = payment.get('paymentKey')
    if not order_id or not payment_key:
        return jsonify({'status': 'ignored'}), 200

    # 우리 주문이 아니면 무시.
    order = credits_service.get_topup_order(order_id)
    if not order:
        return jsonify({'status': 'unknown_order'}), 200

    # webhook payload 를 신뢰하지 않고 Toss 에 실제 상태를 재조회.
    verified = _toss_get_payment(payment_key)
    if not verified or verified.get('orderId') != order_id:
        logger.warning('webhook verify mismatch: order=%s', order_id)
        return jsonify({'status': 'verify_failed'}), 200

    status = verified.get('status')
    if status == 'DONE':
        res = credits_service.apply_topup(order_id, payment_key=payment_key)
        logger.info('webhook topup applied: order=%s ok=%s already=%s',
                    order_id, res.get('ok'), res.get('already'))
    elif status in ('CANCELED', 'PARTIAL_CANCELED'):
        credits_service.mark_topup_canceled(order_id, status.lower())

    return jsonify({'status': 'success'}), 200


@credits_topup_bp.route('/refund', methods=['POST'])
@login_required
def refund():
    """미사용분 환불. 크레딧 차감 → Toss 취소 → 실패 시 크레딧 복구."""
    user = session['user']
    body = request.get_json(silent=True) or {}
    order_id = body.get('orderId')
    if not order_id:
        return jsonify({'error': 'missing_orderId'}), 400

    order = credits_service.get_topup_order(order_id)
    if not order:
        return jsonify({'error': 'order_not_found'}), 404
    if str(order.get('user_id')) != str(user['id']):
        return jsonify({'error': 'forbidden'}), 403

    # 1) 크레딧 차감 + 상태 refunded (트랜잭션). 미사용분 아니면 ok:false.
    res = credits_service.refund_topup(order_id)
    if not res.get('ok'):
        # 정책 위반(사용함/기간만료 등)은 200 + ok:false 로 클라가 안내.
        return jsonify(res), 200

    payment_key = res.get('payment_key')
    refund_credits = int(res.get('refund_credits', 0))
    user_id = str(user['id'])

    # 2) Toss 결제 취소.
    if payment_key:
        try:
            cancel_resp = requests.post(
                f'{TOSS_API_URL}/payments/{payment_key}/cancel',
                headers={**_toss_auth_header(), 'Content-Type': 'application/json'},
                json={'cancelReason': '사용자 환불 요청 (미사용 크레딧)'},
                timeout=10,
            )
        except (requests.RequestException, RuntimeError) as e:
            # Toss 취소 호출 자체 실패 → 크레딧 복구 (보상).
            logger.error('Toss cancel request failed: %s — reverting credits', e)
            credits_service.revert_refund(order_id, user_id, refund_credits)
            return jsonify({'ok': False, 'reason': 'cancel_request_failed'}), 502

        if not cancel_resp.ok:
            err = cancel_resp.json() if cancel_resp.content else {}
            logger.error('Toss cancel failed: %s — reverting credits', err.get('message'))
            credits_service.revert_refund(order_id, user_id, refund_credits)
            return jsonify({'ok': False, 'reason': 'cancel_failed',
                            'message': err.get('message')}), 400

    return jsonify({'ok': True, 'refunded_credits': refund_credits,
                    'balance': res.get('balance'), 'krw': res.get('krw')}), 200
