import discord
import asyncio
from discord.ext import commands
from run.config import characters, DISCORD_TOKEN, OWNER_ID
from run import config
from run.api_clients import (
    get_player_basic_data, 
    get_player_season_data, 
    get_player_played_seasons,
    initialize_game_data,
    game_data
)
from run.graph_generator import save_mmr_graph_to_file
import os
import tempfile
from run import youtube_service

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# --- Helper Functions ---

def create_character_embed(character, title, description, command_used=""):
    embed = discord.Embed(title=title, description=description, color=character.get("color", 0xFF0000))
    if command_used:
        embed.set_footer(text=f"사용된 명령어: {command_used}")
    return embed

def create_stats_embed(player_data):
    rank_info = player_data.get('tier_info', 'Unranked')
    description = ""
    rank = player_data.get('rank', 0)
    rank_percent = player_data.get('rank_percent', 0)
    if rank > 0:
        description = f"{rank:,}위 상위 {rank_percent}%"
    
    embed = discord.Embed(title=rank_info, description=description, color=0x00D4AA)
    
    nickname = player_data.get('nickname', 'Unknown Player')
    author_icon_url = None
    if player_data.get('most_characters'):
        most_char = player_data['most_characters'][0]
        if most_char.get('image_url'):
            author_icon_url = most_char['image_url']
    embed.set_author(name=nickname, icon_url=author_icon_url)

    season_name = game_data.get_season_name(player_data['season_id'])
    embed.set_footer(text=season_name)
    
    if player_data.get('tier_image_url'):
        embed.set_thumbnail(url=player_data['tier_image_url'])

    if player_data.get('most_characters'):
        top_char = player_data['most_characters'][0]
        embed.add_field(name="가장 많이 플레이한 실험체", value=f"**{top_char['name']}** ({top_char['games']}게임)", inline=True)
    
    if player_data.get('stats'):
        stats = player_data['stats']
        embed.add_field(name="승률", value=f"**{stats.get('winrate', 0):.1f}%**", inline=True)
    
    return embed

# --- UI Views ---

