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

# 무기 mastery ID → WSkillIcon CDN ID 매핑
# mastery ID는 API(/data/masteries)의 id, WSkillIcon은 CDN 파일명의 숫자
WEAPON_SKILL_MAP = {
    1: 101,    # Glove (글러브) → 어퍼컷
    4: 113,    # Whip (채찍) → 바람가르기
    6: 117,    # DirectFire (암기) → 마름쇠
    7: 112,    # Bow (활) → 곡사
    13: 111,   # Hammer (망치) → 갑옷깨기
    14: 114,   # Axe (도끼) → 피의 나선
    15: 115,   # OneHandSword (단검) → 망토와 단검
    16: 116,   # TwoHandSword (양손검) → 빗겨 흘리기
    20: 191,   # Nunchaku (쌍절곤) → 맹룡과강
    21: 192,   # Rapier (레이피어) → 섬격
    22: 181,   # Guitar (기타) → Love&...
    23: 193,   # Camera (카메라) → 플래시
    24: 194,   # Arcana (아르카나) → VF 매개
    25: 198,   # VFArm (VF의수) → VF안정화
}
# CDN에 아이콘 없는 무기: Tonfa(2), Bat(3), HighAngleFire(5),
# CrossBow(8), Pistol(9), AssaultRifle(10), SniperRifle(11),
# DualSword(18), Spear(19)


def get_weapon_skill_emoji(mastery_id: int) -> str:
    """
    무기스킬 이모지 가져오기 (mastery ID → WSkillIcon ID 변환)

    Args:
        mastery_id: 무기 mastery ID (예: 1=Glove, 4=Whip, 13=Hammer)

    Returns:
        Discord 이모지 문자열 또는 빈 문자열
    """
    wskill_id = WEAPON_SKILL_MAP.get(mastery_id)
    if not wskill_id:
        return ""
    emoji_name = f"wskill_{wskill_id}"
    return EMOJI_MAP.get(emoji_name, "")


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


def get_weather_emoji(weather_id: int) -> str:
    """날씨 이모지 가져오기 (weather_{id} 형식)"""
    emoji_name = f"weather_{weather_id}"
    return EMOJI_MAP.get(emoji_name, "")


# ========== 이모지 자동 업데이트 ==========

import asyncio
import aiohttp
import base64
import logging
from datetime import time, datetime
from PIL import Image, ImageDraw
from io import BytesIO
from discord.ext import tasks
from typing import Set

