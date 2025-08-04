import discord
import asyncio
from discord.ext import commands
from run.config import characters, DISCORD_TOKEN
from run import config
from run.api_clients import (
    get_player_basic_data, 
    get_player_season_data, 
    get_player_played_seasons,
    initialize_game_data,
    game_data # 중앙 캐시 객체 임포트
)
from run.graph_generator import save_mmr_graph_to_file
import os
import tempfile
from run import youtube_service

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} 봇이 시작되었습니다!')
    try:
        # 명령어 동기화
        await bot.tree.sync()
        print("명령어 동기화 완료.")

        # 중앙 데이터 초기화 함수 호출
        await initialize_game_data()
        await youtube_service.initialize_youtube()
        youtube_service.set_bot_instance(bot)
        youtube_service.check_new_videos.start()
    except Exception as e:
        print(f"CRITICAL: 데이터 초기화 중 봇 시작 실패: {e}")
        # 필요하다면 여기서 봇을 종료하거나, 관리자에게 알림을 보낼 수 있습니다.
        await bot.close()

def create_embed(player_data):
    # 1. RANK 정보를 타이틀로 설정
    rank_info = player_data.get('tier_info', 'Unranked')
    
    # 2. description에 순위 정보 추가
    description = ""
    rank = player_data.get('rank', 0)
    rank_percent = player_data.get('rank_percent', 0)
    if rank > 0:
        description = f"{rank:,}위 상위 {rank_percent}%"
    
    embed = discord.Embed(
        title=rank_info,
        description=description,
        color=0x00D4AA
    )
    
    # 3. 닉네임과 모스트 실험체는 set_author로 표시
    nickname = player_data.get('nickname', 'Unknown Player')
    author_icon_url = None  # Embed.Empty 대신 None 사용
    if player_data.get('most_characters'):
        most_char = player_data['most_characters'][0]
        if most_char.get('image_url'):
            author_icon_url = most_char['image_url']
    embed.set_author(name=nickname, icon_url=author_icon_url)

    # 3. 시즌 정보 푸터
    season_name = game_data.get_season_name(player_data['season_id'])
    embed.set_footer(text=season_name)
    
    # 4. 티어 이미지는 썸네일로 유지
    if player_data.get('tier_image_url'):
        embed.set_thumbnail(url=player_data['tier_image_url'])

    # 5. 나머지 정보는 필드로 추가
    if player_data.get('most_characters'):
        top_char = player_data['most_characters'][0]
        embed.add_field(name="가장 많이 플레이한 실험체", value=f"**{top_char['name']}** ({top_char['games']}게임)", inline=True)
    
    if player_data.get('stats'):
        stats = player_data['stats']
        embed.add_field(name="승률", value=f"**{stats.get('winrate', 0):.1f}%**", inline=True)
    
    return embed

def create_character_embed(character, title, description, command_used=""):
    embed = discord.Embed(title=title, description=description, color=character.get("color", 0xFF0000))
    if command_used:
        embed.set_footer(text=f"사용된 명령어: {command_used}")
    return embed

