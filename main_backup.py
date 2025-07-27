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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
from PIL import Image, ImageDraw, ImageFont
import requests

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

# 티어 이미지 URL 매핑
TIER_IMAGES = {
    "언랭": "https://static.dakgg.io/images/er/tiers/00-iron.png",
    "언랭크": "https://static.dakgg.io/images/er/tiers/00-iron.png",
    "아이언": "https://static.dakgg.io/images/er/tiers/01-iron.png", 
    "브론즈": "https://static.dakgg.io/images/er/tiers/02-bronze.png",
    "실버": "https://static.dakgg.io/images/er/tiers/03-silver.png",
    "골드": "https://static.dakgg.io/images/er/tiers/04-gold.png",
    "플래티넘": "https://static.dakgg.io/images/er/tiers/05-platinum.png",
    "다이아몬드": "https://static.dakgg.io/images/er/tiers/06-diamond.png",
    "미스릴": "https://static.dakgg.io/images/er/tiers/07-mithril.png",
    "오리칼쿰": "https://static.dakgg.io/images/er/tiers/08-orihalcum.png"
}



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

# 닥지지 API 설정
DAKGG_API_BASE = "https://er.dakgg.io/api/v1"


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
                
                response = await session.get(url, headers=headers, timeout=10)
                print(f"상태 코드: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"응답 키들: {list(data.keys()) if isinstance(data, dict) else 'List type'}")
                    
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"  {key}: 리스트 (길이: {len(value)})")
                                if value and len(value) > 0:
                                    print(f"    첫 번째 항목 키들: {list(value[0].keys()) if isinstance(value[0], dict) else type(value[0])}")
                            else:
                                print(f"  {key}: {type(value)} = {value if not isinstance(value, (dict, list)) else f'{type(value)} with {len(value)} items'}")
                    
                    # JSON 전체 구조 출력 (처음 200자만)
                    json_str = json.dumps(data, indent=2, ensure_ascii=False)
                    print(f"\n전체 JSON 구조 (처음 500자):\n{json_str[:500]}...")
                else:
                    error_text = await response.text()
                    print(f"오류 응답: {error_text[:200]}")
                    
            except Exception as e:
                print(f"요청 실패: {e}")

async def get_player_stats_from_dakgg(nickname: str, detailed: bool = False) -> Optional[Dict[str, Any]]:
    """닥지지 API를 사용해서 플레이어 통계 정보 가져오기"""
    try:
        # 닉네임 URL 인코딩
        encoded_nickname = urllib.parse.quote(nickname)
        
        # API URL 구성
        player_url = f'{DAKGG_API_BASE}/players/{encoded_nickname}/profile?season=SEASON_17'
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
            
            if (player_response.status == 200 and 
                tier_response.status == 200 and 
                character_response.status == 200):
                
                player_data = await player_response.json()
                tier_data = await tier_response.json()
                character_data = await character_response.json()
                
                # 결과 딕셔너리 초기화
                result = {
                    'nickname': nickname,
                    'tier_info': None,
                    'most_character': None,
                    'stats': {}
                }
                
                # 현재 시즌 정보 추출
                if 'playerSeasons' not in player_data or len(player_data['playerSeasons']) == 0:
                    return None
                    
                current_season = player_data['playerSeasons'][0]
                
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
                    result['tier_info'] = f'**{tier_name}** (MMR {mmr})'
                else:
                    result['tier_info'] = f'**{tier_name} {grade_name}** {tier_mmr} RP (MMR {mmr})'
                
                # 티어 이미지 URL 추가
                result['tier_image_url'] = tier_image
                
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
                        'avg_team_kills': round(rank_stats.get('teamKill', 0) / max(rank_stats.get('play', 1), 1), 1),
                        'avg_damage': round(rank_stats.get('damageToPlayer', 0) / max(rank_stats.get('play', 1), 1)),
                        'top2': rank_stats.get('top2', 0),
                        'top3': rank_stats.get('top3', 0),
                        'top2_rate': round((rank_stats.get('top2', 0) / max(rank_stats.get('play', 1), 1)) * 100, 1),
                        'top3_rate': round((rank_stats.get('top3', 0) / max(rank_stats.get('play', 1), 1)) * 100, 1),
                        'mmr': mmr
                    }
                    
                    # 모스트 캐릭터들 찾기 (상위 3개)
                    character_stats = rank_stats.get('characterStats', [])
                    if character_stats:
                        # 게임 수 순으로 정렬
                        sorted_chars = sorted(character_stats, key=lambda x: x.get('play', 0), reverse=True)
                        
                        # 1위 캐릭터 (기존 호환성을 위해)
                        if sorted_chars:
                            most_char_stat = sorted_chars[0]
                            char_key = most_char_stat.get('key', '')
                            
                            # 캐릭터 정보 찾기
                            for char in character_data.get('characters', []):
                                if char.get('id') == char_key:
                                    result['most_character'] = {
                                        'name': char.get('name', '알 수 없음'),
                                        'key': char_key,
                                        'image_url': char.get('imageUrl', ''),
                                        'games': most_char_stat.get('play', 0),
                                        'wins': most_char_stat.get('win', 0),
                                        'winrate': round((most_char_stat.get('win', 0) / max(most_char_stat.get('play', 1), 1)) * 100, 1)
                                    }
                                    break
                        
                        # 상위 10개 캐릭터 통계 (detailed 모드에서 사용)
                        if detailed:
                            top_10_chars = []
                            for i, char_stat in enumerate(sorted_chars[:10]):
                                char_key = char_stat.get('key', '')
                                games = char_stat.get('play', 0)
                                wins = char_stat.get('win', 0)
                                winrate = round((wins / max(games, 1)) * 100, 1) if games > 0 else 0
                                
                                char_info = {
                                    'name': '알 수 없음',
                                    'games': games,
                                    'wins': wins,
                                    'winrate': winrate,
                                    'image_url': None
                                }
                                
                                # 캐릭터 이름과 이미지 찾기
                                for char in character_data.get('characters', []):
                                    if char.get('id') == char_key:
                                        char_info['name'] = char.get('name', '알 수 없음')
                                        char_info['image_url'] = char.get('imageUrl')
                                        break
                                
                                if games > 0:
                                    top_10_chars.append(char_info)
                                    print(f"✅ 캐릭터 {i+1}위: {char_info['name']} ({char_info['games']}게임, {char_info['winrate']}% 승률)")
                            
                            result['character_stats'] = top_10_chars
                            print(f"✅ playerSeasonOverviews에서 캐릭터 통계 {len(top_10_chars)}개 로드")
                
                # 상세 정보 요청시 경기 데이터도 가져오기
                if detailed:
                    matches_url = f'{DAKGG_API_BASE}/players/{encoded_nickname}/matches?season=SEASON_17&matchingMode=RANK&teamMode=ALL&page=1'
                    matches_response = await session.get(matches_url, headers=headers, timeout=10)
                    
                    if matches_response.status == 200:
                        matches_data = await matches_response.json()
                        result['matches_data'] = matches_data.get('matches', [])
                    else:
                        result['matches_data'] = []
                
                return result
            else:
                print(f'닥지지 API 오류: Player {player_response.status}, Tier {tier_response.status}, Character {character_response.status}')
                return None
                
    except Exception as e:
        print(f'닥지지 API 오류: {e}')
        return None

