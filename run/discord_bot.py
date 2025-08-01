import discord
import asyncio
from discord.ext import commands
from run.config import characters, DISCORD_TOKEN
from run import config
from run.api_clients import get_player_basic_data, get_season_name, get_season_data, get_player_season_data, get_player_played_seasons

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

def create_embed(player_data):
    embed = discord.Embed(
        title=f"{player_data['nickname']}",
        color=0x00D4AA
    )
    
    # 모스트 실험체 아이콘 추가
    if player_data.get('most_characters'):
        most_char = player_data['most_characters'][0]
        if most_char.get('image_url'):
            embed.set_author(
                name=f"{player_data['nickname']} ({most_char['name']})",
                icon_url=most_char['image_url']
            )
    
    # 시즌 정보 푸터
    season_name = player_data.get('season_name', get_season_name(33))
    embed.set_footer(text=season_name)
    
    if player_data.get('tier_info'):
        embed.add_field(name="RANK", value=f"**{player_data['tier_info']}**", inline=False)
    
    if player_data.get('most_characters'):
        top_char = player_data['most_characters'][0]
        embed.add_field(name="가장 많이 플레이한 실험체", value=f"**{top_char['name']}** ({top_char['games']}게임)", inline=True)
    
    if player_data.get('stats'):
        stats = player_data['stats']
        embed.add_field(name="승률", value=f"**{stats.get('winrate', 0):.1f}%**", inline=True)
    
    if player_data.get('tier_image_url'):
        tier_image_url = player_data['tier_image_url']
        if tier_image_url.startswith('//'):
            tier_image_url = 'https:' + tier_image_url
        embed.set_thumbnail(url=tier_image_url)
    
    return embed

