"""
목소리 관리자: 미리 학습된 TTS 모델 관리

데비&마를렌 캐릭터의 미리 학습된 TTS 모델 경로를 관리합니다.
"""

import os
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class VoiceManager:
    """
    목소리 관리 클래스

    미리 학습된 캐릭터별 TTS 모델 경로를 관리합니다.
    """

    def __init__(self, models_dir: str = "assets/models"):
        """
        목소리 관리자 초기화

        Args:
            models_dir: TTS 모델 파일이 저장된 디렉토리 경로
        """
        self.models_dir = models_dir

        # 모델 디렉토리 생성 (없으면)
        os.makedirs(self.models_dir, exist_ok=True)

        # 파인튜닝된 모델 경로
        self.finetuned_model_path = os.path.join(self.models_dir, "debi_marlene_finetuned")

    def get_finetuned_model_path(self) -> Optional[str]:
        """
        파인튜닝된 모델 경로를 반환합니다.

        Returns:
            모델 경로 (없으면 None)
        """
        if os.path.exists(self.finetuned_model_path):
            return self.finetuned_model_path
        return None

    def has_finetuned_model(self) -> bool:
        """파인튜닝된 모델이 있는지 확인합니다."""
        return self.get_finetuned_model_path() is not None
