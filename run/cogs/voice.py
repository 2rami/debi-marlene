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

# 음성 이름 매핑
VOICE_NAMES = {
    "debi": "데비", "marlene": "마를렌", "alex": "알렉스",
    "edge_sunhi": "SunHi", "edge_injoon": "InJoon", "edge_hyunsu": "Hyunsu",
}

# 전역 인스턴스
audio_player: Optional[AudioPlayer] = None

# 캐릭터별 TTS 서비스 캐시
tts_services: dict = {}
# Edge TTS 폴백 서비스 캐시
edge_tts_services: dict = {}

# 서버별 TTS 재생 큐 (생성은 병렬, 재생은 순서대로)
tts_playback_queues: Dict[str, asyncio.Queue] = {}
tts_workers: Dict[str, asyncio.Task] = {}


async def get_tts_service(character: str = "default") -> TTSService:
    """캐릭터에 맞는 TTS 서비스를 가져옵니다.
    edge_ 접두사면 Edge TTS 직접 사용."""
    global tts_services

    # Edge TTS 직접 선택 (edge_sunhi, edge_injoon, edge_hyunsu)
    if character.startswith("edge_"):
        return await get_edge_tts_service(character)

    if character in tts_services:
        return tts_services[character]

    logger.info(f"CosyVoice3 TTS 사용 ({character})")
    tts_service = TTSService(speaker=character)
    await tts_service.initialize()
    tts_services[character] = tts_service

    return tts_service


async def get_edge_tts_service(character: str = "debi") -> TTSService:
    """Edge TTS 서비스를 가져옵니다."""
    global edge_tts_services

    if character in edge_tts_services:
        return edge_tts_services[character]

    logger.info(f"Edge TTS 초기화 ({character})")
    tts_service = TTSService(speaker=character, engine="edge")
    await tts_service.initialize()
    edge_tts_services[character] = tts_service

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

                if not tts_channel_id:
                    # 채널 미설정 시 /tts를 입력한 채널을 자동 설정
                    tts_channel_id = str(interaction.channel.id)
                    if "guilds" not in settings:
                        settings["guilds"] = {}
                    if guild_id not in settings["guilds"]:
                        settings["guilds"][guild_id] = {}
                    settings["guilds"][guild_id]["tts_channel_id"] = tts_channel_id
                    save_settings(settings)

                tts_channel = interaction.guild.get_channel(int(tts_channel_id))
                channel_info = f"읽을 채널: {tts_channel.mention}" if tts_channel else "읽을 채널: (삭제된 채널)"

                # 현재 목소리 정보
                user_id = str(interaction.user.id)
                user_voices = guild_settings.get("user_voices", {})
                current_voice = user_voices.get(user_id) or guild_settings.get("tts_voice", "edge_sunhi")
                voice_names = VOICE_NAMES
                voice_display = voice_names.get(current_voice, current_voice)

                is_admin = interaction.user.guild_permissions.administrator
                is_edge_voice = current_voice.startswith("edge_")

                if is_edge_voice:
                    # Edge TTS: 서버 불필요, 즉시 준비 완료
                    embed = discord.Embed(
                        title="TTS 입장",
                        description=f"{voice_channel.mention}에 입장했어요!\n\n"
                                   f"{channel_info}\n"
                                   f"내 목소리: **{voice_display}** (Edge TTS)\n\n"
                                   "준비 완료!",
                        color=0x00FF00
                    )
                    view = TTSControlView(guild_id, interaction.user.id, is_admin)
                    msg = await interaction.followup.send(embed=embed, view=view, ephemeral=True, wait=True)
                    view.message = msg

                    # Edge라도 Modal 서버 상태는 보여줌 (백그라운드)
                    asyncio.create_task(self._update_server_status(msg, voice_channel, channel_info, voice_display, is_admin, guild_id, interaction.user.id, is_edge=True))
                else:
                    # AI 음성: Modal 서버 워밍업 필요
                    embed = discord.Embed(
                        title="TTS 입장",
                        description=f"{voice_channel.mention}에 입장했어요!\n\n"
                                   f"{channel_info}\n"
                                   f"내 목소리: **{voice_display}**\n\n"
                                   "TTS 서버를 준비하고 있어요...",
                        color=0xFFA500
                    )
                    view = TTSControlView(guild_id, interaction.user.id, is_admin)
                    msg = await interaction.followup.send(embed=embed, view=view, ephemeral=True, wait=True)
                    view.message = msg

                    # Modal TTS 서버 워밍업 + 상태 표시
                    asyncio.create_task(self._update_server_status(msg, voice_channel, channel_info, voice_display, is_admin, guild_id, interaction.user.id, is_edge=False))
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

    async def _update_server_status(self, msg, voice_channel, channel_info, voice_display, is_admin, guild_id, user_id, is_edge: bool):
        """Modal TTS 서버 상태를 확인하고 메시지를 업데이트합니다."""
        try:
            from run.services.tts.cosyvoice3_client import CosyVoice3Client
            results = await CosyVoice3Client.warmup_all_servers()

            # 서버 상태 라인 생성
            status_lines = []
            has_error = False
            all_ready = True
            for name, status in results.items():
                if status == "running":
                    mark = "[OK]"
                elif status == "starting":
                    mark = "[준비중]"
                    all_ready = False
                else:
                    mark = "[오류]"
                    has_error = True
                    all_ready = False
                status_lines.append(f"  {mark} {name}")

            server_status_text = "AI 서버 상태:\n" + "\n".join(status_lines)

            if is_edge:
                # Edge TTS 사용자: 이미 준비 완료 상태, 서버 상태만 추가 표시
                embed = discord.Embed(
                    title="TTS 입장",
                    description=f"{voice_channel.mention}에 입장했어요!\n\n"
                               f"{channel_info}\n"
                               f"내 목소리: **{voice_display}** (Edge TTS)\n\n"
                               "준비 완료!\n\n"
                               f"{server_status_text}"
                               + ("\n서버 오류 시 Edge TTS로 자동 전환됩니다." if has_error else ""),
                    color=0x00FF00
                )
            else:
                # AI 음성 사용자: 서버 상태에 따라 색상 변경
                if all_ready:
                    desc = (f"{voice_channel.mention}에 입장했어요!\n\n"
                            f"{channel_info}\n"
                            f"내 목소리: **{voice_display}**\n\n"
                            f"TTS 서버 준비 완료!\n\n"
                            f"{server_status_text}")
                    color = 0x00FF00
                else:
                    note = "\n준비중인 서버는 첫 메시지에서 시간이 걸릴 수 있어요."
                    if has_error:
                        note += "\n서버 오류 시 Edge TTS로 자동 전환됩니다."
                    desc = (f"{voice_channel.mention}에 입장했어요!\n\n"
                            f"{channel_info}\n"
                            f"내 목소리: **{voice_display}**\n\n"
                            f"{server_status_text}\n"
                            f"{note}")
                    color = 0xFF6B6B if has_error else 0xFFA500

                embed = discord.Embed(title="TTS 입장", description=desc, color=color)

            view = TTSControlView(guild_id, user_id, is_admin)
            await msg.edit(embed=embed, view=view)
        except Exception as e:
            logger.warning(f"TTS 서버 상태 확인 실패: {e}")


