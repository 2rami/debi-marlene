"""크레딧 시스템 — 이터널리턴 게임 재화 모티프.

룰 (확정):
- 일일 출석: +10. 연속 3일 +30 보너스. 연속 7일 +100 보너스.
- 봇 대화 메시지당 -2 (chat.py 일일 무료 5회 초과분).
- TTS 10초당 -1 (반올림 ceil).
- /뽑기: 70% 0배 / 20% 2배 / 8% 3배 / 2% 10배. 일일 베팅 합 50 상한.
- 기부: 개인 → 서버 공동 지갑.

Firestore 컬렉션:
- credits/{user_id}: { balance, last_check_in, streak_days, daily_bet, daily_bet_date }
- guild_credits/{guild_id}: { balance }
- credit_ledger/{auto_id}: { user_id, guild_id?, type, amount, reason, ts }

모든 mutating 연산은 firestore transaction 으로 race 방지.
ledger 는 같은 트랜잭션에 추가해서 원장-잔고 정합성 유지.
"""

from __future__ import annotations

import math
import random
from datetime import date, datetime, timezone
from typing import Optional

from google.cloud import firestore  # type: ignore

from run.core.config import get_firestore_client


CREDITS_COLLECTION = 'credits'
GUILD_CREDITS_COLLECTION = 'guild_credits'
LEDGER_COLLECTION = 'credit_ledger'

DAILY_CHECK_IN = 10
STREAK_3_BONUS = 30
STREAK_7_BONUS = 100

CHAT_COST = 2  # /대화 메시지당
TTS_COST_PER_10S = 1

GACHA_DAILY_BET_CAP = 50
# 누적분포: 70 / 90 / 98 / 100
GACHA_TABLE = [
    (0.70, 0),   # 0배 (꽝)
    (0.90, 2),   # 2배
    (0.98, 3),   # 3배
    (1.00, 10),  # 10배
]


# ───────────────────── 헬퍼 ─────────────────────

def _today_kst_str() -> str:
    """KST 기준 오늘 날짜 string. 출석/베팅 일자 키로 사용."""
    # 봇·대시보드 모두 UTC 환경이라 +9 보정. 실서버 영향 없음.
    from datetime import timedelta
    return (datetime.now(timezone.utc) + timedelta(hours=9)).date().isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_user_doc() -> dict:
    return {
        'balance': 0,
        'last_check_in': None,    # ISO date string (YYYY-MM-DD, KST)
        'streak_days': 0,
        'daily_bet': 0,
        'daily_bet_date': None,
    }


def _add_ledger(transaction, user_id: str, type_: str, amount: int, reason: str,
                guild_id: Optional[str] = None) -> None:
    """transaction 에 ledger 항목 1개 추가. auto-id 문서."""
    fs = get_firestore_client()
    if not fs:
        return
    ref = fs.collection(LEDGER_COLLECTION).document()  # auto-id
    payload = {
        'user_id': str(user_id),
        'type': type_,
        'amount': int(amount),
        'reason': reason,
        'ts': _now_iso(),
    }
    if guild_id is not None:
        payload['guild_id'] = str(guild_id)
    transaction.set(ref, payload)


# ───────────────────── 조회 ─────────────────────

def get_balance(user_id) -> dict:
    """잔고 조회 (논블로킹). { personal, last_check_in, streak_days, daily_bet }."""
    fs = get_firestore_client()
    if not fs:
        return {'personal': 0, 'last_check_in': None, 'streak_days': 0, 'daily_bet': 0}
    doc = fs.collection(CREDITS_COLLECTION).document(str(user_id)).get()
    data = doc.to_dict() if doc.exists else _empty_user_doc()
    today = _today_kst_str()
    return {
        'personal': int(data.get('balance', 0)),
        'last_check_in': data.get('last_check_in'),
        'streak_days': int(data.get('streak_days', 0)),
        'daily_bet': int(data.get('daily_bet', 0)) if data.get('daily_bet_date') == today else 0,
        'checked_in_today': data.get('last_check_in') == today,
    }


