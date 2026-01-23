"""
CosyVoice3 TTS 서비스 (로컬 모델)

파인튜닝된 CosyVoice3 모델을 직접 로드하여 TTS를 생성합니다.
GPU가 있는 로컬 환경에서만 작동합니다.
"""

import os
import sys
import asyncio
import logging
import hashlib
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# CosyVoice 경로 설정
COSYVOICE_PATH = os.environ.get(
    "COSYVOICE_PATH",
    r"c:\Users\2rami\Desktop\KASA\CosyVoice"
)


class CosyVoiceService:
    """
    CosyVoice3 로컬 TTS 서비스

    파인튜닝된 모델을 사용하여 데비&마를렌 음성을 생성합니다.
    """

    def __init__(
        self,
        model_dir: Optional[str] = None,
        cosyvoice_path: str = COSYVOICE_PATH
    ):
        """
        CosyVoice3 서비스 초기화

        Args:
            model_dir: 모델 디렉토리 경로 (기본값: Fun-CosyVoice3-0.5B)
            cosyvoice_path: CosyVoice 설치 경로
        """
        self.cosyvoice_path = cosyvoice_path
        self.model_dir = model_dir or os.path.join(
            cosyvoice_path, "pretrained_models", "Fun-CosyVoice3-0.5B"
        )
        self.temp_dir = "/tmp/tts_audio"
        self.is_initialized = False
        self.cosyvoice = None
        self.executor = ThreadPoolExecutor(max_workers=1)

        # 스피커 매핑 (소문자 -> 실제 spk_id)
        self.speaker_map = {
            "debi": "Debi",
            "marlene": "Marlene",
            "default": "Debi"
        }

        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"CosyVoice3 서비스 생성: model_dir={self.model_dir}")

    def _setup_paths(self):
        """CosyVoice 경로를 sys.path에 추가"""
        paths_to_add = [
            self.cosyvoice_path,
            os.path.join(self.cosyvoice_path, "third_party", "Matcha-TTS")
        ]
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)

    def _load_model_sync(self):
        """모델을 동기적으로 로드 (스레드에서 실행)"""
        os.environ["TORCHAUDIO_BACKEND"] = "soundfile"

        self._setup_paths()

        import torchaudio
        try:
            torchaudio.set_audio_backend("soundfile")
        except:
            pass

        from cosyvoice.cli.cosyvoice import AutoModel

        logger.info(f"CosyVoice3 모델 로드 중: {self.model_dir}")
        self.cosyvoice = AutoModel(model_dir=self.model_dir)

        # 사용 가능한 스피커 확인
        speakers = self.cosyvoice.list_available_spks()
        logger.info(f"사용 가능한 스피커: {speakers}")

        if not speakers:
            logger.warning("스피커가 없습니다. spk2info.pt를 확인하세요.")

        self.is_initialized = True
        logger.info("CosyVoice3 모델 로드 완료")

    async def initialize(self):
        """
        CosyVoice3 모델을 비동기로 로드합니다.
        """
        if self.is_initialized:
            logger.info("CosyVoice3 이미 초기화됨")
            return

        # 모델 파일 확인
        llm_path = os.path.join(self.model_dir, "llm.pt")
        spk_path = os.path.join(self.model_dir, "spk2info.pt")

        if not os.path.exists(llm_path):
            raise FileNotFoundError(
                f"llm.pt 파일이 없습니다: {llm_path}\n"
                "Google Drive에서 파인튜닝 모델을 다운로드하세요."
            )

        if not os.path.exists(spk_path):
            raise FileNotFoundError(
                f"spk2info.pt 파일이 없습니다: {spk_path}\n"
                "Google Drive에서 spk2info.pt를 다운로드하세요."
            )

        # 스레드에서 모델 로드 (블로킹 방지)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, self._load_model_sync)

    def _generate_speech_sync(
        self,
        text: str,
        spk_id: str,
        output_path: str
    ) -> str:
        """음성 생성 (동기, 스레드에서 실행)"""
        import soundfile as sf

        for i, output in enumerate(self.cosyvoice.inference_sft(
            tts_text=text,
            spk_id=spk_id,
            stream=False
        )):
            audio_data = output['tts_speech'].squeeze().cpu().numpy()
            sf.write(output_path, audio_data, self.cosyvoice.sample_rate)
            break  # 첫 번째 결과만 사용

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

        # 스피커 ID 매핑
        spk_id = self.speaker_map.get(
            speaker.lower(),
            self.speaker_map["default"]
        )

        # 사용 가능한 스피커 확인
        available_spks = self.cosyvoice.list_available_spks()
        if spk_id not in available_spks:
            logger.warning(f"스피커 '{spk_id}'가 없습니다. 기본값 사용.")
            spk_id = available_spks[0] if available_spks else "Debi"

        # 출력 파일 경로 생성
        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"tts_{speaker}_{text_hash}.wav")

        logger.info(f"TTS 생성: {text[:30]}... (화자: {spk_id})")

        # 스레드에서 음성 생성
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._generate_speech_sync,
            text, spk_id, output_path
        )

        logger.info(f"TTS 생성 완료: {output_path}")
        return result

    def cleanup_temp_files(self):
        """임시 음성 파일들을 정리합니다."""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path) and file.startswith("tts_"):
                    os.remove(file_path)
            logger.info("CosyVoice3 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    def list_speakers(self) -> List[str]:
        """사용 가능한 스피커 목록을 반환합니다."""
        if self.cosyvoice:
            return self.cosyvoice.list_available_spks()
        return list(self.speaker_map.keys())


# 오디오 유틸리티 함수들
def mix_audio_files(audio_paths: List[str], output_path: str) -> str:
    """여러 오디오 파일을 믹싱(동시 재생)합니다."""
    from pydub import AudioSegment

    if not audio_paths:
        raise ValueError("믹싱할 오디오 파일이 없습니다.")

    mixed = AudioSegment.from_file(audio_paths[0])
    for audio_path in audio_paths[1:]:
        audio = AudioSegment.from_file(audio_path)
        mixed = mixed.overlay(audio)

    mixed.export(output_path, format="wav")
    logger.info(f"오디오 믹싱 완료: {len(audio_paths)}개 -> {output_path}")
    return output_path


def concatenate_audio_files(audio_paths: List[str], output_path: str) -> str:
    """여러 오디오 파일을 순서대로 이어붙입니다."""
    from pydub import AudioSegment

    if not audio_paths:
        raise ValueError("이어붙일 오디오 파일이 없습니다.")

    combined = AudioSegment.from_file(audio_paths[0])
    for audio_path in audio_paths[1:]:
        audio = AudioSegment.from_file(audio_path)
        combined = combined + audio

    combined.export(output_path, format="wav")
    logger.info(f"오디오 이어붙이기 완료: {len(audio_paths)}개 -> {output_path}")
    return output_path
