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
from api_clients import get_simple_player_stats, get_premium_analysis
from ai_utils import create_character_embed

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

def create_main_embed(player_stats, most_char=None, stats=None):
    """일관된 메인 전적 화면 임베드 생성"""
    embed = discord.Embed(
        title=f"{player_stats['nickname']}님의 전적",
        color=0x00D4AA
    )
    embed.set_footer(text="Season 8")
    
    # 기본 정보 추가
    if player_stats.get('tier_info'):
        current_tier = player_stats.get('tier_info', '정보 없음').replace('**', '')
        embed.add_field(
            name="현재 랭크",
            value=f"**{current_tier}**",
            inline=False
        )
    
    # 모스트 캐릭터 정보
    if most_char:
        embed.add_field(
            name="모스트 실험체", 
            value=f"**{most_char['name']}** ({most_char['games']}게임)", 
            inline=True
        )
    elif player_stats.get('most_characters') and len(player_stats['most_characters']) > 0:
        top_char = player_stats['most_characters'][0]
        embed.add_field(
            name="모스트 실험체", 
            value=f"**{top_char['name']}** ({top_char['games']}게임)", 
            inline=True
        )
    
    # 승률 정보
    if stats:
        embed.add_field(
            name="승률", 
            value=f"**{stats.get('winrate', 0):.1f}%**", 
            inline=True
        )
    
    # 티어 이미지 설정
    if player_stats and player_stats.get('tier_image_url'):
        tier_image_raw = player_stats.get('tier_image_url')
        tier_image_url = "https:" + tier_image_raw if tier_image_raw.startswith('//') else tier_image_raw
        embed.set_thumbnail(url=tier_image_url)
    
    # 모스트 캐릭터 아이콘 설정
    char_image_url = None
    if most_char and most_char.get('image_url'):
        char_image_url = "https:" + most_char['image_url'] if most_char['image_url'].startswith('//') else most_char['image_url']
    elif player_stats.get('most_characters') and len(player_stats['most_characters']) > 0:
        top_char = player_stats['most_characters'][0]
        if top_char.get('image_url'):
            char_image_url = "https:" + top_char['image_url'] if top_char['image_url'].startswith('//') else top_char['image_url']
    
    if char_image_url:
        embed.set_author(name=f"Season 8 {player_stats['nickname']}님의 전적", icon_url=char_image_url)
    else:
        embed.set_author(name=f"Season 8 {player_stats['nickname']}님의 전적")
    
    return embed

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
    
    await initialize_youtube()

@bot.event
async def on_message(message):
    """메시지 이벤트 처리"""
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)


class SeasonSelectView(discord.ui.View):
    def __init__(self, player_stats, button_characters, parent_view=None, season_tiers=None):
        super().__init__(timeout=300)
        self.player_stats = player_stats
        self.button_characters = button_characters
        self.parent_view = parent_view
        self.season_tiers = season_tiers or {}
        
        # 시즌 선택 드롭다운 추가 (티어 정보 포함)
        self.add_item(SeasonDropdown(player_stats, button_characters, season_tiers))
    
    def add_back_button(self):
        """메인으로 돌아가기 버튼 추가"""
        back_button = discord.ui.Button(
            label='메인으로', 
            style=discord.ButtonStyle.secondary,
            row=1
        )
        back_button.callback = self.back_to_main
        self.add_item(back_button)
    
    def add_character_button(self):
        """실험체 버튼 추가 (시즌별)"""
        char_button = discord.ui.Button(
            label='실험체', 
            style=discord.ButtonStyle.primary,
            row=1
        )
        char_button.callback = self.show_season_characters
        self.add_item(char_button)
    
    def add_stats_button(self):
        """통계 버튼 추가 (시즌별)"""
        stats_button = discord.ui.Button(
            label='통계', 
            style=discord.ButtonStyle.secondary,
            row=1
        )
        stats_button.callback = self.show_season_stats
        self.add_item(stats_button)
    
    async def show_season_stats(self, interaction: discord.Interaction):
        """선택된 시즌의 통계 표시"""
        # 현재 선택된 시즌 ID와 이름 가져오기
        current_season_data = getattr(self, '_current_season_data', None)
        if not current_season_data:
            # 기본값으로 현재 시즌 사용
            current_season_data = {
                'season_id': 33,
                'season_name': 'Season 8'
            }
        
        await interaction.response.defer()
        
        try:
            from api_clients import get_season_stats_from_dakgg
            season_stats = await get_season_stats_from_dakgg(
                self.player_stats['nickname'], 
                current_season_data['season_id']
            )
            
            embed = discord.Embed(
                title=f"{self.player_stats['nickname']}님의 {current_season_data['season_name']} 통계",
                color=0xE67E22
            )
            embed.set_footer(text=current_season_data['season_name'])
            
            if season_stats and season_stats['total_games'] > 0:
                embed.add_field(
                    name="게임 수",
                    value=f"{season_stats['total_games']}게임",
                    inline=True
                )
                embed.add_field(
                    name="승률",
                    value=f"{season_stats['winrate']:.1f}%\n({season_stats['wins']}승)",
                    inline=True
                )
                embed.add_field(
                    name="평균 순위",
                    value=f"{season_stats['avg_rank']:.1f}등",
                    inline=True
                )
                embed.add_field(
                    name="평균 킬",
                    value=f"{season_stats['avg_kills']:.1f}킬",
                    inline=True
                )
                embed.add_field(
                    name="평균 팀킬",
                    value=f"{season_stats['avg_team_kills']:.1f}킬",
                    inline=True
                )
                embed.add_field(
                    name="2등/3등",
                    value=f"{season_stats['top2']}회 / {season_stats['top3']}회",
                    inline=True
                )
            else:
                embed.add_field(
                    name="통계 정보",
                    value="해당 시즌 데이터가 없습니다.",
                    inline=False
                )
            
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            print(f"❌ 시즌별 통계 표시 실패: {e}")
            embed = discord.Embed(
                title=f"{self.player_stats['nickname']}님의 {current_season_data['season_name']} 통계",
                description="통계 데이터를 불러올 수 없습니다.",
                color=0xE67E22
            )
            embed.set_footer(text=current_season_data['season_name'])
            await interaction.edit_original_response(embed=embed, view=self)
    
    async def show_season_characters(self, interaction: discord.Interaction):
        """선택된 시즌의 실험체 목록 표시"""
        # 현재 선택된 시즌 ID와 이름 가져오기
        current_season_data = getattr(self, '_current_season_data', None)
        if not current_season_data:
            # 기본값으로 현재 시즌 사용
            current_season_data = {
                'season_id': 33,
                'season_name': 'Season 8'
            }
        
        await interaction.response.defer()
        
        # 먼저 로딩 화면 표시
        loading_embed = discord.Embed(
            title=f"🔄 {current_season_data['season_name']} 실험체 데이터 로딩 중...",
            description="잠시만 기다려주세요!",
            color=0x5865F2
        )
        loading_embed.set_footer(text=f"{current_season_data['season_name']} • 데이터 로딩 중")
        
        # 임시 뷰 (버튼만 있는)
        temp_view = SeasonCharacterView(
            self.player_stats, 
            current_season_data['season_id'], 
            current_season_data['season_name'],
            parent_view=self.parent_view,
            character_data=[]  # 빈 데이터로 시작
        )
        
        await interaction.edit_original_response(embed=loading_embed, view=temp_view)
        
        # 백그라운드에서 데이터 로드
        try:
            print(f"🔍 시즌 {current_season_data['season_id']} 실험체 데이터 로드 시작")
            from api_clients import get_season_characters_from_dakgg
            character_data = await get_season_characters_from_dakgg(
                self.player_stats['nickname'], 
                current_season_data['season_id']
            )
            
            # 데이터 로드 완료 후 새 뷰로 업데이트
            final_view = SeasonCharacterView(
                self.player_stats, 
                current_season_data['season_id'], 
                current_season_data['season_name'],
                parent_view=self.parent_view,
                character_data=character_data
            )
            
            # 최종 임베드
            if character_data and len(character_data) > 0:
                final_embed = discord.Embed(
                    title=f"🎮 {current_season_data['season_name']} | {self.player_stats['nickname']}님의 실험체",
                    description=f"총 {len(character_data)}개 실험체 • 드롭다운에서 선택해보세요",
                    color=0x5865F2
                )
                final_embed.set_footer(text=f"{current_season_data['season_name']} • 랭크 게임 기준")
                print(f"✅ 시즌 {current_season_data['season_id']} 실험체 {len(character_data)}개 로드 완료")
            else:
                final_embed = discord.Embed(
                    title=f"🎮 {current_season_data['season_name']} | {self.player_stats['nickname']}님의 실험체",
                    description="해당 시즌에 플레이한 실험체가 없습니다.",
                    color=0x5865F2
                )
                final_embed.set_footer(text=f"{current_season_data['season_name']} • 데이터 없음")
                print(f"⚠️ 시즌 {current_season_data['season_id']} 실험체 데이터 없음")
            
            # 최종 업데이트
            await interaction.edit_original_response(embed=final_embed, view=final_view)
            
        except Exception as e:
            print(f"❌ 시즌 {current_season_data['season_id']} 실험체 로드 실패: {e}")
            error_embed = discord.Embed(
                title=f"❌ {current_season_data['season_name']} 실험체 로드 실패",
                description="데이터를 가져올 수 없습니다. 잠시 후 다시 시도해주세요.",
                color=0xFF0000
            )
            error_embed.set_footer(text=f"{current_season_data['season_name']} • 오류 발생")
            
            error_view = SeasonCharacterView(
                self.player_stats, 
                current_season_data['season_id'], 
                current_season_data['season_name'],
                parent_view=self.parent_view,
                character_data=None
            )
            
            await interaction.edit_original_response(embed=error_embed, view=error_view)
    
    async def back_to_main(self, interaction: discord.Interaction):
        """메인 전적 화면으로 돌아가기"""
        if self.parent_view:
            # StatsView에서 원본 데이터 가져오기
            most_char = getattr(self.parent_view, 'most_char', None)
            stats = getattr(self.parent_view, 'stats', None)
            # 공통 함수로 메인 임베드 생성 (모든 파라미터 포함)
            embed = create_main_embed(self.player_stats, most_char, stats)
            await interaction.response.edit_message(embed=embed, view=self.parent_view)

