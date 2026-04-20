"""페르소나별 응답 파싱 유틸.

기존 Managed Agent는 system prompt에 "데비: X\n마를렌: Y" 형식이 박혀 있어
한 번 호출로 두 페르소나 대사를 항상 같이 생성한다.

솔로봇(BOT_IDENTITY='debi' or 'marlene')은 agent를 공유하되
이 유틸로 자기 페르소나 대사만 추출해 전송한다.
unified 봇은 원본 응답을 그대로 사용.
"""

import re

PERSONA_LABELS = {
    "debi": "데비",
    "marlene": "마를렌",
}

_SPLIT_PATTERN = re.compile(r"^(데비|마를렌)\s*:\s*", re.MULTILINE)


def extract_persona_response(full_response: str, identity: str) -> str:
    """identity에 해당하는 대사만 추출. unified/매칭 실패 시 원본 반환."""
    if not full_response:
        return full_response

    label = PERSONA_LABELS.get(identity)
    if not label:
        return full_response

    # prefix 위치로 분할 → 짝을 이룬 (label, text) 추출
    parts = _SPLIT_PATTERN.split(full_response)
    # split 결과: [prefix_before, label1, text1, label2, text2, ...]
    if len(parts) < 3:
        return full_response

    collected = []
    for i in range(1, len(parts) - 1, 2):
        spk, text = parts[i], parts[i + 1]
        if spk == label:
            collected.append(text.strip())

    if not collected:
        return full_response

    return "\n".join(collected)
