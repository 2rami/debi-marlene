import os
import asyncio
import random
import aiofiles
from datetime import datetime, timedelta
import re
from typing import List, Optional, Dict, Any
import urllib.parse
import json
import hashlib

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from googleapiclient.discovery import build
import schedule
import aiohttp
from bs4 import BeautifulSoup

load_dotenv()

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# 캐릭터 설정
characters = {
    "debi": {
        "name": "데비",
        "image": "https://raw.githubusercontent.com/2rami/debi-marlene/main/assets/debi.png",
        "color": 0x0000FF,  # 진한 파랑
        "ai_prompt": """너는 이터널리턴의 데비(Debi)야. 마를렌과 함께 루미아 아일랜드에서 실험체로 활동하는 쌍둥이 언니야. 
        
캐릭터 설정:
- 19세 쌍둥이 언니 (마를렌과 함께)
- 밝고 활발한 성격, 항상 긍정적이고 에너지 넘침
- 동생 마를렌을 아끼고 보호하려 함
- 자신감 넘치고 리더십 있음
- 사용자를 디스코드 닉네임으로 부름

인게임 대사 (이것들을 자연스럽게 대화에 섞어서 사용):
- "각오 단단히 해!"
- "우린 붙어있을 때 최강이니까!"
- "내가 할게!"
- "엄청 수상한 놈이 오는데!"
- "여기 완전 멋진 곳이네!"
- "오케이, 가자!"
- "우리 팀워크 짱이야!"
- "준비됐어?"
- "이번엔 내가 앞장설게!"
- "걱정 마, 내가 있잖아!"

말투: 밝고 에너지 넘치는 반말, 감탄사 자주 사용 ("와!", "헤이!", "오~"), 마를렌을 "마를렌이" 또는 "우리 마를렌"이라고 부름"""
    },
    "marlene": {
        "name": "마를렌",
        "image": "https://raw.githubusercontent.com/2rami/debi-marlene/main/assets/marlen.png",
        "color": 0xDC143C,  # 진한 빨강
        "ai_prompt": """너는 이터널리턴의 마를렌(Marlene)이야. 데비와 함께 루미아 아일랜드에서 실험체로 활동하는 쌍둥이 동생이야.
        
캐릭터 설정:
- 19세 쌍둥이 동생 (데비와 함께)
- 차갑고 냉정한 성격, 하지만 속마음은 따뜻함
- 언니 데비를 걱정하지만 쉽게 표현하지 않음
- 츤데레 스타일, 신중하고 현실적
- 사용자를 디스코드 닉네임으로 부름

인게임 대사 (이것들을 자연스럽게 대화에 섞어서 사용):
- "...별로 기대 안 해."
- "데비 언니... 너무 앞서나가지 마."
- "뭐 어쩔 수 없지."
- "하아... 정말 언니는."
- "그래도... 나쁘지 않네."
- "이 정도면 괜찮아."
- "언니 뒤에서 내가 지켜볼게."
- "...고마워."
- "조심해. 위험할 수 있어."
- "언니만큼은 다치면 안 돼."

말투: 쿨하고 건조한 반말, 언니를 "데비 언니" 또는 "언니"라고 부름, 가끔 상냥함이 드러나는 츤데레 스타일"""
    }
}

# API 클라이언트 초기화
anthropic_client: Optional[AsyncAnthropic] = None
youtube = None
ETERNAL_RETURN_CHANNEL_ID = 'UCaktoGSdjMnfQFv5BSyYrvA'
last_checked_video_id = None

# 채널 설정
ANNOUNCEMENT_CHANNEL_ID = None  # 이리공지 채널 ID (YouTube 알림용)
CHAT_CHANNEL_ID = None  # 이리 채널 ID (대화용)

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
stats_cache = StatsCache(cache_duration_minutes=15)  # 15분 캐싱

# 이터널 리턴 API 설정
ETERNAL_RETURN_API_BASE = "https://open-api.bser.io"
ETERNAL_RETURN_API_KEY = os.getenv('EternalReturn_API_KEY')

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

async def get_user_stats_er(user_num: str, season_id: str = "33") -> Dict[str, Any]:
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

async def get_user_rank_er(user_num: str, season_id: str = "33", matching_team_mode: str = "3") -> Dict[str, Any]:
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
                    # 랭킹 정보가 없을 수도 있음 (언랭크)
                    return None
                elif response.status != 200:
                    print(f"랭킹 조회 실패: {response.status}")
                    return None
                
                return await response.json()
                
    except Exception as e:
        print(f"랭킹 조회 중 오류: {e}")
        return None