class StatsView(discord.ui.View):
    def __init__(self, player_data, played_seasons=None):
        super().__init__(timeout=300)
        self.player_data = player_data
        self.played_seasons = played_seasons or []
        self.show_preseason = False  # False: 정식시즌, True: 프리시즌

    @discord.ui.button(label='실험체', style=discord.ButtonStyle.primary)
    async def show_characters(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title=f"{self.player_data['nickname']}님의 실험체", color=0x5865F2)
        most_chars = self.player_data.get('most_characters', [])
        if most_chars:
            for i, char in enumerate(most_chars[:10]):  # 10개까지 표시
                mmr_gain = char.get('mmr_gain', 0)
                rp_text = f"{mmr_gain:+d} RP" if mmr_gain != 0 else "±0 RP"
                rp_emoji = "📈" if mmr_gain > 0 else "📉" if mmr_gain < 0 else "➖"
                avg_rank = char.get('avg_rank', 0)
                
                embed.add_field(
                    name=f"{i+1}. {char['name']}", 
                    value=f"{char['games']}게임, {char['winrate']:.1f}% 승률\n평균 {avg_rank:.1f}등, {rp_emoji} {rp_text}", 
                    inline=True
                )
        else:
            embed.add_field(name="실험체 정보", value="데이터가 없습니다.", inline=False)
        await interaction.response.edit_message(embed=embed, view=self, attachments=[])

    @discord.ui.button(label='통계', style=discord.ButtonStyle.secondary)
    async def show_stats(self, interaction: discord.Interaction, button):
        await interaction.response.defer() 
        
        embed = discord.Embed(title=f"{self.player_data['nickname']}님의 통계", color=0xE67E22)
        stats = self.player_data.get('stats', {})
        file_attachment = None
        
        # MMR 그래프 생성
        mmr_history = self.player_data.get('mmr_history', [])
        if mmr_history and len(mmr_history) >= 2:
            try:
                # 임시 파일에 그래프 저장
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    graph_path = save_mmr_graph_to_file(
                        mmr_history, 
                        self.player_data.get('nickname', '플레이어'),
                        tmp_file.name
                    )
                    
                if graph_path and os.path.exists(graph_path):
                    file_attachment = discord.File(graph_path, filename="mmr_graph.png")
                    embed.set_image(url="attachment://mmr_graph.png")
            except Exception as e:
                print(f"그래프 생성 오류: {e}")
        
        if stats:
            embed.add_field(name="게임 수", value=f"{stats.get('total_games', 0)}게임", inline=True)
            embed.add_field(name="승률", value=f"{stats.get('winrate', 0):.1f}%", inline=True)
            embed.add_field(name="평균 순위", value=f"{stats.get('avg_rank', 0):.1f}등", inline=True)
            embed.add_field(name="평균 킬", value=f"{stats.get('avg_kills', 0):.1f}킬", inline=True)
            embed.add_field(name="평균 어시", value=f"{stats.get('avg_assists', 0):.1f}어시", inline=True)
            embed.add_field(name="KDA", value=f"**{stats.get('kda', 0):.2f}**", inline=True)
            embed.add_field(name="평균 딜량", value=f"{stats.get('avg_damage', 0):,.0f}", inline=True)
            embed.add_field(name="Top2 비율", value=f"{stats.get('top2_rate', 0):.1f}%", inline=True)
            embed.add_field(name="Top3 비율", value=f"{stats.get('top3_rate', 0):.1f}%", inline=True)
            
            # 듀오 파트너 통계 추가
            duo_partners = self.player_data.get('duo_partners', [])
            if duo_partners:
                # 파트너 정보를 한 줄로 묶어서 표시 (줄 간격 추가)
                partner_info_str = "\n\u200b\n".join([
                    f"**{p['nickname']}**: {p['games']}게임, {p['winrate']:.1f}% 승률, 평점 {p['avg_rank']:.1f}등"
                    for p in duo_partners
                ])
                embed.add_field(
                    name="\n\u200b\n함께 플레이 (최근 20 매치)",
                    value=f"\u200b\n{partner_info_str}",
                    inline=False
                )
        else:
            embed.add_field(name="통계 정보", value="데이터가 없습니다.", inline=False)
        
        # 파일과 함께 응답
        if file_attachment:
            await interaction.edit_original_response(embed=embed, attachments=[file_attachment], view=self)
            # 임시 파일 정리
            try:
                os.unlink(graph_path)
            except:
                pass
        else:
            await interaction.edit_original_response(embed=embed, view=self)

    def _is_preseason(self, season_name: str) -> bool:
        """시즌명으로 프리시즌 여부 판단"""
        return "프리" in season_name or "Pre" in season_name

    def _filter_seasons_by_type(self):
        """현재 모드(정식/프리시즌)에 맞는 시즌만 필터링"""
        if not self.played_seasons:
            return []
        
        filtered = []
        for season in self.played_seasons:
            is_preseason = self._is_preseason(season['name'])
            if self.show_preseason == is_preseason:
                filtered.append(season)
        
        return filtered[:25]  # 최대 25개로 제한

    def create_season_select(self):
        filtered_seasons = self._filter_seasons_by_type()
        
        if not filtered_seasons:
            return None

        options = []        
        for season in filtered_seasons:
            label = f"{season['name']}" + (" (현재)" if season.get('is_current') else "")
            emoji = "🔥" if season.get('is_current') else None
            options.append(discord.SelectOption(label=label, value=str(season['id']), emoji=emoji))
        
        if not options:
            return None

        placeholder = "프리시즌별 전적 보기..." if self.show_preseason else "시즌별 전적 보기..."
        select = discord.ui.Select(placeholder=placeholder, options=options)
        select.callback = self.season_select_callback
        return select
    
    async def season_select_callback(self, interaction):
        await interaction.response.defer()
        season_id = int(interaction.data['values'][0])
        
        season_player_data = await get_player_season_data(self.player_data['nickname'], season_id)
        
        if season_player_data:
            self.player_data = season_player_data
            embed = create_embed(season_player_data)
        else:
            season_name = game_data.get_season_name(season_id)
            embed = discord.Embed(
                title=f"{self.player_data['nickname']}님의 {season_name} 전적",
                description="해당 시즌 데이터를 찾을 수 없습니다.",
                color=0xE74C3C
            )
            embed.set_footer(text=season_name)
        
        new_view = StatsView(self.player_data, self.played_seasons)
        # 현재 시즌 모드 상태 유지
        new_view.show_preseason = self.show_preseason
        
        season_select = new_view.create_season_select()
        if season_select:
            new_view.add_item(season_select)
        
        # 프리시즌이 있으면 전환 버튼 다시 추가
        has_preseason = any(new_view._is_preseason(season['name']) for season in self.played_seasons)
        if has_preseason:
            toggle_button = discord.ui.Button(
                label='정식시즌 보기' if new_view.show_preseason else '프리시즌 보기',
                style=discord.ButtonStyle.secondary,
                custom_id='toggle_season',
                row=2
            )
            toggle_button.callback = new_view.toggle_season_type
            new_view.add_item(toggle_button)
            
            # 메인으로 버튼도 row=2로 이동
            for item in new_view.children:
                if hasattr(item, 'label') and item.label == '메인으로':
                    item.row = 2
        
        await interaction.edit_original_response(embed=embed, view=new_view)
    
    async def toggle_season_type(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # 모드 전환
        self.show_preseason = not self.show_preseason
        
        # 전환 버튼 찾아서 라벨 업데이트
        for item in self.children:
            if hasattr(item, 'custom_id') and item.custom_id == 'toggle_season':
                item.label = '정식시즌 보기' if self.show_preseason else '프리시즌 보기'
                break
        
        # 기존 시즌 셀렉트 제거하고 새로 추가
        # Select 컴포넌트 찾아서 제거
        for item in list(self.children):
            if hasattr(item, 'options'):
                self.remove_item(item)
                break
        
        # 새로운 시즌 셀렉트 추가
        season_select = self.create_season_select()
        if season_select:
            self.add_item(season_select)
        
        # 메인 임베드로 돌아가기
        embed = create_embed(self.player_data)
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='메인으로', style=discord.ButtonStyle.gray, row=2)
    async def back_to_main(self, interaction: discord.Interaction, button):
        embed = create_embed(self.player_data)
        await interaction.response.edit_message(embed=embed, view=self, attachments=[])

