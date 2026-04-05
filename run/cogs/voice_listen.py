"""
음성 듣기 Cog

음성채널에서 유저 음성을 녹음하고 STT → 키워드 감지 → AI 응답.
discord-ext-voice-recv 사용.

모드:
  - 키워드 호출: "데비야" 감지 시 뒤의 내용으로 캐릭터 응답
"""

import asyncio
import base64
import io
import logging
import struct
import time
from typing import Dict, Optional

import discord
from discord.ext import commands

import discord.ext.voice_recv as voice_recv

from run.services.chat import ChatClient
from run.services.voice_manager import VoiceManager

logger = logging.getLogger(__name__)

# 키워드 트리거 (텍스트 대화와 동일)
TRIGGER_WORDS = ["데비야", "데비나", "데비아", "마를렌아", "마를렌야", "뎁마야", "뎁마"]

# 오디오 설정
SAMPLE_RATE = 48000  # Discord 기본
CHANNELS = 2         # Discord 기본 (stereo)
SAMPLE_WIDTH = 2     # 16-bit

# 발화 후 무음 대기 시간 (초) — 이 시간 동안 추가 발화 없으면 처리
SILENCE_THRESHOLD = 1.5
# 최소 발화 길이 (초) — 너무 짧은 소리 무시
MIN_SPEECH_DURATION = 0.5
# 최대 발화 길이 (초) — Gemma4 오디오 30초 제한
MAX_SPEECH_DURATION = 25

AUDIO_CHAT_URL = "https://goenho0613--gemma4-chat-server-gemma4audio-audio-chat.modal.run"


class SpeechBuffer:
    """유저별 발화 버퍼. speaking_start~stop 사이의 PCM 데이터를 모음."""

    def __init__(self):
        self.chunks: list[bytes] = []
        self.start_time: float = 0
        self.last_write_time: float = 0
        self.is_speaking: bool = False

    def start(self):
        self.chunks = []
        self.start_time = time.time()
        self.last_write_time = time.time()
        self.is_speaking = True

    def write(self, pcm_data: bytes):
        self.chunks.append(pcm_data)
        self.last_write_time = time.time()

    def stop(self):
        self.is_speaking = False

    @property
    def duration(self) -> float:
        total_bytes = sum(len(c) for c in self.chunks)
        return total_bytes / (SAMPLE_RATE * CHANNELS * SAMPLE_WIDTH)

    def to_wav_bytes(self) -> bytes:
        """PCM 데이터를 WAV 파일로 변환"""
        import wave
        pcm_data = b"".join(self.chunks)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm_data)
        return buf.getvalue()

    def clear(self):
        self.chunks = []
        self.start_time = 0
        self.last_write_time = 0
        self.is_speaking = False


class ListenSink(voice_recv.AudioSink):
    """음성채널 오디오를 수신하는 Sink. 유저별 발화를 버퍼링."""

    def __init__(self, cog: "VoiceListenCog", guild_id: str, text_channel: discord.TextChannel):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
        self.text_channel = text_channel
        self.buffers: Dict[int, SpeechBuffer] = {}  # user_id -> buffer
        self._processing: set = set()  # 처리 중인 user_id

    def wants_opus(self) -> bool:
        return False  # 디코딩된 PCM을 받음

    def write(self, user, data: voice_recv.VoiceData):
        if user is None or user.bot:
            return

        uid = user.id
        if uid not in self.buffers:
            self.buffers[uid] = SpeechBuffer()
            print(f"[듣기] 새 버퍼 생성: {user.display_name}", flush=True)

        buf = self.buffers[uid]

        if not buf.is_speaking:
            buf.start()
            print(f"[듣기] 발화 감지: {user.display_name}", flush=True)

        # 최대 길이 초과 시 무시
        if buf.duration < MAX_SPEECH_DURATION:
            buf.write(data.pcm)

    def on_voice_member_speaking_stop(self, member: discord.Member):
        """발화 종료 감지 → 일정 시간 후 처리"""
        print(f"[듣기] speaking_stop: {member.display_name}", flush=True)
        if member.bot:
            return

        uid = member.id
        if uid not in self.buffers:
            return

        buf = self.buffers[uid]
        buf.stop()

        # 이미 처리 중이면 무시
        if uid in self._processing:
            return

        # 무음 대기 후 처리 (추가 발화가 올 수 있으니까)
        asyncio.get_event_loop().create_task(
            self._delayed_process(member, uid)
        )

    def on_voice_member_speaking_start(self, member: discord.Member):
        """발화 시작 — 버퍼링 시작"""
        print(f"[듣기] speaking_start: {member.display_name}", flush=True)
        if member.bot:
            return

        uid = member.id
        if uid not in self.buffers:
            self.buffers[uid] = SpeechBuffer()

        # 이미 speaking이면 연속 발화
        if not self.buffers[uid].is_speaking:
            self.buffers[uid].start()

    async def _delayed_process(self, member: discord.Member, uid: int):
        """무음 대기 후 발화 처리"""
        await asyncio.sleep(SILENCE_THRESHOLD)

        buf = self.buffers.get(uid)
        if buf is None:
            return

        # 다시 말하기 시작했으면 취소
        if buf.is_speaking:
            return

        # 너무 짧으면 무시
        if buf.duration < MIN_SPEECH_DURATION:
            buf.clear()
            return

        self._processing.add(uid)
        try:
            wav_bytes = buf.to_wav_bytes()
            duration = buf.duration
            buf.clear()

            print(f"[듣기] {member.display_name}: {duration:.1f}초 발화 감지", flush=True)
            await self.cog.process_speech(
                self.text_channel, member, wav_bytes, duration
            )
        finally:
            self._processing.discard(uid)

    def cleanup(self):
        self.buffers.clear()


