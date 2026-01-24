"""
Qwen3-TTS API 클라이언트

FastAPI TTS 서버를 호출하여 음성을 생성합니다.
Discord 봇에서 사용합니다.
"""

import os
import hashlib
import logging
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)

# API 서버 설정
DEFAULT_API_URL = os.environ.get("QWEN3_TTS_API_URL", "http://localhost:8100")


class Qwen3TTSClient:
    """
    Qwen3-TTS API 클라이언트

    로컬 FastAPI 서버를 호출하여 TTS를 생성합니다.
    """

    def __init__(self, api_url: Optional[str] = None):
        """
        클라이언트 초기화

        Args:
            api_url: TTS API 서버 URL (기본값: http://localhost:8100)
        """
        self.api_url = api_url or DEFAULT_API_URL
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        self._session: Optional[aiohttp.ClientSession] = None

        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"Qwen3-TTS 클라이언트 생성: {self.api_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """HTTP 세션 가져오기"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            )
        return self._session

    async def initialize(self):
        """서버 연결 확인"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.api_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.is_initialized = data.get("model_loaded", False)
                    logger.info(f"TTS API 서버 연결 확인: {data}")
                else:
                    logger.warning(f"TTS API 서버 응답 이상: {response.status}")
                    self.is_initialized = False
        except aiohttp.ClientError as e:
            logger.error(f"TTS API 서버 연결 실패: {e}")
            self.is_initialized = False

    async def text_to_speech(
        self,
        text: str,
        speaker: str = "debi",
        language: str = "ko",
        output_path: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환

        Args:
            text: 변환할 텍스트
            speaker: 화자 이름 (debi, marlene)
            language: 언어 코드 (사용 안 함, 호환용)
            output_path: 저장할 파일 경로

        Returns:
            생성된 음성 파일 경로
        """
        # 출력 파일 경로 생성
        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"tts_{speaker}_{text_hash}.wav")

        try:
            session = await self._get_session()

            # TTS API 호출
            async with session.post(
                f"{self.api_url}/tts",
                json={"text": text, "speaker": speaker}
            ) as response:
                if response.status == 200:
                    # 음성 데이터 저장
                    audio_data = await response.read()
                    with open(output_path, "wb") as f:
                        f.write(audio_data)

                    logger.info(f"TTS 생성 완료: {output_path}")
                    return output_path

                elif response.status == 503:
                    raise RuntimeError("TTS 서버 모델 로딩 중")
                else:
                    error_detail = await response.text()
                    raise RuntimeError(f"TTS 생성 실패: {response.status} - {error_detail}")

        except aiohttp.ClientError as e:
            raise RuntimeError(f"TTS API 서버 연결 실패: {e}")

    async def get_speakers(self) -> list:
        """사용 가능한 화자 목록"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.api_url}/speakers") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("speakers", [])
                return []
        except aiohttp.ClientError:
            return []

    def cleanup_temp_files(self):
        """임시 음성 파일 정리"""
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith("tts_") and file.endswith(".wav"):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            logger.info("TTS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    async def close(self):
        """세션 종료"""
        if self._session and not self._session.closed:
            await self._session.close()

    def list_speakers(self):
        """동기용 화자 목록 (호환용)"""
        return ["debi", "marlene"]
