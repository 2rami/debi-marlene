"""
음성 듣기 Cog

음성채널에서 유저 음성을 수신하고 Gemma4 omni로 키워드 감지 + AI 응답.

파이프라인:
  discord-ext-voice-recv (transport 복호화)
  -> DAVE 2차 복호화 (davey)
  -> opus -> PCM 디코딩 (discord.opus.Decoder)
  -> WebRTC VAD 음성 감지
  -> pre-buffer 0.5s 포함 녹음
  -> WAV -> Gemma4Audio (키워드 + 응답)
"""

import asyncio
import base64
import io
import logging
import struct
import time
import threading
from collections import deque
from typing import Dict, Optional

import aiohttp
import discord
import webrtcvad
from discord import app_commands
from discord.ext import commands
from discord.opus import Decoder as OpusDecoder

import davey
import discord.ext.voice_recv as voice_recv

from run.services.voice_manager import VoiceManager

logger = logging.getLogger(__name__)

# voice_recv 내부 로그 스팸 억제
logging.getLogger("discord.ext.voice_recv.reader").setLevel(logging.WARNING)
logging.getLogger("discord.ext.voice_recv.gateway").setLevel(logging.WARNING)
logging.getLogger("discord.ext.voice_recv.opus").setLevel(logging.WARNING)

# 오디오 설정
SAMPLE_RATE = 48000
CHANNELS = 2
SAMPLE_WIDTH = 2  # 16-bit
FRAME_DURATION_MS = 20  # opus 프레임 길이
FRAME_SIZE = SAMPLE_RATE * CHANNELS * SAMPLE_WIDTH * FRAME_DURATION_MS // 1000  # 3840 bytes

# VAD 설정
VAD_SAMPLE_RATE = 16000  # webrtcvad는 8k/16k/32k만 지원
VAD_AGGRESSIVENESS = 3   # 0(느슨) ~ 3(엄격)
PRE_BUFFER_SEC = 0.5     # 발화 시작 전 포함할 오디오 (초)
PRE_BUFFER_FRAMES = int(PRE_BUFFER_SEC / (FRAME_DURATION_MS / 1000))  # 25 프레임
SILENCE_FRAMES = int(1.5 / (FRAME_DURATION_MS / 1000))  # 75 프레임 (1.5초 무음)
MIN_SPEECH_FRAMES = int(0.5 / (FRAME_DURATION_MS / 1000))  # 25 프레임 (0.5초)
MAX_SPEECH_SEC = 25

AUDIO_CHAT_URL = "https://goenho0613--gemma4-chat-server-gemma4audio-audio-chat.modal.run"


def pcm_to_mono_16k(pcm: bytes) -> bytes:
    """스테레오 48kHz PCM -> 모노 16kHz PCM (VAD용)"""
    samples = struct.unpack(f'<{len(pcm) // 2}h', pcm)
    # 스테레오 -> 모노 (L+R 평균)
    mono = [(samples[i] + samples[i + 1]) // 2 for i in range(0, len(samples), 2)]
    # 48kHz -> 16kHz (3배 다운샘플)
    downsampled = mono[::3]
    return struct.pack(f'<{len(downsampled)}h', *downsampled)


class SpeechDetector:
    """유저별 VAD + pre-buffer 기반 발화 감지기"""

    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        self.decoder = OpusDecoder()
        self.pre_buffer: deque = deque(maxlen=PRE_BUFFER_FRAMES)
        self.speech_chunks: list[bytes] = []
        self.is_speaking: bool = False
        self.silence_count: int = 0
        self._lock = threading.Lock()

    def feed_opus(self, opus_data: bytes) -> Optional[bytes]:
        """opus 프레임을 받아서 VAD 처리.

        Returns:
            완성된 발화의 WAV bytes, 또는 None (아직 발화 중/대기 중)
        """
        try:
            pcm = self.decoder.decode(opus_data, fec=False)
        except Exception:
            return None

        # VAD 체크 (모노 16kHz로 변환)
        vad_data = pcm_to_mono_16k(pcm)
        try:
            is_speech = self.vad.is_speech(vad_data, VAD_SAMPLE_RATE)
        except Exception:
            is_speech = False

        with self._lock:
            if is_speech:
                if not self.is_speaking:
                    # 발화 시작 -- pre-buffer 포함
                    self.speech_chunks = list(self.pre_buffer)
                    self.is_speaking = True
                self.speech_chunks.append(pcm)
                self.silence_count = 0

                # 최대 길이 체크
                duration = len(self.speech_chunks) * FRAME_DURATION_MS / 1000
                if duration >= MAX_SPEECH_SEC:
                    return self._finalize()
            else:
                if self.is_speaking:
                    self.silence_count += 1
                    self.speech_chunks.append(pcm)  # trailing silence 포함
                    if self.silence_count >= SILENCE_FRAMES:
                        return self._finalize()
                else:
                    # 대기 중 -- pre-buffer에 추가
                    self.pre_buffer.append(pcm)

        return None

    def _finalize(self) -> Optional[bytes]:
        """현재 발화를 WAV로 변환하고 초기화"""
        if len(self.speech_chunks) < MIN_SPEECH_FRAMES:
            self.speech_chunks = []
            self.is_speaking = False
            self.silence_count = 0
            return None

        pcm_data = b"".join(self.speech_chunks)
        self.speech_chunks = []
        self.is_speaking = False
        self.silence_count = 0

        # PCM -> WAV
        buf = io.BytesIO()
        import wave
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm_data)
        return buf.getvalue()

    @property
    def speech_duration(self) -> float:
        with self._lock:
            return len(self.speech_chunks) * FRAME_DURATION_MS / 1000


