import os
import asyncio
import random
import aiofiles
from datetime import datetime
import re
from typing import List, Optional, Dict, Any
import urllib.parse

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
        "image": "./assets/debi.png",
        "color": 0x0000FF,  # 진한 파랑
        "ai_prompt": """너는 이터널리턴의 데비(언니, 파란색)야. 쾌활하고 활발한 성격으로 반말로 대화해. 
        
인게임 대사 스타일:
- "각오 단단히 해!", "우린 붙어있을 때 최강이니까!"
- "내가 할게!", "Stick with me! I got this."
- "엄청 수상한 놈이 오는데!", "Let's go somewhere cool!"

성격: 천진난만하고 적극적, 자신감 넘치고 상황을 주도하려 함. 밝고 에너지 넘치는 톤으로 대화하고 감탄사를 자주 써."""
    },
    "marlene": {
        "name": "마를렌",
        "image": "./assets/marlen.png",
        "color": 0xDC143C,  # 진한 빨강
        "ai_prompt": """너는 이터널리턴의 마를렌(동생, 빨간색)이야. 차갑고 도도한 성격으로 반말로 대화해.

인게임 대사 스타일:
- "Like hell you do." (데비 견제할 때)
- "Oh! A very suspicious guy is coming this way!"
- "Hope it's not too cold.", "I already let you hear mine, remember?"

성격: 냉소적이고 현실적, 쿨하고 건조한 톤. 언니를 견제하면서도 케어하는 츤데레 스타일. 신중하고 경계심 있는 표현을 써."""
    }
}

# API 클라이언트 초기화
anthropic_client: Optional[AsyncAnthropic] = None
youtube = None
ETERNAL_RETURN_CHANNEL_ID = 'UCaktoGSdjMnfQFv5BSyYrvA'
last_checked_video_id = None

class PlayerStatsError(Exception):
    """플레이어 전적 조회 관련 예외"""
    pass


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

