"""
edge-tts + RVC v2 TTS 서버 (Modal Serverless)

빠른 TTS(edge-tts) + 음성 변환(RVC v2) 파이프라인입니다.
edge-tts로 한국어 음성을 생성하고, RVC v2로 debi/marlene 음색으로 변환합니다.

배포:
    modal deploy run/services/tts/edgetts_rvc_server.py

로컬 테스트:
    modal serve run/services/tts/edgetts_rvc_server.py
"""

import os
import time
import modal

app = modal.App("edgetts-rvc-server")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "libsndfile1")
    .pip_install(
        "edge-tts",
        "soundfile",
        "numpy<2",
        "librosa==0.10.2",
        "torch==2.1.0",
        "torchaudio==2.1.0",
        "faiss-cpu",
        "scipy",
        "fastapi[standard]",
        "torchcrepe",
        "pyworld",
        "praat-parselmouth",
        "huggingface_hub",
    )
    .run_commands(
        "pip install 'pip==23.3.2'"
        " && pip install fairseq"
        " && pip install --upgrade pip"
    )
    .pip_install(
        "https://github.com/CircuitCM/RVC-inference/raw/main/dist/inferrvc-1.0-py3-none-any.whl",
        extra_options="--no-deps",
    )
)

volume = modal.Volume.from_name("rvc-model-cache", create_if_missing=True)

# edge-tts 한국어 음성 (기본: 여성)
EDGE_TTS_VOICE = "ko-KR-SunHiNeural"

# RVC 설정
SPEAKER_CONFIG = {
    "debi": {
        "model": "/cache/models/debi.pth",
        "index": "/cache/models/debi.index",
        "f0_up_key": 0,  # 피치 조정 (필요시 변경)
    },
    "marlene": {
        "model": "/cache/models/marlene.pth",
        "index": "/cache/models/marlene.index",
        "f0_up_key": 0,
    },
}