async def get_tier_info_from_dakgg(nickname: str) -> Optional[str]:
    """기존 호환성을 위한 간단한 티어 정보 함수"""
    stats = await get_player_stats_from_dakgg(nickname)
    return stats['tier_info'] if stats else None

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


# 현재 시즌 ID 캐시
current_season_cache = {"season_id": None, "last_updated": 0}

async def get_current_season_id() -> str:
    """현재 활성화된 시즌 ID를 가져오는 함수 (캐싱 적용)"""
    import time
    
    # 1시간마다 갱신 (3600초)
    if (current_season_cache["season_id"] and 
        time.time() - current_season_cache["last_updated"] < 3600):
        return current_season_cache["season_id"]
    
    try:
        season_meta = await get_meta_data_er("Season")
        if season_meta and season_meta.get('data'):
            # isCurrent가 1인 시즌 찾기
            current_seasons = [s for s in season_meta['data'] if s.get('isCurrent') == 1]
            
            if current_seasons:
                season_id = str(current_seasons[0]['seasonID'])
                current_season_cache["season_id"] = season_id
                current_season_cache["last_updated"] = time.time()
                print(f"✅ 현재 시즌 ID: {season_id}")
                return season_id
            else:
                # 가장 높은 seasonID 사용
                latest_season = max(season_meta['data'], key=lambda x: x['seasonID'])
                season_id = str(latest_season['seasonID'])
                current_season_cache["season_id"] = season_id
                current_season_cache["last_updated"] = time.time()
                print(f"⚠️ 활성 시즌 없음, 최신 시즌 사용: {season_id}")
                return season_id
    except Exception as e:
        print(f"⚠️ 시즌 조회 실패: {e}")
    
    # 기본값
    return "17"

async def get_simple_player_stats_only_tier(nickname: str) -> str:
    """
    간단한 티어 정보만 가져오는 함수 - API 호출 최소화
    """
    try:
        # 1. 닉네임으로 유저 정보 조회
        user_info = await get_user_by_nickname_er(nickname)
        
        if not user_info.get('user'):
            return "❌ 플레이어를 찾을 수 없어요!"
        
        user_data = user_info['user']
        user_num = str(user_data['userNum'])
        
        # 실제 게임 시즌 ID 확인 (최근 게임에서 가져오기)
        recent_games = await get_user_recent_games_er(user_num)
        current_season = "33"  # 기본값
        if recent_games and not isinstance(recent_games, Exception) and recent_games.get('userGames'):
            if recent_games['userGames']:
                current_season = str(recent_games['userGames'][0].get('seasonId', 33))
                print(f"🔍 실제 게임 시즌 ID: {current_season}")
        
        # 2. 솔로 랭킹만 빠르게 확인 (API 호출 최소화)
        solo_rank = await get_user_rank_er(user_num, current_season, "3")
        
        # 3. 티어 매핑 데이터 로드 (한 번만)
        tier_mapping = []
        try:
            tier_meta = await get_meta_data_er("MatchingQueueTier")
            print(f"🔍 tier_meta 응답: {tier_meta}")
            if tier_meta and tier_meta.get('data'):
                print(f"🔍 tier_meta 데이터 개수: {len(tier_meta['data'])}")
                # 필터링 전 데이터 확인
                print(f"🔍 현재 시즌: {current_season}, 타입: {type(current_season)}")
                all_tiers = tier_meta['data']
                print(f"🔍 첫 번째 티어 데이터 샘플: {all_tiers[0] if all_tiers else 'None'}")
                
                # 서울(Seoul) 지역의 랭크 모드 솔로 티어 데이터만 필터링
                seoul_solo_tiers = [tier for tier in tier_meta['data'] if 
                                  tier.get('matchingRegion') == 'Seoul' and 
                                  tier.get('matchingMode') == 'Rank' and 
                                  tier.get('teamMode') == 'Solo']
                print(f"🔍 필터링된 티어 개수: {len(seoul_solo_tiers)}")
                if seoul_solo_tiers:
                    print(f"🔍 첫 번째 필터링된 티어: {seoul_solo_tiers[0]}")
                
                seoul_solo_tiers.sort(key=lambda x: x.get('mmrMoreThan', 0))
                tier_mapping = seoul_solo_tiers
            else:
                print("⚠️ tier_meta 데이터 없음")
        except Exception as e:
            print(f"⚠️ 티어 메타데이터 로드 실패: {e}")
            pass
        
        def mmr_to_tier(mmr):
            print(f"🔍 mmr_to_tier 호출: MMR={mmr}, tier_mapping 개수={len(tier_mapping)}")
            if not tier_mapping or mmr <= 0:
                return "Unranked"
            for tier in reversed(tier_mapping):
                mmr_threshold = tier.get('mmrMoreThan', 0)
                tier_name = tier.get('tierType', 'Unranked')
                print(f"🔍 티어 체크: {tier_name} (최소 MMR: {mmr_threshold})")
                if mmr >= mmr_threshold:
                    print(f"✅ 매칭된 티어: {tier_name}")
                    return tier_name
            return "Unranked"
        
        # 4. 간단한 결과 텍스트 생성 (디버깅 추가)
        result = f"**🎮 플레이어**: {user_data['nickname']}\n\n"
        
        print(f"🔍 solo_rank 디버깅: {type(solo_rank)}, 예외: {isinstance(solo_rank, Exception)}")
        if solo_rank and not isinstance(solo_rank, Exception):
            print(f"🔍 solo_rank 키들: {list(solo_rank.keys()) if isinstance(solo_rank, dict) else 'Not dict'}")
            print(f"🔍 solo_rank 내용: {solo_rank}")
        
        if solo_rank and not isinstance(solo_rank, Exception) and solo_rank.get('userRank'):
            mmr = solo_rank['userRank'].get('mmr', 0)
            tier = mmr_to_tier(mmr)
            print(f"🔍 MMR: {mmr}, 계산된 티어: {tier}")
            result += f"🥇 **솔로 랭크**: {tier} ({mmr}점)"
        else:
            print(f"⚠️ 랭킹 데이터 없음 - solo_rank: {solo_rank}")
            result += f"🥇 **솔로 랭크**: Unranked"
        
        return result
        
    except Exception as e:
        return f"❌ 전적 조회 중 오류가 발생했어요: {str(e)}"

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


