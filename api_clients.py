import asyncio
import aiohttp
import urllib.parse
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from config import ETERNAL_RETURN_API_BASE, ETERNAL_RETURN_API_KEY, DAKGG_API_BASE

class PlayerStatsError(Exception):
    """전적 검색 관련 예외"""
    pass

class StatsCache:
    """전적 조회 결과 캐싱 클래스"""
    def __init__(self, cache_duration_minutes: int = 10):
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
    
    def _generate_key(self, nickname: str) -> str:
        """캐시 키 생성"""
        return hashlib.md5(nickname.lower().encode()).hexdigest()
    
    def get(self, nickname: str) -> Optional[Dict[str, Any]]:
        """캐시된 데이터 조회"""
        key = self._generate_key(nickname)
        if key in self.cache:
            cached_data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                print(f"✅ 캐시에서 {nickname} 데이터 로드")
                return cached_data
            else:
                # 만료된 캐시 삭제
                del self.cache[key]
                print(f"🗑️ {nickname}의 만료된 캐시 삭제")
        return None
    
    def set(self, nickname: str, data: Dict[str, Any]) -> None:
        """데이터 캐싱"""
        key = self._generate_key(nickname)
        self.cache[key] = (data, datetime.now())
        print(f"💾 {nickname} 데이터 캐시 저장")
    
    def clear_expired(self) -> None:
        """만료된 캐시 정리"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, (data, timestamp) in self.cache.items():
            if current_time - timestamp >= self.cache_duration:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print(f"🗑️ 만료된 캐시 {len(expired_keys)}개 정리")

# 전역 캐시 인스턴스
stats_cache = StatsCache(cache_duration_minutes=15)

# 현재 시즌 ID 캐시
current_season_cache = {"season_id": None, "last_updated": 0}

async def test_dakgg_api_structure(nickname: str = "모묘모"):
    """DAKGG API 구조 테스트 - 실제 응답 확인"""
    encoded_nickname = urllib.parse.quote(nickname)
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://dak.gg',
        'Referer': 'https://dak.gg/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    urls_to_test = [
        f'{DAKGG_API_BASE}/players/{encoded_nickname}/profile?season=SEASON_17',
        f'{DAKGG_API_BASE}/players/{encoded_nickname}/profile?season=SEASON_16', 
        f'{DAKGG_API_BASE}/players/{encoded_nickname}/characters?season=SEASON_17&matchingMode=RANK',
        f'{DAKGG_API_BASE}/data/tiers?hl=ko',
        f'{DAKGG_API_BASE}/data/characters?hl=ko'
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(urls_to_test):
            try:
                print(f"\n{'='*60}")
                print(f"테스트 {i+1}: {url}")
                print(f"{'='*60}")
                
                async with session.get(url, headers=headers, timeout=10) as response:
                    print(f"응답 코드: {response.status}")
                    print(f"응답 헤더: {dict(response.headers)}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"응답 키: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, (list, dict)):
                                    print(f"  {key}: {type(value).__name__} (길이: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                                else:
                                    print(f"  {key}: {value}")
                    else:
                        error_text = await response.text()
                        print(f"오류 응답: {error_text[:200]}...")
                        
            except Exception as e:
                print(f"오류 발생: {e}")
            
            await asyncio.sleep(1)  # API 호출 간격

async def get_player_stats_from_dakgg(nickname: str, detailed: bool = False) -> Optional[Dict[str, Any]]:
    """닥지지 API를 사용해서 플레이어 통계 정보 가져오기"""
    try:
        # 닉네임 URL 인코딩
        encoded_nickname = urllib.parse.quote(nickname)
        
        # API URL 구성
        player_url = f'{DAKGG_API_BASE}/players/{encoded_nickname}/profile'
        tier_url = f'{DAKGG_API_BASE}/data/tiers?hl=ko'
        character_url = f'{DAKGG_API_BASE}/data/characters?hl=ko'
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            # 모든 데이터 동시 요청
            player_task = session.get(player_url, headers=headers, timeout=10)
            tier_task = session.get(tier_url, headers=headers, timeout=10)
            character_task = session.get(character_url, headers=headers, timeout=10)
            
            player_response, tier_response, character_response = await asyncio.gather(
                player_task, tier_task, character_task
            )
            
            print(f"🔍 Profile API 호출: {player_url}")
            
            if (player_response.status == 200 and 
                tier_response.status == 200):
                
                player_data = await player_response.json()
                tier_data = await tier_response.json()
                # character_data는 선택적으로 처리
                character_data = {}
                if character_response.status == 200:
                    character_data = await character_response.json()
                    print(f"✅ 캐릭터 데이터 로드 성공")
                else:
                    print(f"⚠️ 캐릭터 데이터 로드 실패: {character_response.status}")
                    # 기본 캐릭터 매핑 사용
                    character_data = {'characters': [
                        {'id': 1, 'name': '재키'}, {'id': 2, 'name': '아야'}, {'id': 3, 'name': '피오라'},
                        {'id': 4, 'name': '매그너스'}, {'id': 5, 'name': '자히르'}, {'id': 6, 'name': '나딘'},
                        {'id': 7, 'name': '현우'}, {'id': 8, 'name': '하트'}, {'id': 9, 'name': '아이솔'},
                        {'id': 10, 'name': '리 다이린'}, {'id': 11, 'name': '유키'}, {'id': 12, 'name': '혜진'},
                        {'id': 13, 'name': '쇼우'}, {'id': 14, 'name': '키아라'}, {'id': 15, 'name': '시셀라'},
                        {'id': 16, 'name': '아드리아나'}, {'id': 17, 'name': '실비아'}, {'id': 18, 'name': '아직'},
                        {'id': 19, 'name': '엠마'}, {'id': 20, 'name': '레녹스'}, {'id': 21, 'name': '로지'},
                        {'id': 22, 'name': '루크'}, {'id': 23, 'name': '캐시'}, {'id': 24, 'name': '아델라'},
                        {'id': 25, 'name': '버니스'}, {'id': 26, 'name': '바바라'}, {'id': 27, 'name': '알렉스'},
                        {'id': 28, 'name': '수아'}, {'id': 29, 'name': '레온'}, {'id': 30, 'name': '일레븐'},
                        {'id': 31, 'name': '리오'}, {'id': 32, 'name': '윌리엄'}, {'id': 33, 'name': '니키'},
                        {'id': 34, 'name': '나타폰'}, {'id': 35, 'name': '얀'}, {'id': 36, 'name': '이바'},
                        {'id': 37, 'name': '다니엘'}, {'id': 38, 'name': '제니'}, {'id': 39, 'name': '카밀로'},
                        {'id': 40, 'name': '클로에'}, {'id': 41, 'name': '요한'}, {'id': 42, 'name': '비앙카'},
                        {'id': 43, 'name': '셀린'}, {'id': 44, 'name': '에키온'}, {'id': 45, 'name': '마이'},
                        {'id': 46, 'name': '에이든'}, {'id': 47, 'name': '라우라'}, {'id': 48, 'name': '티엔'},
                        {'id': 49, 'name': '펠릭스'}, {'id': 50, 'name': '엘레나'}, {'id': 51, 'name': '프리야'},
                        {'id': 52, 'name': '아르다'}, {'id': 53, 'name': '아바'}, {'id': 54, 'name': '마커스'},
                        {'id': 55, 'name': '레니'}, {'id': 56, 'name': '츠바메'}, {'id': 57, 'name': '데비&마를렌'},
                        {'id': 58, 'name': '카티야'}, {'id': 59, 'name': '슈린'}, {'id': 60, 'name': '에스텔'},
                        {'id': 61, 'name': '피올로'}, {'id': 62, 'name': '테오도르'}, {'id': 63, 'name': '이안'},
                        {'id': 64, 'name': '로잔나'}, {'id': 65, 'name': '타지'}
                    ]}
                
                print(f"🔍 Profile 데이터 키들: {list(player_data.keys())}")
                
                # 결과 딕셔너리 초기화
                result = {
                    'nickname': nickname,
                    'tier_info': None,
                    'most_character': None,
                    'stats': {},
                    'source': 'dakgg'
                }
                
                # 현재 시즌 정보 추출
                if 'playerSeasons' not in player_data or len(player_data['playerSeasons']) == 0:
                    return None
                    
                current_season = player_data['playerSeasons'][0]
                
                # 시즌 목록 로그
                print(f"🔍 플레이어 시즌 목록 (총 {len(player_data['playerSeasons'])}개):")
                for season in player_data['playerSeasons'][:5]:  # 최근 5개만 출력
                    print(f"  - seasonId: {season.get('seasonId')}, mmr: {season.get('mmr')}, tierId: {season.get('tierId')}")
                
                # 티어 정보 처리
                mmr = current_season.get('mmr', 0)
                tier_id = current_season.get('tierId', 0)
                tier_grade_id = current_season.get('tierGradeId', 1)
                tier_mmr = current_season.get('tierMmr', 0)
                
                # 티어 이름 및 이미지 찾기
                tier_name = '언랭크'
                tier_image = None
                for tier in tier_data.get('tiers', []):
                    if tier['id'] == tier_id:
                        tier_name = tier['name']
                        tier_image = tier.get('imageUrl') or tier.get('image') or tier.get('icon')
                        print(f"🔍 찾은 티어 데이터: {tier}")
                        break
                
                # 티어 등급 매핑
                grade_names = {1: '1', 2: '2', 3: '3', 4: '4'}
                grade_name = grade_names.get(tier_grade_id, '1')
                
                if tier_id == 0:
                    result['tier_info'] = f'{tier_name} (MMR {mmr})'
                else:
                    result['tier_info'] = f'{tier_name} {grade_name} {tier_mmr} RP (MMR {mmr})'
                
                result['tier_image_url'] = tier_image
                result['mmr'] = mmr
                result['lp'] = tier_mmr
                
                # 통계 정보 추출 (playerSeasonOverviews에서)
                season_overviews = player_data.get('playerSeasonOverviews', [])
                rank_stats = None
                
                # RANK 모드 통계 찾기 (matchingModeId가 0인 것이 랭크)
                for overview in season_overviews:
                    if overview.get('seasonId') == 33 and overview.get('matchingModeId') == 0:
                        rank_stats = overview
                        break
                
                if rank_stats:
                    result['stats'] = {
                        'total_games': rank_stats.get('play', 0),
                        'wins': rank_stats.get('win', 0),
                        'winrate': round((rank_stats.get('win', 0) / max(rank_stats.get('play', 1), 1)) * 100, 1),
                        'avg_rank': round(rank_stats.get('place', 0) / max(rank_stats.get('play', 1), 1), 1),
                        'avg_kills': round(rank_stats.get('playerKill', 0) / max(rank_stats.get('play', 1), 1), 1),
                        'avg_team_kills': round(rank_stats.get('teamKill', 0) / max(rank_stats.get('play', 1), 1), 1)
                    }
                
                # 모스트 캐릭터 정보 추출
                most_characters = []
                print(f"🔍 playerSeasonOverviews 개수: {len(season_overviews)}")
                
                # 디버그: 시즌 33 데이터 확인
                season_33_data = [o for o in season_overviews if o.get('seasonId') == 33]
                print(f"🔍 시즌 33 데이터 개수: {len(season_33_data)}")
                for data in season_33_data[:2]:  # 처음 2개만 출력
                    print(f"🔍 전체 데이터 구조 키들: {list(data.keys())}")
                    print(f"  - matchingModeId: {data.get('matchingModeId')}, play: {data.get('play', 0)}")
                    if 'characterStats' in data:
                        char_stats = data['characterStats']
                        print(f"  - characterStats 타입: {type(char_stats)}, 길이: {len(char_stats) if isinstance(char_stats, (list, dict)) else 'N/A'}")
                        if isinstance(char_stats, list) and char_stats:
                            print(f"  - 첫번째 캐릭터 데이터: {char_stats[0]}")
                        elif isinstance(char_stats, dict):
                            print(f"  - characterStats 키들: {list(char_stats.keys())}")
                
                # characterStats에서 캐릭터별 데이터 추출
                for overview in season_overviews:
                    if overview.get('seasonId') == 33 and overview.get('matchingModeId') == 0:
                        char_stats_list = overview.get('characterStats', [])
                        print(f"🔍 랭크 데이터에서 캐릭터 {len(char_stats_list)}개 발견")
                        
                        for char_stat in char_stats_list:
                            char_id = char_stat.get('key')
                            char_name = None
                            
                            # 캐릭터 이름 찾기
                            for char in character_data.get('characters', []):
                                if char['id'] == char_id:
                                    char_name = char['name']
                                    break
                            
                            if char_name and char_stat.get('play', 0) > 0:
                                games = char_stat.get('play', 0)
                                wins = char_stat.get('win', 0)
                                winrate = round((wins / max(games, 1)) * 100, 1)
                                avg_rank = round(char_stat.get('place', 0) / max(games, 1), 1)
                                avg_kills = round(char_stat.get('playerKill', 0) / max(games, 1), 1)
                                avg_assists = round(char_stat.get('playerAssistant', 0) / max(games, 1), 1)
                                avg_damage = round(char_stat.get('damageToPlayer', 0) / max(games, 1), 1)
                                
                                char_info = {
                                    'name': char_name,
                                    'games': games,
                                    'wins': wins,
                                    'winrate': winrate,
                                    'avg_rank': avg_rank,
                                    'avg_kills': avg_kills,
                                    'avg_assists': avg_assists,
                                    'avg_damage': avg_damage,
                                    'top2': char_stat.get('top2', 0),
                                    'top3': char_stat.get('top3', 0)
                                }
                                most_characters.append(char_info)
                                print(f"✅ 캐릭터 추가: {char_name} ({games}게임, {winrate}% 승률, {avg_rank}등, {avg_kills}킬)")
                
                # 게임 수 기준으로 정렬
                most_characters.sort(key=lambda x: x['games'], reverse=True)
                result['most_characters'] = most_characters[:10]  # 상위 10개
                
                if most_characters:
                    print(f"✅ playerSeasonOverviews에서 캐릭터 통계 {len(most_characters)}개 로드")
                
                # 캐시 저장 (detailed가 아닌 경우만)
                if not detailed:
                    stats_cache.set(nickname, result)
                
                return result
            else:
                print(f"❌ API 호출 실패 - Player: {player_response.status}, Tier: {tier_response.status}, Character: {character_response.status}")
                return None
            
    except Exception as e:
        print(f"❌ DAKGG API 오류: {e}")
        return None

async def get_tier_info_from_dakgg(nickname: str) -> Optional[str]:
    """DAKGG에서 티어 정보만 빠르게 조회"""
    stats = await get_player_stats_from_dakgg(nickname)
    return stats.get('tier_info') if stats else None

async def get_user_by_nickname_er(nickname: str) -> Dict[str, Any]:
    """이터널 리턴 공식 API - 닉네임으로 유저 정보 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            params = {
                'query': str(nickname)
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/user/nickname"
            
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 404:
                    raise PlayerStatsError("player_not_found")
                elif response.status != 200:
                    raise PlayerStatsError(f"request_failed_{response.status}")
                
                return await response.json()
                
    except PlayerStatsError:
        raise
    except Exception as e:
        print(f"닉네임 조회 중 오류: {e}")
        raise PlayerStatsError(f"nickname_search_failed: {str(e)}")

async def get_user_stats_er(user_num: str, season_id: str = "17") -> Dict[str, Any]:
    """이터널 리턴 공식 API - 유저 통계 정보 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/user/stats/{str(user_num)}/{str(season_id)}"
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 404:
                    raise PlayerStatsError("stats_not_found")
                elif response.status != 200:
                    raise PlayerStatsError(f"stats_request_failed_{response.status}")
                
                return await response.json()
                
    except PlayerStatsError:
        raise
    except Exception as e:
        print(f"통계 조회 중 오류: {e}")
        raise PlayerStatsError(f"stats_search_failed: {str(e)}")

async def get_user_rank_er(user_num: str, season_id: str = "17", matching_team_mode: str = "3") -> Dict[str, Any]:
    """이터널 리턴 공식 API - 유저 랭킹 정보 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/rank/{str(user_num)}/{str(season_id)}/{str(matching_team_mode)}"
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    print(f"랭킹 조회 실패: {response.status}")
                    return None
                
                return await response.json()
                
    except Exception as e:
        print(f"랭킹 조회 중 오류: {e}")
        return None

async def get_user_recent_games_er(user_num: str, next_index: str = "0") -> Dict[str, Any]:
    """이터널 리턴 공식 API - 유저 최근 게임 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            params = {}
            if next_index and str(next_index) != "0":
                params['next'] = str(next_index)
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/user/games/{str(user_num)}"
            
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                print(f"🔍 최근게임 API 응답: {response.status}")
                if response.status == 404:
                    print(f"⚠️ 최근게임 404: 데이터 없음")
                    return None
                elif response.status == 429:
                    print(f"⚠️ 최근게임 429: rate limit exceeded")
                    return None
                elif response.status != 200:
                    print(f"⚠️ 최근 게임 조회 실패: {response.status}")
                    return None
                
                response_data = await response.json()
                print(f"✅ 최근게임 성공, 키: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not dict'}")
                return response_data
                
    except Exception as e:
        print(f"최근 게임 조회 중 오류: {e}")
        return None

async def get_game_detail_er(game_id: str) -> Dict[str, Any]:
    """이터널 리턴 공식 API - 게임 상세 정보 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/games/{str(game_id)}"
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    print(f"게임 상세 조회 실패: {response.status}")
                    return None
                
                return await response.json()
                
    except Exception as e:
        print(f"게임 상세 조회 중 오류: {e}")
        return None

async def get_meta_data_er(meta_type: str = "Character", max_retries: int = 3) -> Dict[str, Any]:
    """이터널 리턴 공식 API - 메타 데이터 조회 (캐릭터, 아이템 등)"""
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': str(ETERNAL_RETURN_API_KEY),
                    'Accept': 'application/json'
                }
                
                url = f"{ETERNAL_RETURN_API_BASE}/v1/data/{meta_type}"
                
                async with session.get(url, headers=headers, timeout=15) as response:
                    print(f"🔍 메타데이터 {meta_type} API 응답: {response.status} (시도 {retry_count + 1}/{max_retries})")
                    
                    if response.status == 429:
                        print(f"⚠️ Rate limit - 3초 대기 후 재시도")
                        await asyncio.sleep(3)
                        retry_count += 1
                        continue
                    elif response.status == 404:
                        print(f"⚠️ 메타데이터 404: {meta_type} 데이터 없음")
                        return None
                    elif response.status != 200:
                        print(f"⚠️ 메타데이터 조회 실패: {response.status}")
                        return None
                    
                    response_data = await response.json()
                    print(f"✅ 메타데이터 {meta_type} 성공")
                    return response_data
                    
        except Exception as e:
            print(f"메타데이터 조회 중 오류: {e}")
            retry_count += 1
            if retry_count < max_retries:
                await asyncio.sleep(2)
            else:
                return None
    
    return None

