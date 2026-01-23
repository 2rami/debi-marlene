"""
TTS 서비스: CosyVoice3 파인튜닝 모델 사용

데비&마를렌 음성으로 TTS를 제공합니다.
로컬 GPU 환경에서만 작동합니다.
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """
    TTS 엔진 클래스

    CosyVoice3 파인튜닝 모델을 사용합니다.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        config_path: Optional[str] = None,
        default_model: str = "ko",
        speaker: Optional[str] = None
    ):
        """
        TTS 서비스 초기화

        Args:
            model_path: 모델 경로 (사용 안 함, 하위 호환용)
            config_path: 설정 파일 경로 (사용 안 함, 하위 호환용)
            default_model: 언어 코드 (기본값: 'ko')
            speaker: 화자 이름 (debi, marlene)
        """
        self.language = default_model
        self.temp_dir = "/tmp/tts_audio"
        self.speaker = speaker or "debi"
        self.cosyvoice_service = None

        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"TTS 서비스 초기화 (CosyVoice3, 화자: {self.speaker})")

    async def initialize(self):
        """CosyVoice3 엔진을 비동기로 초기화합니다."""
        if self.cosyvoice_service is None:
            from .cosyvoice_service import CosyVoiceService

            self.cosyvoice_service = CosyVoiceService()
            await self.cosyvoice_service.initialize()
            logger.info("CosyVoice3 초기화 완료")

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
        if not self.cosyvoice_service:
            raise RuntimeError("CosyVoice3 서비스가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")

        return await self.cosyvoice_service.text_to_speech(
            text=text,
            speaker=self.speaker,
            language=self.language,
            output_path=output_path
        )

    def cleanup_temp_files(self):
        """임시 음성 파일들을 정리합니다."""
        try:
            if self.cosyvoice_service:
                self.cosyvoice_service.cleanup_temp_files()

            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            logger.info("TTS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")
