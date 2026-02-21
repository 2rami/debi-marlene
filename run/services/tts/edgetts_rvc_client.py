"""
edge-tts + RVC v2 TTS 클라이언트

Modal에서 실행되는 edge-tts + RVC 파이프라인 API를 호출합니다.
기존 ModalTTSClient와 동일한 인터페이스를 제공합니다.
"""

import os
import hashlib
import logging
import asyncio
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_API_URL = os.environ.get(
    "EDGETTS_RVC_API_URL",
    "https://goenho0613--edgetts-rvc-server-edgettsrvc-tts.modal.run"
)
DEFAULT_HEALTH_URL = os.environ.get(
    "EDGETTS_RVC_HEALTH_URL",
    "https://goenho0613--edgetts-rvc-server-edgettsrvc-health.modal.run"
)


class EdgeTTSRVCClient:
    """
    edge-tts + RVC v2 TTS 클라이언트

    ModalTTSClient와 동일한 인터페이스.
    """

    def __init__(self, api_url: Optional[str] = None, health_url: Optional[str] = None):
        self.api_url = api_url or DEFAULT_API_URL
        self.health_url = health_url or DEFAULT_HEALTH_URL
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        self._session: Optional[aiohttp.ClientSession] = None

        self.timeout = aiohttp.ClientTimeout(
            total=60,  # edge-tts + RVC는 빠르므로 60초면 충분
            connect=30,
            sock_read=30
        )

        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"EdgeTTS+RVC 클라이언트 생성: {self.api_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def initialize(self):
        if not self.api_url:
            logger.warning("EdgeTTS+RVC API URL이 설정되지 않음")
            self.is_initialized = False
            return

        try:
            session = await self._get_session()
            async with session.get(self.health_url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models_loaded", [])
                    self.is_initialized = len(models) > 0
                    logger.info(f"EdgeTTS+RVC 서버 연결: models={models}")
                else:
                    self.is_initialized = False
        except asyncio.TimeoutError:
            logger.warning("EdgeTTS+RVC 서버 cold start 중... (정상)")
            self.is_initialized = True
        except aiohttp.ClientError as e:
            logger.error(f"EdgeTTS+RVC 서버 연결 실패: {e}")
            self.is_initialized = False

    async def text_to_speech(
        self,
        text: str,
        speaker: str = "debi",
        language: str = "ko",
        output_path: Optional[str] = None,
        max_retries: int = 2,
        guild_name: Optional[str] = None,
        channel_name: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> str:
        if not self.api_url:
            raise RuntimeError("EdgeTTS+RVC API URL이 설정되지 않음")

        if len(text) > 500:
            text = text[:500]

        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"edgetts_rvc_{speaker}_{text_hash}.wav")

        session = await self._get_session()
        last_error = None

        payload = {
            "text": text,
            "speaker": speaker,
            "guild_name": guild_name,
            "channel_name": channel_name,
            "user_name": user_name,
        }

        for attempt in range(max_retries + 1):
            try:
                async with session.post(self.api_url, json=payload) as response:
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "")

                        if "audio" in content_type:
                            audio_data = await response.read()
                            with open(output_path, "wb") as f:
                                f.write(audio_data)
                            logger.info(f"EdgeTTS+RVC 생성 완료: {output_path}")
                            return output_path
                        else:
                            data = await response.json()
                            error = data.get("error", "Unknown error")
                            raise RuntimeError(f"TTS 생성 실패: {error}")

                    elif response.status == 503:
                        logger.info(f"Cold start 중... (시도 {attempt + 1}/{max_retries + 1})")
                        if attempt < max_retries:
                            await asyncio.sleep(5)
                            continue
                        raise RuntimeError("서버 준비 중, 잠시 후 다시 시도하세요")

                    else:
                        error_detail = await response.text()
                        raise RuntimeError(f"TTS 실패: {response.status} - {error_detail}")

            except asyncio.TimeoutError:
                logger.warning(f"타임아웃 (시도 {attempt + 1}/{max_retries + 1})")
                last_error = "타임아웃"
                if attempt < max_retries:
                    continue
            except aiohttp.ClientError as e:
                last_error = str(e)
                if attempt < max_retries:
                    await asyncio.sleep(2)
                    continue

        raise RuntimeError(f"EdgeTTS+RVC TTS 실패: {last_error}")

    async def warm_up(self):
        logger.info("EdgeTTS+RVC 서버 워밍업 중...")
        await self.initialize()
        logger.info("EdgeTTS+RVC 서버 워밍업 완료")

    def cleanup_temp_files(self):
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith("edgetts_rvc_") and file.endswith(".wav"):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def list_speakers(self):
        return ["debi", "marlene"]
