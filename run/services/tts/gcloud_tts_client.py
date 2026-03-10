"""
Google Cloud TTS 클라이언트

GCP Text-to-Speech API를 사용합니다.
LINEAR16(PCM) 포맷으로 요청 → FFmpeg 없이 discord.PCMAudio로 직접 재생.
"""

import os
import io
import struct
import wave
import asyncio
import audioop
import hashlib
import logging
from google.cloud import texttospeech

logger = logging.getLogger(__name__)

VOICES = {
    "debi": texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Standard-A",
    ),
    "marlene": texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Standard-B",
    ),
}

# LINEAR16 48kHz: Discord가 필요로 하는 PCM 포맷과 동일
AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    sample_rate_hertz=48000,
    speaking_rate=1.0,
)


class GCloudTTSClient:

    def __init__(self):
        self.temp_dir = "/tmp/tts_audio"
        self.client = None
        os.makedirs(self.temp_dir, exist_ok=True)

    async def initialize(self):
        self.client = texttospeech.TextToSpeechClient()
        logger.info("Google Cloud TTS 클라이언트 초기화 완료")

    def _synthesize(self, text: str, speaker: str) -> bytes:
        """동기 API 호출 (to_thread로 실행됨)"""
        voice = VOICES.get(speaker, VOICES["debi"])
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=AUDIO_CONFIG,
        )
        return response.audio_content

    def _wav_to_stereo_pcm(self, wav_bytes: bytes) -> bytes:
        """WAV (mono 48kHz 16bit) → stereo PCM bytes (Discord 포맷), 앞뒤 무음 제거"""
        with wave.open(io.BytesIO(wav_bytes), 'rb') as wav:
            mono_pcm = wav.readframes(wav.getnframes())
        # 앞쪽 무음 제거 (Google TTS가 0.3~0.5초 무음 삽입)
        mono_pcm = self._trim_silence(mono_pcm, sample_width=2)
        # mono → stereo (Discord는 stereo 필요)
        return audioop.tostereo(mono_pcm, 2, 1, 1)

    @staticmethod
    def _trim_silence(pcm_data: bytes, sample_width: int = 2, threshold: int = 500) -> bytes:
        """PCM 데이터 앞쪽 무음을 제거합니다."""
        # 16-bit mono: 2 bytes per sample
        # threshold 500 ≈ 최대값(32767)의 1.5% — 저레벨 노이즈까지 잘라냄
        for i in range(0, len(pcm_data) - sample_width, sample_width):
            sample = abs(struct.unpack_from('<h', pcm_data, i)[0])
            if sample > threshold:
                return pcm_data[i:]
        return pcm_data

    async def text_to_speech(
        self,
        text: str,
        speaker: str = "debi",
        language: str = "ko",
        output_path=None,
        max_retries: int = 2,
        guild_name=None,
        channel_name=None,
        user_name=None,
    ) -> str:
        if len(text) > 500:
            text = text[:500]

        if output_path is None:
            text_hash = hashlib.md5(f"{text}{speaker}".encode()).hexdigest()[:8]
            output_path = os.path.join(self.temp_dir, f"gctts_{speaker}_{text_hash}.pcm")

        # 캐시: 동일 텍스트면 재사용
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path

        # 블로킹 API 호출을 별도 스레드에서 실행 (이벤트 루프 안 막음)
        wav_bytes = await asyncio.to_thread(self._synthesize, text, speaker)

        # WAV → stereo PCM 변환
        stereo_pcm = self._wav_to_stereo_pcm(wav_bytes)

        with open(output_path, "wb") as f:
            f.write(stereo_pcm)

        return output_path

    def cleanup_temp_files(self):
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith("gctts_") and file.endswith(".pcm"):
                    os.remove(os.path.join(self.temp_dir, file))
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")

    def list_speakers(self):
        return list(VOICES.keys())
