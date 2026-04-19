"""대화 메모리 (수정사항 저장) — 서버별 분리 저장.

사용자가 대화 중 봇의 잘못된 답변을 수정하면 GCS에 저장.
다음 대화 시 시스템 프롬프트에 반영되어 같은 실수를 반복하지 않음.

저장 위치: GCS {BUCKET}/chat_memory/{guild_id}.json
  - guild_id가 있으면 해당 서버 전용 메모리
  - DM이면 {BUCKET}/chat_memory/dm.json
  - 같은 봇이 서로 다른 서버에서 다른 정보를 학습해도 충돌 없음
"""

import json
import logging
import re
from typing import Optional, Dict, Union

logger = logging.getLogger(__name__)

MAX_CORRECTIONS = 50

# guild별 메모리 캐시: {"12345": {"corrections": [...]}, "dm": {...}}
_memory_cache: Dict[str, dict] = {}

# 수정 감지 패턴 (guild-agnostic, 전역 유지)
CORRECTION_PATTERNS = [
    re.compile(r".+(?:는|은)\s*(?:남자|여자|남캐|여캐)(?:야|임|이야|인데|거든|잖아)"),
    re.compile(r"^(?:아니야|아닌데|틀렸어|아니거든)[,.]?\s*.+"),
    re.compile(r".+(?:가|이)\s*아니라\s*.+(?:야|임|이야)"),
    re.compile(r".+(?:안|못)\s*(?:써|씀|쓰거든|쓰는데|쓴다고|함|해|하거든)"),
    re.compile(r".+(?:쓰는|하는|쓰거든|하거든)\s*(?:거야|거임|건데)"),
    re.compile(r".+(?:기억해|알아둬|외워|잊지마|기억하고)"),
]


def _scope_key(guild_id: Optional[Union[int, str]]) -> str:
    """guild_id를 캐시/GCS 경로용 스코프 문자열로 변환."""
    if guild_id is None or guild_id == "":
        return "dm"
    return str(guild_id)


def _gcs_blob_key(scope: str) -> str:
    return f"chat_memory/{scope}.json"


def _get_memory(guild_id: Optional[Union[int, str]] = None) -> dict:
    """해당 guild의 메모리 로드 (없으면 빈 상태 반환, 캐시 사용)"""
    scope = _scope_key(guild_id)
    if scope in _memory_cache:
        return _memory_cache[scope]

    try:
        from run.core.config import get_gcs_client, GCS_BUCKET
        client = get_gcs_client()
        if client:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(_gcs_blob_key(scope))
            if blob.exists():
                data = json.loads(blob.download_as_text())
                _memory_cache[scope] = data
                return data
    except Exception as e:
        logger.warning("메모리 로드 실패 (scope=%s): %s", scope, e)

    _memory_cache[scope] = {"corrections": []}
    return _memory_cache[scope]


def _save_memory(memory: dict, guild_id: Optional[Union[int, str]] = None):
    """해당 guild의 메모리 저장."""
    scope = _scope_key(guild_id)
    try:
        from run.core.config import get_gcs_client, GCS_BUCKET
        client = get_gcs_client()
        if client:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(_gcs_blob_key(scope))
            blob.upload_from_string(json.dumps(memory, ensure_ascii=False, indent=2))
            _memory_cache[scope] = memory
            print(
                f"[메모리] 저장 완료 [scope={scope}] ({len(memory.get('corrections', []))}개)",
                flush=True,
            )
    except Exception as e:
        logger.error("메모리 저장 실패 (scope=%s): %s", scope, e)


def detect_correction(message: str) -> bool:
    """메시지가 수정/교정 패턴인지 감지 (guild-agnostic)."""
    for pattern in CORRECTION_PATTERNS:
        if pattern.search(message):
            return True
    return False


def add_correction(text: str, guild_id: Optional[Union[int, str]] = None):
    """수정사항 추가 (해당 guild에만 반영)."""
    memory = _get_memory(guild_id)
    corrections = memory.get("corrections", [])

    if text in corrections:
        return

    corrections.append(text)
    if len(corrections) > MAX_CORRECTIONS:
        corrections = corrections[-MAX_CORRECTIONS:]

    memory["corrections"] = corrections
    _save_memory(memory, guild_id)


def get_corrections_prompt(guild_id: Optional[Union[int, str]] = None) -> str:
    """해당 guild의 수정사항을 시스템 프롬프트 추가 텍스트로 반환."""
    memory = _get_memory(guild_id)
    corrections = memory.get("corrections", [])
    if not corrections:
        return ""
    items = "\n".join(f"- {c}" for c in corrections)
    return f"\n\n[사용자가 알려준 정보 - 반드시 지켜]\n{items}"


def clear_corrections(guild_id: Optional[Union[int, str]] = None):
    """해당 guild의 수정사항 전체 초기화."""
    _save_memory({"corrections": []}, guild_id)
