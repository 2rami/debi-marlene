"""
이모지 유틸리티

Discord 서버의 커스텀 이모지를 관리하고 사용하는 함수들입니다.
"""
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

def get_skin_emoji(skin_id: int) -> str:
    """
    스킨 이모지 가져오기

    Args:
        skin_id: 스킨 ID (예: 1001001)

    Returns:
        Discord 이모지 문자열 또는 빈 문자열
    """
    # Application Emoji 이름은 skin_{skin_id} 형식
    emoji_name = f"skin_{skin_id}"
    return EMOJI_MAP.get(emoji_name, "")


# ========== 이모지 자동 업데이트 ==========

import asyncio
import aiohttp
import base64
import logging
from datetime import time, datetime
from PIL import Image
from io import BytesIO
from discord.ext import tasks
from typing import Set

logger = logging.getLogger(__name__)


class EmojiAutoUpdater:
    """
    이모지 자동 업데이트 관리 클래스

    매주 목요일 오후 5시에 dak.gg API를 체크하여
    새로운 아이템/캐릭터/스킨 이모지를 자동으로 Discord에 업로드합니다.
    """

    def __init__(self, bot):
        self.bot = bot
        self.application_id: Optional[str] = None
        self.base_url = 'https://discord.com/api/v10'
        self.dak_api_base = 'https://er.dakgg.io/api/v1/data'

        # 업데이트 태스크 시작
        self.weekly_update.start()
        logger.info("이모지 자동 업데이트 서비스 시작됨 (매주 목요일 오후 5시)")

    def cog_unload(self):
        """봇 종료 시 태스크 정리"""
        self.weekly_update.cancel()

    @tasks.loop(time=time(hour=17, minute=0))  # 매일 오후 5시에 실행
    async def weekly_update(self):
        """매주 목요일 오후 5시에 이모지 업데이트 체크"""
        try:
            # 목요일(3)인지 체크
            if datetime.now().weekday() != 3:
                return

            logger.info("=" * 60)
            logger.info("이모지 자동 업데이트 시작 (목요일 오후 5시)")
            logger.info("=" * 60)

            # Application ID 가져오기
            self.application_id = self.bot.application_id
            if not self.application_id:
                logger.error("Application ID가 없어 업데이트를 중단합니다.")
                return

            # 기존 이모지 목록 가져오기
            existing_emojis = await self._get_existing_emojis()
            logger.info(f"현재 Discord 이모지 개수: {len(existing_emojis)}개")

            # 각 타입별 업데이트
            total_added = 0
            total_added += await self._update_item_emojis(existing_emojis)
            total_added += await self._update_character_emojis(existing_emojis)
            total_added += await self._update_skin_emojis(existing_emojis)

            logger.info("=" * 60)
            logger.info(f"이모지 자동 업데이트 완료! 총 {total_added}개 추가됨")
            logger.info("=" * 60)

            # 이모지 맵 재로드
            if total_added > 0:
                await load_emoji_map(self.bot)
                logger.info("이모지 맵 재로드 완료")

        except Exception as e:
            logger.error(f"이모지 자동 업데이트 중 오류 발생: {e}", exc_info=True)

    @weekly_update.before_loop
    async def before_weekly_update(self):
        """태스크 시작 전 봇이 준비될 때까지 대기"""
        await self.bot.wait_until_ready()

    async def _get_existing_emojis(self) -> Set[str]:
        """현재 Discord에 등록된 이모지 이름 목록 가져오기"""
        try:
            headers = {
                'Authorization': f'Bot {self.bot.http.token}',
                'Content-Type': 'application/json'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.base_url}/applications/{self.application_id}/emojis',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        emojis = data.get('items', [])
                        return {emoji['name'] for emoji in emojis}
                    else:
                        logger.error(f"이모지 목록 가져오기 실패: {response.status}")
                        return set()
        except Exception as e:
            logger.error(f"이모지 목록 가져오기 오류: {e}")
            return set()

    async def _update_item_emojis(self, existing: Set[str]) -> int:
        """아이템 이모지 업데이트"""
        logger.info("아이템 이모지 체크 중...")

        try:
            async with aiohttp.ClientSession() as session:
                # API에서 아이템 데이터 가져오기
                async with session.get(f'{self.dak_api_base}/items?hl=ko') as response:
                    if response.status != 200:
                        logger.error(f"아이템 API 요청 실패: {response.status}")
                        return 0

                    data = await response.json()
                    items = data.get('items', [])

                    # 새로운 아이템 필터링
                    new_items = []
                    for item in items:
                        item_code = item.get('code')
                        emoji_name = f"item_{item_code}"

                        if emoji_name not in existing:
                            new_items.append({
                                'code': item_code,
                                'name': item.get('name', 'Unknown'),
                                'url': item.get('imageUrl', '')
                            })

                    if not new_items:
                        logger.info("  새로운 아이템 없음")
                        return 0

                    logger.info(f"  새로운 아이템 {len(new_items)}개 발견!")

                    # 다운로드 + 업로드
                    added_count = 0
                    for item in new_items:
                        emoji_name = f"item_{item['code']}"
                        success = await self._download_resize_upload(
                            session, item['url'], emoji_name, 128, 128
                        )
                        if success:
                            added_count += 1
                            logger.info(f"  [+] {emoji_name} ({item['name']})")
                        else:
                            logger.warning(f"  [!] {emoji_name} 업로드 실패")

                        # Rate limit 방지
                        await asyncio.sleep(0.5)

                    return added_count

        except Exception as e:
            logger.error(f"아이템 이모지 업데이트 오류: {e}")
            return 0

    async def _update_character_emojis(self, existing: Set[str]) -> int:
        """캐릭터 이모지 업데이트"""
        logger.info("캐릭터 이모지 체크 중...")

        try:
            async with aiohttp.ClientSession() as session:
                # API에서 캐릭터 데이터 가져오기
                async with session.get(f'{self.dak_api_base}/characters?hl=ko') as response:
                    if response.status != 200:
                        logger.error(f"캐릭터 API 요청 실패: {response.status}")
                        return 0

                    data = await response.json()
                    characters = data.get('characters', [])

                    # 새로운 캐릭터 필터링
                    new_chars = []
                    for char in characters:
                        char_key = char.get('key', '').lower()
                        emoji_name = f"char_{char_key}"

                        if emoji_name not in existing:
                            new_chars.append({
                                'key': char_key,
                                'name': char.get('name', 'Unknown'),
                                'url': char.get('imageUrl', '')
                            })

                    if not new_chars:
                        logger.info("  새로운 캐릭터 없음")
                        return 0

                    logger.info(f"  새로운 캐릭터 {len(new_chars)}개 발견!")

                    # 다운로드 + 업로드
                    added_count = 0
                    for char in new_chars:
                        emoji_name = f"char_{char['key']}"
                        success = await self._download_resize_upload(
                            session, char['url'], emoji_name, 128, 128
                        )
                        if success:
                            added_count += 1
                            logger.info(f"  [+] {emoji_name} ({char['name']})")
                        else:
                            logger.warning(f"  [!] {emoji_name} 업로드 실패")

                        # Rate limit 방지
                        await asyncio.sleep(0.5)

                    return added_count

        except Exception as e:
            logger.error(f"캐릭터 이모지 업데이트 오류: {e}")
            return 0

    async def _update_skin_emojis(self, existing: Set[str]) -> int:
        """스킨 이모지 업데이트"""
        logger.info("스킨 이모지 체크 중...")

        try:
            async with aiohttp.ClientSession() as session:
                # API에서 캐릭터 데이터 가져오기 (스킨 포함)
                async with session.get(f'{self.dak_api_base}/characters?hl=ko') as response:
                    if response.status != 200:
                        logger.error(f"스킨 API 요청 실패: {response.status}")
                        return 0

                    data = await response.json()
                    characters = data.get('characters', [])

                    # 새로운 스킨 필터링 (grade != 1)
                    new_skins = []
                    for char in characters:
                        char_name = char.get('name', 'Unknown')
                        skins = char.get('skins', [])

                        for skin in skins:
                            if skin.get('grade') != 1:  # 기본 스킨 제외
                                skin_id = skin.get('id')
                                emoji_name = f"skin_{skin_id}"

                                if emoji_name not in existing:
                                    new_skins.append({
                                        'id': skin_id,
                                        'name': skin.get('name', 'Unknown'),
                                        'char_name': char_name,
                                        'url': skin.get('imageUrl', '')
                                    })

                    if not new_skins:
                        logger.info("  새로운 스킨 없음")
                        return 0

                    logger.info(f"  새로운 스킨 {len(new_skins)}개 발견!")

                    # 다운로드 + 업로드
                    added_count = 0
                    for skin in new_skins:
                        emoji_name = f"skin_{skin['id']}"
                        success = await self._download_resize_upload(
                            session, skin['url'], emoji_name, 128, 128
                        )
                        if success:
                            added_count += 1
                            logger.info(f"  [+] {emoji_name} ({skin['char_name']} - {skin['name']})")
                        else:
                            logger.warning(f"  [!] {emoji_name} 업로드 실패")

                        # Rate limit 방지
                        await asyncio.sleep(0.5)

                    return added_count

        except Exception as e:
            logger.error(f"스킨 이모지 업데이트 오류: {e}")
            return 0

    async def _download_resize_upload(
        self, session: aiohttp.ClientSession, url: str, emoji_name: str,
        width: int, height: int
    ) -> bool:
        """이미지 다운로드 -> 리사이즈 -> Discord 업로드"""
        try:
            # URL 처리
            if url.startswith('//'):
                url = f"https:{url}"

            # 1. 다운로드
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    return False
                image_data = await response.read()

            # 2. 리사이즈
            img = Image.open(BytesIO(image_data))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 128x128로 강제 리사이즈
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)

            # PNG로 인코딩
            output = BytesIO()
            img_resized.save(output, 'PNG', optimize=True)
            png_data = output.getvalue()

            # 3. Base64 인코딩
            base64_data = base64.b64encode(png_data).decode('utf-8')
            data_uri = f"data:image/png;base64,{base64_data}"

            # 4. Discord 업로드
            headers = {
                'Authorization': f'Bot {self.bot.http.token}',
                'Content-Type': 'application/json'
            }

            payload = {
                "name": emoji_name,
                "image": data_uri
            }

            async with session.post(
                f'{self.base_url}/applications/{self.application_id}/emojis',
                headers=headers,
                json=payload
            ) as response:
                return response.status == 201

        except Exception as e:
            logger.error(f"이미지 처리 오류 ({emoji_name}): {e}")
            return False