def get_guild_balance(guild_id) -> int:
    fs = get_firestore_client()
    if not fs:
        return 0
    doc = fs.collection(GUILD_CREDITS_COLLECTION).document(str(guild_id)).get()
    return int((doc.to_dict() or {}).get('balance', 0)) if doc.exists else 0


# ───────────────────── 출석 ─────────────────────

def check_attendance(user_id) -> dict:
    """일일 출석. 이미 받았으면 gained=0. 연속 보너스 계산."""
    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'gained': 0, 'balance': 0, 'streak': 0,
                'reason': 'firestore_unavailable'}

    user_ref = fs.collection(CREDITS_COLLECTION).document(str(user_id))
    today = _today_kst_str()

    @firestore.transactional
    def _txn(transaction):
        snap = user_ref.get(transaction=transaction)
        data = snap.to_dict() if snap.exists else _empty_user_doc()

        last = data.get('last_check_in')
        if last == today:
            return {
                'ok': True, 'already': True, 'gained': 0,
                'balance': int(data.get('balance', 0)),
                'streak': int(data.get('streak_days', 0)),
                'bonus': 0,
            }

        # streak 계산: 어제면 +1, 아니면 1로 리셋
        from datetime import timedelta as _td
        yesterday = (datetime.fromisoformat(today) - _td(days=1)).date().isoformat()
        streak = int(data.get('streak_days', 0))
        new_streak = streak + 1 if last == yesterday else 1

        gained = DAILY_CHECK_IN
        bonus = 0
        # 7 우선 (3 의 배수이기도 해서 중복 지급 방지)
        if new_streak > 0 and new_streak % 7 == 0:
            bonus = STREAK_7_BONUS
        elif new_streak > 0 and new_streak % 3 == 0:
            bonus = STREAK_3_BONUS
        gained += bonus

        new_balance = int(data.get('balance', 0)) + gained
        update = {
            'balance': new_balance,
            'last_check_in': today,
            'streak_days': new_streak,
        }
        # 신규 doc 이면 누락 키 채워서 set, 기존이면 update
        if not snap.exists:
            base = _empty_user_doc()
            base.update(update)
            transaction.set(user_ref, base)
        else:
            transaction.update(user_ref, update)

        _add_ledger(transaction, str(user_id), 'check_in', gained,
                    f'daily_check_in streak={new_streak} bonus={bonus}')
        return {
            'ok': True, 'already': False, 'gained': gained, 'bonus': bonus,
            'balance': new_balance, 'streak': new_streak,
        }

    return _txn(fs.transaction())


# ───────────────────── 차감 / 적립 ─────────────────────

def debit(user_id, amount: int, reason: str) -> dict:
    """잔고에서 amount 차감. 부족하면 ok=False. 트랜잭션."""
    if amount <= 0:
        return {'ok': True, 'balance': get_balance(user_id)['personal'], 'charged': 0}

    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'reason': 'firestore_unavailable', 'balance': 0}

    user_ref = fs.collection(CREDITS_COLLECTION).document(str(user_id))

    @firestore.transactional
    def _txn(transaction):
        snap = user_ref.get(transaction=transaction)
        data = snap.to_dict() if snap.exists else _empty_user_doc()
        balance = int(data.get('balance', 0))
        if balance < amount:
            return {'ok': False, 'reason': 'insufficient', 'balance': balance, 'needed': amount}
        new_balance = balance - amount
        if not snap.exists:
            base = _empty_user_doc()
            base['balance'] = new_balance
            transaction.set(user_ref, base)
        else:
            transaction.update(user_ref, {'balance': new_balance})
        _add_ledger(transaction, str(user_id), 'debit', -amount, reason)
        return {'ok': True, 'balance': new_balance, 'charged': amount}

    return _txn(fs.transaction())