async def fetch_detailed_player_stats(nickname: str) -> Dict[str, Any]:
    """
    dak.gg에서 플레이어의 상세 전적 정보를 가져오는 함수
    
    Args:
        nickname: 플레이어 닉네임
        
    Returns:
        Dict containing:
        - name: 플레이어 이름
        - level: 레벨 정보
        - profile: 프로필 정보 (티어, LP 등)
        - rank_info: 랭크 정보
        - recent_games: 최근 5게임 정보
        - url: dak.gg 프로필 URL
    """
    try:
        # URL 인코딩
        encoded_nickname = urllib.parse.quote(nickname)
        url = f"https://dak.gg/er/players/{encoded_nickname}"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 404:
                    raise PlayerStatsError("player_not_found")
                elif response.status != 200:
                    raise PlayerStatsError(f"request_failed_{response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 플레이어 정보 추출
                player_data = {
                    'name': nickname,
                    'level': None,
                    'profile': {},
                    'rank_info': {},
                    'recent_games': [],
                    'url': url
                }
                
                # 1. 기본 플레이어 정보 (이름, 레벨)
                await _extract_basic_info(soup, player_data)
                
                # 2. 프로필 정보 (티어, LP, 승률 등)
                await _extract_profile_info(soup, player_data)
                
                # 3. 랭크 정보
                await _extract_rank_info(soup, player_data)
                
                # 4. 최근 게임 정보
                await _extract_recent_games(soup, player_data)
                
                return player_data
                
    except PlayerStatsError:
        raise
    except Exception as e:
        print(f"플레이어 전적 조회 중 예외 발생: {e}")
        raise PlayerStatsError(f"fetch_failed: {str(e)}")


async def _extract_basic_info(soup: BeautifulSoup, player_data: Dict[str, Any]):
    """기본 플레이어 정보 추출 (이름, 레벨)"""
    
    # 플레이어 이름과 레벨 정보
    name_selectors = [
        'h1.css-1v8q5mj',  # dak.gg 메인 플레이어 이름
        'h1[class*="player"]',
        '.player-name h1',
        'h1',
        '.css-389hsa h3',
        '.content h3',
        '[class*="nickname"]' # 일반적인 닉네임 클래스
    ]
    
    for selector in name_selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            if text and len(text) > 0:
                # 레벨 정보가 포함된 경우 분리
                if 'Lv.' in text or 'Level' in text:
                    level_match = re.search(r'Lv\.?\s*(\d+)', text)
                    if level_match:
                        player_data['level'] = f"Lv.{level_match.group(1)}"
                        player_name = re.sub(r'Lv\.?\s*\d+', '', text).strip()
                        if player_name:
                            player_data['name'] = player_name
                else:
                    player_data['name'] = text
                break
    
    # 별도 레벨 정보 찾기
    if not player_data.get('level'):
        level_selectors = [
            '.css-1v8q5mj + div',  # 이름 다음 div
            '.player-level',
            '.level',
            '[class*="level"]' # 일반적인 레벨 클래스
        ]
        
        for selector in level_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                level_match = re.search(r'(?:Lv\.?\s*)?(\d+)', text)
                if level_match and ('lv' in text.lower() or 'level' in text.lower()):
                    player_data['level'] = f"Lv.{level_match.group(1)}"
                    break


async def _extract_profile_info(soup: BeautifulSoup, player_data: Dict[str, Any]):
    """프로필 정보 추출 (티어, LP, 승률 등)"""
    
    # 티어 정보
    tier_selectors = [
        '.css-1qjr4z5',  # dak.gg 티어 클래스
        '.tier-name',
        '.rank-tier',
        '[class*="tier"]',
        '[class*="rank"]',
        '[class*="tier-info"]' # 일반적인 티어 정보 클래스
    ]
    
    for selector in tier_selectors:
        elem = soup.select_one(selector)
        if elem:
            tier_text = elem.get_text(strip=True)
            if tier_text and any(rank in tier_text.lower() for rank in ['iron', 'bronze', 'silver', 'gold', 'platinum', 'diamond', 'titan', 'immortal']):
                player_data['profile']['tier'] = tier_text
                break
    
    # LP/MMR 정보
    lp_selectors = [
        '.css-1ynm8dt',  # LP 표시 클래스
        '.lp',
        '.mmr',
        '.rating-points',
        '[class*="lp"]',
        '[class*="rating"]' # 일반적인 점수 클래스
    ]
    
    for selector in lp_selectors:
        elem = soup.select_one(selector)
        if elem:
            lp_text = elem.get_text(strip=True)
            if lp_text and ('LP' in lp_text or 'MMR' in lp_text or lp_text.isdigit()):
                player_data['profile']['lp'] = lp_text
                break
    
    # 승률 정보
    winrate_selectors = [
        '.css-1h7j4z9',  # 승률 클래스
        '.winrate',
        '.win-rate',
        '[class*="winrate"]',
        '[class*="win-rate"]',
        '[class*="wr"]' # 일반적인 승률 클래스
    ]
    
    for selector in winrate_selectors:
        elem = soup.select_one(selector)
        if elem:
            winrate_text = elem.get_text(strip=True)
            if winrate_text and ('%' in winrate_text or 'win' in winrate_text.lower()):
                player_data['profile']['winrate'] = winrate_text
                break
    
    # 총 게임 수
    games_selectors = [
        '.total-games',
        '.games-played',
        '[class*="total"]',
        '[class*="games"]',
        '[class*="matches"]' # 일반적인 게임 수 클래스
    ]
    
    for selector in games_selectors:
        elem = soup.select_one(selector)
        if elem:
            games_text = elem.get_text(strip=True)
            if games_text and ('게임' in games_text or 'games' in games_text.lower() or games_text.isdigit()):
                player_data['profile']['total_games'] = games_text
                break


async def _extract_rank_info(soup: BeautifulSoup, player_data: Dict[str, Any]):
    """랭크 정보 추출"""
    
    # 랭킹 정보
    rank_selectors = [
        '.css-1h0j2z4',  # 순위 표시 클래스
        '.rank-position',
        '.ranking',
        '[class*="rank"]'
    ]
    
    for selector in rank_selectors:
        elem = soup.select_one(selector)
        if elem:
            rank_text = elem.get_text(strip=True)
            if rank_text and ('#' in rank_text or '위' in rank_text or rank_text.isdigit()):
                player_data['rank_info']['position'] = rank_text
                break
    
    # 서버/지역 랭킹
    server_rank_selectors = [
        '.server-rank',
        '.region-rank',
        '[class*="server"]'
    ]
    
    for selector in server_rank_selectors:
        elem = soup.select_one(selector)
        if elem:
            server_rank_text = elem.get_text(strip=True)
            if server_rank_text:
                player_data['rank_info']['server_rank'] = server_rank_text
                break


async def _extract_recent_games(soup: BeautifulSoup, player_data: Dict[str, Any]):
    """최근 게임 정보 추출 (최대 5게임)"""
    
    # 게임 리스트 찾기
    game_selectors = [
        '.css-1s2u8g9',  # 게임 카드 클래스
        '.match-item',
        '.game-item',
        '.recent-game',
        '[class*="match"]',
        '[class*="game"]',
        'li[class*="match-history__item"]' # 일반적인 최근 게임 아이템 클래스
    ]
    
    games = []
    
    for selector in game_selectors:
        game_elements = soup.select(selector)[:5]  # 최대 5게임
        
        if game_elements:
            for i, game_elem in enumerate(game_elements):
                try:
                    game_info = await _parse_game_element(game_elem, i + 1)
                    if game_info:
                        games.append(game_info)
                except Exception as e:
                    print(f"게임 {i+1} 파싱 중 오류: {e}")
                    continue
            
            if games:  # 게임 정보를 찾았으면 중단
                break
    
    # 게임 정보가 없으면 테이블 형태로 시도
    if not games:
        await _extract_games_from_table(soup, games)
    
    player_data['recent_games'] = games[:5]  # 최대 5게임만


async def _parse_game_element(game_elem, game_number: int) -> Optional[Dict[str, Any]]:
    """개별 게임 요소 파싱"""
    
    game_info = {
        'game_number': game_number,
        'result': None,
        'character': None,
        'rank': None,
        'kills': None,
        'duration': None,
        'mode': None
    }
    
    # 게임 결과 (승/패)
    result_indicators = game_elem.select('.win, .victory, .lose, .defeat, [class*="win"], [class*="lose"], [class*="victory"], [class*="defeat"], [class*="result"] span')
    for indicator in result_indicators:
        class_list = ' '.join(indicator.get('class', []))
        text = indicator.get_text(strip=True).lower()
        
        if 'win' in class_list.lower() or 'victory' in class_list.lower() or '승리' in text:
            game_info['result'] = '승리'
            break
        elif 'lose' in class_list.lower() or 'defeat' in class_list.lower() or '패배' in text:
            game_info['result'] = '패배'
            break
    
    # 캐릭터 이름
    char_selectors = [
        '.character-name',
        '.char-name',
        '[class*="character"]',
        '.css-character',
        'img[alt*="character"]',
        '[class*="character-name"] span' # 일반적인 캐릭터 이름 클래스
    ]
    
    for selector in char_selectors:
        char_elem = game_elem.select_one(selector)
        if char_elem:
            if char_elem.name == 'img':
                char_name = char_elem.get('alt', '')
            else:
                char_name = char_elem.get_text(strip=True)
            
            if char_name and len(char_name) > 1:
                game_info['character'] = char_name
                break
    
    # 순위
    rank_selectors = [
        '.rank',
        '.position',
        '[class*="rank"]',
        '.placement',
        '[class*="ranking"] span' # 일반적인 순위 클래스
    ]
    
    for selector in rank_selectors:
        rank_elem = game_elem.select_one(selector)
        if rank_elem:
            rank_text = rank_elem.get_text(strip=True)
            if rank_text and (rank_text.isdigit() or '위' in rank_text):
                game_info['rank'] = rank_text
                break
    
    # 킬 수
    kill_selectors = [
        '.kills',
        '.kill-count',
        '[class*="kill"]',
        '[class*="kda"] span' # 일반적인 킬 수 클래스
    ]
    
    for selector in kill_selectors:
        kill_elem = game_elem.select_one(selector)
        if kill_elem:
            kill_text = kill_elem.get_text(strip=True)
            if kill_text and (kill_text.isdigit() or 'kill' in kill_text.lower()):
                game_info['kills'] = kill_text
                break
    
    # 게임 시간
    duration_selectors = [
        '.duration',
        '.game-time',
        '.time',
        '[class*="duration"]',
        '[class*="time"]',
        '[class*="length"] span' # 일반적인 게임 시간 클래스
    ]
    
    for selector in duration_selectors:
        duration_elem = game_elem.select_one(selector)
        if duration_elem:
            duration_text = duration_elem.get_text(strip=True)
            if duration_text and (':' in duration_text or 'min' in duration_text or 'm' in duration_text):
                game_info['duration'] = duration_text
                break
    
    # 게임 모드
    mode_selectors = [
        '.game-mode',
        '.mode',
        '[class*="mode"]',
        '[class*="queue-type"] span' # 일반적인 게임 모드 클래스
    ]
    
    for selector in mode_selectors:
        mode_elem = game_elem.select_one(selector)
        if mode_elem:
            mode_text = mode_elem.get_text(strip=True)
            if mode_text and len(mode_text) > 0:
                game_info['mode'] = mode_text
                break
    
    # 최소한 하나의 의미있는 정보가 있는지 확인
    meaningful_fields = ['result', 'character', 'rank', 'kills']
    if any(game_info.get(field) for field in meaningful_fields):
        return game_info
    
    return None


async def _extract_games_from_table(soup: BeautifulSoup, games: List[Dict[str, Any]]):
    """테이블 형태의 게임 기록에서 정보 추출"""
    
    table_selectors = [
        'table',
        '.match-history-table',
        '.games-table',
        '[class*="table"]'
    ]
    
    for selector in table_selectors:
        table = soup.select_one(selector)
        if table:
            rows = table.select('tr')[1:6]  # 헤더 제외, 최대 5행
            
            for i, row in enumerate(rows):
                cells = row.select('td, th')
                if len(cells) >= 3:  # 최소 3개 컬럼 필요
                    game_info = {
                        'game_number': i + 1,
                        'result': None,
                        'character': None,
                        'rank': None,
                        'kills': None,
                        'duration': None,
                        'mode': None
                    }
                    
                    # 각 셀에서 정보 추출
                    for cell in cells:
                        cell_text = cell.get_text(strip=True)
                        cell_class = ' '.join(cell.get('class', []))
                        
                        # 결과 판정
                        if '승리' in cell_text or 'win' in cell_text.lower() or 'victory' in cell_class.lower():
                            game_info['result'] = '승리'
                        elif '패배' in cell_text or 'lose' in cell_text.lower() or 'defeat' in cell_class.lower():
                            game_info['result'] = '패배'
                        
                        # 캐릭터명 (일반적으로 특정 길이 이상의 텍스트)
                        if len(cell_text) > 2 and not cell_text.isdigit() and '위' not in cell_text:
                            if not game_info['character']:
                                game_info['character'] = cell_text
                        
                        # 순위 (숫자 + 위 또는 단순 숫자)
                        if cell_text.isdigit() or '위' in cell_text:
                            if not game_info['rank']:
                                game_info['rank'] = cell_text
                    
                    if any(game_info.get(field) for field in ['result', 'character', 'rank']):
                        games.append(game_info)
            
            if games:  # 테이블에서 게임을 찾았으면 중단
                break

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
    
    # YouTube 체크 작업 시작
    check_youtube_shorts.start()
    
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
    
    # 멘션 처리 - 데비가 응답
    if bot.user in message.mentions:
        response = await generate_ai_response(
            characters["debi"], 
            message.content, 
            "사용자가 봇을 멘션했습니다"
        )
        embed = create_character_embed(characters["debi"], "멘션 응답", response)
        
        files = []
        if os.path.exists('./assets/debi.png'):
            files.append(discord.File('./assets/debi.png'))
        
        await message.reply(embed=embed, files=files)
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
        
        files = []
        if selected_character["name"] == "데비" and os.path.exists('./assets/debi.png'):
            files.append(discord.File('./assets/debi.png'))
        elif selected_character["name"] == "마를렌" and os.path.exists('./assets/marlen.png'):
            files.append(discord.File('./assets/marlen.png'))
        
        await message.reply(embed=embed, files=files)
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
        
        files = []
        if os.path.exists('./assets/debi.png'):
            files.append(discord.File('./assets/debi.png'))
        
        await interaction.followup.send(embed=debi_embed, files=files)
        
        await asyncio.sleep(1)
        marlene_files = []
        if os.path.exists('./assets/marlen.png'):
            marlene_files.append(discord.File('./assets/marlen.png'))
        await interaction.followup.send(embed=marlene_embed, files=marlene_files)
    except Exception as error:
        print(f'안녕 커맨드 오류: {error}')
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message("어라? 뭔가 문제가 생겼어! 😅", ephemeral=True)
        except:
            pass

@bot.tree.command(name="도움", description="마를렌이 봇 사용법을 알려드립니다")
async def help_slash(interaction: discord.Interaction):
    """도움말 슬래시 커맨드"""
    await interaction.response.defer()
    
    response = await generate_ai_response(
        characters["marlene"], "도움말", "사용자가 도움말을 요청했습니다"
    )
    
    embed = discord.Embed(
        color=characters["marlene"]["color"],
        title=f'{characters["marlene"]["name"]}의 도움말',
        description=response
    )
    embed.add_field(
        name='🌟 데비의 기능', 
        value='• 유튜브 쇼츠 알림\n• 재밌는 대화\n• 활발한 응답', 
        inline=True
    )
    embed.add_field(
        name='🔮 마를렌의 기능', 
        value='• 봇 설정 관리\n• 도움말 제공\n• 차분한 안내', 
        inline=True
    )
    embed.add_field(
        name='📝 슬래시 커맨드 목록', 
        value='`/안녕` - 인사\n`/전적` - 전적 검색\n`/랭킹` - 랭킹 정보\n`/캐릭터` - 캐릭터 정보\n`/설정` - 봇 설정\n`/테스트` - 봇 테스트\n`/유튜브` - 유튜브 영상 검색\n`/대화` - AI와 자유 대화', 
        inline=False
    )
    embed.set_footer(text='궁금한 점이 있으시면 언제든 말씀하세요!')
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="전적", description="데비가 전적을 검색해드려요")
async def stats_slash(interaction: discord.Interaction, 닉네임: str):
    """전적 검색 슬래시 커맨드"""
    try:
        await interaction.response.defer()
    except discord.errors.NotFound:
        print("❌ 인터랙션이 이미 만료됨 - 전적 검색 중단")
        return
    except Exception as defer_error:
        print(f"❌ defer 실패: {defer_error}")
        return
    
    # 플레이어 전적 정보 가져오기
    try:
        player_stats = await fetch_detailed_player_stats(닉네임)
    except PlayerStatsError as e:
        if "player_not_found" in str(e):
            response = await generate_ai_response(
                characters["debi"], f"{닉네임} 전적 검색 실패", 
                "플레이어를 찾을 수 없었습니다"
            )
            embed = create_character_embed(
                characters["debi"], "전적 검색 실패", 
                f"{response}\n\n❌ '{닉네임}' 플레이어를 찾을 수 없어!\n닉네임을 다시 확인해봐!"
            )
        else:
            response = await generate_ai_response(
                characters["debi"], "전적 검색 오류", 
                "전적 검색 중 오류가 발생했습니다"
            )
            embed = create_character_embed(
                characters["debi"], "전적 검색 오류", 
                f"{response}\n\n⚠️ 전적 조회 중 오류가 발생했습니다: {e}"
            )
        files = []
        if os.path.exists('./assets/debi.png'):
            files.append(discord.File('./assets/debi.png'))
        await interaction.followup.send(embed=embed, files=files)
        return

    # 성공 시 전적 정보 표시
    response = await generate_ai_response(
        characters["debi"], f"{닉네임} 전적 정보", 
        f"플레이어 {닉네임}의 전적을 성공적으로 찾았습니다"
    )
    
    # 기본 정보 구성
    stats_info = f"**🎮 플레이어**: {player_stats.get('name', 닉네임)}\n"
    
    if player_stats.get('level'):
        stats_info += f"**📊 레벨**: {player_stats['level']}\n"
    
    profile = player_stats.get('profile', {})
    if profile.get('tier'):
        stats_info += f"**🏆 티어**: {profile['tier']}\n"
    
    if profile.get('lp'):
        stats_info += f"**💎 LP**: {profile['lp']}\n"
    
    if profile.get('winrate'):
        stats_info += f"**📈 승률**: {profile['winrate']}\n"
    
    if profile.get('total_games'):
        stats_info += f"**🎯 게임 수**: {profile['total_games']}\n"
    
    # 최근 게임 정보
    if player_stats.get('recent_games'):
        stats_info += f"\n**⭐ 최근 게임**:\n"
        for game in player_stats['recent_games']:
            result = game.get('result', '')
            character = game.get('character', '')
            rank = game.get('rank', '')
            kills = game.get('kills', '')
            stats_info += f"- {result} ({character}): {rank}, {kills}\n"
    
    stats_info += f"\n🔗 [상세 전적 보기]({player_stats['url']})"
    
    embed = create_character_embed(
        characters["debi"], "전적 검색 결과", 
        f"{response}\n\n{stats_info}"
    )
    embed.set_footer(text="데비가 dak.gg에서 가져온 정보야!")
    
    files = []
    if os.path.exists('./assets/debi.png'):
        files.append(discord.File('./assets/debi.png'))
    await interaction.followup.send(embed=embed, files=files)

