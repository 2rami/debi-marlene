"""
TTS 서비스: 텍스트를 음성으로 변환하는 엔진

Google TTS (gTTS)를 사용하여 텍스트를 음성으로 변환합니다.
"""

import os
import asyncio
from typing import Optional
from gtts import gTTS
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """
    TTS 엔진 클래스

    Google TTS를 사용하여 텍스트를 음성으로 변환합니다.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        config_path: Optional[str] = None,
        default_model: str = "ko"  # 한국어
    ):
        """
        TTS 서비스 초기화

        Args:
            model_path: 사용하지 않음 (호환성 유지)
            config_path: 사용하지 않음 (호환성 유지)
            default_model: 언어 코드 (기본값: 'ko' - 한국어)
        """
        self.language = default_model
        self.temp_dir = "/tmp/tts_audio"

        # 임시 파일 저장 폴더 생성
        os.makedirs(self.temp_dir, exist_ok=True)

        logger.info(f"gTTS 서비스 초기화 완료 (언어: {self.language})")

    async def initialize(self):
        """
        TTS 엔진을 비동기로 초기화합니다.

        gTTS는 초기화가 필요 없으므로 즉시 완료됩니다.
        """
        logger.info("gTTS 초기화 완료")

    async def text_to_speech(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환합니다.

        Args:
            text: 변환할 텍스트
            output_path: 저장할 파일 경로 (없으면 자동 생성)

        Returns:
            생성된 음성 파일의 경로
        """
        # 출력 파일 경로 생성
        if output_path is None:
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"tts_{text_hash}.mp3")

        try:
            # TTS 변환 실행 (blocking이므로 executor 사용)
            loop = asyncio.get_event_loop()

            def generate_tts():
                tts = gTTS(text=text, lang=self.language, slow=False)
                tts.save(output_path)

            await loop.run_in_executor(None, generate_tts)

            logger.info(f"TTS 변환 완료: {text[:20]}... -> {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"TTS 변환 실패: {e}")
            raise

    def cleanup_temp_files(self):
        """임시 음성 파일들을 정리합니다."""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            logger.info("TTS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")
