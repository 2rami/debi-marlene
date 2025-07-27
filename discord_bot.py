import asyncio
import random
import discord
from discord.ext import commands, tasks
from typing import Optional, Dict, Any
from googleapiclient.discovery import build
import aiohttp
from bs4 import BeautifulSoup

from config import characters, DISCORD_TOKEN, YOUTUBE_API_KEY, ETERNAL_RETURN_CHANNEL_ID
import config
from ai_utils import initialize_claude_api, generate_ai_response, create_character_embed
from api_clients import get_simple_player_stats, get_premium_analysis

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# YouTube 설정
youtube = None
last_checked_video_id = None

async def initialize_youtube():
    """YouTube API 초기화"""
    global youtube
    try:
        if YOUTUBE_API_KEY:
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            print("✅ YouTube API 초기화 완료")
        else:
            print("⚠️ YouTube API 키가 없습니다")
    except Exception as e:
        print(f"❌ YouTube API 초기화 실패: {e}")

@bot.event
async def on_ready():
    """봇이 준비되었을 때"""
    print(f'{bot.user}로 로그인했습니다!')
    
    try:
        synced = await bot.tree.sync()
        print(f"슬래시 커맨드 {len(synced)}개 동기화 완료")
    except Exception as e:
        print(f"슬래시 커맨드 동기화 실패: {e}")
    
    # 백그라운드 작업 시작
    if not check_youtube_shorts.is_running():
        check_youtube_shorts.start()
    
    # AI 초기화
    await initialize_claude_api()
    await initialize_youtube()

@bot.event
async def on_message(message):
    """메시지 이벤트 처리"""
    if message.author == bot.user:
        return
    
    # CHAT_CHANNEL_ID가 설정되어 있고, 해당 채널이 아니면 무시
    if config.CHAT_CHANNEL_ID and message.channel.id != config.CHAT_CHANNEL_ID:
        await bot.process_commands(message)
        return
    
    # 봇이 멘션되었거나 DM인 경우 AI 응답
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # 멘션 제거
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if content:
            # 랜덤하게 캐릭터 선택
            character = random.choice(list(characters.values()))
            
            # AI 응답 생성
            response = await generate_ai_response(character, content)
            
            # 임베드로 응답
            embed = create_character_embed(
                character, 
                f"💬 {character['name']}의 답변",
                response,
                content
            )
            
            await message.reply(embed=embed)
    
    await bot.process_commands(message)

@bot.tree.command(name="안녕", description="데비와 마를렌에게 인사해보세요!")
async def hello_slash(interaction: discord.Interaction):
    """인사 슬래시 커맨드"""
    greetings = [
        "안녕! 나는 데비야! 같이 게임할래?",
        "반가워! 데비야~ 오늘 컨디션 어때?",
        "헤이! 새로운 친구네! 데비라고 해!",
        "와! 안녕하세요~ 데비입니다!",
        "...안녕. 마를렌이야.",
        "안녕하세요. 마를렌입니다... 잘 부탁해요.",
        "...뭐 인사 정도야 해드릴게요. 마를렌이에요.",
        "안녕하세요. 데비 언니와 함께 온 마를렌이라고 해요."
    ]
    
    greeting = random.choice(greetings)
    
    # 데비인지 마를렌인지 구분
    if "데비" in greeting:
        character = characters["debi"]
    else:
        character = characters["marlene"]
    
    embed = create_character_embed(
        character,
        f"👋 {character['name']}의 인사",
        greeting
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="대화", description="데비나 마를렌과 대화해보세요!")
async def chat_slash(interaction: discord.Interaction, 메시지: str, 캐릭터: Optional[str] = None):
    """대화 슬래시 커맨드"""
    await interaction.response.defer()
    
    # 채널 체크
    if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    # 캐릭터 선택
    if 캐릭터:
        if 캐릭터.lower() in ["데비", "debi"]:
            character = characters["debi"]
        elif 캐릭터.lower() in ["마를렌", "marlene"]:
            character = characters["marlene"]
        else:
            character = random.choice(list(characters.values()))
    else:
        character = random.choice(list(characters.values()))
    
    # AI 응답 생성
    response = await generate_ai_response(character, 메시지)
    
    # 임베드로 응답
    embed = create_character_embed(
        character, 
        f"💬 {character['name']}의 답변",
        response,
        메시지
    )
    
    await interaction.followup.send(embed=embed)

