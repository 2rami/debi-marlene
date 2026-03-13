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
from run.services.tts.text_preprocessor import extract_segments_with_sfx, has_sfx_triggers, match_voice_line, preprocess_text_for_tts, split_text_for_tts
from run.services.tts.audio_utils import convert_to_discord_pcm
from run.core.config import load_settings, save_settings
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

# 효과음 파일 경로
SFX_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")

# 전역 인스턴스
audio_player: Optional[AudioPlayer] = None

# 캐릭터별 TTS 서비스 캐시
tts_services: dict = {}

# 서버별 TTS 재생 큐 (생성은 병렬, 재생은 순서대로)
tts_playback_queues: Dict[str, asyncio.Queue] = {}
tts_workers: Dict[str, asyncio.Task] = {}


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

    # 효과음 이름에 맞는 파일 찾기 (대소문자 무시)
    sfx_name_lower = sfx_name.lower()
    sfx_files = [
        f for f in os.listdir(sfx_character_dir)
        if sfx_name_lower in f.lower() and f.endswith(".wav")
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

            try:
                await interaction.response.defer(ephemeral=True)
            except discord.NotFound:
                logger.warning("음성입장: interaction 만료됨 (3초 초과)")
                return

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

            # 기존 연결이 죽어있으면 정리 후 재연결
            from run.services.voice_manager import voice_manager
            guild_id_str = str(interaction.guild.id)
            vc = voice_manager.get_voice_client(guild_id_str)
            if vc and not vc.is_connected():
                await voice_manager.leave(guild_id_str)

            success = await audio_player.join_voice_channel(voice_channel)

            if success:
                # 읽을 채널 정보 가져오기
                guild_id = str(interaction.guild.id)
                settings = load_settings()
                guild_settings = settings.get("guilds", {}).get(guild_id, {})
                tts_channel_id = guild_settings.get("tts_channel_id")

                if tts_channel_id:
                    tts_channel = interaction.guild.get_channel(int(tts_channel_id))
                    channel_info = f"읽을 채널: {tts_channel.mention}" if tts_channel else f"읽을 채널: (삭제된 채널)"
                else:
                    channel_info = "읽을 채널: 모든 채널"

                embed = discord.Embed(
                    title="음성 채널 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               f"{channel_info}\n"
                               "TTS 서버를 준비하고 있어요...",
                    color=0xFFA500
                )
                msg = await interaction.followup.send(embed=embed, ephemeral=True, wait=True)

                # Modal TTS 서버 선제 워밍업 (백그라운드)
                asyncio.create_task(self._warmup_and_notify(msg, voice_channel, channel_info))
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

    async def _warmup_and_notify(self, msg: discord.WebhookMessage, voice_channel, channel_info: str):
        """Modal TTS 서버를 깨우고 완료되면 메시지를 업데이트합니다."""
        try:
            from run.services.tts.cosyvoice3_client import CosyVoice3Client
            results = await CosyVoice3Client.warmup_all_servers()

            all_ready = all(s == "running" for s in results.values())
            if all_ready:
                embed = discord.Embed(
                    title="음성 채널 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               f"{channel_info}\n"
                               "TTS 서버 준비 완료! 바로 사용할 수 있어요.",
                    color=0x00FF00
                )
            else:
                status_lines = []
                for name, status in results.items():
                    mark = "[OK]" if status == "running" else "[준비중]" if status == "starting" else "[오류]"
                    status_lines.append(f"{mark} {name}")
                embed = discord.Embed(
                    title="음성 채널 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               f"{channel_info}\n\n"
                               "TTS 서버 상태:\n" + "\n".join(status_lines) + "\n\n"
                               "준비중인 서버는 첫 메시지에서 시간이 걸릴 수 있어요.",
                    color=0xFFA500
                )

            await msg.edit(embed=embed)
        except Exception as e:
            logger.warning(f"TTS 워밍업 알림 실패: {e}")

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

    @app_commands.command(name="목소리", description="서버 기본 TTS 음성을 설정합니다 (관리자)")
    @app_commands.describe(음성="서버 기본 음성 선택")
    @app_commands.choices(음성=[
        app_commands.Choice(name="데비", value="debi"),
        app_commands.Choice(name="마를렌", value="marlene"),
        app_commands.Choice(name="알렉스", value="alex"),
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

    @app_commands.command(name="내목소리", description="내가 사용할 TTS 목소리를 선택합니다")
    @app_commands.describe(목소리="사용할 목소리 선택")
    @app_commands.choices(목소리=[
        app_commands.Choice(name="데비", value="debi"),
        app_commands.Choice(name="마를렌", value="marlene"),
        app_commands.Choice(name="알렉스", value="alex"),
        app_commands.Choice(name="서버 기본값", value="default"),
    ])
    async def set_my_voice(
        self,
        interaction: discord.Interaction,
        목소리: app_commands.Choice[str]
    ):
        """유저 개인 TTS 목소리를 설정합니다."""
        await interaction.response.defer(ephemeral=True)

        try:
            if not interaction.guild:
                await interaction.followup.send(
                    "이 명령어는 서버에서만 사용할 수 있어요!",
                    ephemeral=True
                )
                return

            await log_command_usage(
                command_name="내목소리",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
                args={"목소리": 목소리.name}
            )

            settings = load_settings()
            guild_id = str(interaction.guild.id)
            user_id = str(interaction.user.id)

            if "guilds" not in settings:
                settings["guilds"] = {}
            if guild_id not in settings["guilds"]:
                settings["guilds"][guild_id] = {}

            guild_settings = settings["guilds"][guild_id]

            if 목소리.value == "default":
                # 개인 설정 삭제 -> 서버 기본값 사용
                if "user_voices" in guild_settings and user_id in guild_settings["user_voices"]:
                    del guild_settings["user_voices"][user_id]
                save_settings(settings)

                server_voice = guild_settings.get("tts_voice", "debi")
                embed = discord.Embed(
                    title="내 목소리 설정 해제",
                    description=f"서버 기본값({server_voice})으로 돌아갔어요!",
                    color=0x7289DA
                )
            else:
                if "user_voices" not in guild_settings:
                    guild_settings["user_voices"] = {}
                guild_settings["user_voices"][user_id] = 목소리.value
                save_settings(settings)

                embed = discord.Embed(
                    title="내 목소리 설정 완료",
                    description=f"{목소리.name} 목소리로 내 메시지를 읽어드릴게요!",
                    color=0x7289DA
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"내목소리 명령어 오류: {e}")
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


def _ensure_playback_worker(guild_id: str):
    """재생 워커가 실행 중인지 확인하고, 없으면 시작합니다."""
    if guild_id not in tts_playback_queues:
        tts_playback_queues[guild_id] = asyncio.Queue()
    task = tts_workers.get(guild_id)
    if task is None or task.done():
        tts_workers[guild_id] = asyncio.create_task(_playback_worker(guild_id))


async def _playback_worker(guild_id: str):
    """
    재생 워커: Future를 순서대로 await하고 오디오를 재생합니다.

    여러 메시지가 동시에 TTS를 생성하더라도, 이 워커가 순서를 보장합니다.
    """
    from run.services.voice_manager import voice_manager

    queue = tts_playback_queues[guild_id]
    while True:
        try:
            future = await asyncio.wait_for(queue.get(), timeout=120.0)
        except asyncio.TimeoutError:
            break

        if future is None:
            break

        try:
            audio_path = await future
            if audio_path and voice_manager.is_connected(guild_id):
                await voice_manager.play_tts(guild_id, audio_path)
        except Exception as e:
            logger.error(f"TTS 재생 오류: {e}")

    tts_workers.pop(guild_id, None)


async def _generate_tts_audio(
    future: asyncio.Future,
    message: discord.Message,
    guild_id: str,
    guild_settings: dict
):
    """TTS 오디오를 생성하고 PCM 변환 후 Future에 결과를 설정합니다."""
    try:
        # 유저별 목소리 우선, 없으면 서버 기본값
        user_id = str(message.author.id)
        user_voices = guild_settings.get("user_voices", {})
        tts_voice = user_voices.get(user_id) or guild_settings.get("tts_voice", "debi")
        if tts_voice not in ["debi", "marlene", "alex"]:
            tts_voice = "debi"

        meta = {
            "guild_name": message.guild.name if message.guild else None,
            "channel_name": message.channel.name if hasattr(message.channel, 'name') else None,
            "user_name": message.author.display_name or message.author.name
        }

        audio_path = None

        # 게임 대사 매칭 (metadata.csv 기반, 정확한 대사 → 즉시 재생)
        voice_line_path = match_voice_line(message.content, tts_voice)
        if voice_line_path:
            audio_path = voice_line_path
            logger.info(f"대사 매칭: '{message.content}' -> {os.path.basename(voice_line_path)}")

        # 효과음 트리거 확인
        if audio_path is None and has_sfx_triggers(message.content):
            segments = extract_segments_with_sfx(message.content)
            audio_segments = []
            for seg in segments:
                if seg["type"] == "text" and seg["content"].strip():
                    tts_service = await get_tts_service(tts_voice)
                    path = await tts_service.text_to_speech(text=seg["content"], **meta)
                    audio_segments.append(path)
                elif seg["type"] == "sfx":
                    sfx_path = get_random_sfx(seg["name"], tts_voice)
                    if sfx_path:
                        audio_segments.append(sfx_path)

            if len(audio_segments) == 1:
                audio_path = audio_segments[0]
            elif len(audio_segments) > 1:
                msg_hash = hashlib.md5(message.content.encode()).hexdigest()[:8]
                final_path = os.path.join("/tmp/tts_audio", f"sfx_{msg_hash}.wav")
                from run.services.tts.audio_utils import concatenate_audio_files
                audio_path = concatenate_audio_files(audio_segments, final_path)

        if audio_path is None:
            # 300자 이상이면 간단 응답
            if len(message.content) > 300:
                tts_service = await get_tts_service(tts_voice)
                short_msgs = [
                    "너무 길어서 못 읽겠어요.",
                    "힘들어서 못 말하겠어.",
                    "이건 좀 길어요.",
                    "요약 부탁드려요."
                ]
                audio_path = await tts_service.text_to_speech(text=random.choice(short_msgs), **meta)
            else:
                tts_service = await get_tts_service(tts_voice)
                processed_text = preprocess_text_for_tts(message.content)
                audio_path = await tts_service.text_to_speech(text=processed_text, **meta)

        # 모든 오디오를 Discord PCM으로 변환 (재생 시 FFmpeg 불필요)
        if audio_path:
            audio_path = await convert_to_discord_pcm(audio_path)

        future.set_result(audio_path)

    except Exception as e:
        logger.error(f"TTS 생성 오류: {e}", exc_info=True)
        if not future.done():
            future.set_result(None)


# 메시지 이벤트 핸들러
async def handle_tts_message(message: discord.Message):
    """메시지를 TTS로 읽어줍니다."""
    from run.services.voice_manager import voice_manager

    if message.author.bot:
        return

    if not message.guild:
        return

    guild_id = str(message.guild.id)

    if not voice_manager.is_connected(guild_id):
        return

    if voice_manager.is_music_playing(guild_id):
        return

    await initialize_audio_player()

    settings = load_settings()
    guild_settings = settings.get("guilds", {}).get(guild_id, {})

    tts_channel_id = guild_settings.get("tts_channel_id")
    if tts_channel_id and str(message.channel.id) != tts_channel_id:
        return

    if not message.content.strip():
        return

    print(f"[TTS] {message.author.name}: {message.content[:30]}", flush=True)

    # 재생 큐에 Future 추가 (메시지 순서 보장)
    _ensure_playback_worker(guild_id)
    future = asyncio.get_running_loop().create_future()
    await tts_playback_queues[guild_id].put(future)

    # TTS 생성을 백그라운드로 실행 (여러 메시지 동시 생성)
    asyncio.create_task(_generate_tts_audio(future, message, guild_id, guild_settings))


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