class TTSControlView(discord.ui.View):
    """TTS 컨트롤 뷰 - 목소리 선택, 퇴장, 채널설정"""

    def __init__(self, guild_id: str, user_id: int, is_admin: bool):
        super().__init__(timeout=120)
        self.guild_id = guild_id

        # 내 목소리 선택 드롭다운
        voice_select = discord.ui.Select(
            placeholder="내 목소리 변경",
            options=[
                discord.SelectOption(label="SunHi", value="edge_sunhi", description="Edge TTS (여성)"),
                discord.SelectOption(label="InJoon", value="edge_injoon", description="Edge TTS (남성)"),
                discord.SelectOption(label="Hyunsu", value="edge_hyunsu", description="Edge TTS (남성, 다국어)"),
                discord.SelectOption(label="데비", value="debi", description="AI 음성 (서버 준비 필요)"),
                discord.SelectOption(label="마를렌", value="marlene", description="AI 음성 (서버 준비 필요)"),
                discord.SelectOption(label="알렉스", value="alex", description="AI 음성 (서버 준비 필요)"),
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
            server_voice = guild_settings.get("tts_voice", "edge_sunhi")
            voice_names = VOICE_NAMES
            await interaction.response.send_message(
                f"서버 기본값({voice_names.get(server_voice, server_voice)})으로 변경했어요!",
                ephemeral=True
            )
        else:
            if "user_voices" not in guild_settings:
                guild_settings["user_voices"] = {}
            guild_settings["user_voices"][user_id] = selected
            save_settings(settings)
            voice_names = VOICE_NAMES

            is_ai_voice = selected in ("debi", "marlene", "alex")
            if is_ai_voice:
                await interaction.response.send_message(
                    f"{voice_names.get(selected, selected)} 목소리로 변경했어요! AI 서버 상태를 확인하고 있어요...",
                    ephemeral=True
                )
                # AI 음성 선택 시 Modal 서버 워밍업 + 상태 표시
                try:
                    from run.services.tts.cosyvoice3_client import CosyVoice3Client
                    results = await CosyVoice3Client.warmup_all_servers()
                    status_lines = []
                    for name, status in results.items():
                        if status == "running":
                            mark = "[OK]"
                        elif status == "starting":
                            mark = "[준비중]"
                        else:
                            mark = "[오류]"
                        status_lines.append(f"  {mark} {name}")
                    await interaction.followup.send(
                        f"AI 서버 상태:\n" + "\n".join(status_lines),
                        ephemeral=True
                    )
                except Exception:
                    pass
            else:
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
        """읽을 채널 설정"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 사용할 수 있어요!", ephemeral=True)
            return

        view = TTSChannelSelectView(self.guild_id)
        await interaction.response.send_message("TTS가 읽을 채널을 선택하세요:", view=view, ephemeral=True)
        view.message = await interaction.original_response()

    async def _on_server_voice(self, interaction: discord.Interaction):
        """서버 기본 목소리 설정"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 사용할 수 있어요!", ephemeral=True)
            return

        view = ServerVoiceSelectView(self.guild_id)
        await interaction.response.send_message("서버 기본 목소리를 선택하세요:", view=view, ephemeral=True)
        view.message = await interaction.original_response()


class TTSChannelSelectView(discord.ui.View):
    """TTS 읽을 채널 선택 (ChannelSelect 사용)"""

    def __init__(self, guild_id: str):
        super().__init__(timeout=60)
        self.guild_id = guild_id
        self.message = None

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="채널을 선택하세요",
        min_values=0,
        max_values=1,
    )
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        settings = load_settings()
        if "guilds" not in settings:
            settings["guilds"] = {}
        if self.guild_id not in settings["guilds"]:
            settings["guilds"][self.guild_id] = {}

        if select.values:
            channel = select.values[0]
            settings["guilds"][self.guild_id]["tts_channel_id"] = str(channel.id)
            save_settings(settings)
            await interaction.response.send_message(f"{channel.mention} 채널의 메시지만 읽을게요!", ephemeral=True)
        else:
            await interaction.response.send_message("채널을 선택해주세요.", ephemeral=True)
            return

        self.stop()

    @discord.ui.button(label="설정 해제", style=discord.ButtonStyle.danger, row=1)
    async def clear_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_settings()
        if "guilds" not in settings:
            settings["guilds"] = {}
        if self.guild_id not in settings["guilds"]:
            settings["guilds"][self.guild_id] = {}

        if "tts_channel_id" in settings["guilds"][self.guild_id]:
            del settings["guilds"][self.guild_id]["tts_channel_id"]
        save_settings(settings)
        await interaction.response.send_message("채널 설정을 해제했어요. 채널을 설정하기 전까지 메시지를 읽지 않아요.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except Exception:
                pass


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
            discord.SelectOption(label="SunHi", value="edge_sunhi", description="Edge TTS (여성)"),
            discord.SelectOption(label="InJoon", value="edge_injoon", description="Edge TTS (남성)"),
            discord.SelectOption(label="Hyunsu", value="edge_hyunsu", description="Edge TTS (남성, 다국어)"),
            discord.SelectOption(label="데비", value="debi", description="AI 음성"),
            discord.SelectOption(label="마를렌", value="marlene", description="AI 음성"),
            discord.SelectOption(label="알렉스", value="alex", description="AI 음성"),
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

        voice_names = VOICE_NAMES
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
        tts_voice = user_voices.get(user_id) or guild_settings.get("tts_voice", "edge_sunhi")
        valid_voices = ["debi", "marlene", "alex", "edge_sunhi", "edge_injoon", "edge_hyunsu"]
        if tts_voice not in valid_voices:
            tts_voice = "edge_sunhi"

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
            text_to_read = message.content
            if len(text_to_read) > 300:
                short_msgs = [
                    "너무 길어서 못 읽겠어요.",
                    "힘들어서 못 말하겠어.",
                    "이건 좀 길어요.",
                    "요약 부탁드려요."
                ]
                text_to_read = random.choice(short_msgs)
            else:
                text_to_read = preprocess_text_for_tts(text_to_read)

            # CosyVoice3 시도 → 실패 시 Edge TTS 폴백
            try:
                tts_service = await get_tts_service(tts_voice)
                audio_path = await tts_service.text_to_speech(text=text_to_read, **meta)
            except Exception as e:
                logger.warning(f"CosyVoice3 실패, Edge TTS 폴백: {e}")
                edge_service = await get_edge_tts_service(tts_voice)
                audio_path = await edge_service.text_to_speech(text=text_to_read, **meta)

        if audio_path:
            audio_path = await convert_to_discord_pcm(audio_path)

        future.set_result(audio_path)

    except Exception as e:
        logger.error(f"TTS 생성 오류: {e}", exc_info=True)
        if not future.done():
            future.set_result(None)


async def _delete_message_after(message: discord.Message, seconds: int):
    """N초 후 메시지 삭제"""
    try:
        await asyncio.sleep(seconds)
        await message.delete()
    except Exception:
        pass


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
    if not tts_channel_id:
        return  # 채널 미설정이면 읽지 않음
    if str(message.channel.id) != tts_channel_id:
        return

    if not message.content.strip():
        return

    print(f"[TTS] {message.author.name}: {message.content[:30]}", flush=True)

    # TTS 메시지 자동 삭제
    auto_delete = guild_settings.get("tts_auto_delete_seconds", 0)
    if auto_delete and auto_delete > 0:
        asyncio.create_task(_delete_message_after(message, auto_delete))

    _ensure_playback_worker(guild_id)
    future = asyncio.get_running_loop().create_future()
    await tts_playback_queues[guild_id].put(future)

    asyncio.create_task(_generate_tts_audio(future, message, guild_id, guild_settings))


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
