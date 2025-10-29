"""
이모지 유틸리티

Discord 서버의 커스텀 이모지를 관리하고 사용하는 함수들입니다.
"""
import json
from pathlib import Path
from typing import Dict, Optional

# 이모지 맵 저장
EMOJI_MAP: Dict[str, str] = {}
EMOJI_MAP_FILE = Path(__file__).parent.parent / "emoji_map.json"


async def load_emoji_map(bot):
    """
    봇이 속한 서버들의 모든 이모지와 Application Emojis를 가져와서 맵을 만듭니다.

    파일명 -> 이모지 ID 매핑:
    - 캐릭터: Jackie.png -> Jackie
    - 무기: Whip.png -> Whip
    - 특성: 7000201.png -> 7000201
    - 아이템: 101101.png -> 101101
    """
    global EMOJI_MAP
    EMOJI_MAP = {}

    emoji_count = 0

    # 1. Application Emojis 수집 (HTTP API로 직접 가져오기)
    try:
        # bot.application_id를 사용해서 직접 API 호출
        app_id = bot.application_id
        if app_id:
            import aiohttp
            headers = {"Authorization": f"Bot {bot.http.token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://discord.com/api/v10/applications/{app_id}/emojis",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        app_emojis_data = await resp.json()
                        if 'items' in app_emojis_data:
                            for emoji_data in app_emojis_data['items']:
                                name = emoji_data['name']
                                emoji_id = emoji_data['id']
                                EMOJI_MAP[name] = f"<:{name}:{emoji_id}>"
                                emoji_count += 1
                        else:
                            print(f"[경고] Application Emojis가 없거나 응답 형식이 다릅니다: {list(app_emojis_data.keys())}")
                    else:
                        print(f"[경고] Application Emojis API 호출 실패: HTTP {resp.status}")
    except Exception as e:
        print(f"[경고] Application Emojis 로드 실패: {e}")
        import traceback
        traceback.print_exc()

    # 2. 모든 서버의 이모지 수집
    guild_emoji_count = 0
    for guild in bot.guilds:
        for emoji in guild.emojis:
            # 중복 방지: Application Emoji가 우선
            if emoji.name not in EMOJI_MAP:
                EMOJI_MAP[emoji.name] = f"<:{emoji.name}:{emoji.id}>"
                guild_emoji_count += 1

    total_count = emoji_count + guild_emoji_count
    print(f"[완료] 이모지 {total_count}개 로드 완료")


def get_character_emoji(character_key: str) -> str:
    """
    캐릭터 이모지 가져오기

    Args:
        character_key: 캐릭터의 영어 key (예: "Jackie", "Aya")

    Returns:
        Discord 이모지 문자열 (예: "<:Jackie:123456>") 또는 빈 문자열
    """
    return EMOJI_MAP.get(character_key, "")


def get_weapon_emoji(weapon_key: str) -> str:
    """
    무기 이모지 가져오기

    Args:
        weapon_key: 무기의 영어 key (예: "Whip", "Axe")

    Returns:
        Discord 이모지 문자열
    """
    return EMOJI_MAP.get(weapon_key, "")


def get_trait_emoji(trait_id: int) -> str:
    """
    특성 이모지 가져오기

    Args:
        trait_id: 특성 ID (예: 7000201)

    Returns:
        Discord 이모지 문자열
    """
    return EMOJI_MAP.get(str(trait_id), "")


def get_item_emoji(item_id: int) -> str:
    """
    아이템 이모지 가져오기

    Args:
        item_id: 아이템 ID (예: 101101)

    Returns:
        Discord 이모지 문자열
    """
    # Application Emoji 이름은 item_{item_id} 형식
    emoji_name = f"item_{item_id}"
    return EMOJI_MAP.get(emoji_name, "")

def get_tactical_skill_emoji(tactical_skill_key: str) -> str:
    """
    전술 스킬 이모지 가져오기

    Args:
        tactical_skill_key: 전술 스킬의 영어 key

    Returns:
        Discord 이모지 문자열 또는 빈 문자열
    """
    return EMOJI_MAP.get(tactical_skill_key, "")

def get_weather_emoji(weather_key: str) -> str:
    """
    날씨 이모지 가져오기

    Args:
        weather_key: 날씨의 영어 key

    Returns:
        Discord 이모지 문자열 또는 빈 문자열
    """
    return EMOJI_MAP.get(weather_key, "")
