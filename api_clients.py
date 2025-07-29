import asyncio
import aiohttp
import urllib.parse
import hashlib
import json
import os
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

# 시즌 매핑 전역 변수
_season_mapping = None

def load_season_mapping():
    """시즌 매핑 JSON 파일 로드"""
    global _season_mapping
    if _season_mapping is None:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, 'season_mapping.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                _season_mapping = json.load(f)
            print("✅ 시즌 매핑 JSON 로드 완료")
        except Exception as e:
            print(f"❌ 시즌 매핑 JSON 로드 실패: {e}")
            # 폴백: 기본 매핑
            _season_mapping = {
                "season_ids": {
                    "33": {"api_param": "SEASON_17", "name": "시즌 8"},
                    "31": {"api_param": "SEASON_16", "name": "시즌 7"},
                    "29": {"api_param": "SEASON_15", "name": "시즌 6"}
                }
            }
    return _season_mapping

def get_season_api_param(season_id: int) -> str:
    """시즌 ID를 API 파라미터로 변환"""
    mapping = load_season_mapping()
    season_info = mapping["season_ids"].get(str(season_id))
    if season_info:
        return season_info["api_param"]
    return "SEASON_17"  # 기본값

def get_season_name(season_id: int) -> str:
    """시즌 ID를 시즌 이름으로 변환"""
    mapping = load_season_mapping()
    season_info = mapping["season_ids"].get(str(season_id))
    if season_info:
        return season_info["name"]
    return f"Season {season_id}"  # 기본값

def get_season_id_by_key(season_key: str) -> int:
    """시즌 키를 시즌 ID로 변환 (현재는 간단한 매핑만 제공)"""
    # 주요 시즌 키만 매핑 (필요에 따라 확장 가능)
    key_mapping = {
        "current": 33,    # 현재 시즌 (시즌 8)
        "previous": 31,   # 이전 시즌 (시즌 7)
        "season6": 29,    # 시즌 6
        "season5": 27,    # 시즌 5
        "season4": 25,    # 시즌 4
        "season3": 23,    # 시즌 3
        "season2": 21,    # 시즌 2
        "season1": 19     # 시즌 1
    }
    return key_mapping.get(season_key, 33)  # 기본값은 현재 시즌

async def get_player_season_list_simple(nickname: str):
    """플레이어의 시즌 목록만 간단히 조회 (시즌 선택용)"""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season=SEASON_17"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print(f"🔍 시즌 목록 조회 API 호출: {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"🌐 응답 상태: {response.status}")
                if response.status != 200:
                    print(f"❌ 플레이어 시즌 목록 조회 실패: {response.status}")
                    return None
                    
                data = await response.json()
                
                # 시즌 정보만 추출
                result = {
                    'playerSeasons': data.get('playerSeasons', []),
                    'playerSeasonOverviews': data.get('playerSeasonOverviews', [])
                }
                
                print(f"✅ 시즌 목록 조회 성공: playerSeasons={len(result['playerSeasons'])}, playerSeasonOverviews={len(result['playerSeasonOverviews'])}")
                return result
                
    except Exception as e:
        print(f"❌ 플레이어 시즌 목록 조회 중 오류: {e}")
        return None

