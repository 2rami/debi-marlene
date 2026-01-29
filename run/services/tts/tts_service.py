"""
TTS 서비스: Qwen3-TTS 사용

데비&마를렌 음성으로 TTS를 제공합니다.

엔진 종류:
- modal: Modal Serverless TTS (권장, Flash Attention)
- qwen3_api: Qwen3-TTS FastAPI 서버 (로컬)
- qwen3: Qwen3-TTS 로컬 모델
"""

import os
from typing import Optional
import logging

from .text_preprocessor import preprocess_text_for_tts

logger = logging.getLogger(__name__)

# 환경변수로 TTS 엔진 선택 (modal / qwen3_api / qwen3)
TTS_ENGINE = os.environ.get("TTS_ENGINE", "modal")


class TTSService:
    """
    TTS 엔진 클래스

    Qwen3-TTS를 사용합니다.
    환경변수 TTS_ENGINE으로 선택 (qwen3_api / qwen3)
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        config_path: Optional[str] = None,
        default_model: str = "ko",
        speaker: Optional[str] = None,
        engine: Optional[str] = None
    ):
        """
        TTS 서비스 초기화

        Args:
            model_path: 모델 경로 (사용 안 함, 하위 호환용)
            config_path: 설정 파일 경로 (사용 안 함, 하위 호환용)
            default_model: 언어 코드 (기본값: 'ko')
            speaker: 화자 이름 (debi, marlene)
            engine: TTS 엔진 (qwen3_api / qwen3)
        """
        self.language = default_model
        self.temp_dir = "/tmp/tts_audio"
        self.speaker = speaker or "debi"
        self.engine = engine or TTS_ENGINE
        self.tts_backend = None

        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"TTS 서비스 초기화 (엔진: {self.engine}, 화자: {self.speaker})")

    async def initialize(self):
        """TTS 엔진을 비동기로 초기화합니다."""
        if self.tts_backend is not None:
            return

        if self.engine == "modal":
            # Modal Serverless TTS (권장)
            from .modal_tts_client import ModalTTSClient
            self.tts_backend = ModalTTSClient()
            await self.tts_backend.initialize()
            logger.info("Modal TTS 클라이언트 초기화 완료")
        elif self.engine == "qwen3_api":
            # 로컬 API 서버 사용
            from .qwen3_tts_client import Qwen3TTSClient
            self.tts_backend = Qwen3TTSClient()
            await self.tts_backend.initialize()
            logger.info("Qwen3-TTS API 클라이언트 초기화 완료")
        else:
            # 로컬 모델 직접 로드
            from .qwen3_tts_service import Qwen3TTSService
            self.tts_backend = Qwen3TTSService()
            await self.tts_backend.initialize()
            logger.info("Qwen3-TTS 로컬 모델 초기화 완료")

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
        if not self.tts_backend:
            raise RuntimeError("TTS 서비스가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")

        # 텍스트 전처리 (ㅋㅋ → 크크, ㄱㄱ → 고고 등)
        processed_text = preprocess_text_for_tts(text)
        if processed_text != text:
            logger.info(f"텍스트 전처리: '{text}' -> '{processed_text}'")

        return await self.tts_backend.text_to_speech(
            text=processed_text,
            speaker=self.speaker,
            language=self.language,
            output_path=output_path
        )

    def cleanup_temp_files(self):
        """임시 음성 파일들을 정리합니다."""
        try:
            if self.tts_backend:
                self.tts_backend.cleanup_temp_files()

            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            logger.info("TTS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")
