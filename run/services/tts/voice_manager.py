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

        # 캐릭터별 모델 경로
        # 각 캐릭터 폴더에 model.pth와 config.json이 있어야 함
        self.character_models = {
            "debi": os.path.join(self.models_dir, "debi"),
            "marlene": os.path.join(self.models_dir, "marlene"),
            "default": os.path.join(self.models_dir, "default")
        }

    def get_model_paths(
        self,
        character: str = "default"
    ) -> Optional[Tuple[str, str]]:
        """
        캐릭터의 TTS 모델 파일 경로를 가져옵니다.

        Args:
            character: 캐릭터 이름 ("debi", "marlene", "default")

        Returns:
            (model_path, config_path) 튜플 (없으면 None)
        """
        model_dir = self.character_models.get(character)

        if not model_dir:
            logger.warning(f"알 수 없는 캐릭터: {character}")
            return None

        model_path = os.path.join(model_dir, "model.pth")
        config_path = os.path.join(model_dir, "config.json")

        # 둘 다 존재하는지 확인
        if os.path.exists(model_path) and os.path.exists(config_path):
            logger.info(f"캐릭터 모델 발견: {character} -> {model_dir}")
            return (model_path, config_path)
        else:
            logger.info(f"캐릭터 모델이 없습니다: {character}")
            return None

    def has_model(self, character: str = "default") -> bool:
        """
        캐릭터의 TTS 모델이 존재하는지 확인합니다.

        Args:
            character: 캐릭터 이름

        Returns:
            모델 존재 여부
        """
        return self.get_model_paths(character) is not None

    def list_available_characters(self) -> Dict[str, bool]:
        """
        사용 가능한 캐릭터 목록을 반환합니다.

        Returns:
            {캐릭터명: 모델존재여부} 딕셔너리
        """
        return {
            char: self.has_model(char)
            for char in self.character_models.keys()
        }
