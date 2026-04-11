"""
음성 듣기 Cog

음성채널에서 유저 음성을 수신하고 Qwen3.5-Omni로 키워드 감지 + AI 응답.

파이프라인:
  discord-ext-voice-recv (transport 복호화)
  -> DAVE 2차 복호화 (davey)
  -> opus -> PCM 디코딩 (discord.opus.Decoder)
  -> WebRTC VAD 음성 감지
  -> pre-buffer 0.5s 포함 녹음
  -> WAV -> Qwen3.5-Omni API (키워드 + 응답)
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

import os

import discord
import webrtcvad
from openai import AsyncOpenAI
from discord import app_commands
from discord.ext import commands
from discord.opus import Decoder as OpusDecoder

import davey
import discord.ext.voice_recv as voice_recv

from run.services.voice_manager import VoiceManager
from run.services.tts import TTSService

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
SILENCE_FRAMES = int(0.7 / (FRAME_DURATION_MS / 1000))  # 35 프레임 (0.7초 무음)
MIN_SPEECH_FRAMES = int(0.3 / (FRAME_DURATION_MS / 1000))  # 15 프레임 (0.3초)
MAX_SPEECH_SEC = 8

OMNI_MODEL = "qwen3.5-omni-plus"
SYSTEM_PROMPT = (
    "너는 이터널 리턴의 쌍둥이 실험체 데비&마를렌이야. 한국어로만 대답해. 이모지 사용하지 마.\n"
    "데비(언니): 활발, 천진난만, 장난기. 직설적이고 솔직한 10대 소녀 말투.\n"
    '마를렌(동생): 냉소적이지만 자연스러운 10대 소녀. 말이 짧고 차분함. "..."으로 시작하기도 함.\n'
    "규칙:\n"
    "- '데비야/데비' 호출 -> 데비가 메인으로 대답. 마를렌은 가끔 한마디 끼어들기만.\n"
    "- '마를렌아/마를렌' 호출 -> 마를렌이 메인으로 대답. 데비가 가끔 끼어들기만.\n"
    "- '뎁마' 호출 -> 둘 다 대답.\n"
    "- 호출된 캐릭터만 대답해도 됨. 매번 둘 다 말할 필요 없음.\n"
    "형식: 데비: (대사) 또는 마를렌: (대사). 각자 1-2문장으로 짧게."
)

# 웨이크워드 응답 음성 (로컬 재생용)
WAKEWORD_THRESHOLD_SEC = 2.0  # 이 이하면 웨이크워드로 판단
LISTEN_MODE_TIMEOUT_SEC = 8.0  # 듣기 모드 타임아웃

SFX_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")
ACK_AUDIO = {
    "debi": os.path.join(SFX_DIR, "debi", "Debi_selected_1_01_01.wav"),
    "marlene": os.path.join(SFX_DIR, "marlene", "Marlene_selected_1_01_01.wav"),
}


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


def parse_character_lines(text: str) -> list[tuple[str, str]]:
    """응답에서 화자별 대사를 분리.

    Returns: [(speaker, line), ...] — speaker는 "debi" 또는 "marlene"
    """
    lines = []
    for raw in text.split("\n"):
        raw = raw.strip()
        if not raw:
            continue
        if raw.startswith("데비:") or raw.startswith("데비 :"):
            lines.append(("debi", raw.split(":", 1)[1].strip()))
        elif raw.startswith("마를렌:") or raw.startswith("마를렌 :"):
            lines.append(("marlene", raw.split(":", 1)[1].strip()))
        else:
            lines.append(("debi", raw))
    return lines


class VoiceListenCog(commands.Cog, name="음성듣기"):
    """음성채널에서 듣고 키워드 감지 시 음성 + 텍스트 응답"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_sinks: Dict[str, ListenSink] = {}
        self.tts_services: Dict[str, TTSService] = {}
        # 유저별 듣기 모드: {user_id: expiry_time}
        self.listen_mode: Dict[int, float] = {}
        self.listen_mode_timers: Dict[int, asyncio.Task] = {}

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

    def _is_listen_mode(self, user_id: int) -> bool:
        """유저가 듣기 모드 중인지 확인"""
        expiry = self.listen_mode.get(user_id)
        if expiry and time.time() < expiry:
            return True
        self.listen_mode.pop(user_id, None)
        return False

    def _enter_listen_mode(self, user_id: int):
        """듣기 모드 진입 (타임아웃 후 자동 해제)"""
        self.listen_mode[user_id] = time.time() + LISTEN_MODE_TIMEOUT_SEC
        # 이전 타이머 취소
        old_task = self.listen_mode_timers.pop(user_id, None)
        if old_task and not old_task.done():
            old_task.cancel()

        async def _expire():
            await asyncio.sleep(LISTEN_MODE_TIMEOUT_SEC)
            self.listen_mode.pop(user_id, None)
            self.listen_mode_timers.pop(user_id, None)
            logger.info(f"[듣기] 듣기 모드 타임아웃: {user_id}")

        self.listen_mode_timers[user_id] = asyncio.create_task(_expire())

    def _exit_listen_mode(self, user_id: int):
        """듣기 모드 해제"""
        self.listen_mode.pop(user_id, None)
        old_task = self.listen_mode_timers.pop(user_id, None)
        if old_task and not old_task.done():
            old_task.cancel()

    async def process_speech(
        self,
        text_channel: discord.TextChannel,
        member: Optional[discord.Member],
        wav_bytes: bytes,
        duration: float,
    ):
        uid = member.id if member else 0
        display = member.display_name if member else "unknown"
        in_listen_mode = self._is_listen_mode(uid)

        # 하이브리드 분기
        if in_listen_mode:
            # 듣기 모드: 키워드 체크 없이 바로 대화
            self._exit_listen_mode(uid)
            logger.warning(f"[듣기] 듣기 모드 발화: {display} {duration:.1f}초")
            await self._respond_with_ai(text_channel, member, wav_bytes, keyword_check=False)
        elif duration < WAKEWORD_THRESHOLD_SEC:
            # 짧은 발화: 웨이크워드로 판단 -> ack 재생 + 듣기 모드
            logger.warning(f"[듣기] 짧은 발화 (웨이크워드?): {display} {duration:.1f}초")
            await self._play_ack(text_channel, "debi")
            self._enter_listen_mode(uid)
        else:
            # 긴 발화: 키워드 + 응답 한번에
            logger.warning(f"[듣기] 긴 발화 (원샷): {display} {duration:.1f}초")
            await self._respond_with_ai(text_channel, member, wav_bytes, keyword_check=True)

    async def _play_ack(self, text_channel: discord.TextChannel, character: str):
        """웨이크워드 응답 음성 재생 (로컬 파일, API 호출 없음)"""
        guild_id = str(text_channel.guild.id)
        vm = VoiceManager()
        vc = vm.get_voice_client(guild_id)
        if not vc or not vc.is_connected():
            return

        ack_path = ACK_AUDIO.get(character)
        if not ack_path or not os.path.exists(ack_path):
            return

        try:
            await vm.play_tts(guild_id, ack_path)
        except Exception as e:
            logger.error(f"[듣기] ack 재생 실패: {e}")

    async def _respond_with_ai(
        self,
        text_channel: discord.TextChannel,
        member: Optional[discord.Member],
        wav_bytes: bytes,
        keyword_check: bool,
    ):
        """Qwen3.5-Omni로 응답 생성 + TTS 재생"""
        display = member.display_name if member else "unknown"
        audio_b64 = base64.b64encode(wav_bytes).decode()

        if keyword_check:
            prompt = (
                "이 오디오를 듣고 판단해:\n"
                "1. 이 사람이 '데비', '마를렌', '뎁마' 중 하나를 부르고 있으면 캐릭터로 대답해.\n"
                "2. 너를 부르지 않았으면 정확히 'IGNORE'만 출력해.\n"
                "반드시 둘 중 하나만 해.\n\n"
                "응답 형식 (호출된 경우):\n"
                "[들린 말] 상대방이 말한 내용 그대로\n"
                "데비: 대사\n"
                "마를렌: 대사 (선택)\n\n"
                "주의: 대사에서 상대방이 한 말을 따라하거나 반복하지 마. 자연스럽게 대답만 해."
            )
        else:
            prompt = (
                "이 오디오를 듣고 캐릭터로 대답해.\n\n"
                "응답 형식:\n"
                "[들린 말] 상대방이 말한 내용 그대로\n"
                "데비: 대사\n"
                "마를렌: 대사 (선택)\n\n"
                "주의: 대사에서 상대방이 한 말을 따라하거나 반복하지 마. 자연스럽게 대답만 해."
            )

        try:
            client = AsyncOpenAI(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            )
            completion = await client.chat.completions.create(
                model=OMNI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": f"data:;base64,{audio_b64}",
                                    "format": "wav",
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    },
                ],
                modalities=["text"],
            )
            response = completion.choices[0].message.content.strip()
        except asyncio.TimeoutError:
            logger.warning("[듣기] omni 타임아웃")
            return
        except Exception as e:
            logger.error(f"[듣기] omni 에러: {e}")
            return

        if not response or "IGNORE" in response:
            logger.warning(f"[듣기] {display}: IGNORE")
            return

        # [들린 말] 추출
        heard = ""
        reply_lines = []
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("[들린 말]"):
                heard = line.replace("[들린 말]", "").strip()
            elif line:
                reply_lines.append(line)
        reply_text = "\n".join(reply_lines)

        logger.warning(f"[듣기] {display} -> heard='{heard}' reply='{reply_text[:80]}'")

        # 텍스트 채널에 전송
        msg = f"**{display}:** {heard}\n{reply_text}" if heard else reply_text
        await text_channel.send(msg)

        # TTS로 음성채널에서 재생
        guild_id = str(text_channel.guild.id)
        vm = VoiceManager()
        vc = vm.get_voice_client(guild_id)
        if not vc or not vc.is_connected():
            return

        try:
            character_lines = parse_character_lines(reply_text)
            for speaker, line in character_lines:
                if not line:
                    continue
                if speaker not in self.tts_services:
                    svc = TTSService(speaker=speaker)
                    await svc.initialize()
                    self.tts_services[speaker] = svc
                audio_path = await self.tts_services[speaker].text_to_speech(text=line)
                await vm.play_tts(guild_id, audio_path)
        except Exception as e:
            logger.error(f"[듣기] TTS 재생 실패: {e}")
