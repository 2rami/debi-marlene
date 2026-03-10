"""
오디오 유틸리티 함수

오디오 파일 믹싱, 이어붙이기, PCM 변환 등 유틸리티 기능을 제공합니다.
"""

import asyncio
import logging
import os
import struct
import subprocess
from typing import List

logger = logging.getLogger(__name__)

# FFmpeg 경로
_FFMPEG_PATH = None


def _get_ffmpeg():
    global _FFMPEG_PATH
    if _FFMPEG_PATH is None:
        import glob as globmod
        import platform
        if platform.system() == "Windows":
            candidates = globmod.glob("C:/ffmpeg*/bin/ffmpeg.exe") + ["ffmpeg"]
        else:
            candidates = ["/usr/bin/ffmpeg", "ffmpeg"]
        for p in candidates:
            if os.path.exists(p):
                _FFMPEG_PATH = p
                break
        if _FFMPEG_PATH is None:
            _FFMPEG_PATH = "ffmpeg"
    return _FFMPEG_PATH


async def convert_to_discord_pcm(audio_path: str) -> str:
    """
    오디오 파일을 Discord PCM 포맷으로 변환합니다.
    (48kHz, stereo, 16-bit signed LE)

    이미 .pcm 파일이면 그대로 반환합니다.
    변환된 파일은 .pcm 확장자로 저장됩니다.
    """
    if audio_path.endswith('.pcm'):
        return audio_path

    pcm_path = os.path.splitext(audio_path)[0] + '.pcm'

    # 캐시: 이미 변환된 PCM이 있으면 재사용
    if os.path.exists(pcm_path) and os.path.getsize(pcm_path) > 0:
        return pcm_path

    ffmpeg = _get_ffmpeg()
    cmd = [
        ffmpeg, "-y",
        "-nostdin",
        "-probesize", "32",
        "-analyzeduration", "0",
        "-i", audio_path,
        "-f", "s16le",
        "-ar", "48000",
        "-ac", "2",
        pcm_path
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    await proc.wait()

    if proc.returncode != 0 or not os.path.exists(pcm_path):
        logger.error(f"PCM 변환 실패: {audio_path}")
        return audio_path  # 실패 시 원본 반환 (FFmpeg 재생으로 폴백)

    # 앞쪽 무음 제거 (stereo 16-bit: 4 bytes per frame)
    _trim_leading_silence_file(pcm_path, frame_size=4, threshold=500)

    return pcm_path


def _trim_leading_silence_file(pcm_path: str, frame_size: int = 4, threshold: int = 500):
    """PCM 파일의 앞쪽 무음을 제거합니다. (in-place)"""
    with open(pcm_path, 'rb') as f:
        data = f.read()

    for i in range(0, len(data) - frame_size, frame_size):
        # stereo: left(2 bytes) + right(2 bytes)
        left = abs(struct.unpack_from('<h', data, i)[0])
        right = abs(struct.unpack_from('<h', data, i + 2)[0])
        if left > threshold or right > threshold:
            if i > 0:
                with open(pcm_path, 'wb') as f:
                    f.write(data[i:])
            return


def mix_audio_files(audio_paths: List[str], output_path: str) -> str:
    import numpy as np
    import soundfile as sf

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
    import numpy as np
    import soundfile as sf

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