class StatsView(discord.ui.View):
    def __init__(self, player_data, played_seasons=None):
        super().__init__(timeout=300)
        self.player_data = player_data
        self.played_seasons = played_seasons or []
        self.show_preseason = False
        self.add_item(self.create_season_select())
        if any(self._is_preseason(s['name']) for s in self.played_seasons):
            toggle_button = discord.ui.Button(label='프리시즌 보기', style=discord.ButtonStyle.secondary, custom_id='toggle_season', row=2)
            toggle_button.callback = self.toggle_season_type
            self.add_item(toggle_button)

    @discord.ui.button(label='실험체', style=discord.ButtonStyle.primary)
    async def show_characters(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title=f"{self.player_data['nickname']}님의 실험체", color=0x5865F2)
        most_chars = self.player_data.get('most_characters', [])
        if most_chars:
            for i, char in enumerate(most_chars[:10]):
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
        graph_path = None
        mmr_history = self.player_data.get('mmr_history', [])
        if mmr_history and len(mmr_history) >= 2:
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    graph_path = save_mmr_graph_to_file(mmr_history, self.player_data.get('nickname', '플레이어'), tmp_file.name)
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
        else:
            embed.add_field(name="통계 정보", value="데이터가 없습니다.", inline=False)
        
        if file_attachment:
            await interaction.edit_original_response(embed=embed, attachments=[file_attachment], view=self)
            if graph_path: os.unlink(graph_path)
        else:
            await interaction.edit_original_response(embed=embed, view=self)

    def _is_preseason(self, season_name: str) -> bool:
        return "프리" in season_name or "Pre" in season_name

    def _filter_seasons_by_type(self):
        if not self.played_seasons:
            return []
        return [s for s in self.played_seasons if self._is_preseason(s['name']) == self.show_preseason][:25]

    def create_season_select(self):
        filtered_seasons = self._filter_seasons_by_type()
        if not filtered_seasons:
            return None
        options = [discord.SelectOption(label=f"{s['name']}{ ' (현재)' if s.get('is_current') else ''}", value=str(s['id']), emoji="🔥" if s.get('is_current') else None) for s in filtered_seasons]
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
            embed = create_stats_embed(season_player_data)
        else:
            season_name = game_data.get_season_name(season_id)
            embed = discord.Embed(title=f"{self.player_data['nickname']}님의 {season_name} 전적", description="해당 시즌 데이터를 찾을 수 없습니다.", color=0xE74C3C)
            embed.set_footer(text=season_name)
        
        new_view = StatsView(self.player_data, self.played_seasons)
        new_view.show_preseason = self.show_preseason
        await interaction.edit_original_response(embed=embed, view=new_view)
    
    async def toggle_season_type(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.show_preseason = not self.show_preseason
        for item in self.children:
            if hasattr(item, 'custom_id') and item.custom_id == 'toggle_season':
                item.label = '정식시즌 보기' if self.show_preseason else '프리시즌 보기'
                break
        for item in list(self.children):
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)
                break
        self.add_item(self.create_season_select())
        embed = create_stats_embed(self.player_data)
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='메인으로', style=discord.ButtonStyle.gray, row=2)
    async def back_to_main(self, interaction: discord.Interaction, button):
        embed = create_stats_embed(self.player_data)
        await interaction.response.edit_message(embed=embed, view=self, attachments=[])

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚙️ 바로 설정하기", style=discord.ButtonStyle.success, custom_id="welcome_setup_button")
    async def setup_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("이 버튼은 서버 관리자만 사용할 수 있어요!", ephemeral=True)
            return
        
        embed = discord.Embed(title="⚙️ 서버 설정", description="아래 버튼으로 유튜브 공지 채널과 명령어 전용 채널을 설정하세요.", color=0x7289DA)
        embed.add_field(name="📢 공지 채널", value="유튜브 새 영상 알림이 올라갈 채널입니다. (필수)", inline=False)
        embed.add_field(name="💬 채팅 채널", value="`/전적` 등 봇의 명령어를 사용할 특정 채널입니다. 설정하지 않으면 모든 채널에서 사용 가능합니다. (선택)", inline=False)
        view = SettingsView(interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class SettingsView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.update_components()

    def update_components(self):
        guild_settings = config.get_guild_settings(self.guild.id)
        announcement_ch_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
        chat_ch_id = guild_settings.get("CHAT_CHANNEL_ID")

        announcement_button = self.children[0]
        if announcement_ch_id and (ch := self.guild.get_channel(announcement_ch_id)):
            announcement_button.label = f"📢 공지 채널: #{ch.name}"
            announcement_button.style = discord.ButtonStyle.success
        else:
            announcement_button.label = "📢 공지 채널 설정"
            announcement_button.style = discord.ButtonStyle.secondary

        chat_button = self.children[1]
        if chat_ch_id and (ch := self.guild.get_channel(chat_ch_id)):
            chat_button.label = f"💬 채팅 채널: #{ch.name}"
            chat_button.style = discord.ButtonStyle.success
        else:
            chat_button.label = "💬 채팅 채널 설정 (선택사항)"
            chat_button.style = discord.ButtonStyle.secondary

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, custom_id="setting_announcement")
    async def announcement_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelSelectViewForSetting("announcement")
        await interaction.response.send_message("유튜브 영상 알림을 받을 채널을 선택해주세요.", view=view, ephemeral=True)

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, custom_id="setting_chat")
    async def chat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelSelectViewForSetting("chat")
        await interaction.response.send_message("명령어 사용을 제한할 채널을 선택해주세요 (없으면 모두 허용).", view=view, ephemeral=True)