async def get_current_season_id() -> str:
    """현재 활성화된 시즌 ID를 가져오는 함수 (캐싱 적용)"""
    import time
    current_time = time.time()
    
    # 캐시된 시즌 ID가 있고 5분 이내라면 사용
    if (current_season_cache["season_id"] is not None and 
        current_time - current_season_cache["last_updated"] < 300):  # 5분
        return current_season_cache["season_id"]
    
    try:
        season_meta = await get_meta_data_er("Season")
        if season_meta and 'data' in season_meta:
            # 가장 최신 시즌 찾기 (ID가 가장 큰 것)
            seasons = season_meta['data']
            if seasons:
                current_season = max(seasons, key=lambda x: int(x.get('seasonID', 0)))
                season_id = str(current_season.get('seasonID', '17'))
                
                # 캐시 업데이트
                current_season_cache["season_id"] = season_id
                current_season_cache["last_updated"] = current_time
                
                print(f"✅ 현재 시즌 ID: {season_id}")
                return season_id
    
    except Exception as e:
        print(f"❌ 시즌 ID 조회 실패: {e}")
    
    # 실패 시 기본값 반환
    return "17"

async def get_simple_player_stats_only_tier(nickname: str) -> str:
    """간단한 티어 정보만 조회"""
    try:
        user_info = await get_user_by_nickname_er(nickname)
        if not user_info or 'user' not in user_info:
            return "플레이어를 찾을 수 없습니다."
        
        user_num = user_info['user']['userNum']
        current_season = await get_current_season_id()
        
        # 최근 게임 데이터로 티어 정보 확인
        recent_games = await get_user_recent_games_er(user_num)
        if not recent_games or 'userGames' not in recent_games:
            return "게임 데이터를 찾을 수 없습니다."
        
        # 랭크 게임 찾기
        rank_games = [game for game in recent_games['userGames'] if game.get('matchingMode') == 3]
        
        if rank_games:
            latest_rank_game = rank_games[0]
            # 최신 랭크 게임에서 MMR 정보 추출
            mmr_after = latest_rank_game.get('mmrAfter', 0)
            
            if mmr_after > 0:
                # 티어 메타데이터로 티어명 변환
                tier_meta = await get_meta_data_er("MatchingQueueTier")
                if tier_meta and 'data' in tier_meta:
                    tiers = tier_meta['data']
                    for tier in tiers:
                        mmr_range = tier.get('mmrRange', {})
                        if mmr_range.get('from', 0) <= mmr_after <= mmr_range.get('to', 9999):
                            return f"{tier.get('name', 'Unknown')} ({mmr_after} MMR)"
                
                return f"{mmr_after} MMR"
            
        return "랭크 게임 데이터가 없습니다."
        
    except PlayerStatsError as e:
        if "user_not_found" in str(e):
            return "플레이어를 찾을 수 없습니다."
        elif "403" in str(e):
            return "API 권한이 없습니다."
        else:
            return f"조회 중 오류가 발생했습니다: {e}"
    except Exception as e:
        print(f"❌ 티어 조회 중 예상치 못한 오류: {e}")
        return "서비스에 일시적인 문제가 발생했습니다."

