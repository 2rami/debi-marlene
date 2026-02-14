"""
음성 Cog

TTS 관련 명령어: 음성입장, 음성퇴장, 음성설정, 읽기채널설정, 읽기채널해제
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Dict
import logging
import os
import hashlib
import random
import asyncio

from run.services.tts import TTSService, AudioPlayer
from run.services.tts.text_preprocessor import extract_segments_with_sfx, has_sfx_triggers, preprocess_text_for_tts, split_text_for_tts
from run.core.config import load_settings, save_settings
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

# 효과음 파일 경로
SFX_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")

# 전역 인스턴스
audio_player: Optional[AudioPlayer] = None

# 캐릭터별 TTS 서비스 캐시
tts_services: dict = {}

# 서버별 TTS 처리 락 (메시지 순서 보장)
tts_locks: Dict[str, asyncio.Lock] = {}


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


def get_random_sfx(sfx_name: str, character: str = "debi") -> Optional[str]:
    """랜덤 효과음 파일 경로를 반환합니다."""
    sfx_character_dir = os.path.join(SFX_DIR, character)

    if not os.path.exists(sfx_character_dir):
        logger.warning(f"효과음 폴더 없음: {sfx_character_dir}")
        return None

    # 효과음 이름에 맞는 파일 찾기
    sfx_files = [
        f for f in os.listdir(sfx_character_dir)
        if sfx_name in f.lower() and f.endswith(".wav")
    ]

    if not sfx_files:
        logger.warning(f"{character}의 {sfx_name} 효과음 파일 없음")
        return None

    selected = random.choice(sfx_files)
    return os.path.join(sfx_character_dir, selected)


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
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
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
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
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
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
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

    @app_commands.command(name="목소리", description="TTS 음성을 설정합니다 (데비/마를렌)")
    @app_commands.describe(음성="사용할 음성 선택")
    @app_commands.choices(음성=[
        app_commands.Choice(name="데비", value="debi"),
        app_commands.Choice(name="마를렌", value="marlene"),
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
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
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

            embed = discord.Embed(
                title="TTS 음성 설정 완료",
                description=f"{음성.name} 목소리로 메시지를 읽어드릴게요!",
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
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
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


# 메시지 이벤트 핸들러
async def handle_tts_message(message: discord.Message):
    """메시지를 TTS로 읽어줍니다."""
    from run.services.voice_manager import voice_manager

    if message.author.bot:
        return

    if not message.guild:
        return

    guild_id = str(message.guild.id)

    # 음성 채널에 연결되어 있는지 확인 (TTS 또는 음악으로 연결)
    if not voice_manager.is_connected(guild_id):
        return

    # 음악 재생 중이면 TTS 건너뛰기
    if voice_manager.is_music_playing(guild_id):
        return

    # audio_player가 없으면 초기화
    await initialize_audio_player()

    # 설정 확인 (락 전에 빠르게)
    settings = load_settings()
    guild_settings = settings.get("guilds", {}).get(guild_id, {})

    tts_channel_id = guild_settings.get("tts_channel_id")
    if tts_channel_id and str(message.channel.id) != tts_channel_id:
        return

    if not message.content.strip():
        return

    # 서버별 락 획득 (메시지 순서 보장)
    if guild_id not in tts_locks:
        tts_locks[guild_id] = asyncio.Lock()

    async with tts_locks[guild_id]:
        try:
            tts_voice = guild_settings.get("tts_voice", "debi")

            # alternate가 설정된 경우 debi로 대체 (교대 모드 제거됨)
            if tts_voice not in ["debi", "marlene"]:
                tts_voice = "debi"

            logger.info(f"TTS 목소리: {tts_voice}")

            # 메타데이터 (Modal 로깅용)
            meta = {
                "guild_name": message.guild.name if message.guild else None,
                "channel_name": message.channel.name if hasattr(message.channel, 'name') else None,
                "user_name": message.author.display_name or message.author.name
            }

            # 효과음 트리거 확인 (ㅋ 6개 이상 등)
            sfx_handled = False
            if has_sfx_triggers(message.content):
                segments = extract_segments_with_sfx(message.content)
                logger.info(f"효과음 감지됨. 세그먼트: {len(segments)}개")

                audio_segments = []
                for seg in segments:
                    if seg["type"] == "text" and seg["content"].strip():
                        tts_service = await get_tts_service(tts_voice)
                        audio_path = await tts_service.text_to_speech(text=seg["content"], **meta)
                        audio_segments.append(audio_path)
                    elif seg["type"] == "sfx":
                        sfx_path = get_random_sfx(seg["name"], tts_voice)
                        if sfx_path:
                            audio_segments.append(sfx_path)
                            logger.info(f"효과음 추가: {seg['name']} -> {os.path.basename(sfx_path)}")

                # 세그먼트 이어붙이기
                if len(audio_segments) == 1:
                    await audio_player.play_audio(guild_id, audio_segments[0])
                    sfx_handled = True
                elif len(audio_segments) > 1:
                    message_hash = hashlib.md5(message.content.encode()).hexdigest()[:8]
                    final_path = os.path.join("/tmp/tts_audio", f"sfx_{message_hash}.wav")

                    from run.services.tts.audio_utils import concatenate_audio_files
                    final_audio = concatenate_audio_files(audio_segments, final_path)
                    await audio_player.play_audio(guild_id, final_audio)
                    sfx_handled = True

                if sfx_handled:
                    logger.info("TTS + 효과음 재생 완료")
                else:
                    logger.warning(f"효과음 파일 없음, 일반 TTS로 폴백: {message.content}")

            if not sfx_handled:
                # 효과음 없음 - 일반 TTS
                # 300자 이상이면 "너무 길어서 못 읽겠어요" 메시지 재생
                if len(message.content) > 300:
                    import random
                    logger.info(f"긴 문장 감지 ({len(message.content)}자) - 간단 응답")
                    tts_service = await get_tts_service(tts_voice)
                    short_msgs = [
                        "너무 길어서 못 읽겠어요.",
                        "힘들어서 못 말하겠어.",
                        "이건 좀 길어요.",
                        "요약 부탁드려요."
                    ]
                    short_msg = random.choice(short_msgs)
                    audio_path = await tts_service.text_to_speech(text=short_msg, **meta)
                    await audio_player.play_audio(guild_id, audio_path)
                    logger.info(f"긴 문장 간단 응답 재생: {short_msg}")
                else:
                    tts_service = await get_tts_service(tts_voice)
                    processed_text = preprocess_text_for_tts(message.content)
                    chunks = split_text_for_tts(processed_text)

                    if len(chunks) <= 1:
                        # 짧은 메시지: 기존 방식
                        audio_path = await tts_service.text_to_speech(text=processed_text, **meta)
                        logger.info(f"TTS 변환 완료: {audio_path}")
                        await audio_player.play_audio(guild_id, audio_path)
                    else:
                        # 긴 메시지: 파이프라인 방식 (생성과 재생 동시 진행)
                        logger.info(f"청크 TTS 시작: {len(chunks)}개 청크")
                        await audio_player.play_chunked(guild_id, chunks, tts_service, meta)
                    logger.info("TTS 재생 완료")

        except Exception as e:
            logger.error(f"TTS 메시지 처리 오류: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