class ListenSink(voice_recv.AudioSink):
    """음성채널 오디오를 수신하는 Sink.

    write()는 packet-router 스레드에서 호출됨.
    완성된 발화는 asyncio 이벤트 루프로 넘겨서 처리.
    """

    def __init__(self, cog: "VoiceListenCog", guild_id: str, text_channel: discord.TextChannel):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
        self.text_channel = text_channel
        self.detectors: Dict[int, SpeechDetector] = {}
        self._user_map: Dict[int, discord.Member] = {}
        self._first_data = True
        self._feed_count = 0

    def wants_opus(self) -> bool:
        return True

    def _get_dave_session(self):
        vc = VoiceManager().get_voice_client(self.guild_id)
        if vc is None:
            return None
        conn = getattr(vc, '_connection', None)
        if conn is None:
            return None
        return getattr(conn, 'dave_session', None)

    def write(self, user, data: voice_recv.VoiceData):
        try:
            self._write_inner(user, data)
        except Exception:
            pass

    def _write_inner(self, user, data: voice_recv.VoiceData):
        if user is None or user.bot:
            return

        encrypted_data = data.opus
        if not encrypted_data:
            return

        uid = user.id

        # DAVE 2차 복호화
        dave = self._get_dave_session()
        if dave and dave.ready and not dave.can_passthrough(uid):
            try:
                opus_data = dave.decrypt(uid, davey.MediaType.audio, encrypted_data)
            except ValueError:
                opus_data = encrypted_data
        else:
            opus_data = encrypted_data

        if not opus_data or opus_data == b'\xf8\xff\xfe':
            return

        if self._first_data:
            self._first_data = False
            logger.warning(f"[듣기] 첫 오디오: {user.display_name} len={len(opus_data)}")

        # Member 캐싱
        if isinstance(user, discord.Member):
            self._user_map[uid] = user

        # SpeechDetector에 피딩
        if uid not in self.detectors:
            self.detectors[uid] = SpeechDetector()

        wav_bytes = self.detectors[uid].feed_opus(opus_data)
        if wav_bytes is not None:
            # 발화 완성 -- asyncio 이벤트 루프로 처리 넘기기
            member = self._user_map.get(uid)
            duration = len(wav_bytes) / (SAMPLE_RATE * CHANNELS * SAMPLE_WIDTH)
            logger.warning(f"[듣기] 발화 감지: {getattr(member, 'display_name', uid)} {duration:.1f}초")
            self.cog.bot.loop.call_soon_threadsafe(
                asyncio.ensure_future,
                self.cog.process_speech(self.text_channel, member, wav_bytes, duration),
            )

        self._feed_count += 1
        if self._feed_count in (10, 100, 500):
            det = self.detectors.get(uid)
            speaking = det.is_speaking if det else False
            logger.warning(f"[듣기] feed #{self._feed_count} speaking={speaking}")

    def cleanup(self):
        self.detectors.clear()


