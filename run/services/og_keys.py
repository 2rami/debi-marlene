"""OpenGateway API 키 보관 — 사용자가 자기 키로 자기 카드에서 결제한다.

봇은 키를 대신 들고 부를 뿐이고 요금은 키 주인에게 청구된다. 남의 결제 수단이므로
평문으로 두지 않는다 — DB 를 읽을 수 있는 사람이 곧 남의 카드를 쓸 수 있게 되기 때문이다.

Firestore `og_keys/{user_id}`:
    key_enc     Fernet 로 잠근 키 (평문은 어디에도 안 남는다)
    key_tail    화면 표시용 끝 4자. 원본 복구용이 아니라 "어느 키인지" 구분용
    created_at  등록 시각
    last_used   마지막 사용
    calls       누적 호출 수 (사용자에게 "얼마 썼는지" 보여주려고 봇이 직접 센다 —
                게이트웨이는 API 키로 잔액을 알려주지 않는다)
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from google.cloud import firestore  # type: ignore

from run.core.config import get_firestore_client

COLLECTION = 'og_keys'

# 한 장에 드는 대략 비용(USD). 사용자에게 "이만큼 나갔어요" 를 보여주는 데만 쓴다 —
# 정확한 청구는 게이트웨이가 하므로 이 값은 안내용 추정치다.
COST_PER_IMAGE_USD = 0.05

# ── 크레딧 "상당" 환산 ────────────────────────────────────────────────
# 봇에는 이미 크레딧이라는 자가 있는데(대화·TTS) 이미지만 달러로 말하면 사용자가
# 두 화폐를 머릿속에서 환산해야 한다. 그래서 **보이는 단위만** 크레딧으로 맞춘다.
#
# ⚠️실제로 차감되는 것은 봇 크레딧이 아니라 **사용자 본인 OG 잔액**이다.
# 화면에는 반드시 "상당" 을 붙여 오해를 막는다 — 안 그러면 "왜 크레딧이 안 줄지?" 가 된다.
USD_TO_KRW = 1400          # 안내용 근사치. 정밀 환산이 목적이 아니다
KRW_PER_CREDIT = 10        # 기본 충전가 기준(1,000원 = 100크레딧)


def credits_equivalent(images: int = 1) -> int:
    """이미지 N장이 봇 크레딧으로 치면 몇 개어치인지. 표시 전용."""
    krw = COST_PER_IMAGE_USD * USD_TO_KRW * max(images, 0)
    return max(1, round(krw / KRW_PER_CREDIT)) if images else 0


CREDITS_PER_IMAGE = credits_equivalent(1)


class KeyVaultError(RuntimeError):
    """암호가 준비 안 됐을 때. 키를 평문으로 저장하느니 거절한다."""


def _fernet():
    from cryptography.fernet import Fernet  # 지연 import — 이 기능을 안 쓰는 프로세스도 있다

    secret = os.getenv('OG_KEY_SECRET')
    if not secret:
        raise KeyVaultError(
            'OG_KEY_SECRET 이 없습니다. '
            "`python -c \"from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())\"` "
            '로 만들어 .env 에 넣으세요.'
        )
    try:
        return Fernet(secret.encode() if isinstance(secret, str) else secret)
    except Exception as e:
        raise KeyVaultError(f'OG_KEY_SECRET 형식이 잘못됐습니다: {e}') from e


def _doc(user_id):
    db = get_firestore_client()
    if db is None:
        # 인증이 안 되면 클라이언트가 None 으로 온다. 그대로 두면 한참 뒤에
        # AttributeError 로 터져서 원인이 안 보인다.
        raise KeyVaultError(
            'Firestore 에 연결하지 못했습니다. GOOGLE_APPLICATION_CREDENTIALS 를 확인하세요.'
        )
    return db.collection(COLLECTION).document(str(user_id))


def save_key(user_id, api_key: str) -> dict:
    """키를 잠가서 저장. 이미 있으면 덮어쓴다(재발급 대응)."""
    api_key = (api_key or '').strip()
    if not api_key:
        return {'ok': False, 'reason': 'empty'}

    enc = _fernet().encrypt(api_key.encode()).decode()
    now = datetime.now(timezone.utc)
    _doc(user_id).set({
        'key_enc': enc,
        'key_tail': api_key[-4:],
        'created_at': now,
        'last_used': None,
        'calls': 0,
    }, merge=True)
    return {'ok': True, 'key_tail': api_key[-4:]}


def get_key(user_id) -> Optional[str]:
    """복호화한 키. 없으면 None."""
    snap = _doc(user_id).get()
    if not snap.exists:
        return None
    enc = (snap.to_dict() or {}).get('key_enc')
    if not enc:
        return None
    try:
        return _fernet().decrypt(enc.encode()).decode()
    except Exception:
        # 암호가 바뀌었거나 손상됐다. 못 푸는 키는 없는 것과 같다.
        return None


def delete_key(user_id) -> bool:
    """등록 해제. 사용자가 언제든 뺄 수 있어야 키를 맡긴다."""
    doc = _doc(user_id)
    if not doc.get().exists:
        return False
    doc.delete()
    return True


def get_status(user_id) -> dict:
    """화면에 보여줄 상태. 키 자체는 절대 돌려주지 않는다."""
    snap = _doc(user_id).get()
    if not snap.exists:
        return {'connected': False}
    d = snap.to_dict() or {}
    calls = int(d.get('calls') or 0)
    return {
        'connected': bool(d.get('key_enc')),
        'key_tail': d.get('key_tail'),
        'created_at': d.get('created_at'),
        'last_used': d.get('last_used'),
        'calls': calls,
        'est_usd': round(calls * COST_PER_IMAGE_USD, 2),
        'est_credits': credits_equivalent(calls),
    }


def record_use(user_id) -> None:
    """호출 1건 기록. 실패해도 그림 생성 자체를 막지는 않는다."""
    try:
        _doc(user_id).update({
            'calls': firestore.Increment(1),
            'last_used': datetime.now(timezone.utc),
        })
    except Exception:
        pass