def create_character_embed(character, title, description, command_used=""):
    """캐릭터 기반 에러 임베드 생성"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=character.get("color", 0xFF0000)
    )
    if command_used:
        embed.set_footer(text=f"사용된 명령어: {command_used}")
    return embed

class StatsView(discord.ui.View):
    def __init__(self, player_data, played_seasons=None):
        super().__init__(timeout=300)
        self.player_data = player_data
        self.played_seasons = played_seasons or []

    @discord.ui.button(label='실험체', style=discord.ButtonStyle.primary)
    async def show_characters(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title=f"{self.player_data['nickname']}님의 실험체", color=0x5865F2)
        
        most_chars = self.player_data.get('most_characters', [])
        if most_chars:
            for i, char in enumerate(most_chars[:5]):
                embed.add_field(
                    name=f"{i+1}. {char['name']}",
                    value=f"{char['games']}게임, {char['winrate']:.1f}% 승률",
                    inline=True
                )
        else:
            embed.add_field(name="실험체 정보", value="데이터가 없습니다.", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='통계', style=discord.ButtonStyle.secondary)
    async def show_stats(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title=f"{self.player_data['nickname']}님의 통계", color=0xE67E22)
        
        stats = self.player_data.get('stats', {})
        if stats:
            embed.add_field(name="게임 수", value=f"{stats.get('total_games', 0)}게임", inline=True)
            embed.add_field(name="승률", value=f"{stats.get('winrate', 0):.1f}%", inline=True)
            embed.add_field(name="평균 순위", value=f"{stats.get('avg_rank', 0):.1f}등", inline=True)
            embed.add_field(name="평균 킬", value=f"{stats.get('avg_kills', 0):.1f}킬", inline=True)
            embed.add_field(name="MMR", value=f"{self.player_data.get('mmr', 0)}", inline=True)
        else:
            embed.add_field(name="통계 정보", value="데이터가 없습니다.", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)

    def create_season_select(self):
        """플레이어가 플레이한 시즌으로 동적 드롭다운 생성"""
        if not self.played_seasons:
            # 기본 옵션들
            options = [
                discord.SelectOption(label="시즌 8 (현재)", value="33", emoji="🔥"),
                discord.SelectOption(label="시즌 7", value="31"),
                discord.SelectOption(label="시즌 6", value="29"),
                discord.SelectOption(label="시즌 5", value="27"),
                discord.SelectOption(label="시즌 4", value="25"),
            ]
        else:
            # 플레이한 시즌들로 옵션 생성
            options = []
            for season in self.played_seasons:
                label = f"{season['name']}" + (" (현재)" if season['is_current'] else "")
                emoji = "🔥" if season['is_current'] else None
                options.append(discord.SelectOption(
                    label=label,
                    value=str(season['id']),
                    emoji=emoji
                ))
        
        select = discord.ui.Select(
            placeholder="시즌별 전적 보기...",
            options=options
        )
        select.callback = self.season_select_callback
        return select
    
    async def season_select_callback(self, interaction):
        await interaction.response.defer()
        
        season_id = int(interaction.data['values'][0])
        
        # 선택한 시즌의 전체 데이터 가져오기
        season_player_data = await get_player_season_data(self.player_data['nickname'], season_id)
        
        if season_player_data:
            # 플레이어 데이터 업데이트
            self.player_data = season_player_data
            # 새로운 데이터로 임베드 생성
            embed = create_embed(season_player_data)
        else:
            embed = discord.Embed(
                title=f"{self.player_data['nickname']}님의 {get_season_name(season_id)} 전적",
                description="해당 시즌 데이터를 찾을 수 없습니다.",
                color=0xE74C3C
            )
            embed.set_footer(text=get_season_name(season_id))
        
        # 새로운 뷰 생성 (드롭다운 다시 추가)
        new_view = StatsView(self.player_data, self.played_seasons)
        new_view.add_item(new_view.create_season_select())
        await interaction.edit_original_response(embed=embed, view=new_view)

    @discord.ui.button(label='메인으로', style=discord.ButtonStyle.gray)
    async def back_to_main(self, interaction: discord.Interaction, button):
        embed = create_embed(self.player_data)
        await interaction.response.edit_message(embed=embed, view=self)

@bot.tree.command(name="전적", description="이터널 리턴 플레이어 전적을 검색해요!")
async def stats_command(interaction: discord.Interaction, 닉네임: str):
    """플레이어 전적 검색"""
    await interaction.response.defer()
    
    if config.CHAT_CHANNEL_ID and interaction.channel.id != config.CHAT_CHANNEL_ID:
        await interaction.followup.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
        return
    
    try:
        searching_embed = discord.Embed(
            title="전적 검색 중...",
            description=f"**{닉네임}**님의 전적을 검색하고 있어요!",
            color=characters["debi"]["color"]
        )
        await interaction.followup.send(embed=searching_embed)
        
        # 플레이어 기본 데이터와 시즌 목록을 동시에 가져오기
        player_data_task = get_player_basic_data(닉네임.strip())
        played_seasons_task = get_player_played_seasons(닉네임.strip())
        
        player_data, played_seasons = await asyncio.gather(player_data_task, played_seasons_task)
        
        # 초기 로드 시 현재 시즌(시즌 8) 정보 추가
        if player_data:
            player_data['season_id'] = 33
            player_data['season_name'] = get_season_name(33)
        
        if not player_data:
            error_embed = create_character_embed(
                characters["debi"], 
                "전적 검색 실패",
                f"**{닉네임}**님의 전적을 찾을 수 없어!",
                f"/전적 {닉네임}"
            )
            await interaction.edit_original_response(embed=error_embed, view=None)
            return
        
        view = StatsView(player_data, played_seasons)
        view.add_item(view.create_season_select())
        embed = create_embed(player_data)
        response_message = f"{닉네임}님의 전적 찾았어!"

        await interaction.edit_original_response(content=response_message, embed=embed, view=view)
        
    except Exception as e:
        error_embed = create_character_embed(
            characters["debi"], 
            "검색 오류",
            f"**{닉네임}**님 검색 중 오류가 발생했어!",
            f"/전적 {닉네임}"
        )
        await interaction.edit_original_response(embed=error_embed, view=None)

@bot.tree.command(name="채널설정", description="관리자 전용: 공지채널과 대화채널을 설정합니다")
async def set_channels(interaction: discord.Interaction, 공지채널: discord.TextChannel = None, 대화채널: discord.TextChannel = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("이 명령어는 관리자만 사용할 수 있습니다.", ephemeral=True)
        return
    
    result_messages = []
    
    if 공지채널:
        config.ANNOUNCEMENT_CHANNEL_ID = 공지채널.id
        result_messages.append(f"공지채널이 {공지채널.mention}로 설정되었습니다.")
    
    if 대화채널:
        config.CHAT_CHANNEL_ID = 대화채널.id
        result_messages.append(f"대화채널이 {대화채널.mention}로 설정되었습니다.")
    
    if not result_messages:
        result_messages.append("설정할 채널을 선택해주세요.")
    
    embed = discord.Embed(
        title="채널 설정 완료",
        description="\n".join(result_messages),
        color=characters["debi"]["color"]
    )
    
    await interaction.response.send_message(embed=embed)

def run_bot():
    if not DISCORD_TOKEN:
        return
    
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        pass

if __name__ == "__main__":
    run_bot()