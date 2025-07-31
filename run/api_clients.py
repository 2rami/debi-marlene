import asyncio
import aiohttp
import urllib.parse
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from run.config import ETERNAL_RETURN_API_BASE, ETERNAL_RETURN_API_KEY, DAKGG_API_BASE


def load_config_data():
    """data_config.json과 season_mapping.json 파일들을 로드"""
    global _config_data
    if _config_data is None:
        try:
            # 티어명, API 헤더 등 기본 설정 로드
            config_path = os.path.join(os.path.dirname(__file__), 'data_config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                _config_data = json.load(f)
        except:
            _config_data = {"tier_names": {}, "season_keys": {"current": 33}}
        
        try:
            # 시즌 매핑 정보 로드
            season_path = os.path.join(os.path.dirname(__file__), '..', 'season_mapping.json')
            with open(season_path, 'r', encoding='utf-8') as f:
                season_data = json.load(f)
                _config_data['season_mapping'] = season_data
        except:
            _config_data['season_mapping'] = {"season_ids": {"33": {"api_param": "SEASON_17", "name": "시즌 8"}}}
    return _config_data

def get_season_name(season_id: int) -> str:
    """시즌 ID를 한글 시즌명으로 변환 (예: 33 -> "시즌 8")"""
    config = load_config_data()
    season_info = config['season_mapping']['season_ids'].get(str(season_id))
    return season_info['name'] if season_info else f"Season {season_id}"

def get_season_api_param(season_id: int) -> str:
    """시즌 ID를 API 파라미터로 변환 (예: 33 -> "SEASON_17")"""
    config = load_config_data()
    season_info = config['season_mapping']['season_ids'].get(str(season_id))
    return season_info['api_param'] if season_info else "SEASON_17"

def get_tier_name(tier_id: int) -> str:
    """티어 ID를 티어명으로 변환 (예: 4 -> "골드")"""
    config = load_config_data()
    return config['tier_names'].get(str(tier_id), "언랭크")

def get_tier_image_url(tier_id: int) -> str:
    """티어 ID에 해당하는 티어 이미지 URL 반환"""
    config = load_config_data()
    return config['tier_images'].get(str(tier_id), config['tier_images']['0'])

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

    
    # URL 인코딩
    encoded_nickname = urllib.parse.quote(nickname)
    profile_url = f'{DAKGG_API_BASE}/players/{encoded_nickname}/profile'
    
    # 프로필, 티어, 캐릭터 데이터를 동시에 요청
    tasks = [
        fetch_api(profile_url),
        fetch_api(f'{DAKGG_API_BASE}/data/tiers?hl=ko'),
        fetch_api(f'{DAKGG_API_BASE}/data/characters?hl=ko')
    ]
    
    profile_data, tier_data, char_data = await asyncio.gather(*tasks)
    
    if not profile_data or not profile_data.get('playerSeasons'):
        return None
    

def process_player_data(nickname: str, profile_data: Dict, tier_data: Dict, char_data: Dict) -> Dict:
    """API에서 받은 원본 데이터를 봇에서 사용할 형태로 가공"""
    current_season = profile_data['playerSeasons'][0]  # 첫 번째가 현재 시즌
    
    # 티어 정보 추출
    mmr = current_season.get('mmr', 0)
    tier_id = current_season.get('tierId', 0)
    tier_grade = current_season.get('tierGradeId', 1)
    tier_mmr = current_season.get('tierMmr', 0)
    
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
        # 현재 시즌(33)의 랭크 모드(0) 데이터만 처리
        if overview.get('seasonId') == 33 and overview.get('matchingModeId') == 0:
            # 기본 통계
            result['stats'] = {
                'total_games': overview.get('play', 0),
                'wins': overview.get('win', 0),
                'winrate': round((overview.get('win', 0) / max(overview.get('play', 1), 1)) * 100, 1),
                'avg_rank': round(overview.get('place', 0) / max(overview.get('play', 1), 1), 1),
                'avg_kills': round(overview.get('playerKill', 0) / max(overview.get('play', 1), 1), 1)
            }
            
            # 캐릭터별 통계 처리
            char_map = {char['id']: char['name'] for char in char_data.get('characters', [])} if char_data else {}
            char_stats = []
            
            for char_stat in overview.get('characterStats', []):
                if char_stat.get('play', 0) > 0:  # 플레이한 캐릭터만
                    char_id = char_stat.get('key')
                    char_name = char_map.get(char_id, f'Unknown_{char_id}')
                    games = char_stat.get('play', 1)
                    wins = char_stat.get('win', 0)
                    
                    char_stats.append({
                        'name': char_name,
                        'games': games,
                        'wins': wins,
                        'winrate': round((wins / games) * 100, 1),
                        'avg_rank': round(char_stat.get('place', 0) / games, 1)
                    })
            
            # 게임 수 기준으로 정렬하여 모스트 캐릭터 결정
            result['most_characters'] = sorted(char_stats, key=lambda x: x['games'], reverse=True)[:10]
            break
    
    return result

async def get_season_data(nickname: str, season_id: int) -> Optional[Dict]:
    """특정 시즌의 티어 데이터만 조회"""
    encoded_nickname = urllib.parse.quote(nickname)
    season_param = get_season_api_param(season_id)
    url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season={season_param}"
    
    data = await fetch_api(url)
    if not data:
        return None
    
    # 해당 시즌 데이터 찾기
    for season in data.get('playerSeasons', []):
        if season.get('seasonId') == season_id:
            tier_id = season.get('tierId', 0)
            tier_grade = season.get('tierGradeId', 1)
            mmr = season.get('mmr', 0)
            tier_mmr = season.get('tierMmr', 0)
            
            tier_name = get_tier_name(tier_id)
            tier_info = f"{tier_name} {tier_grade} {tier_mmr} RP (MMR {mmr})" if tier_id > 0 else "언랭크"
            
            return {
                'tier_info': tier_info,
                'tier_image_url': get_tier_image_url(tier_id)
            }
    
    return None

# === 하위 호환성을 위한 함수들 ===
# 기존 코드에서 사용하던 함수명들을 유지

async def get_player_stats_from_dakgg(nickname: str, detailed: bool = False):
    """기존 함수명 호환용"""
    return await get_player_basic_data(nickname)

async def get_season_tier_from_dakgg(nickname: str, season_id: int):
    """특정 시즌의 티어 정보만 반환"""
    data = await get_season_data(nickname, season_id)
    return data['tier_info'] if data else None

async def get_season_tier_with_image(nickname: str, season_id: int):
    """특정 시즌의 티어 정보와 이미지 URL을 튜플로 반환"""
    data = await get_season_data(nickname, season_id)
    return (data['tier_info'], data['tier_image_url']) if data else (None, None)

async def get_player_season_list_simple(nickname: str):
    """플레이어의 시즌 목록만 간단히 조회"""
    encoded_nickname = urllib.parse.quote(nickname)
    url = f"https://er.dakgg.io/api/v1/players/{encoded_nickname}/profile?season=SEASON_17"
    data = await fetch_api(url)
    
    if data:
        return {
            'playerSeasons': data.get('playerSeasons', []),
            'playerSeasonOverviews': data.get('playerSeasonOverviews', [])
        }
    return None

async def get_simple_player_stats(nickname: str) -> Dict[str, Any]:
    """간단한 전적 정보를 success/error 형태로 반환"""
    data = await get_player_basic_data(nickname)
    if data:
        return {
            'success': True,
            'nickname': nickname,
            'tier_info': data.get('tier_info'),
            'mmr': data.get('mmr', 0),
            'raw_data': data
        }
    return {'success': False, 'message': '플레이어를 찾을 수 없습니다.'}