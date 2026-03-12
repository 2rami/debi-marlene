"""
TTS 텍스트 전처리

한글 자음 조합 인터넷 용어, 이모티콘 등을 읽을 수 있는 형태로 변환합니다.
효과음 감지 기능도 포함합니다.
"""

import re
import os
import csv
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def number_to_korean(num: int) -> str:
    """숫자를 한글로 변환"""
    if num == 0:
        return "영"

    units = ["", "만", "억", "조"]
    digits = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
    positions = ["", "십", "백", "천"]

    if num < 0:
        return "마이너스 " + number_to_korean(-num)

    result = []
    unit_idx = 0

    while num > 0:
        part = num % 10000
        if part > 0:
            part_str = ""
            for i, pos in enumerate(positions):
                digit = part % 10
                if digit > 0:
                    if i > 0 and digit == 1:
                        part_str = pos + part_str
                    else:
                        part_str = digits[digit] + pos + part_str
                part //= 10
            result.append(part_str + units[unit_idx])
        num //= 10000
        unit_idx += 1

    return "".join(reversed(result))


def convert_numbers_to_korean(text: str) -> str:
    """텍스트 내 숫자를 한글로 변환"""
    def replace_number(match):
        num_str = match.group()
        try:
            num = int(num_str)
            return number_to_korean(num)
        except:
            return num_str

    # 숫자 패턴 찾아서 변환 (연속된 숫자만)
    return re.sub(r'\d+', replace_number, text)

# 자음 조합 인터넷 용어 (순서 중요: 긴 패턴 먼저)
JAMO_SLANG = {
    # 3글자 이상
    "ㅋㅋㅋ": "크크크",
    "ㅎㅎㅎ": "흐흐흐",
    "ㄱㄱㄱ": "고고고",
    "ㅇㅇㅇ": "응응응",
    # 2글자 조합
    "ㄱㄱ": "고고",
    "ㅎㅎ": "흐흐",
    "ㅋㅋ": "크크",
    "ㅅㅅ": "샷샷",
    "ㄲㅂ": "까비",
    "ㅇㅎ": "아하",
    "ㅇㅇ": "응응",
    "ㄴㄴ": "노노",
    "ㅈㅈ": "지지",
    "ㄷㄷ": "덜덜",
    "ㅂㅂ": "바바",
    "ㅊㅊ": "축축",
    "ㅌㅌ": "튀튀",
    "ㄱㅅ": "감사",
    "ㅅㄱ": "수고",
    "ㅈㅅ": "죄송",
    "ㄱㄷ": "기달",
    "ㄱㅊ": "괜찮",
    "ㅇㅋ": "오케이",
    "ㅎㅇ": "하이",
    "ㅂㅇ": "바이",
    "ㅁㅊ": "미친",
    "ㅇㄷ": "어디",
    "ㄹㅇ": "리얼",
    "ㅈㄹ": "지랄",
    "ㄱㅇ": "개이득",
    "ㅁㄹ": "몰라",
    "ㅇㅈ": "인정",
    "ㄴㅈ": "노잼",
    # 단일 자음 (문장 끝에서)
    "ㅋ": "크",
    "ㅎ": "흐",
    "ㅇ": "응",
}

# 모음 반복 패턴
MOUM_PATTERNS = {
    "ㅠㅠ": "유유",
    "ㅜㅜ": "우우",
    "ㅠㅠㅠ": "유유유",
    "ㅜㅜㅜ": "우우우",
}


def preprocess_text_for_tts(text: str) -> str:
    """
    TTS용 텍스트 전처리

    Args:
        text: 원본 텍스트

    Returns:
        TTS가 읽을 수 있는 형태로 변환된 텍스트
    """
    if not text:
        return text

    result = text

    # 1. 모음 패턴 먼저 (긴 것부터)
    for pattern, replacement in sorted(MOUM_PATTERNS.items(), key=lambda x: -len(x[0])):
        result = result.replace(pattern, replacement)

    # 2. 자음 조합 변환 (긴 패턴부터 처리)
    # ㅋㅋㅋㅋ 같은 연속 패턴 처리
    result = re.sub(r"ㅋ{4,}", lambda m: "크" * len(m.group()), result)
    result = re.sub(r"ㅎ{4,}", lambda m: "흐" * len(m.group()), result)
    result = re.sub(r"ㄱ{4,}", lambda m: "고" * len(m.group()), result)
    result = re.sub(r"ㅇ{4,}", lambda m: "응" * len(m.group()), result)

    # 3. 정의된 자음 조합 변환 (긴 것부터)
    for pattern, replacement in sorted(JAMO_SLANG.items(), key=lambda x: -len(x[0])):
        result = result.replace(pattern, replacement)

    # 4. URL 제거 또는 "링크"로 대체
    result = re.sub(r"https?://\S+", "링크", result)

    # 5. 멘션 처리 (<@123456> → "")
    result = re.sub(r"<@!?\d+>", "", result)

    # 6. 채널 멘션 처리 (<#123456> → "")
    result = re.sub(r"<#\d+>", "", result)

    # 7. 역할 멘션 처리 (<@&123456> → "")
    result = re.sub(r"<@&\d+>", "", result)

    # 8. 커스텀 이모지 처리 (<:name:123456> → "")
    result = re.sub(r"<a?:\w+:\d+>", "", result)

    # 9. 숫자를 한글로 변환
    result = convert_numbers_to_korean(result)

    # 10. 연속 공백 정리
    result = re.sub(r"\s+", " ", result).strip()

    return result