class CharacterDropdown(discord.ui.Select):
    def __init__(self, player_stats, detailed_data=None, season_id=33):
        self.player_stats = player_stats
        self.detailed_data = detailed_data
        self.season_id = season_id
        
        # 모스트 캐릭터 데이터 가져오기
        most_chars = []
        if detailed_data and 'most_characters' in detailed_data:
            most_chars = detailed_data['most_characters'][:10]  # 상위 10개만
        else:
            most_chars = player_stats.get('most_characters', [])[:10]
        
        # 드롭다운 옵션 생성
        options = []
        for i, char in enumerate(most_chars):
            rank_num = i + 1
            char_name = char.get('name', '알 수 없음')
            games = char.get('games', 0)
            winrate = char.get('winrate', 0)
            
            options.append(discord.SelectOption(
                label=f"{rank_num}. {char_name}",
                description=f"{games}게임, 승률 {winrate:.1f}%",
                value=str(i)
            ))
        
        # 옵션이 없으면 기본 옵션 추가
        if not options:
            options.append(discord.SelectOption(
                label="데이터 없음",
                description="실험체 데이터를 찾을 수 없습니다",
                value="none"
            ))
        
        super().__init__(
            placeholder="실험체를 선택하세요...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.values[0] == "none":
            embed = discord.Embed(
                title=f"{self.player_stats['nickname']}님의 실험체 정보",
                description="실험체 데이터를 찾을 수 없습니다.",
                color=0x5865F2
            )
            embed.set_footer(text="Season 8")
            await interaction.edit_original_response(embed=embed, view=self.view)
            return
        
        # 선택된 캐릭터 인덱스
        char_index = int(self.values[0])
        
        # 모스트 캐릭터 데이터 가져오기
        most_chars = []
        if self.detailed_data and 'most_characters' in self.detailed_data:
            most_chars = self.detailed_data['most_characters']
        else:
            most_chars = self.player_stats.get('most_characters', [])
        
        if char_index >= len(most_chars):
            await interaction.edit_original_response(embed=embed, view=self.view)
            return
            
        char = most_chars[char_index]
        rank_num = char_index + 1
        
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 실험체 정보",
            color=0x5865F2
        )
        embed.set_footer(text="Season 8")
        
        # 캐릭터 상세 정보
        char_name = char.get('name', '알 수 없음')
        games = char.get('games', 0)
        winrate = char.get('winrate', 0)
        avg_rank = char.get('avg_rank', 0)
        avg_kills = char.get('avg_kills', 0)
        top2 = char.get('top2', 0)
        top3 = char.get('top3', 0)
        
        # 상세 정보를 필드로 추가
        embed.add_field(
            name=f"🏆 {rank_num}위 - {char_name}",
            value=f"**게임 수:** {games}게임\n**승률:** {winrate:.1f}%\n**평균 순위:** {avg_rank:.1f}등\n**평균 킬:** {avg_kills:.1f}킬\n**2등:** {top2}회\n**3등:** {top3}회",
            inline=False
        )
        
        # 캐릭터 이미지 설정
        if char.get('image_url'):
            char_image_url = "https:" + char['image_url'] if char['image_url'].startswith('//') else char['image_url']
            embed.set_image(url=char_image_url)
        
        await interaction.edit_original_response(embed=embed, view=self.view)

