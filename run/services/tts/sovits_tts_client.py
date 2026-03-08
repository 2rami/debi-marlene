"""
GPT-SoVITS v2Pro Modal TTS 클라이언트

Modal Serverless에서 실행되는 GPT-SoVITS API를 호출합니다.
"""

import os
import hashlib
import logging
import asyncio
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_SOVITS_URL = os.environ.get(
    "SOVITS_TTS_API_URL",
    "https://goenho0613--sovits-tts-server-sovitsmodel-tts.modal.run"
)
DEFAULT_SOVITS_HEALTH_URL = os.environ.get(
    "SOVITS_TTS_HEALTH_URL",
    "https://goenho0613--sovits-tts-server-sovitsmodel-health.modal.run"
)


class SoVITSTTSClient:
    """GPT-SoVITS v2Pro Modal TTS 클라이언트"""

    def __init__(self, api_url: Optional[str] = None, health_url: Optional[str] = None):
        self.api_url = api_url or DEFAULT_SOVITS_URL
        self.health_url = health_url or DEFAULT_SOVITS_HEALTH_URL
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        self._session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=180, connect=30, sock_read=150)
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"SoVITS TTS 클라이언트 생성: {self.api_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def initialize(self):
        """서버 연결 확인"""
        try:
            session = await self._get_session()
            async with session.get(self.health_url) as response:
                if response.status == 200:
                    self.is_initialized = True
                    logger.info("SoVITS TTS 서버 연결 확인")
                else:
                    self.is_initialized = False
        except asyncio.TimeoutError:
            logger.warning("SoVITS TTS 서버 cold start 중... (정상)")
            self.is_initialized = True
        except aiohttp.ClientError as e:
            logger.error(f"SoVITS TTS 서버 연결 실패: {e}")
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
            raise RuntimeError("SoVITS API URL이 설정되지 않음")

        if len(text) > 500:
            text = text[:500]

        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"sovits_tts_{speaker}_{text_hash}.wav")

        session = await self._get_session()
        last_error = None

        payload = {"text": text, "text_language": language}

        for attempt in range(max_retries + 1):
            try:
                async with session.post(self.api_url, json=payload) as response:
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "")
                        if "audio" in content_type:
                            audio_data = await response.read()
                            with open(output_path, "wb") as f:
                                f.write(audio_data)
                            logger.info(f"SoVITS TTS 생성 완료: {output_path}")
                            return output_path
                        else:
                            data = await response.json()
                            raise RuntimeError(f"TTS 생성 실패: {data.get('error', 'Unknown')}")
                    elif response.status == 503:
                        logger.info(f"SoVITS cold start 중... ({attempt + 1}/{max_retries + 1})")
                        if attempt < max_retries:
                            await asyncio.sleep(5)
                            continue
                        raise RuntimeError("SoVITS 서버 준비 중")
                    else:
                        error_detail = await response.text()
                        raise RuntimeError(f"TTS 실패: {response.status} - {error_detail}")
            except asyncio.TimeoutError:
                last_error = "타임아웃"
                if attempt < max_retries:
                    continue
            except aiohttp.ClientError as e:
                last_error = str(e)
                if attempt < max_retries:
                    await asyncio.sleep(2)
                    continue

        raise RuntimeError(f"SoVITS TTS 실패: {last_error}")

    def cleanup_temp_files(self):
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith("sovits_tts_") and file.endswith(".wav"):
                    os.remove(os.path.join(self.temp_dir, file))
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