class ChannelSelectViewForSetting(discord.ui.View):
    def __init__(self, channel_type: str):
        super().__init__(timeout=180)
        self.channel_type = channel_type
        label = "공지" if channel_type == "announcement" else "채팅"
        placeholder = f"#{label} 채널을 선택하세요..."
        self.select_menu = discord.ui.ChannelSelect(
            placeholder=placeholder,
            channel_types=[discord.ChannelType.text]
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        channel = self.select_menu.values[0]
        if self.channel_type == "announcement":
            config.save_guild_settings(interaction.guild.id, announcement_id=channel.id)
            await interaction.response.edit_message(content=f"✅ 공지 채널이 {channel.mention}으로 설정되었습니다.", view=None)
        else:
            config.save_guild_settings(interaction.guild.id, chat_id=channel.id)
            await interaction.response.edit_message(content=f"✅ 채팅 채널이 {channel.mention}으로 설정되었습니다.", view=None)

# --- Bot Events ---

@bot.event
async def on_ready():
    print(f'{bot.user} 봇이 시작되었습니다!')
    try:
        await bot.tree.sync()
        print("명령어 동기화 완료.")
        await initialize_game_data()
        youtube_service.set_bot_instance(bot)
        await youtube_service.initialize_youtube()
        youtube_service.check_new_videos.start()
    except Exception as e:
        print(f"CRITICAL: 데이터 초기화 중 봇 시작 실패: {e}")
        await bot.close()

@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f"✅ 새로운 서버에 초대되었습니다: {guild.name} (ID: {guild.id})")
    target_channel = guild.system_channel
    if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break
    
    if target_channel:
        try:
            profile_image = discord.File("assets/profile.webp", filename="profile.webp")
            embed = discord.Embed(title="👋 저희를 불러주셨네요!", description="이곳에서 여러분과 함께하게 되어 정말 기뻐요!", color=characters["debi"]["color"])
            embed.set_thumbnail(url="attachment://profile.webp")
            embed.add_field(name=f"{characters['debi']['name']}", value=f"> {characters['debi']['welcome_message']}", inline=False)
            embed.add_field(name=f"{characters['marlene']['name']}", value=f"> {characters['marlene']['welcome_message']}", inline=False)
            embed.add_field(name="\n⚙️ 초기 설정 안내", value="제가 제대로 활동하려면 **공지 채널**과 **채팅 채널** 설정이 필요해요.\n아래 버튼을 눌러 바로 시작할 수 있습니다!", inline=False)
            await target_channel.send(file=profile_image, embed=embed, view=WelcomeView())
        except Exception as e:
            print(f"❌ 환영 메시지 전송 중 오류 발생: {e}")

# --- Commands ---

@bot.tree.command(name="전적", description="이터널 리턴 플레이어 전적을 검색해요!")
async def stats_command(interaction: discord.Interaction, 닉네임: str):
    # 서버에서 사용할 때만 채널 제한 체크 (개인 DM에서는 제한 없음)
    if interaction.guild:
        guild_settings = config.get_guild_settings(interaction.guild.id)
        chat_channel_id = guild_settings.get("CHAT_CHANNEL_ID")
        if chat_channel_id and interaction.channel.id != chat_channel_id:
            allowed_channel = bot.get_channel(chat_channel_id)
            await interaction.response.send_message(f"이 명령어는 {allowed_channel.mention} 채널에서만 사용할 수 있어요!", ephemeral=True)
            return
    
    await interaction.response.defer()
    try:
        player_data, played_seasons = await asyncio.gather(
            get_player_basic_data(닉네임.strip()),
            get_player_played_seasons(닉네임.strip())
        )
        if not player_data:
            await interaction.followup.send(embed=create_character_embed(characters["debi"], "전적 검색 실패", f"**{닉네임}**님의 전적을 찾을 수 없어!", f"/전적 {닉네임}"))
            return
        
        view = StatsView(player_data, played_seasons)
        embed = create_stats_embed(player_data)
        await interaction.followup.send(content=f"{닉네임}님의 전적 찾았어!", embed=embed, view=view)
    except Exception as e:
        print(f"--- 전적 명령어 오류: {e} ---")
        await interaction.followup.send(embed=create_character_embed(characters["debi"], "검색 오류", f"**{닉네임}**님 검색 중 오류가 발생했어!", f"/전적 {닉네임}"))

@bot.tree.command(name="설정", description="[관리자] 서버의 공지/채팅 채널을 설정합니다.")
async def settings(interaction: discord.Interaction):
    # 서버에서만 사용 가능
    if not interaction.guild:
        await interaction.response.send_message("이 명령어는 서버에서만 사용할 수 있어요!", ephemeral=True)
        return
    
    # 관리자 권한 체크
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("이 명령어는 서버 관리자만 사용할 수 있어요!", ephemeral=True)
        return
    
    embed = discord.Embed(title="⚙️ 서버 설정", description="아래 버튼으로 유튜브 공지 채널과 명령어 전용 채널을 설정하세요.", color=0x7289DA)
    embed.add_field(name="📢 공지 채널", value="유튜브 새 영상 알림이 올라갈 채널입니다.", inline=False)
    embed.add_field(name="💬 채팅 채널", value="`/전적` 등 봇의 명령어를 사용할 특정 채널입니다. 설정하지 않으면 모든 채널에서 사용 가능합니다. (선택)", inline=False)
    view = SettingsView(interaction.guild)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="유튜브알림", description="[개인] 유튜브 새 영상 알림을 DM으로 받거나 해제합니다.")
