"""
오디오 플레이어: Discord 음성 채널에서 음성 재생

음성 채널 연결, TTS 음성 재생, 재생 큐 관리를 담당합니다.
"""

import asyncio
import discord
import logging
import os
import glob
from typing import Optional, Dict
from collections import deque

logger = logging.getLogger(__name__)

# ffmpeg 실행 파일 경로 찾기
def find_ffmpeg():
    """ffmpeg 실행 파일의 경로를 찾습니다."""
    # Windows WinGet 설치 경로
    winget_path = os.path.join(
        os.getenv("LOCALAPPDATA"),
        "Microsoft", "WinGet", "Packages",
        "Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_*",
        "ffmpeg-*-essentials_build", "bin", "ffmpeg.exe"
    )

    matches = glob.glob(winget_path)
    if matches:
        return matches[0]

    # 기본값 (PATH에서 찾기)
    return "ffmpeg"

FFMPEG_PATH = find_ffmpeg()
logger.info(f"ffmpeg 경로: {FFMPEG_PATH}")


class AudioPlayer:
    """
    Discord 음성 채널 오디오 플레이어

    음성 채널 연결 및 TTS 음성 재생을 관리합니다.
    """

    def __init__(self):
        """오디오 플레이어 초기화"""
        # 서버별 음성 클라이언트
        # guild_id -> VoiceClient
        self.voice_clients: Dict[str, discord.VoiceClient] = {}

        # 서버별 재생 큐
        # guild_id -> deque[audio_path]
        self.audio_queues: Dict[str, deque] = {}

        # 서버별 재생 중 상태
        # guild_id -> bool
        self.is_playing: Dict[str, bool] = {}

    async def join_voice_channel(
        self,
        voice_channel: discord.VoiceChannel
    ) -> bool:
        """
        음성 채널에 입장합니다.

        Args:
            voice_channel: 입장할 음성 채널

        Returns:
            입장 성공 여부
        """
        guild_id = str(voice_channel.guild.id)

        try:
            # 이미 연결되어 있으면 이동
            if guild_id in self.voice_clients:
                voice_client = self.voice_clients[guild_id]
                if voice_client.is_connected():
                    await voice_client.move_to(voice_channel)
                    logger.info(f"음성 채널 이동: {voice_channel.name}")
                    return True

            # 새로 연결
            voice_client = await voice_channel.connect()
            self.voice_clients[guild_id] = voice_client

            # 큐 초기화
            if guild_id not in self.audio_queues:
                self.audio_queues[guild_id] = deque()

            logger.info(f"음성 채널 입장: {voice_channel.name}")
            return True

        except Exception as e:
            import traceback
            logger.error(f"음성 채널 입장 실패: {e}")
            logger.error(traceback.format_exc())
            print(f"음성 채널 입장 실패: {e}", flush=True)
            print(traceback.format_exc(), flush=True)
            return False

    async def leave_voice_channel(self, guild_id: str) -> bool:
        """
        음성 채널에서 퇴장합니다.

        Args:
            guild_id: 서버 ID

        Returns:
            퇴장 성공 여부
        """
        try:
            if guild_id in self.voice_clients:
                voice_client = self.voice_clients[guild_id]

                # 재생 중지
                if voice_client.is_playing():
                    voice_client.stop()

                # 연결 종료
                await voice_client.disconnect()

                # 정리
                del self.voice_clients[guild_id]

                if guild_id in self.audio_queues:
                    self.audio_queues[guild_id].clear()

                if guild_id in self.is_playing:
                    del self.is_playing[guild_id]

                logger.info(f"음성 채널 퇴장: {guild_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"음성 채널 퇴장 실패: {e}")
            return False

    async def play_audio(self, guild_id: str, audio_path: str):
        """
        음성 파일을 재생합니다. (큐에 추가)

        Args:
            guild_id: 서버 ID
            audio_path: 재생할 음성 파일 경로
        """
        if guild_id not in self.voice_clients:
            logger.warning(f"음성 채널에 연결되지 않음: {guild_id}")
            return

        # 큐에 추가
        if guild_id not in self.audio_queues:
            self.audio_queues[guild_id] = deque()

        self.audio_queues[guild_id].append(audio_path)

        # 재생 중이 아니면 재생 시작
        if not self.is_playing.get(guild_id, False):
            await self._process_queue(guild_id)

    async def _process_queue(self, guild_id: str):
        """
        재생 큐를 처리합니다.

        Args:
            guild_id: 서버 ID
        """
        if guild_id not in self.voice_clients:
            return

        voice_client = self.voice_clients[guild_id]
        queue = self.audio_queues.get(guild_id)

        if not queue:
            self.is_playing[guild_id] = False
            return

        self.is_playing[guild_id] = True

        while queue:
            audio_path = queue.popleft()

            try:
                # FFmpeg를 사용하여 오디오 소스 생성
                # MP3 파일을 지원하기 위한 옵션 추가
                audio_source = discord.FFmpegPCMAudio(
                    audio_path,
                    executable=FFMPEG_PATH,
                    options="-vn"  # 비디오 스트림 무시
                )

                # 재생 완료를 기다리기 위한 이벤트
                play_finished = asyncio.Event()

                def after_playing(error):
                    if error:
                        logger.error(f"재생 중 오류: {error}")
                        print(f"오디오 재생 실패: {error}", flush=True)
                    play_finished.set()

                # 재생 시작
                voice_client.play(audio_source, after=after_playing)

                # 재생 완료 대기
                await play_finished.wait()

                # 짧은 딜레이 (다음 메시지와의 간격)
                await asyncio.sleep(0.5)

            except Exception as e:
                import traceback
                logger.error(f"오디오 재생 실패: {e}")
                logger.error(traceback.format_exc())
                print(f"오디오 재생 실패: {e}", flush=True)
                print(traceback.format_exc(), flush=True)

        self.is_playing[guild_id] = False

    def is_connected(self, guild_id: str) -> bool:
        """
        봇이 음성 채널에 연결되어 있는지 확인합니다.

        Args:
            guild_id: 서버 ID

        Returns:
            연결 여부
        """
        if guild_id in self.voice_clients:
            return self.voice_clients[guild_id].is_connected()
        return False

    def get_current_channel(self, guild_id: str) -> Optional[discord.VoiceChannel]:
        """
        현재 연결된 음성 채널을 가져옵니다.

        Args:
            guild_id: 서버 ID

        Returns:
            현재 음성 채널 (연결되지 않았으면 None)
        """
        if guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            if voice_client.is_connected():
                return voice_client.channel
        return None