async def test_dakgg_api_structure(nickname: str = "모묘모"):
    # 시즌 정보 확인
    await get_player_season_info(nickname)
    
    # 시즌1 테스트 (수정된 ID: 19)
    print(f"\n=== 시즌1 (ID: 19) 테스트 ===")
    season1_result = await get_season_tier_from_dakgg(nickname, 19)
    print(f"시즌1 결과: {season1_result}")
    
    # 모든 시즌 티어 정보 다시 테스트
    print(f"\n=== 수정된 시즌 티어 정보 ===")
    all_tiers = await get_player_all_season_tiers(nickname)
    for season_key, season_id in SEASON_IDS.items():
        tier_info = all_tiers.get(season_id, "데이터 없음")
        print(f"{season_key} (ID: {season_id}): {tier_info}")
    
    # 시즌 매핑 분석
    print(f"\n=== 시즌 매핑 분석 ===")
    
    # 다양한 SEASON_X 값으로 테스트
    for season_num in range(10, 18):  # SEASON_10 ~ SEASON_17
        try:
            encoded_nickname = urllib.parse.quote(nickname)
            url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season=SEASON_{season_num}"
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        current_season = data.get('playerSeasons', [{}])[0]  # 첫 번째가 현재 시즌
                        season_id = current_season.get('seasonId')
                        tier_id = current_season.get('tierId')
                        tier_grade = current_season.get('tierGradeId')
                        
                        print(f"SEASON_{season_num} → seasonId: {season_id}, tierId: {tier_id}, grade: {tier_grade}")
                        
                        if season_num == 17:  # 현재 시즌 자세히 분석
                            print(f"  현재 시즌 상세:")
                            print(f"  첫 5개 시즌 ID: {[s.get('seasonId') for s in data.get('playerSeasons', [])[:5]]}")
                    else:
                        print(f"SEASON_{season_num} → 응답 실패: {response.status}")
        except Exception as e:
            print(f"SEASON_{season_num} → 오류: {e}")
    
    # 시즌 매핑 추정 및 검증
    print(f"\n=== 시즌 매핑 추정 ===")
    
    # 현재 시즌이 33이고 Season 8이라면
    # Season 7 = 31 (확인됨)
    # Season 6 = 30 (확인됨) 
    # Season 5 = 29 (확인됨)
    # 그러면 패턴이 있는지 확인
    
    estimated_mapping = {
        33: "Season 8",
        32: "Season ? (프리시즌?)",
        31: "Season 7", 
        30: "Season 6",
        29: "Season 5",
        28: "Season ? (프리시즌?)",
        27: "Season ? (프리시즌?)", 
        26: "Season ?",
        25: "Season ? (프리시즌?)",
        24: "Season ?",
        23: "Season ?",
        22: "Season ?",
        21: "Season 4 (?)",
        20: "Season 3 또는 Season 2 (?)",
        19: "Season 1 (사용자 골드 확인)",
        18: "Season 0 또는 초기 시즌 (?)"
    }
    
    for season_id, estimated in estimated_mapping.items():
        print(f"seasonId {season_id}: {estimated}")
    
    # 시즌 정보 API 호출
    print(f"\n=== 시즌 정보 API 확인 ===")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://er.dakgg.io/api/v1/seasons", headers={
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }) as response:
                if response.status == 200:
                    seasons_data = await response.json()
                    print(f"시즌 API 응답: {seasons_data}")
                else:
                    print(f"시즌 API 실패: {response.status}")
                    
    except Exception as e:
        print(f"시즌 API 오류: {e}")
    
    # 티어 이미지 테스트
    print(f"\n=== 티어 이미지 테스트 ===")
    
    # 시즌1 골드4 이미지 테스트 
    season1_info, season1_image = await get_season_tier_with_image(nickname, 19)
    print(f"시즌1: {season1_info}")
    print(f"시즌1 이미지: {season1_image}")
    
    # 현재 시즌 다이아몬드4 이미지 테스트
    current_info, current_image = await get_season_tier_with_image(nickname, 33)
    print(f"현재 시즌: {current_info}")
    print(f"현재 시즌 이미지: {current_image}")
    
    # 언랭크 시즌 테스트
    unranked_info, unranked_image = await get_season_tier_with_image(nickname, 21)
    print(f"언랭크 시즌: {unranked_info}")
    print(f"언랭크 이미지: {unranked_image}")
    
    # 티어 정보 API 확인
    print(f"\n=== 티어 정보 API 확인 ===")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://er.dakgg.io/api/v1/data/tiers?hl=ko", headers={
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }) as response:
                if response.status == 200:
                    tiers_data = await response.json()
                    print("실제 티어 정보:")
                    for tier in tiers_data.get('tiers', []):
                        tier_id = tier.get('id')
                        tier_name = tier.get('name')
                        tier_image = tier.get('image')
                        print(f"  ID: {tier_id}, Name: {tier_name}, Image: {tier_image}")
                else:
                    print(f"티어 API 실패: {response.status}")
    except Exception as e:
        print(f"티어 API 오류: {e}")
        
    return


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
                
                # characterStats에서 캐릭터별 데이터 추출 - 중복 제거를 위해 딕셔너리 사용
                char_dict = {}
                
                for overview in season_overviews:
                    if overview.get('seasonId') == 33 and overview.get('matchingModeId') == 0:
                        char_stats_list = overview.get('characterStats', [])
                        print(f"🔍 랭크 데이터에서 캐릭터 {len(char_stats_list)}개 발견")
                        
                        for char_stat in char_stats_list:
                            char_id = char_stat.get('key')
                            games = char_stat.get('play', 0)
                            
                            # 게임 수가 0인 경우 스킵
                            if games <= 0:
                                continue
                                
                            char_name = None
                            char_image_url = None
                            
                            # 캐릭터 이름과 이미지 찾기
                            for char in character_data.get('characters', []):
                                if char['id'] == char_id:
                                    char_name = char['name']
                                    char_image_url = char.get('imageUrl') or char.get('image')
                                    break
                            
                            if char_name:
                                # 중복 캐릭터 처리 - 게임 수가 더 많은 데이터 사용
                                if char_name in char_dict:
                                    if games > char_dict[char_name]['games']:
                                        # 더 많은 게임 수 데이터로 업데이트
                                        print(f"🔄 {char_name} 업데이트: {char_dict[char_name]['games']}게임 → {games}게임")
                                    else:
                                        # 기존 데이터가 더 좋으므로 스킵
                                        continue
                                
                                wins = char_stat.get('win', 0)
                                winrate = round((wins / max(games, 1)) * 100, 1)
                                avg_rank = round(char_stat.get('place', 0) / max(games, 1), 1)
                                avg_kills = round(char_stat.get('playerKill', 0) / max(games, 1), 1)
                                avg_assists = round(char_stat.get('playerAssistant', 0) / max(games, 1), 1)
                                avg_damage = round(char_stat.get('damageToPlayer', 0) / max(games, 1), 1)
                                
                                char_dict[char_name] = {
                                    'name': char_name,
                                    'games': games,
                                    'wins': wins,
                                    'winrate': winrate,
                                    'avg_rank': avg_rank,
                                    'avg_kills': avg_kills,
                                    'avg_assists': avg_assists,
                                    'avg_damage': avg_damage,
                                    'top2': char_stat.get('top2', 0),
                                    'top3': char_stat.get('top3', 0),
                                    'image_url': char_image_url
                                }
                                print(f"✅ 캐릭터 추가/업데이트: {char_name} ({games}게임, {winrate}% 승률)")
                
                # 딕셔너리를 리스트로 변환하고 게임 수 기준으로 정렬
                most_characters = list(char_dict.values())
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