@bot.tree.command(name="랭킹", description="마를렌이 현재 랭킹 정보를 알려드려요")
async def ranking_slash(interaction: discord.Interaction):
    """랭킹 정보 슬래시 커맨드"""
    await interaction.response.defer()
    
    response = await generate_ai_response(
        characters["marlene"], "랭킹 정보", "사용자가 현재 랭킹을 요청했습니다"
    )
    embed = create_character_embed(
        characters["marlene"], "랭킹 정보", 
        response + "\n\n📊 현재 이터널리턴 랭킹 정보를 확인 중..."
    )
    
    files = []
    if os.path.exists('./assets/marlen.png'):
        files.append(discord.File('./assets/marlen.png'))
    await interaction.followup.send(embed=embed, files=files)

@bot.tree.command(name="캐릭터", description="마를렌이 캐릭터 정보를 알려드려요")
async def character_slash(interaction: discord.Interaction, 캐릭터명: str):
    """캐릭터 정보 슬래시 커맨드"""
    await interaction.response.defer()
    
    response = await generate_ai_response(
        characters["marlene"], f"{캐릭터명} 캐릭터 정보", "사용자가 캐릭터 정보를 요청했습니다"
    )
    embed = create_character_embed(
        characters["marlene"], "캐릭터 정보", 
        response + f"\n\n⚔️ {캐릭터명} 정보를 찾고 있어..."
    )
    
    files = []
    if os.path.exists('./assets/marlen.png'):
        files.append(discord.File('./assets/marlen.png'))
    await interaction.followup.send(embed=embed, files=files)

