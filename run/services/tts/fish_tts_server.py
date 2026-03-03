"""
Fish-Speech (OpenAudio S1-mini) TTS 서버 (Modal Serverless)

Zero-shot 음성 복제 + 빠른 추론 파이프라인입니다.
Qwen3-TTS로 생성한 레퍼런스 오디오로 debi/marlene 음색을 복제합니다.

배포:
    modal deploy run/services/tts/fish_tts_server.py

로컬 테스트:
    modal serve run/services/tts/fish_tts_server.py
"""

import os
import time
import modal

app = modal.App("fish-tts-server")

# fish-speech 설치 이미지
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg", "libsox-dev", "libsndfile1", "portaudio19-dev")
    .run_commands(
        "git clone https://github.com/fishaudio/fish-speech.git /opt/fish-speech",
        "cd /opt/fish-speech && pip install -e '.[cu129]'",
        gpu="A10G",
    )
    .pip_install("ormsgpack", "soundfile", "torchcodec")
    .run_commands(
        "python -c \""
        "import os; "
        "from huggingface_hub import snapshot_download; "
        "snapshot_download('fishaudio/openaudio-s1-mini', "
        "local_dir='/opt/fish-speech/checkpoints/openaudio-s1-mini', "
        "token=os.environ.get('HF_TOKEN'))\"",
        secrets=[modal.Secret.from_name("huggingface")],
    )
)

volume = modal.Volume.from_name("fish-tts-refs", create_if_missing=True)

# 레퍼런스 오디오의 텍스트 (생성 시 사용한 문장)
REF_TEXTS = {
    "debi": (
        "안녕하세요, 오늘 날씨가 정말 좋네요. 같이 게임 한 판 할까요? "
        "이터널 리턴 하고 싶어요. 오늘 첫 솔로 랭크를 했는데, 삼위를 했어요. "
        "다음에는 더 잘할 수 있을 거예요. 화이팅!"
    ),
    "marlene": (
        "안녕하세요, 오늘 날씨가 정말 좋네요. 같이 게임 한 판 할까요? "
        "이터널 리턴 하고 싶어요. 오늘 첫 솔로 랭크를 했는데, 삼위를 했어요. "
        "다음에는 더 잘할 수 있을 거예요. 화이팅!"
    ),
}

SPEAKER_REFS = {
    "debi": "/refs/debi_ref.wav",
    "marlene": "/refs/marlene_ref.wav",
}

LLAMA_PATH = "/opt/fish-speech/checkpoints/openaudio-s1-mini"
DECODER_PATH = "/opt/fish-speech/checkpoints/openaudio-s1-mini/codec.pth"
DECODER_CONFIG = "modded_dac_vq"