async def get_season_tier_from_dakgg(nickname: str, season_id: int):
    """DAKGG에서 특정 시즌 티어 정보 조회 (숫자 ID 형식)"""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        # JSON에서 시즌 API 파라미터 가져오기
        season_param = get_season_api_param(season_id)
        url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season={season_param}"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return None
                    
                data = await response.json()
                player_seasons = data.get('playerSeasons', [])
                
                # 해당 시즌 찾기 (숫자 ID 매칭)
                for season in player_seasons:
                    if season.get('seasonId') == season_id:
                        mmr = season.get('mmr', 0)
                        tier_id = season.get('tierId')
                        tier_grade_id = season.get('tierGradeId')
                        tier_mmr = season.get('tierMmr', 0)
                        
                        # 티어 이름 매핑 (간단화)
                        tier_names = {
                            1: "아이언", 2: "브론즈", 3: "실버", 4: "골드", 5: "플래티넘",
                            6: "다이아몬드", 7: "미스릴", 60: "아데만타이트", 65: "마스터", 66: "임모탈"
                        }
                        
                        tier_name = tier_names.get(tier_id, "언랭크")
                        
                        if tier_name != "언랭크" and tier_grade_id:
                            return f"{tier_name} {tier_grade_id} {tier_mmr} RP (MMR {mmr})"
                        elif mmr > 0:
                            return f"{tier_name} (MMR {mmr})"
                        else:
                            return "언랭크"
                
                return None
                
    except Exception as e:
        print(f"❌ 시즌 {season_id} 티어 조회 실패: {e}")
        return None

# DEPRECATED: 이제 JSON 파일의 get_season_id_by_key() 함수 사용
# 하위 호환성을 위해 남겨둠 - 추후 제거 예정
def get_legacy_season_ids():
    """하위 호환성을 위한 SEASON_IDS 딕셔너리 반환"""
    # 기존 코드와의 호환성을 위한 간단한 매핑
    return {
        "current": 33,    # 현재 시즌 (시즌 8)
        "previous": 31,   # 이전 시즌 (시즌 7)
        "season6": 29,    # 시즌 6
        "season5": 27,    # 시즌 5
        "season4": 25,    # 시즌 4
        "season3": 23,    # 시즌 3
        "season2": 21,    # 시즌 2
        "season1": 19     # 시즌 1
    }