class VoiceListenCog(commands.Cog, name="음성듣기"):
    """음성채널에서 듣고 키워드 감지 시 채팅 응답"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_sinks: Dict[str, ListenSink] = {}

    async def cog_unload(self):
        for guild_id in list(self.active_sinks):
            await self.stop_listening(guild_id)

    @commands.Cog.listener()
    async def on_ready(self):
        """봇 시작 시 유령 음성 세션 정리 (백그라운드)"""
        asyncio.create_task(self._cleanup_ghost_sessions())

    async def _cleanup_ghost_sessions(self):
        await asyncio.sleep(3)  # 다른 초기화 끝날 때까지 대기
        for guild in self.bot.guilds:
            if guild.me and guild.me.voice:
                logger.info(f"[듣기] 유령 세션 정리: {guild.name}")
                try:
                    if guild.voice_client:
                        await guild.voice_client.disconnect(force=True)
                    await guild.change_voice_state(channel=None)
                except Exception:
                    pass

    @app_commands.command(name="듣기", description="음성채널에서 듣기 시작")
    @app_commands.guild_only()
    async def listen_start(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
        except discord.NotFound:
            return  # interaction 만료

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("먼저 음성채널에 들어가줘.")
            return

        guild_id = str(interaction.guild_id)
        voice_channel = interaction.user.voice.channel
        vm = VoiceManager()

        # 이전 상태 강제 정리
        if guild_id in self.active_sinks:
            await self.stop_listening(guild_id)
            await asyncio.sleep(0.5)

        existing_vc = interaction.guild.voice_client
        if existing_vc:
            try:
                await existing_vc.disconnect(force=True)
            except Exception:
                pass
            vm.voice_clients.pop(guild_id, None)
            await asyncio.sleep(1)

        try:
            await interaction.guild.change_voice_state(channel=None)
            await asyncio.sleep(0.5)
        except Exception:
            pass

        # VoiceRecvClient로 연결
        try:
            vm.listening_guilds.add(guild_id)
            vc = await voice_channel.connect(
                cls=voice_recv.VoiceRecvClient,
                self_deaf=False,
                reconnect=False,
            )
            vm.voice_clients[guild_id] = vc
        except Exception as e:
            vm.listening_guilds.discard(guild_id)
            await interaction.followup.send(f"음성채널 연결 실패: {e}")
            return

        sink = ListenSink(self, guild_id, interaction.channel)

        try:
            vc.listen(sink)
            self.active_sinks[guild_id] = sink
        except Exception as e:
            await self.stop_listening(guild_id)
            await interaction.followup.send(f"듣기 시작 실패: {e}")
            return

        await interaction.followup.send(
            f"듣기 시작 - {voice_channel.name}\n\"데비야\" 같은 키워드로 말 걸어봐."
        )
        logger.info(f"[듣기] 시작: {interaction.guild.name} / {voice_channel.name}")

    @app_commands.command(name="듣기중지", description="음성채널 듣기 중지")
    @app_commands.guild_only()
    async def listen_stop(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild_id)

        if guild_id not in self.active_sinks:
            await interaction.response.send_message("듣고 있지 않아.", ephemeral=True)
            return

        await self.stop_listening(guild_id)
        await interaction.response.send_message("듣기 중지.")

    async def stop_listening(self, guild_id: str):
        sink = self.active_sinks.pop(guild_id, None)
        if sink:
            sink.cleanup()

        vm = VoiceManager()
        vm.listening_guilds.discard(guild_id)

        vc = vm.get_voice_client(guild_id)
        if vc:
            try:
                if hasattr(vc, 'is_listening') and vc.is_listening():
                    vc.stop_listening()
            except Exception:
                pass
            try:
                await vc.disconnect(force=True)
            except Exception:
                pass
            vm.voice_clients.pop(guild_id, None)

        logger.info(f"[듣기] 중지: {guild_id}")

    async def process_speech(
        self,
        text_channel: discord.TextChannel,
        member: Optional[discord.Member],
        wav_bytes: bytes,
        duration: float,
    ):
        display = member.display_name if member else "unknown"
        logger.warning(f"[듣기] Gemma4 전송: {display} {duration:.1f}초")

        audio_b64 = base64.b64encode(wav_bytes).decode()

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
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"[듣기] omni 응답 실패: {resp.status}")
                        return
                    data = await resp.json()
                    response = data.get("response", "").strip()
        except asyncio.TimeoutError:
            logger.warning("[듣기] omni 타임아웃 (cold start?)")
            return
        except Exception as e:
            logger.error(f"[듣기] omni 에러: {e}")
            return

        if not response or "IGNORE" in response:
            logger.warning(f"[듣기] {display}: IGNORE")
            return

        logger.warning(f"[듣기] {display} -> {response[:80]}")
        await text_channel.send(response)
