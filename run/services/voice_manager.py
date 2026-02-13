"""
공유 VoiceManager

서버별 하나의 음성 연결을 관리합니다.
TTS와 음악이 동일한 voice_client를 공유합니다.
TTS는 음악보다 우선순위가 높아 끼어들기합니다.
"""

import asyncio
import logging
import os
import glob
import platform
from typing import Optional, Dict, Callable, Any
from enum import Enum

import discord

logger = logging.getLogger(__name__)


def find_ffmpeg() -> str:
    """ffmpeg 실행 파일의 경로를 찾습니다."""
    if platform.system() == "Windows":
        localappdata = os.getenv("LOCALAPPDATA")
        if localappdata:
            winget_path = os.path.join(
                localappdata,
                "Microsoft", "WinGet", "Packages",
                "Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_*",
                "ffmpeg-*-essentials_build", "bin", "ffmpeg.exe"
            )
            matches = glob.glob(winget_path)
            if matches:
                return matches[0]
    return "ffmpeg"


FFMPEG_PATH = find_ffmpeg()


class AudioType(Enum):
    """오디오 타입"""
    TTS = "tts"
    MUSIC = "music"


IDLE_TIMEOUT_SECONDS = 300  # 5분


class VoiceManager:
    """
    서버별 음성 연결 관리자

    TTS와 음악이 동일한 voice_client를 공유합니다.
    TTS는 음악보다 우선순위가 높습니다.
    """

    _instance: Optional["VoiceManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 서버별 음성 클라이언트
        self.voice_clients: Dict[str, discord.VoiceClient] = {}

        # 서버별 현재 재생 중인 오디오 타입
        self.current_type: Dict[str, Optional[AudioType]] = {}

        # 서버별 TTS 끼어들기 상태
        self.tts_interrupting: Dict[str, bool] = {}

        # 서버별 음악 재시작 콜백
        self.music_restart_callbacks: Dict[str, Optional[Callable]] = {}

        # 서버별 재생 완료 이벤트
        self.play_finished_events: Dict[str, asyncio.Event] = {}

        # 서버별 락 (동시 접근 방지)
        self.locks: Dict[str, asyncio.Lock] = {}

        # 서버별 idle 타이머 태스크
        self.idle_tasks: Dict[str, asyncio.Task] = {}

        self._initialized = True
        logger.info("VoiceManager 초기화 완료")

    def _get_lock(self, guild_id: str) -> asyncio.Lock:
        """서버별 락을 가져옵니다."""
        if guild_id not in self.locks:
            self.locks[guild_id] = asyncio.Lock()
        return self.locks[guild_id]

    async def join(self, channel: discord.VoiceChannel) -> bool:
        """음성 채널에 입장합니다."""
        guild_id = str(channel.guild.id)

        async with self._get_lock(guild_id):
            try:
                if guild_id in self.voice_clients:
                    vc = self.voice_clients[guild_id]
                    if vc.is_connected():
                        if vc.channel.id != channel.id:
                            await vc.move_to(channel)
                            logger.info(f"음성 채널 이동: {channel.name}")
                        return True

                vc = await channel.connect()
                self.voice_clients[guild_id] = vc
                self.current_type[guild_id] = None
                logger.info(f"음성 채널 입장: {channel.name}")
                return True

            except Exception as e:
                logger.error(f"음성 채널 입장 실패: {e}")
                return False

    async def leave(self, guild_id: str) -> bool:
        """음성 채널에서 퇴장합니다."""
        self.cancel_idle_timer(guild_id)

        async with self._get_lock(guild_id):
            try:
                if guild_id in self.voice_clients:
                    vc = self.voice_clients[guild_id]
                    if vc.is_playing():
                        vc.stop()
                    await vc.disconnect()
                    del self.voice_clients[guild_id]

                    # 상태 정리
                    self.current_type.pop(guild_id, None)
                    self.tts_interrupting.pop(guild_id, None)
                    self.music_restart_callbacks.pop(guild_id, None)
                    self.play_finished_events.pop(guild_id, None)

                    logger.info(f"음성 채널 퇴장: {guild_id}")
                    return True
                return False

            except Exception as e:
                logger.error(f"음성 채널 퇴장 실패: {e}")
                return False

    def is_connected(self, guild_id: str) -> bool:
        """음성 채널에 연결되어 있는지 확인합니다."""
        if guild_id in self.voice_clients:
            return self.voice_clients[guild_id].is_connected()
        return False

    def get_voice_client(self, guild_id: str) -> Optional[discord.VoiceClient]:
        """음성 클라이언트를 가져옵니다."""
        return self.voice_clients.get(guild_id)

    def set_music_restart_callback(self, guild_id: str, callback: Callable):
        """음악 재시작 콜백을 설정합니다."""
        self.music_restart_callbacks[guild_id] = callback

    def is_tts_interrupting(self, guild_id: str) -> bool:
        """TTS가 음악을 끼어들기 중인지 확인합니다."""
        return self.tts_interrupting.get(guild_id, False)

    async def play_tts(self, guild_id: str, audio_path: str, suppress_music_restart: bool = False) -> bool:
        """
        TTS 오디오를 재생합니다. (음악보다 우선)

        음악이 재생 중이면 정지하고 TTS 재생 후 재시작합니다.
        """
        if guild_id not in self.voice_clients:
            logger.warning(f"음성 채널에 연결되지 않음: {guild_id}")
            return False

        vc = self.voice_clients[guild_id]
        was_music_playing = False

        # 음악 재생 중이면 정지 (TTS 끼어들기)
        if vc.is_playing() and self.current_type.get(guild_id) == AudioType.MUSIC:
            self.tts_interrupting[guild_id] = True
            was_music_playing = True
            vc.stop()  # pause 대신 stop (play()가 오디오 소스를 교체하므로)
            logger.info("음악 정지 (TTS 끼어들기)")
            await asyncio.sleep(0.1)  # 정지 완료 대기

        try:
            # TTS 재생
            self.current_type[guild_id] = AudioType.TTS

            audio_source = discord.FFmpegPCMAudio(
                audio_path,
                executable=FFMPEG_PATH,
                options="-vn"
            )

            play_finished = asyncio.Event()

            def after_playing(error):
                if error:
                    logger.error(f"TTS 재생 오류: {error}")
                play_finished.set()

            vc.play(audio_source, after=after_playing)
            await play_finished.wait()

            self.current_type[guild_id] = None
            self.tts_interrupting[guild_id] = False

            # TTS 완료 후 음악 재시작 (청크 모드에서는 마지막 청크만)
            if was_music_playing and not suppress_music_restart:
                callback = self.music_restart_callbacks.get(guild_id)
                if callback:
                    logger.info("음악 재시작 콜백 호출")
                    asyncio.create_task(callback())
                else:
                    logger.warning("음악 재시작 콜백 없음")

            return True

        except Exception as e:
            logger.error(f"TTS 재생 실패: {e}")
            self.tts_interrupting[guild_id] = False
            self.current_type[guild_id] = None
            return False

    def is_music_playing(self, guild_id: str) -> bool:
        """음악이 재생 중인지 확인합니다."""
        if guild_id not in self.voice_clients:
            return False
        vc = self.voice_clients[guild_id]
        return (vc.is_playing() or vc.is_paused()) and self.current_type.get(guild_id) == AudioType.MUSIC

    def set_music_playing(self, guild_id: str):
        """음악 재생 상태로 설정합니다."""
        self.current_type[guild_id] = AudioType.MUSIC

    def clear_music_state(self, guild_id: str):
        """음악 상태를 초기화합니다."""
        if self.current_type.get(guild_id) == AudioType.MUSIC:
            self.current_type[guild_id] = None

    def start_idle_timer(self, guild_id: str):
        """봇 혼자 남았을 때 idle 타이머를 시작합니다."""
        self.cancel_idle_timer(guild_id)
        self.idle_tasks[guild_id] = asyncio.create_task(
            self._idle_disconnect(guild_id)
        )
        logger.info(f"idle 타이머 시작: {guild_id} ({IDLE_TIMEOUT_SECONDS}초)")

    def cancel_idle_timer(self, guild_id: str):
        """idle 타이머를 취소합니다."""
        task = self.idle_tasks.pop(guild_id, None)
        if task and not task.done():
            task.cancel()
            logger.info(f"idle 타이머 취소: {guild_id}")

    async def _idle_disconnect(self, guild_id: str):
        """idle 대기 후 자동 퇴장합니다."""
        try:
            await asyncio.sleep(IDLE_TIMEOUT_SECONDS)

            # 타이머 만료 - 아직 연결되어 있고 혼자인지 재확인
            vc = self.voice_clients.get(guild_id)
            if not vc or not vc.is_connected():
                return

            non_bot_members = [m for m in vc.channel.members if not m.bot]
            if non_bot_members:
                return

            logger.info(f"idle 타이머 만료, 자동 퇴장: {guild_id}")

            # 퇴장 알림
            try:
                await vc.channel.send("음성채널에 아무도 없어서 나갈게!")
            except Exception:
                pass

            # MusicManager 정리 (순환 import 방지를 위해 여기서 import)
            from run.services.music.music_player import MusicManager
            if MusicManager.has_player(guild_id):
                await MusicManager.remove_player(guild_id)
            else:
                await self.leave(guild_id)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"idle 자동 퇴장 실패: {e}")
        finally:
            self.idle_tasks.pop(guild_id, None)


# 싱글톤 인스턴스
voice_manager = VoiceManager()