class CharacterSelectView(discord.ui.View):
    def __init__(self, player_stats, detailed_data=None, parent_view=None, season_id=33):
        super().__init__(timeout=300)
        self.player_stats = player_stats
        self.detailed_data = detailed_data
        self.parent_view = parent_view
        self.season_id = season_id
        
        # 캐릭터 드롭다운 추가
        self.add_item(CharacterDropdown(player_stats, detailed_data, season_id))
    
    @discord.ui.button(label='메인으로', style=discord.ButtonStyle.secondary, row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.parent_view:
            # StatsView에서 원본 데이터 가져오기
            most_char = getattr(self.parent_view, 'most_char', None)
            stats = getattr(self.parent_view, 'stats', None)
            # 공통 함수로 메인 임베드 생성 (모든 파라미터 포함)
            embed = create_main_embed(self.player_stats, most_char, stats)
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.send_message("메인 뷰를 찾을 수 없습니다.", ephemeral=True)

class SeasonDropdown(discord.ui.Select):
    def __init__(self, player_stats, button_characters, season_tiers=None):
        self.player_stats = player_stats
        self.button_characters = button_characters
        self.season_tiers = season_tiers or {}
        
        # 시즌 ID 매핑 import
        from api_clients import SEASON_IDS
        
        # 시즌 옵션들 정의 (티어 정보 포함)
        options = []
        
        season_info = [
            ("current", "Season 8 (현재 시즌)", "현재 진행 중인 시즌"),
            ("previous", "Season 7 (이전 시즌)", "바로 전 시즌 기록"),
            ("season6", "Season 6", "Season 6 기록"),
            ("season5", "Season 5", "Season 5 기록"),
            ("season4", "Season 4", "Season 4 기록"),
            ("season3", "Season 3", "Season 3 기록"),
            ("season2", "Season 2", "Season 2 기록"),
            ("season1", "Season 1", "Season 1 기록")
        ]
        
        for season_key, season_label, season_desc in season_info:
            season_id = SEASON_IDS.get(season_key)
            tier_info = self.season_tiers.get(season_id, "언랭크")
            
            # 티어 정보가 있으면 라벨에 포함
            if tier_info != "언랭크":
                final_label = f"{season_label} - {tier_info}"
                final_desc = f"{season_desc} (달성: {tier_info})"
            else:
                final_label = f"{season_label} - 언랭크"
                final_desc = f"{season_desc} (미플레이)"
            
            options.append(discord.SelectOption(
                label=final_label,
                description=final_desc,
                value=season_key
            ))
        
        
        super().__init__(
            placeholder="시즌을 선택하세요...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        selected_season = self.values[0]
        
        # 선택된 시즌 정보를 view에 저장
        season_names = {
            "current": "Season 8",
            "previous": "Season 7", 
            "season6": "Season 6",
            "season5": "Season 5",
            "season4": "Season 4",
            "season3": "Season 3",
            "season2": "Season 2",
            "season1": "Season 1"
        }
        
        from api_clients import SEASON_IDS
        season_id = SEASON_IDS.get(selected_season, 33)
        season_name = season_names.get(selected_season, "Season 8")
        
        self.view._current_season_data = {
            'season_id': season_id,
            'season_name': season_name
        }
        
        # 선택한 시즌에 따라 데이터 표시
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 랭크",
            color=0x00D4AA
        )
        
        # 시즌명을 기반으로 푸터 텍스트 설정
        season_names = {
            "current": "Season 8",
            "previous": "Season 7", 
            "season6": "Season 6",
            "season5": "Season 5",
            "season4": "Season 4",
            "season3": "Season 3",
            "season2": "Season 2",
            "season1": "Season 1"
        }
        footer_text = f"{season_names.get(selected_season, 'Season 8')}"
        embed.set_footer(text=footer_text)
        
        if selected_season == "current":
            # 현재 시즌 데이터 (새로운 이미지 URL 사용)
            try:
                from api_clients import get_season_tier_with_image, SEASON_IDS
                
                season_id = SEASON_IDS.get("current")  # 33
                current_season_info, tier_image_url = await get_season_tier_with_image(self.player_stats['nickname'], season_id)
                
                if current_season_info:
                    import re
                    tier_match = re.match(r'(.+?)\s+(\d+)\s+(\d+)\s+RP\s+\(MMR\s+(\d+)\)', current_season_info)
                    if tier_match:
                        tier_name, grade, rp, mmr = tier_match.groups()
                        formatted_current = f"**{tier_name}** `{grade}` **{rp}** `RP` (MMR {mmr})"
                    else:
                        formatted_current = f"**{current_season_info}**"
                        
                    embed.add_field(
                        name="🔥 현재 시즌 (Season 8)",
                        value=formatted_current,
                        inline=False
                    )
                    
                    # 티어 이미지 설정
                    if tier_image_url and tier_image_url.startswith(('http://', 'https://')):
                        embed.set_image(url=tier_image_url)
                        print(f"✅ 현재 시즌 이미지 설정: {tier_image_url}")
                else:
                    # 기존 방식으로 폴백
                    current_tier = self.player_stats.get('tier_info', '정보 없음').replace('**', '')
                    embed.add_field(
                        name="🔥 현재 시즌 (Season 8)",
                        value=f"**{current_tier}**",
                        inline=False
                    )
                    # 기존 이미지 사용
                    if self.player_stats and self.player_stats.get('tier_image_url'):
                        tier_image_raw = self.player_stats.get('tier_image_url')
                        current_tier_image_url = "https:" + tier_image_raw if tier_image_raw.startswith('//') else tier_image_raw
                        embed.set_image(url=current_tier_image_url)
                        
            except Exception as e:
                print(f"현재 시즌 이미지 로드 실패: {e}")
                # 기존 방식으로 폴백
                current_tier = self.player_stats.get('tier_info', '정보 없음').replace('**', '')
                embed.add_field(
                    name="🔥 현재 시즌 (Season 8)",
                    value=f"**{current_tier}**",
                    inline=False
                )
                if self.player_stats and self.player_stats.get('tier_image_url'):
                    tier_image_raw = self.player_stats.get('tier_image_url')
                    current_tier_image_url = "https:" + tier_image_raw if tier_image_raw.startswith('//') else tier_image_raw
                    embed.set_image(url=current_tier_image_url)
                
        elif selected_season == "previous":
            # 이전 시즌 데이터 (티어 이미지 포함)
            try:
                from api_clients import get_season_tier_with_image, SEASON_IDS
                
                season_id = SEASON_IDS.get("previous")  # 31
                prev_season_info, tier_image_url = await get_season_tier_with_image(self.player_stats['nickname'], season_id)
                
                if prev_season_info:
                    import re
                    prev_tier_match = re.match(r'(.+?)\s+(\d+)\s+(\d+)\s+RP\s+\(MMR\s+(\d+)\)', prev_season_info)
                    if prev_tier_match:
                        prev_tier_name, prev_grade, prev_rp, prev_mmr = prev_tier_match.groups()
                        formatted_prev = f"**{prev_tier_name}** `{prev_grade}` **{prev_rp}** `RP` (MMR {prev_mmr})"
                    else:
                        formatted_prev = f"**{prev_season_info}**"
                    
                    embed.add_field(
                        name="📊 이전 시즌 (Season 7)",
                        value=formatted_prev,
                        inline=False
                    )
                    
                    # 티어 이미지 설정
                    if tier_image_url and tier_image_url.startswith(('http://', 'https://')):
                        embed.set_image(url=tier_image_url)
                        print(f"✅ 이전 시즌 이미지 설정: {tier_image_url}")
                else:
                    embed.add_field(
                        name="📊 이전 시즌 (Season 7)",
                        value="`데이터 없음`",
                        inline=False
                    )
                    # 언랭크 이미지 설정
                    embed.set_image(url="https://cdn.dak.gg/assets/er/images/rank/full/0.png")
                    print("✅ 언랭크 이미지 설정 (이전 시즌)")
                    
            except:
                embed.add_field(
                    name="📊 이전 시즌 (Season 7)",
                    value="`데이터 없음`",
                    inline=False
                )
                embed.set_image(url="https://cdn.dak.gg/assets/er/images/rank/full/0.png")
                print("✅ 언랭크 이미지 설정 (예외 처리)")
        else:
            # 다른 시즌들 (티어 이미지 포함)
            try:
                from api_clients import get_season_tier_with_image, SEASON_IDS
                
                season_id = SEASON_IDS.get(selected_season)
                if season_id:
                    # 티어 정보와 이미지 함께 가져오기
                    season_info, tier_image_url = await get_season_tier_with_image(self.player_stats['nickname'], season_id)
                    season_name = selected_season.replace("season", "Season ")
                    
                    if season_info:
                        import re
                        tier_match = re.match(r'(.+?)\s+(\d+)\s+(\d+)\s+RP\s+\(MMR\s+(\d+)\)', season_info)
                        if tier_match:
                            tier_name, grade, rp, mmr = tier_match.groups()
                            formatted_season = f"**{tier_name}** `{grade}` **{rp}** `RP` (MMR {mmr})"
                        else:
                            formatted_season = f"**{season_info}**"
                        
                        embed.add_field(
                            name=f"📈 {season_name}",
                            value=formatted_season,
                            inline=False
                        )
                        
                        # 티어 이미지 설정
                        if tier_image_url and tier_image_url.startswith(('http://', 'https://')):
                            embed.set_image(url=tier_image_url)
                            print(f"✅ {season_name} 이미지 설정: {tier_image_url}")
                            
                    else:
                        embed.add_field(
                            name=f"📈 {season_name}",
                            value="`데이터 없음`",
                            inline=False
                        )
                        # 언랭크 이미지 설정
                        embed.set_image(url="https://cdn.dak.gg/assets/er/images/rank/full/0.png")
                        print(f"✅ {season_name} 언랭크 이미지 설정")
                        
                else:
                    season_name = selected_season.replace("season", "Season ")
                    embed.add_field(
                        name=f"📈 {season_name}",
                        value="`해당 시즌 데이터는 아직 지원되지 않습니다`",
                        inline=False
                    )
            except Exception as e:
                season_name = selected_season.replace("season", "Season ")
                embed.add_field(
                    name=f"📈 {season_name}",
                    value="`데이터 조회 중 오류 발생`",
                    inline=False
                )
        
        await interaction.edit_original_response(embed=embed, view=self.view)

class SeasonCharacterView(discord.ui.View):
    """시즌별 실험체 선택 뷰"""
    def __init__(self, player_stats, season_id, season_name, parent_view=None, character_data=None, parent_interaction=None):
        super().__init__(timeout=300)
        self.player_stats = player_stats
        self.season_id = season_id
        self.season_name = season_name
        self.parent_view = parent_view
        self.character_data = character_data
        self.parent_interaction = parent_interaction # 상호작용 객체 저장
        
        if character_data:
            dropdown = LoadedCharacterDropdown(player_stats, season_id, season_name, character_data)
        else:
            # 데이터가 없으면 로딩 상태를 표시하지 않고 바로 에러 처리 또는 안내
            dropdown = discord.ui.Select(placeholder="데이터를 불러올 수 없습니다.", options=[discord.SelectOption(label="오류", value="error")])

        self.add_item(dropdown)
        self.add_navigation_buttons()
    
    def add_navigation_buttons(self):
        """네비게이션 버튼들 추가"""
        back_button = discord.ui.Button(
            emoji="◀️", 
            label="시즌 선택",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        back_button.callback = self.go_back_to_season_select
        self.add_item(back_button)
        
        main_button = discord.ui.Button(
            emoji="🏠", 
            label="메인",
            style=discord.ButtonStyle.primary,
            row=1
        )
        main_button.callback = self.back_to_main
        self.add_item(main_button)
    
    async def go_back_to_season_select(self, interaction: discord.Interaction):
        """시즌 선택 화면으로 돌아가기"""
        await interaction.response.defer()
        nickname = self.player_stats['nickname']
        
        # 새로운 시즌 선택 화면을 생성하여 표시
        from api_clients import get_player_season_list_simple
        season_data = await get_player_season_list_simple(nickname)
        if not season_data:
            await interaction.edit_original_response(content="플레이어의 시즌 정보를 다시 가져올 수 없습니다.", embed=None, view=None)
            return

        available_seasons = season_data.get('playerSeasons', []) + season_data.get('playerSeasonOverviews', [])
        available_seasons = sorted(
            list({s['seasonId']: s for s in available_seasons if s.get('seasonId')}.values()),
            key=lambda x: x.get('seasonId', 0), 
            reverse=True
        )

        season_embed = discord.Embed(
            title=f"🎮 {nickname}님의 시즌 선택",
            description=f"{len(available_seasons)}개 시즌에서 플레이 기록을 찾았어요!",
            color=0x5865F2
        )
        view = SeasonSelectView(nickname, available_seasons)
        await interaction.edit_original_response(embed=season_embed, view=view)

    async def back_to_main(self, interaction: discord.Interaction):
        """메인 화면으로 돌아가기 (현재 시즌 전적)"""
        await interaction.response.defer()
        await stats_search_logic(interaction, self.player_stats['nickname'], selected_season_id=33)

class SeasonCharacterDropdown(discord.ui.Select):
    """시즌별 실험체 드롭다운"""
    def __init__(self, player_stats, season_id, season_name):
        self.player_stats = player_stats
        self.season_id = season_id  
        self.season_name = season_name
        self.character_data = None
        self.is_loading = True
        
        super().__init__(
            placeholder=f"{season_name} 실험체를 로딩 중...",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(
                label="로딩 중...",
                description="데이터를 가져오는 중입니다",
                value="loading"
            )]
        )
        
        # 비동기로 데이터 로드 시작
        import asyncio
        try:
            task = asyncio.create_task(self.load_character_data())
            print(f"🚀 비동기 태스크 생성 완료: {task}")
        except Exception as e:
            print(f"❌ 비동기 태스크 생성 실패: {e}")
            # 폴백: 즉시 실행
            import asyncio
            loop = asyncio.get_event_loop()
            loop.create_task(self.load_character_data())
    
    async def load_character_data(self):
        """시즌별 실험체 데이터 로드"""
        try:
            print(f"🔍 시즌 {self.season_id} ({self.season_name}) 실험체 데이터 로드 시작")
            print(f"🔍 player_stats 키들: {list(self.player_stats.keys()) if self.player_stats else 'None'}")
            
            # 현재 시즌(33) 판별 - player_stats의 most_characters 사용
            if self.season_id == 33:
                print(f"✨ 현재 시즌 {self.season_id} - most_characters 데이터 사용")
                most_chars = self.player_stats.get('most_characters', [])
                if most_chars:
                    print(f"🔍 most_characters 개수: {len(most_chars)}")
                    print(f"🔍 첫 번째 캐릭터 구조: {most_chars[0].keys()}")
                    self.character_data = most_chars
                    print(f"✅ 현재 시즌 데이터 로드 완료: {len(self.character_data)}개 캐릭터")
                else:
                    print(f"⚠️ most_characters 데이터 없음")
                    self.character_data = []
            else:
                # 다른 시즌은 API 호출
                print(f"🌐 시즌 {self.season_id} API 호출 시작")
                from api_clients import get_season_characters_from_dakgg
                self.character_data = await get_season_characters_from_dakgg(
                    self.player_stats['nickname'], 
                    self.season_id
                )
                if self.character_data:
                    print(f"✅ API 호출 성공: {len(self.character_data)}개 캐릭터")
                else:
                    print(f"❌ API 호출 결과 데이터 없음")
                    self.character_data = []
            
            self.is_loading = False
            
            # 로딩 완료 후 새로운 View로 업데이트 (Discord Select 제한 때문)
            print(f"🔄 로딩 완료, 새로운 View로 업데이트 시작")
            
            # 현재 View 찾기
            current_view = self.view
            if current_view:
                # 새로운 SeasonCharacterView 생성 (데이터 포함)
                new_view = SeasonCharacterView(
                    self.player_stats, 
                    self.season_id, 
                    self.season_name, 
                    parent_view=current_view.parent_view,
                    character_data=self.character_data
                )
                
                # 임베드 업데이트
                if self.character_data and len(self.character_data) > 0:
                    embed = discord.Embed(
                        title=f"🎮 {self.season_name} | {self.player_stats['nickname']}님의 실험체 정보",
                        description=f"총 {len(self.character_data)}개 실험체 • 드롭다운에서 선택해보세요",
                        color=0x5865F2
                    )
                    embed.set_footer(text=f"{self.season_name} • 랭크 게임 기준")
                    print(f"✅ 시즌 {self.season_id} 실험체 {len(self.character_data)}개 로드 완료")
                else:
                    embed = discord.Embed(
                        title=f"🎮 {self.season_name} | {self.player_stats['nickname']}님의 실험체 정보",
                        description="해당 시즌에 플레이한 실험체가 없습니다.",
                        color=0x5865F2
                    )
                    embed.set_footer(text=f"{self.season_name} • 데이터 없음")
                    print(f"⚠️ 시즌 {self.season_id} 실험체 데이터 없음")
                
                # View 업데이트 시도 (현재 상호작용이 있으면)
                try:
                    # 마지막 상호작용을 찾아서 업데이트
                    # 이는 복잡하므로 일단 로그로 확인
                    print(f"🔄 새 View 생성 완료: {new_view}")
                except Exception as e:
                    print(f"❌ View 업데이트 실패: {e}")
                
        except Exception as e:
            print(f"❌ 시즌 {self.season_id} 실험체 로드 실패: {e}")
            self.options = [discord.SelectOption(
                label="로드 실패",
                description="데이터를 가져올 수 없습니다",
                value="error"
            )]
            self.placeholder = "데이터 로드 실패"
            self.is_loading = False
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # 로딩 중이면 잠시 대기
        if self.is_loading:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"{self.player_stats['nickname']}님의 {self.season_name} 실험체 정보",
                    description="데이터를 로딩 중입니다. 잠시만 기다려주세요...",
                    color=0x5865F2
                ).set_footer(text=self.season_name),
                view=self.view
            )
            return
        
        # 실험체 선택 처리
        if self.values[0] in ["loading", "none", "error"]:
            embed = discord.Embed(
                title=f"{self.player_stats['nickname']}님의 {self.season_name} 실험체 정보",
                description="실험체 데이터를 표시할 수 없습니다.",
                color=0x5865F2
            )
            embed.set_footer(text=self.season_name)
            await interaction.edit_original_response(embed=embed, view=self.view)
            return
        
        # 선택된 캐릭터 표시
        char_index = int(self.values[0])
        if char_index < len(self.character_data):
            char = self.character_data[char_index]
            rank_num = char_index + 1
            
            embed = discord.Embed(
                title=f"🎮 {self.season_name} | {self.player_stats['nickname']}님의 실험체",
                description=f"**{rank_num}위 실험체 상세 정보**",
                color=0x5865F2
            )
            embed.set_footer(text=f"{self.season_name} • 랭크 게임 기준")
            
            # 캐릭터 상세 정보
            embed.add_field(
                name=f"🏆 {char['name']}",
                value=f"**게임 수:** {char['games']}게임\n**승률:** {char['winrate']:.1f}%\n**평균 순위:** {char['avg_rank']:.1f}등\n**평균 킬:** {char['avg_kills']:.1f}킬\n**2등:** {char['top2']}회\n**3등:** {char['top3']}회",
                inline=False
            )
            
            # 캐릭터 이미지 설정
            if char.get('image_url'):
                char_image_url = "https:" + char['image_url'] if char['image_url'].startswith('//') else char['image_url']
                embed.set_image(url=char_image_url)
            
            await interaction.edit_original_response(embed=embed, view=self.view)