async def get_simple_player_stats(nickname: str) -> Dict[str, Any]:
    """플레이어의 간단한 통계 정보를 조회하는 함수"""
    try:
        # 먼저 DAKGG에서 시도
        dakgg_stats = await get_player_stats_from_dakgg(nickname)
        if dakgg_stats:
            return {
                'success': True,
                'source': 'dakgg',
                'nickname': nickname,
                'tier_info': dakgg_stats.get('tier_info', '정보 없음'),
                'mmr': dakgg_stats.get('mmr', 0),
                'lp': dakgg_stats.get('lp', 0),
                'most_characters': dakgg_stats.get('most_characters', []),
                'raw_data': dakgg_stats
            }
        
        # DAKGG 실패 시 공식 API 사용
        user_info = await get_user_by_nickname_er(nickname)
        if not user_info or 'user' not in user_info:
            return {
                'success': False,
                'error': 'user_not_found',
                'message': '플레이어를 찾을 수 없습니다.'
            }
        
        user_num = user_info['user']['userNum']
        current_season = await get_current_season_id()
        
        # 최근 게임 조회
        recent_games = await get_user_recent_games_er(user_num)
        if not recent_games or 'userGames' not in recent_games:
            return {
                'success': False,
                'error': 'no_games',
                'message': '게임 데이터를 찾을 수 없습니다.'
            }
        
        # 랭크 게임 필터링
        rank_games = [game for game in recent_games['userGames'] if game.get('matchingMode') == 3]
        
        # 현재 티어 정보
        tier_info = "Unranked"
        mmr = 0
        
        if rank_games:
            latest_rank_game = rank_games[0]
            mmr = latest_rank_game.get('mmrAfter', 0)
            
            # 티어 메타데이터로 티어명 변환
            tier_meta = await get_meta_data_er("MatchingQueueTier")
            if tier_meta and 'data' in tier_meta:
                tiers = tier_meta['data']
                for tier in tiers:
                    mmr_range = tier.get('mmrRange', {})
                    if mmr_range.get('from', 0) <= mmr <= mmr_range.get('to', 9999):
                        tier_info = tier.get('name', 'Unknown')
                        break
        
        # 최근 10게임 통계 계산
        recent_stats = calculate_recent_stats(rank_games[:10])
        
        return {
            'success': True,
            'source': 'eternal_return_api',
            'nickname': nickname,
            'tier_info': tier_info,
            'mmr': mmr,
            'recent_stats': recent_stats,
            'total_games': len(rank_games),
            'raw_data': {
                'user_info': user_info,
                'recent_games': recent_games
            }
        }
        
    except PlayerStatsError as e:
        error_message = str(e)
        if "user_not_found" in error_message:
            return {
                'success': False,
                'error': 'user_not_found',
                'message': '플레이어를 찾을 수 없습니다.'
            }
        elif "403" in error_message:
            return {
                'success': False,
                'error': 'api_forbidden',
                'message': 'API 권한이 없습니다.'
            }
        else:
            return {
                'success': False,
                'error': 'api_error',
                'message': f'API 오류: {error_message}'
            }
    except Exception as e:
        print(f"❌ 전적 조회 중 예상치 못한 오류: {e}")
        return {
            'success': False,
            'error': 'unexpected_error',
            'message': '서비스에 일시적인 문제가 발생했습니다.'
        }