# 전적 표시용 View 클래스
class StatsView(discord.ui.View):
    def __init__(self, player_stats: dict, most_char: dict, stats: dict, detailed_data: dict = None):
        super().__init__(timeout=300)  # 5분 타임아웃
        self.player_stats = player_stats
        self.most_char = most_char
        self.stats = stats
        self.detailed_data = detailed_data
        # 마를렌과 데비 번갈아 사용
        self.character_pool = ["debi", "marlene"]
        self.button_characters = {
            "rank": random.choice(self.character_pool),
            "character": random.choice(self.character_pool), 
            "stats": random.choice(self.character_pool)
        }

    async def _get_previous_season_data(self, nickname: str) -> str:
        """이전 시즌 데이터 가져오기 (기존 profile API에서 seasonId 31 찾기)"""
        try:
            encoded_nickname = urllib.parse.quote(nickname)
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://dak.gg',
                'Referer': 'https://dak.gg/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            # DAKGG API Base URL  
            DAKGG_API_BASE = 'https://er.dakgg.io/api/v1'
            
            async with aiohttp.ClientSession() as session:
                # Profile API에서 모든 시즌 데이터 가져오기 (HAR 파일 분석 결과)
                profile_url = f'{DAKGG_API_BASE}/players/{encoded_nickname}/profile'
                tier_url = f'{DAKGG_API_BASE}/data/tiers?hl=ko'
                
                print(f"🔍 Profile API 호출: {profile_url}")
                
                # 프로필과 티어 데이터 동시 요청
                profile_task = session.get(profile_url, headers=headers, timeout=10)
                tier_task = session.get(tier_url, headers=headers, timeout=10)
                
                profile_response, tier_response = await asyncio.gather(profile_task, tier_task, return_exceptions=True)
                
                if (not isinstance(profile_response, Exception) and profile_response.status == 200 and
                    not isinstance(tier_response, Exception) and tier_response.status == 200):
                    
                    profile_data = await profile_response.json()
                    tier_data = await tier_response.json()
                    
                    print(f"🔍 Profile 데이터 키들: {list(profile_data.keys())}")
                    player_seasons = profile_data.get('playerSeasons', [])
                    print(f"🔍 플레이어 시즌 목록 (총 {len(player_seasons)}개):")
                    for season in player_seasons[:5]:  # 처음 5개만 출력
                        print(f"  - seasonId: {season.get('seasonId')}, mmr: {season.get('mmr')}, tierId: {season.get('tierId')}")
                    
                    # seasonId 31 (Season 16 = 게임 내 시즌 7) 찾기
                    prev_season_data = None
                    for season in player_seasons:
                        if season.get('seasonId') == 31:  # Season 16 (게임 내 시즌 7)
                            prev_season_data = season
                            break
                    
                    if prev_season_data and prev_season_data.get('mmr') is not None:
                        print(f"🔍 Season 16 (게임 내 시즌 7) 데이터 발견: {prev_season_data}")
                        
                        mmr = prev_season_data.get('mmr', 0)
                        tier_id = prev_season_data.get('tierId', 0)
                        tier_grade_id = prev_season_data.get('tierGradeId', 1)
                        tier_mmr = prev_season_data.get('tierMmr', 0)
                        
                        # 티어 이름 찾기
                        tier_name = '언랭크'
                        for tier in tier_data.get('tiers', []):
                            if tier['id'] == tier_id:
                                tier_name = tier['name']
                                break
                        
                        # 티어 등급 매핑
                        grade_name = str(tier_grade_id)
                        
                        result = f'{tier_name} {grade_name} {tier_mmr} RP (MMR {mmr})' if tier_id != 0 else f'{tier_name} (MMR {mmr})'
                        print(f"✅ Season 16 (게임 내 시즌 7) 결과: {result}")
                        return result
                    else:
                        print("❌ Season 16 (seasonId 31) 데이터가 없거나 MMR이 없음")
                        return None
                else:
                    if not isinstance(profile_response, Exception):
                        error_text = await profile_response.text()
                        print(f"❌ Profile API 오류 ({profile_response.status}): {error_text[:200]}")
                    else:
                        print(f"❌ Profile API 예외: {profile_response}")
                    return None
                    
        except Exception as e:
            print(f"이전 시즌 데이터 오류: {e}")
            return None
            
    def _get_performance_indicator(self, value: float, stat_type: str) -> str:
        """성적에 따른 시각적 표시기 반환"""
        if stat_type == "winrate":
            if value >= 70: return "🟢"  # 초록 - 매우 좋음
            elif value >= 50: return "🟡"  # 노랑 - 좋음  
            elif value >= 30: return "🟠"  # 주황 - 보통
            else: return "🔴"  # 빨강 - 나쁨
        elif stat_type == "avg_rank":
            if value <= 3: return "🟢"  # 3등 이상
            elif value <= 6: return "🟡"  # 6등 이상
            elif value <= 10: return "🟠"  # 10등 이상 
            else: return "🔴"  # 11등 이하
        elif stat_type == "avg_kills":
            if value >= 5: return "🟢"  # 5킬 이상
            elif value >= 3: return "🟡"  # 3킬 이상
            elif value >= 1.5: return "🟠"  # 1.5킬 이상
            else: return "🔴"  # 1.5킬 미만
        elif stat_type == "top2_rate":
            if value >= 40: return "🟢"  # 40% 이상
            elif value >= 25: return "🟡"  # 25% 이상
            elif value >= 15: return "🟠"  # 15% 이상
            else: return "🔴"  # 15% 미만
        elif stat_type == "avg_damage":
            if value >= 15000: return "🟢"  # 15000 이상
            elif value >= 10000: return "🟡"  # 10000 이상
            elif value >= 6000: return "🟠"  # 6000 이상
            else: return "🔴"  # 6000 미만
        else:
            return ""  # 기본값
    
    async def _get_previous_season_tier_image(self, nickname: str) -> str:
        """이전 시즌 티어 이미지 URL 가져오기"""
        try:
            encoded_nickname = urllib.parse.quote(nickname)
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://dak.gg',
                'Referer': 'https://dak.gg/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            DAKGG_API_BASE = 'https://er.dakgg.io/api/v1'
            
            async with aiohttp.ClientSession() as session:
                profile_url = f'{DAKGG_API_BASE}/players/{encoded_nickname}/profile'
                tier_url = f'{DAKGG_API_BASE}/data/tiers?hl=ko'
                
                profile_task = session.get(profile_url, headers=headers, timeout=10)
                tier_task = session.get(tier_url, headers=headers, timeout=10)
                
                profile_response, tier_response = await asyncio.gather(profile_task, tier_task, return_exceptions=True)
                
                if (not isinstance(profile_response, Exception) and profile_response.status == 200 and
                    not isinstance(tier_response, Exception) and tier_response.status == 200):
                    
                    profile_data = await profile_response.json()
                    tier_data = await tier_response.json()
                    
                    player_seasons = profile_data.get('playerSeasons', [])
                    
                    # seasonId 31 (Season 16) 찾기
                    prev_season_data = None
                    for season in player_seasons:
                        if season.get('seasonId') == 31:
                            prev_season_data = season
                            break
                    
                    if prev_season_data and prev_season_data.get('tierId'):
                        tier_id = prev_season_data.get('tierId', 0)
                        
                        # 티어 이미지 찾기
                        for tier in tier_data.get('tiers', []):
                            if tier['id'] == tier_id:
                                tier_image = tier.get('imageUrl') or tier.get('image') or tier.get('icon')
                                if tier_image:
                                    return "https:" + tier_image if tier_image.startswith('//') else tier_image
                                break
                    
            return None
        except Exception as e:
            print(f"이전 시즌 티어 이미지 오류: {e}")
            return None

    @discord.ui.button(label='랭크', style=discord.ButtonStyle.success, emoji='🏆')
    async def show_rank(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 랭크",
            color=0x00D4AA
        )
        # 랭크 버튼용 캐릭터
        char_key = self.button_characters["rank"]
        embed.set_author(name=characters[char_key]["name"], icon_url=characters[char_key]["image"])
        embed.set_footer(text="이터널 리턴")
        
        # 현재 시즌 랭크 - 폰트 스타일링 개선
        current_tier = self.player_stats['tier_info'].replace('**', '')
        # 티어명과 숫자/RP를 분리해서 다른 스타일 적용
        import re
        tier_match = re.match(r'(.+?)\s+(\d+)\s+(\d+)\s+RP\s+\(MMR\s+(\d+)\)', current_tier)
        if tier_match:
            tier_name, grade, rp, mmr = tier_match.groups()
            formatted_current = f"**{tier_name}** `{grade}` **{rp}** `RP` (MMR {mmr})"
        else:
            formatted_current = f"**{current_tier}**"
            
        embed.add_field(
            name="현재 시즌 (Season 17 - 게임 내 시즌 8)",
            value=formatted_current,
            inline=False
        )
        
        # 저번 시즌 정보 (Season 16)
        try:
            prev_season_info = await self._get_previous_season_data(self.player_stats['nickname'])
            if prev_season_info:
                # 이전 시즌도 같은 폰트 스타일링 적용
                prev_tier_match = re.match(r'(.+?)\s+(\d+)\s+(\d+)\s+RP\s+\(MMR\s+(\d+)\)', prev_season_info)
                if prev_tier_match:
                    prev_tier_name, prev_grade, prev_rp, prev_mmr = prev_tier_match.groups()
                    formatted_prev = f"**{prev_tier_name}** `{prev_grade}` **{prev_rp}** `RP` (MMR {prev_mmr})"
                else:
                    formatted_prev = f"**{prev_season_info}**"
                
                embed.add_field(
                    name="이전 시즌 (Season 16 - 게임 내 시즌 7)",
                    value=formatted_prev,
                    inline=False
                )
            else:
                embed.add_field(
                    name="이전 시즌 (Season 16 - 게임 내 시즌 7)",
                    value="`데이터 없음`",
                    inline=False
                )
        except:
            embed.add_field(
                name="이전 시즌 (Season 16 - 게임 내 시즌 7)",
                value="`데이터 없음`",
                inline=False
            )
        
        # 현재 시즌 티어 이미지를 큰 이미지로 설정
        if self.player_stats and self.player_stats.get('tier_image_url'):
            tier_image_raw = self.player_stats.get('tier_image_url')
            current_tier_image_url = "https:" + tier_image_raw if tier_image_raw.startswith('//') else tier_image_raw
            embed.set_image(url=current_tier_image_url)
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='실험체', style=discord.ButtonStyle.primary, emoji='🎯')
    async def show_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 모스트 실험체",
            color=0x5865F2
        )
        # 실험체 버튼용 캐릭터
        char_key = self.button_characters["character"]
        embed.set_author(name=characters[char_key]["name"], icon_url=characters[char_key]["image"])
        embed.set_footer(text="이터널 리턴")
        
        # 상세 데이터가 없으면 가져오기
        if not self.detailed_data:
            await interaction.response.defer()
            try:
                self.detailed_data = await get_player_stats_from_dakgg(self.player_stats['nickname'], detailed=True)
            except:
                await interaction.followup.edit_message(content="❌ 실험체 정보를 불러오는데 실패했습니다.")
                return
        
        # 모스트 10개 실험체 표시
        if self.detailed_data and self.detailed_data.get('character_stats'):
            # API에서 캐릭터 통계 가져오기
            char_stats = self.detailed_data['character_stats'][:10]  # 상위 10개
            
            # 10개를 깔끔하게 배치 (3열씩)
            for i, char in enumerate(char_stats):
                rank_num = i + 1
                
                embed.add_field(
                    name=f"{rank_num}위", 
                    value=f"**{char.get('name', '알 수 없음')}**\n`{char.get('games', 0)}게임` **{char.get('winrate', 0):.1f}%** `승률`", 
                    inline=True
                )
                
                # 3개마다 줄바꿈 (Discord embed는 3개씩 한 줄)
                if (i + 1) % 3 == 0:
                    # 빈 필드 없이 자연스럽게 줄바꿈 됨
                    pass
            
            # 1순위 캐릭터 이미지만 큰 이미지로 설정
            if char_stats and char_stats[0].get('image_url'):
                char_image_url = "https:" + char_stats[0]['image_url'] if char_stats[0]['image_url'].startswith('//') else char_stats[0]['image_url']
                embed.set_image(url=char_image_url)
        
        elif self.most_char:
            # detailed_data가 없는 경우에도 상세 데이터 요청 시도
            try:
                await interaction.response.defer()
                detailed_data = await get_player_stats_from_dakgg(self.player_stats['nickname'], detailed=True)
                if detailed_data and detailed_data.get('character_stats') and len(detailed_data['character_stats']) > 1:
                    # 상세 데이터로 업데이트
                    self.detailed_data = detailed_data
                    char_stats = detailed_data['character_stats'][:10]  # 상위 10개
                    
                    # 10개를 깔끔하게 배치 (3열씩)
                    for i, char in enumerate(char_stats):
                        rank_num = i + 1
                        
                        embed.add_field(
                            name=f"{rank_num}위", 
                            value=f"**{char.get('name', '알 수 없음')}**\n`{char.get('games', 0)}게임` **{char.get('winrate', 0):.1f}%** `승률`", 
                            inline=True
                        )
                    
                    # 1순위 캐릭터 이미지만 큰 이미지로 설정
                    if char_stats and char_stats[0].get('image_url'):
                        char_image_url = "https:" + char_stats[0]['image_url'] if char_stats[0]['image_url'].startswith('//') else char_stats[0]['image_url']
                        embed.set_image(url=char_image_url)
                else:
                    # 여전히 데이터가 없는 경우 기본 표시
                    embed.add_field(
                        name="1위", 
                        value=f"**{self.most_char['name']}**\n`{self.most_char['games']}게임` **{self.most_char['winrate']}%** `승률`", 
                        inline=True
                    )
                    for i in range(2, 11):
                        embed.add_field(
                            name=f"{i}위", 
                            value=f"**`데이터 수집 중..`**\n-", 
                            inline=True
                        )
                    
                    # 1순위 캐릭터 이미지를 큰 이미지로 설정
                    if self.most_char.get('image_url'):
                        char_image_url = "https:" + self.most_char['image_url'] if self.most_char['image_url'].startswith('//') else self.most_char['image_url']
                        embed.set_image(url=char_image_url)
            except Exception as e:
                print(f"캐릭터 상세 데이터 요청 실패: {e}")
                # 기본 표시로 fallback
                embed.add_field(
                    name="1위", 
                    value=f"**{self.most_char['name']}**\n`{self.most_char['games']}게임` **{self.most_char['winrate']}%** `승률`", 
                    inline=True
                )
                for i in range(2, 11):
                    embed.add_field(
                        name=f"{i}위", 
                        value=f"**`데이터 수집 중..`**\n-", 
                        inline=True
                    )
                
                # 1순위 캐릭터 이미지를 큰 이미지로 설정
                if self.most_char.get('image_url'):
                    char_image_url = "https:" + self.most_char['image_url'] if self.most_char['image_url'].startswith('//') else self.most_char['image_url']
                    embed.set_image(url=char_image_url)
        else:
            embed.description = "⚠️ 실험체 데이터가 없습니다."
        
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except:
            # 이미 응답한 경우 followup 사용
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)

    @discord.ui.button(label='통계', style=discord.ButtonStyle.secondary, emoji='📊')
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 상세 통계가 없으면 가져오기
        if not self.detailed_data:
            await interaction.response.defer()
            try:
                self.detailed_data = await get_player_stats_from_dakgg(self.player_stats['nickname'], detailed=True)
            except:
                # 상세 데이터 실패시 기본 통계만 표시
                embed = discord.Embed(
                    title=f"{self.player_stats['nickname']}님의 통계",
                    color=0x57F287
                )
                # 통계 버튼용 캐릭터
                char_key = self.button_characters["stats"]
                embed.set_author(name=characters[char_key]["name"], icon_url=characters[char_key]["image"])
                embed.set_footer(text="이터널 리턴")
                
                embed.add_field(
                    name="평균 TK", 
                    value=f"**{self.stats.get('avg_team_kills', 0):.1f}**", 
                    inline=True
                )
                embed.add_field(
                    name="승률", 
                    value=f"**{self.stats.get('winrate', 0):.1f}%**", 
                    inline=True
                )
                embed.add_field(
                    name="게임 수", 
                    value=f"**{self.stats.get('total_games', 0)}**게임", 
                    inline=True
                )
                
                await interaction.followup.edit_message(embed=embed, view=self)
                return
        
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 통계",
            color=0x57F287
        )
        # 통계 버튼용 캐릭터
        char_key = self.button_characters["stats"]
        embed.set_author(name=characters[char_key]["name"], icon_url=characters[char_key]["image"])
        embed.set_footer(text="이터널 리턴")
        
        # 기본 통계 - 성적에 따른 색상 표시
        winrate = self.stats.get('winrate', 0)
        avg_kills = self.stats.get('avg_kills', 0)
        total_games = self.stats.get('total_games', 0)
        
        embed.add_field(
            name="평균 TK", 
            value=f"{self._get_performance_indicator(avg_kills, 'avg_kills')} **{self.stats.get('avg_team_kills', 0):.1f}**", 
            inline=True
        )
        embed.add_field(
            name="승률", 
            value=f"{self._get_performance_indicator(winrate, 'winrate')} **{winrate:.1f}%**", 
            inline=True
        )
        embed.add_field(
            name="게임 수", 
            value=f"**{total_games}**게임", 
            inline=True
        )
        
        # 상세 통계 (있을 경우)
        if self.detailed_data and self.detailed_data.get('matches_data'):
            matches = self.detailed_data['matches_data'][:20]  # 최근 20경기
            
            # 상세 통계 계산
            total_kills = sum(match.get('playerKill', 0) for match in matches)
            total_damage = sum(match.get('damageToPlayer', 0) for match in matches)
            avg_rank = sum(match.get('gameRank', 18) for match in matches) / len(matches)
            top2_count = sum(1 for match in matches if match.get('gameRank', 18) <= 2)
            top3_count = sum(1 for match in matches if match.get('gameRank', 18) <= 3)
            
            avg_kills_detailed = total_kills/len(matches)
            avg_damage_detailed = total_damage/len(matches)
            top2_rate = top2_count/len(matches)*100
            
            embed.add_field(
                name="평균 킬", 
                value=f"{self._get_performance_indicator(avg_kills_detailed, 'avg_kills')} **{avg_kills_detailed:.1f}**", 
                inline=True
            )
            embed.add_field(
                name="평균 딜량", 
                value=f"{self._get_performance_indicator(avg_damage_detailed, 'avg_damage')} **{avg_damage_detailed:,.0f}**", 
                inline=True
            )
            embed.add_field(
                name="평균 순위", 
                value=f"{self._get_performance_indicator(avg_rank, 'avg_rank')} **{avg_rank:.1f}**등", 
                inline=True
            )
            embed.add_field(
                name="TOP 2", 
                value=f"{self._get_performance_indicator(top2_rate, 'top2_rate')} **{top2_count}**회 ({top2_rate:.1f}%)", 
                inline=True
            )
            top3_rate = top3_count/len(matches)*100
            embed.add_field(
                name="TOP 3", 
                value=f"{self._get_performance_indicator(top3_rate, 'top2_rate')} **{top3_count}**회 ({top3_rate:.1f}%)", 
                inline=True
            )
            embed.add_field(
                name="분석 게임", 
                value=f"최근 **{len(matches)}**게임", 
                inline=True
            )
        
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except:
            # 이미 응답한 경우 followup 사용
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)

