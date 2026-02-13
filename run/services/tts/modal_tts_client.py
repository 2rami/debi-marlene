"""
Modal TTS API 클라이언트

Modal Serverless에서 실행되는 TTS API를 호출합니다.
Cold start 처리 및 재시도 로직이 포함되어 있습니다.
"""

import os
import hashlib
import logging
import asyncio
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)

# Modal API URLs
DEFAULT_MODAL_URL = os.environ.get(
    "MODAL_TTS_API_URL",
    "https://goenho0613--qwen3-tts-server-ttsmodel-tts.modal.run"
)
DEFAULT_MODAL_HEALTH_URL = os.environ.get(
    "MODAL_TTS_HEALTH_URL",
    "https://goenho0613--qwen3-tts-server-ttsmodel-health.modal.run"
)


class ModalTTSClient:
    """
    Modal Serverless TTS 클라이언트

    Cold start가 있을 수 있으므로 타임아웃과 재시도 처리가 포함됩니다.
    """

    def __init__(self, api_url: Optional[str] = None, health_url: Optional[str] = None):
        """
        클라이언트 초기화

        Args:
            api_url: Modal TTS API URL
            health_url: Modal TTS Health URL
        """
        self.api_url = api_url or DEFAULT_MODAL_URL
        self.health_url = health_url or DEFAULT_MODAL_HEALTH_URL
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        self._session: Optional[aiohttp.ClientSession] = None

        # Cold start 대응: 긴 타임아웃
        self.timeout = aiohttp.ClientTimeout(
            total=180,  # 전체 180초 (cold start + 긴 문장 대응)
            connect=30,
            sock_read=150
        )

        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"Modal TTS 클라이언트 생성: {self.api_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """HTTP 세션 가져오기"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def initialize(self):
        """서버 연결 확인 (warm up)"""
        if not self.api_url:
            logger.warning("Modal API URL이 설정되지 않음")
            self.is_initialized = False
            return

        try:
            session = await self._get_session()
            # health 엔드포인트 호출 (별도 URL)
            async with session.get(self.health_url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models_loaded", [])
                    self.is_initialized = len(models) > 0
                    logger.info(f"Modal TTS 서버 연결: models={models}")
                else:
                    logger.warning(f"Modal TTS 서버 응답 이상: {response.status}")
                    self.is_initialized = False
        except asyncio.TimeoutError:
            logger.warning("Modal TTS 서버 cold start 중... (정상)")
            self.is_initialized = True  # cold start는 정상
        except aiohttp.ClientError as e:
            logger.error(f"Modal TTS 서버 연결 실패: {e}")
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
        """
        텍스트를 음성으로 변환

        Args:
            text: 변환할 텍스트
            speaker: 화자 이름 (debi, marlene)
            language: 언어 코드 (사용 안 함, 호환용)
            output_path: 저장할 파일 경로
            max_retries: 최대 재시도 횟수 (cold start 대응)
            guild_name: 서버 이름 (로깅용)
            channel_name: 채널 이름 (로깅용)
            user_name: 유저 이름 (로깅용)

        Returns:
            생성된 음성 파일 경로
        """
        if not self.api_url:
            raise RuntimeError("Modal API URL이 설정되지 않음 (MODAL_TTS_API_URL)")

        # 500자 초과 시 자르기
        if len(text) > 500:
            text = text[:500]

        # 출력 파일 경로 생성
        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"modal_tts_{speaker}_{text_hash}.wav")

        session = await self._get_session()
        last_error = None

        # 요청 페이로드 (메타데이터 포함)
        payload = {
            "text": text,
            "speaker": speaker,
            "guild_name": guild_name,
            "channel_name": channel_name,
            "user_name": user_name
        }

        for attempt in range(max_retries + 1):
            try:
                async with session.post(
                    self.api_url,
                    json=payload
                ) as response:
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "")

                        if "audio" in content_type:
                            # 음성 데이터 저장
                            audio_data = await response.read()
                            with open(output_path, "wb") as f:
                                f.write(audio_data)
                            logger.info(f"Modal TTS 생성 완료: {output_path}")
                            return output_path
                        else:
                            # JSON 에러 응답
                            data = await response.json()
                            error = data.get("error", "Unknown error")
                            raise RuntimeError(f"TTS 생성 실패: {error}")

                    elif response.status == 503:
                        # 서버 준비 중 (cold start)
                        logger.info(f"Modal cold start 중... (시도 {attempt + 1}/{max_retries + 1})")
                        if attempt < max_retries:
                            await asyncio.sleep(5)
                            continue
                        raise RuntimeError("Modal 서버 준비 중, 잠시 후 다시 시도하세요")

                    else:
                        error_detail = await response.text()
                        raise RuntimeError(f"TTS 생성 실패: {response.status} - {error_detail}")

            except asyncio.TimeoutError:
                logger.warning(f"Modal 타임아웃 (시도 {attempt + 1}/{max_retries + 1})")
                last_error = "타임아웃 - Modal 서버 cold start가 오래 걸릴 수 있습니다"
                if attempt < max_retries:
                    continue
            except aiohttp.ClientError as e:
                last_error = str(e)
                if attempt < max_retries:
                    await asyncio.sleep(2)
                    continue

        raise RuntimeError(f"Modal TTS 실패: {last_error}")

    async def warm_up(self):
        """서버 워밍업 (cold start 방지용)"""
        logger.info("Modal TTS 서버 워밍업 중...")
        await self.initialize()
        logger.info("Modal TTS 서버 워밍업 완료")

    def cleanup_temp_files(self):
        """임시 음성 파일 정리"""
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith("modal_tts_") and file.endswith(".wav"):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            logger.info("Modal TTS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    async def close(self):
        """세션 종료"""
        if self._session and not self._session.closed:
            await self._session.close()

    def list_speakers(self):
        """사용 가능한 화자 목록"""
        return ["debi", "marlene"]