def credit(user_id, amount: int, reason: str) -> dict:
    """잔고에 amount 추가. 트랜잭션."""
    if amount <= 0:
        return {'ok': True, 'balance': get_balance(user_id)['personal'], 'gained': 0}

    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'reason': 'firestore_unavailable', 'balance': 0}

    user_ref = fs.collection(CREDITS_COLLECTION).document(str(user_id))

    @firestore.transactional
    def _txn(transaction):
        snap = user_ref.get(transaction=transaction)
        data = snap.to_dict() if snap.exists else _empty_user_doc()
        new_balance = int(data.get('balance', 0)) + amount
        if not snap.exists:
            base = _empty_user_doc()
            base['balance'] = new_balance
            transaction.set(user_ref, base)
        else:
            transaction.update(user_ref, {'balance': new_balance})
        _add_ledger(transaction, str(user_id), 'credit', amount, reason)
        return {'ok': True, 'balance': new_balance, 'gained': amount}

    return _txn(fs.transaction())


def debit_for_tts(user_id, seconds: float, reason_suffix: str = '') -> dict:
    """TTS 길이 기반 차감. 10초당 1, ceil. 0.5초 미만은 무료."""
    if seconds <= 0.5:
        return {'ok': True, 'charged': 0, 'balance': get_balance(user_id)['personal']}
    cost = max(1, math.ceil(seconds / 10.0)) * TTS_COST_PER_10S
    reason = f'tts_{seconds:.1f}s' + (f' {reason_suffix}' if reason_suffix else '')
    return debit(user_id, cost, reason)


# ───────────────────── 기부 ─────────────────────

def donate(user_id, guild_id, amount: int) -> dict:
    """개인 → 서버 공동 지갑. 트랜잭션 (양쪽 doc + ledger)."""
    if amount <= 0:
        return {'ok': False, 'reason': 'amount_must_be_positive'}

    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'reason': 'firestore_unavailable'}

    user_ref = fs.collection(CREDITS_COLLECTION).document(str(user_id))
    guild_ref = fs.collection(GUILD_CREDITS_COLLECTION).document(str(guild_id))

    @firestore.transactional
    def _txn(transaction):
        u_snap = user_ref.get(transaction=transaction)
        g_snap = guild_ref.get(transaction=transaction)

        u_data = u_snap.to_dict() if u_snap.exists else _empty_user_doc()
        balance = int(u_data.get('balance', 0))
        if balance < amount:
            return {'ok': False, 'reason': 'insufficient', 'balance': balance, 'needed': amount}

        g_balance = int((g_snap.to_dict() or {}).get('balance', 0)) if g_snap.exists else 0
        new_user_balance = balance - amount
        new_guild_balance = g_balance + amount

        if not u_snap.exists:
            base = _empty_user_doc()
            base['balance'] = new_user_balance
            transaction.set(user_ref, base)
        else:
            transaction.update(user_ref, {'balance': new_user_balance})

        if not g_snap.exists:
            transaction.set(guild_ref, {'balance': new_guild_balance})
        else:
            transaction.update(guild_ref, {'balance': new_guild_balance})

        _add_ledger(transaction, str(user_id), 'donate', -amount,
                    f'donate_to_guild', guild_id=str(guild_id))
        return {
            'ok': True, 'personal_balance': new_user_balance,
            'guild_balance': new_guild_balance, 'donated': amount,
        }

    return _txn(fs.transaction())


# ───────────────────── 뽑기 ─────────────────────

