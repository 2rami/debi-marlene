"""
오디오 플레이어: Discord 음성 채널에서 TTS 음성 재생

공유 VoiceManager를 사용하여 음악과 동일한 voice_client를 공유합니다.
"""

import asyncio
import discord
import logging
from typing import Optional
from collections import deque

from run.services.voice_manager import voice_manager

logger = logging.getLogger(__name__)


class AudioPlayer:
    """
    Discord TTS 오디오 플레이어

    VoiceManager를 통해 음성 채널을 관리합니다.
    TTS는 음악보다 우선순위가 높습니다.
    """

    def __init__(self):
        """오디오 플레이어 초기화"""
        # 서버별 TTS 재생 큐
        self.tts_queues: dict[str, deque] = {}

        # 서버별 재생 중 상태
        self.is_playing: dict[str, bool] = {}

    async def join_voice_channel(self, voice_channel: discord.VoiceChannel) -> bool:
        """음성 채널에 입장합니다."""
        guild_id = str(voice_channel.guild.id)

        success = await voice_manager.join(voice_channel)

        if success:
            if guild_id not in self.tts_queues:
                self.tts_queues[guild_id] = deque()
            logger.info(f"[TTS] 음성 채널 입장: {voice_channel.name}")

        return success

    async def leave_voice_channel(self, guild_id: str) -> bool:
        """음성 채널에서 퇴장합니다."""
        # TTS 큐 정리
        if guild_id in self.tts_queues:
            self.tts_queues[guild_id].clear()

        if guild_id in self.is_playing:
            del self.is_playing[guild_id]

        success = await voice_manager.leave(guild_id)

        if success:
            logger.info(f"[TTS] 음성 채널 퇴장: {guild_id}")

        return success

    def is_connected(self, guild_id: str) -> bool:
        """봇이 음성 채널에 연결되어 있는지 확인합니다."""
        return voice_manager.is_connected(guild_id)

    async def play_audio(self, guild_id: str, audio_path: str):
        """
        TTS 음성 파일을 재생합니다.

        Args:
            guild_id: 서버 ID
            audio_path: 재생할 음성 파일 경로
        """
        if not voice_manager.is_connected(guild_id):
            logger.warning(f"[TTS] 음성 채널에 연결되지 않음: {guild_id}")
            return

        # 큐에 추가
        if guild_id not in self.tts_queues:
            self.tts_queues[guild_id] = deque()

        self.tts_queues[guild_id].append(audio_path)

        # 재생 중이 아니면 큐 처리 시작
        if not self.is_playing.get(guild_id, False):
            await self._process_queue(guild_id)

    async def _process_queue(self, guild_id: str):
        """TTS 재생 큐를 처리합니다."""
        if not voice_manager.is_connected(guild_id):
            return

        queue = self.tts_queues.get(guild_id)
        if not queue:
            self.is_playing[guild_id] = False
            return

        self.is_playing[guild_id] = True

        while queue:
            audio_path = queue.popleft()

            try:
                # VoiceManager를 통해 TTS 재생 (음악 끼어들기 포함)
                await voice_manager.play_tts(guild_id, audio_path)

                # 짧은 딜레이
                await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"[TTS] 오디오 재생 실패: {e}")

        self.is_playing[guild_id] = False

    def get_current_channel(self, guild_id: str) -> Optional[discord.VoiceChannel]:
        """현재 연결된 음성 채널을 가져옵니다."""
        vc = voice_manager.get_voice_client(guild_id)
        if vc and vc.is_connected():
            return vc.channel
        return None
