"""이탈(서버 추방) 사유 수집 — Firestore churn_feedback 컬렉션.

봇이 서버에서 제거될 때 owner 에게 DM 투표(Discord Poll)를 보내 사유를 모은다.
잠든 서버 / 이탈 원인을 데이터로 파악해 리텐션 개선에 쓴다.

흐름:
  1. on_guild_remove 직후 save_churn_pending() 으로 pending 문서 생성(status="sent",
     poll_message_id 포함).
  2. owner 가 DM Poll 에 투표하면 on_raw_poll_vote_add 이벤트가 record_poll_vote() 호출.
     answer_id 로 사유를 매핑해 해당 문서를 갱신(status="answered").

Poll 은 Discord 가 서버사이드로 관리 → 컴포넌트 인터랙션이 아니므로 봇 재시작과
무관하고 "상호작용 실패"가 발생하지 않는다.

계층 분리: 데이터(Firestore) 전담. Discord 포맷팅/Poll 구성은
run/views/churn_survey_view.py.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from google.cloud.firestore_v1.base_query import FieldFilter

from run.core import config

CHURN_COLLECTION = "churn_feedback"

# 설문 사유 (value, label) — 카미봇 검증 항목을 봇 특성에 맞게.
# 순서가 곧 Poll answer 순서. answer_id(1-based) = 인덱스 + 1.
CHURN_REASONS = [
    ("not_working", "봇이 제대로 작동하지 않아요"),
    ("no_feature", "원하는 기능이 없어요"),
    ("too_complex", "너무 복잡하거나 사용법을 모르겠어요"),
    ("not_needed", "더 이상 필요하지 않아요"),
    ("etc", "기타"),
]
_REASON_LABELS = {value: label for value, label in CHURN_REASONS}


def save_churn_pending(
    *,
    guild_id,
    guild_name: Optional[str] = None,
    owner_id=None,
    member_count: Optional[int] = None,
    installed_days: Optional[int] = None,
    poll_message_id=None,
) -> bool:
    """추방 직후 pending 설문 문서 생성(status="sent").

    poll_message_id 로 나중에 투표 이벤트(on_raw_poll_vote_add)와 매칭한다.
    """
    fs = config.get_firestore_client()
    if not fs:
        return False
    try:
        doc = {
            "guild_id": str(guild_id),
            "guild_name": guild_name,
            "owner_id": str(owner_id) if owner_id else None,
            "reasons": [],
            "reason_labels": [],
            "member_count": member_count,
            "installed_days": installed_days,
            "poll_message_id": str(poll_message_id) if poll_message_id else None,
            "status": "sent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        fs.collection(CHURN_COLLECTION).add(doc)
        return True
    except Exception as e:
        print(f"[경고] 이탈 pending 저장 실패: {e}", flush=True)
        return False


def record_poll_vote(*, message_id, answer_id) -> bool:
    """DM Poll 투표 1건을 해당 pending 문서에 기록.

    answer_id 는 1-based(add_answer 순서). CHURN_REASONS[answer_id-1] 로 매핑.
    multiple=True 라 한 명이 여러 번 호출될 수 있어 reasons 를 합집합으로 누적한다.
    poll_message_id 단일 필드 인덱스만 사용(복합 인덱스 회피).
    """
    idx = (answer_id or 0) - 1
    if idx < 0 or idx >= len(CHURN_REASONS):
        return False
    value = CHURN_REASONS[idx][0]

    fs = config.get_firestore_client()
    if not fs:
        return False
    try:
        now = datetime.now(timezone.utc).isoformat()
        col = fs.collection(CHURN_COLLECTION)
        docs = list(col.where(filter=FieldFilter("poll_message_id", "==", str(message_id))).stream())
        if not docs:
            return False
        for d in docs:
            data = d.to_dict() or {}
            reasons = set(data.get("reasons") or [])
            reasons.add(value)
            ordered = [v for v, _ in CHURN_REASONS if v in reasons]
            d.reference.update({
                "reasons": ordered,
                "reason_labels": [_REASON_LABELS[v] for v in ordered],
                "status": "answered",
                "answered_at": now,
            })
        return True
    except Exception as e:
        print(f"[경고] 이탈 투표 기록 실패: {e}", flush=True)
        return False
