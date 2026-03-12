"""
TTS 서비스

데비&마를렌 음성으로 TTS를 제공합니다.

엔진 종류:
- cosyvoice3: CosyVoice3 파인튜닝 모델 (Modal Serverless, 24kHz)
- fish: Fish-Speech OpenAudio S1-mini (빠름 + 고품질)
- modal: Modal Serverless Qwen3-TTS (Flash Attention)
- sovits: GPT-SoVITS v2Pro 파인튜닝 모델 (Modal Serverless)
- qwen3_api: Qwen3-TTS FastAPI 서버 (로컬)
- qwen3: Qwen3-TTS 로컬 모델
"""

import os
import hashlib
from typing import Optional
import logging

from .text_preprocessor import preprocess_text_for_tts
from .audio_utils import convert_to_discord_pcm

logger = logging.getLogger(__name__)

# TTS 캐시 디렉토리 (서버 재시작해도 유지)
TTS_CACHE_DIR = os.environ.get("TTS_CACHE_DIR", "/tmp/tts_cache")
# 캐시 최대 개수 (초과 시 오래된 것부터 삭제)
TTS_CACHE_MAX = int(os.environ.get("TTS_CACHE_MAX", "2000"))

# 환경변수로 TTS 엔진 선택 (modal / qwen3_api / qwen3)
TTS_ENGINE = os.environ.get("TTS_ENGINE", "modal")