# 하위 호환성을 위한 전역 변수 (지연 로딩)
def __getattr__(name):
    if name == 'SEASON_IDS':
        return get_legacy_season_ids()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

async def get_player_season_info(nickname: str):
    """플레이어의 모든 시즌 정보 조회"""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season=SEASON_17"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    player_seasons = data.get('playerSeasons', [])
                    
                    print(f"\n=== {nickname}님의 시즌 정보 ===")
                    print(f"총 {len(player_seasons)}개 시즌 데이터")
                    
                    # 모든 시즌 ID 출력
                    season_ids = [season.get('seasonId') for season in player_seasons if season.get('seasonId')]
                    print(f"실제 시즌 ID 목록: {sorted(season_ids, reverse=True)}")
                    
                    for idx, season in enumerate(player_seasons[:8]):  # 처음 8개 출력
                        season_id = season.get('seasonId')
                        if season_id:
                            print(f"시즌 {season_id}: {list(season.keys())}")
                    
                    return player_seasons
                else:
                    print(f"❌ API 오류: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ 시즌 정보 조회 실패: {e}")
        return None

async def get_player_all_season_tiers(nickname: str):
    """플레이어의 모든 시즌 티어 정보를 미리 조회"""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        # 모든 시즌 정보를 가져오기 위해 최신 시즌으로 조회
        url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season=SEASON_17"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {}
                    
                data = await response.json()
                player_seasons = data.get('playerSeasons', [])
                
                # 티어 이름 매핑 (실제 API 기준)
                tier_names = {
                    0: "언랭크", 1: "아이언", 2: "브론즈", 3: "실버", 4: "골드", 5: "플래티넘",
                    6: "다이아몬드", 63: "메테오라이트", 66: "미스릴", 7: "데미갓", 8: "이터니티"
                }
                
                season_tiers = {}
                
                for season in player_seasons:
                    season_id = season.get('seasonId')
                    if not season_id:
                        continue
                        
                    tier_id = season.get('tierId')
                    tier_grade_id = season.get('tierGradeId')
                    
                    if tier_id and tier_grade_id:
                        tier_name = tier_names.get(tier_id, "언랭크")
                        season_tiers[season_id] = f"{tier_name} {tier_grade_id}"
                    else:
                        season_tiers[season_id] = "언랭크"
                
                return season_tiers
                
    except Exception as e:
        print(f"❌ 모든 시즌 티어 조회 실패: {e}")
        return {}

