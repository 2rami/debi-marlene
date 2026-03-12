"""
CosyVoice3 TTS 클라이언트

Modal에서 실행되는 CosyVoice3 API를 호출합니다.
기존 ModalTTSClient / FishTTSClient와 동일한 인터페이스를 제공합니다.
"""

import io
import os
import wave
import struct
import hashlib
import logging
import asyncio
import audioop
import aiohttp
from typing import Optional, AsyncGenerator

logger = logging.getLogger(__name__)

DEFAULT_API_URL = os.environ.get(
    "COSYVOICE3_API_URL",
    "https://goenho0613--cosyvoice3-tts-server-cosyvoice3model-tts.modal.run"
)
DEFAULT_STREAM_URL = os.environ.get(
    "COSYVOICE3_STREAM_URL",
    "https://goenho0613--cosyvoice3-tts-server-cosyvoice3model-tts-stream.modal.run"
)
DEFAULT_HEALTH_URL = os.environ.get(
    "COSYVOICE3_HEALTH_URL",
    "https://goenho0613--cosyvoice3-tts-server-cosyvoice3model-health.modal.run"
)

# Alex 전용 Modal 엔드포인트 (별도 체크포인트)
ALEX_API_URL = os.environ.get(
    "COSYVOICE3_ALEX_API_URL",
    "https://goenho0613--cosyvoice3-alex-tts-server-cosyvoice3model-tts.modal.run"
)
ALEX_STREAM_URL = os.environ.get(
    "COSYVOICE3_ALEX_STREAM_URL",
    "https://goenho0613--cosyvoice3-alex-tts-server-cosyvoice3model-t-e222cf.modal.run"
)
ALEX_HEALTH_URL = os.environ.get(
    "COSYVOICE3_ALEX_HEALTH_URL",
    "https://goenho0613--cosyvoice3-alex-tts-server-cosyvoice3model-health.modal.run"
)

# 스피커별 엔드포인트 매핑
SPEAKER_ENDPOINTS = {
    "debi": {"api": DEFAULT_API_URL, "stream": DEFAULT_STREAM_URL, "health": DEFAULT_HEALTH_URL},
    "marlene": {"api": DEFAULT_API_URL, "stream": DEFAULT_STREAM_URL, "health": DEFAULT_HEALTH_URL},
    "alex": {"api": ALEX_API_URL, "stream": ALEX_STREAM_URL, "health": ALEX_HEALTH_URL},
}