# 전적 검색 모달 클래스
class StatsModal(discord.ui.Modal, title='🔍 전적 검색'):
    def __init__(self):
        super().__init__()

    nickname = discord.ui.TextInput(
        label='닉네임',
        placeholder='검색할 플레이어 닉네임을 입력하세요...',
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        # ephemeral=True로 설정하여 사용자에게만 보이도록 합니다.
        await interaction.response.defer(ephemeral=True)
        await stats_search_logic(interaction, str(self.nickname))

# /전적 명령어 (모달 사용)
@bot.tree.command(name="전적", description="데비가 플레이어의 전적을 검색해 드려요!")
async def stats_command(interaction: discord.Interaction):
    """전적 검색 모달을 띄우는 슬래시 커맨드"""
    await interaction.response.send_modal(StatsModal())

# 모달을 띄우는 슬래시 커맨드
async def stats_search_logic(interaction: discord.Interaction, 닉네임: str, 서버지역: str = None):
    """전적 검색 로직 (모달과 일반 명령어에서 공통 사용)"""
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
        
        # 전적 검색 수행 - 닥지지 API 사용 (상세 정보 포함)
        player_stats = await get_player_stats_from_dakgg(닉네임)
        
        if player_stats is None:
            # 닥지지 API 실패시 기존 API 사용
            stats = await get_simple_player_stats_only_tier(닉네임)
            stats_text = stats
            response = f"와! {닉네임}님의 전적을 찾았어! 데비가 빠르게 정리해줄게!"
        else:
            # 닥지지 API 성공 - 상세 정보 포맷팅
            stats = player_stats['stats']
            most_char = player_stats['most_character']
            
            # 모스트 캐릭터 정보
            if most_char:
                char_info = f"**모스트 캐릭터**: {most_char['name']} ({most_char['games']}게임, {most_char['winrate']}% 승률)"
            else:
                char_info = "**모스트 캐릭터**: 데이터 없음"
            
            # 통합된 전적 정보 생성
            stats_info = f"""**현재 랭크**: {player_stats['tier_info']}

**모스트 캐릭터**: {most_char['name'] if most_char else '데이터 없음'}
{f"({most_char['games']}게임, {most_char['winrate']}% 승률)" if most_char else ""}

**통계**
평균 TK: {stats.get('avg_team_kills', 0):.1f}
승률: {stats.get('winrate', 0):.1f}% ({stats.get('wins', 0)}/{stats.get('total_games', 0)})
게임 수: {stats.get('total_games', 0)}게임"""
        
        # View + Button으로 전적 표시
        view = StatsView(player_stats, most_char, stats)
        
        # 기본 전적 정보 표시 (깔끔하게 개선)
        basic_embed = discord.Embed(
            title=f"✨ {닉네임}님의 전적",
            description="아래 버튼을 눌러 자세한 정보를 확인하세요!",
            color=0x5865F2
        )
        basic_embed.set_author(name="데비", icon_url=characters["debi"]["image"])
        basic_embed.set_footer(text="이터널 리턴 • 버튼으로 정보를 탐색하세요")
        
        # 간단한 정보 미리보기
        basic_embed.add_field(
            name="🏆 랭크", 
            value=f"**{player_stats['tier_info'].replace('**', '')}**", 
            inline=False
        )
        
        if most_char:
            basic_embed.add_field(
                name="🎯 모스트 실험체", 
                value=f"**{most_char['name']}** ({most_char['games']}게임)", 
                inline=True
            )
        
        basic_embed.add_field(
            name="📊 승률", 
            value=f"**{stats.get('winrate', 0):.1f}%**", 
            inline=True
        )
        
        # 티어 이미지를 썸네일로 설정
        if player_stats and player_stats.get('tier_image_url'):
            tier_image_raw = player_stats.get('tier_image_url')
            tier_image_url = "https:" + tier_image_raw if tier_image_raw.startswith('//') else tier_image_raw
            basic_embed.set_thumbnail(url=tier_image_url)
        
        await interaction.followup.send(embed=basic_embed, view=view)
        
    except PlayerStatsError as e:
        error_msg = str(e)
        
        try:
            # 에러 메시지 번역
            if "player_not_found" in error_msg:
                response = f"앗! {닉네임} 플레이어를 찾을 수 없어!"
            elif "stats_search_failed" in error_msg:
                response = f"{닉네임}님의 전적을 가져오는 중에 문제가 생겼어!"
            elif "official_api_failed" in error_msg:
                response = "이터널 리턴 서버가 바쁜 것 같아! 잠시 후 다시 시도해줘!"
            else:
                response = "어? 뭔가 문제가 생긴 것 같아!"
                
            error_embed = create_character_embed(
                characters["debi"], 
                "⚠️ 전적 검색 오류",
                response,
                f"/전적 {닉네임}"
            )
            
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            
        except Exception as ai_error:
            print(f"AI 응답 생성 실패 (에러 처리): {ai_error}")
            # AI 응답 실패 시 기본 메시지 사용
            if "player_not_found" in str(e):
                response = f"앗! {닉네임} 플레이어를 찾을 수 없어!"
            else:
                response = "어? 뭔가 문제가 생긴 것 같아!"
                
            error_embed = create_character_embed(
                characters["debi"], 
                "⚠️ 전적 검색 오류",
                response,
                f"/전적 {닉네임}"
            )
            
            await interaction.followup.send(embed=error_embed, ephemeral=True)


# /상세전적 명령어는 통합되어 제거됨 - /전적의 "상세 통계" 버튼으로 대체

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

def create_character_embed(character: Dict[str, Any], title: str, description: str, user_message: str = None, author_image_override: str = None) -> discord.Embed:
    """캐릭터별 임베드 생성"""
    embed = discord.Embed(
        color=character["color"],
        description=description
    )
    
    if user_message:
        embed.add_field(name="메시지", value=f"```{user_message}```", inline=False)
    
    # author 이미지 오버라이드가 있으면 사용, 없으면 기본 캐릭터 이미지
    author_icon = author_image_override if author_image_override else character["image"]
    
    if author_icon:
        embed.set_author(
            name=character["name"],
            icon_url=author_icon
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


# 프리미엄 분석 기능들
async def get_premium_analysis(nickname: str):
    """이터널 리턴 공식 API로 프리미엄 분석 수행"""
    try:
        # 1. 유저 정보 가져오기
        encoded_nickname = urllib.parse.quote(nickname)
        headers = {'x-api-key': ETERNAL_RETURN_API_KEY}
        
        async with aiohttp.ClientSession() as session:
            # 유저 번호 조회
            user_response = await session.get(
                f'{ETERNAL_RETURN_API_BASE}/v1/user/nickname?query={encoded_nickname}',
                headers=headers
            )
            
            if user_response.status != 200:
                return None
                
            user_data = await user_response.json()
            if user_data['code'] != 200:
                return None
                
            user_num = user_data['user']['userNum']
            
            # 시즌 33 랭크 통계 가져오기
            stats_response = await session.get(
                f'{ETERNAL_RETURN_API_BASE}/v2/user/stats/{user_num}/33/3',
                headers=headers
            )
            
            if stats_response.status != 200:
                return None
                
            stats_data = await stats_response.json()
            if stats_data['code'] != 200 or not stats_data['userStats']:
                return None
                
            return {
                'user_num': user_num,
                'stats': stats_data['userStats'][0],
                'nickname': nickname
            }
            
    except Exception as e:
        print(f"프리미엄 분석 오류: {e}")
        return None

@bot.tree.command(name="분석", description="데비가 플레이어의 성능을 심층 분석해드려요!")
async def analysis_command(interaction: discord.Interaction, 닉네임: str):
    """성능 분석 명령어"""
    await interaction.response.defer()
    
    # 채널 체크
    if CHAT_CHANNEL_ID and interaction.channel.id != CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        # 분석 중 메시지
        analysis_embed = discord.Embed(
            title="🔬 성능 분석 중...",
            description=f"**{닉네임}**님의 게임 데이터를 심층 분석하고 있어요!",
            color=characters["debi"]["color"]
        )
        analysis_embed.set_author(
            name=characters["debi"]["name"],
            icon_url=characters["debi"]["image"]
        )
        await interaction.followup.send(embed=analysis_embed)
        
        # 프리미엄 분석 수행
        analysis_data = await get_premium_analysis(닉네임)
        
        if not analysis_data:
            response = f"앗! {닉네임} 플레이어의 분석 데이터를 가져올 수 없어!"
            error_embed = create_character_embed(
                characters["debi"], 
                "⚠️ 분석 실패",
                response,
                f"/분석 {닉네임}"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return
        
        stats = analysis_data['stats']
        
        # 성능 분석 결과 생성
        analysis_text = f"""🏆 **랭크 정보**
📊 **현재 MMR**: {stats['mmr']}점
🏅 **서버 순위**: {stats['rank']:,}위 / {stats['rankSize']:,}명 (상위 {stats['rankPercent']:.1%})

📈 **게임 성과 분석**
🎮 **총 게임**: {stats['totalGames']}게임
🏆 **승리**: {stats['totalWins']}회 ({stats['totalWins']/stats['totalGames']*100:.1f}%)
💀 **평균 킬**: {stats['averageKills']:.1f}킬
🤝 **평균 어시**: {stats['averageAssistants']:.1f}회
📊 **평균 순위**: {stats['averageRank']:.1f}등

🎯 **생존율 분석**
🥇 **1등**: {stats['top1']:.1%}
🥈 **TOP 2**: {stats['top2']:.1%}
🥉 **TOP 3**: {stats['top3']:.1%}
🏅 **TOP 5**: {stats['top5']:.1%}

🎭 **캐릭터 분석**"""

        # 캐릭터별 분석
        if 'characterStats' in stats and stats['characterStats']:
            char_stats = sorted(stats['characterStats'], key=lambda x: x['totalGames'], reverse=True)
            for i, char in enumerate(char_stats[:3]):
                char_name = f"캐릭터 {char['characterCode']}"  # 실제 캐릭터 이름 매핑 필요
                analysis_text += f"""
**{i+1}. {char_name}** ({char['totalGames']}게임)
   - 승률: {char['wins']/char['totalGames']*100:.1f}% ({char['wins']}승)
   - TOP3: {char['top3']}회
   - 평균 순위: {char['averageRank']:.1f}등
   - 최고 킬: {char['maxKillings']}킬"""

        response = f"와! {닉네임}님의 심층 분석이 끝났어! 정말 상세한 데이터야!"
        
        # 임베드 생성 및 전송
        embed = create_character_embed(
            characters["debi"], 
            f"🔬 {닉네임}님의 성능 분석",
            response + "\n\n" + analysis_text,
            f"/분석 {닉네임}"
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"분석 명령어 오류: {e}")
        response = f"앗! {닉네임}님의 분석 중에 문제가 생겼어!"
        error_embed = create_character_embed(
            characters["debi"], 
            "⚠️ 분석 오류",
            response,
            f"/분석 {닉네임}"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)

@bot.tree.command(name="추천", description="데비가 AI 분석으로 개선점을 추천해드려요!")
async def recommend_command(interaction: discord.Interaction, 닉네임: str):
    """개선 추천 명령어"""
    await interaction.response.defer()
    
    # 채널 체크
    if CHAT_CHANNEL_ID and interaction.channel.id != CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        # 분석 중 메시지
        recommend_embed = discord.Embed(
            title="🎯 AI 추천 분석 중...",
            description=f"**{닉네임}**님만을 위한 맞춤 개선 방안을 찾고 있어요!",
            color=characters["debi"]["color"]
        )
        recommend_embed.set_author(
            name=characters["debi"]["name"],
            icon_url=characters["debi"]["image"]
        )
        await interaction.followup.send(embed=recommend_embed)
        
        # 분석 데이터 가져오기
        analysis_data = await get_premium_analysis(닉네임)
        
        if not analysis_data:
            response = f"앗! {닉네임} 플레이어의 데이터를 가져올 수 없어!"
            error_embed = create_character_embed(
                characters["debi"], 
                "⚠️ 추천 실패",
                response,
                f"/추천 {닉네임}"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return
        
        stats = analysis_data['stats']
        
        # AI 스타일 추천 생성
        recommendations = []
        
        # 승률 기반 추천
        win_rate = stats['totalWins'] / stats['totalGames'] * 100
        if win_rate < 10:
            recommendations.append("🎯 **생존 우선 전략**: 승률이 낮으니 킬보다는 생존에 집중해보세요!")
        elif win_rate > 20:
            recommendations.append("🏆 **공격적 플레이**: 높은 승률이니 더 공격적으로 플레이해도 좋을 것 같아요!")
        
        # 평균 순위 기반 추천
        avg_rank = stats['averageRank']
        if avg_rank > 6:
            recommendations.append("📈 **초반 생존력 강화**: 평균 순위가 낮으니 초반 파밍과 안전한 포지셔닝을 연습해보세요!")
        elif avg_rank < 4:
            recommendations.append("⚔️ **마무리 능력 향상**: 상위권 진입은 잘하시는데, 마지막 1등 경쟁력을 키워보세요!")
        
        # 킬 수 기반 추천
        avg_kills = stats['averageKills']
        if avg_kills < 2:
            recommendations.append("💪 **전투력 강화**: 평균 킬이 낮으니 전투 연습을 더 해보세요!")
        elif avg_kills > 4:
            recommendations.append("🎭 **균형잡힌 플레이**: 킬은 잘 따시는데, 생존과의 밸런스를 맞춰보세요!")
        
        # 캐릭터 추천
        if 'characterStats' in stats and stats['characterStats']:
            char_stats = sorted(stats['characterStats'], key=lambda x: x['wins']/x['totalGames'] if x['totalGames'] > 0 else 0, reverse=True)
            if char_stats:
                best_char = char_stats[0]
                recommendations.append(f"🌟 **추천 캐릭터**: 캐릭터 {best_char['characterCode']}로 {best_char['wins']}/{best_char['totalGames']}승! 더 연습해보세요!")
        
        # TOP 순위 분석
        if stats['top3'] < 0.3:
            recommendations.append("🥉 **중후반 전략**: TOP3 진입률이 낮아요. 중후반 판단력을 키워보세요!")
        
        recommend_text = "🔮 **맞춤 개선 추천**\n\n" + "\n\n".join(recommendations)
        
        # 일반적인 팁 추가
        recommend_text += f"""

💡 **일반적인 팁**
• 현재 MMR: {stats['mmr']}점 (상위 {stats['rankPercent']:.1%})
• 목표: 다음 등급까지 약 {max(0, (stats['mmr']//100 + 1)*100 - stats['mmr'])}점 필요
• 추천 연습: 가장 잘하는 캐릭터로 꾸준히 플레이하기
• 하루 목표: 2-3게임씩 꾸준히 플레이"""

        response = f"와! {닉네임}님을 위한 맞춤형 추천이 완성됐어! 따라해보면 실력이 쑥쑥 늘 거야!"
        
        # 임베드 생성 및 전송
        embed = create_character_embed(
            characters["debi"], 
            f"🎯 {닉네임}님의 AI 추천",
            response + "\n\n" + recommend_text,
            f"/추천 {닉네임}"
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"추천 명령어 오류: {e}")
        response = f"앗! {닉네임}님의 추천 분석 중에 문제가 생겼어!"
        error_embed = create_character_embed(
            characters["debi"], 
            "⚠️ 추천 오류",
            response,
            f"/추천 {닉네임}"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)

@bot.tree.command(name="예측", description="데비가 티어 변동을 예측해드려요!")
async def predict_command(interaction: discord.Interaction, 닉네임: str):
    """티어 예측 명령어"""
    await interaction.response.defer()
    
    # 채널 체크
    if CHAT_CHANNEL_ID and interaction.channel.id != CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        # 예측 중 메시지
        predict_embed = discord.Embed(
            title="🔮 티어 예측 중...",
            description=f"**{닉네임}**님의 미래 랭크를 예측하고 있어요!",
            color=characters["debi"]["color"]
        )
        predict_embed.set_author(
            name=characters["debi"]["name"],
            icon_url=characters["debi"]["image"]
        )
        await interaction.followup.send(embed=predict_embed)
        
        # 현재 시즌과 전 시즌 데이터 가져오기
        analysis_data = await get_premium_analysis(닉네임)
        
        if not analysis_data:
            response = f"앗! {닉네임} 플레이어의 데이터를 가져올 수 없어!"
            error_embed = create_character_embed(
                characters["debi"], 
                "⚠️ 예측 실패",
                response,
                f"/예측 {닉네임}"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return
        
        stats = analysis_data['stats']
        user_num = analysis_data['user_num']
        
        # 전 시즌 데이터도 가져오기 (시즌 31)
        prev_season_stats = None
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'x-api-key': ETERNAL_RETURN_API_KEY}
                prev_response = await session.get(
                    f'{ETERNAL_RETURN_API_BASE}/v2/user/stats/{user_num}/31/3',
                    headers=headers
                )
                if prev_response.status == 200:
                    prev_data = await prev_response.json()
                    if prev_data['code'] == 200 and prev_data['userStats']:
                        prev_season_stats = prev_data['userStats'][0]
        except Exception as e:
            print(f"전 시즌 데이터 조회 오류: {e}")
        current_mmr = stats['mmr']
        win_rate = stats['totalWins'] / stats['totalGames'] * 100
        
        # 정확한 티어 시스템 (이터널 리턴 공식)
        mmr_tiers = {
            6000: "에테르 1",
            5800: "에테르 2", 
            5600: "에테르 3",
            5400: "미스릴 1",
            5200: "미스릴 2",
            5000: "미스릴 3",
            4800: "플래티넘 1",
            4600: "플래티넘 2", 
            4400: "플래티넘 3",
            4200: "골드 1",
            4000: "골드 2",
            3800: "골드 3",
            3600: "실버 1",
            3400: "실버 2",
            3200: "실버 3",
            3000: "브론즈 1",
            2800: "브론즈 2",
            2600: "브론즈 3",
            2000: "아이언"
        }
        
        # 현재 티어 찾기
        current_tier = "언랭크"
        for mmr_threshold, tier_name in mmr_tiers.items():
            if current_mmr >= mmr_threshold:
                current_tier = tier_name
                break
        
        # 시즌간 트렌드 분석 및 예측
        season_trend = ""
        if prev_season_stats:
            prev_mmr = prev_season_stats['mmr']
            prev_win_rate = prev_season_stats['totalWins'] / prev_season_stats['totalGames'] * 100
            mmr_change = current_mmr - prev_mmr
            win_rate_change = win_rate - prev_win_rate
            
            if mmr_change > 0:
                season_trend = f"📈 시즌간 상승 ({mmr_change:+.0f}점)"
            else:
                season_trend = f"📉 시즌간 하락 ({mmr_change:+.0f}점)"
        
        # 종합적인 MMR 변동 예측
        prediction_factors = []
        base_prediction = 0
        
        # 현재 승률 기반
        if win_rate > 15:
            prediction_factors.append("높은 승률 (+60점)")
            base_prediction += 60
        elif win_rate > 8:
            prediction_factors.append("보통 승률 (±10점)")
            base_prediction += 10
        else:
            prediction_factors.append("낮은 승률 (-40점)")
            base_prediction -= 40
            
        # 전 시즌 대비 트렌드
        if prev_season_stats:
            if win_rate > prev_season_stats['totalWins'] / prev_season_stats['totalGames'] * 100:
                prediction_factors.append("승률 향상 (+20점)")
                base_prediction += 20
            else:
                prediction_factors.append("승률 하락 (-20점)")
                base_prediction -= 20
        
        # 게임 수 기반 안정성
        if stats['totalGames'] > 100:
            prediction_factors.append("충분한 게임 수 (안정)")
        else:
            prediction_factors.append("적은 게임 수 (변동성 높음)")
            base_prediction = int(base_prediction * 1.5)  # 변동성 증가
        
        # 최종 예측
        if base_prediction > 30:
            mmr_trend = "상승"
            predicted_change = f"+{base_prediction-20}~+{base_prediction+20}"
            trend_emoji = "📈"
        elif base_prediction > -30:
            mmr_trend = "유지"
            predicted_change = f"{base_prediction-15}~+{abs(base_prediction)+15}"
            trend_emoji = "📊"
        else:
            mmr_trend = "하락"
            predicted_change = f"{base_prediction-20}~{base_prediction+20}"
            trend_emoji = "📉"
        
        # 목표 달성 예측
        next_tier_mmr = None
        for mmr_threshold in sorted(mmr_tiers.keys(), reverse=True):
            if mmr_threshold > current_mmr:
                next_tier_mmr = mmr_threshold
                next_tier_name = mmr_tiers[mmr_threshold]
        
        predict_text = f"""🔮 **고급 티어 예측 분석**

📊 **현재 상태**
• 현재 MMR: {current_mmr}점
• 현재 티어: {current_tier}
• 승률: {win_rate:.1f}% ({stats['totalWins']}/{stats['totalGames']})
• 서버 순위: {stats['rank']:,}위 (상위 {stats['rankPercent']:.1%})

{season_trend if season_trend else "📊 첫 시즌 데이터"}

{trend_emoji} **AI 예측 결과**
• MMR 트렌드: {mmr_trend} 경향
• 예상 변동폭: {predicted_change}점
• 10게임 후 예상 MMR: {current_mmr + base_prediction}점

🔍 **예측 근거**
{chr(10).join(f"• {factor}" for factor in prediction_factors)}"""

        if next_tier_mmr:
            games_needed = max(1, int((next_tier_mmr - current_mmr) / (20 if win_rate > 15 else 5)))
            predict_text += f"""

🎯 **목표 달성 예측**
• 다음 티어: {next_tier_name}
• 필요 MMR: {next_tier_mmr - current_mmr}점
• 예상 게임 수: {games_needed}게임 (현재 승률 기준)
• 달성 확률: {'높음' if win_rate > 15 else '보통' if win_rate > 8 else '낮음'}"""

        # 전 시즌 비교 정보 추가
        if prev_season_stats:
            prev_tier = "언랭크"
            for mmr_threshold, tier_name in mmr_tiers.items():
                if prev_season_stats['mmr'] >= mmr_threshold:
                    prev_tier = tier_name
                    break
                    
            predict_text += f"""

📈 **시즌간 비교 분석**
• 시즌 31: {prev_tier} ({prev_season_stats['mmr']}점, {prev_win_rate:.1f}% 승률)
• 시즌 33: {current_tier} ({current_mmr}점, {win_rate:.1f}% 승률)
• 성장률: MMR {mmr_change:+.0f}점, 승률 {win_rate_change:+.1f}%
• 트렌드: {'꾸준한 성장 중!' if mmr_change > 0 else '실력 조정 중'}"""

        predict_text += f"""

💡 **맞춤형 향상 가이드**
• 승률 10% 향상시: 약 {int((next_tier_mmr - current_mmr) / 30) if next_tier_mmr else 20}게임으로 단축 가능
• 추천 전략: {'공격적 플레이로 킬 늘리기' if win_rate > 10 else '생존 위주로 안정성 확보'}
• 일일 목표: 2-3게임 (주 14게임)
• 예상 도달 시간: {f'{int((next_tier_mmr - current_mmr) / max(base_prediction, 10))}주' if next_tier_mmr and base_prediction > 0 else '현재 폼 유지 필요'}"""

        response = f"와! {닉네임}님의 미래가 보여! 이 예측대로라면 정말 기대돼!"
        
        # 임베드 생성 및 전송
        embed = create_character_embed(
            characters["debi"], 
            f"🔮 {닉네임}님의 티어 예측",
            response + "\n\n" + predict_text,
            f"/예측 {닉네임}"
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"예측 명령어 오류: {e}")
        response = f"앗! {닉네임}님의 예측 분석 중에 문제가 생겼어!"
        error_embed = create_character_embed(
            characters["debi"], 
            "⚠️ 예측 오류",
            response,
            f"/예측 {닉네임}"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)

if __name__ == "__main__":
    import sys
    
    # API 테스트 모드
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("DAKGG API 구조 테스트 모드")
        asyncio.run(test_dakgg_api_structure())
        exit(0)
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("DISCORD_TOKEN이 설정되지 않았습니다!")
        exit(1)
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"봇 실행 중 오류: {e}")