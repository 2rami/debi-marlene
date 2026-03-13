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
        Discord 이모지 문자열 (예: "<:char_jackie:123456>") 또는 빈 문자열
    """
    # Application Emoji 이름은 char_{key.lower()} 형식
    emoji_name = f"char_{character_key.lower()}"
    return EMOJI_MAP.get(emoji_name, "")


def get_tier_emoji(tier_id: int) -> str:
    """
    티어 이모지 가져오기

    Args:
        tier_id: 티어 ID (예: 63)

    Returns:
        Discord 이모지 문자열 (예: "<:tier_63:123456>") 또는 빈 문자열
    """
    emoji_name = f"tier_{tier_id}"
    return EMOJI_MAP.get(emoji_name, "")


def get_weapon_emoji(weapon_key: str) -> str:
    """
    무기 이모지 가져오기

    Args:
        weapon_key: 무기의 영어 key (예: "Whip", "Axe")

    Returns:
        Discord 이모지 문자열
    """
    # 여러 네이밍 포맷 시도: weapon_whip, Whip, whip
    for name in [f"weapon_{weapon_key.lower()}", weapon_key, weapon_key.lower()]:
        emoji = EMOJI_MAP.get(name)
        if emoji:
            return emoji
    return ""


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
        tactical_skill_key: 전술 스킬 key (예: "tactical_30")

    Returns:
        Discord 이모지 문자열 또는 빈 문자열
    """
    # tactical_{id} 형식 또는 raw key 시도
    emoji = EMOJI_MAP.get(tactical_skill_key)
    if emoji:
        return emoji
    # 소문자 시도
    return EMOJI_MAP.get(tactical_skill_key.lower(), "")