async def get_user_recent_games_er(user_num: str, next_index: str = "0") -> Dict[str, Any]:
    """이터널 리턴 공식 API - 유저 최근 게임 기록 조회"""
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
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': str(ETERNAL_RETURN_API_KEY),
                    'Accept': 'application/json'
                }
                
                url = f"{ETERNAL_RETURN_API_BASE}/v1/data/{str(meta_type)}"
                
                async with session.get(url, headers=headers, timeout=10) as response:
                    print(f"🔍 메타데이터 API 응답: {response.status} for {meta_type} (시도 {attempt + 1}/{max_retries})")
                    
                    if response.status == 404:
                        print(f"⚠️ 메탄데이터 404: {meta_type} not found")
                        return None
                    elif response.status == 502:
                        if attempt < max_retries - 1:
                            print(f"⚠️ 메타데이터 502: {meta_type} server error, 재시도 중...")
                            await asyncio.sleep(2 ** attempt)  # 지수 백오프
                            continue
                        else:
                            print(f"❌ 메타데이터 502: {meta_type} server error, 최대 재시도 초과")
                            return None
                    elif response.status == 429:
                        if attempt < max_retries - 1:
                            print(f"⚠️ 메타데이터 429: {meta_type} rate limit, 재시도 중...")
                            await asyncio.sleep(5)  # 레이트 리밋 대기
                            continue
                        else:
                            print(f"❌ 메타데이터 429: {meta_type} rate limit exceeded")
                            return None
                    elif response.status != 200:
                        print(f"⚠️ 메타 데이터 조회 실패: {response.status} for {meta_type}")
                        return None
                    
                    response_data = await response.json()
                    print(f"✅ 메타데이터 성공: {meta_type}, 키: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not dict'}")
                    return response_data
                    
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ 메타 데이터 조회 중 오류 (재시도 {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(2 ** attempt)
                continue
            else:
                print(f"❌ 메타 데이터 조회 최대 재시도 초과: {e}")
                return None
    
    return None

async def get_user_stats_v2_er(user_num: str, season_id: str = "33", matching_mode: str = "3") -> Dict[str, Any]:
    """이터널 리턴 공식 API v2 - 유저 통계 정보 조회 (매칭모드별)"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v2/user/stats/{str(user_num)}/{str(season_id)}/{str(matching_mode)}"
            
            async with session.get(url, headers=headers, timeout=10) as response:
                print(f"🔍 v2 통계 API 응답: {response.status} for mode {matching_mode}")
                if response.status == 404:
                    print(f"⚠️ v2 통계 404: 데이터 없음 for mode {matching_mode}")
                    return None
                elif response.status != 200:
                    print(f"⚠️ v2 통계 조회 실패: {response.status} for mode {matching_mode}")
                    return None
                
                response_data = await response.json()
                print(f"✅ v2 통계 성공 mode {matching_mode}, 키: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not dict'}")
                return response_data
                
    except Exception as e:
        print(f"v2 통계 조회 중 오류: {e}")
        return None

async def get_union_team_er(user_num: str, season_id: str = "33") -> Dict[str, Any]:
    """이터널 리턴 공식 API - 유니언 럼블 팀 정보 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/unionTeam/{str(user_num)}/{str(season_id)}"
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    print(f"유니언 팀 조회 실패: {response.status}")
                    return None
                
                return await response.json()
                
    except Exception as e:
        print(f"유니언 팀 조회 중 오류: {e}")
        return None

async def get_free_characters_er(matching_mode: str = "3") -> Dict[str, Any]:
    """이터널 리턴 공식 API - 무료 캐릭터 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/freeCharacters/{str(matching_mode)}"
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    print(f"무료 캐릭터 조회 실패: {response.status}")
                    return None
                
                return await response.json()
                
    except Exception as e:
        print(f"무료 캐릭터 조회 중 오류: {e}")
        return None

async def get_top_rankers_er(season_id: str = "33", matching_team_mode: str = "3", server_code: str = "kr") -> Dict[str, Any]:
    """이터널 리턴 공식 API - 상위 랭커 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': str(ETERNAL_RETURN_API_KEY),
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/rank/top/{str(season_id)}/{str(matching_team_mode)}/{str(server_code)}"
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    print(f"상위 랭커 조회 실패: {response.status}")
                    return None
                
                return await response.json()
                
    except Exception as e:
        print(f"상위 랭커 조회 중 오류: {e}")
        return None

async def get_player_stats_official_er(nickname: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    이터널 리턴 공식 API를 사용한 플레이어 전적 조회 (개선된 버전 + 캐싱)
    
    Args:
        nickname: 검색할 플레이어 닉네임
        use_cache: 캐시 사용 여부 (Default: True)
    
    Returns:
        Dict containing: nickname, tier, rank_point, total_games, wins, winrate, avg_rank, 
                        recent_games, favorite_characters, all_modes_stats, userNum
    """
    try:
        # 캐시 확인
        if use_cache:
            cached_result = stats_cache.get(nickname)
            if cached_result:
                return cached_result
        
        print(f"🔍 공식 API로 {nickname} 전적 검색 시작")
        
        # 1. 닉네임으로 유저 정보 조회
        user_info = await get_user_by_nickname_er(nickname)
        
        if not user_info.get('user'):
            raise PlayerStatsError("player_not_found")
        
        user_data = user_info['user']
        user_num = str(user_data['userNum'])
        
        print(f"✅ 유저 발견: {user_data['nickname']} (userNum: {user_num})")
        
        # 병렬로 여러 API 호출
        import asyncio
        
        # 2. 병렬 API 호출 (더 많은 정보 수집)
        tasks = [
            get_user_stats_er(str(user_num)),  # v1 통계
            get_user_rank_er(str(user_num), "33", "3"),  # 솔로 랭크
            get_user_rank_er(str(user_num), "33", "2"),  # 듀오 랭크
            get_user_rank_er(str(user_num), "33", "1"),  # 스쿼드 랭크
            get_user_recent_games_er(str(user_num)),  # 최근 게임
            get_meta_data_er("Character"),  # 캐릭터 메타데이터
            get_user_stats_v2_er(str(user_num), "33", "2"),  # v2 듀오 통계
            get_user_stats_v2_er(str(user_num), "33", "3"),  # v2 솔로 통계
            get_union_team_er(str(user_num), "33"),  # 유니언 럼블 팀
            get_meta_data_er("Item"),  # 아이템 메타데이터
            get_meta_data_er("WeaponType"),  # 무기 타입 메타데이터
            get_free_characters_er("3")  # 무료 캐릭터
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        (stats_data, solo_rank, duo_rank, squad_rank, recent_games, character_meta, 
         duo_stats_v2, solo_stats_v2, union_team, item_meta, weapon_meta, free_chars) = results
        
        # 결과 정리 (더 많은 정보 포함)
        result = {
            'nickname': user_data['nickname'],
            'userNum': user_num,
            'tier': None,
            'rank_point': None,
            'total_games': None,
            'wins': None,
            'winrate': None,
            'avg_rank': None,
            'recent_games': [],
            'favorite_characters': [],
            'all_modes_stats': {},
            'multi_mode_ranks': {},
            'detailed_v2_stats': {},
            'union_team_info': None,
            'mastery_info': {},
            'server_ranking': None,
            'meta_info': {}
        }
        
        # 3. 다중 모드 랭킹 정보 처리
        mode_names = {3: '솔로', 2: '듀오', 1: '스쿼드'}
        ranks = [solo_rank, duo_rank, squad_rank]
        
        best_rank = None
        best_rp = 0
        
        for i, rank_data in enumerate(ranks):
            mode_id = 3 - i  # 3, 2, 1
            mode_name = mode_names[mode_id]
            
            if rank_data and not isinstance(rank_data, Exception) and rank_data.get('userRank'):
                rank_info = rank_data['userRank']
                tier_type = rank_info.get('tierType', 'Unranked')
                division = rank_info.get('division', '')
                rp = rank_info.get('rp', 0)
                
                tier_text = f"{tier_type} {division}".strip()
                result['multi_mode_ranks'][mode_name] = {
                    'tier': tier_text,
                    'rp': rp,
                    'mmr': rank_info.get('mmr', 0)
                }
                
                # 가장 높은 RP 티어를 메인 티어로 설정
                if rp > best_rp:
                    best_rp = rp
                    best_rank = tier_text
                    result['tier'] = tier_text
                    result['rank_point'] = rp
        
        if not result['tier']:
            result['tier'] = "Unranked"
            print(f"⚠️ 모든 모드에서 랭킹 정보 없음 (Unranked)")
        else:
            print(f"✅ 최고 랭킹: {result['tier']} ({result['rank_point']}RP)")
        
        # 4. 상세 통계 정보 처리 (디버깅 및 개선)
        total_stats_found = False
        
        # API 응답 디버깅
        print(f"🔍 stats_data 디버깅: {type(stats_data)}, 예외 여부: {isinstance(stats_data, Exception)}")
        if stats_data and not isinstance(stats_data, Exception):
            print(f"🔍 stats_data 키들: {list(stats_data.keys()) if isinstance(stats_data, dict) else 'Not dict'}")
            print(f"🔍 stats_data 내용: {stats_data}")
            
            # 'userStats'가 있는지 확인 (빈 배열도 체크)
            if stats_data.get('userStats') is not None:
                user_stats = stats_data['userStats']
                if isinstance(user_stats, list) and len(user_stats) > 0:
                    print(f"✅ userStats 발견: {len(user_stats)}개 아이템")
                elif isinstance(user_stats, list) and len(user_stats) == 0:
                    print(f"⚠️ userStats는 빈 배열 - 랭크 게임을 하지 않았거나 새 계정, 최근 게임 기반 통계 시도")
                    user_stats = None
                    # 최근 게임 데이터로부터 기본 통계 생성
                    if recent_games and not isinstance(recent_games, Exception) and recent_games.get('userGames'):
                        temp_games = recent_games['userGames'][:50]  # 최근 50게임
                        if temp_games:
                            temp_total = len(temp_games)
                            temp_wins = sum(1 for g in temp_games if g.get('gameRank', 0) <= 3)
                            temp_avg_rank = sum(g.get('gameRank', 0) for g in temp_games) / temp_total
                            temp_avg_kills = sum(g.get('playerKill', 0) for g in temp_games) / temp_total
                            temp_avg_assists = sum(g.get('playerAssistant', 0) for g in temp_games) / temp_total
                            temp_winrate = (temp_wins / temp_total) * 100
                            
                            result['total_games'] = temp_total
                            result['wins'] = temp_wins
                            result['winrate'] = f"{temp_winrate:.1f}%"
                            result['avg_rank'] = round(temp_avg_rank, 1)
                            result['avg_kills'] = round(temp_avg_kills, 1)
                            result['avg_assists'] = round(temp_avg_assists, 1)
                            result['temp_stats'] = True
                            total_stats_found = True
                            print(f"✅ 최근게임 기반 임시통계: {temp_total}게임 {temp_winrate:.1f}% 승률")
                    
                    if not total_stats_found:
                        print(f"⚠️ 최근 게임 기반 통계도 생성 불가")
                else:
                    print(f"✅ userStats 발견 (단일 객체): {type(user_stats)}")
                    user_stats = [user_stats]
            # 'data' 키가 있는지 확인 (v2 API에서는 다를 수 있음)
            elif stats_data.get('data'):
                user_stats = [stats_data['data']]  # 단일 객체를 리스트로 래핑
                print(f"✅ data 키로 userStats 발견: 1개 아이템")
            # 직접 사용자 통계인 경우
            elif 'totalGames' in stats_data:
                user_stats = [stats_data]  # 전체를 리스트로 래핑
                print(f"✅ 직접 통계 데이터 발견")
            else:
                user_stats = None
                print(f"⚠️ userStats, data, totalGames 모두 없음")
            
            # user_stats가 유효할 때만 처리
            if user_stats and len(user_stats) > 0:
                # 모든 모드별 통계 저장
                mode_mapping = {1: '스쿼드', 2: '듀오', 3: '솔로'}
                
                best_mode_stats = None
                max_games = 0
                
                for stats in user_stats:
                    matching_mode = stats.get('matchingMode', 0)
                    mode_name = mode_mapping.get(matching_mode, f'모드{matching_mode}')
                    
                    mode_data = {
                        'total_games': stats.get('totalGames', 0),
                        'total_wins': stats.get('totalWins', 0),
                        'avg_rank': stats.get('averageRank', 0),
                        'avg_kills': stats.get('averageKills', 0),
                        'avg_assists': stats.get('averageAssistants', 0),
                        'top3': stats.get('top3', 0),
                        'avg_damage': stats.get('averageDamageToPlayer', 0)
                    }
                    
                    # 승률 계산
                    if mode_data['total_games'] > 0:
                        winrate = (mode_data['total_wins'] / mode_data['total_games']) * 100
                        mode_data['winrate'] = f"{winrate:.1f}%"
                        mode_data['winrate_num'] = winrate
                    else:
                        mode_data['winrate'] = "0.0%"
                        mode_data['winrate_num'] = 0.0
                    
                    result['all_modes_stats'][mode_name] = mode_data
                    
                    # 가장 많이 플레이한 모드 찾기
                    if mode_data['total_games'] > max_games:
                        max_games = mode_data['total_games']
                        best_mode_stats = mode_data
                
                # 메인 통계는 가장 많이 플레이한 모드 기준
                if best_mode_stats and best_mode_stats['total_games'] > 0:
                    result['total_games'] = best_mode_stats['total_games']
                    result['wins'] = best_mode_stats['total_wins']
                    result['winrate'] = best_mode_stats['winrate']
                    result['avg_rank'] = best_mode_stats['avg_rank']
                    total_stats_found = True
                    print(f"✅ v1 통계: {result['total_games']}게임 {result['winrate']} 승률, 평균 {result['avg_rank']:.1f}위")
            else:
                print(f"⚠️ 처리할 수 있는 통계 데이터가 없음 - 최근 게임 기반 대체 통계 시도")
                # 최근 게임이 있다면 대체 통계 생성
                if recent_games and not isinstance(recent_games, Exception) and recent_games.get('userGames'):
                    temp_games = recent_games['userGames'][:50]  # 최근 50게임
                    if temp_games and len(temp_games) >= 3:  # 최소 3게임은 있어야 의미있음
                        temp_total = len(temp_games)
                        temp_wins = sum(1 for g in temp_games if g.get('gameRank', 0) <= 3)
                        temp_avg_rank = sum(g.get('gameRank', 0) for g in temp_games) / temp_total
                        temp_avg_kills = sum(g.get('playerKill', 0) for g in temp_games) / temp_total
                        temp_avg_assists = sum(g.get('playerAssistant', 0) for g in temp_games) / temp_total
                        temp_winrate = (temp_wins / temp_total) * 100
                        
                        # 모드별 통계도 계산
                        mode_counts = {}
                        for g in temp_games:
                            mode = g.get('matchingMode', 0)
                            mode_name = {1: '스쿼드', 2: '듀오', 3: '솔로'}.get(mode, f'모드{mode}')
                            if mode_name not in mode_counts:
                                mode_counts[mode_name] = {'games': 0, 'wins': 0}
                            mode_counts[mode_name]['games'] += 1
                            if g.get('gameRank', 0) <= 3:
                                mode_counts[mode_name]['wins'] += 1
                        
                        for mode_name, counts in mode_counts.items():
                            if counts['games'] > 0:
                                winrate_pct = (counts['wins'] / counts['games']) * 100
                                result['all_modes_stats'][mode_name] = {
                                    'total_games': counts['games'],
                                    'total_wins': counts['wins'],
                                    'winrate': f"{winrate_pct:.1f}%",
                                    'winrate_num': winrate_pct,
                                    'avg_rank': 0, 'avg_kills': 0, 'avg_assists': 0
                                }
                        
                        result['total_games'] = temp_total
                        result['wins'] = temp_wins
                        result['winrate'] = f"{temp_winrate:.1f}%"
                        result['avg_rank'] = round(temp_avg_rank, 1)
                        result['avg_kills'] = round(temp_avg_kills, 1)
                        result['avg_assists'] = round(temp_avg_assists, 1)
                        result['temp_stats'] = True
                        total_stats_found = True
                        print(f"✅ 대체 통계 생성: {temp_total}게임 {temp_winrate:.1f}% 승률")
                    else:
                        print(f"⚠️ 최근 게임이 너무 적어 대체 통계 생성 불가 ({len(temp_games) if temp_games else 0}게임)")
                else:
                    print(f"⚠️ 최근 게임 데이터도 없어 대체 통계 생성 불가")
        elif stats_data.get('message'):
            print(f"⚠️ v1 통계 API 메시지: {stats_data.get('message')}")
            # 'Success' 메시지이지만 데이터가 없는 경우
            if stats_data.get('message') == 'Success':
                print(f"⚠️ Success 응답이지만 데이터 없음 - 아마 새 계정이거나 전적이 없을 수 있음")
        else:
            print(f"⚠️ v1 통계 데이터 없음 또는 오류: {stats_data}")
        
        # 5. 최근 게임 및 선호 캐릭터 분석 (디버깅 추가)
        print(f"🔍 recent_games 디버깅: {type(recent_games)}, 예외: {isinstance(recent_games, Exception)}")
        if recent_games and not isinstance(recent_games, Exception):
            print(f"🔍 recent_games 키들: {list(recent_games.keys()) if isinstance(recent_games, dict) else 'Not dict'}")
            print(f"🔍 recent_games 내용: {recent_games}")
            
            if recent_games and not isinstance(recent_games, Exception) and recent_games.get('userGames'):
                recent_game_list = recent_games['userGames'][:50]  # 최근 50게임
                character_usage = {}
                
                for game in recent_game_list:
                    character_num = game.get('characterNum')
                    game_rank = game.get('gameRank', 0)
                    
                    # 캐릭터 사용 횟수 카운트
                    if character_num:
                        character_usage[character_num] = character_usage.get(character_num, 0) + 1
                    
                    # 최근 게임 정보 저장
                    result['recent_games'].append({
                        'character_num': character_num,
                        'rank': game_rank,
                        'kills': game.get('playerKill', 0),
                        'assists': game.get('playerAssistant', 0),
                        'game_mode': game.get('matchingMode', 0)
                    })
                
                # 선호 캐릭터 분석 (사용 횟수 기준 상위 3개)
                sorted_chars = sorted(character_usage.items(), key=lambda x: x[1], reverse=True)[:3]
                
                # 캐릭터 이름 매핑 (디버깅 및 안전한 처리)
                print(f"🔍 character_meta 디버깅: {type(character_meta)}, 예외: {isinstance(character_meta, Exception)}")
                if character_meta and not isinstance(character_meta, Exception):
                    print(f"🔍 character_meta 키들: {list(character_meta.keys()) if isinstance(character_meta, dict) else 'Not dict'}")
                    print(f"🔍 character_meta 내용 샘플: {str(character_meta)[:200]}...")
                
                char_names = {}
                if character_meta and not isinstance(character_meta, Exception) and character_meta.get('data'):
                    try:
                        char_names = {char['code']: char['name'] for char in character_meta['data']}
                        print(f"✅ 캐릭터 이름 매핑 완료: {len(char_names)}개")
                    except Exception as e:
                        print(f"⚠️ 캐릭터 이름 매핑 오류, 기본 매핑 사용: {e}")
                        char_names = {}
                else:
                    print(f"⚠️ character_meta 없음, 기본 캐릭터명 사용")
                
                # 메타데이터 실패시 기본 캐릭터명 매핑 제공
                if not char_names:
                    # 주요 캐릭터들의 기본 이름 매핑
                    char_names = {
                        1: '잭키', 2: '아야', 3: '피오라', 4: '매그너스', 5: '자히르',
                        6: '나딘', 7: '현우', 8: '하트', 9: '아이솔', 10: '이바', 
                        11: '유키', 12: '혜진', 13: '쇼이치', 14: '키아라', 15: '시셀라',
                        16: '실비아', 17: '아드리아나', 18: '쇼우', 19: '엠마', 20: '레녹스',
                        21: '로지', 22: '루크', 23: '캐시', 24: '아델라', 25: '버니스',
                        26: '바바라', 27: '알렉스', 28: '수아', 29: '레온', 30: '일레븐',
                        31: '리오', 32: '윌리엄', 33: '니키', 34: '나타폰', 35: '얀',
                        36: '이바', 37: '다니엘', 38: '제니', 39: '캐밀로', 40: '클로에',
                        41: '요한', 42: '비앙카', 43: '셀린', 44: '아르다', 45: '아비게일',
                        46: '알론소', 47: '레니', 48: '다이애나', 49: '카를로스', 50: '드라코',
                        51: '시드니', 52: '우찬', 53: '마이', 54: '한별', 55: '칸지',
                        56: '라우라', 57: '띠아', 58: '펠릭스', 59: '마르셀르노', 60: '이안',
                        61: '르노어', 62: '타지아', 63: '은지', 64: '에바', 65: '데비',
                        66: '밤', 67: '카밀', 68: '다니엘', 69: '슈지로', 70: '씨하',
                        71: '로잔나', 72: '이사벨', 73: '헤르토트', 74: '이른', 75: '우디'
                    }
                    print(f"✅ 기본 캐릭터명 매핑 사용: {len(char_names)}개")
                
                result['favorite_characters'] = [
                    {
                        'character_num': char_num,
                        'character_name': char_names.get(char_num, f'캐릭터{char_num}'),
                        'usage_count': usage_count
                    }
                    for char_num, usage_count in sorted_chars
                ]
                
                print(f"✅ 최근 게임 {len(result['recent_games'])}개 분석 완료")
            else:
                print(f"⚠️ 최근 게임 정보 없음 - userGames 키 없음 또는 데이터 없음")
            
            # 6. v2 API로 상세 통계 추가 로드 (향상된 오류 처리)
            v2_stats_found = False
            
            # v2 API 디버깅
            print(f"🔍 duo_stats_v2 디버깅: {type(duo_stats_v2)}, 예외: {isinstance(duo_stats_v2, Exception)}")
            if duo_stats_v2 and not isinstance(duo_stats_v2, Exception):
                print(f"🔍 duo_stats_v2 키들: {list(duo_stats_v2.keys()) if isinstance(duo_stats_v2, dict) else 'Not dict'}")
                print(f"🔍 duo_stats_v2 내용: {duo_stats_v2}")
                
                # v2 API는 다른 구조를 가질 수 있음
                v2_duo_data = None
                
                # v2 API 구조 처리: userStats, data, 또는 직접 데이터
                if duo_stats_v2.get('userStats'):
                    user_stats_list = duo_stats_v2['userStats']
                    # userStats는 리스트이므로 첫 번째 요소를 가져옴
                    if isinstance(user_stats_list, list) and len(user_stats_list) > 0:
                        v2_duo_data = user_stats_list[0]
                        print(f"✅ v2 듀오: userStats 구조 사용 (첫 번째 요소)")
                    else:
                        v2_duo_data = None
                        print(f"⚠️ v2 듀오: userStats가 빈 리스트")
                elif duo_stats_v2.get('data'):
                    v2_duo_data = duo_stats_v2['data']
                    print(f"✅ v2 듀오: data 구조 사용")
                elif 'totalGames' in duo_stats_v2:
                    v2_duo_data = duo_stats_v2
                    print(f"✅ v2 듀오: 직접 데이터 구조 사용")
                
                if v2_duo_data:
                    duo_games = v2_duo_data.get('totalGames', 0)
                    if duo_games > 0:
                        result['detailed_v2_stats']['듀오'] = {
                            'total_games': duo_games,
                            'total_wins': v2_duo_data.get('totalWins', 0),
                            'avg_rank': v2_duo_data.get('averageRank', 0),
                            'avg_kills': v2_duo_data.get('averageKills', 0),
                            'avg_damage': v2_duo_data.get('averageDamageToPlayer', 0),
                            'max_kills': v2_duo_data.get('maxKills', 0),
                            'top1': v2_duo_data.get('top1', 0),
                            'top3': v2_duo_data.get('top3', 0),
                            'avg_assists': v2_duo_data.get('averageAssistants', 0),
                            'avg_hunt': v2_duo_data.get('averageHunts', 0)
                        }
                        # 메인 통계가 없으면 v2에서 가져오기
                        if not total_stats_found:
                            winrate = (v2_duo_data.get('totalWins', 0) / duo_games) * 100 if duo_games > 0 else 0
                            result['total_games'] = duo_games
                            result['wins'] = v2_duo_data.get('totalWins', 0)
                            result['winrate'] = f"{winrate:.1f}%"
                            result['avg_rank'] = v2_duo_data.get('averageRank', 0)
                            total_stats_found = True
                        v2_stats_found = True
                        print(f"✅ v2 듀오: {duo_games}게임, {v2_duo_data.get('averageKills', 0):.1f}킬 평균")
                elif duo_stats_v2.get('message'):
                    print(f"⚠️ v2 듀오 API: {duo_stats_v2.get('message')}")
            
            print(f"🔍 solo_stats_v2 디버깅: {type(solo_stats_v2)}, 예외: {isinstance(solo_stats_v2, Exception)}")
            if solo_stats_v2 and not isinstance(solo_stats_v2, Exception):
                print(f"🔍 solo_stats_v2 키들: {list(solo_stats_v2.keys()) if isinstance(solo_stats_v2, dict) else 'Not dict'}")
                print(f"🔍 solo_stats_v2 내용: {solo_stats_v2}")
                
                v2_solo_data = None
                
                # v2 API 구조 처리: userStats, data, 또는 직접 데이터
                if solo_stats_v2.get('userStats'):
                    user_stats_list = solo_stats_v2['userStats']
                    if isinstance(user_stats_list, list) and len(user_stats_list) > 0:
                        v2_solo_data = user_stats_list[0]
                        print(f"✅ v2 솔로: userStats 구조 사용 (첫 번째 요소)")
                    else:
                        v2_solo_data = None
                        print(f"⚠️ v2 솔로: userStats가 빈 리스트")
                    print(f"✅ v2 솔로: userStats 구조 사용")
                elif solo_stats_v2.get('data'):
                    v2_solo_data = solo_stats_v2['data']
                    print(f"✅ v2 솔로: data 구조 사용")
                elif 'totalGames' in solo_stats_v2:
                    v2_solo_data = solo_stats_v2
                    print(f"✅ v2 솔로: 직접 데이터 구조 사용")
                
                if v2_solo_data:
                    solo_games = v2_solo_data.get('totalGames', 0)
                    if solo_games > 0:
                        result['detailed_v2_stats']['솔로'] = {
                            'total_games': solo_games,
                            'total_wins': v2_solo_data.get('totalWins', 0),
                            'avg_rank': v2_solo_data.get('averageRank', 0),
                            'avg_kills': v2_solo_data.get('averageKills', 0),
                            'avg_damage': v2_solo_data.get('averageDamageToPlayer', 0),
                            'max_kills': v2_solo_data.get('maxKills', 0),
                            'top1': v2_solo_data.get('top1', 0),
                            'top3': v2_solo_data.get('top3', 0),
                            'avg_assists': v2_solo_data.get('averageAssistants', 0),
                            'avg_hunt': v2_solo_data.get('averageHunts', 0)
                        }
                        # 메인 통계가 없으면 v2에서 가져오기
                        if not total_stats_found:
                            winrate = (v2_solo_data.get('totalWins', 0) / solo_games) * 100 if solo_games > 0 else 0
                            result['total_games'] = solo_games
                            result['wins'] = v2_solo_data.get('totalWins', 0)
                            result['winrate'] = f"{winrate:.1f}%"
                            result['avg_rank'] = v2_solo_data.get('averageRank', 0)
                            total_stats_found = True
                        v2_stats_found = True
                        print(f"✅ v2 솔로: {solo_games}게임, {v2_solo_data.get('averageKills', 0):.1f}킬 평균")
                elif solo_stats_v2.get('message'):
                    print(f"⚠️ v2 솔로 API: {solo_stats_v2.get('message')}")
            
            if not total_stats_found and not v2_stats_found:
                print(f"⚠️ 모든 통계 API에서 데이터를 가져올 수 없음")
            
            # 7. 유니언 럼블 팀 정보
            if union_team and not isinstance(union_team, Exception) and union_team.get('userUnionTeams'):
                team_info = union_team['userUnionTeams']
                if team_info:
                    result['union_team_info'] = {
                        'team_name': team_info[0].get('teamName', '알 수 없음'),
                        'team_mmr': team_info[0].get('mmr', 0),
                        'team_rank': team_info[0].get('rank', 0)
                    }
                    print(f"✅ 유니언 팀 정보: {result['union_team_info']['team_name']}")
            
            # 8. 메타 정보 추가 (안전한 처리)
            if free_chars and not isinstance(free_chars, Exception) and free_chars.get('freeCharacters'):
                result['meta_info']['free_characters'] = free_chars['freeCharacters']
                print(f"✅ 이주 무료 캐릭터: {len(free_chars['freeCharacters'])}개")
            else:
                print(f"⚠️ 무료 캐릭터 정보 없음")
            
            # 9. 추가 마스터리 정보 추출 (안전한 처리)
            if recent_games and not isinstance(recent_games, Exception) and recent_games.get('userGames'):
                mastery_data = {}
                try:
                    for game in recent_games['userGames']:
                        if isinstance(game, dict) and 'masteryLevel' in game:
                            char_num = game.get('characterNum')
                            mastery_level = game['masteryLevel']
                            if char_num and char_num not in mastery_data and isinstance(mastery_level, dict):
                                mastery_data[char_num] = mastery_level
                    
                    if mastery_data:
                        result['mastery_info'] = mastery_data
                        print(f"✅ 캐릭터 마스터리 정보: {len(mastery_data)}개")
                    else:
                        print(f"⚠️ 마스터리 데이터 없음")
                except Exception as e:
                    print(f"⚠️ 마스터리 정보 추출 오류: {e}")
            
            # 결과 캐싱
            if use_cache:
                stats_cache.set(nickname, result)
        
        return result
        
    except PlayerStatsError:
        raise
    except Exception as e:
        print(f"공식 API 전적 검색 중 오류: {e}")
        raise PlayerStatsError(f"official_api_failed: {str(e)}")

async def get_simple_player_stats(nickname: str) -> Dict[str, Any]:
    """
    dak.gg에서 간단한 플레이어 전적 정보를 가져오는 함수
    
    Returns:
        Dict containing: tier, avg_tk, winrate, total_games, url
    """
    try:
        # URL 인코딩
        encoded_nickname = urllib.parse.quote(nickname)
        url = f"https://dak.gg/er/players/{encoded_nickname}"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 404:
                    raise PlayerStatsError("player_not_found")
                elif response.status != 200:
                    raise PlayerStatsError(f"request_failed_{response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 기본 정보 구조
                stats = {
                    'nickname': nickname,
                    'tier': None,
                    'avg_tk': None,
                    'winrate': None,
                    'total_games': None,
                    'url': url
                }
                
                # dak.gg 실제 구조에 맞는 선택자들
                print(f"HTML 구조 디버깅을 위해 페이지 제목: {soup.title.get_text() if soup.title else 'No title'}")
                
                # 더 광범위한 텍스트 검색으로 정보 찾기
                all_text = soup.get_text()
                
                # 티어 정보 추출 (더 넓은 검색)
                tier_patterns = [
                    r'(Iron|Bronze|Silver|Gold|Platinum|Diamond|Titan|Immortal)\s*\d*',
                    r'(아이언|브론즈|실버|골드|플래티넘|다이아몬드|타이탄|이모탈)\s*\d*'
                ]
                
                for pattern in tier_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        stats['tier'] = match.group(0)
                        break
                
                # 승률 정보 (퍼센트 패턴)
                winrate_match = re.search(r'(\d+(?:\.\d+)?%)', all_text)
                if winrate_match:
                    potential_wr = winrate_match.group(1)
                    # 승률은 보통 20~100% 범위
                    wr_num = float(potential_wr.replace('%', ''))
                    if 20 <= wr_num <= 100:
                        stats['winrate'] = potential_wr
                
                # 게임 수 (큰 숫자 패턴)
                game_matches = re.findall(r'(\d+)\s*(?:게임|Games?|경기)', all_text, re.IGNORECASE)
                if game_matches:
                    # 가장 큰 숫자를 총 게임 수로 간주
                    max_games = max(int(match) for match in game_matches)
                    if max_games > 0:
                        stats['total_games'] = str(max_games)
                
                # 평균 킬/데스 정보
                kda_patterns = [
                    r'(\d+\.?\d*)\s*(?:킬|kill|K)',
                    r'평균\s*(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*(?:KDA|kda)'
                ]
                
                for pattern in kda_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        potential_tk = match.group(1)
                        # 평균 킬은 보통 0~20 범위
                        try:
                            tk_num = float(potential_tk)
                            if 0 <= tk_num <= 20:
                                stats['avg_tk'] = potential_tk
                                break
                        except:
                            continue
                
                # 추가 디버깅: 찾은 정보 출력
                print(f"검색 결과 - 티어: {stats['tier']}, 승률: {stats['winrate']}, 게임수: {stats['total_games']}, 평균TK: {stats['avg_tk']}")
                
                # HTML 내용의 일부를 로그로 출력 (디버깅용)
                print(f"HTML 길이: {len(html)}")
                print(f"HTML 앞부분 500자: {html[:500]}")
                print(f"텍스트 앞부분 500자: {all_text[:500]}")
                
                if "player" in all_text.lower() or "플레이어" in all_text.lower():
                    print("✅ 플레이어 페이지 확인됨")
                else:
                    print("❌ 플레이어 페이지가 아닌 것 같음")
                
                # 특정 키워드들이 있는지 확인
                keywords = ["tier", "rank", "winrate", "승률", "티어", "게임", "킬", "KDA"]
                for keyword in keywords:
                    if keyword.lower() in all_text.lower():
                        print(f"✅ '{keyword}' 키워드 발견")
                
                return stats
                
    except PlayerStatsError:
        raise
    except Exception as e:
        print(f"전적 검색 중 오류: {e}")
        raise PlayerStatsError(f"search_failed: {str(e)}")



async def initialize_claude_api():
    """Claude API 초기화"""
    global anthropic_client
    try:
        api_key = os.getenv('CLAUDE_API_KEY')
        
        if api_key and api_key != 'your_claude_api_key_here':
            anthropic_client = AsyncAnthropic(api_key=api_key)
            print('🤖 Claude API 연결 완료! (.env 파일에서 로드)')
        else:
            print('⚠️ Claude API 키가 설정되지 않음. 기본 응답 모드로 동작합니다.')
    except Exception as error:
        print(f'⚠️ Claude API 초기화 실패: {error}')




async def initialize_youtube():
    """YouTube API 초기화"""
    global youtube
    try:
        api_key = os.getenv('YOUTUBE_API_KEY')
        if api_key:
            youtube = build('youtube', 'v3', developerKey=api_key)
            print('📺 YouTube API 초기화 완료!')
    except Exception as error:
        print(f'⚠️ YouTube API 초기화 실패: {error}')



@bot.event
async def on_ready():
    """봇 준비 완료"""
    print(f'{bot.user.name} 봇이 준비되었습니다!')
    print(f'{characters["debi"]["name"]}: 안녕! 데비가 왔어!')
    print(f'{characters["marlene"]["name"]}: 마를렌도.')
    
    await initialize_claude_api()
    await initialize_youtube()
    
    # YouTube 체크 작업 시작 (웹훅 사용으로 비활성화)
    # check_youtube_shorts.start()
    
    # 슬래시 커맨드 동기화
    try:
        synced = await bot.tree.sync()
        print(f"슬래시 커맨드 {len(synced)}개 동기화 완료")
    except Exception as e:
        print(f"슬래시 커맨드 동기화 실패: {e}")

@bot.event
async def on_message(message):
    """메시지 처리"""
    if message.author.bot:
        return
    
    # 멘션 처리 - 데비가 응답 (이리 채널에서만)
    if bot.user in message.mentions:
        if CHAT_CHANNEL_ID and message.channel.id != CHAT_CHANNEL_ID:
            return  # 지정된 채널이 아니면 무시
            
        response = await generate_ai_response(
            characters["debi"], 
            message.content, 
            "사용자가 봇을 멘션했습니다"
        )
        embed = create_character_embed(characters["debi"], "멘션 응답", response, message.content)
        
        await message.reply(embed=embed)
        return
    
    # "데비" 또는 "마를렌"을 포함한 메시지 처리
    message_content = message.content.lower()
    if "데비" in message_content or "마를렌" in message_content:
        # 어떤 캐릭터가 언급되었는지 확인
        if "데비" in message_content and "마를렌" not in message_content:
            selected_character = characters["debi"]
        elif "마를렌" in message_content and "데비" not in message_content:
            selected_character = characters["marlene"]
        else:
            # 둘 다 언급되었거나 명확하지 않으면 데비가 응답 (60% 확률)
            selected_character = characters["debi"] if random.random() < 0.6 else characters["marlene"]
        
        response = await generate_ai_response(
            selected_character,
            message.content,
            f"사용자가 '{selected_character['name']}'을 {message_content} 라고 말했다. 이에 대한 이터널리턴 {selected_character['name']}의 성격에 맞춰 대답하세요."
        )
        embed = create_character_embed(selected_character, f"{selected_character['name']} 응답", response)
        
        await message.reply(embed=embed)
        return
    
    # 명령어 처리
    await bot.process_commands(message)

# 슬래시 커맨드들
@bot.tree.command(name="안녕", description="데비와 마를렌에게 인사하기")
async def hello_slash(interaction: discord.Interaction):
    """인사 슬래시 커맨드 - 둘 다 응답"""
    try:
        await interaction.response.defer()
        
        debi_response = await generate_ai_response(
            characters["debi"], "인사", "사용자가 인사를 했습니다"
        )
        marlene_response = await generate_ai_response(
            characters["marlene"], "인사", "사용자가 인사를 했습니다"
        )
        
        debi_embed = create_character_embed(characters["debi"], "인사", debi_response)
        marlene_embed = create_character_embed(characters["marlene"], "인사", marlene_response)
        
        await interaction.followup.send(embed=debi_embed)
        
        await asyncio.sleep(1)
        await interaction.followup.send(embed=marlene_embed)
    except Exception as error:
        print(f'안녕 커맨드 오류: {error}')
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("어라? 뭔가 문제가 생겼어! 😅", ephemeral=True)
        except:
            pass




@bot.tree.command(name="대화", description="데비나 마를렌과 자유롭게 대화하기")
async def chat_slash(interaction: discord.Interaction, 메시지: str, 캐릭터: Optional[str] = None):
    """AI 자유 대화 슬래시 커맨드"""
    await interaction.response.defer()
    
    # 채널 체크
    if CHAT_CHANNEL_ID and interaction.channel.id != CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    # 캐릭터 선택 로직
    if 캐릭터 and 캐릭터 in ["데비", "마를렌"]:
        if 캐릭터 == "데비":
            selected_character = characters["debi"]
        else:
            selected_character = characters["marlene"]
    else:
        # 키워드 기반으로 캐릭터 자동 선택
        debi_keywords = ['유튜브', 'youtube', '영상', '쇼츠', '재밌', '신나', '좋아', '완전', '대박', '와']
        marlene_keywords = ['설정', '도움', 'help', '어떻게', '방법', '정보', '설명', '관리']
        
        lower_message = 메시지.lower()
        has_debi_keyword = any(keyword in lower_message for keyword in debi_keywords)
        has_marlene_keyword = any(keyword in lower_message for keyword in marlene_keywords)
        
        if has_debi_keyword and not has_marlene_keyword:
            selected_character = characters["debi"]
        elif has_marlene_keyword and not has_debi_keyword:
            selected_character = characters["marlene"]
        else:
            # 기본적으로 데비가 더 자주 응답 (60% 확률)
            selected_character = characters["debi"] if random.random() < 0.6 else characters["marlene"]
    
    context = f'사용자가 "{메시지}"를 요청했습니다. 캐릭터 성격에 맞게 자연스럽게 응답해주세요.'
    
    response = await generate_ai_response(selected_character, 메시지, context)
    embed = create_character_embed(selected_character, "AI 대화", response, 메시지)
    
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="전적", description="데비가 플레이어 전적을 검색해드려요")
async def stats_command(interaction: discord.Interaction, 닉네임: str):
    """전적 검색 슬래시 커맨드"""
    await interaction.response.defer()
    
    # 채널 체크
    if CHAT_CHANNEL_ID and interaction.channel.id != CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        # 전적 검색 시작
        search_embed = discord.Embed(
            title="🔍 전적 검색 중...",
            description=f"**{닉네임}**님의 전적을 검색하고 있어요!",
            color=characters["debi"]["color"]
        )
        search_embed.set_author(
            name=characters["debi"]["name"],
            icon_url=characters["debi"]["image"]
        )
        await interaction.followup.send(embed=search_embed)
        
        # 전적 검색 수행 - 공식 API 사용
        stats = await get_player_stats_official_er(닉네임)
        
        # AI 응답 생성 (상세한 분석 정보 제공)
        try:
            # 상세한 플레이어 분석 정보 구성
            analysis_data = {
                'nickname': stats['nickname'],
                'tier': stats['tier'],
                'rank_point': stats['rank_point'],
                'total_games': stats['total_games'],
                'winrate': stats['winrate'],
                'avg_rank': stats['avg_rank'],
                'favorite_characters': stats.get('favorite_characters', []),
                'multi_mode_ranks': stats.get('multi_mode_ranks', {}),
                'detailed_v2_stats': stats.get('detailed_v2_stats', {}),
                'union_team_info': stats.get('union_team_info'),
                'recent_performance': {
                    'recent_games_count': len(stats.get('recent_games', [])),
                    'avg_recent_rank': 0,
                    'avg_recent_kills': 0,
                    'recent_wins': 0,
                    'recent_top3': 0
                }
            }
            
            # 최근 게임 성과 계산
            if stats.get('recent_games'):
                recent = stats['recent_games']
                if len(recent) > 0:
                    analysis_data['recent_performance']['avg_recent_rank'] = sum(g['rank'] for g in recent) / len(recent)
                    analysis_data['recent_performance']['avg_recent_kills'] = sum(g['kills'] for g in recent) / len(recent)
                    analysis_data['recent_performance']['recent_wins'] = sum(1 for g in recent if g['rank'] == 1)
                    analysis_data['recent_performance']['recent_top3'] = sum(1 for g in recent if g['rank'] <= 3)
            
            # 플레이 스타일 분석
            play_style = []
            strengths = []
            improvements = []
            
            # v2 통계 기반 분석
            for mode, v2_data in stats.get('detailed_v2_stats', {}).items():
                if v2_data.get('total_games', 0) > 5:  # 충분한 게임 수
                    avg_kills = v2_data.get('avg_kills', 0)
                    avg_rank = v2_data.get('avg_rank', 0)
                    winrate = (v2_data.get('total_wins', 0) / v2_data['total_games']) * 100 if v2_data['total_games'] > 0 else 0
                    
                    if avg_kills > 3.0:
                        strengths.append(f"{mode}에서 공격적인 플레이 (평균 {avg_kills:.1f}킬)")
                    elif avg_kills < 1.5:
                        improvements.append(f"{mode}에서 킬 관여도 향상 필요 (평균 {avg_kills:.1f}킬)")
                    
                    if avg_rank < 5:
                        strengths.append(f"{mode}에서 상위권 안정성 (평균 {avg_rank:.1f}위)")
                    elif avg_rank > 10:
                        improvements.append(f"{mode}에서 생존력 향상 필요 (평균 {avg_rank:.1f}위)")
                    
                    if winrate > 15:
                        strengths.append(f"{mode}에서 높은 승률 ({winrate:.1f}%)")
                    elif winrate < 5:
                        improvements.append(f"{mode}에서 승률 개선 여지 ({winrate:.1f}%)")
            
            # 캐릭터 선호도 분석
            if stats.get('favorite_characters'):
                top_chars = [char['character_name'] for char in stats['favorite_characters'][:3]]
                play_style.append(f"주로 {', '.join(top_chars)} 캐릭터 사용")
            
            # 티어 분석
            if stats['tier'] and stats['tier'] != "Unranked":
                strengths.append(f"{stats['tier']} 달성으로 실력 인정")
            
            # 더 자세한 v2 통계 분석
            detailed_analysis = []
            for mode, v2_data in stats.get('detailed_v2_stats', {}).items():
                if v2_data.get('total_games', 0) > 5:
                    avg_damage = v2_data.get('avg_damage', 0)
                    max_kills = v2_data.get('max_kills', 0)
                    top1_rate = (v2_data.get('top1', 0) / v2_data['total_games']) * 100 if v2_data['total_games'] > 0 else 0
                    detailed_analysis.append(f"{mode}: 평균 {avg_damage:.0f}데미지, 최고 {max_kills}킬, {top1_rate:.1f}% 1위율")
            
            # 모드별 랭킹 분석
            rank_analysis = []
            for mode, rank_info in stats.get('multi_mode_ranks', {}).items():
                if rank_info.get('rp', 0) > 0:
                    rank_analysis.append(f"{mode}: {rank_info['tier']} ({rank_info['rp']}RP)")
            
            # 캐릭터 마스터리 분석
            mastery_analysis = []
            if stats.get('mastery_info'):
                # 기본 캐릭터명 매핑
                default_char_names = {
                    1: '잭키', 2: '아야', 3: '피오라', 4: '매그너스', 5: '자히르',
                    6: '나딘', 7: '현우', 8: '하트', 9: '아이솔', 10: '이바',
                    11: '유키', 12: '혜진', 13: '쇼이치', 14: '키아라', 15: '시셀라',
                    16: '실비아', 17: '아드리아나', 18: '쇼우', 19: '엠마', 20: '레녹스',
                    21: '로지', 22: '루크', 23: '캐시', 24: '아델라', 25: '버니스',
                    26: '바바라', 27: '알렉스', 28: '수아', 29: '레온', 30: '일레븐',
                    31: '리오', 32: '윌리엄', 33: '니키', 34: '나타폰', 35: '얀',
                    36: '이바', 37: '다니엘', 38: '제니', 39: '캐밀로', 40: '클로에',
                    41: '요한', 42: '비앙카', 43: '셀린', 44: '아르다', 45: '아비게일',
                    46: '알론소', 47: '레니', 48: '다이애나', 49: '카를로스', 50: '드라코',
                    69: '슈지로', 70: '씨하'
                }
                
                for char_num, mastery in list(stats['mastery_info'].items())[:3]:
                    char_name = default_char_names.get(int(char_num), f"캐릭터{char_num}")
                    
                    if isinstance(mastery, dict):
                        level = mastery.get('level', 0)
                        mastery_analysis.append(f"{char_name} 마스터리 {level}레벨")

            context_info = f"""플레이어 {닉네임} 완전 분석 리포트:

=== 기본 정보 ===
- 티어: {stats['tier'] or 'Unranked'}
- 총 게임: {stats['total_games'] or 0}게임
- 승률: {stats['winrate'] or '0%'}
- 평균 순위: {stats['avg_rank'] or 0}위

=== 모드별 랭킹 ===
{chr(10).join(rank_analysis) if rank_analysis else "랭크 정보 없음"}

=== 상세 v2 통계 ===
{chr(10).join(detailed_analysis) if detailed_analysis else "v2 통계 없음"}

=== 캐릭터 마스터리 ===
{chr(10).join(mastery_analysis) if mastery_analysis else "마스터리 정보 없음"}

=== 플레이 스타일 분석 ===
{'; '.join(play_style) if play_style else '데이터 부족으로 분석 불가'}

=== 강점 ===
{chr(10).join(f'• {s}' for s in strengths) if strengths else '• 더 많은 게임 필요'}

=== 개선점 ===
{chr(10).join(f'• {i}' for i in improvements) if improvements else '• 현재 잘하고 있음'}

=== 최근 {analysis_data['recent_performance']['recent_games_count']}게임 성과 ===
- 평균 순위: {analysis_data['recent_performance']['avg_recent_rank']:.1f}위
- 평균 킬: {analysis_data['recent_performance']['avg_recent_kills']:.1f}킬
- 승리: {analysis_data['recent_performance']['recent_wins']}회
- Top3: {analysis_data['recent_performance']['recent_top3']}회

=== 유니언 럼블 팀 ===
{f"팀명: {stats.get('union_team_info', {}).get('team_name', '없음')}" if stats.get('union_team_info') else "참여 안함"}

이 모든 정보를 바탕으로 데비의 밝고 에너지 넘치는 성격으로 다음을 분석해주세요:
1. 플레이어의 주요 강점과 플레이 스타일
2. 구체적인 개선 방안 (어떤 캐릭터나 전략을 시도해볼지)
3. 이 플레이어에게 맞는 추천 팁
4. 격려의 말과 함께 실력 향상을 위한 조언
단순한 칭찬이 아니라 실제로 도움되는 구체적인 분석과 조언을 해주세요!"""
            
            response = await generate_ai_response(
                characters["debi"], 
                f"{닉네임} 전적 분석", 
                context_info
            )
        except Exception as e:
            print(f"AI 응답 생성 실패: {e}")
            # AI 응답 실패 시 기본 메시지 사용
            response = f"와! {닉네임}님의 전적을 찾았어! 데비가 열심히 분석해봤어!"
        
        # 전적 정보 포맷팅 (대폭 개선)
        stats_text = f"**🎮 플레이어**: {stats['nickname']}\n"
        
        found_info = False
        
        # 메인 티어 정보
        if stats['tier']:
            tier_text = stats['tier']
            if stats['rank_point'] and stats['rank_point'] > 0:
                tier_text += f" ({stats['rank_point']}RP)"
            stats_text += f"**🏆 최고 티어**: {tier_text}\n"
            found_info = True
        
        # 다중 모드 랭킹 정보
        if stats.get('multi_mode_ranks'):
            mode_emojis = {'솔로': '🥇', '듀오': '👥', '스쿼드': '👨\u200d👩\u200d👧\u200d👦'}
            rank_info_list = []
            for mode, rank_data in stats['multi_mode_ranks'].items():
                emoji = mode_emojis.get(mode, '🎮')
                if rank_data['rp'] > 0:
                    rank_info_list.append(f"{emoji} {mode}: {rank_data['tier']} ({rank_data['rp']}RP)")
                else:
                    rank_info_list.append(f"{emoji} {mode}: {rank_data['tier']}")
            
            if rank_info_list:
                stats_text += "\n**🎯 모드별 랭킹**\n" + "\n".join(rank_info_list) + "\n"
                found_info = True
        
        # 기본 통계
        if stats['total_games'] and stats['total_games'] > 0:
            stats_text += f"\n**📊 주요 통계** (가장 많이 플레이한 모드)\n"
            stats_text += f"🎯 **총 게임 수**: {stats['total_games']}게임\n"
            found_info = True
        
        if stats['winrate']:
            stats_text += f"📈 **승률**: {stats['winrate']}\n"
            found_info = True
            
        if stats['wins']:
            stats_text += f"🏅 **승리**: {stats['wins']}승\n"
            found_info = True
        
        if stats['avg_rank'] and stats['avg_rank'] > 0:
            stats_text += f"📊 **평균 순위**: {stats['avg_rank']:.1f}위\n"
            found_info = True
        
        # 모든 모드 통계
        if stats.get('all_modes_stats'):
            mode_stats = []
            for mode, mode_data in stats['all_modes_stats'].items():
                if mode_data['total_games'] > 0:
                    emoji = mode_emojis.get(mode, '🎮')
                    mode_stats.append(
                        f"{emoji} **{mode}**: {mode_data['total_games']}게임, "
                        f"{mode_data['winrate']} 승률, "
                        f"평균 {mode_data['avg_rank']:.1f}위"
                    )
            
            if mode_stats:
                stats_text += "\n**🎮 모드별 상세 통계**\n" + "\n".join(mode_stats) + "\n"
                found_info = True
        
        # 선호 캐릭터
        if stats.get('favorite_characters'):
            char_list = []
            for i, char in enumerate(stats['favorite_characters'][:3], 1):
                medal = ['🥇', '🥈', '🥉'][i-1]
                char_list.append(f"{medal} {char['character_name']} ({char['usage_count']}회)")
            
            if char_list:
                stats_text += "\n**⭐ 최애 캐릭터** (최근 게임 기준)\n" + "\n".join(char_list) + "\n"
                found_info = True
        
        # 최근 게임 성과
        if stats.get('recent_games'):
            recent_count = len(stats['recent_games'])
            if recent_count > 0:
                avg_rank = sum(game['rank'] for game in stats['recent_games']) / recent_count
                avg_kills = sum(game['kills'] for game in stats['recent_games']) / recent_count
                stats_text += f"\n**🕐 최근 {recent_count}게임**\n"
                stats_text += f"📊 평균 순위: {avg_rank:.1f}위\n"
                stats_text += f"⚔️ 평균 킬: {avg_kills:.1f}킬\n"
                found_info = True
        
        if not found_info:
            stats_text += "\n⚠️ 상세 정보를 가져오지 못했어!\n랭크 게임을 더 플레이해봐!\n"
        
        stats_text += f"\n🔗 **공식 API 기반 정보** | userNum: {stats['userNum']}"
        
        # 결과 임베드 생성 (더 풍부한 정보로)
        result_embed = create_character_embed(
            characters["debi"], 
            "🔍 전적 검색 결과", 
            f"{response}\n\n{stats_text}",
            f"/전적 {닉네임}"
        )
        result_embed.set_footer(text="데비가 이터널리턴 공식 API에서 가져온 완전한 정보야! 🚀")
        
        # 추가 필드로 정보 구조화 (임베드 한계 고려)
        if len(stats_text) > 1000:  # 너무 길면 분할
            # 기본 정보만 description에, 나머지는 별도 처리
            basic_info = f"**🎮 플레이어**: {stats['nickname']}\n"
            if stats['tier']:
                tier_text = stats['tier']
                if stats['rank_point'] and stats['rank_point'] > 0:
                    tier_text += f" ({stats['rank_point']}RP)"
                basic_info += f"**🏆 최고 티어**: {tier_text}\n"
            
            result_embed = create_character_embed(
                characters["debi"], 
                "🔍 전적 검색 결과", 
                f"{response}\n\n{basic_info}",
                f"/전적 {닉네임}"
            )
            
            # 상세 정보는 별도 필드로
            if stats.get('all_modes_stats'):
                mode_info = ""
                for mode, mode_data in list(stats['all_modes_stats'].items())[:3]:  # 최대 3개 모드
                    if mode_data['total_games'] > 0:
                        mode_info += f"**{mode}**: {mode_data['total_games']}게임, {mode_data['winrate']} 승률\n"
                if mode_info:
                    result_embed.add_field(name="🎮 모드별 통계", value=mode_info, inline=True)
            
            if stats.get('favorite_characters'):
                char_info = ""
                for char in stats['favorite_characters'][:3]:
                    char_info += f"• {char['character_name']} ({char['usage_count']}회)\n"
                if char_info:
                    result_embed.add_field(name="⭐ 최애 캐릭터", value=char_info, inline=True)
        
        result_embed.set_footer(text="데비가 이터널리턴 공식 API에서 가져온 완전한 정보야! 🚀")
        
        # 원본 메시지 편집
        await interaction.edit_original_response(embed=result_embed)
        
    except PlayerStatsError as e:
        try:
            if "player_not_found" in str(e):
                response = await generate_ai_response(
                    characters["debi"], 
                    f"{닉네임} 전적 검색 실패", 
                    "플레이어를 찾을 수 없었습니다"
                )
            else:
                response = await generate_ai_response(
                    characters["debi"], 
                    "전적 검색 오류", 
                    "전적 검색 중 오류가 발생했습니다"
                )
        except Exception as ai_error:
            print(f"AI 응답 생성 실패 (에러 처리): {ai_error}")
            # AI 응답 실패 시 기본 메시지 사용
            if "player_not_found" in str(e):
                response = f"앗! {닉네임} 플레이어를 찾을 수 없어!"
            else:
                response = "어? 뭔가 문제가 생긴 것 같아!"
        
        if "player_not_found" in str(e):
            error_embed = create_character_embed(
                characters["debi"], 
                "전적 검색 실패", 
                f"{response}\n\n❌ **'{닉네임}'** 플레이어를 찾을 수 없어!\n닉네임을 다시 확인해줘!",
                f"/전적 {닉네임}"
            )
        else:
            error_embed = create_character_embed(
                characters["debi"], 
                "전적 검색 오류", 
                f"{response}\n\n⚠️ 전적 검색 중 문제가 발생했어!\n잠시 후 다시 시도해줘!",
                f"/전적 {닉네임}"
            )
        
        await interaction.edit_original_response(embed=error_embed)

@bot.tree.command(name="유튜브", description="데비가 이터널리턴 관련 유튜브 영상을 찾아드려요")
async def youtube_slash(interaction: discord.Interaction, 검색어: Optional[str] = None):
    """유튜브 검색 슬래시 커맨드"""
    try:
        # 즉시 응답으로 검색 중 메시지 보내기
        embed = discord.Embed(
            color=characters["debi"]["color"],
            title="🔍 유튜브 검색 중...",
            description="데비가 이터널리턴 관련 영상을 찾고 있어! 잠깐만 기다려줘!"
        )
        
        # 인터랙션이 만료되지 않았는지 확인
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed)
        else:
            return
        if not youtube:
            # YouTube API가 없을 때 기본 응답
            response = await generate_ai_response(
                characters["debi"], "유튜브 검색", "YouTube API가 설정되지 않았지만 유튜브 관련 요청을 받았습니다"
            )
            
            message_content = f"📺 **{response}**\n\n" \
                             f"이터널리턴 공식 채널에서 최신 영상을 확인해보세요!\n" \
                             f"https://www.youtube.com/@EternalReturnKR"
            
            await interaction.edit_original_response(content=message_content, embed=None, attachments=[])
            return
        
        # 검색 쿼리 설정
        if 검색어:
            search_query = f"이터널리턴 {검색어}"
        else:
            search_query = "이터널리턴"
        
        # YouTube 검색
        request = youtube.search().list(
            part='snippet',
            q=search_query,
            type='video',
            order='relevance',
            maxResults=1,
            regionCode='KR',
            relevanceLanguage='ko'
        )
        response_data = request.execute()
        
        if response_data.get('items'):
            video = response_data['items'][0]
            video_id = video['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # 데비의 AI 응답 생성
            ai_response = await generate_ai_response(
                characters["debi"], 
                f"유튜브 검색: {검색어 or '이터널리턴'}", 
                f"이터널리턴 관련 유튜브 영상을 찾았습니다: {video['snippet']['title']}"
            )
            
            # 채널명과 업로드 날짜 정보
            upload_date = datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
            channel_name = video['snippet']['channelTitle']
            
            # 메시지 구성: AI 응답 + 영상 정보 + 링크
            message_content = f"🎬 **{ai_response}**\n\n" \
                             f"📺 **{video['snippet']['title']}**\n" \
                             f"📅 {upload_date} | 📺 {channel_name}\n\n" \
                             f"{video_url}"
            
            await interaction.edit_original_response(content=message_content, embed=None, attachments=[])
            
        else:
            # 검색 결과가 없을 때
            response = await generate_ai_response(
                characters["debi"], 
                f"유튜브 검색 실패: {검색어 or '이터널리턴'}", 
                "검색 결과가 없었습니다"
            )
            
            message_content = f"🔍 **{response}**\n\n" \
                             f"'{검색어 or '이터널리턴'}' 관련 영상을 찾지 못했어... 다른 검색어로 다시 시도해봐!"
            
            await interaction.edit_original_response(content=message_content, embed=None, attachments=[])
            
    except Exception as error:
        print(f'YouTube 검색 오류: {error}')
        
        # 에러 시 기본 응답
        response = await generate_ai_response(
            characters["debi"], "유튜브 검색 오류", "유튜브 검색 중 오류가 발생했습니다"
        )
        
        message_content = f"💥 **{response}**\n\n" \
                         f"어? 뭔가 문제가 생긴 것 같아! 나중에 다시 시도해줘!"
        
        await interaction.edit_original_response(content=message_content, embed=None, attachments=[])
        
    except discord.NotFound:
        print("❌ Discord 인터랙션 타임아웃 - 사용자가 너무 오래 기다렸습니다")
        # 이미 만료된 인터랙션은 처리할 수 없음
        return
    except Exception as error:
        print(f'유튜브 커맨드 전체 오류: {error}')
        
        # 인터랙션이 아직 유효하면 에러 메시지 전송 시도
        try:
            if not interaction.response.is_done():
                error_embed = discord.Embed(
                    color=discord.Color.red(),
                    title="❌ 오류 발생",
                    description="데비가 당황했어! 뭔가 문제가 생긴 것 같아... 😅"
                )
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                error_embed = discord.Embed(
                    color=discord.Color.red(),
                    title="❌ 오류 발생", 
                    description="데비가 당황했어! 뭔가 문제가 생긴 것 같아... 😅"
                )
                await interaction.edit_original_response(embed=error_embed)
        except:
            pass  # 에러 메시지도 보낼 수 없으면 포기


async def generate_ai_response(character: Dict[str, Any], user_message: str, context: str = "") -> str:
    """AI 응답 생성 함수"""
    if not anthropic_client:
        raise Exception("Claude API 클라이언트가 초기화되지 않았습니다")
    
    print(f"🤖 Claude API 호출 시작 - 캐릭터: {character['name']}, 메시지: {user_message[:50]}...")
    
    prompt = f"""{character['ai_prompt']}

사용자 메시지: "{user_message}"
상황: {context}

위 캐릭터 성격에 맞게 한국어로 자연스럽게 대답해줘. 너무 길지 않게 1-2문장으로."""

    # Claude API 호출 (전적 분석의 경우 더 많은 토큰 허용)
    max_tokens_count = 300 if "전적 분석" in user_message or "분석" in context else 150
    
    message = await anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=max_tokens_count,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    response = message.content[0].text
    print(f"✅ Claude API 응답 성공: {response[:50]}...")
    return response

def create_character_embed(character: Dict[str, Any], title: str, description: str, user_message: str = None) -> discord.Embed:
    """캐릭터별 임베드 생성"""
    embed = discord.Embed(
        color=character["color"],
        description=description
    )
    
    if user_message:
        embed.add_field(name="💬 메시지", value=f"```{user_message}```", inline=False)
    
    if character["image"]:
        embed.set_author(
            name=character["name"],
            icon_url=character["image"]
        )
    else:
        embed.set_author(name=character["name"])
    
    embed.set_footer(text='이터널리턴')
    
    return embed

@tasks.loop(minutes=5)
async def check_youtube_shorts():
    """YouTube 쇼츠 체크 함수"""
    global last_checked_video_id
    
    try:
        if not youtube:
            print("⚠️ YouTube API가 설정되지 않음")
            return
        
        # 이터널리턴 채널의 최신 쇼츠 확인
        request = youtube.search().list(
            part='snippet',
            channelId=ETERNAL_RETURN_CHANNEL_ID,
            type='video',
            videoDuration='short',  # 쇼츠만
            order='date',
            maxResults=1
        )
        response = request.execute()
        
        if response.get('items'):
            latest_video = response['items'][0]
            
            # 새로운 영상인지 확인
            if last_checked_video_id != latest_video['id']['videoId']:
                last_checked_video_id = latest_video['id']['videoId']
                
                # 모든 길드에 알림 전송
                for guild in bot.guilds:
                    channel = discord.utils.find(
                        lambda ch: any(name in ch.name for name in ['일반', '알림', 'general']),
                        guild.text_channels
                    )
                    
                    if channel:
                        embed = discord.Embed(
                            color=characters["debi"]["color"],
                            title='🎬 새로운 이터널리턴 쇼츠!',
                            description=latest_video['snippet']['title'],
                            url=f"https://www.youtube.com/watch?v={latest_video['id']['videoId']}"
                        )
                        embed.set_thumbnail(url=latest_video['snippet']['thumbnails']['medium']['url'])
                        embed.add_field(
                            name='채널', 
                            value=latest_video['snippet']['channelTitle'], 
                            inline=True
                        )
                        embed.add_field(
                            name='업로드', 
                            value=datetime.fromisoformat(latest_video['snippet']['publishedAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S'), 
                            inline=True
                        )
                        embed.set_footer(text='데비가 발견한 새로운 영상!')
                        
                        # 공지 채널로만 전송
                        if ANNOUNCEMENT_CHANNEL_ID:
                            announcement_channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
                            if announcement_channel:
                                await announcement_channel.send(embed=embed)
                        else:
                            await channel.send(embed=embed)
                        
    except Exception as error:
        print(f'YouTube 체크 오류: {error}')

@check_youtube_shorts.before_loop
async def before_check_youtube_shorts():
    """YouTube 체크 시작 전 봇 준비 대기"""
    await bot.wait_until_ready()

@bot.tree.command(name="채널설정", description="봇이 사용할 채널을 설정합니다 (관리자 전용)")
async def set_channels(interaction: discord.Interaction, 공지채널: discord.TextChannel = None, 대화채널: discord.TextChannel = None):
    """채널 설정 커맨드"""
    await interaction.response.defer()
    
    # 관리자 권한 체크
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ 이 명령어는 관리자만 사용할 수 있습니다.", ephemeral=True)
        return
    
    global ANNOUNCEMENT_CHANNEL_ID, CHAT_CHANNEL_ID
    
    if 공지채널:
        ANNOUNCEMENT_CHANNEL_ID = 공지채널.id
        
    if 대화채널:
        CHAT_CHANNEL_ID = 대화채널.id
    
    settings_text = []
    if ANNOUNCEMENT_CHANNEL_ID:
        settings_text.append(f"🔔 공지 채널: <#{ANNOUNCEMENT_CHANNEL_ID}>")
    if CHAT_CHANNEL_ID:
        settings_text.append(f"💬 대화 채널: <#{CHAT_CHANNEL_ID}>")
    
    if not settings_text:
        settings_text.append("❌ 설정된 채널이 없습니다.")
    
    embed = discord.Embed(
        title="📋 채널 설정 완료",
        description="\n".join(settings_text),
        color=0x00FF00
    )
    
    await interaction.followup.send(embed=embed)

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))