class VoiceListenCog(commands.Cog, name="음성듣기"):
    """음성채널에서 듣고 키워드 감지 시 채팅 응답"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.chat_client = ChatClient()
        self.active_sinks: Dict[str, ListenSink] = {}  # guild_id -> sink

    async def cog_unload(self):
        # 모든 리스닝 중지
        for guild_id, sink in list(self.active_sinks.items()):
            await self.stop_listening(guild_id)
        await self.chat_client.close()

    @commands.command(name="듣기")
    async def listen_start(self, ctx: commands.Context):
        """음성채널에서 듣기 시작 (!듣기)"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("먼저 음성채널에 들어가줘.", mention_author=False)
            return

        guild_id = str(ctx.guild.id)

        # 이전 상태 강제 정리
        if guild_id in self.active_sinks:
            await self.stop_listening(guild_id)
            await asyncio.sleep(0.5)

        voice_channel = ctx.author.voice.channel
        vm = VoiceManager()

        # 기존 음성 연결 완전히 정리
        existing_vc = ctx.guild.voice_client
        if existing_vc:
            try:
                await existing_vc.disconnect(force=True)
            except Exception:
                pass
            vm.voice_clients.pop(guild_id, None)
            await asyncio.sleep(1)

        # VoiceRecvClient로 연결 (listen 지원)
        try:
            vc = await voice_channel.connect(cls=voice_recv.VoiceRecvClient, self_deaf=False)
            vm.voice_clients[guild_id] = vc
            print(f"[듣기] VoiceClient 타입: {type(vc).__name__}", flush=True)
            print(f"[듣기] listen 메서드 존재: {hasattr(vc, 'listen')}", flush=True)
        except Exception as e:
            await ctx.reply(f"음성채널 연결 실패: {e}", mention_author=False)
            return

        # ListenSink 생성 및 연결
        sink = ListenSink(self, guild_id, ctx.channel)

        try:
            vc.listen(sink)
            # listen 성공한 후에만 active_sinks에 등록
            self.active_sinks[guild_id] = sink
        except Exception as e:
            await ctx.reply(f"듣기 시작 실패: {e}", mention_author=False)
            return

        await ctx.reply(
            f"듣기 시작 - {voice_channel.name}\n\"데비야\" 같은 키워드로 말 걸어봐.",
            mention_author=False,
        )
        print(f"[듣기] 시작: {ctx.guild.name} / {voice_channel.name}", flush=True)

    @commands.command(name="듣기중지")
    async def listen_stop(self, ctx: commands.Context):
        """듣기 중지 (!듣기중지)"""
        guild_id = str(ctx.guild.id)
        await self.stop_listening(guild_id)
        await ctx.reply("듣기 중지.", mention_author=False)

    async def stop_listening(self, guild_id: str):
        """리스닝 중지"""
        sink = self.active_sinks.pop(guild_id, None)
        if sink:
            sink.cleanup()

        vm = VoiceManager()
        vc = vm.get_voice_client(guild_id)
        if vc and vc.is_listening():
            vc.stop_listening()

        print(f"[듣기] 중지: {guild_id}", flush=True)

    async def process_speech(
        self,
        text_channel: discord.TextChannel,
        member: discord.Member,
        wav_bytes: bytes,
        duration: float,
    ):
        """녹음된 발화를 omni 모델에 바로 전달 → 키워드 감지 + 응답을 한번에"""
        import aiohttp

        audio_b64 = base64.b64encode(wav_bytes).decode()

        # omni 모델에 오디오 직접 전달
        # 모델이 키워드 감지 + 응답을 한번에 처리
        prompt = (
            "이 오디오를 듣고 판단해:\n"
            "1. 이 사람이 '데비', '마를렌', '뎁마' 중 하나를 부르고 있으면 캐릭터로 대답해.\n"
            "2. 너를 부르지 않았으면 정확히 'IGNORE'만 출력해.\n"
            "반드시 둘 중 하나만 해."
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    AUDIO_CHAT_URL,
                    json={
                        "audio_base64": audio_b64,
                        "message": prompt,
                        "character": True,
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status != 200:
                        print(f"[듣기] omni 실패: {resp.status}", flush=True)
                        return
                    data = await resp.json()
                    response = data.get("response", "").strip()
        except Exception as e:
            print(f"[듣기] omni 에러: {e}", flush=True)
            return

        if not response or "IGNORE" in response:
            print(f"[듣기] {member.display_name}: 키워드 없음 (무시)", flush=True)
            return

        # 채팅에 텍스트로 출력
        elapsed = data.get("elapsed", 0)
        print(f"[듣기] {member.display_name} -> {response[:50]}... ({elapsed}초)", flush=True)
        await text_channel.send(response)
