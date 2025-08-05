import asyncio
import aiohttp
import urllib.parse
from typing import Optional, Dict, Any, List

# --- 데이터 캐시 클래스 ---

class GameDataCache:
    def __init__(self):
        self.seasons: Dict[str, Any] = {}
        self.characters: Dict[int, Any] = {}
        self.all_skins: Dict[int, Any] = {} # 모든 스킨을 ID로 저장
        self.tiers: Dict[int, Any] = {}
        self.current_season_id: Optional[int] = None

    def get_season_name(self, season_id: int) -> str:
        return self.seasons.get(str(season_id), {}).get('name', f"Season {season_id}")

    def get_season_api_param(self, season_id: int) -> Optional[str]:
        season_info = self.seasons.get(str(season_id))
        if season_info and season_info.get('key'):
            return season_info['key']
        print(f"🚨 경고: 시즌 {season_id}의 API 파라미터('key')를 찾을 수 없습니다.")
        return None

    def get_character_name(self, char_id: int) -> str:
        return self.characters.get(char_id, {}).get('name', f'Unknown_{char_id}')

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

# --- 전역 인스턴스 및 상수 ---

game_data = GameDataCache()

DAKGG_API_BASE = "https://er.dakgg.io/api/v1"
API_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://dak.gg",
    "Referer": "https://dak.gg/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# --- 데이터 초기화 ---

async def initialize_game_data():
    print("⏳ DAK.GG 데이터 초기화를 시작합니다...")
    
    async with aiohttp.ClientSession(headers=API_HEADERS) as session:
        try:
            tasks = {
                'current_season': session.get("https://er.dakgg.io/api/v0/current-season"),
                'seasons': session.get(f"{DAKGG_API_BASE}/data/seasons?hl=ko"),
                'characters': session.get(f"{DAKGG_API_BASE}/data/characters?hl=ko"),
                'tiers': session.get(f"{DAKGG_API_BASE}/data/tiers?hl=ko")
            }
            responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
            results: Dict[str, Any] = dict(zip(tasks.keys(), responses))
        except Exception as e:
            print(f"HTTP 요청 중 오류: {e}")
            return

    # 현재 시즌 데이터 처리 (v0/current-season 우선 사용)
    current_season_resp = results.get('current_season')
    if isinstance(current_season_resp, aiohttp.ClientResponse) and current_season_resp.status == 200:
        current_season_data = await current_season_resp.json()
        current_season_resp.close()
        game_data.current_season_id = current_season_data.get('id')
        print(f"✅ 현재 시즌 정보 로드 완료 (v0 API): {game_data.current_season_id}")
    else:
        if isinstance(current_season_resp, aiohttp.ClientResponse):
            current_season_resp.close()
        print("⚠️ v0/current-season API 실패, 기존 방법 사용")
        game_data.current_season_id = None
    
    # 전체 시즌 데이터 처리
    seasons_resp = results.get('seasons')
    try:
        if isinstance(seasons_resp, aiohttp.ClientResponse) and seasons_resp.status == 200:
            data = await seasons_resp.json()
            seasons_resp.close()
            game_data.seasons = {str(s['id']): s for s in data.get('seasons', [])}
            
            # v0 API로 현재 시즌을 못 가져왔으면 기존 방법 사용
            if game_data.current_season_id is None:
                current_season = next((s for s in data.get('seasons', []) if s.get('isCurrent')), None)
                if current_season:
                    game_data.current_season_id = current_season['id']
                    print(f"✅ 시즌 데이터 로드 완료 (기존 방법): {game_data.current_season_id}")
                else:
                    raise Exception("❌ 치명적 오류: 현재 시즌 정보를 찾을 수 없습니다.")
            else:
                print(f"✅ 전체 시즌 데이터 로드 완료")
        else:
            if isinstance(seasons_resp, aiohttp.ClientResponse):
                seasons_resp.close()
            raise Exception(f"❌ 치명적 오류: 시즌 데이터를 가져오지 못했습니다. 응답: {seasons_resp}")
    except Exception as e:
        if isinstance(seasons_resp, aiohttp.ClientResponse):
            seasons_resp.close()
        raise e

    # 캐릭터 및 스킨 데이터 처리
    characters_resp = results.get('characters')
    try:
        if isinstance(characters_resp, aiohttp.ClientResponse) and characters_resp.status == 200:
            data = await characters_resp.json()
            characters_resp.close()
            for char in data.get('characters', []):
                game_data.characters[char['id']] = char
                if 'skins' in char:
                    for skin in char['skins']:
                        game_data.all_skins[skin['id']] = skin
            print("✅ 캐릭터 및 스킨 데이터 로드 완료")
        else:
            if isinstance(characters_resp, aiohttp.ClientResponse):
                characters_resp.close()
            print(f"⚠️ 경고: 캐릭터 데이터를 가져오지 못했습니다. 응답: {characters_resp}")
    except Exception as e:
        if isinstance(characters_resp, aiohttp.ClientResponse):
            characters_resp.close()
        print(f"캐릭터 데이터 처리 중 오류: {e}")

    # 티어 데이터 처리
    tiers_resp = results.get('tiers')
    try:
        if isinstance(tiers_resp, aiohttp.ClientResponse) and tiers_resp.status == 200:
            data = await tiers_resp.json()
            tiers_resp.close()
            game_data.tiers = {t['id']: {'name': t['name'], 'imageUrl': f"https:{t['imageUrl']}" if t.get('imageUrl', '').startswith('//') else t.get('imageUrl')} for t in data.get('tiers', [])}
            print("✅ 티어 데이터 로드 완료")
        else:
            if isinstance(tiers_resp, aiohttp.ClientResponse):
                tiers_resp.close()
            print(f"⚠️ 경고: 티어 데이터를 가져오지 못했습니다. 응답: {tiers_resp}")
    except Exception as e:
        if isinstance(tiers_resp, aiohttp.ClientResponse):
            tiers_resp.close()
        print(f"티어 데이터 처리 중 오류: {e}")

    print("🚀 모든 DAK.GG 데이터 초기화 완료!")

# --- API 호출 로직 ---

async def _fetch_api(url: str) -> Optional[Dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=API_HEADERS, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                print(f"API Error: {response.status} for URL: {url}")
                return None
    except Exception as e:
        print(f"An unexpected error occurred during API fetch for {url}: {e}")
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
