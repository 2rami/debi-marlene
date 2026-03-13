"""
음악 Cog

음악 재생 명령어: /음악
정지, 스킵, 대기열은 버튼으로 제공 (Components V2)
"""

import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import logging

from run.services.music import MusicManager, YouTubeExtractor
from run.views.music_view import MusicPlayerView, create_error_view
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)


class MusicCog(commands.Cog, name="음악"):
    """음악 재생 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="음악", description="YouTube 음악을 재생합니다")
    @app_commands.describe(검색어="YouTube URL 또는 검색어")
    async def play(self, interaction: discord.Interaction, 검색어: str):
        """YouTube 음악을 재생합니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            if not interaction.user.voice:
                await interaction.response.send_message(
                    "먼저 음성 채널에 입장해주세요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            await interaction.response.defer()

            await log_command_usage(
                command_name="음악",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
                args={"검색어": 검색어}
            )

            song = await YouTubeExtractor.extract_info(검색어, interaction.user)

            if not song:
                view = create_error_view("검색 결과를 찾을 수 없어요. 다른 검색어를 시도해보세요.")
                await interaction.followup.send(view=view)
                return

            player = MusicManager.get_player(guild_id)

            if not player.is_connected():
                voice_channel = interaction.user.voice.channel
                success = await player.join(voice_channel)
                if not success:
                    view = create_error_view("음성 채널에 입장할 수 없어요.")
                    await interaction.followup.send(view=view)
                    return

            position = await player.add_song(song)

            # play_loop가 시작될 시간을 줌 (첫 번째 곡일 때)
            if position == 1:
                await asyncio.sleep(0.3)

            view = MusicPlayerView(guild_id, added_song=song, added_position=position)
            await interaction.followup.send(view=view)

        except Exception as e:
            logger.error(f"음악 명령어 오류: {e}", exc_info=True)
            try:
                view = create_error_view(f"오류가 발생했어요: {str(e)}")
                await interaction.followup.send(view=view)
            except:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))