@bot.tree.command(name="설정", description="마를렌이 봇 설정을 도와드려요")
async def settings_slash(interaction: discord.Interaction, 설정내용: Optional[str] = None):
    """설정 슬래시 커맨드"""
    await interaction.response.defer()
    
    if not 설정내용:
        response = await generate_ai_response(
            characters["marlene"], "설정 도움", "사용자가 설정 방법을 문의했습니다"
        )
    else:
        response = await generate_ai_response(
            characters["marlene"], 설정내용, "설정 변경 요청"
        )
    
    embed = create_character_embed(characters["marlene"], "설정 관리", response)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="테스트", description="데비와 마를렌과 함께 봇 테스트하기")
async def test_slash(interaction: discord.Interaction):
    """테스트 슬래시 커맨드"""
    await interaction.response.defer()
    
    debi_response = await generate_ai_response(
        characters["debi"], "테스트", "봇 테스트를 하고 있습니다"
    )
    marlene_response = await generate_ai_response(
        characters["marlene"], "테스트", "봇 테스트를 하고 있습니다"
    )
    
    debi_embed = create_character_embed(characters["debi"], "테스트", debi_response)
    marlene_embed = create_character_embed(characters["marlene"], "테스트", marlene_response)
    
    debi_files = []
    if os.path.exists('./assets/debi.png'):
        debi_files.append(discord.File('./assets/debi.png'))
    
    await interaction.followup.send(embed=debi_embed, files=debi_files)
    
    await asyncio.sleep(1.5)
    marlene_files = []
    if os.path.exists('./assets/marlen.png'):
        marlene_files.append(discord.File('./assets/marlen.png'))
    await interaction.followup.send(embed=marlene_embed, files=marlene_files)

