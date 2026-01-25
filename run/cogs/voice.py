"""
음성 Cog

TTS 관련 명령어: 음성입장, 음성퇴장, 음성설정, 읽기채널설정, 읽기채널해제
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import logging
import os
import hashlib

from run.services.tts import TTSService, AudioPlayer
from run.core.config import load_settings, save_settings
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

# 전역 인스턴스
audio_player: Optional[AudioPlayer] = None

# 캐릭터별 TTS 서비스 캐시
tts_services: dict = {}


async def get_tts_service(character: str = "default") -> TTSService:
    """캐릭터에 맞는 TTS 서비스를 가져옵니다."""
    global tts_services

    if character in tts_services:
        return tts_services[character]

    logger.info(f"Qwen3-TTS 사용 ({character})")
    tts_service = TTSService(speaker=character)
    await tts_service.initialize()
    tts_services[character] = tts_service

    return tts_service


async def initialize_audio_player():
    """오디오 플레이어를 초기화합니다."""
    global audio_player

    if audio_player is None:
        audio_player = AudioPlayer()
        logger.info("오디오 플레이어 초기화 완료")


class VoiceCog(commands.GroupCog, group_name="음성"):
    """음성 채널 TTS 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="입장", description="봇이 음성 채널에 입장합니다")
    async def voice_join(self, interaction: discord.Interaction):
        """봇을 음성 채널에 입장시킵니다."""
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

            await interaction.response.defer(ephemeral=True)

            await log_command_usage(
                command_name="음성입장",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={}
            )

            await initialize_audio_player()

            voice_channel = interaction.user.voice.channel
            success = await audio_player.join_voice_channel(voice_channel)

            if success:
                embed = discord.Embed(
                    title="음성 채널 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               "이제 채팅을 읽어드릴게요.\n"
                               "`/음성 채널설정`으로 읽을 채널을 지정할 수 있어요.",
                    color=0x00FF00
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "음성 채널 입장에 실패했어요. 다시 시도해주세요.",
                    ephemeral=True
                )

        except Exception as e:
            import traceback
            logger.error(f"음성입장 명령어 오류: {e}")
            logger.error(traceback.format_exc())
            try:
                await interaction.followup.send(
                    f"오류가 발생했어요: {str(e)}",
                    ephemeral=True
                )
            except:
                pass

    @app_commands.command(name="퇴장", description="봇이 음성 채널에서 퇴장합니다")
    async def voice_leave(self, interaction: discord.Interaction):
        """봇을 음성 채널에서 퇴장시킵니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            if not audio_player or not audio_player.is_connected(guild_id):
                await interaction.response.send_message(
                    "봇이 음성 채널에 연결되어 있지 않아요!",
                    ephemeral=True
                )
                return

            await interaction.response.defer(ephemeral=True)

            await log_command_usage(
                command_name="음성퇴장",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={}
            )

            success = await audio_player.leave_voice_channel(guild_id)

            if success:
                embed = discord.Embed(
                    title="음성 채널 퇴장",
                    description="음성 채널에서 퇴장했어요!",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "음성 채널 퇴장에 실패했어요.",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"음성퇴장 명령어 오류: {e}")
            try:
                await interaction.followup.send(
                    f"오류가 발생했어요: {str(e)}",
                    ephemeral=True
                )
            except:
                pass

    @app_commands.command(name="채널설정", description="메시지를 읽어줄 채널을 설정합니다")
    @app_commands.describe(채널="메시지를 읽어줄 채널")
    @app_commands.default_permissions(administrator=True)
    async def set_tts_channel(
        self,
        interaction: discord.Interaction,
        채널: discord.TextChannel
    ):
        """TTS로 읽어줄 채널을 설정합니다."""
        await interaction.response.defer(ephemeral=True)

        try:
            if not interaction.guild:
                await interaction.followup.send(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(
                    "이 명령어는 서버 관리자만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            await log_command_usage(
                command_name="읽기채널설정",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={"채널": 채널.name}
            )

            settings = load_settings()
            guild_id = str(interaction.guild.id)

            if "guilds" not in settings:
                settings["guilds"] = {}
            if guild_id not in settings["guilds"]:
                settings["guilds"][guild_id] = {}

            settings["guilds"][guild_id]["tts_channel_id"] = str(채널.id)
            save_settings(settings)

            embed = discord.Embed(
                title="TTS 채널 설정 완료",
                description=f"{채널.mention} 채널의 메시지를 읽어드릴게요!",
                color=0x7289DA
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"읽기채널설정 명령어 오류: {e}")
            try:
                await interaction.followup.send(
                    f"오류가 발생했어요: {str(e)}",
                    ephemeral=True
                )
            except:
                pass

    @app_commands.command(name="목소리", description="TTS 음성을 설정합니다 (데비/마를렌/교대)")
    @app_commands.describe(음성="사용할 음성 선택")
    @app_commands.choices(음성=[
        app_commands.Choice(name="데비", value="debi"),
        app_commands.Choice(name="마를렌", value="marlene"),
        app_commands.Choice(name="교대 (데비+마를렌)", value="alternate"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def set_tts_voice(
        self,
        interaction: discord.Interaction,
        음성: app_commands.Choice[str]
    ):
        """TTS 음성을 설정합니다."""
        await interaction.response.defer(ephemeral=True)

        try:
            if not interaction.guild:
                await interaction.followup.send(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(
                    "이 명령어는 서버 관리자만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            await log_command_usage(
                command_name="음성설정",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={"음성": 음성.name}
            )

            settings = load_settings()
            guild_id = str(interaction.guild.id)

            if "guilds" not in settings:
                settings["guilds"] = {}
            if guild_id not in settings["guilds"]:
                settings["guilds"][guild_id] = {}

            settings["guilds"][guild_id]["tts_voice"] = 음성.value
            save_settings(settings)

            if 음성.value == "alternate":
                description = (
                    "교대 모드가 설정되었어요!\n\n"
                    "1번째 단어: 데비\n"
                    "2번째 단어: 마를렌\n"
                    "3번째 이후: 데비 + 마를렌 동시에"
                )
            else:
                description = f"{음성.name} 목소리로 메시지를 읽어드릴게요!"

            embed = discord.Embed(
                title="TTS 음성 설정 완료",
                description=description,
                color=0x7289DA
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"음성설정 명령어 오류: {e}")
            try:
                await interaction.followup.send(
                    f"오류가 발생했어요: {str(e)}",
                    ephemeral=True
                )
            except:
                pass

    @app_commands.command(name="채널해제", description="TTS 채널 설정을 해제합니다")
    @app_commands.default_permissions(administrator=True)
    async def unset_tts_channel(self, interaction: discord.Interaction):
        """TTS 채널 설정을 해제합니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "이 명령어는 서버 관리자만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            await log_command_usage(
                command_name="읽기채널해제",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={}
            )

            settings = load_settings()
            guild_id = str(interaction.guild.id)

            if "guilds" in settings and guild_id in settings["guilds"] and "tts_channel_id" in settings["guilds"][guild_id]:
                del settings["guilds"][guild_id]["tts_channel_id"]
                save_settings(settings)

                embed = discord.Embed(
                    title="TTS 채널 설정 해제",
                    description="이제 모든 채널의 메시지를 읽어드릴게요!",
                    color=0x7289DA
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    "TTS 채널이 설정되어 있지 않아요!",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"읽기채널해제 명령어 오류: {e}")
            await interaction.response.send_message(
                f"오류가 발생했어요: {str(e)}",
                ephemeral=True
            )


