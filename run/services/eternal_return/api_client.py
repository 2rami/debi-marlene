import asyncio
import aiohttp
import urllib.parse
from typing import Optional, Dict, Any, List

# 글로벌 봇 인스턴스 저장
_bot_instance = None

def set_bot_instance(bot):
    """웹 패널에서 사용할 봇 인스턴스를 설정"""
    global _bot_instance
    _bot_instance = bot

def get_bot_instance():
    """웹 패널에서 봇 인스턴스를 가져옴"""
    return _bot_instance

# --- 데이터 캐시 클래스 ---

class GameDataCache:
    def __init__(self):
        self.seasons: Dict[str, Any] = {}
        self.characters: Dict[int, Any] = {}
        self.all_skins: Dict[int, Any] = {} # 모든 스킨을 ID로 저장
        self.tiers: Dict[int, Any] = {}
        self.items: Dict[int, Any] = {}  # 아이템 데이터
        self.masteries: Dict[int, Any] = {}  # 무기(마스터리) 데이터
        self.trait_skills: Dict[int, Any] = {}  # 특성 스킬 데이터
        self.current_season_id: Optional[int] = None

    def get_season_name(self, season_id: int) -> str:
        return self.seasons.get(str(season_id), {}).get('name', f"Season {season_id}")

    def get_season_api_param(self, season_id: int) -> Optional[str]:
        season_info = self.seasons.get(str(season_id))
        if season_info and season_info.get('key'):
            return season_info['key']
        print(f"[경고] 경고: 시즌 {season_id}의 API 파라미터('key')를 찾을 수 없습니다.")
        return None

    def get_character_name(self, char_id: int) -> str:
        if not self.characters:
            print("[오류] 캐릭터 데이터가 로드되지 않았습니다!")
            return f'Unknown_{char_id}'
        
        char_name = self.characters.get(char_id, {}).get('name', f'Unknown_{char_id}')
        if char_name == f'Unknown_{char_id}':
            # print(f"[오류] 캐릭터 ID {char_id}를 찾을 수 없습니다. 로드된 캐릭터 수: {len(self.characters)}")
            # 처음 몇 개 캐릭터 ID 출력
            if self.characters:
                sample_ids = list(self.characters.keys())[:5]
                # print(f"   로드된 캐릭터 ID 예시: {sample_ids}")
        return char_name

    def get_skin_image_url(self, skin_id: int) -> Optional[str]:
        """스킨 ID로 이미지 URL을 반환합니다."""
        skin_info = self.all_skins.get(skin_id)
        if not skin_info:
            return None
        image_url = skin_info.get('imageUrl')
        return f"https:{image_url}" if image_url and image_url.startswith('//') else image_url

    def get_tier_name(self, tier_id: int) -> str:
        return self.tiers.get(tier_id, {}).get('name', "언랭크")

    def get_tier_image_url(self, tier_id: int) -> str:
        default_url = "https://cdn.dak.gg/assets/er/images/rank/full/0.png"
        return self.tiers.get(tier_id, {}).get('imageUrl', default_url)

    def get_character_key(self, char_id: int) -> Optional[str]:
        """캐릭터 ID로 영어 key를 반환합니다 (이모지용)."""
        return self.characters.get(char_id, {}).get('key')

    def get_weapon_key(self, weapon_id: int) -> Optional[str]:
        """무기 ID로 영어 key를 반환합니다 (이모지용)."""
        return self.masteries.get(weapon_id, {}).get('key')

    def get_weapon_name(self, weapon_id: int) -> str:
        """무기 ID로 한글 이름을 반환합니다."""
        return self.masteries.get(weapon_id, {}).get('name', '알 수 없음')
    
    def get_item_image_url(self, item_id: int) -> Optional[str]:
        """아이템 ID로 이미지 URL을 반환합니다 (CDN 직접 생성)."""
        if item_id:
            # CDN URL 직접 생성 (메인 화면 방식)
            return f"https://cdn.dak.gg/assets/er/game-assets/8.4.0/ItemIcon_{item_id}.png"
        return None
    
    def get_item_grade(self, item_id: int) -> str:
        """아이템 ID로 등급을 반환합니다."""
        item_info = self.items.get(item_id)
        if item_info:
            grade = item_info.get('grade', 'Common')
            # 등급 이름 한글화
            grade_map = {
                'Common': '일반',
                'Uncommon': '고급', 
                'Rare': '희귀',
                'Epic': '영웅',
                'Legend': '전설',
                'Mythic': '신화'
            }
            return grade_map.get(grade, grade)
        return '일반'
    
    def get_weapon_image_url(self, weapon_id: int) -> Optional[str]:
        """무기 ID로 이미지 URL을 반환합니다 (CDN 직접 생성)."""
        if weapon_id:
            # CDN URL 직접 생성 (메인 화면 방식)
            return f"https://cdn.dak.gg/assets/er/game-assets/8.4.0/Ico_Mastery_{weapon_id}.png"
        return None
    
    def get_trait_image_url(self, trait_id: int) -> Optional[str]:
        """특성 ID로 이미지 URL을 반환합니다 (CDN 직접 생성)."""
        if trait_id:
            # CDN URL 직접 생성 (메인 화면 방식)
            return f"https://cdn.dak.gg/assets/er/game-assets/8.4.0/TraitIcon_{trait_id}.png"
        return None

