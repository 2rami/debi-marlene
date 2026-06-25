"""이탈(서버 추방) 사유 수집 — Firestore churn_feedback 컬렉션.

봇이 서버에서 제거될 때 owner 설문 응답을 저장한다.
잠든 서버 / 이탈 원인을 데이터로 파악해 리텐션 개선에 쓴다.

계층 분리: 데이터(Firestore) 전담. Discord 포맷팅은 run/views/churn_survey_view.py.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from run.core import config

CHURN_COLLECTION = "churn_feedback"

# 설문 사유 (value, label) — 카미봇 검증 항목을 봇 특성에 맞게
CHURN_REASONS = [
    ("not_working", "봇이 제대로 작동하지 않아요"),
    ("no_feature", "원하는 기능이 없어요"),
    ("too_complex", "너무 복잡하거나 사용법을 모르겠어요"),
    ("not_needed", "더 이상 필요하지 않아요"),
    ("etc", "기타"),
]
_REASON_LABELS = {value: label for value, label in CHURN_REASONS}


def save_churn_feedback(
    *,
    guild_id,
    guild_name: Optional[str] = None,
    owner_id=None,
    reasons=None,
    extra_text: Optional[str] = None,
    member_count: Optional[int] = None,
    installed_days: Optional[int] = None,
) -> bool:
    """이탈 사유를 Firestore churn_feedback 에 저장.

    Args:
        reasons: CHURN_REASONS 의 value 리스트 (예: ["no_feature", "etc"]).
    """
    fs = config.get_firestore_client()
    if not fs:
        return False
    try:
        reason_values = list(reasons or [])
        doc = {
            "guild_id": str(guild_id),
            "guild_name": guild_name,
            "owner_id": str(owner_id) if owner_id else None,
            "reasons": reason_values,
            "reason_labels": [_REASON_LABELS.get(r, r) for r in reason_values],
            "extra_text": extra_text,
            "member_count": member_count,
            "installed_days": installed_days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        fs.collection(CHURN_COLLECTION).add(doc)
        return True
    except Exception as e:
        print(f"[경고] 이탈 사유 저장 실패: {e}", flush=True)
        return False
