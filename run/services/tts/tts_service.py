"""
TTS 서비스: 텍스트를 음성으로 변환하는 엔진

GPT-SoVITS를 사용하여 데비&마를렌 목소리로 TTS를 제공합니다.
"""

import os
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """
    TTS 엔진 클래스

    GPT-SoVITS (학습된 데비&마를렌 모델)만 사용합니다.
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
            default_model: 언어 코드 (기본값: 'ko' - 한국어)
            speaker: 화자 이름 (debi, marlene)
        """
        self.language = default_model
        self.temp_dir = "/tmp/tts_audio"
        self.speaker = speaker or "debi"
        self.gpt_sovits_service = None

        # 임시 파일 저장 폴더 생성
        os.makedirs(self.temp_dir, exist_ok=True)

        # GPT-SoVITS 모델 경로
        self.gpt_model_path = "assets/models/debimarlene_gptsovits/gpt_model.ckpt"
        self.sovits_model_path = "assets/models/debimarlene_gptsovits/sovits_model.pth"

        # API URL (환경 변수에서 가져오기)
        self.api_url = os.getenv("TTS_API_URL", "http://localhost:9880")

        logger.info(f"TTS 서비스 초기화 (GPT-SoVITS 전용, 화자: {self.speaker})")

    async def initialize(self):
        """
        TTS 엔진을 비동기로 초기화합니다.
        """
        if self.gpt_sovits_service is None:
            from .gpt_sovits_service import GPTSoVITSService

            self.gpt_sovits_service = GPTSoVITSService(
                gpt_model_path=self.gpt_model_path,
                sovits_model_path=self.sovits_model_path,
                api_url=self.api_url
            )
            await self.gpt_sovits_service.initialize()
            logger.info("GPT-SoVITS 초기화 완료")

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
        if not self.gpt_sovits_service:
            raise RuntimeError("GPT-SoVITS 서비스가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")

        return await self.gpt_sovits_service.text_to_speech(
            text=text,
            speaker=self.speaker,
            language=self.language,
            output_path=output_path
        )

    def cleanup_temp_files(self):
        """임시 음성 파일들을 정리합니다."""
        try:
            if self.gpt_sovits_service:
                self.gpt_sovits_service.cleanup_temp_files()

            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            logger.info("TTS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")