@bot.tree.command(name="전적", description="이터널 리턴 플레이어 전적을 검색해요!")
async def stats_command(interaction: discord.Interaction, 닉네임: str):
    await interaction.response.defer() 
    
    if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
        await interaction.followup.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        searching_embed = discord.Embed(title="전적 검색 중...", description=f"**{닉네임}**님의 전적을 검색하고 있어요!", color=characters["debi"]["color"])
        await interaction.followup.send(embed=searching_embed)
        
        player_data, played_seasons = await asyncio.gather(
            get_player_basic_data(닉네임.strip()),
            get_player_played_seasons(닉네임.strip())
        )
        
        if not player_data:
            error_embed = create_character_embed(characters["debi"], "전적 검색 실패", f"**{닉네임}**님의 전적을 찾을 수 없어!", f"/전적 {닉네임}")
            await interaction.edit_original_response(embed=error_embed, view=None)
            return
        
        view = StatsView(player_data, played_seasons)
        if played_seasons:
            # 프리시즌이 있는지 확인
            has_preseason = any(view._is_preseason(season['name']) for season in played_seasons)
            
            # 시즌 셀렉트 추가
            season_select = view.create_season_select()
            if season_select:
                view.add_item(season_select)
            
            # 프리시즌이 있으면 전환 버튼 추가
            if has_preseason:
                toggle_button = discord.ui.Button(
                    label='프리시즌 보기', 
                    style=discord.ButtonStyle.secondary, 
                    custom_id='toggle_season',
                    row=2
                )
                toggle_button.callback = view.toggle_season_type
                view.add_item(toggle_button)
                
                # 메인으로 버튼도 row=2로 이동
                for item in view.children:
                    if hasattr(item, 'label') and item.label == '메인으로':
                        item.row = 2
            
        embed = create_embed(player_data)
        response_message = f"{닉네임}님의 전적 찾았어!"

        await interaction.edit_original_response(content=response_message, embed=embed, view=view)
        
    except Exception as e:
        print(f"--- 전적 명령어 오류 발생 ---")
        import traceback
        traceback.print_exc()
        print(f"--- 오류 끝 ---")
        error_embed = create_character_embed(characters["debi"], "검색 오류", f"**{닉네임}**님 검색 중 오류가 발생했어!", f"/전적 {닉네임}")
        await interaction.edit_original_response(embed=error_embed, view=None)