def gacha(user_id, bet: int) -> dict:
    """룰렛. 베팅액 즉시 차감 후 멀티플라이어만큼 환급.

    일일 베팅 합산 50 상한 (KST 자정 리셋).
    Returns: { ok, multiplier, payout, net, balance, daily_bet, ... }
    """
    if bet <= 0:
        return {'ok': False, 'reason': 'bet_must_be_positive'}

    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'reason': 'firestore_unavailable'}

    user_ref = fs.collection(CREDITS_COLLECTION).document(str(user_id))
    today = _today_kst_str()

    @firestore.transactional
    def _txn(transaction):
        snap = user_ref.get(transaction=transaction)
        data = snap.to_dict() if snap.exists else _empty_user_doc()
        balance = int(data.get('balance', 0))

        # 일일 베팅 합산 (날짜 다르면 리셋)
        used_today = int(data.get('daily_bet', 0)) if data.get('daily_bet_date') == today else 0
        if used_today + bet > GACHA_DAILY_BET_CAP:
            return {
                'ok': False, 'reason': 'daily_cap', 'cap': GACHA_DAILY_BET_CAP,
                'used_today': used_today, 'remaining': GACHA_DAILY_BET_CAP - used_today,
            }
        if balance < bet:
            return {'ok': False, 'reason': 'insufficient', 'balance': balance, 'needed': bet}

        # 결과 추첨
        roll = random.random()
        multiplier = 0
        for cum, mult in GACHA_TABLE:
            if roll < cum:
                multiplier = mult
                break
        payout = bet * multiplier
        net = payout - bet
        new_balance = balance - bet + payout
        new_daily_bet = used_today + bet

        update = {
            'balance': new_balance,
            'daily_bet': new_daily_bet,
            'daily_bet_date': today,
        }
        if not snap.exists:
            base = _empty_user_doc()
            base.update(update)
            transaction.set(user_ref, base)
        else:
            transaction.update(user_ref, update)

        _add_ledger(transaction, str(user_id), 'gacha', net,
                    f'gacha bet={bet} mult={multiplier}x payout={payout}')
        return {
            'ok': True, 'multiplier': multiplier, 'bet': bet,
            'payout': payout, 'net': net, 'balance': new_balance,
            'daily_bet': new_daily_bet, 'daily_cap': GACHA_DAILY_BET_CAP,
        }

    return _txn(fs.transaction())


# ───────────────────── 원장 조회 ─────────────────────

def get_recent_ledger(user_id, limit: int = 20) -> list[dict]:
    """최근 거래 내역 (대시보드 표시용)."""
    fs = get_firestore_client()
    if not fs:
        return []
    try:
        from google.cloud.firestore_v1 import Query as FsQuery
        q = (fs.collection(LEDGER_COLLECTION)
               .where('user_id', '==', str(user_id))
               .order_by('ts', direction=FsQuery.DESCENDING)
               .limit(limit))
        return [d.to_dict() for d in q.stream()]
    except Exception as e:
        print(f"[credits] ledger 조회 실패: {e}", flush=True)
        return []


def get_usage_summary(user_id, recent_limit: int = 20) -> dict:
    """크레딧 요약 (웹패널/대시보드 표시용).

    잔액 + 누적 지출/수입/충전 + 거래 횟수 + 최근 내역을 한 번에.
    원장 전체를 1회 스캔해 합산하고 최근 항목까지 같은 스트림에서 뽑는다.
    """
    out = {
        'balance': get_balance(user_id)['personal'],
        'total_spent': 0,    # 음수 거래 절댓값 합 (실제 소비)
        'total_earned': 0,   # 양수 거래 합 (출석·기부·충전 등 유입)
        'total_topup': 0,    # 현금 충전으로 들어온 크레딧
        'tx_count': 0,
        'recent': [],
    }
    fs = get_firestore_client()
    if not fs:
        return out
    try:
        entries = [d.to_dict() for d in fs.collection(LEDGER_COLLECTION)
                   .where('user_id', '==', str(user_id)).stream()]
    except Exception as e:
        print(f"[credits] usage summary 조회 실패: {e}", flush=True)
        return out

    for e in entries:
        amt = int(e.get('amount', 0))
        if amt < 0:
            out['total_spent'] += -amt
        else:
            out['total_earned'] += amt
        if e.get('type') == 'topup' and amt > 0:
            out['total_topup'] += amt
    out['tx_count'] = len(entries)
    entries.sort(key=lambda x: x.get('ts', ''), reverse=True)
    out['recent'] = entries[:recent_limit]
    return out


def list_credit_holders(min_balance: int = 1, limit: int = 500) -> list[dict]:
    """크레딧 보유 유저 목록 (웹패널 크레딧 패널용). balance 내림차순."""
    fs = get_firestore_client()
    if not fs:
        return []
    try:
        out = []
        for d in fs.collection(CREDITS_COLLECTION).stream():
            data = d.to_dict() or {}
            bal = int(data.get('balance', 0))
            if bal >= min_balance:
                out.append({
                    'user_id': d.id,
                    'balance': bal,
                    'last_check_in': data.get('last_check_in'),
                    'streak_days': int(data.get('streak_days', 0)),
                })
        out.sort(key=lambda x: x['balance'], reverse=True)
        return out[:limit]
    except Exception as e:
        print(f"[credits] holders 조회 실패: {e}", flush=True)
        return []


