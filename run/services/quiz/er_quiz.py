"""
이터널리턴 퀴즈 문제 생성

game_data 캐시를 활용하여 다양한 유형의 4지선다 문제를 생성합니다.
"""

import random
import logging
from dataclasses import dataclass
from typing import Optional, List

from run.services.eternal_return.api_client import game_data

logger = logging.getLogger(__name__)


@dataclass
class ERQuestion:
    """이터널리턴 퀴즈 문제"""
    question_text: str
    choices: List[str]  # 4개 선택지
    correct_index: int  # 정답 인덱스 (0-3)
    image_url: Optional[str] = None

    @property
    def correct_answer(self) -> str:
        return self.choices[self.correct_index]


def _pick_wrong_answers(correct: str, pool: list, count: int = 3) -> list:
    """정답을 제외한 오답 선택지를 뽑습니다."""
    candidates = [x for x in pool if x != correct]
    if len(candidates) < count:
        return candidates
    return random.sample(candidates, count)


def _shuffle_choices(correct: str, wrongs: list) -> tuple:
    """정답과 오답을 섞어서 선택지와 정답 인덱스를 반환합니다."""
    choices = [correct] + wrongs
    random.shuffle(choices)
    correct_index = choices.index(correct)
    return choices, correct_index


def _generate_character_image_question() -> Optional[ERQuestion]:
    """실험체 이미지 보고 이름 맞추기"""
    if not game_data.characters:
        return None

    # 스킨이 있는 캐릭터만 선택
    chars_with_skins = []
    for char_id, char_info in game_data.characters.items():
        skins = char_info.get('skins', [])
        if skins:
            chars_with_skins.append((char_id, char_info))

    if len(chars_with_skins) < 4:
        return None

    # 정답 캐릭터 선택
    correct_id, correct_info = random.choice(chars_with_skins)
    correct_name = correct_info['name']

    # 스킨 이미지 가져오기
    skins = correct_info.get('skins', [])
    skin = random.choice(skins)
    image_url = game_data.get_skin_image_url(skin.get('id'))

    # 오답 생성
    all_names = [info['name'] for _, info in chars_with_skins]
    wrongs = _pick_wrong_answers(correct_name, all_names)
    if len(wrongs) < 3:
        return None

    choices, correct_index = _shuffle_choices(correct_name, wrongs)

    return ERQuestion(
        question_text="이 실험체의 이름은?",
        choices=choices,
        correct_index=correct_index,
        image_url=image_url,
    )


def _generate_weapon_image_question() -> Optional[ERQuestion]:
    """무기 이미지 보고 이름 맞추기"""
    if len(game_data.masteries) < 4:
        return None

    items = list(game_data.masteries.items())
    correct_id, correct_info = random.choice(items)
    correct_name = correct_info.get('name', '')
    if not correct_name:
        return None

    image_url = game_data.get_weapon_image_url(correct_id)

    all_names = [info.get('name', '') for _, info in items if info.get('name')]
    wrongs = _pick_wrong_answers(correct_name, all_names)
    if len(wrongs) < 3:
        return None

    choices, correct_index = _shuffle_choices(correct_name, wrongs)

    return ERQuestion(
        question_text="이 무기의 이름은?",
        choices=choices,
        correct_index=correct_index,
        image_url=image_url,
    )


def _generate_item_grade_question() -> Optional[ERQuestion]:
    """아이템 이미지 보고 등급 맞추기"""
    if len(game_data.items) < 4:
        return None

    # 등급이 있는 아이템만
    graded_items = [
        (item_id, info) for item_id, info in game_data.items.items()
        if info.get('grade') and info.get('name')
    ]
    if len(graded_items) < 4:
        return None

    correct_id, correct_info = random.choice(graded_items)
    correct_grade = game_data.get_item_grade(correct_id)
    item_name = correct_info.get('name', '')
    image_url = game_data.get_item_image_url(correct_id)

    all_grades = ['일반', '고급', '희귀', '영웅', '전설', '신화']
    wrongs = _pick_wrong_answers(correct_grade, all_grades)
    if len(wrongs) < 3:
        return None

    choices, correct_index = _shuffle_choices(correct_grade, wrongs)

    return ERQuestion(
        question_text=f"'{item_name}'의 등급은?",
        choices=choices,
        correct_index=correct_index,
        image_url=image_url,
    )


def _generate_trait_image_question() -> Optional[ERQuestion]:
    """특성 이미지 보고 이름 맞추기"""
    if len(game_data.trait_skills) < 4:
        return None

    items = [(tid, info) for tid, info in game_data.trait_skills.items() if info.get('name')]
    if len(items) < 4:
        return None

    correct_id, correct_info = random.choice(items)
    correct_name = correct_info['name']
    image_url = game_data.get_trait_image_url(correct_id)

    all_names = [info['name'] for _, info in items]
    wrongs = _pick_wrong_answers(correct_name, all_names)
    if len(wrongs) < 3:
        return None

    choices, correct_index = _shuffle_choices(correct_name, wrongs)

    return ERQuestion(
        question_text="이 특성의 이름은?",
        choices=choices,
        correct_index=correct_index,
        image_url=image_url,
    )


# 문제 생성 함수 목록
_GENERATORS = [
    _generate_character_image_question,
    _generate_weapon_image_question,
    _generate_item_grade_question,
    _generate_trait_image_question,
]


def generate_er_question() -> Optional[ERQuestion]:
    """랜덤 유형의 ER 퀴즈 문제를 생성합니다."""
    # 셔플해서 순서대로 시도 (실패하면 다음 유형)
    generators = _GENERATORS.copy()
    random.shuffle(generators)

    for gen in generators:
        try:
            question = gen()
            if question:
                return question
        except Exception as e:
            logger.error(f"ER 퀴즈 문제 생성 실패: {e}")
            continue

    logger.error("모든 ER 퀴즈 문제 생성 실패")
    return None