class TTSService:
    """
    TTS 엔진 클래스

    Qwen3-TTS를 사용합니다.
    환경변수 TTS_ENGINE으로 선택 (fish / modal / sovits / qwen3_api / qwen3)
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
            engine: TTS 엔진 (fish / modal / sovits / qwen3_api / qwen3)
        """
        self.language = default_model
        self.temp_dir = "/tmp/tts_audio"
        self.cache_dir = TTS_CACHE_DIR
        self.speaker = speaker or "debi"
        self.engine = engine or TTS_ENGINE
        self.tts_backend = None

        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info(f"TTS 서비스 초기화 (엔진: {self.engine}, 화자: {self.speaker})")

    async def initialize(self):
        """TTS 엔진을 비동기로 초기화합니다."""
        if self.tts_backend is not None:
            return

        if self.engine == "gcloud":
            # Google Cloud TTS (GCP VM에서 초저지연)
            from .gcloud_tts_client import GCloudTTSClient
            self.tts_backend = GCloudTTSClient()
            await self.tts_backend.initialize()
            logger.info("Google Cloud TTS 클라이언트 초기화 완료")
        elif self.engine == "edge":
            # Edge TTS (Microsoft, 무료, 빠름)
            from .edge_tts_client import EdgeTTSClient
            self.tts_backend = EdgeTTSClient()
            await self.tts_backend.initialize()
            logger.info("Edge TTS 클라이언트 초기화 완료")
        elif self.engine == "cosyvoice3":
            # CosyVoice3 파인튜닝 모델 (Modal Serverless)
            from .cosyvoice3_client import CosyVoice3Client
            self.tts_backend = CosyVoice3Client()
            await self.tts_backend.initialize()
            logger.info("CosyVoice3 클라이언트 초기화 완료")
        elif self.engine == "fish":
            # Fish-Speech OpenAudio S1-mini (zero-shot, 빠름)
            from .fish_tts_client import FishTTSClient
            self.tts_backend = FishTTSClient()
            await self.tts_backend.initialize()
            logger.info("Fish-TTS 클라이언트 초기화 완료")
        elif self.engine == "modal":
            # Modal Serverless Qwen3-TTS
            from .modal_tts_client import ModalTTSClient
            self.tts_backend = ModalTTSClient()
            await self.tts_backend.initialize()
            logger.info("Modal TTS 클라이언트 초기화 완료")
        elif self.engine == "sovits":
            # GPT-SoVITS v2Pro (Modal Serverless)
            from .sovits_tts_client import SoVITSTTSClient
            self.tts_backend = SoVITSTTSClient()
            await self.tts_backend.initialize()
            logger.info("SoVITS TTS 클라이언트 초기화 완료")
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
        output_path: Optional[str] = None,
        guild_name: Optional[str] = None,
        channel_name: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환합니다.

        Args:
            text: 변환할 텍스트
            output_path: 저장할 파일 경로 (없으면 자동 생성)
            guild_name: 서버 이름 (로깅용)
            channel_name: 채널 이름 (로깅용)
            user_name: 유저 이름 (로깅용)

        Returns:
            생성된 음성 파일의 경로
        """
        if not self.tts_backend:
            raise RuntimeError("TTS 서비스가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")

        # 텍스트 전처리 (ㅋㅋ → 크크, ㄱㄱ → 고고 등)
        processed_text = preprocess_text_for_tts(text)
        if processed_text != text:
            logger.info(f"텍스트 전처리: '{text}' -> '{processed_text}'")

        # 캐시 확인 (엔진 + 화자 + 전처리된 텍스트 기준)
        cache_key = hashlib.md5(f"{self.engine}:{self.speaker}:{processed_text}".encode()).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pcm")

        if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            logger.info(f"TTS 캐시 히트: '{processed_text[:30]}...' -> {cache_path}")
            return cache_path

        # 캐시 미스: TTS 생성
        audio_path = await self.tts_backend.text_to_speech(
            text=processed_text,
            speaker=self.speaker,
            language=self.language,
            output_path=output_path,
            guild_name=guild_name,
            channel_name=channel_name,
            user_name=user_name
        )

        # PCM 변환 후 캐시 저장
        pcm_path = await convert_to_discord_pcm(audio_path)
        try:
            if pcm_path != cache_path:
                import shutil
                shutil.copy2(pcm_path, cache_path)
            self._evict_cache_if_needed()
            logger.info(f"TTS 캐시 저장: '{processed_text[:30]}...' -> {cache_path}")
        except Exception as e:
            logger.warning(f"TTS 캐시 저장 실패 (무시): {e}")

        return pcm_path

    async def text_to_speech_streaming(
        self,
        text: str,
        guild_name: Optional[str] = None,
        channel_name: Optional[str] = None,
        user_name: Optional[str] = None,
    ):
        """
        스트리밍 TTS - 오디오 청크 파일 경로를 yield.
        Modal 엔진에서만 사용 가능. 다른 엔진은 전체 생성 후 단일 yield.
        """
        if not self.tts_backend:
            raise RuntimeError("TTS 서비스가 초기화되지 않았습니다.")

        processed_text = preprocess_text_for_tts(text)

        # Modal / CosyVoice3 클라이언트 스트리밍 지원
        if self.engine in ("modal", "cosyvoice3") and hasattr(self.tts_backend, "text_to_speech_streaming"):
            async for audio_path in self.tts_backend.text_to_speech_streaming(
                text=processed_text,
                speaker=self.speaker,
                guild_name=guild_name,
                channel_name=channel_name,
                user_name=user_name,
            ):
                yield audio_path
        else:
            # 다른 엔진: 전체 생성 후 단일 yield (fallback)
            audio_path = await self.text_to_speech(
                text=text,
                guild_name=guild_name,
                channel_name=channel_name,
                user_name=user_name,
            )
            yield audio_path

    def _evict_cache_if_needed(self):
        """캐시 파일이 최대 개수를 초과하면 오래된 것부터 삭제"""
        try:
            cache_files = [
                os.path.join(self.cache_dir, f)
                for f in os.listdir(self.cache_dir)
                if f.endswith(".pcm")
            ]
            if len(cache_files) <= TTS_CACHE_MAX:
                return

            # 수정 시간 기준 오래된 순 정렬
            cache_files.sort(key=lambda f: os.path.getmtime(f))
            # 초과분 삭제
            for f in cache_files[:len(cache_files) - TTS_CACHE_MAX]:
                os.remove(f)
                logger.info(f"캐시 정리: {os.path.basename(f)}")
        except Exception as e:
            logger.warning(f"캐시 정리 실패: {e}")

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
