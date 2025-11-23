"""
Coqui TTS 서비스: XTTS v2를 사용한 음성 합성 (파인튜닝 모델 지원)
"""

import os
import torch
import logging
from TTS.api import TTS
from typing import Optional

# 라이선스 동의
os.environ["COQUI_TOS_AGREED"] = "1"

logger = logging.getLogger(__name__)

class CoquiTTSService:
    """
    Coqui TTS (XTTS v2) 서비스 클래스
    """

    def __init__(self, model_path: Optional[str] = None, config_path: Optional[str] = None, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        """
        Coqui TTS 서비스 초기화

        Args:
            model_path: 파인튜닝된 모델 경로 (폴더)
            config_path: 설정 파일 경로 (사용 안 함, model_path에 포함됨)
            device: 실행할 디바이스 ('cuda' 또는 'cpu')
        """
        self.device = device
        self.tts: Optional[TTS] = None
        self.model_path = model_path
        self.temp_dir = "/tmp/tts_audio"
        
        # 임시 파일 저장 폴더 생성
        os.makedirs(self.temp_dir, exist_ok=True)

    async def initialize(self):
        """
        TTS 모델을 로드합니다.
        """
        if self.tts is None:
            logger.info(f"Coqui TTS 모델 로딩 시작 ({self.device})...")
            try:
                if self.model_path and os.path.exists(self.model_path):
                    logger.info(f"파인튜닝된 모델 로드: {self.model_path}")
                    # 로컬 모델 로드
                    self.tts = TTS(model_path=self.model_path, config_path=os.path.join(self.model_path, "config.json")).to(self.device)
                else:
                    logger.info("기본 XTTS v2 모델 로드")
                    self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
                
                logger.info("Coqui TTS 모델 로딩 완료")
            except Exception as e:
                logger.error(f"Coqui TTS 모델 로딩 실패: {e}")
                raise

    async def text_to_speech(
        self,
        text: str,
        speaker: str,
        language: str = "ko",
        output_path: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환합니다.

        Args:
            text: 변환할 텍스트
            speaker: 화자 이름 (학습된 모델의 화자명)
            language: 언어 코드
            output_path: 저장할 파일 경로

        Returns:
            생성된 음성 파일의 경로
        """
        if self.tts is None:
            await self.initialize()

        # 출력 파일 경로 생성
        if output_path is None:
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"xtts_{text_hash}.wav")

        try:
            logger.info(f"TTS 변환 시작: '{text}' (화자: {speaker})")
            
            # TTS 실행
            self.tts.tts_to_file(
                text=text,
                speaker=speaker,
                language=language,
                file_path=output_path
            )
            
            logger.info(f"TTS 변환 완료: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"TTS 변환 실패: {e}")
            raise

    def cleanup_temp_files(self):
        """임시 음성 파일들을 정리합니다."""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            logger.info("TTS 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")