@app.cls(
    image=image,
    gpu="T4",
    timeout=120,
    volumes={"/cache": volume},
    scaledown_window=120,
    allow_concurrent_inputs=5,
)
class EdgeTTSRVC:
    """edge-tts + RVC v2 TTS 파이프라인"""

    @modal.enter()
    def load_models(self):
        """컨테이너 시작시 RVC 모델 로드"""
        self.rvc_models = {}
        self.load_errors = []

        for speaker, config in SPEAKER_CONFIG.items():
            model_path = config["model"]
            index_path = config["index"]

            if not os.path.exists(model_path):
                msg = f"{speaker}: model not found at {model_path}"
                print(f"[WARN] {msg}")
                self.load_errors.append(msg)
                continue

            try:
                from inferrvc import RVC
                import inferrvc.modules as rvc_mod
                index = index_path if os.path.exists(index_path) else None

                # ResampleCache monkey-patch: fp16 오디오를 float로 변환 후 resample
                _orig_resample = rvc_mod.ResampleCache.resample
                @staticmethod
                def _safe_resample(fromto, audio, device):
                    return _orig_resample(fromto, audio.float(), device)
                rvc_mod.ResampleCache.resample = _safe_resample

                rvc = RVC(model_path, index=index)
                self.rvc_models[speaker] = rvc
                print(f"[OK] RVC model loaded: {speaker}")
            except Exception as e:
                msg = f"{speaker}: {e}"
                print(f"[ERROR] {msg}")
                self.load_errors.append(msg)

        print(f"Models ready: {list(self.rvc_models.keys())}")

    @modal.fastapi_endpoint(method="POST", docs=True)
    async def tts(self, request: dict):
        """POST /tts - 텍스트를 음성으로 변환"""
        import numpy as np
        import soundfile as sf
        import subprocess
        import tempfile
        from edge_tts import Communicate
        from fastapi.responses import Response

        text = request.get("text", "")
        speaker = request.get("speaker", "debi")
        guild_name = request.get("guild_name", "unknown")
        channel_name = request.get("channel_name", "unknown")
        user_name = request.get("user_name", "unknown")

        print(f"[TTS] server: {guild_name} | channel: {channel_name} | "
              f"user: {user_name} | speaker: {speaker} | text: {text[:50]}")

        if not text.strip():
            return {"error": "Text is empty"}

        if len(text) > 500:
            text = text[:500]

        if speaker not in self.rvc_models:
            available = list(self.rvc_models.keys())
            return {"error": f"Speaker '{speaker}' not available. Available: {available}"}

        f0_override = request.get("f0_up_key", None)

        total_start = time.time()
        config = SPEAKER_CONFIG[speaker]
        tmp_files = []

        try:
            # Step 1: edge-tts로 음성 생성
            tts_start = time.time()
            tmp_mp3 = tempfile.mktemp(suffix=".mp3")
            tmp_tts_wav = tempfile.mktemp(suffix="_tts.wav")
            tmp_files.extend([tmp_mp3, tmp_tts_wav])

            communicate = Communicate(text=text, voice=EDGE_TTS_VOICE)
            await communicate.save(tmp_mp3)

            # MP3 -> WAV 48kHz mono
            subprocess.run([
                "ffmpeg", "-y", "-i", tmp_mp3,
                "-ar", "48000", "-ac", "1", "-f", "wav", tmp_tts_wav
            ], capture_output=True, check=True)

            # 짧은 오디오 패딩
            # RVC 내부에서 16kHz로 리샘플 후 반사 패딩 48000 적용
            # 16kHz 기준 최소 96001 샘플 필요 -> 48kHz에서 7초면 안전
            # 무음(zeros) 패딩 대신 오디오를 반복해서 F0 추출 품질 유지
            audio_data, sr = sf.read(tmp_tts_wav)
            original_len = len(audio_data)
            min_samples = sr * 7
            if len(audio_data) < min_samples:
                repeats = (min_samples // len(audio_data)) + 1
                audio_data = np.tile(audio_data, repeats)[:min_samples]
                sf.write(tmp_tts_wav, audio_data, sr)
                print(f"[PAD] {original_len} -> {len(audio_data)} samples (repeat x{repeats})")

            tts_time = time.time() - tts_start

            # Step 2: RVC로 음색 변환
            rvc_start = time.time()
            model = self.rvc_models[speaker]
            tmp_rvc_wav = tempfile.mktemp(suffix="_rvc.wav")
            tmp_files.append(tmp_rvc_wav)

            try:
                pitch = f0_override if f0_override is not None else config["f0_up_key"]
                result = model(
                    tmp_tts_wav,
                    f0_up_key=pitch,
                    index_rate=0.75,
                )
                if hasattr(result, 'cpu'):
                    result = result.cpu().numpy()
                result = np.asarray(result, dtype=np.float32)
                # 패딩으로 늘린 무음 부분 제거
                if original_len < min_samples:
                    keep_ratio = original_len / min_samples
                    keep_samples = int(len(result) * keep_ratio)
                    result = result[:keep_samples]
                sf.write(tmp_rvc_wav, result, 48000)
                rvc_time = time.time() - rvc_start
                output_file = tmp_rvc_wav
            except Exception as rvc_err:
                print(f"[WARN] RVC failed, falling back to edge-tts: {rvc_err}")
                rvc_time = time.time() - rvc_start
                output_file = tmp_tts_wav

            total_time = time.time() - total_start
            print(f"[TTS] Done: tts={tts_time:.2f}s rvc={rvc_time:.2f}s "
                  f"total={total_time:.2f}s")

            with open(output_file, "rb") as f:
                wav_bytes = f.read()

            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={
                    "X-TTS-Time": f"{tts_time:.3f}",
                    "X-RVC-Time": f"{rvc_time:.3f}",
                    "X-Total-Time": f"{total_time:.3f}",
                },
            )
        except Exception as e:
            import traceback
            print(f"[ERROR] {traceback.format_exc()}")
            return {"error": str(e)}
        finally:
            for f in tmp_files:
                if os.path.exists(f):
                    os.unlink(f)

    @modal.fastapi_endpoint(method="GET")
    def health(self):
        """GET /health - 상태 확인"""
        return {
            "status": "running",
            "version": "v4-pitch-param",
            "models_loaded": list(self.rvc_models.keys()),
            "edge_tts_voice": EDGE_TTS_VOICE,
            "errors": self.load_errors,
        }