@app.cls(
    image=image,
    gpu="A10G",
    timeout=120,
    volumes={"/refs": volume},
    scaledown_window=600,
    startup_timeout=600,
)
class FishTTSModel:
    """Fish-Speech (OpenAudio S1-mini) zero-shot TTS"""

    @modal.enter()
    def load_model(self):
        """컨테이너 시작시 모델 로드 + compile"""
        import sys
        sys.path.insert(0, "/opt/fish-speech")

        # torchaudio 2.5+에서 list_audio_backends() 제거됨 → monkey-patch
        import torchaudio
        if not hasattr(torchaudio, "list_audio_backends"):
            torchaudio.list_audio_backends = lambda: ["soundfile"]

        from tools.server.model_manager import ModelManager
        from tools.server.inference import inference_wrapper

        self.inference_wrapper = inference_wrapper

        # ModelManager가 LLAMA + DAC 디코더 모두 로드
        self.manager = ModelManager(
            mode="tts",
            device="cuda",
            half=True,
            compile=False,
            llama_checkpoint_path=LLAMA_PATH,
            decoder_checkpoint_path=DECODER_PATH,
            decoder_config_name=DECODER_CONFIG,
        )

        # 레퍼런스 오디오 로드
        self.ref_audio = {}
        self.ref_loaded = []
        for speaker, path in SPEAKER_REFS.items():
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self.ref_audio[speaker] = f.read()
                self.ref_loaded.append(speaker)
                print(f"[OK] Reference loaded: {speaker} "
                      f"({len(self.ref_audio[speaker])} bytes)")
            else:
                print(f"[WARN] Reference not found: {path}")

        print(f"Model ready. Speakers: {self.ref_loaded}")

    def _generate(self, speaker: str, text: str, **kwargs) -> bytes:
        """텍스트를 음성으로 변환하고 WAV bytes 반환"""
        import io
        import struct
        import numpy as np

        from fish_speech.utils.schema import (
            ServeReferenceAudio,
            ServeTTSRequest,
        )

        refs = []
        if speaker in self.ref_audio:
            refs.append(ServeReferenceAudio(
                audio=self.ref_audio[speaker],
                text=REF_TEXTS.get(speaker, ""),
            ))

        # 텍스트 끝에 구두점이 없으면 추가 (모델이 끝을 인식하도록)
        if text and text[-1] not in ".。!！?？~…,，":
            text = text + "."

        request = ServeTTSRequest(
            text=text,
            references=refs,
            format="wav",
            chunk_length=200,
            streaming=False,
            use_memory_cache="on",
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.7),
            repetition_penalty=kwargs.get("repetition_penalty", 1.2),
            max_new_tokens=kwargs.get("max_new_tokens", 2048),
        )

        # inference_wrapper yields: ndarray (float32) or bytes chunks
        pcm_chunks = []
        for chunk in self.inference_wrapper(request, self.manager.tts_inference_engine):
            if isinstance(chunk, np.ndarray):
                if chunk.dtype in (np.float32, np.float64):
                    chunk = np.clip(chunk, -1.0, 1.0)
                    chunk = (chunk * 32767).astype(np.int16)
                else:
                    chunk = chunk.astype(np.int16)
                pcm_chunks.append(chunk.tobytes())
            elif isinstance(chunk, bytes) and len(chunk) > 0:
                pcm_chunks.append(chunk)

        pcm_data = b"".join(pcm_chunks)

        if not pcm_data:
            raise RuntimeError("No audio generated")

        # 끝에 200ms 무음 패딩 추가 (끝 잘림 방지)
        sample_rate = 44100
        pad_samples = int(sample_rate * 0.2)
        pcm_data += b"\x00\x00" * pad_samples
        buf = io.BytesIO()
        # WAV header
        data_size = len(pcm_data)
        buf.write(b"RIFF")
        buf.write(struct.pack("<I", 36 + data_size))
        buf.write(b"WAVE")
        buf.write(b"fmt ")
        buf.write(struct.pack("<I", 16))  # chunk size
        buf.write(struct.pack("<H", 1))   # PCM format
        buf.write(struct.pack("<H", 1))   # mono
        buf.write(struct.pack("<I", sample_rate))
        buf.write(struct.pack("<I", sample_rate * 2))  # byte rate
        buf.write(struct.pack("<H", 2))   # block align
        buf.write(struct.pack("<H", 16))  # bits per sample
        buf.write(b"data")
        buf.write(struct.pack("<I", data_size))
        buf.write(pcm_data)

        return buf.getvalue()

    @modal.fastapi_endpoint(method="POST", docs=True)
    async def tts(self, request: dict):
        """POST /tts - 텍스트를 음성으로 변환"""
        from fastapi.responses import Response

        text = request.get("text", "")
        speaker = request.get("speaker", "debi")
        guild_name = request.get("guild_name", "unknown")
        channel_name = request.get("channel_name", "unknown")
        user_name = request.get("user_name", "unknown")

        print(f"[TTS] {guild_name} | {channel_name} | "
              f"{user_name} | {speaker} | {text[:50]}")

        if not text.strip():
            return {"error": "Text is empty"}
        if len(text) > 500:
            text = text[:500]
        if speaker not in self.ref_audio:
            return {
                "error": f"Speaker '{speaker}' not available. "
                         f"Available: {self.ref_loaded}"
            }

        total_start = time.time()
        try:
            wav_bytes = self._generate(speaker, text)
            total_time = time.time() - total_start
            print(f"[TTS] Done: {total_time:.2f}s, {len(wav_bytes)} bytes")

            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={"X-Total-Time": f"{total_time:.3f}"},
            )
        except Exception as e:
            import traceback
            print(f"[ERROR] {traceback.format_exc()}")
            return {"error": str(e)}

    @modal.fastapi_endpoint(method="GET")
    def health(self):
        """GET /health - 상태 확인"""
        return {
            "status": "running",
            "engine": "openaudio-s1-mini",
            "speakers_loaded": self.ref_loaded,
        }
