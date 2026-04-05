"""
대화 메모리 (수정사항 저장)

사용자가 대화 중 봇의 잘못된 답변을 수정하면 GCS에 저장.
다음 대화 시 시스템 프롬프트에 반영되어 같은 실수를 반복하지 않음.

저장 위치: GCS {BUCKET}/chat_memory.json
형식: {"corrections": ["알렉스는 남자 실험체", "에이든은 망치를 씀", ...]}
"""

import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

GCS_MEMORY_KEY = "chat_memory.json"
MAX_CORRECTIONS = 50

# 메모리 캐시
_memory_cache: Optional[dict] = None

# 수정 감지 패턴
CORRECTION_PATTERNS = [
    # "X는 남자야/여자야/남자임/여자임"
    re.compile(r".+(?:는|은)\s*(?:남자|여자|남캐|여캐)(?:야|임|이야|인데|거든|잖아)"),
    # "아니야/아닌데/틀렸어 + 내용"
    re.compile(r"^(?:아니야|아닌데|틀렸어|아니거든)[,.]?\s*.+"),
    # "X가 아니라 Y야"
    re.compile(r".+(?:가|이)\s*아니라\s*.+(?:야|임|이야)"),
    # "X 안 써/안 씀/안 쓰거든"
    re.compile(r".+(?:안|못)\s*(?:써|씀|쓰거든|쓰는데|쓴다고|함|해|하거든)"),
    # "X 쓰는 거야/쓰는 거임"
    re.compile(r".+(?:쓰는|하는|쓰거든|하거든)\s*(?:거야|거임|건데)"),
    # "기억해/알아둬/외워"
    re.compile(r".+(?:기억해|알아둬|외워|잊지마|기억하고)"),
]


def _get_memory() -> dict:
    """GCS에서 메모리 로드 (캐시 사용)"""
    global _memory_cache
    if _memory_cache is not None:
        return _memory_cache

    try:
        from run.core.config import get_gcs_client, GCS_BUCKET
        client = get_gcs_client()
        if client:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_MEMORY_KEY)
            if blob.exists():
                data = json.loads(blob.download_as_text())
                _memory_cache = data
                return data
    except Exception as e:
        logger.warning("메모리 로드 실패: %s", e)

    _memory_cache = {"corrections": []}
    return _memory_cache


def _save_memory(memory: dict):
    """GCS에 메모리 저장"""
    global _memory_cache
    try:
        from run.core.config import get_gcs_client, GCS_BUCKET
        client = get_gcs_client()
        if client:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_MEMORY_KEY)
            blob.upload_from_string(json.dumps(memory, ensure_ascii=False, indent=2))
            _memory_cache = memory
            print(f"[메모리] 저장 완료 ({len(memory.get('corrections', []))}개)", flush=True)
    except Exception as e:
        logger.error("메모리 저장 실패: %s", e)


def detect_correction(message: str) -> bool:
    """메시지가 수정/교정 패턴인지 감지"""
    for pattern in CORRECTION_PATTERNS:
        if pattern.search(message):
            return True
    return False


def add_correction(text: str):
    """수정사항 추가"""
    memory = _get_memory()
    corrections = memory.get("corrections", [])

    # 중복 방지
    if text in corrections:
        return

    corrections.append(text)
    # 최대 개수 제한
    if len(corrections) > MAX_CORRECTIONS:
        corrections = corrections[-MAX_CORRECTIONS:]

    memory["corrections"] = corrections
    _save_memory(memory)


def get_corrections_prompt() -> str:
    """시스템 프롬프트에 추가할 수정사항 텍스트"""
    memory = _get_memory()
    corrections = memory.get("corrections", [])
    if not corrections:
        return ""
    items = "\n".join(f"- {c}" for c in corrections)
    return f"\n\n[사용자가 알려준 정보 - 반드시 지켜]\n{items}"


def clear_corrections():
    """수정사항 전체 초기화"""
    _save_memory({"corrections": []})