# --- 전역 인스턴스 및 상수 ---

game_data = GameDataCache()

async def load_character_data_fallback():
    """캐릭터 데이터 로드 실패 시 대체 로딩 방법"""
    try:
        print("[재시도] 캐릭터 데이터 대체 로딩 시도...")
        url = f"{DAKGG_API_BASE}/data/characters?hl=ko"
        data = await _fetch_api(url)
        if data and 'characters' in data:
            for char in data.get('characters', []):
                game_data.characters[char['id']] = char
                if 'skins' in char:
                    for skin in char['skins']:
                        game_data.all_skins[skin['id']] = skin
            print("[완료] 캐릭터 데이터 대체 로딩 성공")
        else:
            print("[오류] 캐릭터 데이터 대체 로딩 실패")
    except Exception as e:
        print(f"캐릭터 데이터 대체 로딩 오류: {e}")

DAKGG_API_BASE = "https://er.dakgg.io/api/v1"
API_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://dak.gg",
    "Referer": "https://dak.gg/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# --- 데이터 초기화 ---

async def initialize_game_data():
    import sys
    # 15초 타임아웃으로 ClientSession 생성
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(headers=API_HEADERS, timeout=timeout) as session:
        try:
            tasks = {
                'current_season': session.get("https://er.dakgg.io/api/v0/current-season"),
                'seasons': session.get(f"{DAKGG_API_BASE}/data/seasons?hl=ko"),
                'characters': session.get(f"{DAKGG_API_BASE}/data/characters?hl=ko"),
                'tiers': session.get(f"{DAKGG_API_BASE}/data/tiers?hl=ko"),
                'items': session.get(f"{DAKGG_API_BASE}/data/items?hl=ko"),
                'masteries': session.get(f"{DAKGG_API_BASE}/data/masteries?hl=ko"),
                'trait_skills': session.get(f"{DAKGG_API_BASE}/data/trait-skills?hl=ko")
            }
            
            responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
            results: Dict[str, Any] = {}

            # Session이 닫히기 전에 모든 JSON 데이터를 미리 읽어둠
            for key, resp in zip(tasks.keys(), responses):
                if isinstance(resp, aiohttp.ClientResponse) and resp.status == 200:
                    try:
                        results[key] = await resp.json()
                        resp.close()
                    except Exception as e:
                        results[key] = None
                        if not resp.closed:
                            resp.close()
                else:
                    results[key] = resp  # Exception이거나 실패한 response

        except Exception as e:
            print(f"[오류] HTTP 요청 중 오류: {e}", flush=True)
            return

    # 현재 시즌 데이터 처리 (v0/current-season 우선 사용)
    current_season_data = results.get('current_season')
    if current_season_data and isinstance(current_season_data, dict):
        game_data.current_season_id = current_season_data.get('id')
    else:
        print("[경고] v0/current-season API 실패, 기존 방법 사용")
        game_data.current_season_id = None
    
    # 전체 시즌 데이터 처리
    seasons_data = results.get('seasons')
    if seasons_data and isinstance(seasons_data, dict):
        game_data.seasons = {str(s['id']): s for s in seasons_data.get('seasons', [])}

        # v0 API로 현재 시즌을 못 가져왔으면 기존 방법 사용
        if game_data.current_season_id is None:
            current_season = next((s for s in seasons_data.get('seasons', []) if s.get('isCurrent')), None)
            if current_season:
                game_data.current_season_id = current_season['id']
            else:
                raise Exception("[오류] 치명적 오류: 현재 시즌 정보를 찾을 수 없습니다.")
    else:
        raise Exception(f"[오류] 치명적 오류: 시즌 데이터를 가져오지 못했습니다.")

    # 캐릭터 및 스킨 데이터 처리
    characters_data = results.get('characters')
    if characters_data and isinstance(characters_data, dict):
        for char in characters_data.get('characters', []):
            game_data.characters[char['id']] = char
            if 'skins' in char:
                for skin in char['skins']:
                    game_data.all_skins[skin['id']] = skin
    else:
        print(f"[경고] 캐릭터 데이터를 가져오지 못했습니다.")
        await load_character_data_fallback()

    # 티어 데이터 처리
    tiers_data = results.get('tiers')
    if tiers_data and isinstance(tiers_data, dict):
        game_data.tiers = {t['id']: {'name': t['name'], 'imageUrl': f"https:{t['imageUrl']}" if t.get('imageUrl', '').startswith('//') else t.get('imageUrl')} for t in tiers_data.get('tiers', [])}
    else:
        print(f"[경고] 티어 데이터를 가져오지 못했습니다.")

    # 아이템 데이터 처리
    items_data = results.get('items')
    if items_data and isinstance(items_data, dict):
        for item in items_data.get('items', []):
            game_data.items[item['id']] = item
    
    # 무기(마스터리) 데이터 처리
    masteries_data = results.get('masteries')
    if masteries_data and isinstance(masteries_data, dict):
        for mastery in masteries_data.get('masteries', []):
            game_data.masteries[mastery['id']] = mastery
    
    # 특성 스킬 데이터 처리
    trait_skills_data = results.get('trait_skills')
    if trait_skills_data and isinstance(trait_skills_data, dict):
        for trait in trait_skills_data.get('traitSkills', []):
            game_data.trait_skills[trait['id']] = trait
    
    print("[시작] 모든 DAK.GG 데이터 초기화 완료!", flush=True)

