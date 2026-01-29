"""
음악 Cog

음악 재생 명령어: 재생, 정지, 스킵, 대기열
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging

from run.services.music import MusicManager, YouTubeExtractor
from run.views.music_view import (
    create_added_to_queue_embed,
    create_queue_embed,
    create_skipped_embed,
    create_stopped_embed,
    create_error_embed
)
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)


class MusicCog(commands.GroupCog, group_name="음악"):
    """음악 재생 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="재생", description="YouTube 음악을 재생합니다")
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
                command_name="재생",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                args={"검색어": 검색어}
            )

            song = await YouTubeExtractor.extract_info(검색어, interaction.user)

            if not song:
                embed = create_error_embed("검색 결과를 찾을 수 없어요. 다른 검색어를 시도해보세요.")
                await interaction.followup.send(embed=embed)
                return

            player = MusicManager.get_player(guild_id)

            if not player.is_connected():
                voice_channel = interaction.user.voice.channel
                success = await player.join(voice_channel)
                if not success:
                    embed = create_error_embed("음성 채널에 입장할 수 없어요.")
                    await interaction.followup.send(embed=embed)
                    return

            position = await player.add_song(song)

            embed = create_added_to_queue_embed(song, position)
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"재생 명령어 오류: {e}")
            try:
                embed = create_error_embed(f"오류가 발생했어요: {str(e)}")
                await interaction.followup.send(embed=embed)
            except:
                pass

    @app_commands.command(name="정지", description="음악을 정지하고 대기열을 비웁니다")
    async def stop(self, interaction: discord.Interaction):
        """음악을 정지하고 대기열을 비웁니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            if not MusicManager.has_player(guild_id):
                await interaction.response.send_message(
                    "재생 중인 음악이 없어요!",
                    ephemeral=True
                )
                return

            player = MusicManager.get_player(guild_id)

            if not player.is_connected():
                await interaction.response.send_message(
                    "봇이 음성 채널에 연결되어 있지 않아요!",
                    ephemeral=True
                )
                return

            await interaction.response.defer()

            await log_command_usage(
                command_name="정지",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                args={}
            )

            await MusicManager.remove_player(guild_id)

            embed = create_stopped_embed()
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"정지 명령어 오류: {e}")
            try:
                embed = create_error_embed(f"오류가 발생했어요: {str(e)}")
                await interaction.followup.send(embed=embed)
            except:
                pass

    @app_commands.command(name="스킵", description="현재 곡을 건너뜁니다")
    async def skip(self, interaction: discord.Interaction):
        """현재 곡을 건너뜁니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            if not MusicManager.has_player(guild_id):
                await interaction.response.send_message(
                    "재생 중인 음악이 없어요!",
                    ephemeral=True
                )
                return

            player = MusicManager.get_player(guild_id)

            if not player.current:
                await interaction.response.send_message(
                    "스킵할 곡이 없어요!",
                    ephemeral=True
                )
                return

            await interaction.response.defer()

            await log_command_usage(
                command_name="스킵",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                args={}
            )

            skipped = await player.skip()

            if skipped:
                embed = create_skipped_embed(skipped)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("스킵할 곡이 없어요!")

        except Exception as e:
            logger.error(f"스킵 명령어 오류: {e}")
            try:
                embed = create_error_embed(f"오류가 발생했어요: {str(e)}")
                await interaction.followup.send(embed=embed)
            except:
                pass

    @app_commands.command(name="대기열", description="현재 대기열을 확인합니다")
    async def queue(self, interaction: discord.Interaction):
        """현재 대기열을 확인합니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            if not MusicManager.has_player(guild_id):
                await interaction.response.send_message(
                    "재생 중인 음악이 없어요!",
                    ephemeral=True
                )
                return

            player = MusicManager.get_player(guild_id)

            await log_command_usage(
                command_name="대기열",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                args={}
            )

            embed = create_queue_embed(
                current=player.current,
                queue=player.get_queue()
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logger.error(f"대기열 명령어 오류: {e}")
            try:
                embed = create_error_embed(f"오류가 발생했어요: {str(e)}")
                await interaction.response.send_message(embed=embed)
            except:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))