def list_guild_credit_holders(min_balance: int = 1, limit: int = 500) -> list[dict]:
    """크레딧 보유 서버(공동 지갑) 목록. balance 내림차순."""
    fs = get_firestore_client()
    if not fs:
        return []
    try:
        out = []
        for d in fs.collection(GUILD_CREDITS_COLLECTION).stream():
            bal = int((d.to_dict() or {}).get('balance', 0))
            if bal >= min_balance:
                out.append({'guild_id': d.id, 'balance': bal})
        out.sort(key=lambda x: x['balance'], reverse=True)
        return out[:limit]
    except Exception as e:
        print(f"[credits] guild holders 조회 실패: {e}", flush=True)
        return []


def get_balances_batch(user_ids) -> dict:
    """여러 유저 잔액 일괄 조회 (멤버 목록 배지용). {user_id: balance}."""
    ids = [str(u) for u in user_ids if u]
    out = {uid: 0 for uid in ids}
    fs = get_firestore_client()
    if not fs or not ids:
        return out
    try:
        col = fs.collection(CREDITS_COLLECTION)
        for snap in fs.get_all([col.document(uid) for uid in ids]):
            if snap.exists:
                out[snap.id] = int((snap.to_dict() or {}).get('balance', 0))
    except Exception as e:
        print(f"[credits] 배치 잔액 조회 실패: {e}", flush=True)
    return out


# ───────────────────── 충전 (현금→크레딧, Toss) ─────────────────────

TOPUP_ORDERS_COLLECTION = 'topup_orders'

# 충전 후 환불 가능 기간 (완료 시각 기준)
TOPUP_REFUND_WINDOW_DAYS = 7


def create_topup_order(user_id, order_id: str, pkg_id: str,
                       krw: int, credits_amount: int) -> dict:
    """충전 주문 생성 (status=pending). checkout 단계에서 호출.

    금액·크레딧은 서버가 패키지 정의로 결정 — 클라이언트 입력은 신뢰하지 않는다.
    confirm/webhook 은 이 문서의 krw/credits 만 사용한다.
    """
    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'reason': 'firestore_unavailable'}
    ref = fs.collection(TOPUP_ORDERS_COLLECTION).document(order_id)
    ref.set({
        'user_id': str(user_id),
        'pkg_id': pkg_id,
        'krw': int(krw),
        'credits': int(credits_amount),
        'status': 'pending',
        'created_at': _now_iso(),
    })
    return {'ok': True, 'order_id': order_id}


def get_topup_order(order_id: str) -> Optional[dict]:
    fs = get_firestore_client()
    if not fs:
        return None
    doc = fs.collection(TOPUP_ORDERS_COLLECTION).document(order_id).get()
    return doc.to_dict() if doc.exists else None