async def get_tier_image_url(tier_id: int):
    """DAKGG API에서 실제 티어 이미지 URL 가져오기"""
    try:
        # DAKGG 티어 API 호출
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://er.dakgg.io/api/v1/data/tiers?hl=ko", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    tiers = data.get('tiers', [])
                    
                    # 매칭되는 티어 찾기
                    for tier in tiers:
                        if tier.get('id') == tier_id:
                            # 여러 가능한 키 확인
                            image_url = tier.get('imageUrl') or tier.get('image') or tier.get('icon') or tier.get('img')
                            if image_url:
                                # //로 시작하는 URL을 https로 변환
                                if image_url.startswith('//'):
                                    image_url = 'https:' + image_url
                                print(f"✅ 티어 {tier_id} 이미지 URL 발견: {image_url}")
                                return image_url
                    
                    # 언랭크나 매칭 안되는 경우 첫 번째 티어 이미지 사용  
                    if tiers:
                        first_tier = tiers[0]
                        fallback_url = first_tier.get('imageUrl') or first_tier.get('image') or first_tier.get('icon')
                        if fallback_url:
                            # //로 시작하는 URL을 https로 변환
                            if fallback_url.startswith('//'):
                                fallback_url = 'https:' + fallback_url
                            print(f"⚠️ 티어 {tier_id} 매칭 실패, 기본 이미지 사용: {fallback_url}")
                            return fallback_url
                
                print(f"❌ 티어 API 호출 실패: {response.status}")
        
        # API 실패 시 DAKGG CDN 직접 URL 사용
        fallback_images = {
            0: "https://cdn.dak.gg/assets/er/images/rank/full/0.png",  # 언랭크
            1: "https://cdn.dak.gg/assets/er/images/rank/full/1.png",  # 아이언  
            2: "https://cdn.dak.gg/assets/er/images/rank/full/2.png",  # 브론즈
            3: "https://cdn.dak.gg/assets/er/images/rank/full/3.png",  # 실버
            4: "https://cdn.dak.gg/assets/er/images/rank/full/4.png",  # 골드
            5: "https://cdn.dak.gg/assets/er/images/rank/full/5.png",  # 플래티넘
            6: "https://cdn.dak.gg/assets/er/images/rank/full/6.png",  # 다이아몬드
            63: "https://cdn.dak.gg/assets/er/images/rank/full/63.png", # 메테오라이트
            66: "https://cdn.dak.gg/assets/er/images/rank/full/66.png", # 미스릴
            7: "https://cdn.dak.gg/assets/er/images/rank/full/7.png",  # 데미갓
            8: "https://cdn.dak.gg/assets/er/images/rank/full/8.png"   # 이터니티
        }
        
        fallback_url = fallback_images.get(tier_id, fallback_images.get(0))
        print(f"⚠️ API 실패, 기본 URL 사용: {fallback_url}")
        return fallback_url
        
    except Exception as e:
        print(f"❌ 티어 이미지 URL 조회 실패: {e}")
        return "https://dak.gg/er/images/ui/ranking/tier_medal_00.png"

async def get_season_characters_from_dakgg(nickname: str, season_id: int):
    """DAKGG에서 특정 시즌의 캐릭터 통계 조회 (프로필 API 활용, 개선됨)"""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        # JSON에서 시즌 API 파라미터 가져오기
        season_param = get_season_api_param(season_id)
        url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season={season_param}"
        
        print(f"🔍 시즌 {season_id} 캐릭터 API 호출 (프로필 활용): {url}")
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            character_data_task = session.get(f"{DAKGG_API_BASE}/data/characters?hl=ko", headers=headers)
            profile_data_task = session.get(url, headers=headers)
            
            character_response, profile_response = await asyncio.gather(character_data_task, profile_data_task)

            if profile_response.status != 200:
                print(f"❌ 시즌 {season_id} 캐릭터 데이터 조회 실패 (프로필 API): {profile_response.status}")
                return None
            
            profile_data = await profile_response.json()
            
            character_map = {}
            if character_response.status == 200:
                character_data = await character_response.json()
                for char in character_data.get('characters', []):
                    character_map[char['id']] = {
                        'name': char['name'],
                        'image_url': char.get('imageUrl') or char.get('image')
                    }
            
            season_overviews = profile_data.get('playerSeasonOverviews', [])
            
            # 해당 시즌의 통계 찾기 (랭크 우선)
            target_overview = None
            normal_overview = None
            for overview in season_overviews:
                if overview.get('seasonId') == season_id and overview.get('characterStats'):
                    if overview.get('matchingModeId') == 0:  # 0 for Rank
                        target_overview = overview
                        break  # 랭크 모드를 찾았으니 더 찾을 필요 없음
                    if not normal_overview:
                        normal_overview = overview # 다른 모드(일반 등)라도 일단 저장
            
            if not target_overview:
                target_overview = normal_overview # 랭크 없으면 일반이라도 사용

            if not target_overview:
                print(f"⚠️ 시즌 {season_id} 캐릭터 데이터 없음")
                return []

            raw_char_stats = target_overview.get('characterStats', [])
            
            # 캐릭터 데이터 정리
            character_stats = []
            for char_stat in raw_char_stats:
                if char_stat.get('play', 0) > 0:
                    char_id = char_stat.get('key')
                    char_info = character_map.get(char_id, {'name': f'Unknown_{char_id}', 'image_url': None})
                    
                    games = char_stat.get('play', 1)
                    wins = char_stat.get('win', 0)
                    
                    character_stats.append({
                        'name': char_info['name'],
                        'games': games,
                        'wins': wins,
                        'winrate': round((wins / max(games, 1)) * 100, 1),
                        'avg_rank': round(char_stat.get('place', 0) / max(games, 1), 1),
                        'avg_kills': round(char_stat.get('playerKill', 0) / max(games, 1), 1),
                        'top2': char_stat.get('top2', 0),
                        'top3': char_stat.get('top3', 0),
                        'image_url': char_info['image_url']
                    })
            
            # 게임 수 기준으로 정렬
            character_stats.sort(key=lambda x: x['games'], reverse=True)
            print(f"✅ 시즌 {season_id} 캐릭터 {len(character_stats)}개 로드 (프로필 API 활용)")
            return character_stats
            
    except Exception as e:
        print(f"❌ 시즌 {season_id} 캐릭터 조회 실패 (프로필 API 활용): {e}")
        return None