class CosyVoice3Client:
    """
    CosyVoice3 TTS 클라이언트

    기존 TTS 클라이언트들과 동일한 인터페이스.
    Cold start 대응 (120s timeout + 2회 재시도).
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        stream_url: Optional[str] = None,
        health_url: Optional[str] = None,
    ):
        self.api_url = api_url or DEFAULT_API_URL
        self.stream_url = stream_url or DEFAULT_STREAM_URL
        self.health_url = health_url or DEFAULT_HEALTH_URL
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        self._session: Optional[aiohttp.ClientSession] = None

        self.timeout = aiohttp.ClientTimeout(
            total=120,
            connect=30,
            sock_read=90,
        )

        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"CosyVoice3 클라이언트 생성: {self.api_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def initialize(self):
        if not self.api_url:
            logger.warning("CosyVoice3 API URL이 설정되지 않음")
            self.is_initialized = False
            return

        try:
            session = await self._get_session()
            async with session.get(self.health_url) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status", "")
                    self.is_initialized = status == "running"
                    logger.info(f"CosyVoice3 서버 연결: {data}")
                else:
                    self.is_initialized = False
        except asyncio.TimeoutError:
            logger.warning("CosyVoice3 서버 cold start 중... (정상)")
            self.is_initialized = True
        except aiohttp.ClientError as e:
            logger.error(f"CosyVoice3 서버 연결 실패: {e}")
            self.is_initialized = False

    def _get_urls_for_speaker(self, speaker: str) -> dict:
        """스피커별 엔드포인트 URL 반환"""
        endpoints = SPEAKER_ENDPOINTS.get(speaker)
        if endpoints:
            return endpoints
        # 알 수 없는 스피커는 기본 엔드포인트 사용
        return SPEAKER_ENDPOINTS["debi"]

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
        urls = self._get_urls_for_speaker(speaker)
        api_url = urls["api"]
        if not api_url:
            raise RuntimeError("CosyVoice3 API URL이 설정되지 않음")

        if len(text) > 500:
            text = text[:500]

        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(
                self.temp_dir, f"cosyvoice3_{speaker}_{text_hash}.pcm"
            )

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
                async with session.post(api_url, json=payload) as response:
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "")

                        if "audio" in content_type:
                            audio_data = await response.read()
                            # WAV → Discord PCM 변환 (48kHz stereo, FFmpeg 불필요)
                            pcm_data = self._wav_to_discord_pcm(audio_data)
                            with open(output_path, "wb") as f:
                                f.write(pcm_data)
                            return output_path
                        else:
                            data = await response.json()
                            error = data.get("error", "Unknown error")
                            raise RuntimeError(f"TTS 생성 실패: {error}")

                    elif response.status == 503:
                        logger.info(
                            f"Cold start 중... "
                            f"(시도 {attempt + 1}/{max_retries + 1})"
                        )
                        if attempt < max_retries:
                            await asyncio.sleep(5)
                            continue
                        raise RuntimeError("서버 준비 중, 잠시 후 다시 시도하세요")

                    else:
                        error_detail = await response.text()
                        raise RuntimeError(
                            f"TTS 실패: {response.status} - {error_detail}"
                        )

            except asyncio.TimeoutError:
                logger.warning(
                    f"타임아웃 (시도 {attempt + 1}/{max_retries + 1})"
                )
                last_error = "타임아웃 - CosyVoice3 서버 cold start가 오래 걸릴 수 있습니다"
                if attempt < max_retries:
                    continue
            except aiohttp.ClientError as e:
                last_error = str(e)
                if attempt < max_retries:
                    await asyncio.sleep(2)
                    continue

        raise RuntimeError(f"CosyVoice3 실패: {last_error}")

    @staticmethod
    def _wav_to_discord_pcm(wav_bytes: bytes) -> bytes:
        """WAV(24kHz mono) → Discord PCM(48kHz stereo 16bit). FFmpeg 불필요."""
        with wave.open(io.BytesIO(wav_bytes), 'rb') as wav:
            sr = wav.getframerate()
            mono_pcm = wav.readframes(wav.getnframes())

        # 리샘플링 (24kHz 등 → 48kHz)
        if sr != 48000:
            mono_pcm, _ = audioop.ratecv(mono_pcm, 2, 1, sr, 48000, None)

        # mono → stereo
        stereo_pcm = audioop.tostereo(mono_pcm, 2, 1, 1)

        # 앞쪽 무음 제거
        for i in range(0, len(stereo_pcm) - 4, 4):
            left = abs(struct.unpack_from('<h', stereo_pcm, i)[0])
            right = abs(struct.unpack_from('<h', stereo_pcm, i + 2)[0])
            if left > 500 or right > 500:
                return stereo_pcm[i:]

        return stereo_pcm

    async def text_to_speech_streaming(
        self,
        text: str,
        speaker: str = "debi",
        guild_name: Optional[str] = None,
        channel_name: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """스트리밍 TTS - 청크별 wav 파일 경로를 yield"""
        urls = self._get_urls_for_speaker(speaker)
        stream_url = urls["stream"]
        if not stream_url:
            raise RuntimeError("CosyVoice3 Stream URL이 설정되지 않음")

        if len(text) > 500:
            text = text[:500]

        session = await self._get_session()
        payload = {
            "text": text,
            "speaker": speaker,
            "guild_name": guild_name,
            "channel_name": channel_name,
            "user_name": user_name,
        }

        chunk_index = 0
        try:
            async with session.post(stream_url, json=payload) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    raise RuntimeError(f"TTS 스트리밍 실패: {response.status} - {error_detail}")

                buffer = b""
                async for data in response.content.iter_any():
                    buffer += data

                    while len(buffer) >= 8:
                        chunk_len = int.from_bytes(buffer[:4], "big")
                        total_needed = 8 + chunk_len
                        if len(buffer) < total_needed:
                            break

                        wav_data = buffer[8:total_needed]
                        buffer = buffer[total_needed:]

                        text_hash = hashlib.md5(
                            f"{text}{speaker}{chunk_index}".encode()
                        ).hexdigest()[:8]
                        output_path = os.path.join(
                            self.temp_dir,
                            f"cosyvoice3_stream_{speaker}_{text_hash}.wav",
                        )

                        with open(output_path, "wb") as f:
                            f.write(wav_data)

                        chunk_index += 1
                        yield output_path

        except asyncio.TimeoutError:
            raise RuntimeError("TTS 스트리밍 타임아웃")
        except aiohttp.ClientError as e:
            raise RuntimeError(f"TTS 스트리밍 연결 실패: {e}")

    async def warm_up(self):
        logger.info("CosyVoice3 서버 워밍업 중...")
        await self.initialize()
        logger.info("CosyVoice3 서버 워밍업 완료")

    def cleanup_temp_files(self):
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith("cosyvoice3_") and (file.endswith(".wav") or file.endswith(".pcm")):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def list_speakers(self):
        return list(SPEAKER_ENDPOINTS.keys())
