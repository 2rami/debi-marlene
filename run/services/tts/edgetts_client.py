"""
edge-tts 전용 TTS 클라이언트 (RVC 없이)

Microsoft edge-tts로 한국어 음성을 직접 생성합니다.
GPU 불필요, 로컬에서 바로 실행.
"""

import os
import hashlib
import logging
import subprocess
import tempfile
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

EDGE_TTS_VOICE = "ko-KR-SunHiNeural"


class EdgeTTSClient:
    def __init__(self):
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        os.makedirs(self.temp_dir, exist_ok=True)

    async def initialize(self):
        self.is_initialized = True
        logger.info(f"EdgeTTS 클라이언트 초기화 (voice: {EDGE_TTS_VOICE})")

    async def text_to_speech(
        self,
        text: str,
        speaker: str = "debi",
        language: str = "ko",
        output_path: Optional[str] = None,
        max_retries: int = 2,
        guild_name: Optional[str] = None,
        channel_name: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> str:
        from edge_tts import Communicate

        if len(text) > 500:
            text = text[:500]

        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"edgetts_{text_hash}.mp3")

        communicate = Communicate(text=text, voice=EDGE_TTS_VOICE)
        await communicate.save(output_path)
        logger.info(f"EdgeTTS 생성: {output_path}")
        return output_path

    async def warm_up(self):
        pass

    def cleanup_temp_files(self):
        try:
            for f in os.listdir(self.temp_dir):
                if f.startswith("edgetts_") and f.endswith(".wav"):
                    os.remove(os.path.join(self.temp_dir, f))
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    async def close(self):
        pass

    def list_speakers(self):
        return ["debi", "marlene"]
