"""
음성 Cog

TTS 관련 명령어: /tts
설정(목소리, 채널, 퇴장)은 버튼/드롭다운으로 제공
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


class VoiceCog(commands.Cog, name="TTS"):
    """음성 채널 TTS 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tts", description="봇이 음성 채널에 입장합니다")
    async def tts_join(self, interaction: discord.Interaction):
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
                logger.warning("tts: interaction 만료됨 (3초 초과)")
                return

            await log_command_usage(
                command_name="tts",
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
                guild_id = str(interaction.guild.id)
                settings = load_settings()
                guild_settings = settings.get("guilds", {}).get(guild_id, {})
                tts_channel_id = guild_settings.get("tts_channel_id")

                if tts_channel_id:
                    tts_channel = interaction.guild.get_channel(int(tts_channel_id))
                    channel_info = f"읽을 채널: {tts_channel.mention}" if tts_channel else "읽을 채널: (삭제된 채널)"
                else:
                    channel_info = "읽을 채널: 모든 채널"

                # 현재 목소리 정보
                user_id = str(interaction.user.id)
                user_voices = guild_settings.get("user_voices", {})
                current_voice = user_voices.get(user_id) or guild_settings.get("tts_voice", "debi")
                voice_names = {"debi": "데비", "marlene": "마를렌", "alex": "알렉스"}
                voice_display = voice_names.get(current_voice, current_voice)

                embed = discord.Embed(
                    title="TTS 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               f"{channel_info}\n"
                               f"내 목소리: **{voice_display}**\n\n"
                               "TTS 서버를 준비하고 있어요...",
                    color=0xFFA500
                )

                is_admin = interaction.user.guild_permissions.administrator
                view = TTSControlView(guild_id, interaction.user.id, is_admin)
                msg = await interaction.followup.send(embed=embed, view=view, ephemeral=True, wait=True)
                view.message = msg

                # Modal TTS 서버 선제 워밍업 (백그라운드)
                asyncio.create_task(self._warmup_and_notify(msg, voice_channel, channel_info, voice_display, is_admin, guild_id, interaction.user.id))
            else:
                await interaction.followup.send(
                    "음성 채널 입장에 실패했어요. 다시 시도해주세요.",
                    ephemeral=True
                )

        except Exception as e:
            import traceback
            logger.error(f"tts 명령어 오류: {e}")
            logger.error(traceback.format_exc())
            try:
                await interaction.followup.send(
                    f"오류가 발생했어요: {str(e)}",
                    ephemeral=True
                )
            except:
                pass

    async def _warmup_and_notify(self, msg, voice_channel, channel_info, voice_display, is_admin, guild_id, user_id):
        """Modal TTS 서버를 깨우고 완료되면 메시지를 업데이트합니다."""
        try:
            from run.services.tts.cosyvoice3_client import CosyVoice3Client
            results = await CosyVoice3Client.warmup_all_servers()

            all_ready = all(s == "running" for s in results.values())
            if all_ready:
                embed = discord.Embed(
                    title="TTS 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               f"{channel_info}\n"
                               f"내 목소리: **{voice_display}**\n\n"
                               "TTS 서버 준비 완료!",
                    color=0x00FF00
                )
            else:
                status_lines = []
                for name, status in results.items():
                    mark = "[OK]" if status == "running" else "[준비중]" if status == "starting" else "[오류]"
                    status_lines.append(f"{mark} {name}")
                embed = discord.Embed(
                    title="TTS 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               f"{channel_info}\n"
                               f"내 목소리: **{voice_display}**\n\n"
                               "TTS 서버 상태:\n" + "\n".join(status_lines) + "\n\n"
                               "준비중인 서버는 첫 메시지에서 시간이 걸릴 수 있어요.",
                    color=0xFFA500
                )

            view = TTSControlView(guild_id, user_id, is_admin)
            await msg.edit(embed=embed, view=view)
        except Exception as e:
            logger.warning(f"TTS 워밍업 알림 실패: {e}")


class TTSControlView(discord.ui.View):
    """TTS 컨트롤 뷰 - 목소리 선택, 퇴장, 채널설정"""

    def __init__(self, guild_id: str, user_id: int, is_admin: bool):
        super().__init__(timeout=120)
        self.guild_id = guild_id

        # 내 목소리 선택 드롭다운
        voice_select = discord.ui.Select(
            placeholder="내 목소리 변경",
            options=[
                discord.SelectOption(label="데비", value="debi"),
                discord.SelectOption(label="마를렌", value="marlene"),
                discord.SelectOption(label="알렉스", value="alex"),
                discord.SelectOption(label="서버 기본값", value="default"),
            ]
        )
        voice_select.callback = self._on_voice_select
        self.add_item(voice_select)

        # 퇴장 버튼
        leave_btn = discord.ui.Button(
            label="퇴장", style=discord.ButtonStyle.danger, row=1
        )
        leave_btn.callback = self._on_leave
        self.add_item(leave_btn)

        # 관리자 전용: 채널 설정
        if is_admin:
            channel_btn = discord.ui.Button(
                label="읽을 채널 설정", style=discord.ButtonStyle.secondary, row=1
            )
            channel_btn.callback = self._on_channel_setting
            self.add_item(channel_btn)

            voice_btn = discord.ui.Button(
                label="서버 기본 목소리", style=discord.ButtonStyle.secondary, row=1
            )
            voice_btn.callback = self._on_server_voice
            self.add_item(voice_btn)

    async def on_timeout(self):
        """타임아웃 시 ephemeral 메시지 삭제"""
        if self.message:
            try:
                await self.message.delete()
            except Exception:
                pass

    async def _on_voice_select(self, interaction: discord.Interaction):
        """내 목소리 변경"""
        selected = interaction.data["values"][0]
        settings = load_settings()
        guild_id = self.guild_id
        user_id = str(interaction.user.id)

        if "guilds" not in settings:
            settings["guilds"] = {}
        if guild_id not in settings["guilds"]:
            settings["guilds"][guild_id] = {}

        guild_settings = settings["guilds"][guild_id]

        if selected == "default":
            if "user_voices" in guild_settings and user_id in guild_settings["user_voices"]:
                del guild_settings["user_voices"][user_id]
            save_settings(settings)
            server_voice = guild_settings.get("tts_voice", "debi")
            voice_names = {"debi": "데비", "marlene": "마를렌", "alex": "알렉스"}
            await interaction.response.send_message(
                f"서버 기본값({voice_names.get(server_voice, server_voice)})으로 변경했어요!",
                ephemeral=True
            )
        else:
            if "user_voices" not in guild_settings:
                guild_settings["user_voices"] = {}
            guild_settings["user_voices"][user_id] = selected
            save_settings(settings)
            voice_names = {"debi": "데비", "marlene": "마를렌", "alex": "알렉스"}
            await interaction.response.send_message(
                f"{voice_names.get(selected, selected)} 목소리로 변경했어요!",
                ephemeral=True
            )

    async def _on_leave(self, interaction: discord.Interaction):
        """음성 채널 퇴장"""
        if not audio_player or not audio_player.is_connected(self.guild_id):
            await interaction.response.send_message("봇이 음성 채널에 연결되어 있지 않아요!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        success = await audio_player.leave_voice_channel(self.guild_id)

        if success:
            await interaction.followup.send("음성 채널에서 퇴장했어요!", ephemeral=True)
        else:
            await interaction.followup.send("퇴장에 실패했어요.", ephemeral=True)

    async def _on_channel_setting(self, interaction: discord.Interaction):
        """읽을 채널 설정 모달"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 사용할 수 있어요!", ephemeral=True)
            return

        modal = TTSChannelModal(self.guild_id)
        await interaction.response.send_modal(modal)

    async def _on_server_voice(self, interaction: discord.Interaction):
        """서버 기본 목소리 설정"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 사용할 수 있어요!", ephemeral=True)
            return

        view = ServerVoiceSelectView(self.guild_id)
        await interaction.response.send_message("서버 기본 목소리를 선택하세요:", view=view, ephemeral=True)
        view.message = await interaction.original_response()


class TTSChannelModal(discord.ui.Modal, title="TTS 읽을 채널 설정"):
    """TTS 채널 설정 모달"""

    channel_id_input = discord.ui.TextInput(
        label="채널 ID (비우면 모든 채널에서 읽음)",
        placeholder="채널 ID를 입력하세요 (숫자)",
        required=False,
        max_length=20,
    )

    def __init__(self, guild_id: str):
        super().__init__()
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        settings = load_settings()
        if "guilds" not in settings:
            settings["guilds"] = {}
        if self.guild_id not in settings["guilds"]:
            settings["guilds"][self.guild_id] = {}

        channel_id = self.channel_id_input.value.strip()
        if channel_id:
            settings["guilds"][self.guild_id]["tts_channel_id"] = channel_id
            channel = interaction.guild.get_channel(int(channel_id))
            if channel:
                await interaction.response.send_message(f"{channel.mention} 채널의 메시지를 읽어드릴게요!", ephemeral=True)
            else:
                await interaction.response.send_message(f"채널 ID {channel_id} 설정 완료!", ephemeral=True)
        else:
            if "tts_channel_id" in settings["guilds"][self.guild_id]:
                del settings["guilds"][self.guild_id]["tts_channel_id"]
            await interaction.response.send_message("모든 채널의 메시지를 읽어드릴게요!", ephemeral=True)

        save_settings(settings)


class ServerVoiceSelectView(discord.ui.View):
    """서버 기본 목소리 선택"""

    def __init__(self, guild_id: str):
        super().__init__(timeout=30)
        self.guild_id = guild_id
        self.message = None

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except Exception:
                pass

    @discord.ui.select(
        placeholder="서버 기본 목소리 선택",
        options=[
            discord.SelectOption(label="데비", value="debi"),
            discord.SelectOption(label="마를렌", value="marlene"),
            discord.SelectOption(label="알렉스", value="alex"),
        ]
    )
    async def voice_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        selected = select.values[0]
        settings = load_settings()
        if "guilds" not in settings:
            settings["guilds"] = {}
        if self.guild_id not in settings["guilds"]:
            settings["guilds"][self.guild_id] = {}

        settings["guilds"][self.guild_id]["tts_voice"] = selected
        save_settings(settings)

        voice_names = {"debi": "데비", "marlene": "마를렌", "alex": "알렉스"}
        await interaction.response.edit_message(
            content=f"서버 기본 목소리를 {voice_names.get(selected, selected)}(으)로 설정했어요!",
            view=None
        )


# ========== TTS 메시지 처리 (기존 로직 유지) ==========

def _ensure_playback_worker(guild_id: str):
    """재생 워커가 실행 중인지 확인하고, 없으면 시작합니다."""
    if guild_id not in tts_playback_queues:
        tts_playback_queues[guild_id] = asyncio.Queue()
    task = tts_workers.get(guild_id)
    if task is None or task.done():
        tts_workers[guild_id] = asyncio.create_task(_playback_worker(guild_id))


async def _playback_worker(guild_id: str):
    """재생 워커: Future를 순서대로 await하고 오디오를 재생합니다."""
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

        # 게임 대사 매칭
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

    _ensure_playback_worker(guild_id)
    future = asyncio.get_running_loop().create_future()
    await tts_playback_queues[guild_id].put(future)

    asyncio.create_task(_generate_tts_audio(future, message, guild_id, guild_settings))


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