# 아이템 등급별 배경 그라데이션 (하단 색상, 상단 색상) - dak.gg 소스 기준
GRADE_COLORS = {
    'Common':   ((0xA8, 0xAD, 0xB4), (0x67, 0x69, 0x6C)),  # 회색
    'Uncommon': ((0x69, 0xB7, 0x6F), (0x46, 0x6A, 0x49)),  # 초록
    'Rare':     ((0x63, 0x97, 0xE7), (0x34, 0x4A, 0x6C)),  # 파랑
    'Epic':     ((0x85, 0x69, 0xB3), (0x62, 0x47, 0x83)),  # 보라
    'Legend':   ((0xA9, 0x85, 0x29), (0x55, 0x43, 0x25)),  # 금색
    'Mythic':   ((0x81, 0x2D, 0x2E), (0x4A, 0x22, 0x22)),  # 빨강
}

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

        self.weekly_update.start()

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

            self.application_id = self.bot.application_id
            if not self.application_id:
                return

            existing_emojis = await self._get_existing_emojis()

            # 각 타입별 업데이트
            total_added = 0
            total_added += await self._update_item_emojis(existing_emojis)
            total_added += await self._update_character_emojis(existing_emojis)
            total_added += await self._update_skin_emojis(existing_emojis)
            total_added += await self._update_weapon_emojis(existing_emojis)
            total_added += await self._update_tier_emojis(existing_emojis)
            total_added += await self._update_tactical_skill_emojis(existing_emojis)
            total_added += await self._update_weapon_skill_emojis(existing_emojis)
            total_added += await self._update_weather_emojis(existing_emojis)

            if total_added > 0:
                await load_emoji_map(self.bot)
                print(f"[이모지] 주간 업데이트: {total_added}개 추가", flush=True)

        except Exception as e:
            logger.error(f"이모지 자동 업데이트 중 오류 발생: {e}", exc_info=True)

    @weekly_update.before_loop
    async def before_weekly_update(self):
        """태스크 시작 전 봇이 준비될 때까지 대기 + 초기 이모지 체크"""
        await self.bot.wait_until_ready()

        # 봇 시작 시 신규 이모지 체크
        try:
            self.application_id = self.bot.application_id
            if not self.application_id:
                return

            # [일회성] 아이템 이모지 전체 재업로드 (등급 그라데이션 배경 적용)
            await self._reupload_all_item_emojis_with_grades()

            existing = await self._get_existing_emojis()
            total = 0
            total += await self._update_item_emojis(existing)
            total += await self._update_character_emojis(existing)
            total += await self._update_weapon_emojis(existing)
            total += await self._update_tier_emojis(existing)
            total += await self._update_tactical_skill_emojis(existing)
            total += await self._update_weather_emojis(existing)
            if total > 0:
                print(f"[이모지] 신규 {total}개 업로드", flush=True)
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
        """아이템 이모지 업데이트 (공식 ER API - 완성템만, 등급 배경 포함)"""
        logger.info("아이템 이모지 체크 중...")
        cdn_base = "https://cdn.dak.gg/assets/er/game-assets/10.4.0"
        er_api_base = "https://open-api.bser.io/v1/data"
        er_api_headers = {"x-api-key": "wxIgXerGxj1xJ3r4z4xjoavjMUfh10Kw3pVtMasn"}

        try:
            new_items = []
            api_item_names = set()  # API에 있는 모든 완성템 이름
            async with aiohttp.ClientSession() as session:
                # 공식 ER API에서 무기 + 방어구 완성템 가져오기
                for endpoint in ['ItemWeapon', 'ItemArmor']:
                    async with session.get(
                        f'{er_api_base}/{endpoint}',
                        headers=er_api_headers
                    ) as response:
                        if response.status != 200:
                            logger.error(f"{endpoint} API 요청 실패: {response.status}")
                            continue
                        data = await response.json()
                        for item in data.get('data', []):
                            if not item.get('isCompletedItem'):
                                continue
                            code = item.get('code')
                            emoji_name = f"item_{code}"
                            api_item_names.add(emoji_name)
                            if emoji_name not in existing:
                                new_items.append({
                                    'code': code,
                                    'name': item.get('name', ''),
                                    'grade': item.get('itemGrade', ''),
                                    'url': f"{cdn_base}/ItemIcon_{code}.png"
                                })

                # 새 아이템 업로드
                added_count = 0
                if new_items:
                    print(f"[이모지] 새로운 아이템 {len(new_items)}개 발견!", flush=True)
                    for item in new_items:
                        emoji_name = f"item_{item['code']}"
                        success = await self._download_resize_upload(
                            session, item['url'], emoji_name, 128, 128,
                            grade=item.get('grade')
                        )
                        if success:
                            added_count += 1
                        else:
                            logger.warning(f"  [!] {emoji_name} 업로드 실패")
                        await asyncio.sleep(0.5)

                # Discord에 있지만 API에 없는 item_ 이모지 찾기
                existing_with_ids = await self._get_existing_emojis_with_ids()
                orphan_items = {
                    name: eid for name, eid in existing_with_ids.items()
                    if name.startswith('item_') and name not in api_item_names
                }

                if orphan_items:
                    print(f"[이모지] API에 없는 아이템 {len(orphan_items)}개 발견, 등급 배경 재업로드", flush=True)
                    for name, eid in orphan_items.items():
                        code = name.replace('item_', '')
                        url = f"{cdn_base}/ItemIcon_{code}.png"
                        # 기존 이모지 삭제
                        await self._delete_emoji(session, eid)
                        await asyncio.sleep(0.3)
                        # Epic 등급 배경으로 재업로드
                        success = await self._download_resize_upload(
                            session, url, name, 128, 128, grade='Epic'
                        )
                        if success:
                            added_count += 1
                            print(f"  [+] {name} 재업로드 (Epic 배경)", flush=True)
                        else:
                            logger.warning(f"  [!] {name} 재업로드 실패")
                        await asyncio.sleep(0.5)

                if added_count == 0:
                    logger.info("  아이템 변경 없음")
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

    async def _reupload_emojis_by_prefix(self, prefix: str) -> int:
        """특정 prefix의 이모지를 삭제 후 재업로드 (resize 적용)

        Args:
            prefix: 이모지 이름 접두사 (예: 'weapon_', 'char_')

        Returns:
            재업로드된 이모지 수
        """
        print(f"[이모지] {prefix} 이모지 재업로드 시작...", flush=True)
        try:
            existing_with_ids = await self._get_existing_emojis_with_ids()
            # prefix로 시작하는 이모지 찾기
            matched = {k: v for k, v in existing_with_ids.items() if k.startswith(prefix)}
            if not matched:
                print(f"[이모지] {prefix} 이모지 없음, 스킵", flush=True)
                return 0

            async with aiohttp.ClientSession() as session:
                # 1. 기존 이모지 삭제
                for name, eid in matched.items():
                    await self._delete_emoji(session, eid)
                    await asyncio.sleep(0.3)
                print(f"[이모지] {prefix} 이모지 {len(matched)}개 삭제 완료", flush=True)

                # 2. API에서 데이터 가져와서 재업로드
                if prefix == 'weapon_':
                    api_url = f'{self.dak_api_base}/masteries?hl=ko'
                    async with session.get(api_url) as response:
                        if response.status != 200:
                            return 0
                        data = await response.json()
                        items = [
                            {'emoji_name': f"weapon_{m['key'].lower()}", 'url': m.get('iconUrl', '')}
                            for m in data.get('masteries', [])
                            if m.get('key') and m.get('iconUrl')
                        ]
                elif prefix == 'char_':
                    api_url = f'{self.dak_api_base}/characters?hl=ko'
                    async with session.get(api_url) as response:
                        if response.status != 200:
                            return 0
                        data = await response.json()
                        items = [
                            {'emoji_name': f"char_{c['key'].lower()}", 'url': c.get('imageUrl', '')}
                            for c in data.get('characters', [])
                            if c.get('key') and c.get('imageUrl')
                        ]
                else:
                    print(f"[이모지] 알 수 없는 prefix: {prefix}", flush=True)
                    return 0

                added = 0
                for item in items:
                    success = await self._download_resize_upload(
                        session, item['url'], item['emoji_name'], 128, 128
                    )
                    if success:
                        added += 1
                    await asyncio.sleep(0.3)

                print(f"[이모지] {prefix} 이모지 {added}개 재업로드 완료", flush=True)
                return added
        except Exception as e:
            logger.error(f"{prefix} 이모지 재업로드 오류: {e}")
            return 0

    async def _reupload_weapon_emojis(self) -> int:
        """무기 이모지를 삭제 후 재업로드 (resize 적용, 일회성)"""
        print("[이모지] 무기 이모지 재업로드 시작...", flush=True)
        try:
            existing_with_ids = await self._get_existing_emojis_with_ids()
            # weapon_ 으로 시작하는 이모지 찾기
            weapon_emojis = {k: v for k, v in existing_with_ids.items() if k.startswith('weapon_')}
            if not weapon_emojis:
                print("[이모지] 무기 이모지 없음, 새로 업로드", flush=True)

            # 기존 무기 이모지 삭제
            async with aiohttp.ClientSession() as session:
                for name, eid in weapon_emojis.items():
                    await self._delete_emoji(session, eid)
                    await asyncio.sleep(0.3)
                print(f"[이모지] 무기 이모지 {len(weapon_emojis)}개 삭제 완료", flush=True)

                # API에서 무기 데이터 가져와서 재업로드
                async with session.get(f'{self.dak_api_base}/masteries?hl=ko') as response:
                    if response.status != 200:
                        return 0
                    data = await response.json()
                    masteries = data.get('masteries', [])

                added = 0
                for m in masteries:
                    key = m.get('key', '').lower()
                    icon_url = m.get('iconUrl', '')
                    if not key or not icon_url:
                        continue
                    emoji_name = f"weapon_{key}"
                    success = await self._download_resize_upload(
                        session, icon_url, emoji_name, 128, 128
                    )
                    if success:
                        added += 1
                    await asyncio.sleep(0.3)

                print(f"[이모지] 무기 이모지 {added}개 재업로드 완료", flush=True)
                return added
        except Exception as e:
            logger.error(f"무기 이모지 재업로드 오류: {e}")
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

    async def _update_weather_emojis(self, existing: Set[str]) -> int:
        """날씨 이모지 업데이트"""
        logger.info("날씨 이모지 체크 중...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.dak_api_base}/weathers?hl=ko') as response:
                    if response.status != 200:
                        logger.error(f"날씨 API 요청 실패: {response.status}")
                        return 0

                    data = await response.json()
                    weathers = data.get('weathers', [])

                    new_weathers = []
                    for w in weathers:
                        wid = w.get('key')
                        if wid is None:
                            continue
                        emoji_name = f"weather_{wid}"
                        if emoji_name not in existing:
                            icon_url = w.get('imageUrl', '') or w.get('iconUrl', '')
                            if icon_url:
                                new_weathers.append({
                                    'id': wid,
                                    'name': w.get('name', 'Unknown'),
                                    'url': icon_url
                                })

                    if not new_weathers:
                        logger.info("  새로운 날씨 없음")
                        return 0

                    logger.info(f"  새로운 날씨 {len(new_weathers)}개 발견!")
                    added_count = 0
                    for w in new_weathers:
                        emoji_name = f"weather_{w['id']}"
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
            logger.error(f"날씨 이모지 업데이트 오류: {e}")
            return 0

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

    async def _reupload_all_item_emojis_with_grades(self):
        """[일회성] 기존 item_ 이모지 전부 삭제 후 등급 배경으로 재업로드"""
        print("[이모지] 아이템 전체 재업로드 시작 (등급 그라데이션 적용)...", flush=True)
        cdn_base = "https://cdn.dak.gg/assets/er/game-assets/10.4.0"
        er_api_base = "https://open-api.bser.io/v1/data"
        er_api_headers = {"x-api-key": "wxIgXerGxj1xJ3r4z4xjoavjMUfh10Kw3pVtMasn"}

        try:
            # 1. ER API에서 모든 아이템 코드 → 등급 매핑 수집
            item_grades = {}
            async with aiohttp.ClientSession() as session:
                for endpoint in ['ItemWeapon', 'ItemArmor', 'ItemMisc', 'ItemConsumable', 'ItemSpecial']:
                    async with session.get(
                        f'{er_api_base}/{endpoint}', headers=er_api_headers
                    ) as response:
                        if response.status != 200:
                            continue
                        data = await response.json()
                        for item in data.get('data', []):
                            item_grades[str(item['code'])] = item.get('itemGrade', '')
                print(f"[이모지] ER API에서 {len(item_grades)}개 아이템 등급 수집", flush=True)

                # 2. 기존 item_ 이모지 전부 삭제
                existing = await self._get_existing_emojis_with_ids()
                item_emojis = {k: v for k, v in existing.items() if k.startswith('item_')}
                if not item_emojis:
                    print("[이모지] item_ 이모지 없음, 스킵", flush=True)
                    return

                print(f"[이모지] item_ 이모지 {len(item_emojis)}개 삭제 중...", flush=True)
                for name, eid in item_emojis.items():
                    await self._delete_emoji(session, eid)
                    await asyncio.sleep(0.3)

                # 3. 등급 배경과 함께 재업로드
                print(f"[이모지] 등급 배경으로 재업로드 중...", flush=True)
                added = 0
                for name in item_emojis:
                    code = name.replace('item_', '')
                    grade = item_grades.get(code, 'Epic')  # API에 없으면 Epic
                    url = f"{cdn_base}/ItemIcon_{code}.png"
                    success = await self._download_resize_upload(
                        session, url, name, 128, 128, grade=grade
                    )
                    if success:
                        added += 1
                    else:
                        logger.warning(f"  [!] {name} 재업로드 실패 ({grade})")
                    await asyncio.sleep(0.5)

                print(f"[이모지] 아이템 재업로드 완료: {added}개", flush=True)
                await load_emoji_map(self.bot)

        except Exception as e:
            logger.error(f"아이템 재업로드 오류: {e}", exc_info=True)

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
        width: int, height: int, grade: str = None
    ) -> bool:
        """이미지 다운로드 -> 리사이즈 -> Discord 업로드

        Args:
            grade: 아이템 등급 (Common/Uncommon/Rare/Epic/Legend/Mythic).
                   지정하면 등급 색상 둥근 사각형 배경 위에 아이콘을 합성.
        """
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

            # 비율 유지하면서 캔버스에 꽉 차게 스케일 (확대/축소 모두)
            scale = min(width / img.width, height / img.height)
            new_w = int(img.width * scale)
            new_h = int(img.height * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # 등급 배경 합성 (grade가 지정된 경우)
            if grade and grade in GRADE_COLORS:
                bottom_color, top_color = GRADE_COLORS[grade]
                canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                # 수직 그라데이션 생성 (위=어두운색, 아래=밝은색, dak.gg 0deg 방향)
                gradient = Image.new('RGBA', (1, height))
                for y_pos in range(height):
                    ratio = y_pos / (height - 1) if height > 1 else 0
                    r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
                    g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
                    b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
                    gradient.putpixel((0, y_pos), (r, g, b, 255))
                gradient = gradient.resize((width, height), Image.Resampling.NEAREST)
                # 둥근 사각형 마스크
                mask = Image.new('L', (width, height), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle(
                    [(0, 0), (width - 1, height - 1)],
                    radius=16, fill=255
                )
                canvas.paste(gradient, (0, 0), mask)
                # 아이콘을 배경보다 약간 작게 (패딩 8px)
                icon_scale = min((width - 16) / img.width, (height - 16) / img.height)
                icon_w = int(img.width * icon_scale)
                icon_h = int(img.height * icon_scale)
                icon = img.resize((icon_w, icon_h), Image.Resampling.LANCZOS)
                ix = (width - icon_w) // 2
                iy = (height - icon_h) // 2
                canvas.paste(icon, (ix, iy), icon)
                img_resized = canvas
            else:
                # 투명 캔버스에 중앙 배치
                canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                x = (width - new_w) // 2
                y = (height - new_h) // 2
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