class StatsView(discord.ui.View):
    """전적 검색 뷰"""
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
        else:
            return ""  # 기본값

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
        
        # 현재 시즌 랭크 표시
        current_tier = self.player_stats.get('tier_info', '정보 없음').replace('**', '')
        
        embed.add_field(
            name="현재 시즌 (Season 17 - 게임 내 시즌 8)",
            value=f"**{current_tier}**",
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
        embed.set_footer(text="이터널 리턴 • 상위 10개 실험체")
        
        # 상세 데이터가 없으면 가져오기
        if not self.detailed_data:
            await interaction.response.defer()
            try:
                from api_clients import get_player_stats_from_dakgg
                print(f"🔍 실험체 데이터 로드 시작: {self.player_stats['nickname']}")
                self.detailed_data = await get_player_stats_from_dakgg(self.player_stats['nickname'], detailed=True)
                print(f"🔍 상세 데이터 키: {list(self.detailed_data.keys()) if self.detailed_data else 'None'}")
                if self.detailed_data and 'most_characters' in self.detailed_data:
                    print(f"🔍 most_characters 개수: {len(self.detailed_data['most_characters'])}")
                else:
                    print(f"⚠️ most_characters 키가 없음 또는 detailed_data가 None")
            except Exception as e:
                print(f"❌ 상세 데이터 로드 실패: {e}")
                await interaction.followup.send(embed=embed, view=self, ephemeral=True)
                return
        
        # 모스트 캐릭터 정보 표시 (10위까지)
        # detailed_data에서 most_characters 가져오기 (더 정확한 데이터)
        most_chars = []
        if self.detailed_data and 'most_characters' in self.detailed_data:
            most_chars = self.detailed_data['most_characters']
            print(f"🔍 detailed_data에서 most_characters 로드: {len(most_chars)}개")
        else:
            # fallback으로 player_stats에서 가져오기
            most_chars = self.player_stats.get('most_characters', [])
            print(f"🔍 player_stats에서 most_characters 로드: {len(most_chars)}개")
        
        print(f"🔍 최종 most_chars: {most_chars[:3] if most_chars else '데이터 없음'}")
        
        if most_chars:
            # 상위 10개까지 표시
            for i, char in enumerate(most_chars[:10]):
                rank_num = i + 1
                winrate_indicator = self._get_performance_indicator(char.get('winrate', 0), "winrate")
                avg_rank_indicator = self._get_performance_indicator(char.get('avg_rank', 0), "avg_rank")
                
                # 더 상세한 정보 포함
                char_info = f"**{char.get('name', '알 수 없음')}**\n"
                char_info += f"`{char.get('games', 0)}게임` {winrate_indicator}**{char.get('winrate', 0):.1f}%**\n"
                char_info += f"{avg_rank_indicator}평균 **{char.get('avg_rank', 0):.1f}등** "
                char_info += f"**{char.get('avg_kills', 0):.1f}킬**\n"
                char_info += f"🎯 **{char.get('avg_assists', 0):.1f}어시** "
                char_info += f"💥 **{char.get('avg_damage', 0):,.0f}딜**\n"
                top2 = char.get('top2', 0)
                top3 = char.get('top3', 0)
                if top2 > 0 or top3 > 0:
                    char_info += f"🥈 {top2}회 🥉 {top3}회"
                
                embed.add_field(
                    name=f"{rank_num}위", 
                    value=char_info, 
                    inline=True
                )
                
                # 3개마다 빈 필드로 줄바꿈 효과
                if rank_num % 3 == 0 and rank_num < 10:
                    embed.add_field(name="\u200b", value="\u200b", inline=False)
        else:
            embed.add_field(
                name="모스트 캐릭터 정보",
                value="데이터가 없습니다.",
                inline=False
            )
        
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except:
            # 이미 defer된 경우 followup 사용
            await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='통계', style=discord.ButtonStyle.secondary, emoji='📊')
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 게임 통계",
            color=0xE67E22
        )
        # 통계 버튼용 캐릭터
        char_key = self.button_characters["stats"]
        embed.set_author(name=characters[char_key]["name"], icon_url=characters[char_key]["image"])
        embed.set_footer(text="이터널 리턴")
        
        # 통계 정보 표시
        stats = self.stats
        if stats:
            winrate = stats.get('winrate', 0)
            avg_rank = stats.get('avg_rank', 0)
            avg_kills = stats.get('avg_kills', 0)
            
            # 성과 지표와 함께 표시
            winrate_indicator = self._get_performance_indicator(winrate, "winrate")
            rank_indicator = self._get_performance_indicator(avg_rank, "avg_rank")
            kills_indicator = self._get_performance_indicator(avg_kills, "avg_kills")
            
            embed.add_field(
                name="게임 수",
                value=f"**{stats.get('total_games', 0)}**게임",
                inline=True
            )
            embed.add_field(
                name="승률",
                value=f"{winrate_indicator}**{winrate:.1f}%**\n({stats.get('wins', 0)}승)",
                inline=True
            )
            embed.add_field(
                name="평균 순위",
                value=f"{rank_indicator}**{avg_rank:.1f}등**",
                inline=True
            )
            embed.add_field(
                name="평균 킬",
                value=f"{kills_indicator}**{avg_kills:.1f}킬**",
                inline=True
            )
            embed.add_field(
                name="평균 팀킬",
                value=f"**{stats.get('avg_team_kills', 0):.1f}킬**",
                inline=True
            )
            embed.add_field(
                name="MMR",
                value=f"**{self.player_stats.get('mmr', 0)}**",
                inline=True
            )
        else:
            embed.add_field(
                name="통계 정보",
                value="데이터가 없습니다.",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)

