"""
Edge TTS 클라이언트

Microsoft Edge TTS API를 직접 호출합니다.
외부 서버 불필요, GPU 불필요. 빠름.
"""

import os
import hashlib
import logging
import edge_tts

logger = logging.getLogger(__name__)

VOICES = {
    "debi": "ko-KR-SunHiNeural",
    "marlene": "ko-KR-InJoonNeural",
}


class EdgeTTSClient:

    def __init__(self):
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        os.makedirs(self.temp_dir, exist_ok=True)

    async def initialize(self):
        self.is_initialized = True
        logger.info("Edge TTS 클라이언트 초기화 완료")

    async def text_to_speech(
        self,
        text: str,
        speaker: str = "debi",
        language: str = "ko",
        output_path=None,
        max_retries: int = 2,
        guild_name=None,
        channel_name=None,
        user_name=None,
    ) -> str:
        if len(text) > 500:
            text = text[:500]

        voice = VOICES.get(speaker, VOICES["debi"])

        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"edge_{speaker}_{text_hash}.mp3")

        # 동일 텍스트 캐시: 이미 생성된 파일이 있으면 스킵
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path

        comm = edge_tts.Communicate(text, voice)
        await comm.save(output_path)

        return output_path

    def cleanup_temp_files(self):
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith("edge_") and file.endswith(".mp3"):
                    os.remove(os.path.join(self.temp_dir, file))
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    def list_speakers(self):
        return list(VOICES.keys())