# --- API 호출 로직 ---

async def _fetch_api(url: str, params: Optional[Dict] = None) -> Optional[Dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=API_HEADERS, params=params, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                # 에러 시에만 로그 출력
                print(f"[오류] API Error: {response.status} for URL: {url}", flush=True)
                error_text = await response.text()
                print(f"[오류] API Error response: {error_text[:200]}", flush=True)
                return None
    except Exception as e:
        print(f"An unexpected error occurred during API fetch for {url}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

async def get_character_stats(dt: int = 7, team_mode: str = "SQUAD", tier: str = "diamond_plus") -> Optional[Dict]:
    """캐릭터 통계 정보를 가져옵니다"""
    try:
        params = {
            "dt": dt,
            "matchingMode": "RANK", 
            "teamMode": team_mode,
            "tier": tier
        }
        url = f"{DAKGG_API_BASE}/character-stats"
        return await _fetch_api(url, params)
    except Exception as e:
        print(f"캐릭터 통계 데이터 가져오기 오류: {e}")
        return None

async def get_player_season_data(nickname: str, season_id: int) -> Optional[Dict]:
    season_param = game_data.get_season_api_param(season_id)
    if not season_param:
        return None
    encoded_nickname = urllib.parse.quote(nickname)
    profile_url = f"{DAKGG_API_BASE}/players/{encoded_nickname}/profile?season={season_param}"
    profile_data = await _fetch_api(profile_url)
    if not profile_data:
        return None
    return _process_player_data(nickname, profile_data, season_id)

async def get_player_basic_data(nickname: str) -> Optional[Dict]:
    if game_data.current_season_id is None: return None
    return await get_player_season_data(nickname, game_data.current_season_id)

async def get_player_normal_game_data(nickname: str) -> Optional[Dict]:
    """일반게임 데이터를 가져옵니다."""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        profile_url = f"{DAKGG_API_BASE}/players/{encoded_nickname}/profile?season=NORMAL"
        profile_data = await _fetch_api(profile_url)
        if not profile_data:
            return None
        return _process_normal_game_data(nickname, profile_data)
    except Exception as e:
        print(f"일반게임 데이터 조회 오류: {e}")
        return None

def _process_normal_game_data(nickname: str, profile_data: Dict) -> Optional[Dict]:
    """일반게임 데이터를 처리합니다."""
    # print(f"[검색] 일반게임 데이터 처리 시작: {nickname}")
    # print(f"Profile data keys: {list(profile_data.keys())}")
    
    # 일반게임 오버뷰 찾기 (matchingModeId == 0)
    overview = next((o for o in profile_data.get('playerSeasonOverviews', []) if o.get('matchingModeId') == 0), None)
    
    # 레벨 정보 찾기 - accountLevel 사용
    level = 1
    exp = 0
    
    # 1. player 객체의 accountLevel 확인  
    if 'player' in profile_data and profile_data['player'].get('accountLevel'):
        level = profile_data['player']['accountLevel']
        print(f"[완료] player.accountLevel에서 레벨 발견: {level}")
    # 2. 최상위 accountLevel 확인
    elif 'accountLevel' in profile_data:
        level = profile_data['accountLevel']
        print(f"[완료] 최상위에서 accountLevel 발견: {level}")
    # 3. player 객체의 level 확인  
    elif 'player' in profile_data and profile_data['player'].get('level'):
        level = profile_data['player']['level']
        print(f"[완료] player.level에서 레벨 발견: {level}")
    # 4. 최상위 level 확인
    elif 'level' in profile_data:
        level = profile_data['level']
        print(f"[완료] 최상위에서 level 발견: {level}")
    else:
        print("[오류] 레벨 정보를 찾을 수 없음")
        # 디버깅을 위해 player 구조 출력
        if 'player' in profile_data:
            print(f"Player data keys: {list(profile_data['player'].keys())}")
    
    if not overview:
        return {
            'nickname': nickname, 'tier_info': '일반게임', 'tier_image_url': game_data.get_tier_image_url(0),
            'mmr': 0, 'lp': 0, 'stats': {}, 'most_characters': [],
            'season_id': None, 'season_name': '일반게임',
            'rank': 0, 'rank_size': 0, 'rank_percent': 0,
            'level': level, 'exp': exp  # 레벨 정보 추가
        }
    
    total_games = overview.get('play', 1)
    wins = overview.get('win', 0)
    
    kills = overview.get('playerKill', 0)
    assists = overview.get('playerAssistant', 0)
    deaths = overview.get('playerDeaths', 0)
    kda = round((kills + assists) / max(1, deaths), 2)

    stats = {
        'total_games': overview.get('play', 0), 'wins': wins,
        'winrate': round((wins / max(total_games, 1)) * 100, 1),
        'avg_rank': round(overview.get('place', 0) / max(total_games, 1), 1),
        'avg_kills': round(kills / max(total_games, 1), 1),
        'avg_assists': round(assists / max(total_games, 1), 1),
        'kda': kda,
        'avg_damage': round(overview.get('damageToPlayer', 0) / max(total_games, 1), 0)
    }
    
    # 실험체 통계
    char_stats = []
    # print(f"[검색] 캐릭터 통계 처리 시작 - 총 {len(overview.get('characterStats', []))}개 캐릭터")
    for char_stat in overview.get('characterStats', []):
        if char_stat.get('play', 0) > 0:
            char_id = char_stat.get('key')
            games = char_stat.get('play', 1)
            
            # print(f"  - 캐릭터 ID: {char_id}")
            character_name = game_data.get_character_name(char_id)
            print(f"    캐릭터 이름: {character_name}")

            # 가장 많이 사용한 스킨 찾기
            most_used_skin_id = char_id * 1000 + 1 # 기본 스킨 ID로 초기화
            if char_stat.get('skinStats'):
                sorted_skins = sorted(char_stat['skinStats'], key=lambda x: x.get('play', 0), reverse=True)
                if sorted_skins:
                    most_used_skin_id = sorted_skins[0].get('key', most_used_skin_id)
            
            image_url = game_data.get_skin_image_url(most_used_skin_id)
            # print(f"    스킨 ID: {most_used_skin_id}, 이미지 URL: {image_url}")

            char_stats.append({
                'name': character_name,
                'image_url': image_url,
                'games': games, 'wins': char_stat.get('win', 0),
                'winrate': round((char_stat.get('win', 0) / games) * 100, 1),
                'avg_rank': round(char_stat.get('place', 0) / games, 1),
                'mmr_gain': 0  # 일반게임은 RP 없음
            })
    
    most_characters = sorted(char_stats, key=lambda x: x['games'], reverse=True)[:10]

    return {
        'nickname': nickname, 'tier_info': '일반게임', 'tier_image_url': game_data.get_tier_image_url(0),
        'mmr': 0, 'lp': 0, 'stats': stats, 'most_characters': most_characters,
        'season_id': None, 'season_name': '일반게임',
        'rank': 0, 'rank_size': 0, 'rank_percent': 0,
        'level': level, 'exp': exp  # 레벨 정보 추가
    }

async def get_player_played_seasons(nickname: str) -> List[Dict[str, Any]]:
    if game_data.current_season_id is None: return []
    season_param = game_data.get_season_api_param(game_data.current_season_id)
    if not season_param: return []
    encoded_nickname = urllib.parse.quote(nickname)
    url = f"{DAKGG_API_BASE}/players/{encoded_nickname}/profile?season={season_param}"
    data = await _fetch_api(url)
    if not data or 'playerSeasons' not in data: return []
    played_seasons = []
    for season in data.get('playerSeasons', []):
        season_id = season.get('seasonId')
        if season_id and str(season_id) in game_data.seasons:
            played_seasons.append({'id': season_id, 'name': game_data.get_season_name(season_id), 'is_current': season_id == game_data.current_season_id})
    return sorted(played_seasons, key=lambda x: x['id'], reverse=True)

# --- 데이터 가공 로직 ---

def _process_player_data(nickname: str, profile_data: Dict, target_season_id: int) -> Optional[Dict]:
    target_season = next((s for s in profile_data.get('playerSeasons', []) if s.get('seasonId') == target_season_id), None)
    if not target_season:
        return {
            'nickname': nickname, 'tier_info': '언랭크', 'tier_image_url': game_data.get_tier_image_url(0),
            'mmr': 0, 'lp': 0, 'stats': {}, 'most_characters': [],
            'season_id': target_season_id, 'season_name': game_data.get_season_name(target_season_id)
        }

    mmr, tier_id, grade, lp = target_season.get('mmr', 0), target_season.get('tierId', 0), target_season.get('tierGradeId', 1), target_season.get('tierMmr', 0)
    tier_name = game_data.get_tier_name(tier_id)
    tier_info = f"{tier_name} {grade} {lp} RP (MMR {mmr})" if tier_id > 0 else f"{tier_name} (MMR {mmr})"
    
    # 랭킹 정보는 playerSeasonOverviews에서 찾기
    rank = 0
    rank_size = 0
    rank_percent = 0
    
    result = {
        'nickname': nickname, 'tier_info': tier_info, 'tier_image_url': game_data.get_tier_image_url(tier_id),
        'mmr': mmr, 'lp': lp, 'stats': {}, 'most_characters': [],
        'season_id': target_season_id, 'season_name': game_data.get_season_name(target_season_id),
        'rank': rank, 'rank_size': rank_size, 'rank_percent': rank_percent
    }
    
    # 랭크 게임 오버뷰 우선 선택 (matchingModeId == 3), 없으면 일반 게임 (matchingModeId == 0)
    overview = next((o for o in profile_data.get('playerSeasonOverviews', []) if o.get('seasonId') == target_season_id and o.get('matchingModeId') == 3), None)
    if not overview:
        overview = next((o for o in profile_data.get('playerSeasonOverviews', []) if o.get('seasonId') == target_season_id and o.get('matchingModeId') == 0), None)
    
    # 듀오 게임 통계도 가져오기 (matchingModeId == 2)
    duo_overview = next((o for o in profile_data.get('playerSeasonOverviews', []) if o.get('seasonId') == target_season_id and o.get('matchingModeId') == 2), None)

    if overview:
        total_games = overview.get('play', 1)
        wins = overview.get('win', 0)  # 1위 (승리)
        
        # Top2, Top3 비율 계산 (API에서 직접 제공되는 값 사용)
        top2_count = overview.get('top2', 0)  # 2위까지 (1위 + 2위)
        top3_count = overview.get('top3', 0)  # 3위까지 (1위 + 2위 + 3위)
        top2_rate = round((top2_count / max(total_games, 1)) * 100, 1)
        top3_rate = round((top3_count / max(total_games, 1)) * 100, 1)
        
        kills = overview.get('playerKill', 0)
        assists = overview.get('playerAssistant', 0)
        deaths = overview.get('playerDeaths', 0)
        kda = round((kills + assists) / max(1, deaths), 2)

        result['stats'] = {
            'total_games': overview.get('play', 0), 'wins': wins,
            'winrate': round((wins / max(total_games, 1)) * 100, 1),
            'avg_rank': round(overview.get('place', 0) / max(total_games, 1), 1),
            'avg_kills': round(kills / max(total_games, 1), 1),
            'avg_assists': round(assists / max(total_games, 1), 1),
            'kda': kda,
            'avg_damage': round(overview.get('damageToPlayer', 0) / max(total_games, 1), 0),
            'top2_rate': top2_rate,
            'top3_rate': top3_rate
        }
        
        char_stats = []
        for char_stat in overview.get('characterStats', []):
            if char_stat.get('play', 0) > 0:
                char_id = char_stat.get('key')
                games = char_stat.get('play', 1)

                # 가장 많이 사용한 스킨 찾기
                most_used_skin_id = char_id * 1000 + 1 # 기본 스킨 ID로 초기화
                if char_stat.get('skinStats'):
                    sorted_skins = sorted(char_stat['skinStats'], key=lambda x: x.get('play', 0), reverse=True)
                    if sorted_skins:
                        most_used_skin_id = sorted_skins[0].get('key', most_used_skin_id)
                
                image_url = game_data.get_skin_image_url(most_used_skin_id)

                char_stats.append({
                    'name': game_data.get_character_name(char_id),
                    'image_url': image_url, # 스킨 이미지 URL 사용
                    'games': games, 'wins': char_stat.get('win', 0),
                    'winrate': round((char_stat.get('win', 0) / games) * 100, 1),
                    'avg_rank': round(char_stat.get('place', 0) / games, 1),
                    'mmr_gain': char_stat.get('mmrGain', 0)  # RP 획득/손실 추가
                })
        
        result['most_characters'] = sorted(char_stats, key=lambda x: x['games'], reverse=True)[:10]
        
        # MMR 히스토리 데이터 추가
        if 'mmrStats' in overview:
            result['mmr_history'] = overview['mmrStats']

    # 듀오 파트너 통계 추가 - overview에서 duoStats를 찾습니다.
    duo_partners = []
    if overview and 'duoStats' in overview and isinstance(overview['duoStats'], list):
        sorted_partners = sorted(overview['duoStats'], key=lambda x: x.get('play', 0), reverse=True)[:2]
        for partner in sorted_partners:
            if partner.get('nickname') and partner.get('play', 0) > 0:
                games = partner.get('play')
                wins = partner.get('win', 0)
                place = partner.get('place', 0)
                duo_partners.append({
                    'nickname': partner['nickname'],
                    'games': games,
                    'winrate': round((wins / max(games, 1)) * 100, 1),
                    'avg_rank': round(place / max(games, 1), 1)
                })
    result['duo_partners'] = duo_partners
    
    # 순위 정보 추출 (overview에서 rank 데이터 찾기)
    if overview and 'rank' in overview:
        rank_data = overview['rank']
        # local 순위 우선 사용 (한국 서버)
        if 'local' in rank_data:
            local_rank = rank_data['local']
            rank = local_rank.get('rank', 0)
            rank_size = local_rank.get('rankSize', 0)
            if rank > 0 and rank_size > 0:
                rank_percent = round((rank / rank_size) * 100, 2)
                result['rank'] = rank
                result['rank_size'] = rank_size
                result['rank_percent'] = rank_percent
    
    # 현재 시즌 오버뷰에 순위 정보가 없으면 다른 오버뷰들도 확인
    if result.get('rank', 0) == 0:
        for overview_alt in profile_data.get('playerSeasonOverviews', []):
            if 'rank' in overview_alt:
                rank_data = overview_alt['rank']
                if 'local' in rank_data:
                    local_rank = rank_data['local']
                    rank = local_rank.get('rank', 0)
                    rank_size = local_rank.get('rankSize', 0)
                    if rank > 0 and rank_size > 0:
                        rank_percent = round((rank / rank_size) * 100, 2)
                        result['rank'] = rank
                        result['rank_size'] = rank_size
                        result['rank_percent'] = rank_percent
                        break  # 첫 번째로 찾은 순위 정보 사용
        
    return result

async def get_game_details(game_id: int) -> Optional[Dict]:
    """공식 이터널 리턴 API로 게임 ID의 모든 참가자 정보를 가져옵니다."""
    try:
        # 공식 이터널 리턴 API 사용
        url = f"https://open-api.bser.io/v1/games/{game_id}"
        headers = {
            "accept": "application/json",
            "x-api-key": "wxIgXerGxj1xJ3r4z4xjoavjMUfh10Kw3pVtMasn"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('code') == 200 and data.get('userGames'):
                        return data
                    else:
                        print(f"[오류] 게임 {game_id} API 응답 오류: {data}")
                        return None
                else:
                    print(f"[오류] 게임 {game_id} 상세 정보 가져오기 실패: 상태 코드 {response.status}")
                    return None
                    
    except asyncio.TimeoutError:
        print(f"[오류] 게임 {game_id} 상세 정보 요청 시간 초과")
        return None
    except Exception as e:
        print(f"[오류] 게임 {game_id} 상세 정보 조회 오류: {e}")
        return None

def get_team_members(game_data: Dict, target_nickname: str) -> List[str]:
    """게임 데이터에서 특정 플레이어의 팀원들 닉네임을 반환합니다."""
    if not game_data or not game_data.get('userGames'):
        return []
    
    user_games = game_data['userGames']
    
    # 타겟 플레이어의 팀 번호 찾기
    target_team_num = None
    for player in user_games:
        if player.get('nickname') == target_nickname:
            target_team_num = player.get('teamNumber')
            break
    
    if target_team_num is None:
        return []
    
    # 같은 팀의 모든 플레이어 찾기 (자신 제외)
    team_members = []
    for player in user_games:
        if (player.get('teamNumber') == target_team_num and 
            player.get('nickname') != target_nickname):
            team_members.append(player.get('nickname', '알수없음'))
    
    return team_members

async def get_player_union_teams(nickname: str) -> Optional[Dict]:
    """
    플레이어의 유니온 팀 정보를 가져옵니다.
    
    Args:
        nickname: 플레이어 닉네임
    
    Returns:
        유니온 팀 데이터 또는 None
    """
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        url = f"{DAKGG_API_BASE}/players/{encoded_nickname}/union-teams"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"유니온 데이터 가져오기 실패: 상태 코드 {response.status}")
                    return None
    except asyncio.TimeoutError:
        print(f"유니온 데이터 요청 시간 초과: {nickname}")
        return None
    except Exception as e:
        print(f"유니온 데이터 가져오기 오류: {e}")
        return None

async def get_player_recent_games(nickname: str, season_id: int = None, game_mode: int = 3) -> Optional[List[Dict]]:
    """
    플레이어의 최근 게임 기록을 matches API에서 가져옵니다.
    
    Args:
        nickname: 플레이어 닉네임
        season_id: 시즌 ID (None이면 현재 시즌)
        game_mode: 게임 모드 (0: 일반, 2: 듀오, 3: 랭크)
    """
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        
        # 게임 모드에 따른 시즌 파라미터 설정
        if game_mode == 0:  # 일반게임
            season_param = "NORMAL"
        else:  # 랭크게임, 듀오게임
            if season_id is None:
                season_id = game_data.current_season_id
            season_param = game_data.get_season_api_param(season_id)
            if not season_param:
                return None
        
        # matches API 호출
        matches_url = f"{DAKGG_API_BASE}/players/{encoded_nickname}/matches"
        params = {
            'season': season_param,
            'matchingMode': game_mode,
            'limit': 20
        }
        
        matches_data = await _fetch_api(matches_url, params=params)
        if not matches_data:
            return None
        
        games = matches_data.get('matches', matches_data.get('games', []))
        if not games:
            print(f"[오류] {nickname}의 최근 게임 데이터가 없습니다. (모드: {game_mode})")
            return None
        
        processed_games = []
        for game in games[:20]:  # 최근 20게임만
            # 모든 리스트/딕셔너리 타입 필드를 미리 문자열로 변환
            safe_game = {}
            for key, value in game.items():
                if isinstance(value, (list, dict)):
                    safe_game[key] = str(value)
                else:
                    safe_game[key] = value
            game = safe_game  # 안전한 버전으로 교체

            # 게임 기본 정보
            game_info = {
                'gameId': game.get('gameId'),
                'seasonId': season_id,
                'matchingMode': game.get('matchingMode', game_mode),
                'gameRank': game.get('gameRank', game.get('rank')),
                'playerKill': game.get('playerKill', game.get('kills', 0)),
                'playerAssistant': game.get('playerAssistant', game.get('assists', 0)),
                'damageToPlayer': game.get('damageToPlayer', 0),
                'mmrGain': game.get('mmrGain', 0),
                'characterNum': game.get('characterNum'),
                'characterSkinNum': game.get('characterSkinNum'),
                'playTime': game.get('playTime'),
                'datetime': game.get('datetime'),
                # 추가 정보들
                'weaponType': game.get('weaponType'),
                'traitType': game.get('traitType'), 
                'skillType': game.get('skillType'),
                'items': str(game.get('items', [])),  # 리스트를 문자열로 변환
                'equipment': str(game.get('equipment', [])),  # 리스트를 문자열로 변환
                'mastery': str(game.get('mastery', [])),  # 리스트를 문자열로 변홨
                'teamKill': game.get('teamKill', 0)  # 팀킬 정보 추가
            }
            
            # 캐릭터 정보 추가
            char_id = game.get('characterNum')
            skin_id = game.get('characterSkinNum')

            if char_id:
                game_info['characterName'] = game_data.get_character_name(char_id)
                
                # 실제 사용한 스킨 이미지 가져오기
                character_image_url = None
                char_data = game_data.characters.get(char_id)
                
                if char_data and 'skins' in char_data:
                    # skinCode에서 실제 사용한 스킨 ID 가져오기 (characterSkinNum 대신 skinCode 사용)
                    actual_skin_id = game.get('skinCode')  # 실제 사용한 스킨 코드

                    # 실제 사용한 스킨 찾기
                    used_skin = None
                    if actual_skin_id:
                        for skin in char_data['skins']:
                            if skin.get('id') == actual_skin_id:
                                used_skin = skin
                                break
                    
                    # 실제 사용한 스킨이 없으면 기본 스킨 사용
                    if not used_skin and char_data['skins']:
                        used_skin = char_data['skins'][0]
                    
                    if used_skin and 'imageUrl' in used_skin:
                        skin_url = used_skin['imageUrl']
                        character_image_url = f"https:{skin_url}" if skin_url.startswith('//') else skin_url

                game_info['characterImage'] = character_image_url
                game_info['characterLevel'] = game.get('characterLevel', 1)  # 레벨 정보 추가
            
            # 무기 정보 추가 - bestWeapon 사용
            best_weapon_id = game.get('bestWeapon')

            if best_weapon_id:
                weapon_url = game_data.get_weapon_image_url(best_weapon_id)
                weapon_name = game_data.masteries.get(best_weapon_id, {}).get('name', '')
                game_info['weaponImage'] = weapon_url
                game_info['weaponName'] = weapon_name
            
            # 특성 정보 추가 - traitFirstCore, traitFirstSub, traitSecondSub 사용
            trait_core_id = game.get('traitFirstCore')
            trait_first_sub_id = game.get('traitFirstSub')
            trait_second_sub_id = game.get('traitSecondSub')

            if trait_core_id:
                core_url = game_data.get_trait_image_url(trait_core_id)
                core_name = game_data.trait_skills.get(trait_core_id, {}).get('name', '')
                game_info['traitImage'] = core_url
                game_info['traitName'] = core_name
            
            # 특성 서브 ID 처리 (리스트인 경우 첫 번째 항목 사용)
            if trait_first_sub_id:
                if isinstance(trait_first_sub_id, list) and len(trait_first_sub_id) > 0:
                    trait_first_sub_id = trait_first_sub_id[0]
                elif isinstance(trait_first_sub_id, str):
                    # 문자열인 경우 파싱 시도 (예: "[7210101, 7210801]")
                    import re
                    sub_ids = re.findall(r'\d+', trait_first_sub_id)
                    if sub_ids:
                        trait_first_sub_id = int(sub_ids[0])
                
                if isinstance(trait_first_sub_id, int):
                    sub1_url = game_data.get_trait_image_url(trait_first_sub_id)
                    sub1_name = game_data.trait_skills.get(trait_first_sub_id, {}).get('name', '')
                    game_info['traitFirstSubImage'] = sub1_url
                    game_info['traitFirstSubName'] = sub1_name
            
            if trait_second_sub_id:
                if isinstance(trait_second_sub_id, list) and len(trait_second_sub_id) > 0:
                    trait_second_sub_id = trait_second_sub_id[0]
                elif isinstance(trait_second_sub_id, str):
                    # 문자열인 경우 파싱 시도 (예: "[7111001, 7110601]")
                    import re
                    sub_ids = re.findall(r'\d+', trait_second_sub_id)
                    if sub_ids:
                        trait_second_sub_id = int(sub_ids[0])
                
                if isinstance(trait_second_sub_id, int):
                    sub2_url = game_data.get_trait_image_url(trait_second_sub_id)
                    sub2_name = game_data.trait_skills.get(trait_second_sub_id, {}).get('name', '')
                    game_info['traitSecondSubImage'] = sub2_url
                    game_info['traitSecondSubName'] = sub2_name
            
            # 아이템 이미지 추가 - equipmentGrade 배열 활용
            equipment_images = []
            equipment_str = game.get('equipment', '')
            equipment_grades_raw = game.get('equipmentGrade', [])
            
            # equipmentGrade가 문자열인 경우 배열로 변환
            if isinstance(equipment_grades_raw, str):
                try:
                    import ast
                    equipment_grades = ast.literal_eval(equipment_grades_raw)
                except:
                    # ast 파싱 실패 시 re 사용
                    import re
                    grade_numbers = re.findall(r'\d+', equipment_grades_raw)
                    equipment_grades = [int(num) for num in grade_numbers]
            elif isinstance(equipment_grades_raw, list):
                equipment_grades = equipment_grades_raw
            else:
                equipment_grades = []
            
            if equipment_str and equipment_str != '[]':  # 빈 리스트가 아닌 경우
                # 등급 숫자를 한글 등급명으로 변환
                def grade_number_to_korean(grade_num):
                    grade_map = {
                        1: '일반',    # Common
                        2: '고급',    # Uncommon  
                        3: '희귀',    # Rare
                        4: '영웅',    # Epic
                        5: '전설',    # Legend
                        6: '신화'     # Mythic
                    }
                    return grade_map.get(grade_num, '일반')
                
                # 문자열에서 숫자 추출 시도
                try:
                    # '[105402, 202421, 201507, 205406, 204505]' 같은 형태에서 숫자 추출
                    import re
                    item_ids = re.findall(r'\d+', equipment_str)

                    for i, item_id_str in enumerate(item_ids):
                        item_id = int(item_id_str)
                        # CDN URL 직접 생성으로 모든 아이템 이미지 표시
                        img_url = game_data.get_item_image_url(item_id)
                        if img_url:
                            # equipmentGrade 배열에서 등급 가져오기
                            grade_num = equipment_grades[i] if i < len(equipment_grades) else 1
                            item_grade = grade_number_to_korean(grade_num)
                            
                            equipment_images.append({
                                'url': img_url,
                                'grade': item_grade
                            })
                except Exception as e:
                    print(f"Equipment 처리 오류: {e}")
            game_info['equipmentImages'] = equipment_images
            
            
            processed_games.append(game_info)
        
        return processed_games
        
    except Exception as e:
        print(f"[오류] {nickname} 최근 게임 조회 오류: {e}")
        return None
