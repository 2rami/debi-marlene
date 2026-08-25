"""이터널리턴 캐릭터 이미지 생성.

참조 이미지(게임 스킨 아트)를 함께 보내 캐릭터 정체성을 붙잡고, 배경·포즈만 새로
그리게 한다. 범용 모델은 이 게임 캐릭터를 모르므로 참조 없이는 닮은 그림이 안 나온다.
"""

from run.services.imagegen.characters import (
    get_character_list,
    search_characters,
    get_reference_image,
)
from run.services.imagegen.gateway import generate_image, ImageGenError

__all__ = [
    'get_character_list',
    'search_characters',
    'get_reference_image',
    'generate_image',
    'ImageGenError',
]