@bot.tree.command(name="대화", description="데비나 마를렌과 자유롭게 대화하기")
async def chat_slash(interaction: discord.Interaction, 메시지: str, 캐릭터: Optional[str] = None):
    """AI 자유 대화 슬래시 커맨드"""
    await interaction.response.defer()
    
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
    embed = create_character_embed(selected_character, "AI 대화", response)
    
    files = []
    if selected_character["name"] == "데비" and os.path.exists('./assets/debi.png'):
        files.append(discord.File('./assets/debi.png'))
    elif selected_character["name"] == "마를렌" and os.path.exists('./assets/marlen.png'):
        files.append(discord.File('./assets/marlen.png'))
    
    await interaction.followup.send(embed=embed, files=files)

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
    try:
        if anthropic_client:
            print(f"🤖 Claude API 호출 시작 - 캐릭터: {character['name']}, 메시지: {user_message[:50]}...")
            
            prompt = f"""{character['ai_prompt']}

사용자 메시지: "{user_message}"
상황: {context}

위 캐릭터 성격에 맞게 한국어로 자연스럽게 대답해줘. 너무 길지 않게 1-2문장으로."""

            
        else:
            print("⚠️ Claude API 키가 설정되지 않음 - 기본 응답 사용")
            
    except Exception as error:
        print(f"⚠️ AI 응답 생성 중 예외 발생: {type(error).__name__}: {str(error)}")
        print(f"Anthropic 클라이언트 상태: {type(anthropic_client) if anthropic_client else 'None'}")
        
        # fallback: 기본 응답 패턴 사용
        print("🔄 Fallback 응답 생성 중...")
        
    # 기본 응답 로직 (API 실패 시 또는 API 키 없을 시)
    try:
        responses = {
            "debi": [
                f"와! {user_message}? 완전 흥미진진한데! 😍",
                f"어머! 진짜? {user_message} 얘기하는 거야? 대박! ✨",
                f"{user_message}라니! 완전 재밌겠다~ 나도 궁금해! 🤔",
                f"오오! {user_message}? 데비도 그거 좋아해! 😊",
                f"{user_message}? 우와! 얼른 더 알려줘! 🎉"
            ],
            "marlene": [
                f"{user_message}에 대해 말씀하시는군요. 차근차근 살펴보겠습니다.",
                f"{user_message}라고 하셨는데, 정확히 어떤 부분이 궁금하신가요?",
                f"그렇군요. {user_message}에 대해 도움을 드릴 수 있을 것 같습니다.",
                f"{user_message}... 흥미로운 주제네요. 자세히 설명해드리겠습니다.",
                f"{user_message}에 관해서라면 제가 도움을 드릴 수 있겠네요."
            ]
        }
        
        character_responses = responses["debi" if character["name"] == "데비" else "marlene"]
        fallback_response = random.choice(character_responses)
        print(f"📝 Fallback 응답 선택: {fallback_response[:50]}...")
        return fallback_response
        
    except Exception as fallback_error:
        print(f"❌ Fallback 응답 생성도 실패: {fallback_error}")
        
        # 최후 수단: 하드코딩된 에러 응답
        return ("어? 뭔가 문제가 생긴 것 같아! 다시 말해줄래? 😅" 
                if character["name"] == "데비" 
                else "죄송합니다. 일시적인 문제가 발생했습니다. 다시 시도해주세요.")

def create_character_embed(character: Dict[str, Any], title: str, description: str) -> discord.Embed:
    """캐릭터별 임베드 생성"""
    embed = discord.Embed(
        color=character["color"],
        title=character["name"],
        description=description
    )
    embed.set_footer(text=f'{character["name"]} - 이터널리턴')
    
    if character["image"]:
        image_filename = character["image"].split('./')[-1]
        embed.set_thumbnail(url=f'attachment://{image_filename}')
    
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
                        
                        await channel.send(embed=embed)
                        
    except Exception as error:
        print(f'YouTube 체크 오류: {error}')

@check_youtube_shorts.before_loop
async def before_check_youtube_shorts():
    """YouTube 체크 시작 전 봇 준비 대기"""
    await bot.wait_until_ready()

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))