"""
/전적 명령어

이터널 리턴 플레이어의 전적을 검색합니다.
"""

import discord
import asyncio

from run.core import config
from run.services.eternal_return.api_client import (
    get_player_basic_data,
    get_player_played_seasons
)
from run.views.stats_view import StatsView
from run.utils.embeds import create_stats_embed
from run.utils.command_logger import log_command_usage


async def setup_stats_command(bot):
    """
    /전적 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="전적", description="이터널 리턴 플레이어 전적을 검색해요!")
    async def stats_command(interaction: discord.Interaction, 닉네임: str):

        # defer를 가장 먼저 호출 (3초 타임아웃 방지)
        await interaction.response.defer(ephemeral=False)

        # 명령어 사용 로깅
        await log_command_usage(
            command_name="전적",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            args={"닉네임": 닉네임}
        )

        # 채널 제한 체크 (defer 이후)
        if interaction.guild:
            guild_settings = config.get_guild_settings(interaction.guild.id)
            chat_channel_id = guild_settings.get("CHAT_CHANNEL_ID")
            if chat_channel_id and interaction.channel.id != chat_channel_id:
                allowed_channel = bot.get_channel(chat_channel_id)
                await interaction.followup.send(
                    f"이 명령어는 {allowed_channel.mention} 채널에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

        try:
            # 백그라운드에서 데이터 가져오기
            player_data, played_seasons = await asyncio.gather(
                get_player_basic_data(닉네임.strip()),
                get_player_played_seasons(닉네임.strip()),
                return_exceptions=True
            )

            # 예외 처리
            if isinstance(player_data, Exception):
                raise player_data
            if isinstance(played_seasons, Exception):
                played_seasons = []

            if not player_data:
                embed = discord.Embed(
                    title="전적 검색 실패",
                    description=f"**{닉네임}**님의 전적을 찾을 수 없어!",
                    color=0x0000FF  # 파랑
                )
                embed.set_footer(text=f"사용된 명령어: /전적 {닉네임}")
                await interaction.followup.send(embed=embed)
                return

            view = StatsView(player_data, played_seasons)
            embed = create_stats_embed(player_data, False)  # 기본은 랭크게임 모드
            await interaction.followup.send(
                content=f"{닉네임}님의 전적 찾았어!",
                embed=embed,
                view=view
            )

        except Exception as e:
            print(f"--- 전적 명령어 오류: {e} ---")
            import traceback
            traceback.print_exc()

            try:
                error_embed = discord.Embed(
                    title="검색 오류",
                    description=f"**{닉네임}**님 검색 중 오류가 발생했어!",
                    color=0x0000FF  # 파랑
                )
                error_embed.set_footer(text=f"사용된 명령어: /전적 {닉네임}")

                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=error_embed)
                else:
                    await interaction.followup.send(embed=error_embed)
            except:
                pass