def get_weapon_skill_emoji(wskill_id: int) -> str:
    """
    무기스킬 이모지 가져오기

    Args:
        wskill_id: 무기스킬 ID (예: 101, 111, 191)

    Returns:
        Discord 이모지 문자열 또는 빈 문자열
    """
    emoji_name = f"wskill_{wskill_id}"
    return EMOJI_MAP.get(emoji_name, "")


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
            total_added += await self._update_weapon_emojis(existing_emojis)
            total_added += await self._update_tier_emojis(existing_emojis)
            total_added += await self._update_tactical_skill_emojis(existing_emojis)
            total_added += await self._update_weapon_skill_emojis(existing_emojis)

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
        """태스크 시작 전 봇이 준비될 때까지 대기 + 초기 이모지 체크"""
        await self.bot.wait_until_ready()

        # 봇 시작 시 한 번 빠진 이모지 체크/업로드
        try:
            self.application_id = self.bot.application_id
            if not self.application_id:
                return
            existing = await self._get_existing_emojis()
            total = 0
            total += await self._update_weapon_emojis(existing)
            total += await self._update_tier_emojis(existing)
            total += await self._update_tactical_skill_emojis(existing)
            total += await self._update_weapon_skill_emojis(existing)
            if total > 0:
                logger.info(f"시작 시 이모지 {total}개 업로드 완료")
                await load_emoji_map(self.bot)
        except Exception as e:
            logger.error(f"시작 시 이모지 체크 오류: {e}")

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

    async def _update_weapon_emojis(self, existing: Set[str]) -> int:
        """무기(마스터리) 이모지 업데이트"""
        logger.info("무기 이모지 체크 중...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.dak_api_base}/masteries?hl=ko') as response:
                    if response.status != 200:
                        logger.error(f"무기 API 요청 실패: {response.status}")
                        return 0

                    data = await response.json()
                    masteries = data.get('masteries', [])

                    new_weapons = []
                    for m in masteries:
                        key = m.get('key', '').lower()
                        if not key:
                            continue
                        emoji_name = f"weapon_{key}"
                        if emoji_name not in existing:
                            icon_url = m.get('iconUrl', '')
                            if icon_url:
                                new_weapons.append({
                                    'key': key,
                                    'name': m.get('name', 'Unknown'),
                                    'url': icon_url
                                })

                    if not new_weapons:
                        logger.info("  새로운 무기 없음")
                        return 0

                    logger.info(f"  새로운 무기 {len(new_weapons)}개 발견!")
                    added_count = 0
                    for w in new_weapons:
                        emoji_name = f"weapon_{w['key']}"
                        success = await self._download_resize_upload(
                            session, w['url'], emoji_name, 128, 128
                        )
                        if success:
                            added_count += 1
                            logger.info(f"  [+] {emoji_name} ({w['name']})")
                        else:
                            logger.warning(f"  [!] {emoji_name} 업로드 실패")
                        await asyncio.sleep(0.5)

                    return added_count

        except Exception as e:
            logger.error(f"무기 이모지 업데이트 오류: {e}")
            return 0

    async def _update_tier_emojis(self, existing: Set[str]) -> int:
        """티어 이모지 업데이트"""
        logger.info("티어 이모지 체크 중...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.dak_api_base}/tiers?hl=ko') as response:
                    if response.status != 200:
                        logger.error(f"티어 API 요청 실패: {response.status}")
                        return 0

                    data = await response.json()
                    tiers = data.get('tiers', [])

                    new_tiers = []
                    for t in tiers:
                        tier_id = t.get('id')
                        if tier_id is None:
                            continue
                        emoji_name = f"tier_{tier_id}"
                        if emoji_name not in existing:
                            image_url = t.get('imageUrl', '')
                            if image_url:
                                new_tiers.append({
                                    'id': tier_id,
                                    'name': t.get('name', 'Unknown'),
                                    'url': image_url
                                })

                    if not new_tiers:
                        logger.info("  새로운 티어 없음")
                        return 0

                    logger.info(f"  새로운 티어 {len(new_tiers)}개 발견!")
                    added_count = 0
                    for t in new_tiers:
                        emoji_name = f"tier_{t['id']}"
                        success = await self._download_resize_upload(
                            session, t['url'], emoji_name, 128, 128
                        )
                        if success:
                            added_count += 1
                            logger.info(f"  [+] {emoji_name} ({t['name']})")
                        else:
                            logger.warning(f"  [!] {emoji_name} 업로드 실패")
                        await asyncio.sleep(0.5)

                    return added_count

        except Exception as e:
            logger.error(f"티어 이모지 업데이트 오류: {e}")
            return 0

    async def _update_tactical_skill_emojis(self, existing: Set[str]) -> int:
        """전술스킬 이모지 업데이트"""
        logger.info("전술스킬 이모지 체크 중...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.dak_api_base}/tactical-skills?hl=ko') as response:
                    if response.status != 200:
                        logger.error(f"전술스킬 API 요청 실패: {response.status}")
                        return 0

                    data = await response.json()
                    skills = data.get('tacticalSkills', [])

                    new_skills = []
                    for s in skills:
                        skill_id = s.get('id')
                        if skill_id is None:
                            continue
                        emoji_name = f"tactical_{skill_id}"
                        if emoji_name not in existing:
                            icon_url = s.get('iconUrl', '')
                            if icon_url:
                                new_skills.append({
                                    'id': skill_id,
                                    'name': s.get('name', 'Unknown'),
                                    'url': icon_url
                                })

                    if not new_skills:
                        logger.info("  새로운 전술스킬 없음")
                        return 0

                    logger.info(f"  새로운 전술스킬 {len(new_skills)}개 발견!")
                    added_count = 0
                    for s in new_skills:
                        emoji_name = f"tactical_{s['id']}"
                        success = await self._download_resize_upload(
                            session, s['url'], emoji_name, 128, 128
                        )
                        if success:
                            added_count += 1
                            logger.info(f"  [+] {emoji_name} ({s['name']})")
                        else:
                            logger.warning(f"  [!] {emoji_name} 업로드 실패")
                        await asyncio.sleep(0.5)

                    return added_count

        except Exception as e:
            logger.error(f"전술스킬 이모지 업데이트 오류: {e}")
            return 0

    async def _update_weapon_skill_emojis(self, existing: Set[str]) -> int:
        """무기스킬 이모지 업데이트 (CDN에서 WSkillIcon_{id}.png)"""
        logger.info("무기스킬 이모지 체크 중...")

        # 알려진 무기스킬 ID 목록
        wskill_ids = [101, 111, 112, 113, 114, 115, 116, 117, 181, 191, 192, 193, 194, 198, 199]
        cdn_base = "https://cdn.dak.gg/assets/er/game-assets/10.4.0"

        new_skills = []
        for wid in wskill_ids:
            emoji_name = f"wskill_{wid}"
            if emoji_name not in existing:
                new_skills.append(wid)

        if not new_skills:
            logger.info("  새로운 무기스킬 없음")
            return 0

        logger.info(f"  새로운 무기스킬 {len(new_skills)}개 발견!")
        added_count = 0
        try:
            async with aiohttp.ClientSession() as session:
                for wid in new_skills:
                    emoji_name = f"wskill_{wid}"
                    url = f"{cdn_base}/WSkillIcon_{wid}.png"
                    success = await self._download_resize_upload(
                        session, url, emoji_name, 128, 128
                    )
                    if success:
                        added_count += 1
                        logger.info(f"  [+] {emoji_name}")
                    else:
                        logger.warning(f"  [!] {emoji_name} 업로드 실패")
                    await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"무기스킬 이모지 업데이트 오류: {e}")

        return added_count

    async def _get_existing_emojis_with_ids(self) -> Dict[str, str]:
        """현재 Discord에 등록된 이모지 {이름: ID} 딕셔너리 반환"""
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
                        return {e['name']: e['id'] for e in data.get('items', [])}
                    return {}
        except Exception:
            return {}

    async def _delete_emoji(self, session: aiohttp.ClientSession, emoji_id: str) -> bool:
        """Discord Application Emoji 삭제"""
        try:
            headers = {
                'Authorization': f'Bot {self.bot.http.token}',
            }
            async with session.delete(
                f'{self.base_url}/applications/{self.application_id}/emojis/{emoji_id}',
                headers=headers
            ) as response:
                return response.status == 204
        except Exception:
            return False

    async def force_reupload_all(self):
        """Application Emoji만 삭제 후 재업로드 (비율 보존 리사이즈 적용)

        주의: /applications/{app_id}/emojis API만 사용 — 서버(길드) 이모지는 건드리지 않음.
        """
        self.application_id = self.bot.application_id
        if not self.application_id:
            logger.error("Application ID가 없어 재업로드를 중단합니다.")
            return

        logger.info("=" * 60)
        logger.info("Application Emoji 전체 재업로드 시작")
        logger.info(f"대상: /applications/{self.application_id}/emojis (서버 이모지 아님)")
        logger.info("=" * 60)

        # 1. 기존 Application Emoji 전부 삭제
        existing = await self._get_existing_emojis_with_ids()
        logger.info(f"Application Emoji {len(existing)}개 삭제 시작...")

        async with aiohttp.ClientSession() as session:
            for name, eid in existing.items():
                success = await self._delete_emoji(session, eid)
                if success:
                    logger.info(f"  [-] {name} 삭제")
                else:
                    logger.warning(f"  [!] {name} 삭제 실패")
                await asyncio.sleep(0.3)

        logger.info("Application Emoji 삭제 완료. 재업로드 시작...")

        # 2. 전부 새로 업로드 (빈 set = 모두 새로운 것으로 처리)
        empty_set: Set[str] = set()
        total = 0
        total += await self._update_character_emojis(empty_set)
        total += await self._update_skin_emojis(empty_set)
        total += await self._update_item_emojis(empty_set)
        total += await self._update_weapon_emojis(empty_set)
        total += await self._update_tier_emojis(empty_set)
        total += await self._update_tactical_skill_emojis(empty_set)
        total += await self._update_weapon_skill_emojis(empty_set)

        logger.info("=" * 60)
        logger.info(f"이모지 전체 재업로드 완료! 총 {total}개 업로드")
        logger.info("=" * 60)

        # 이모지 맵 재로드
        await load_emoji_map(self.bot)

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

            # 2. 리사이즈 (비율 유지, 투명 패딩)
            img = Image.open(BytesIO(image_data))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 비율 유지하면서 128x128 안에 맞추기
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            # 투명 캔버스에 중앙 배치
            canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            x = (width - img.width) // 2
            y = (height - img.height) // 2
            canvas.paste(img, (x, y))
            img_resized = canvas

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
