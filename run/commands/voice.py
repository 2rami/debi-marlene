"""
음성 채널 TTS 명령어

봇이 음성 채널에 입장하여 채팅을 읽어주는 기능입니다.
"""

import discord
from discord import app_commands
from typing import Optional
import logging

from run.services.tts import TTSService, VoiceManager, AudioPlayer
from run.core.config import load_settings, save_settings

logger = logging.getLogger(__name__)

# 전역 인스턴스
voice_manager: Optional[VoiceManager] = None
audio_player: Optional[AudioPlayer] = None

# 캐릭터별 TTS 서비스 캐시
tts_services: dict = {}


async def get_tts_service(character: str = "default") -> TTSService:
    """
    캐릭터에 맞는 TTS 서비스를 가져옵니다.

    Args:
        character: 캐릭터 이름

    Returns:
        TTS 서비스 인스턴스
    """
    global voice_manager, tts_services

    # 이미 로드된 서비스가 있으면 반환
    if character in tts_services:
        return tts_services[character]

    # VoiceManager 초기화
    if voice_manager is None:
        voice_manager = VoiceManager()

    # 캐릭터 모델 경로 가져오기
    model_paths = voice_manager.get_model_paths(character)

    if model_paths:
        model_path, config_path = model_paths
        logger.info(f"캐릭터 '{character}' 모델 로드")
        tts_service = TTSService(model_path=model_path, config_path=config_path)
    else:
        logger.info(f"캐릭터 '{character}' 모델이 없어 기본 한국어 모델 사용")
        tts_service = TTSService()

    await tts_service.initialize()

    # 캐시에 저장
    tts_services[character] = tts_service

    return tts_service


async def initialize_audio_player():
    """오디오 플레이어를 초기화합니다."""
    global audio_player

    if audio_player is None:
        audio_player = AudioPlayer()
        logger.info("오디오 플레이어 초기화 완료")


async def setup_voice_commands(bot):
    """
    음성 채널 TTS 명령어들을 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="음성입장", description="봇이 음성 채널에 입장하여 채팅을 읽어줍니다")
    async def voice_join(interaction: discord.Interaction):
        """봇을 음성 채널에 입장시킵니다."""
        try:
            # 서버에서만 사용 가능
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

            # 오디오 플레이어 초기화
            await interaction.response.defer(ephemeral=True)
            await initialize_audio_player()

            # 음성 채널 입장
            voice_channel = interaction.user.voice.channel
            success = await audio_player.join_voice_channel(voice_channel)

            if success:
                embed = discord.Embed(
                    title="음성 채널 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               "이제 채팅을 읽어드릴게요.\n"
                               "`/읽기채널설정`으로 읽을 채널을 지정할 수 있어요.",
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

    @bot.tree.command(name="음성퇴장", description="봇이 음성 채널에서 퇴장합니다")
    async def voice_leave(interaction: discord.Interaction):
        """봇을 음성 채널에서 퇴장시킵니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)

            # 음성 채널에 연결되어 있는지 확인
            if not audio_player or not audio_player.is_connected(guild_id):
                await interaction.response.send_message(
                    "봇이 음성 채널에 연결되어 있지 않아요!",
                    ephemeral=True
                )
                return

            # 퇴장
            await interaction.response.defer(ephemeral=True)
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

    @bot.tree.command(name="읽기채널설정", description="봇이 메시지를 읽어줄 채널을 설정합니다")
    @app_commands.describe(채널="메시지를 읽어줄 채널")
    @app_commands.default_permissions(administrator=True)
    async def set_tts_channel(
        interaction: discord.Interaction,
        채널: discord.TextChannel
    ):
        """TTS로 읽어줄 채널을 설정합니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 관리자 권한 체크
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "이 명령어는 서버 관리자만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 설정 저장
            settings = load_settings()
            guild_id = str(interaction.guild.id)

            if guild_id not in settings:
                settings[guild_id] = {}

            settings[guild_id]["tts_channel_id"] = str(채널.id)
            save_settings(settings)

            embed = discord.Embed(
                title="TTS 채널 설정 완료",
                description=f"{채널.mention} 채널의 메시지를 읽어드릴게요!",
                color=0x7289DA
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"읽기채널설정 명령어 오류: {e}")
            await interaction.response.send_message(
                f"오류가 발생했어요: {str(e)}",
                ephemeral=True
            )

    @bot.tree.command(name="읽기채널해제", description="TTS 채널 설정을 해제합니다")
    @app_commands.default_permissions(administrator=True)
    async def unset_tts_channel(interaction: discord.Interaction):
        """TTS 채널 설정을 해제합니다."""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 관리자 권한 체크
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "이 명령어는 서버 관리자만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 설정 삭제
            settings = load_settings()
            guild_id = str(interaction.guild.id)

            if guild_id in settings and "tts_channel_id" in settings[guild_id]:
                del settings[guild_id]["tts_channel_id"]
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



# 메시지 이벤트 핸들러
async def handle_tts_message(message: discord.Message):
    """
    메시지를 TTS로 읽어줍니다.

    Args:
        message: 읽어줄 메시지
    """
    # 봇 자신의 메시지는 무시
    if message.author.bot:
        return

    # DM은 무시
    if not message.guild:
        return

    guild_id = str(message.guild.id)

    # 봇이 음성 채널에 연결되어 있는지 확인
    if not audio_player or not audio_player.is_connected(guild_id):
        return

    try:
        # 설정 확인
        settings = load_settings()
        guild_settings = settings.get(guild_id, {})

        # TTS 채널이 설정되어 있으면 해당 채널만 읽음
        tts_channel_id = guild_settings.get("tts_channel_id")
        if tts_channel_id and str(message.channel.id) != tts_channel_id:
            return

        # 메시지 내용이 없으면 무시
        if not message.content.strip():
            return

        # 캐릭터 설정 가져오기 (기본값: default)
        character = guild_settings.get("tts_character", "default")

        # 캐릭터에 맞는 TTS 서비스 가져오기
        tts_service = await get_tts_service(character)
        logger.info(f"TTS 서비스 가져오기 완료: {character}")

        # TTS 변환
        audio_path = await tts_service.text_to_speech(text=message.content)
        logger.info(f"TTS 변환 완료: {audio_path}")

        # 재생
        logger.info(f"오디오 재생 시작: {audio_path}")
        await audio_player.play_audio(guild_id, audio_path)
        logger.info("오디오 재생 완료")

    except Exception as e:
        logger.error(f"TTS 메시지 처리 오류: {e}")
