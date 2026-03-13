"""
이터널 리턴 Cog

게임 관련 명령어: 전적, 통계, 추천, 동접
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import aiohttp

from run.core import config
from run.services.eternal_return.api_client import (
    get_player_basic_data,
    get_player_played_seasons,
    get_character_stats,
    game_data
)
from run.views.stats_view import StatsView
from run.views.character_view import CharacterStatsView
from run.utils.embeds import create_stats_embed
from run.utils.command_logger import log_command_usage


# Steam API 설정
ETERNAL_RETURN_APP_ID = 1049590
STEAM_API_URL = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={ETERNAL_RETURN_APP_ID}"


class EternalReturnCog(commands.Cog, name="이터널리턴"):
    """이터널 리턴 게임 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="전적", description="플레이어 전적을 검색합니다")
    @app_commands.describe(닉네임="검색할 플레이어 닉네임")
    async def stats(self, interaction: discord.Interaction, 닉네임: str):
        await interaction.response.defer(ephemeral=False)

        await log_command_usage(
            command_name="전적",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            channel_id=interaction.channel_id,
            channel_name=getattr(interaction.channel, 'name', None) if interaction.channel else None,
            args={"닉네임": 닉네임}
        )

        # 채널 제한 체크
        if interaction.guild:
            guild_settings = config.get_guild_settings(interaction.guild.id)
            chat_channel_id = guild_settings.get("CHAT_CHANNEL_ID")
            if chat_channel_id and interaction.channel.id != chat_channel_id:
                allowed_channel = self.bot.get_channel(chat_channel_id)
                await interaction.followup.send(
                    f"이 명령어는 {allowed_channel.mention} 채널에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

        try:
            player_data, played_seasons = await asyncio.gather(
                get_player_basic_data(닉네임.strip()),
                get_player_played_seasons(닉네임.strip()),
                return_exceptions=True
            )

            if isinstance(player_data, Exception):
                raise player_data
            if isinstance(played_seasons, Exception):
                played_seasons = []

            if not player_data:
                embed = discord.Embed(
                    title="전적 검색 실패",
                    description=f"**{닉네임}**님의 전적을 찾을 수 없어!",
                    color=0x0000FF
                )
                embed.set_footer(text=f"사용된 명령어: /전적 {닉네임}")
                await interaction.followup.send(embed=embed)
                return

            view = StatsView(player_data, played_seasons)
            embed = create_stats_embed(player_data, False)
            await interaction.followup.send(embed=embed, view=view)

        except Exception as e:
            print(f"--- 전적 명령어 오류: {e} ---")
            import traceback
            traceback.print_exc()

            error_embed = discord.Embed(
                title="검색 오류",
                description=f"**{닉네임}**님 검색 중 오류가 발생했어!",
                color=0x0000FF
            )
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(name="통계", description="캐릭터별 통계를 보여줍니다 (다이아+)")
    async def character_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await log_command_usage(
            command_name="통계",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            channel_id=interaction.channel_id,
            channel_name=getattr(interaction.channel, 'name', None) if interaction.channel else None,
            args={}
        )

        try:
            stats_data = await get_character_stats(dt=7, team_mode="SQUAD", tier="diamond_plus")

            if not stats_data:
                await interaction.edit_original_response(content="캐릭터 통계 데이터를 가져올 수 없습니다.")
                return

            view = CharacterStatsView(stats_data, period=7)
            embed = view.create_embed()
            await interaction.edit_original_response(embed=embed, view=view)

        except Exception as e:
            print(f"[오류] 캐릭터 통계 명령어 오류: {e}")
            import traceback
            traceback.print_exc()
            await interaction.edit_original_response(content="캐릭터 통계를 처리하는 중 오류가 발생했습니다.")

    @app_commands.command(name="동접", description="현재 동접자 수를 확인합니다")
    async def online(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await log_command_usage(
            command_name="동접",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            channel_id=interaction.channel_id,
            channel_name=getattr(interaction.channel, 'name', None) if interaction.channel else None,
            args={}
        )

        player_count = await self._get_player_count()

        if player_count is not None:
            formatted_count = f"{player_count:,}"

            embed = discord.Embed(
                title="이터널 리턴 동접자",
                description=f"현재 **{formatted_count}**명이 플레이 중",
                color=0x1B2838
            )
            embed.set_thumbnail(url="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1049590/fa56f360467f675b777dd18a6315f00c84a7b9c4/header.jpg")
            embed.set_footer(text="Steam 기준")

            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="오류",
                description="동접자 수를 가져올 수 없습니다. 잠시 후 다시 시도해주세요.",
                color=0xFF0000
            )
            await interaction.followup.send(embed=embed)

    async def _get_player_count(self) -> int | None:
        """Steam API로 현재 동접자 수를 가져옵니다."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(STEAM_API_URL, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("response", {}).get("result") == 1:
                            return data["response"]["player_count"]
                    return None
        except Exception as e:
            print(f"[오류] Steam API 호출 실패: {e}")
            return None


async def setup(bot: commands.Bot):
    await bot.add_cog(EternalReturnCog(bot))
