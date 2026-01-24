"""
Qwen3-TTS Voice Clone 서비스

Qwen3-TTS 1.7B 모델을 사용하여 Voice Clone 방식으로 TTS를 생성합니다.
GPU가 있는 환경에서만 작동합니다.
"""

import os
import asyncio
import logging
import hashlib
from typing import Optional, Dict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# 참조 오디오 설정 (voice clone에 사용)
DEFAULT_REF_AUDIO_DIR = os.environ.get(
    "QWEN3_TTS_REF_AUDIO_DIR",
    "/content/drive/MyDrive/debi_tts_data/audio"  # Colab용 기본값
)


class Qwen3TTSService:
    """
    Qwen3-TTS Voice Clone 서비스

    Base 모델 + Voice Clone으로 데비&마를렌 음성을 생성합니다.
    """

    def __init__(
        self,
        model_id: str = "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        ref_audio_dir: Optional[str] = None
    ):
        """
        Qwen3-TTS 서비스 초기화

        Args:
            model_id: HuggingFace 모델 ID
            ref_audio_dir: 참조 오디오 파일 디렉토리
        """
        self.model_id = model_id
        self.ref_audio_dir = ref_audio_dir or DEFAULT_REF_AUDIO_DIR
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        self.model = None
        self.voice_prompts: Dict[str, any] = {}  # 캐시된 voice prompt
        self.executor = ThreadPoolExecutor(max_workers=1)

        # 화자별 참조 오디오/텍스트 설정
        self.speaker_config = {
            "debi": {
                "ref_audio": "Debi_airSupply_2_01.wav",
                "ref_text": "줄 거면 좀 쉽게 열리게 만들면 덧나?"
            },
            "marlene": {
                "ref_audio": "Marlene_airSupply_2_01.wav",  # 마를렌 참조 오디오 필요
                "ref_text": "이게 뭐야, 전부 떨어지네."  # 마를렌 참조 텍스트
            },
            "default": {
                "ref_audio": "Debi_airSupply_2_01.wav",
                "ref_text": "줄 거면 좀 쉽게 열리게 만들면 덧나?"
            }
        }

        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"Qwen3-TTS 서비스 생성: model_id={self.model_id}")

    def _load_model_sync(self):
        """모델을 동기적으로 로드 (스레드에서 실행)"""
        import torch
        from qwen_tts import Qwen3TTSModel

        # 디바이스/dtype 설정
        if torch.cuda.is_available():
            device = "cuda"
            dtype = torch.bfloat16
        else:
            device = "cpu"
            dtype = torch.float32
            logger.warning("CUDA 사용 불가, CPU 모드로 실행 (매우 느림)")

        logger.info(f"Qwen3-TTS 모델 로드 중: {self.model_id} (device: {device})")

        self.model = Qwen3TTSModel.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
            device_map=device
        )

        self.is_initialized = True
        logger.info("Qwen3-TTS 모델 로드 완료")

    def _create_voice_prompt_sync(self, speaker: str):
        """Voice clone prompt 생성 (동기, 스레드에서 실행)"""
        config = self.speaker_config.get(speaker, self.speaker_config["default"])

        ref_audio_path = os.path.join(self.ref_audio_dir, config["ref_audio"])

        if not os.path.exists(ref_audio_path):
            logger.error(f"참조 오디오 파일 없음: {ref_audio_path}")
            raise FileNotFoundError(f"참조 오디오 파일이 없습니다: {ref_audio_path}")

        logger.info(f"Voice prompt 생성 중: {speaker} ({ref_audio_path})")

        voice_prompt = self.model.create_voice_clone_prompt(
            ref_audio=ref_audio_path,
            ref_text=config["ref_text"]
        )

        return voice_prompt

    async def initialize(self):
        """
        Qwen3-TTS 모델을 비동기로 로드합니다.
        """
        if self.is_initialized:
            logger.info("Qwen3-TTS 이미 초기화됨")
            return

        # 스레드에서 모델 로드 (블로킹 방지)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, self._load_model_sync)

    async def _get_voice_prompt(self, speaker: str):
        """Voice prompt를 가져옵니다 (캐시 사용)."""
        if speaker not in self.voice_prompts:
            loop = asyncio.get_event_loop()
            self.voice_prompts[speaker] = await loop.run_in_executor(
                self.executor,
                self._create_voice_prompt_sync,
                speaker
            )
        return self.voice_prompts[speaker]

    def _generate_speech_sync(
        self,
        text: str,
        voice_prompt,
        output_path: str
    ) -> str:
        """음성 생성 (동기, 스레드에서 실행)"""
        import soundfile as sf

        wavs, sr = self.model.generate_voice_clone(
            text=text,
            voice_clone_prompt=voice_prompt,
            language="korean"
        )

        sf.write(output_path, wavs[0], sr)
        return output_path

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
            speaker: 화자 이름 (debi, marlene)
            language: 언어 코드 (사용 안 함, 하위 호환용)
            output_path: 저장할 파일 경로 (없으면 자동 생성)

        Returns:
            생성된 음성 파일의 경로
        """
        if not self.is_initialized:
            await self.initialize()

        # Voice prompt 가져오기
        speaker_key = speaker.lower()
        if speaker_key not in self.speaker_config:
            speaker_key = "default"

        voice_prompt = await self._get_voice_prompt(speaker_key)

        # 출력 파일 경로 생성
        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"qwen3_{speaker}_{text_hash}.wav")

        logger.info(f"TTS 생성: {text[:30]}... (화자: {speaker})")

        # 스레드에서 음성 생성
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._generate_speech_sync,
            text, voice_prompt, output_path
        )

        logger.info(f"TTS 생성 완료: {output_path}")
        return result

    def cleanup_temp_files(self):
        """임시 음성 파일들을 정리합니다."""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path) and file.startswith("qwen3_"):
                    os.remove(file_path)
            logger.info("Qwen3-TTS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    def list_speakers(self):
        """사용 가능한 스피커 목록을 반환합니다."""
        return list(self.speaker_config.keys())