async def get_season_stats_from_dakgg(nickname: str, season_id: int):
    """DAKGG에서 특정 시즌의 통계 조회"""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        # JSON에서 시즌 API 파라미터 가져오기
        season_param = get_season_api_param(season_id)
        url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season={season_param}"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"시즌 {season_id} 통계 데이터 조회 실패: {response.status}")
                    return None
                    
                data = await response.json()
                player_season_overviews = data.get('playerSeasonOverviews', [])
                
                # 해당 시즌의 랭크 모드 통계 찾기
                season_stats = None
                for overview in player_season_overviews:
                    if (overview.get('seasonId') == season_id and 
                        overview.get('matchingModeId') == 0):  # 0이 랭크 모드
                        season_stats = overview
                        break
                
                if not season_stats:
                    print(f"시즌 {season_id} 랭크 통계 데이터 없음")
                    return None
                
                # 통계 데이터 정리
                stats = {
                    'total_games': season_stats.get('play', 0),
                    'wins': season_stats.get('win', 0),
                    'winrate': round((season_stats.get('win', 0) / max(season_stats.get('play', 1), 1)) * 100, 1),
                    'avg_rank': round(season_stats.get('place', 0) / max(season_stats.get('play', 1), 1), 1),
                    'avg_kills': round(season_stats.get('playerKill', 0) / max(season_stats.get('play', 1), 1), 1),
                    'avg_team_kills': round(season_stats.get('teamKill', 0) / max(season_stats.get('play', 1), 1), 1),
                    'top2': season_stats.get('top2', 0),
                    'top3': season_stats.get('top3', 0)
                }
                
                print(f"✅ 시즌 {season_id} 통계 로드: {stats['total_games']}게임")
                return stats
                
    except Exception as e:
        print(f"❌ 시즌 {season_id} 통계 조회 실패: {e}")
        return None

async def get_season_tier_with_image(nickname: str, season_id: int):
    """특정 시즌의 티어 정보와 이미지 URL을 함께 반환"""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        # JSON에서 시즌 API 파라미터 가져오기
        season_param = get_season_api_param(season_id)
        url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season={season_param}"
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dak.gg',
            'Referer': 'https://dak.gg/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return None, None
                    
                data = await response.json()
                player_seasons = data.get('playerSeasons', [])
                
                # 해당 시즌 찾기
                for season in player_seasons:
                    if season.get('seasonId') == season_id:
                        mmr = season.get('mmr', 0)
                        tier_id = season.get('tierId')
                        tier_grade_id = season.get('tierGradeId')
                        tier_mmr = season.get('tierMmr', 0)
                        
                        # 티어 이름 매핑 (실제 API 기준)
                        tier_names = {
                            0: "언랭크", 1: "아이언", 2: "브론즈", 3: "실버", 4: "골드", 5: "플래티넘",
                            6: "다이아몬드", 63: "메테오라이트", 66: "미스릴", 7: "데미갓", 8: "이터니티"
                        }
                        
                        tier_name = tier_names.get(tier_id, "언랭크")
                        tier_image_url = await get_tier_image_url(tier_id)
                        
                        if tier_name != "언랭크" and tier_grade_id:
                            tier_text = f"{tier_name} {tier_grade_id} {tier_mmr} RP (MMR {mmr})"
                        elif mmr > 0:
                            tier_text = f"{tier_name} (MMR {mmr})"
                        else:
                            tier_text = "언랭크"
                            tier_image_url = await get_tier_image_url(None)  # 언랭크 이미지
                        
                        return tier_text, tier_image_url
                
                return None, None
                
    except Exception as e:
        print(f"❌ 시즌 {season_id} 티어+이미지 조회 실패: {e}")
        return None, None