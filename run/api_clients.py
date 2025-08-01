import asyncio
import aiohttp
import urllib.parse
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from run.config import ETERNAL_RETURN_API_BASE, ETERNAL_RETURN_API_KEY, DAKGG_API_BASE

# 전역 설정 데이터 캐시
_config_data = None

def load_config_data():
    """combined_config.json 파일을 로드"""
    global _config_data
    if _config_data is None:
        try:
            # 합쳐진 설정 파일 로드
            config_path = os.path.join(os.path.dirname(__file__), 'combined_config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                _config_data = json.load(f)
        except:
            # 기본값 설정
            _config_data = {
                "tier_names": {"0": "언랭크"},
                "tier_images": {"0": "https://cdn.dak.gg/assets/er/images/rank/full/0.png"},
                "season_keys": {"current": 33},
                "api_headers": {
                    "Accept": "application/json, text/plain, */*",
                    "Origin": "https://dak.gg",
                    "Referer": "https://dak.gg/",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
                "season_ids": {"33": {"api_param": "SEASON_17", "name": "시즌 8"}}
            }
    return _config_data

# === 데이터 변환 유틸리티 함수들 ===

def get_season_name(season_id: int) -> str:
    """시즌 ID를 한글 시즌명으로 변환 (예: 33 -> "시즌 8")"""
    config = load_config_data()
    season_info = config['season_ids'].get(str(season_id))
    return season_info['name'] if season_info else f"Season {season_id}"

def get_season_api_param(season_id: int) -> str:
    """시즌 ID를 API 파라미터로 변환 (예: 33 -> "SEASON_17")"""
    config = load_config_data()
    season_info = config['season_ids'].get(str(season_id))
    return season_info['api_param'] if season_info else "SEASON_17"

def get_tier_name(tier_id: int) -> str:
    """티어 ID를 티어명으로 변환 (예: 4 -> "골드")"""
    config = load_config_data()
    return config['tier_names'].get(str(tier_id), "언랭크")

def get_tier_image_url(tier_id: int) -> str:
    """티어 ID에 해당하는 티어 이미지 URL 반환"""
    config = load_config_data()
    return config['tier_images'].get(str(tier_id), config['tier_images']['0'])

# === API 호출 관련 함수들 ===

async def fetch_api(url: str, headers: Dict = None) -> Optional[Dict]:
    """API 호출을 위한 공통 함수"""
    if headers is None:
        config = load_config_data()
        headers = config['api_headers']
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                return await response.json() if response.status == 200 else None
    except:
        return None

# === 플레이어 데이터 조회 함수들 ===

async def get_player_basic_data(nickname: str) -> Optional[Dict]:
    """플레이어의 기본 전적 정보를 조회 (현재 시즌)"""
    return await get_player_season_data(nickname, 33)  # 시즌 8 = 33

async def get_season_data(nickname: str, season_id: int) -> Optional[Dict]:
    """특정 시즌의 티어 데이터만 조회"""
    full_data = await get_player_season_data(nickname, season_id)
    if full_data:
        return {
            'tier_info': full_data['tier_info'],
            'tier_image_url': full_data['tier_image_url']
        }
    return None

async def get_player_played_seasons(nickname: str) -> list:
    """플레이어가 플레이한 시즌 목록을 반환"""
    encoded_nickname = urllib.parse.quote(nickname)
    # 현재 시즌으로 요청해서 전체 시즌 목록 가져오기
    url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season=SEASON_17"
    
    data = await fetch_api(url)
    if not data:
        return []
    
    played_seasons = []
    for season in data.get('playerSeasons', []):
        season_id = season.get('seasonId')
        if season_id:
            season_name = get_season_name(season_id)
            played_seasons.append({
                'id': season_id,
                'name': season_name,
                'is_current': season_id == 33  # 시즌 8이 현재 시즌
            })
    
    # 시즌 ID 내림차순으로 정렬 (최신 시즌부터)
    played_seasons.sort(key=lambda x: x['id'], reverse=True)
    return played_seasons

# === 메인 데이터 처리 함수들 ===

async def get_player_season_data(nickname: str, season_id: int) -> Optional[Dict]:
    """특정 시즌의 전체 플레이어 데이터 조회 (티어 + 통계 + 실험체)"""
    encoded_nickname = urllib.parse.quote(nickname)
    season_param = get_season_api_param(season_id)
    profile_url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season={season_param}"
    
    # 프로필, 티어, 캐릭터 데이터를 동시에 요청
    tasks = [
        fetch_api(profile_url),
        fetch_api(f'{DAKGG_API_BASE}/data/tiers?hl=ko'),
        fetch_api(f'{DAKGG_API_BASE}/data/characters?hl=ko')
    ]
    
    profile_data, tier_data, char_data = await asyncio.gather(*tasks)
    
    if not profile_data or not profile_data.get('playerSeasons'):
        return None
    
    # 데이터 가공해서 반환 (시즌 ID도 포함)
    result = process_player_season_data(nickname, profile_data, tier_data, char_data, season_id)
    result['season_id'] = season_id
    result['season_name'] = get_season_name(season_id)
    return result

def process_player_season_data(nickname: str, profile_data: Dict, tier_data: Dict, char_data: Dict, target_season_id: int) -> Dict:
    """특정 시즌의 API 데이터를 봇에서 사용할 형태로 가공"""
    # 해당 시즌 찾기
    target_season = None
    for season in profile_data.get('playerSeasons', []):
        if season.get('seasonId') == target_season_id:
            target_season = season
            break
    
    if not target_season:
        return {
            'nickname': nickname,
            'tier_info': '언랭크',
            'tier_image_url': get_tier_image_url(0),
            'mmr': 0,
            'lp': 0,
            'stats': {},
            'most_characters': []
        }
    
    # 티어 정보 추출
    mmr = target_season.get('mmr', 0)
    tier_id = target_season.get('tierId', 0)
    tier_grade = target_season.get('tierGradeId', 1)
    tier_mmr = target_season.get('tierMmr', 0)
    
    # 티어명 생성
    tier_name = get_tier_name(tier_id)
    tier_info = f"{tier_name} {tier_grade} {tier_mmr} RP (MMR {mmr})" if tier_id > 0 else f"{tier_name} (MMR {mmr})"
    
    result = {
        'nickname': nickname,
        'tier_info': tier_info,
        'tier_image_url': get_tier_image_url(tier_id),
        'mmr': mmr,
        'lp': tier_mmr,
        'stats': {},
        'most_characters': []
    }
    
    # 시즌 통계 및 모스트 캐릭터 추출
    season_overviews = profile_data.get('playerSeasonOverviews', [])
    for overview in season_overviews:
        # 해당 시즌의 랭크 모드(0) 데이터만 처리
        if overview.get('seasonId') == target_season_id and overview.get('matchingModeId') == 0:
            # 기본 통계
            result['stats'] = {
                'total_games': overview.get('play', 0),
                'wins': overview.get('win', 0),
                'winrate': round((overview.get('win', 0) / max(overview.get('play', 1), 1)) * 100, 1),
                'avg_rank': round(overview.get('place', 0) / max(overview.get('play', 1), 1), 1),
                'avg_kills': round(overview.get('playerKill', 0) / max(overview.get('play', 1), 1), 1)
            }
            
            # 캐릭터별 통계 처리 (이미지 정보 포함)
            char_map = {}
            char_image_map = {}
            config = load_config_data()
            char_image_pattern = config.get('character_image_url', "https://cdn.dak.gg/assets/er/images/character/full/{character_id}.png")
            
            if char_data:
                for char in char_data.get('characters', []):
                    char_id = char['id']
                    char_map[char_id] = char['name']
                    # 캐릭터 이미지 URL 저장 (API에서 제공하거나 ID 패턴 사용)
                    char_image_map[char_id] = char.get('image', char_image_pattern.format(character_id=char_id))
            
            char_stats = []
            
            for char_stat in overview.get('characterStats', []):
                if char_stat.get('play', 0) > 0:  # 플레이한 캐릭터만
                    char_id = char_stat.get('key')
                    char_name = char_map.get(char_id, f'Unknown_{char_id}')
                    char_image = char_image_map.get(char_id, "")
                    games = char_stat.get('play', 1)
                    wins = char_stat.get('win', 0)
                    
                    char_stats.append({
                        'name': char_name,
                        'image_url': char_image,
                        'games': games,
                        'wins': wins,
                        'winrate': round((wins / games) * 100, 1),
                        'avg_rank': round(char_stat.get('place', 0) / games, 1)
                    })
            
            # 게임 수 기준으로 정렬하여 모스트 캐릭터 결정
            result['most_characters'] = sorted(char_stats, key=lambda x: x['games'], reverse=True)[:10]
            break
    
    return result