# 메시지 이벤트 핸들러 (기존 코드 유지)
async def handle_tts_message(message: discord.Message):
    """메시지를 TTS로 읽어줍니다."""
    if message.author.bot:
        return

    if not message.guild:
        return

    guild_id = str(message.guild.id)

    if not audio_player or not audio_player.is_connected(guild_id):
        return

    try:
        settings = load_settings()
        guild_settings = settings.get("guilds", {}).get(guild_id, {})

        tts_channel_id = guild_settings.get("tts_channel_id")
        if tts_channel_id and str(message.channel.id) != tts_channel_id:
            return

        if not message.content.strip():
            return

        tts_voice = guild_settings.get("tts_voice", "alternate")

        if tts_voice in ["debi", "marlene"]:
            logger.info(f"TTS 단일 목소리 모드: {tts_voice}")

            tts_service = await get_tts_service(tts_voice)
            audio_path = await tts_service.text_to_speech(text=message.content)

            logger.info(f"TTS 변환 완료: {audio_path}")
            await audio_player.play_audio(guild_id, audio_path)
            logger.info("TTS 단일 목소리 재생 완료")

        else:
            logger.info("TTS 교대 모드: 데비와 마를렌 교대로 말하기")

            words = message.content.strip().split()
            logger.info(f"TTS 교대 말하기: {len(words)}개 단어 처리")

            audio_segments = []

            for i, word in enumerate(words):
                if i == 0:
                    logger.info(f"[{i}] 데비: {word}")
                    tts_service = await get_tts_service("debi")
                    audio_path = await tts_service.text_to_speech(text=word)
                    audio_segments.append(audio_path)

                elif i == 1:
                    logger.info(f"[{i}] 마를렌: {word}")
                    tts_service = await get_tts_service("marlene")
                    audio_path = await tts_service.text_to_speech(text=word)
                    audio_segments.append(audio_path)

                else:
                    logger.info(f"[{i}] 데비 + 마를렌 동시: {word}")

                    debi_service = await get_tts_service("debi")
                    debi_audio = await debi_service.text_to_speech(text=word)

                    marlene_service = await get_tts_service("marlene")
                    marlene_audio = await marlene_service.text_to_speech(text=word)

                    text_hash = hashlib.md5(f"{word}_mixed_{i}".encode()).hexdigest()[:8]
                    mixed_path = os.path.join("/tmp/tts_audio", f"mixed_{text_hash}.wav")

                    from run.services.tts.audio_utils import mix_audio_files
                    mixed_audio = mix_audio_files(
                        [debi_audio, marlene_audio],
                        mixed_path
                    )

                    logger.info(f"TTS 믹싱 완료: {mixed_audio}")
                    audio_segments.append(mixed_audio)

            logger.info(f"총 {len(audio_segments)}개 오디오 세그먼트 이어붙이기 시작")

            message_hash = hashlib.md5(message.content.encode()).hexdigest()[:8]
            final_path = os.path.join("/tmp/tts_audio", f"final_{message_hash}.wav")

            from run.services.tts.audio_utils import concatenate_audio_files
            final_audio = concatenate_audio_files(
                audio_segments,
                final_path
            )

            logger.info(f"최종 오디오 생성 완료: {final_audio}")
            await audio_player.play_audio(guild_id, final_audio)
            logger.info("TTS 교대 말하기 처리 완료")

    except Exception as e:
        logger.error(f"TTS 메시지 처리 오류: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
