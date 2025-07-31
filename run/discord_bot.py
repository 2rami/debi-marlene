import discord
from discord.ext import commands
from run.config import characters, DISCORD_TOKEN
from run import config
from run.api_clients import get_player_basic_data, get_season_name

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

def create_embed(player_data):
    embed = discord.Embed(
        title=f"{player_data['nickname']}",
        color=0x00D4AA
    )
    embed.set_footer(text=get_season_name(33))
    
    if player_data.get('tier_info'):
        embed.add_field(name="현재 랭크", value=f"**{player_data['tier_info']}**", inline=False)
    
    if player_data.get('most_characters'):
        top_char = player_data['most_characters'][0]
        embed.add_field(name="모스트 실험체", value=f"**{top_char['name']}** ({top_char['games']}게임)", inline=True)
    
    if player_data.get('stats'):
        stats = player_data['stats']
        embed.add_field(name="승률", value=f"**{stats.get('winrate', 0):.1f}%**", inline=True)
    
    if player_data.get('tier_image_url'):
        tier_image_url = player_data['tier_image_url']
        if tier_image_url.startswith('//'):
            tier_image_url = 'https:' + tier_image_url
        embed.set_thumbnail(url=tier_image_url)
    
    return embed

class StatsView(discord.ui.View):
    def __init__(self, player_data):
        super().__init__(timeout=300)
        self.player_data = player_data

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
        
        player_data = await get_player_basic_data(닉네임.strip())
        
        if not player_data:
            error_embed = create_character_embed(
                characters["debi"], 
                "전적 검색 실패",
                f"**{닉네임}**님의 전적을 찾을 수 없어!",
                f"/전적 {닉네임}"
            )
            await interaction.edit_original_response(embed=error_embed, view=None)
            return
        
        view = StatsView(player_data)
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