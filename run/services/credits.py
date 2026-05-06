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