def apply_topup(order_id: str, payment_key: Optional[str] = None) -> dict:
    """충전 적립 (멱등). order pending→completed + 잔고 증가 + ledger 를
    하나의 트랜잭션으로 원자 처리. 이미 completed 면 재적립 없이 already=True.

    confirm 라우트와 webhook 양쪽에서 호출돼도 한 번만 적립된다.
    """
    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'reason': 'firestore_unavailable'}

    order_ref = fs.collection(TOPUP_ORDERS_COLLECTION).document(order_id)

    @firestore.transactional
    def _txn(transaction):
        # 모든 read 를 write 보다 먼저 (firestore 트랜잭션 제약).
        o_snap = order_ref.get(transaction=transaction)
        if not o_snap.exists:
            return {'ok': False, 'reason': 'order_not_found'}
        order = o_snap.to_dict()
        status = order.get('status')
        if status == 'completed':
            return {'ok': True, 'already': True,
                    'credits': int(order.get('credits', 0)),
                    'user_id': order.get('user_id')}
        if status != 'pending':
            return {'ok': False, 'reason': f'status_{status}'}

        user_id = str(order['user_id'])
        credits_amount = int(order['credits'])
        user_ref = fs.collection(CREDITS_COLLECTION).document(user_id)
        u_snap = user_ref.get(transaction=transaction)
        u_data = u_snap.to_dict() if u_snap.exists else _empty_user_doc()
        new_balance = int(u_data.get('balance', 0)) + credits_amount

        if not u_snap.exists:
            base = _empty_user_doc()
            base['balance'] = new_balance
            transaction.set(user_ref, base)
        else:
            transaction.update(user_ref, {'balance': new_balance})

        order_update = {'status': 'completed', 'completed_at': _now_iso()}
        if payment_key:
            order_update['payment_key'] = payment_key
        transaction.update(order_ref, order_update)

        _add_ledger(transaction, user_id, 'topup', credits_amount,
                    f'topup_{order_id}')
        return {'ok': True, 'already': False, 'credits': credits_amount,
                'balance': new_balance, 'user_id': user_id}

    return _txn(fs.transaction())


def mark_topup_canceled(order_id: str, status: str = 'canceled') -> dict:
    """webhook CANCELED/PARTIAL_CANCELED 수신 시 주문 상태 표시 (트랜잭션).
    이미 적립/환불이 끝난 주문(completed/refunded/refund_failed)은 덮어쓰지 않는다 —
    apply_topup 과의 race 로 completed 가 canceled 로 뒤집혀 잔고-주문 불일치가
    생기는 것을 방지."""
    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'reason': 'firestore_unavailable'}
    ref = fs.collection(TOPUP_ORDERS_COLLECTION).document(order_id)

    @firestore.transactional
    def _txn(transaction):
        snap = ref.get(transaction=transaction)
        if not snap.exists:
            return {'ok': False, 'reason': 'order_not_found'}
        cur = (snap.to_dict() or {}).get('status')
        if cur in ('completed', 'refunded', 'refund_failed'):
            return {'ok': False, 'reason': f'already_{cur}'}
        transaction.update(ref, {'status': status, 'canceled_at': _now_iso()})
        return {'ok': True}

    return _txn(fs.transaction())


def _spend_since(user_id, since_iso: Optional[str]) -> int:
    """since_iso(ISO 시각) 이후 해당 사용자의 사용(차감) 크레딧 총합 (양수 반환).
    debit/donate/gacha 손실 등 amount<0 ledger 를 합산. 미사용분 환불 판정용 —
    충전 완료 이후 한 푼이라도 썼으면 0 보다 크다. 조회 실패 시 0(잔고 가드에 위임)."""
    if not since_iso:
        return 0
    fs = get_firestore_client()
    if not fs:
        return 0
    try:
        # user_id 단일 필드 쿼리만 사용 (composite index 불필요). ts/금액은 메모리 필터.
        q = fs.collection(LEDGER_COLLECTION).where('user_id', '==', str(user_id)).limit(1000)
        total = 0
        for d in q.stream():
            e = d.to_dict()
            ts = e.get('ts')
            if ts and ts > since_iso and int(e.get('amount', 0)) < 0:
                total += -int(e['amount'])
        return total
    except Exception as e:
        print(f"[credits] _spend_since 조회 실패: {e}", flush=True)
        return 0