# 효과음 트리거 패턴 (정규식)
SFX_PATTERNS = {
    r"ㅋ{6,}": "laugh",  # ㅋㅋㅋㅋㅋㅋ 이상 → 웃음
    r"ㅎ{6,}": "laugh",  # ㅎㅎㅎㅎㅎㅎ 이상 → 웃음
    r"꺄르륵": "laugh",  # 꺄르륵 → 웃음
    r"으악": "die",      # 으악 → 비명
    r"흐앗": "attack",   # 흐앗 → 기합
}

# 게임 대사 → wav 파일 매핑 (metadata.csv에서 로드)
# {speaker: {normalized_text: wav_filename}}
_voice_line_map: Dict[str, Dict[str, str]] = {}
_voice_line_loaded = False

# SFX 디렉토리 (voice.py의 SFX_DIR와 동일한 위치)
_SFX_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sfx")
# metadata.csv 경로
_METADATA_CSV = os.path.join(_SFX_BASE_DIR, "metadata.csv")


def _normalize_for_match(text: str) -> str:
    """매칭용 텍스트 정규화 (띄어쓰기/구두점 제거, 소문자)"""
    return re.sub(r"[\s,\.!?\-~]+", "", text).lower()


def _load_voice_lines():
    """metadata.csv에서 대사 텍스트 → wav 파일 매핑을 로드합니다."""
    global _voice_line_map, _voice_line_loaded

    if _voice_line_loaded:
        return

    _voice_line_loaded = True

    if not os.path.exists(_METADATA_CSV):
        logger.warning(f"대사 metadata.csv 없음: {_METADATA_CSV}")
        return

    count = 0
    with open(_METADATA_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        header = next(reader, None)  # skip header
        if not header:
            return

        for row in reader:
            if len(row) < 3:
                continue
            wav_path, speaker_id, text = row[0], row[1], row[2]

            # wav_path: "wavs/debi_taunt_2_01_01.wav" → "debi_taunt_2_01_01.wav"
            wav_filename = os.path.basename(wav_path)

            speaker = speaker_id.lower().strip()
            normalized = _normalize_for_match(text)
            if not normalized:
                continue

            if speaker not in _voice_line_map:
                _voice_line_map[speaker] = {}
            _voice_line_map[speaker][normalized] = wav_filename
            count += 1

    logger.info(f"대사 매핑 로드 완료: {count}개 ({', '.join(_voice_line_map.keys())})")


def _find_wav_file(speaker: str, wav_filename: str) -> Optional[str]:
    """
    실제 sfx 폴더에서 wav 파일을 찾습니다.
    metadata.csv는 소문자(debi_taunt...), 실제 파일은 대문자(Debi_taunt...)이므로
    대소문자 무시로 매칭합니다.
    """
    sfx_dir = os.path.join(_SFX_BASE_DIR, speaker)
    if not os.path.exists(sfx_dir):
        return None

    wav_lower = wav_filename.lower()

    # 빠른 경로: 파일명 첫글자만 대문자로 시도
    capitalized = wav_filename[0].upper() + wav_filename[1:]
    direct_path = os.path.join(sfx_dir, capitalized)
    if os.path.exists(direct_path):
        return direct_path

    # 폴백: 대소문자 무시 검색
    for f in os.listdir(sfx_dir):
        if f.lower() == wav_lower:
            return os.path.join(sfx_dir, f)

    return None


def match_voice_line(text: str, speaker: str = "debi") -> Optional[str]:
    """
    텍스트가 게임 대사와 정확히 일치하는지 확인합니다.
    띄어쓰기/구두점 무시.

    Args:
        text: 유저가 입력한 텍스트
        speaker: 캐릭터 이름 (debi / marlene / alex)

    Returns:
        매칭된 wav 파일의 절대 경로, 또는 None
    """
    _load_voice_lines()

    normalized = _normalize_for_match(text)
    if not normalized:
        return None

    speaker = speaker.lower()
    speaker_lines = _voice_line_map.get(speaker, {})
    wav_filename = speaker_lines.get(normalized)

    if not wav_filename:
        return None

    wav_path = _find_wav_file(speaker, wav_filename)
    if wav_path:
        logger.info(f"대사 매칭: '{text}' -> {os.path.basename(wav_path)}")
    return wav_path


def extract_segments_with_sfx(text: str) -> List[Dict[str, Any]]:
    """
    텍스트에서 효과음이 필요한 부분을 분리합니다.

    Args:
        text: 원본 텍스트

    Returns:
        세그먼트 리스트. 각 세그먼트는 다음 형식:
        - {"type": "text", "content": "텍스트"}
        - {"type": "sfx", "name": "laugh"}

    예시:
        "안녕 ㅋㅋㅋㅋㅋㅋㅋ 반가워" →
        [
            {"type": "text", "content": "안녕"},
            {"type": "sfx", "name": "laugh"},
            {"type": "text", "content": "반가워"}
        ]
    """
    if not text:
        return []

    segments = []
    remaining = text

    # 모든 효과음 패턴을 합쳐서 찾기
    combined_pattern = "|".join(f"({p})" for p in SFX_PATTERNS.keys())

    while remaining:
        match = re.search(combined_pattern, remaining)

        if not match:
            # 더 이상 효과음 없음 → 남은 텍스트 추가
            cleaned = remaining.strip()
            if cleaned:
                segments.append({"type": "text", "content": cleaned})
            break

        # 효과음 앞의 텍스트
        before = remaining[:match.start()].strip()
        if before:
            segments.append({"type": "text", "content": before})

        # 어떤 효과음인지 확인
        matched_text = match.group()
        sfx_name = None
        for pattern, name in SFX_PATTERNS.items():
            if re.match(pattern, matched_text):
                sfx_name = name
                break

        if sfx_name:
            segments.append({"type": "sfx", "name": sfx_name})

        # 나머지 텍스트로 진행
        remaining = remaining[match.end():]

    return segments


def split_text_for_tts(text: str, max_chars: int = 100, min_chars: int = 3) -> List[str]:
    """
    TTS용 텍스트를 자연스러운 구간으로 분할합니다.

    분할 우선순위: 문장 끝(.!?~) > 쉼표(,) > 공백 > 강제 분할
    """
    if not text or len(text) <= max_chars:
        return [text] if text and text.strip() else []

    chunks = []

    # 1단계: 문장 끝에서 분할
    sentences = re.split(r'(?<=[.!?~])\s*', text)
    sentences = [s for s in sentences if s.strip()]

    for sentence in sentences:
        if len(sentence) <= max_chars:
            chunks.append(sentence)
            continue

        # 2단계: 쉼표에서 분할
        clauses = re.split(r'(?<=,)\s*', sentence)
        clauses = [c for c in clauses if c.strip()]

        for clause in clauses:
            if len(clause) <= max_chars:
                chunks.append(clause)
                continue

            # 3단계: 공백에서 분할
            words = clause.split(' ')
            current = ""
            for word in words:
                if current and len(current) + 1 + len(word) > max_chars:
                    if current.strip():
                        chunks.append(current.strip())
                    current = word
                else:
                    current = current + " " + word if current else word

            if current.strip():
                # 4단계: 강제 분할 (공백 없는 긴 텍스트)
                remaining = current.strip()
                while len(remaining) > max_chars:
                    chunks.append(remaining[:max_chars])
                    remaining = remaining[max_chars:]
                if remaining:
                    chunks.append(remaining)

    # 짧은 청크는 이전 청크에 병합
    merged = []
    for chunk in chunks:
        if merged and len(chunk) < min_chars:
            merged[-1] = merged[-1] + " " + chunk
        else:
            merged.append(chunk)

    return [c for c in merged if c.strip()]


def has_sfx_triggers(text: str) -> bool:
    """텍스트에 효과음 트리거가 있는지 확인합니다."""
    combined_pattern = "|".join(SFX_PATTERNS.keys())
    return bool(re.search(combined_pattern, text))
