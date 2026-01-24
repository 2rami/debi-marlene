"""
오디오 유틸리티 함수

오디오 파일 믹싱, 이어붙이기 등 유틸리티 기능을 제공합니다.
"""

import numpy as np
import soundfile as sf
from typing import List


def mix_audio_files(audio_paths: List[str], output_path: str) -> str:
    """
    여러 오디오 파일을 믹싱합니다.

    Args:
        audio_paths: 믹싱할 오디오 파일 경로 목록
        output_path: 출력 파일 경로

    Returns:
        생성된 오디오 파일 경로
    """
    if not audio_paths:
        raise ValueError("믹싱할 오디오 파일이 없습니다")

    # 첫 번째 파일 로드
    mixed_audio, sample_rate = sf.read(audio_paths[0])

    # 나머지 파일들 믹싱
    for path in audio_paths[1:]:
        audio, sr = sf.read(path)

        # 샘플레이트가 다르면 스킵 (또는 리샘플링 필요)
        if sr != sample_rate:
            continue

        # 길이 맞추기
        if len(audio) > len(mixed_audio):
            mixed_audio = np.pad(mixed_audio, (0, len(audio) - len(mixed_audio)))
        elif len(audio) < len(mixed_audio):
            audio = np.pad(audio, (0, len(mixed_audio) - len(audio)))

        # 믹싱 (평균)
        mixed_audio = (mixed_audio + audio) / 2

    # 클리핑 방지
    mixed_audio = np.clip(mixed_audio, -1.0, 1.0)

    sf.write(output_path, mixed_audio, sample_rate)
    return output_path


def concatenate_audio_files(audio_paths: List[str], output_path: str) -> str:
    """
    여러 오디오 파일을 이어붙입니다.

    Args:
        audio_paths: 이어붙일 오디오 파일 경로 목록
        output_path: 출력 파일 경로

    Returns:
        생성된 오디오 파일 경로
    """
    if not audio_paths:
        raise ValueError("이어붙일 오디오 파일이 없습니다")

    audio_segments = []
    sample_rate = None

    for path in audio_paths:
        audio, sr = sf.read(path)

        if sample_rate is None:
            sample_rate = sr
        elif sr != sample_rate:
            # 샘플레이트가 다르면 스킵
            continue

        audio_segments.append(audio)

    # 이어붙이기
    concatenated = np.concatenate(audio_segments)

    sf.write(output_path, concatenated, sample_rate)
    return output_path