class StatsModal(discord.ui.Modal, title='🔍 전적 검색'):
    """전적 검색 모달"""
    def __init__(self):
        super().__init__()

    nickname = discord.ui.TextInput(
        label='닉네임',
        placeholder='검색할 플레이어의 닉네임을 입력하세요',
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await stats_search_logic(interaction, self.nickname.value)

@bot.tree.command(name="전적", description="이터널 리턴 플레이어 전적을 검색해요!")
async def stats_command(interaction: discord.Interaction):
    """전적 검색 슬래시 커맨드"""
    modal = StatsModal()
    await interaction.response.send_modal(modal)

async def stats_search_logic(interaction: discord.Interaction, 닉네임: str, 서버지역: str = None):
    """전적 검색 로직 (모달과 일반 명령어에서 공통 사용)"""
    # 채널 체크
    if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        # 전적 검색 중 메시지
        searching_embed = discord.Embed(
            title="🔍 전적 검색 중...",
            description=f"**{닉네임}**님의 전적을 검색하고 있어요!",
            color=characters["debi"]["color"]
        )
        searching_embed.set_author(
            name=characters["debi"]["name"],
            icon_url=characters["debi"]["image"]
        )
        await interaction.followup.send(embed=searching_embed)
        
        # 전적 검색 수행 - 닥지지 API 사용 (상세 정보 포함)
        from api_clients import get_player_stats_from_dakgg, get_simple_player_stats_only_tier
        player_stats = await get_player_stats_from_dakgg(닉네임)
        
        if player_stats is None:
            # 닥지지 API 실패시 기존 API 사용
            stats = await get_simple_player_stats_only_tier(닉네임)
            if "찾을 수 없습니다" not in stats and "오류" not in stats:
                simple_embed = create_character_embed(
                    characters["debi"],
                    f"🏆 {닉네임}님의 간단 전적",
                    f"**현재 티어**: {stats}\n\n*상세 전적은 일시적으로 조회가 어려워요*"
                )
                await interaction.followup.send(embed=simple_embed)
                return
            else:
                # 완전 실패
                error_embed = create_character_embed(
                    characters["debi"], 
                    "⚠️ 전적 검색 실패",
                    f"**{닉네임}**님의 전적을 찾을 수 없어!",
                    f"/전적 {닉네임}"
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
        else:
            # 닥지지 API 성공 - 상세 정보 포맷팅
            stats = player_stats.get('stats', {})
            most_chars = player_stats.get('most_characters', [])
            most_char = most_chars[0] if most_chars else None
        
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
        current_tier = player_stats.get('tier_info', '정보 없음').replace('**', '')
        basic_embed.add_field(
            name="🏆 랭크", 
            value=f"**{current_tier}**", 
            inline=False
        )
        
        if most_char:
            basic_embed.add_field(
                name="🎯 모스트 실험체", 
                value=f"**{most_char['name']}** ({most_char['games']}게임)", 
                inline=True
            )
        
        if stats:
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
        
    except Exception as e:
        print(f"전적 검색 중 오류: {e}")
        error_embed = create_character_embed(
            characters["debi"], 
            "⚠️ 전적 검색 오류",
            f"**{닉네임}**님의 전적 검색 중 오류가 발생했어! 잠시 후 다시 시도해줘!",
            f"/전적 {닉네임}"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)

@bot.tree.command(name="분석", description="데비가 심층 분석해드려요!")
async def analysis_command(interaction: discord.Interaction, 닉네임: str):
    """AI 분석 명령어"""
    await interaction.response.defer()
    
    # 채널 체크
    if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        # 분석 중 메시지
        analysis_embed = discord.Embed(
            title="🔍 심층 분석 중...",
            description=f"**{닉네임}**님의 플레이 스타일을 분석하고 있어요!",
            color=characters["debi"]["color"]
        )
        analysis_embed.set_author(
            name=characters["debi"]["name"],
            icon_url=characters["debi"]["image"]
        )
        await interaction.followup.send(embed=analysis_embed)
        
        # 분석 데이터 수집
        analysis_data = await get_premium_analysis(닉네임)
        
        if not analysis_data:
            response = f"앗! {닉네임} 플레이어의 데이터를 충분히 가져올 수 없어!"
            error_embed = create_character_embed(
                characters["debi"], 
                "⚠️ 분석 실패",
                response,
                f"/분석 {닉네임}"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return
        
        # AI 분석 컨텍스트 생성
        context = f"플레이어: {닉네임}\n"
        
        stats = analysis_data['stats']
        if stats.get('success'):
            if stats.get('source') == 'dakgg':
                context += f"티어: {stats.get('tier_info', '정보없음')}\n"
                context += f"MMR: {stats.get('mmr', 0)}, LP: {stats.get('lp', 0)}\n"
                
                most_chars = stats.get('most_characters', [])
                if most_chars:
                    context += "모스트 캐릭터:\n"
                    for char in most_chars[:3]:
                        context += f"- {char['name']}: {char['games']}게임, {char['winrate']}% 승률\n"
            else:
                context += f"티어: {stats.get('tier_info', '정보없음')}\n"
                recent_stats = stats.get('recent_stats', {})
                context += f"최근 {recent_stats.get('total_games', 0)}게임 승률: {recent_stats.get('winrate', 0)}%\n"
        
        # AI 분석 요청
        analysis_prompt = f"{닉네임} 플레이어의 전적을 분석해서 플레이 스타일과 개선점을 알려줘. 데비의 밝고 격려하는 톤으로 말해줘."
        response = await generate_ai_response(characters["debi"], analysis_prompt, context)
        
        embed = create_character_embed(
            characters["debi"],
            f"🔍 {닉네임}님 분석 결과", 
            response,
            f"/분석 {닉네임}"
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"분석 중 오류: {e}")
        response = f"분석 중에 문제가 생겼어! 잠시 후 다시 시도해줘!"
        error_embed = create_character_embed(
            characters["debi"], 
            "⚠️ 분석 오류",
            response,
            f"/분석 {닉네임}"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)

@bot.tree.command(name="추천", description="마를렌이 캐릭터를 추천해드려요!")
async def recommend_command(interaction: discord.Interaction, 닉네임: str):
    """AI 추천 명령어"""
    await interaction.response.defer()
    
    # 채널 체크
    if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        # 추천 중 메시지
        recommend_embed = discord.Embed(
            title="🎯 캐릭터 추천 중...",
            description=f"**{닉네임}**님께 어울리는 캐릭터를 찾고 있어요!",
            color=characters["marlene"]["color"]
        )
        recommend_embed.set_author(
            name=characters["marlene"]["name"],
            icon_url=characters["marlene"]["image"]
        )
        await interaction.followup.send(embed=recommend_embed)
        
        # 분석 데이터 수집
        analysis_data = await get_premium_analysis(닉네임)
        
        if not analysis_data:
            response = f"...{닉네임}님의 데이터를 가져오지 못했어. 나중에 다시 시도해봐."
            error_embed = create_character_embed(
                characters["marlene"], 
                "⚠️ 추천 실패",
                response,
                f"/추천 {닉네임}"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return
        
        # AI 추천 컨텍스트 생성
        context = f"플레이어: {닉네임}\n"
        
        stats = analysis_data['stats']
        if stats.get('success'):
            if stats.get('source') == 'dakgg':
                context += f"현재 티어: {stats.get('tier_info', '정보없음')}\n"
                most_chars = stats.get('most_characters', [])
                if most_chars:
                    context += "주로 플레이하는 캐릭터:\n"
                    for char in most_chars[:3]:
                        context += f"- {char['name']}: {char['games']}게임, {char['winrate']}% 승률\n"
            else:
                context += f"현재 티어: {stats.get('tier_info', '정보없음')}\n"
                recent_stats = stats.get('recent_stats', {})
                context += f"최근 승률: {recent_stats.get('winrate', 0)}%\n"
        
        # AI 추천 요청
        recommend_prompt = f"{닉네임} 플레이어의 플레이 패턴을 보고 새로운 캐릭터를 추천해줘. 마를렌의 차갑지만 배려심 있는 톤으로 이유와 함께 설명해줘."
        response = await generate_ai_response(characters["marlene"], recommend_prompt, context)
        
        embed = create_character_embed(
            characters["marlene"],
            f"🎯 {닉네임}님께 추천하는 캐릭터",
            response,
            f"/추천 {닉네임}"
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"추천 중 오류: {e}")
        response = f"...추천을 준비하다가 문제가 생겼어. 잠시 후에 다시 물어봐."
        error_embed = create_character_embed(
            characters["marlene"], 
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
    if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
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
        
        # 예측 컨텍스트 생성
        context = f"플레이어: {닉네임}\n"
        
        if stats.get('success'):
            if stats.get('source') == 'dakgg':
                context += f"현재 티어: {stats.get('tier_info', '정보없음')}\n"
                context += f"현재 MMR: {stats.get('mmr', 0)}\n"
                context += f"현재 LP: {stats.get('lp', 0)}\n"
                
                most_chars = stats.get('most_characters', [])
                if most_chars:
                    context += f"모스트 캐릭터: {most_chars[0]['name']} ({most_chars[0]['winrate']}% 승률)\n"
            else:
                context += f"현재 티어: {stats.get('tier_info', '정보없음')}\n"
                recent_stats = stats.get('recent_stats', {})
                context += f"최근 승률: {recent_stats.get('winrate', 0)}%\n"
                context += f"평균 순위: {recent_stats.get('avg_rank', 0):.1f}\n"
        
        # AI 예측 요청
        predict_prompt = f"{닉네임} 플레이어의 현재 실력과 최근 퍼포먼스를 바탕으로 향후 티어 변동을 예측해줘. 데비의 밝고 응원하는 톤으로 조언도 함께 해줘."
        response = await generate_ai_response(characters["debi"], predict_prompt, context)
        
        embed = create_character_embed(
            characters["debi"],
            f"🔮 {닉네임}님의 티어 예측",
            response,
            f"/예측 {닉네임}"
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"예측 중 오류: {e}")
        response = f"예측 중에 문제가 생겼어! 잠시 후 다시 시도해줘!"
        error_embed = create_character_embed(
            characters["debi"], 
            "⚠️ 예측 오류",
            response,
            f"/예측 {닉네임}"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)

@tasks.loop(minutes=30)
async def check_youtube_shorts():
    """YouTube 쇼츠 확인"""
    global last_checked_video_id
    
    if not youtube or not config.ANNOUNCEMENT_CHANNEL_ID:
        return
    
    try:
        # 채널의 최신 동영상 가져오기
        search_response = youtube.search().list(
            part='snippet',
            channelId=ETERNAL_RETURN_CHANNEL_ID,
            maxResults=1,
            order='date',
            type='video'
        ).execute()
        
        if not search_response['items']:
            return
        
        latest_video = search_response['items'][0]
        video_id = latest_video['id']['videoId']
        
        # 새로운 비디오인지 확인
        if last_checked_video_id == video_id:
            return
        
        # 비디오 상세 정보 가져오기
        video_response = youtube.videos().list(
            part='snippet,contentDetails',
            id=video_id
        ).execute()
        
        if not video_response['items']:
            return
        
        video_details = video_response['items'][0]
        duration = video_details['contentDetails']['duration']
        
        # Shorts 확인 (60초 이하)
        if 'PT' in duration and 'M' not in duration:
            seconds = int(duration.replace('PT', '').replace('S', ''))
            if seconds <= 60:
                # 새로운 Shorts 발견
                snippet = latest_video['snippet']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                embed = discord.Embed(
                    title="🎬 새로운 이터널 리턴 쇼츠!",
                    description=f"**{snippet['title']}**\n\n{video_url}",
                    color=0xFF0000
                )
                embed.set_author(name="이터널 리턴 공식 채널")
                
                if 'thumbnails' in snippet:
                    embed.set_image(url=snippet['thumbnails']['medium']['url'])
                
                # 공지 채널에 전송
                channel = bot.get_channel(config.ANNOUNCEMENT_CHANNEL_ID)
                if channel:
                    await channel.send(embed=embed)
                
                last_checked_video_id = video_id
                print(f"✅ 새로운 Shorts 알림 전송: {snippet['title']}")
        
        # 마지막 확인한 비디오 ID 업데이트 (Shorts가 아니어도)
        last_checked_video_id = video_id
        
    except Exception as e:
        print(f"YouTube 확인 중 오류: {e}")

@check_youtube_shorts.before_loop
async def before_check_youtube_shorts():
    await bot.wait_until_ready()

@bot.tree.command(name="채널설정", description="관리자 전용: 공지채널과 대화채널을 설정합니다")
async def set_channels(interaction: discord.Interaction, 공지채널: discord.TextChannel = None, 대화채널: discord.TextChannel = None):
    """채널 설정 명령어 (관리자 전용)"""
    # 관리자 권한 확인
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 이 명령어는 관리자만 사용할 수 있습니다.", ephemeral=True)
        return
    
    result_messages = []
    
    if 공지채널:
        config.ANNOUNCEMENT_CHANNEL_ID = 공지채널.id
        result_messages.append(f"📢 공지채널이 {공지채널.mention}로 설정되었습니다.")
    
    if 대화채널:
        config.CHAT_CHANNEL_ID = 대화채널.id
        result_messages.append(f"💬 대화채널이 {대화채널.mention}로 설정되었습니다.")
    
    if not result_messages:
        result_messages.append("❓ 설정할 채널을 선택해주세요.")
    
    embed = discord.Embed(
        title="⚙️ 채널 설정 완료",
        description="\n".join(result_messages),
        color=characters["debi"]["color"]
    )
    
    await interaction.response.send_message(embed=embed)

def run_bot():
    """봇 실행"""
    if not DISCORD_TOKEN:
        print("❌ Discord 토큰이 설정되지 않았습니다.")
        return
    
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ 봇 실행 실패: {e}")