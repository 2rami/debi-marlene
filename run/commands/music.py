"""
음악 재생 명령어

YouTube 음악을 음성 채널에서 재생합니다.
"""

import discord
from discord import app_commands
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


def is_tts_using_voice(guild_id: str) -> bool:
    """TTS가 음성 채널을 사용 중인지 확인합니다."""
    try:
        from run.commands.voice import audio_player
        if audio_player and audio_player.is_connected(guild_id):
            return True
    except:
        pass
    return False


async def setup_music_commands(bot):
    """
    음악 명령어들을 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="재생", description="YouTube 음악을 재생합니다")
    @app_commands.describe(검색어="YouTube URL 또는 검색어")
    async def play(interaction: discord.Interaction, 검색어: str):
        """YouTube 음악을 재생합니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 사용자가 음성 채널에 있는지 확인
            if not interaction.user.voice:
                await interaction.response.send_message(
                    "먼저 음성 채널에 입장해주세요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            # TTS가 사용 중인지 확인
            if is_tts_using_voice(guild_id):
                await interaction.response.send_message(
                    "TTS 기능이 사용 중이에요. `/음성퇴장` 후에 사용해주세요!",
                    ephemeral=True
                )
                return

            await interaction.response.defer()

            # 명령어 사용 로깅
            await log_command_usage(
                command_name="재생",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
                args={"검색어": 검색어}
            )

            # YouTube에서 곡 정보 추출
            song = await YouTubeExtractor.extract_info(검색어, interaction.user)

            if not song:
                embed = create_error_embed("검색 결과를 찾을 수 없어요. 다른 검색어를 시도해보세요.")
                await interaction.followup.send(embed=embed)
                return

            # MusicPlayer 가져오기
            player = MusicManager.get_player(guild_id)

            # 음성 채널에 입장
            if not player.is_connected():
                voice_channel = interaction.user.voice.channel
                success = await player.join(voice_channel)
                if not success:
                    embed = create_error_embed("음성 채널에 입장할 수 없어요.")
                    await interaction.followup.send(embed=embed)
                    return

            # 대기열에 추가
            position = await player.add_song(song)

            # 응답
            embed = create_added_to_queue_embed(song, position)
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"재생 명령어 오류: {e}")
            try:
                embed = create_error_embed(f"오류가 발생했어요: {str(e)}")
                await interaction.followup.send(embed=embed)
            except:
                pass

    @bot.tree.command(name="정지", description="음악을 정지하고 대기열을 비웁니다")
    async def stop(interaction: discord.Interaction):
        """음악을 정지하고 대기열을 비웁니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            # MusicPlayer 확인
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

            # 명령어 사용 로깅
            await log_command_usage(
                command_name="정지",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
                args={}
            )

            # 정지 및 퇴장
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

    @bot.tree.command(name="스킵", description="현재 곡을 건너뜁니다")
    async def skip(interaction: discord.Interaction):
        """현재 곡을 건너뜁니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            # MusicPlayer 확인
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

            # 명령어 사용 로깅
            await log_command_usage(
                command_name="스킵",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
                args={}
            )

            # 스킵
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

    @bot.tree.command(name="대기열", description="현재 대기열을 확인합니다")
    async def queue(interaction: discord.Interaction):
        """현재 대기열을 확인합니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            # MusicPlayer 확인
            if not MusicManager.has_player(guild_id):
                await interaction.response.send_message(
                    "재생 중인 음악이 없어요!",
                    ephemeral=True
                )
                return

            player = MusicManager.get_player(guild_id)

            # 명령어 사용 로깅
            await log_command_usage(
                command_name="대기열",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id,
                guild_name=interaction.guild.name,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
                args={}
            )

            # 대기열 정보
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

    print("[완료] 음악 명령어 등록 완료")