def calculate_recent_stats(games: List[Dict]) -> Dict[str, Any]:
    """최근 게임들의 통계를 계산"""
    if not games:
        return {
            'total_games': 0,
            'wins': 0,
            'winrate': 0,
            'avg_rank': 0,
            'avg_kills': 0,
            'avg_assists': 0
        }
    
    total_games = len(games)
    wins = sum(1 for game in games if game.get('gameRank', 999) == 1)
    total_kills = sum(game.get('playerKill', 0) for game in games)
    total_assists = sum(game.get('playerAssistant', 0) for game in games)
    total_rank = sum(game.get('gameRank', 999) for game in games)
    
    return {
        'total_games': total_games,
        'wins': wins,
        'winrate': round((wins / total_games) * 100, 1) if total_games > 0 else 0,
        'avg_rank': round(total_rank / total_games, 1) if total_games > 0 else 0,
        'avg_kills': round(total_kills / total_games, 1) if total_games > 0 else 0,
        'avg_assists': round(total_assists / total_games, 1) if total_games > 0 else 0
    }

async def get_premium_analysis(nickname: str):
    """프리미엄 분석을 위한 데이터 수집"""
    try:
        # 기본 전적 정보
        basic_stats = await get_simple_player_stats(nickname)
        if not basic_stats['success']:
            return None
            
        # DAKGG에서 상세 정보 추가 수집
        detailed_dakgg = await get_player_stats_from_dakgg(nickname, detailed=True)
        
        # 공식 API 유저 정보
        user_info = None
        user_num = None
        recent_games = None
        
        try:
            user_info = await get_user_by_nickname_er(nickname)
            if user_info and 'user' in user_info:
                user_num = user_info['user']['userNum']
                recent_games = await get_user_recent_games_er(user_num)
        except:
            pass  # 공식 API 실패 시 무시
        
        analysis_data = {
            'nickname': nickname,
            'user_num': user_num,
            'stats': basic_stats,
            'detailed_dakgg': detailed_dakgg,
            'recent_games': recent_games,
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis_data
        
    except Exception as e:
        print(f"❌ 프리미엄 분석 데이터 수집 실패: {e}")
        return None