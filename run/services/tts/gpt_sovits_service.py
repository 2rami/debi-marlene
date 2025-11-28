"""
GPT-SoVITS TTS 서비스 (API 클라이언트)

GPT-SoVITS API 서버에 HTTP 요청을 보내 TTS를 생성합니다.
"""

import os
import asyncio
import logging
from typing import Optional, List
import hashlib

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None

logger = logging.getLogger(__name__)


class GPTSoVITSService:
    """
    GPT-SoVITS API 클라이언트

    GPT-SoVITS API 서버와 통신하여 TTS를 생성합니다.
    """

    def __init__(
        self,
        gpt_model_path: str,
        sovits_model_path: str,
        reference_audio_dir: str = "assets/reference_audio",
        api_url: str = "http://localhost:9880"
    ):
        """
        GPT-SoVITS 서비스 초기화

        Args:
            gpt_model_path: GPT 모델 경로 (.ckpt) - API 서버에서 사용
            sovits_model_path: SoVITS 모델 경로 (.pth) - API 서버에서 사용
            reference_audio_dir: 참조 오디오 파일이 저장된 디렉토리
            api_url: GPT-SoVITS API 서버 주소
        """
        # 경로를 절대 경로로 변환
        self.gpt_model_path = os.path.abspath(gpt_model_path)
        self.sovits_model_path = os.path.abspath(sovits_model_path)
        self.reference_audio_dir = os.path.abspath(reference_audio_dir)
        self.api_url = api_url
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False

        # 캐릭터별 참조 오디오 설정 (절대 경로 사용)
        self.reference_audio_config = {
            "debi": {
                "audio_path": os.path.abspath(os.path.join(reference_audio_dir, "debi_reference.wav")),
                "text": "이야~ 수영복이라도 챙겨올걸 그랬나~?",
                "language": "ko"
            },
            "marlene": {
                "audio_path": os.path.abspath(os.path.join(reference_audio_dir, "marlene_reference.wav")),
                "text": "포기하던가 아니면 끝까지 발악하던가",
                "language": "ko"
            },
            "default": {
                "audio_path": os.path.abspath(os.path.join(reference_audio_dir, "debi_reference.wav")),
                "text": "이야~ 수영복이라도 챙겨올걸 그랬나~?",
                "language": "ko"
            }
        }

        # 임시 디렉토리 생성
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.reference_audio_dir, exist_ok=True)

        logger.info(f"GPT-SoVITS API 클라이언트 생성: API={api_url}")

    async def initialize(self):
        """
        GPT-SoVITS API 서버 연결을 확인합니다.

        Note: API 서버가 config 파일로 시작된 경우 모델이 이미 로드되어 있으므로
        별도의 모델 로딩이 필요하지 않습니다.
        """
        if self.is_initialized:
            logger.info("GPT-SoVITS 이미 초기화됨")
            return

        # API 서버가 이미 실행되고 있다고 가정하고 초기화 완료
        self.is_initialized = True
        logger.info(f"GPT-SoVITS API 초기화 완료 (API: {self.api_url}, 모델은 서버에서 미리 로드됨)")

    async def text_to_speech(
        self,
        text: str,
        speaker: str = "debi",
        language: str = "ko",
        output_path: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환합니다.

        Args:
            text: 변환할 텍스트
            speaker: 화자 이름 (debi, marlene, default)
            language: 언어 코드
            output_path: 저장할 파일 경로 (없으면 자동 생성)

        Returns:
            생성된 음성 파일의 경로
        """
        if not self.is_initialized:
            await self.initialize()

        # 참조 오디오 정보 가져오기
        ref_config = self.reference_audio_config.get(
            speaker.lower(),
            self.reference_audio_config["default"]
        )

        ref_audio_path = ref_config["audio_path"]
        ref_text = ref_config["text"]
        ref_language = ref_config["language"]

        # 참조 오디오 파일 확인
        if not os.path.exists(ref_audio_path):
            logger.error(f"참조 오디오 파일을 찾을 수 없습니다: {ref_audio_path}")
            raise FileNotFoundError(f"참조 오디오 파일이 없습니다: {ref_audio_path}")

        # 출력 파일 경로 생성
        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"tts_{speaker}_{text_hash}.wav")

        try:
            logger.info(f"TTS API 요청: {text[:30]}... (화자: {speaker})")

            # API 요청 데이터
            request_data = {
                "text": text,
                "text_lang": language,
                "ref_audio_path": ref_audio_path,
                "prompt_text": ref_text,
                "prompt_lang": ref_language,
                "top_k": 15,
                "top_p": 1.0,
                "temperature": 1.0,
                "text_split_method": "cut5",
                "batch_size": 1,
                "speed_factor": 1.0,
                "streaming_mode": False
            }

            # API 서버에 TTS 요청
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/tts",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        # 오디오 데이터 저장
                        audio_data = await resp.read()
                        with open(output_path, "wb") as f:
                            f.write(audio_data)
                        logger.info(f"TTS 변환 완료: {output_path}")
                        return output_path
                    else:
                        error_msg = await resp.text()
                        raise Exception(f"TTS API 오류: {error_msg}")

        except Exception as e:
            logger.error(f"GPT-SoVITS TTS 변환 실패: {e}")
            raise

    def cleanup_temp_files(self):
        """임시 음성 파일들을 정리합니다."""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path) and file.startswith("tts_"):
                    os.remove(file_path)
            logger.info("GPT-SoVITS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    @staticmethod
    def mix_audio_files(audio_paths: List[str], output_path: str) -> str:
        """
        여러 오디오 파일을 믹싱(합성)합니다.

        Args:
            audio_paths: 믹싱할 오디오 파일 경로 리스트
            output_path: 출력 파일 경로

        Returns:
            믹싱된 오디오 파일 경로
        """
        if AudioSegment is None:
            raise ImportError("pydub가 설치되지 않았습니다. pip install pydub을 실행하세요.")

        if not audio_paths:
            raise ValueError("믹싱할 오디오 파일이 없습니다.")

        try:
            # 첫 번째 오디오 로드
            mixed = AudioSegment.from_file(audio_paths[0])

            # 나머지 오디오를 오버레이
            for audio_path in audio_paths[1:]:
                audio = AudioSegment.from_file(audio_path)
                # 두 오디오를 동시에 재생 (오버레이)
                mixed = mixed.overlay(audio)

            # 믹싱된 오디오 저장
            mixed.export(output_path, format="wav")
            logger.info(f"오디오 믹싱 완료: {len(audio_paths)}개 파일 -> {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"오디오 믹싱 실패: {e}")
            raise

    @staticmethod
    def concatenate_audio_files(audio_paths: List[str], output_path: str) -> str:
        """
        여러 오디오 파일을 순서대로 이어붙입니다.

        Args:
            audio_paths: 이어붙일 오디오 파일 경로 리스트
            output_path: 출력 파일 경로

        Returns:
            이어붙인 오디오 파일 경로
        """
        if AudioSegment is None:
            raise ImportError("pydub가 설치되지 않았습니다. pip install pydub을 실행하세요.")

        if not audio_paths:
            raise ValueError("이어붙일 오디오 파일이 없습니다.")

        try:
            # 첫 번째 오디오 로드
            combined = AudioSegment.from_file(audio_paths[0])

            # 나머지 오디오를 순서대로 이어붙이기
            for audio_path in audio_paths[1:]:
                audio = AudioSegment.from_file(audio_path)
                combined = combined + audio

            # 이어붙인 오디오 저장
            combined.export(output_path, format="wav")
            logger.info(f"오디오 이어붙이기 완료: {len(audio_paths)}개 파일 -> {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"오디오 이어붙이기 실패: {e}")
            raise
