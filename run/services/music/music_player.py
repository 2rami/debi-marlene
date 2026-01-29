"""
음악 플레이어

서버별 음악 재생을 관리하는 MusicPlayer와 전역 관리자 MusicManager를 제공합니다.
공유 VoiceManager를 사용하여 TTS와 동일한 voice_client를 공유합니다.
"""

import asyncio
import logging
import os
import glob
import platform
from collections import deque
from typing import Optional, Dict, List

import discord

from run.services.music.youtube_extractor import Song, YouTubeExtractor
from run.services.voice_manager import voice_manager, AudioType

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
logger.info(f"Music ffmpeg 경로: {FFMPEG_PATH}")

# FFmpeg 스트리밍 옵션 (YouTube 403 방지를 위한 헤더 포함)
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -user_agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"',
    'options': '-vn'
}


class MusicPlayer:
    """서버별 음악 플레이어 (VoiceManager 사용)"""

    def __init__(self, guild_id: str):
        self.guild_id = guild_id
        self.queue: deque[Song] = deque()
        self.current: Optional[Song] = None
        self.is_playing: bool = False
        self._play_next_event = asyncio.Event()

    async def join(self, channel: discord.VoiceChannel) -> bool:
        """음성 채널에 입장합니다."""
        success = await voice_manager.join(channel)
        if success:
            logger.info(f"[Music] 음성 채널 입장: {channel.name}")
        return success

    async def leave(self) -> bool:
        """음성 채널에서 퇴장합니다."""
        try:
            # 재생 중지
            vc = voice_manager.get_voice_client(self.guild_id)
            if vc and vc.is_playing():
                vc.stop()

            # 상태 정리
            self.queue.clear()
            self.current = None
            self.is_playing = False
            voice_manager.clear_music_state(self.guild_id)

            # 연결 해제
            success = await voice_manager.leave(self.guild_id)
            if success:
                logger.info(f"[Music] 음성 채널 퇴장: {self.guild_id}")
            return success

        except Exception as e:
            logger.error(f"[Music] 음성 채널 퇴장 실패: {e}")
            return False

    async def add_song(self, song: Song) -> int:
        """
        대기열에 곡을 추가합니다.

        Returns:
            대기열에서의 위치 (0이면 바로 재생)
        """
        self.queue.append(song)
        position = len(self.queue)

        # 재생 중이 아니면 재생 시작
        if not self.is_playing:
            asyncio.create_task(self._play_loop())

        return position

    async def _play_loop(self):
        """재생 루프"""
        self.is_playing = True

        while self.queue:
            self.current = self.queue.popleft()

            vc = voice_manager.get_voice_client(self.guild_id)
            if not vc or not vc.is_connected():
                break

            # 스트림 URL 갱신 (만료된 URL 사용 방지 - 항상 갱신)
            new_url = await YouTubeExtractor.refresh_stream_url(self.current)
            if new_url:
                self.current.stream_url = new_url
                logger.info(f"[Music] 스트림 URL 갱신 완료: {self.current.title}")
            else:
                logger.error(f"[Music] 스트림 URL 갱신 실패: {self.current.title}")
                continue

            try:
                audio_source = discord.FFmpegPCMAudio(
                    self.current.stream_url,
                    executable=FFMPEG_PATH,
                    **FFMPEG_OPTIONS
                )

                self._play_next_event.clear()

                def after_play(error):
                    if error:
                        logger.error(f"[Music] 재생 오류: {error}")
                    self._play_next_event.set()

                # 음악 재생 상태 설정
                voice_manager.set_music_playing(self.guild_id)

                vc.play(audio_source, after=after_play)
                logger.info(f"[Music] 재생 시작: {self.current.title}")

                # 재생 완료 대기
                await self._play_next_event.wait()

            except Exception as e:
                logger.error(f"[Music] 재생 실패: {e}")
                continue

        self.current = None
        self.is_playing = False
        voice_manager.clear_music_state(self.guild_id)

    async def skip(self) -> Optional[Song]:
        """현재 곡을 건너뜁니다."""
        skipped = self.current
        vc = voice_manager.get_voice_client(self.guild_id)
        if vc and vc.is_playing():
            vc.stop()
        return skipped

    async def stop(self):
        """재생을 정지하고 대기열을 비웁니다."""
        self.queue.clear()
        vc = voice_manager.get_voice_client(self.guild_id)
        if vc and vc.is_playing():
            vc.stop()
        self.current = None
        voice_manager.clear_music_state(self.guild_id)

    def get_queue(self) -> List[Song]:
        """대기열 목록을 반환합니다."""
        return list(self.queue)

    def is_connected(self) -> bool:
        """음성 채널 연결 여부"""
        return voice_manager.is_connected(self.guild_id)


class MusicManager:
    """서버별 MusicPlayer 인스턴스를 관리합니다."""

    _players: Dict[str, MusicPlayer] = {}

    @classmethod
    def get_player(cls, guild_id: str) -> MusicPlayer:
        """서버의 MusicPlayer를 가져옵니다. 없으면 생성합니다."""
        if guild_id not in cls._players:
            cls._players[guild_id] = MusicPlayer(guild_id)
        return cls._players[guild_id]

    @classmethod
    async def remove_player(cls, guild_id: str):
        """서버의 MusicPlayer를 제거합니다."""
        if guild_id in cls._players:
            player = cls._players[guild_id]
            await player.leave()
            del cls._players[guild_id]

    @classmethod
    def has_player(cls, guild_id: str) -> bool:
        """서버에 MusicPlayer가 있는지 확인합니다."""
        return guild_id in cls._players
