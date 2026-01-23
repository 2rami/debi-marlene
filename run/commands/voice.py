"""
음성 채널 TTS 명령어

봇이 음성 채널에 입장하여 채팅을 읽어주는 기능입니다.
"""

import discord
from discord import app_commands
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
    """
    캐릭터에 맞는 TTS 서비스를 가져옵니다.

    Args:
        character: 캐릭터 이름

    Returns:
        TTS 서비스 인스턴스
    """
    global tts_services

    # 이미 로드된 서비스가 있으면 반환
    if character in tts_services:
        return tts_services[character]

    # CosyVoice3 사용
    logger.info(f"CosyVoice3 TTS 사용 ({character})")
    tts_service = TTSService(speaker=character)

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

            # 명령어 사용 로깅
            await log_command_usage(
                command_name="음성입장",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={}
            )

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

            # 명령어 사용 로깅
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

    @bot.tree.command(name="읽기채널설정", description="봇이 메시지를 읽어줄 채널을 설정합니다")
    @app_commands.describe(채널="메시지를 읽어줄 채널")
    @app_commands.default_permissions(administrator=True)
    async def set_tts_channel(
        interaction: discord.Interaction,
        채널: discord.TextChannel
    ):
        """TTS로 읽어줄 채널을 설정합니다."""
        # 즉시 defer (3초 타임아웃 방지)
        await interaction.response.defer(ephemeral=True)

        try:
            if not interaction.guild:
                await interaction.followup.send(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 관리자 권한 체크
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(
                    "이 명령어는 서버 관리자만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 명령어 사용 로깅
            await log_command_usage(
                command_name="읽기채널설정",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={"채널": 채널.name}
            )

            # 설정 저장
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

    @bot.tree.command(name="음성설정", description="TTS 음성을 설정합니다 (데비, 마를렌, 교대)")
    @app_commands.describe(음성="사용할 음성 선택")
    @app_commands.choices(음성=[
        app_commands.Choice(name="데비", value="debi"),
        app_commands.Choice(name="마를렌", value="marlene"),
        app_commands.Choice(name="교대 (데비+마를렌)", value="alternate"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def set_tts_voice(
        interaction: discord.Interaction,
        음성: app_commands.Choice[str]
    ):
        """TTS 음성을 설정합니다."""
        # 즉시 defer (3초 타임아웃 방지)
        await interaction.response.defer(ephemeral=True)

        try:
            if not interaction.guild:
                await interaction.followup.send(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 관리자 권한 체크
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(
                    "이 명령어는 서버 관리자만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            # 명령어 사용 로깅
            await log_command_usage(
                command_name="음성설정",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={"음성": 음성.name}
            )

            # 설정 저장
            settings = load_settings()
            guild_id = str(interaction.guild.id)

            if "guilds" not in settings:
                settings["guilds"] = {}
            if guild_id not in settings["guilds"]:
                settings["guilds"][guild_id] = {}

            settings["guilds"][guild_id]["tts_voice"] = 음성.value
            save_settings(settings)

            # 메시지 설명
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

            # 명령어 사용 로깅
            await log_command_usage(
                command_name="읽기채널해제",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={}
            )

            # 설정 삭제
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
        guild_settings = settings.get("guilds", {}).get(guild_id, {})

        # TTS 채널이 설정되어 있으면 해당 채널만 읽음
        tts_channel_id = guild_settings.get("tts_channel_id")
        if tts_channel_id and str(message.channel.id) != tts_channel_id:
            return

        # 메시지 내용이 없으면 무시
        if not message.content.strip():
            return

        # 서버 설정에서 음성 모드 확인 (기본값: alternate)
        tts_voice = guild_settings.get("tts_voice", "alternate")

        # 설정된 목소리가 있으면 그 목소리로만 말하기
        if tts_voice in ["debi", "marlene"]:
            logger.info(f"TTS 단일 목소리 모드: {tts_voice}")

            # 설정된 목소리로 TTS 생성
            tts_service = await get_tts_service(tts_voice)
            audio_path = await tts_service.text_to_speech(text=message.content)

            logger.info(f"TTS 변환 완료: {audio_path}")

            # 재생
            await audio_player.play_audio(guild_id, audio_path)
            logger.info("TTS 단일 목소리 재생 완료")

        else:
            # 설정이 없거나 "alternate"이면 교대로 말하기 모드
            logger.info("TTS 교대 모드: 데비와 마를렌 교대로 말하기")

            # 텍스트를 띄어쓰기로 분리
            words = message.content.strip().split()

            logger.info(f"TTS 교대 말하기: {len(words)}개 단어 처리")

            # 모든 단어의 오디오를 먼저 생성
            audio_segments = []

            for i, word in enumerate(words):
                if i == 0:
                    # 첫 번째 단어: 데비만
                    logger.info(f"[{i}] 데비: {word}")
                    tts_service = await get_tts_service("debi")
                    audio_path = await tts_service.text_to_speech(text=word)
                    audio_segments.append(audio_path)

                elif i == 1:
                    # 두 번째 단어: 마를렌만
                    logger.info(f"[{i}] 마를렌: {word}")
                    tts_service = await get_tts_service("marlene")
                    audio_path = await tts_service.text_to_speech(text=word)
                    audio_segments.append(audio_path)

                else:
                    # 세 번째 단어부터: 데비와 마를렌이 동시에
                    logger.info(f"[{i}] 데비 + 마를렌 동시: {word}")

                    # 데비 TTS
                    debi_service = await get_tts_service("debi")
                    debi_audio = await debi_service.text_to_speech(text=word)

                    # 마를렌 TTS
                    marlene_service = await get_tts_service("marlene")
                    marlene_audio = await marlene_service.text_to_speech(text=word)

                    # 두 오디오 믹싱
                    text_hash = hashlib.md5(f"{word}_mixed_{i}".encode()).hexdigest()[:8]
                    mixed_path = os.path.join("/tmp/tts_audio", f"mixed_{text_hash}.wav")

                    from run.services.tts.cosyvoice_service import mix_audio_files
                    mixed_audio = mix_audio_files(
                        [debi_audio, marlene_audio],
                        mixed_path
                    )

                    logger.info(f"TTS 믹싱 완료: {mixed_audio}")
                    audio_segments.append(mixed_audio)

            # 모든 오디오 세그먼트를 하나로 이어붙이기
            logger.info(f"총 {len(audio_segments)}개 오디오 세그먼트 이어붙이기 시작")

            message_hash = hashlib.md5(message.content.encode()).hexdigest()[:8]
            final_path = os.path.join("/tmp/tts_audio", f"final_{message_hash}.wav")

            from run.services.tts.cosyvoice_service import concatenate_audio_files
            final_audio = concatenate_audio_files(
                audio_segments,
                final_path
            )

            logger.info(f"최종 오디오 생성 완료: {final_audio}")

            # 최종 오디오 파일 하나만 재생
            await audio_player.play_audio(guild_id, final_audio)

            logger.info("TTS 교대 말하기 처리 완료")

    except Exception as e:
        logger.error(f"TTS 메시지 처리 오류: {e}")