def refund_topup(order_id: str) -> dict:
    """미사용분 환불 — 크레딧 차감 + 주문 상태 전환만 트랜잭션 처리.
    Toss 결제 취소 API 호출은 라우트 계층 담당.

    '미사용분만' 정책: 충전 완료(completed_at) 이후 해당 사용자의 차감 내역이 전혀
    없을 때만 전액 환불 (ledger 로 판정). 부분 사용분 환불은 미지원. 잔고 비교는 보조 가드.

    Returns: { ok, reason?, refund_credits?, balance?, krw?, payment_key? }
    """
    fs = get_firestore_client()
    if not fs:
        return {'ok': False, 'reason': 'firestore_unavailable'}

    order_ref = fs.collection(TOPUP_ORDERS_COLLECTION).document(order_id)

    # 트랜잭션 전 ledger 판정: 단일 fungible balance 비교(아래 가드)만으로는 다른 충전이
    # 잔고를 올려 '이미 다 쓴 충전'을 환불 가능으로 오판한다. 해당 주문 완료 이후의 실제
    # 차감을 확인해, 한 푼이라도 썼으면 거부한다.
    order_pre = get_topup_order(order_id)
    if order_pre and order_pre.get('status') == 'completed':
        since = order_pre.get('completed_at') or order_pre.get('created_at')
        if _spend_since(order_pre.get('user_id'), since) > 0:
            return {'ok': False, 'reason': 'credits_already_used'}

    @firestore.transactional
    def _txn(transaction):
        o_snap = order_ref.get(transaction=transaction)
        if not o_snap.exists:
            return {'ok': False, 'reason': 'order_not_found'}
        order = o_snap.to_dict()
        if order.get('status') != 'completed':
            return {'ok': False, 'reason': 'not_refundable_status'}

        # 환불 기간 체크 (완료 시각 기준 N일).
        from datetime import timedelta as _td
        created = order.get('completed_at') or order.get('created_at')
        if created:
            try:
                created_dt = datetime.fromisoformat(created)
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - created_dt > _td(days=TOPUP_REFUND_WINDOW_DAYS):
                    return {'ok': False, 'reason': 'refund_window_expired'}
            except ValueError:
                pass

        user_id = str(order['user_id'])
        credits_amount = int(order['credits'])
        user_ref = fs.collection(CREDITS_COLLECTION).document(user_id)
        u_snap = user_ref.get(transaction=transaction)
        balance = int((u_snap.to_dict() or {}).get('balance', 0)) if u_snap.exists else 0

        # 미사용분만 환불: 충전 크레딧이 잔고에 그대로 남아있어야 환불 가능.
        if balance < credits_amount:
            return {'ok': False, 'reason': 'credits_already_used',
                    'balance': balance, 'topup_credits': credits_amount}

        new_balance = balance - credits_amount
        transaction.update(user_ref, {'balance': new_balance})
        transaction.update(order_ref, {'status': 'refunded', 'refunded_at': _now_iso()})
        _add_ledger(transaction, user_id, 'topup', -credits_amount, f'refund_{order_id}')
        return {'ok': True, 'refund_credits': credits_amount, 'balance': new_balance,
                'krw': int(order.get('krw', 0)), 'payment_key': order.get('payment_key')}

    return _txn(fs.transaction())


def revert_refund(order_id: str, user_id, credits_amount: int) -> dict:
    """refund_topup 후 Toss 취소 API 가 실패했을 때 크레딧 복구 (보상).
    주문은 'refund_failed' (terminal) 로 표시한다 — refund_topup 은 completed 만
    환불하므로 같은 주문의 재환불 무한루프가 차단된다. 재환불이 필요하면 관리자 수동 처리."""
    res = credit(user_id, credits_amount, f'refund_revert_{order_id}')
    fs = get_firestore_client()
    if fs:
        try:
            fs.collection(TOPUP_ORDERS_COLLECTION).document(order_id).update(
                {'status': 'refund_failed', 'refund_failed_at': _now_iso()})
        except Exception:
            pass
    return res


def mark_topup_apply_failed(order_id: str, payment_key: Optional[str] = None) -> dict:
    """confirm 에서 결제 성공(돈 수취) 후 apply_topup 이 실패했을 때 수동 복구 식별용 마킹.
    status 는 pending 유지(webhook/수동 재적립이 apply_topup 멱등으로 처리). paid_unapplied
    플래그로 '돈은 받았으나 미적립'된 주문을 골라낼 수 있다."""
    fs = get_firestore_client()
    if not fs:
        return {'ok': False}
    try:
        upd = {'apply_failed_at': _now_iso(), 'paid_unapplied': True}
        if payment_key:
            upd['payment_key'] = payment_key
        fs.collection(TOPUP_ORDERS_COLLECTION).document(order_id).update(upd)
        return {'ok': True}
    except Exception:
        return {'ok': False}