class LoadedCharacterDropdown(discord.ui.Select):
    """로딩 완료된 시즌별 실험체 드롭다운"""
    def __init__(self, player_stats, season_id, season_name, character_data):
        self.player_stats = player_stats
        self.season_id = season_id
        self.season_name = season_name
        self.character_data = character_data
        
        # 옵션 생성
        options = []
        if character_data and len(character_data) > 0:
            for i, char in enumerate(character_data[:10]):  # 상위 10개
                rank_num = i + 1
                options.append(discord.SelectOption(
                    label=f"{rank_num}. {char['name']}",
                    description=f"{char['games']}게임, 승률 {char['winrate']:.1f}%",
                    value=str(i)
                ))
            placeholder = f"{season_name} 실험체를 선택하세요..."
        else:
            options.append(discord.SelectOption(
                label="데이터 없음",
                description="해당 시즌 실험체 데이터가 없습니다",
                value="none"
            ))
            placeholder = "실험체 데이터 없음"
        
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.values[0] == "none":
            embed = discord.Embed(
                title=f"{self.player_stats['nickname']}님의 {self.season_name} 실험체 정보",
                description="실험체 데이터를 표시할 수 없습니다.",
                color=0x5865F2
            )
            embed.set_footer(text=self.season_name)
            await interaction.edit_original_response(embed=embed, view=self.view)
            return
        
        # 선택된 캐릭터 표시
        char_index = int(self.values[0])
        if char_index < len(self.character_data):
            char = self.character_data[char_index]
            rank_num = char_index + 1
            
            embed = discord.Embed(
                title=f"🎮 {self.season_name} | {self.player_stats['nickname']}님의 실험체",
                description=f"**{rank_num}위 실험체 상세 정보**",
                color=0x5865F2
            )
            embed.set_footer(text=f"{self.season_name} • 랭크 게임 기준")
            
            # 캐릭터 상세 정보
            embed.add_field(
                name=f"🏆 {char['name']}",
                value=f"**게임 수:** {char['games']}게임\n**승률:** {char['winrate']:.1f}%\n**평균 순위:** {char['avg_rank']:.1f}등\n**평균 킬:** {char['avg_kills']:.1f}킬\n**2등:** {char['top2']}회\n**3등:** {char['top3']}회",
                inline=False
            )
            
            # 캐릭터 이미지 설정
            if char.get('image_url'):
                char_image_url = "https:" + char['image_url'] if char['image_url'].startswith('//') else char['image_url']
                embed.set_image(url=char_image_url)
            
            await interaction.edit_original_response(embed=embed, view=self.view)

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


    @discord.ui.button(label='랭크', style=discord.ButtonStyle.success, row=0)
    async def show_rank(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 랭크",
            color=0x00D4AA
        )
        embed.set_footer(text="Season 8")
        
        # 현재 시즌 랭크 - 폰트 스타일링 개선
        current_tier = self.player_stats.get('tier_info', '정보 없음').replace('**', '')
        
        # 티어명과 숫자/RP를 분리해서 다른 스타일 적용
        import re
        tier_match = re.match(r'(.+?)\s+(\d+)\s+(\d+)\s+RP\s+\(MMR\s+(\d+)\)', current_tier)
        if tier_match:
            tier_name, grade, rp, mmr = tier_match.groups()
            formatted_current = f"**{tier_name}** `{grade}` **{rp}** `RP` (MMR {mmr})"
        else:
            formatted_current = f"**{current_tier}**"
            
        embed.add_field(
            name="현재 시즌 (Season 8)",
            value=formatted_current,
            inline=False
        )
        
        
        # 현재 시즌 티어 이미지를 큰 이미지로 설정
        if self.player_stats and self.player_stats.get('tier_image_url'):
            tier_image_raw = self.player_stats.get('tier_image_url')
            current_tier_image_url = "https:" + tier_image_raw if tier_image_raw.startswith('//') else tier_image_raw
            embed.set_image(url=current_tier_image_url)
        
        # 시즌 티어 정보 미리 가져오기
        try:
            from api_clients import get_player_all_season_tiers
            season_tiers = await get_player_all_season_tiers(self.player_stats['nickname'])
        except:
            season_tiers = {}
        
        # 시즌 선택 버튼 추가 (티어 정보 포함)
        season_view = SeasonSelectView(self.player_stats, self.button_characters, parent_view=self, season_tiers=season_tiers)
        season_view.add_back_button()
        season_view.add_character_button()  # 실험체 버튼 추가
        season_view.add_stats_button()  # 통계 버튼 추가
        await interaction.edit_original_response(embed=embed, view=season_view)


    @discord.ui.button(label='실험체', style=discord.ButtonStyle.primary, row=0)
    async def show_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # 상세 데이터가 없으면 가져오기
        if not self.detailed_data:
            try:
                from api_clients import get_player_stats_from_dakgg
                print(f"🔍 실험체 데이터 로드 시작: {self.player_stats['nickname']}")
                self.detailed_data = await get_player_stats_from_dakgg(self.player_stats['nickname'], detailed=True)
                print(f"🔍 상세 데이터 키: {list(self.detailed_data.keys()) if self.detailed_data else 'None'}")
            except Exception as e:
                print(f"❌ 상세 데이터 로드 실패: {e}")
                embed = discord.Embed(
                    title=f"{self.player_stats['nickname']}님의 실험체 정보",
                    description="실험체 데이터를 로드할 수 없습니다.",
                    color=0x5865F2
                )
                embed.set_footer(text="Season 8")
                await interaction.edit_original_response(embed=embed, view=self)
                return
        
        # 초기 임베드 생성
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 실험체 정보",
            description="드롭다운에서 실험체를 선택해보세요",
            color=0x5865F2
        )
        embed.set_footer(text="Season 8")
        
        # 캐릭터 선택 뷰 생성
        character_view = CharacterSelectView(self.player_stats, self.detailed_data, parent_view=self)
        
        await interaction.edit_original_response(embed=embed, view=character_view)

    @discord.ui.button(label='통계', style=discord.ButtonStyle.secondary, row=0)
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"{self.player_stats['nickname']}님의 게임 통계",
            color=0xE67E22
        )
        # 통계 버튼용 캐릭터
        char_key = self.button_characters["stats"]
        embed.set_author(name=characters[char_key]["name"], icon_url=characters[char_key]["image"])
        embed.set_footer(text="Season 8")
        
        # 통계 정보 표시
        stats = self.stats
        if stats:
            winrate = stats.get('winrate', 0)
            avg_rank = stats.get('avg_rank', 0)
            avg_kills = stats.get('avg_kills', 0)
            
            # 이모지 제거하고 깔끔하게 표시
            embed.add_field(
                name="게임 수",
                value=f"{stats.get('total_games', 0)}게임",
                inline=True
            )
            embed.add_field(
                name="승률",
                value=f"{winrate:.1f}%\n({stats.get('wins', 0)}승)",
                inline=True
            )
            embed.add_field(
                name="평균 순위",
                value=f"{avg_rank:.1f}등",
                inline=True
            )
            embed.add_field(
                name="평균 킬",
                value=f"{avg_kills:.1f}킬",
                inline=True
            )
            embed.add_field(
                name="평균 팀킬",
                value=f"{stats.get('avg_team_kills', 0):.1f}킬",
                inline=True
            )
            embed.add_field(
                name="MMR",
                value=f"{self.player_stats.get('mmr', 0)}",
                inline=True
            )
        else:
            embed.add_field(
                name="통계 정보",
                value="데이터가 없습니다.",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='메인으로', style=discord.ButtonStyle.gray, row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 공통 함수로 메인 임베드 생성
        embed = create_main_embed(self.player_stats, self.most_char, self.stats)
        await interaction.response.edit_message(embed=embed, view=self)

class SeasonSelectDropdown(discord.ui.Select):
    """시즌 선택 드롭다운 (플레이어가 실제로 플레이한 시즌만)"""
    def __init__(self, nickname: str, available_seasons: list):
        self.nickname = nickname
        
        # 시즌 이름 매핑 (확장)
        season_name_map = {
            33: ("현재 시즌 (Season 8)", "현재 진행중인 시즌", "🏆"),
            32: ("Season 7-8 프리시즌", "시즌 7과 8 사이", "🌟"),
            31: ("Season 7", "이전 시즌", "🥈"),
            30: ("Season 6", "Season 6", "🥉"),
            29: ("Season 5", "Season 5", "📊"),
            28: ("Season 6-7 프리시즌", "시즌 6과 7 사이", "🌟"),
            27: ("Season 5-6 프리시즌", "시즌 5와 6 사이", "🌟"),
            26: ("Season 4-5 프리시즌", "시즌 4와 5 사이", "🌟"),
            25: ("Season 3-4 프리시즌", "시즌 3과 4 사이", "🌟"),
            24: ("Season 2-3 프리시즌", "시즌 1과 2 사이", "🌟"),
            23: ("Season 1-2 프리시즌", "시즌 1과 2 사이", "🌟"),
            22: ("Season 1 이전 프리시즌", "Season 1 이전", "🌟"),
            21: ("Season 4", "Season 4", "📊"),
            20: ("Season 3", "Season 3", "📊"),
            19: ("Season 2", "Season 2", "📊"),
            18: ("Season 1", "Season 1", "📊"),
            17: ("얼리액세스", "얼리액세스 시즌", "🚀"),
            16: ("알파 테스트", "알파 테스트 시즌", "🚀"),
            15: ("베타 테스트", "베타 테스트 시즌", "🚀"),
        }
        
        # 사용 가능한 시즌만 옵션으로 생성
        options = []
        for season_data in available_seasons:
            season_id = season_data['seasonId']
            if season_id in season_name_map:
                label, description, emoji = season_name_map[season_id]
            else:
                # 알려지지 않은 시즌 ID 처리
                label = f"시즌 {season_id}"
                description = f"시즌 ID {season_id}"
                emoji = "❓"
                print(f"⚠️ 알려지지 않은 시즌 ID: {season_id}")
            
            # MMR이나 게임 수 정보가 있으면 표시
            mmr = season_data.get('mmr')
            games = season_data.get('play', 0)
            tier_id = season_data.get('tierId')
            
            if mmr and mmr > 0:
                description += f" (MMR: {mmr})"
            elif games and games > 0:
                description += f" ({games}게임)"
            elif tier_id:
                description += f" (티어 ID: {tier_id})"
            else:
                description += " (데이터 있음)"
            
            options.append(discord.SelectOption(
                label=label,
                description=description,
                value=str(season_id),
                emoji=emoji
            ))
        
        # 옵션이 없으면 기본 메시지
        if not options:
            options = [discord.SelectOption(
                label="사용 가능한 시즌이 없습니다",
                description="이 플레이어의 시즌 데이터를 찾을 수 없습니다",
                value="0"
            )]
        
        super().__init__(
            placeholder="시즌을 선택하세요...",
            min_values=1,
            max_values=1,
            options=options[:25]  # Discord 최대 25개 제한
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_season_id = int(self.values[0])
        
        if selected_season_id == 0:
            await interaction.response.send_message("❌ 선택 가능한 시즌이 없습니다.", ephemeral=True)
            return
        
        # 선택된 시즌으로 전적 검색 실행
        await interaction.response.defer()
        await stats_search_logic(interaction, self.nickname, selected_season_id)

class SeasonSelectView(discord.ui.View):
    """시즌 선택 뷰"""
    def __init__(self, nickname: str, available_seasons: list):
        super().__init__(timeout=300)
        self.add_item(SeasonSelectDropdown(nickname, available_seasons))

class StatsModal(discord.ui.Modal, title='🔍 전적 검색'):
    """전적 검색 모달 (닉네임 입력용)"""
    def __init__(self):
        super().__init__()

    nickname = discord.ui.TextInput(
        label='닉네임',
        placeholder='검색할 플레이어 닉네임을 입력하세요...',
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # 채널 체크
        if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
            await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return
        
        nickname = self.nickname.value.strip()
        
        try:
            # 플레이어 데이터 먼저 조회해서 사용 가능한 시즌 확인
            searching_embed = discord.Embed(
                title="🔍 플레이어 검색 중...",
                description=f"**{nickname}**님의 시즌 정보를 조회하고 있어요!",
                color=characters["debi"]["color"]
            )
            searching_embed.set_author(
                name=characters["debi"]["name"],
                icon_url=characters["debi"]["image"]
            )
            await interaction.followup.send(embed=searching_embed)
            
            # 플레이어 시즌 목록만 간단히 조회
            from api_clients import get_player_season_list_simple
            season_data = await get_player_season_list_simple(nickname)
            
            if not season_data:
                error_embed = create_character_embed(
                    characters["debi"], 
                    "⚠️ 플레이어 검색 실패",
                    f"**{nickname}**님의 전적을 찾을 수 없어!",
                    f"/전적 {nickname}"
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            
            # 사용 가능한 시즌 목록 추출
            available_seasons = []
            
            print(f"🔍 시즌 데이터 분석 시작 - {nickname}")
            print(f"🔍 시즌 데이터 키들: {list(season_data.keys())}")
            
            # playerSeasons에서 시즌 정보 가져오기
            if 'playerSeasons' in season_data:
                player_seasons = season_data['playerSeasons']
                print(f"🔍 playerSeasons 개수: {len(player_seasons)}")
                for i, season in enumerate(player_seasons):
                    season_id = season.get('seasonId')
                    print(f"  시즌 {i+1}: ID={season_id}, MMR={season.get('mmr')}, TierID={season.get('tierId')}")
                    # 유효한 시즌 ID만 추가 (0 제외, None 제외)
                    if season_id and season_id > 0:
                        available_seasons.append(season)
                        print(f"    ✅ 추가됨")
                    else:
                        print(f"    ❌ 제외됨 (잘못된 시즌 ID: {season_id})")
            else:
                print("⚠️ playerSeasons 키 없음")
            
            # playerSeasonOverviews에서 게임 데이터가 있는 시즌들
            if 'playerSeasonOverviews' in season_data:
                season_overviews = season_data['playerSeasonOverviews']
                print(f"🔍 playerSeasonOverviews 개수: {len(season_overviews)}")
                season_ids_added = {s.get('seasonId') for s in available_seasons}
                for i, overview in enumerate(season_overviews):
                    season_id = overview.get('seasonId')
                    play_count = overview.get('play', 0)
                    print(f"  시즌개요 {i+1}: ID={season_id}, 플레이={play_count}게임")
                    if season_id not in season_ids_added and play_count > 0:
                        available_seasons.append(overview)
                        season_ids_added.add(season_id)
                        print(f"    ✅ 추가됨")
            else:
                print("⚠️ playerSeasonOverviews 키 없음")
                
            print(f"🔍 최종 사용 가능한 시즌 개수: {len(available_seasons)}")
            
            # 시즌 ID 기준으로 정렬 (최신 시즌부터)
            available_seasons.sort(key=lambda x: x.get('seasonId', 0), reverse=True)
            
            if not available_seasons:
                error_embed = create_character_embed(
                    characters["debi"], 
                    "⚠️ 사용 가능한 시즌 없음",
                    f"**{nickname}**님의 시즌 데이터를 찾을 수 없어요!"
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            
            # 시즌 선택 화면 표시
            season_embed = discord.Embed(
                title=f"🎮 {nickname}님의 시즌 선택",
                description=f"{len(available_seasons)}개 시즌에서 플레이 기록을 찾았어요! 조회하고 싶은 시즌을 선택해주세요.",
                color=0x5865F2
            )
            season_embed.set_author(
                name=characters["debi"]["name"],
                icon_url=characters["debi"]["image"]
            )
            
            view = SeasonSelectView(nickname, available_seasons)
            await interaction.followup.send(embed=season_embed, view=view)
            
        except Exception as e:
            print(f"플레이어 검색 중 오류: {e}")
            error_embed = create_character_embed(
                characters["debi"], 
                "⚠️ 검색 오류",
                f"**{nickname}**님 검색 중 오류가 발생했어! 잠시 후 다시 시도해줘!",
                f"/전적 {nickname}"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

@bot.tree.command(name="전적", description="이터널 리턴 플레이어 전적을 검색해요!")
async def stats_command(interaction: discord.Interaction):
    """전적 검색 슬래시 커맨드"""
    modal = StatsModal()
    await interaction.response.send_modal(modal)

async def stats_search_logic(interaction: discord.Interaction, 닉네임: str, selected_season_id: int = None):
    """전적 검색 로직 (모달과 일반 명령어에서 공통 사용)"""
    # 채널 체크
    if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
        await interaction.followup.send("❌ 이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        # defer()가 호출된 상태이므로 edit_original_response 사용
        searching_embed = discord.Embed(
            title="🔍 전적 검색 중...",
            description=f"**{닉네임}**님의 전적을 검색하고 있어요!",
            color=characters["debi"]["color"]
        )
        await interaction.edit_original_response(embed=searching_embed, view=None, content=None)
        
        # 시즌 ID가 33이거나 None이면 현재 시즌 로직 실행
        if selected_season_id is None or selected_season_id == 33:
            from api_clients import get_player_stats_from_dakgg
            player_stats = await get_player_stats_from_dakgg(닉네임)
            
            if player_stats is None:
                error_embed = create_character_embed(characters["debi"], "⚠️ 전적 검색 실패", f"**{닉네임}**님의 전적을 찾을 수 없어!")
                await interaction.edit_original_response(embed=error_embed)
                return

            stats = player_stats.get('stats', {})
            most_chars = player_stats.get('most_characters', [])
            most_char = most_chars[0] if most_chars else None
        
            view = StatsView(player_stats, most_char, stats)
            basic_embed = create_main_embed(player_stats, most_char, stats)
            debi_message = f"와! {닉네임}님의 전적 찾았어! 여기 있어~"

            await interaction.edit_original_response(content=debi_message, embed=basic_embed, view=view)

        else:
            # 다른 시즌이 선택된 경우
            season_name_map = { 31: "Season 7", 30: "Season 6", 29: "Season 5" }
            season_name = season_name_map.get(selected_season_id, f"Season {selected_season_id}")
            
            from api_clients import get_season_characters_from_dakgg, get_player_stats_from_dakgg
            base_player_stats = await get_player_stats_from_dakgg(닉네임)
            if not base_player_stats:
                 error_embed = create_character_embed(characters["debi"], "⚠️ 플레이어 정보 조회 실패", f"**{닉네임}**님의 기본 정보를 찾을 수 없어!")
                 await interaction.edit_original_response(embed=error_embed)
                 return

            season_characters = await get_season_characters_from_dakgg(닉네임, selected_season_id)
            
            if not season_characters:
                error_embed = create_character_embed(characters["debi"], f"⚠️ {season_name} 데이터 없음", f"**{닉네임}**님의 {season_name} 전적을 찾을 수 없어!")
                await interaction.edit_original_response(embed=error_embed)
                return
            
            season_view = SeasonCharacterView(
                base_player_stats, 
                selected_season_id, 
                season_name,
                character_data=season_characters,
                parent_interaction=interaction
            )
            
            season_embed = discord.Embed(
                title=f"🎮 {season_name} | {닉네임}님의 실험체",
                description=f"총 {len(season_characters)}개 실험체 • 드롭다운에서 선택해보세요",
                color=0x5865F2
            )
            season_embed.set_footer(text=f"{season_name} • 랭크/일반 게임 기준")
            
            await interaction.edit_original_response(embed=season_embed, view=season_view)
        
    except Exception as e:
        print(f"전적 검색 중 오류: {e}")
        error_embed = create_character_embed(characters["debi"], "⚠️ 전적 검색 오류", f"**{닉네임}**님의 전적 검색 중 오류가 발생했어!")
        try:
            await interaction.edit_original_response(embed=error_embed, view=None)
        except discord.NotFound:
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
            if seconds <= 180:
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

if __name__ == "__main__":
    run_bot()