class ChannelSelectView(discord.ui.View):
    def __init__(self, guild_channels):
        super().__init__(timeout=300)
        self.guild_channels = guild_channels
        self.current_step = 'announcement'  # 'announcement' 또는 'chat'
        
        # 첫 번째 단계: 공지 채널 선택
        self.show_announcement_select()

    def show_announcement_select(self):
        # 기존 아이템들 제거
        self.clear_items()
        
        # 공지 채널 선택 드롭다운
        announcement_select = discord.ui.Select(
            placeholder="📢 공지 채널을 선택하세요",
            options=self.guild_channels[:25]  # 최대 25개
        )
        announcement_select.callback = self.announcement_callback
        self.add_item(announcement_select)

    def show_chat_select(self):
        # 기존 아이템들 제거
        self.clear_items()
        
        # 대화 채널 선택 드롭다운
        chat_select = discord.ui.Select(
            placeholder="💬 대화 채널을 선택하세요",
            options=self.guild_channels[:25]  # 최대 25개
        )
        chat_select.callback = self.chat_callback
        self.add_item(chat_select)
        
        # 완료 버튼
        finish_button = discord.ui.Button(label="설정 완료", style=discord.ButtonStyle.success)
        finish_button.callback = self.finish_setup
        self.add_item(finish_button)

    async def announcement_callback(self, interaction: discord.Interaction):
        channel_id = int(interaction.data['values'][0])
        channel = interaction.guild.get_channel(channel_id)
        
        if channel and isinstance(channel, discord.TextChannel):
            # 파일에 저장
            if config.save_settings(announcement_id=channel_id):
                # 다음 단계로 진행
                self.current_step = 'chat'
                self.show_chat_select()
                
                await interaction.response.edit_message(
                    content=f"📢 공지 채널: {channel.mention} (저장완료)\n💬 이제 대화 채널을 선택해주세요.",
                    view=self
                )
            else:
                await interaction.response.send_message("설정 저장에 실패했습니다.", ephemeral=True)
        else:
            await interaction.response.send_message("올바른 텍스트 채널을 선택해주세요.", ephemeral=True)

    async def chat_callback(self, interaction: discord.Interaction):
        channel_id = int(interaction.data['values'][0])
        channel = interaction.guild.get_channel(channel_id)

        if channel and isinstance(channel, discord.TextChannel):
            # 파일에 저장
            if config.save_settings(chat_id=channel_id):
                announcement_channel = interaction.guild.get_channel(config.ANNOUNCEMENT_CHANNEL_ID)
                await interaction.response.edit_message(
                    content=f"✅ 채널 설정이 완료되었습니다! (영구저장됨)\n📢 공지 채널: {announcement_channel.mention if announcement_channel else '없음'}\n💬 대화 채널: {channel.mention}",
                    view=self
                )
            else:
                await interaction.response.send_message("설정 저장에 실패했습니다.", ephemeral=True)
        else:
            await interaction.response.send_message("올바른 텍스트 채널을 선택해주세요.", ephemeral=True)
    
    async def finish_setup(self, interaction: discord.Interaction):
        announcement_channel = interaction.guild.get_channel(config.ANNOUNCEMENT_CHANNEL_ID) if config.ANNOUNCEMENT_CHANNEL_ID else None
        chat_channel = interaction.guild.get_channel(config.CHAT_CHANNEL_ID) if config.CHAT_CHANNEL_ID else None
        
        self.clear_items()
        
        await interaction.response.edit_message(
            content=f"🎉 모든 설정이 완료되었습니다!\n📢 공지 채널: {announcement_channel.mention if announcement_channel else '설정 안됨'}\n💬 대화 채널: {chat_channel.mention if chat_channel else '설정 안됨'}",
            view=None
        )



@bot.tree.command(name="채널설정", description="관리자 전용: 봇이 사용할 채널을 설정합니다.")
async def set_channels(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("이 명령어는 관리자만 사용할 수 있습니다.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    print("--- 채널 목록 생성 시작 (권한 확인 임시 비활성화) ---")
    
    # 권한 확인을 임시로 건너뛰고 모든 텍스트 채널을 가져옵니다.
    # 이름이 없는 채널은 제외합니다.
    all_text_channels = sorted(
        [ch for ch in interaction.guild.text_channels if ch.name],
        key=lambda c: c.name
    )
    
    print(f"드롭다운에 포함될 채널 ({len(all_text_channels)}개): {[c.name for c in all_text_channels]}")
    print("--- 채널 목록 생성 끝 ---")
    
    if not all_text_channels:
        await interaction.followup.send("서버에 텍스트 채널이 없습니다.", ephemeral=True)
        return

    options = [
        discord.SelectOption(label=f"#{channel.name}", value=str(channel.id))
        for channel in all_text_channels[:25]
    ]

    view = ChannelSelectView(options)
    
    message_content = f"📢 먼저 공지 채널을 선택해주세요."
    await interaction.followup.send(content=message_content, view=view, ephemeral=True)

def run_bot():
    if not DISCORD_TOKEN:
        print("CRITICAL: DISCORD_TOKEN이 설정되지 않았습니다.")
        return
    
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"CRITICAL: 봇 실행 중 치명적인 오류 발생: {e}")

if __name__ == "__main__":
    run_bot()