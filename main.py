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

# 이터널 리턴 API 설정
ETERNAL_RETURN_API_BASE = "https://open-api.bser.io"
ETERNAL_RETURN_API_KEY = os.getenv('EternalReturn_API_KEY')

async def get_user_by_nickname_er(nickname: str) -> Dict[str, Any]:
    """이터널 리턴 공식 API - 닉네임으로 유저 정보 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': ETERNAL_RETURN_API_KEY,
                'Accept': 'application/json'
            }
            
            params = {
                'query': nickname
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

async def get_user_stats_er(user_num: int, season_id: int = 26) -> Dict[str, Any]:
    """이터널 리턴 공식 API - 유저 통계 정보 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': ETERNAL_RETURN_API_KEY,
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/user/stats/{user_num}/{season_id}"
            
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

async def get_user_rank_er(user_num: int, season_id: int = 26, matching_team_mode: int = 3) -> Dict[str, Any]:
    """이터널 리턴 공식 API - 유저 랭킹 정보 조회"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': ETERNAL_RETURN_API_KEY,
                'Accept': 'application/json'
            }
            
            url = f"{ETERNAL_RETURN_API_BASE}/v1/rank/{user_num}/{season_id}/{matching_team_mode}"
            
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

async def get_player_stats_official_er(nickname: str) -> Dict[str, Any]:
    """
    이터널 리턴 공식 API를 사용한 플레이어 전적 조회
    
    Returns:
        Dict containing: nickname, tier, rank_point, total_games, wins, winrate, avg_rank, userNum
    """
    try:
        print(f"🔍 공식 API로 {nickname} 전적 검색 시작")
        
        # 1. 닉네임으로 유저 정보 조회
        user_info = await get_user_by_nickname_er(nickname)
        
        if not user_info.get('user'):
            raise PlayerStatsError("player_not_found")
        
        user_data = user_info['user']
        user_num = user_data['userNum']
        
        print(f"✅ 유저 발견: {user_data['nickname']} (userNum: {user_num})")
        
        # 2. 유저 통계 조회
        try:
            stats_data = await get_user_stats_er(user_num)
            print(f"✅ 통계 데이터 조회 성공")
        except:
            stats_data = None
            print(f"⚠️ 통계 데이터 조회 실패")
        
        # 3. 랭킹 정보 조회 (솔로 기준)
        rank_data = await get_user_rank_er(user_num, 26, 3)  # 솔로 랭크
        
        # 결과 정리
        result = {
            'nickname': user_data['nickname'],
            'userNum': user_num,
            'tier': None,
            'rank_point': None,
            'total_games': None,
            'wins': None,
            'winrate': None,
            'avg_rank': None
        }
        
        # 랭킹 정보 처리
        if rank_data and rank_data.get('userRank'):
            rank_info = rank_data['userRank']
            tier_type = rank_info.get('tierType', 'Unranked')
            division = rank_info.get('division', '')
            result['tier'] = f"{tier_type} {division}".strip()
            result['rank_point'] = rank_info.get('rp', 0)
            print(f"✅ 랭킹: {result['tier']} ({result['rank_point']}RP)")
        else:
            result['tier'] = "Unranked"
            print(f"⚠️ 랭킹 정보 없음 (Unranked)")
        
        # 통계 정보 처리 (가장 많이 플레이한 모드 기준)
        if stats_data and stats_data.get('userStats'):
            user_stats = stats_data['userStats']
            
            # 가장 게임 수가 많은 모드 찾기
            best_mode_stats = None
            max_games = 0
            
            for stats in user_stats:
                total_games = stats.get('totalGames', 0)
                if total_games > max_games:
                    max_games = total_games
                    best_mode_stats = stats
            
            if best_mode_stats:
                result['total_games'] = best_mode_stats.get('totalGames', 0)
                result['wins'] = best_mode_stats.get('totalWins', 0)
                
                # 승률 계산
                if result['total_games'] > 0:
                    winrate = (result['wins'] / result['total_games']) * 100
                    result['winrate'] = f"{winrate:.1f}%"
                
                result['avg_rank'] = best_mode_stats.get('averageRank', 0)
                print(f"✅ 통계: {result['total_games']}게임 {result['winrate']} 승률")
        else:
            print(f"⚠️ 상세 통계 없음")
        
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
        
        # AI 응답 생성
        response = await generate_ai_response(
            characters["debi"], 
            f"{닉네임} 전적 검색 완료", 
            f"플레이어 {닉네임}의 전적을 성공적으로 찾았습니다"
        )
        
        # 전적 정보 포맷팅
        stats_text = f"**🎮 플레이어**: {stats['nickname']}\n"
        
        found_info = False
        
        if stats['tier']:
            tier_text = stats['tier']
            if stats['rank_point'] and stats['rank_point'] > 0:
                tier_text += f" ({stats['rank_point']}RP)"
            stats_text += f"**🏆 티어**: {tier_text}\n"
            found_info = True
        
        if stats['total_games'] and stats['total_games'] > 0:
            stats_text += f"**🎯 게임 수**: {stats['total_games']}게임\n"
            found_info = True
        
        if stats['winrate']:
            stats_text += f"**📈 승률**: {stats['winrate']}\n"
            found_info = True
            
        if stats['wins']:
            stats_text += f"**🏅 승리**: {stats['wins']}승\n"
            found_info = True
        
        if stats['avg_rank'] and stats['avg_rank'] > 0:
            stats_text += f"**📊 평균 순위**: {stats['avg_rank']:.1f}위\n"
            found_info = True
        
        if not found_info:
            stats_text += "\n⚠️ 상세 정보를 가져오지 못했어!\n랭크 게임을 더 플레이해봐!\n"
        
        stats_text += f"\n🔗 [공식 API 기반 정보]"
        
        # 결과 임베드 생성
        result_embed = create_character_embed(
            characters["debi"], 
            "전적 검색 결과", 
            f"{response}\n\n{stats_text}",
            f"/전적 {닉네임}"
        )
        result_embed.set_footer(text="데비가 이터널리턴 공식 API에서 가져온 정보야!")
        
        # 원본 메시지 편집
        await interaction.edit_original_response(embed=result_embed)
        
    except PlayerStatsError as e:
        if "player_not_found" in str(e):
            response = await generate_ai_response(
                characters["debi"], 
                f"{닉네임} 전적 검색 실패", 
                "플레이어를 찾을 수 없었습니다"
            )
            error_embed = create_character_embed(
                characters["debi"], 
                "전적 검색 실패", 
                f"{response}\n\n❌ **'{닉네임}'** 플레이어를 찾을 수 없어!\n닉네임을 다시 확인해줘!",
                f"/전적 {닉네임}"
            )
        else:
            response = await generate_ai_response(
                characters["debi"], 
                "전적 검색 오류", 
                "전적 검색 중 오류가 발생했습니다"
            )
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

    # Claude API 호출
    message = await anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=150,
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