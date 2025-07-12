import os
import asyncio
import random
import aiofiles
from datetime import datetime
from typing import Optional, Dict, Any
import urllib.parse

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from anthropic import Anthropic
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
anthropic_client = None
youtube = None
ETERNAL_RETURN_CHANNEL_ID = 'UCaktoGSdjMnfQFv5BSyYrvA'
last_checked_video_id = None

async def initialize_claude_api():
    """Claude API 초기화"""
    global anthropic_client
    try:
        api_key = os.getenv('CLAUDE_API_KEY')
        
        if api_key and api_key != 'your_claude_api_key_here':
            anthropic_client = Anthropic(api_key=api_key)
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

async def fetch_player_stats(nickname: str) -> Dict[str, Any]:
    """dak.gg에서 플레이어 전적 정보 가져오기"""
    try:
        # URL 인코딩
        encoded_nickname = urllib.parse.quote(nickname)
        url = f"https://dak.gg/er/players/{encoded_nickname}"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 404:
                    return {"error": "player_not_found", "message": "플레이어를 찾을 수 없습니다."}
                elif response.status != 200:
                    return {"error": "request_failed", "message": f"요청 실패: {response.status}"}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 플레이어 기본 정보 추출
                player_info = {}
                
                # 플레이어 이름과 레벨 정보 (dak.gg의 실제 구조에 맞춰 수정)
                # 여러 가능한 선택자로 시도
                name_selectors = [
                    'h3',  # 기본 h3 태그
                    '.player-name',
                    '.css-389hsa h3',
                    '.content h3'
                ]
                
                player_name = None
                level_info = None
                
                for selector in name_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        text = elem.get_text(strip=True)
                        if text and len(text) > 0:
                            # 레벨 정보가 포함된 경우 분리
                            if 'Lv.' in text:
                                parts = text.split('Lv.')
                                if len(parts) >= 2:
                                    player_name = parts[0].strip()
                                    level_info = f"Lv.{parts[1].strip()}"
                                else:
                                    player_name = text
                            else:
                                player_name = text
                            break
                
                player_info['name'] = player_name or nickname
                if level_info:
                    player_info['level'] = level_info
                
                # 최근 업데이트 정보
                update_elem = soup.select_one('.css-1v2jvkd')
                if update_elem:
                    update_text = update_elem.get_text(strip=True)
                    if '최근 업데이트:' in update_text:
                        player_info['last_update'] = update_text.replace('최근 업데이트:', '').strip()
                
                # 기본적인 정보가 없으면 일반적인 선택자들로 시도
                if not player_info.get('level'):
                    # 다양한 레벨 선택자 시도
                    level_selectors = [
                        '.level', '.player-level', '[class*="level"]',
                        '.css-389hsa .content .top', '.player-info .level'
                    ]
                    for selector in level_selectors:
                        elem = soup.select_one(selector)
                        if elem:
                            text = elem.get_text(strip=True)
                            if 'Lv.' in text:
                                player_info['level'] = text
                                break
                
                # 티어, LP, 승률 등의 정보를 찾기 위한 일반적인 선택자들
                stats_selectors = {
                    'tier': ['.tier', '.rank', '.rating', '[class*="tier"]', '[class*="rank"]'],
                    'lp': ['.lp', '.mmr', '.points', '[class*="lp"]', '[class*="mmr"]'],
                    'winrate': ['.winrate', '.win-rate', '.wr', '[class*="winrate"]', '[class*="win"]'],
                    'games': ['.games', '.matches', '.total-games', '[class*="games"]', '[class*="match"]']
                }
                
                for stat_name, selectors in stats_selectors.items():
                    for selector in selectors:
                        elem = soup.select_one(selector)
                        if elem:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 0:
                                player_info[stat_name] = text
                                break
                
                # 캐릭터 통계 정보 시도
                character_stats = []
                char_selectors = [
                    '.character-stat', '.character-info', '.char-stat',
                    '[class*="character"]', '.most-played'
                ]
                
                for selector in char_selectors:
                    char_elements = soup.select(selector)[:3]  # 상위 3개
                    if char_elements:
                        for char_elem in char_elements:
                            char_text = char_elem.get_text(strip=True)
                            if char_text and len(char_text) > 5:  # 의미있는 텍스트만
                                character_stats.append({
                                    'name': char_text[:20],  # 처음 20자만
                                    'info': char_text
                                })
                        break
                
                if character_stats:
                    player_info['favorite_characters'] = character_stats
                
                player_info['url'] = url
                
                # 최소한의 정보라도 있는지 확인
                if not any(key in player_info for key in ['level', 'tier', 'winrate', 'last_update']):
                    # 페이지는 로드되었지만 통계 정보가 없는 경우
                    player_info['message'] = "플레이어 페이지를 찾았지만 통계 정보가 없습니다. 게임을 플레이한 기록이 있는지 확인해주세요."
                
                return player_info
                
    except Exception as error:
        print(f'플레이어 전적 조회 오류: {error}')
        return {"error": "fetch_failed", "message": f"전적 조회 중 오류가 발생했습니다: {str(error)}"}

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
    player_stats = await fetch_player_stats(닉네임)
    
    if "error" in player_stats:
        # 에러 발생 시 데비의 응답
        if player_stats["error"] == "player_not_found":
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
                f"{response}\n\n⚠️ {player_stats['message']}"
            )
    else:
        # 성공 시 전적 정보 표시
        response = await generate_ai_response(
            characters["debi"], f"{닉네임} 전적 정보", 
            f"플레이어 {닉네임}의 전적을 성공적으로 찾았습니다"
        )
        
        # 기본 정보 구성
        stats_info = f"**🎮 플레이어**: {player_stats.get('name', 닉네임)}\n"
        
        if player_stats.get('level'):
            stats_info += f"**📊 레벨**: {player_stats['level']}\n"
        
        if player_stats.get('last_update'):
            stats_info += f"**🕒 최근 업데이트**: {player_stats['last_update']}\n"
        
        if player_stats.get('tier'):
            stats_info += f"**🏆 티어**: {player_stats['tier']}\n"
        
        if player_stats.get('lp'):
            stats_info += f"**💎 LP**: {player_stats['lp']}\n"
        
        if player_stats.get('winrate'):
            stats_info += f"**📈 승률**: {player_stats['winrate']}\n"
        
        if player_stats.get('games'):
            stats_info += f"**🎯 게임 수**: {player_stats['games']}\n"
        
        # 선호 캐릭터 정보
        if player_stats.get('favorite_characters'):
            stats_info += f"\n**⭐ 캐릭터 정보**:\n"
            for i, char in enumerate(player_stats['favorite_characters'][:3], 1):
                if 'winrate' in char and 'games' in char:
                    stats_info += f"`{i}.` {char['name']} - {char['winrate']} ({char['games']})\n"
                else:
                    stats_info += f"`{i}.` {char.get('info', char.get('name', '정보 없음'))}\n"
        
        # 추가 메시지가 있는 경우
        if player_stats.get('message'):
            stats_info += f"\n📝 {player_stats['message']}\n"
        
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

            try:
                # 동기 함수이므로 await 제거
                message = anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=100,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                
                ai_response = message.content[0].text
                print(f"✅ Claude API 응답 성공: {ai_response[:50]}...")
                return ai_response
                
            except Exception as api_error:
                print(f"❌ Claude API 호출 실패: {type(api_error).__name__}: {str(api_error)}")
                print(f"API 키 상태: {'있음' if anthropic_client else '없음'}")
                
                # API 호출 실패 시 기본 응답으로 fallback
                print("🔄 기본 응답 모드로 전환")
                raise api_error  # 예외를 다시 던져서 아래 except 블록에서 처리
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