async def subscribe_youtube(interaction: discord.Interaction, 받기: bool):
    try:
        config.set_youtube_subscription(interaction.user.id, 받기)
        message = "✅ 이제부터 새로운 영상이 올라오면 DM으로 알려드릴게요!" if 받기 else "✅ 유튜브 DM 알림을 해제했습니다."
        await interaction.response.send_message(message, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"오류가 발생했어요: {e}", ephemeral=True)

@bot.tree.command(name="피드백", description="봇 개발자에게 피드백을 보냅니다.")
async def feedback(interaction: discord.Interaction, 내용: str):
    if not OWNER_ID:
        return await interaction.response.send_message("죄송해요, 피드백 기능이 아직 설정되지 않았어요.", ephemeral=True)
    try:
        owner = await bot.fetch_user(int(OWNER_ID))
        embed = discord.Embed(title="📬 새로운 피드백 도착!", description=내용, color=0xFFB6C1)
        embed.set_author(name=f"{interaction.user.name} ({interaction.user.id})", icon_url=interaction.user.display_avatar.url)
        if interaction.guild:
            embed.add_field(name="서버", value=f"{interaction.guild.name} ({interaction.guild.id})", inline=False)
        else:
            embed.add_field(name="서버", value="개인 메시지(DM)", inline=False)
        await owner.send(embed=embed)
        await interaction.response.send_message("소중한 피드백 고마워요! 개발자에게 잘 전달했어요. ❤️", ephemeral=True)
    except (ValueError, discord.NotFound):
        await interaction.response.send_message("죄송해요, 개발자 정보를 찾을 수 없어서 피드백을 보낼 수 없어요.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("개발자에게 DM을 보낼 수 없도록 설정되어 있어 전달에 실패했어요. 😥", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"피드백 전송 중 오류가 발생했어요: {e}", ephemeral=True)

@bot.tree.command(name="유튜브테스트", description="[관리자] 유튜브 새 영상 확인을 수동으로 테스트합니다.")
async def youtube_test(interaction: discord.Interaction):
    # 개발자는 어디서든 사용 가능
    is_owner = OWNER_ID and interaction.user.id == int(OWNER_ID)
    
    if interaction.guild:
        # 서버에서는 관리자 권한 필요
        if not is_owner and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("이 명령어는 서버 관리자만 사용할 수 있어요!", ephemeral=True)
            return
            
        # 채팅 채널 제한 체크 (개발자는 예외)
        if not is_owner:
            guild_settings = config.get_guild_settings(interaction.guild.id)
            chat_channel_id = guild_settings.get("CHAT_CHANNEL_ID")
            if chat_channel_id and interaction.channel.id != chat_channel_id:
                allowed_channel = bot.get_channel(chat_channel_id)
                await interaction.response.send_message(f"이 명령어는 {allowed_channel.mention} 채널에서만 사용할 수 있어요!", ephemeral=True)
                return
    # DM에서는 누구나 사용 가능 (개인 테스트용)
    
    await interaction.response.defer(ephemeral=True)
    try:
        from run import youtube_service
        
        # 개인 DM에서 사용 시 해당 사용자에게만 테스트
        if not interaction.guild:
            result = await youtube_service.manual_check_for_user(interaction.user)
            await interaction.followup.send(f"✅ 개인 유튜브 테스트 완료!\n```{result}```", ephemeral=True)
        else:
            # 서버에서 사용 시 해당 서버에만 테스트
            result = await youtube_service.manual_check_for_guild(interaction.guild)
            await interaction.followup.send(f"✅ 서버 유튜브 테스트 완료!\n```{result}```", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ 유튜브 테스트 중 오류 발생: {e}", ephemeral=True)

def run_bot():
    if not DISCORD_TOKEN:
        print("CRITICAL: DISCORD_TOKEN이 설정되지 않았습니다.")
        return
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run_bot()