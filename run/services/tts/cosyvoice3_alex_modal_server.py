"""
Modal Serverless TTS Server - CosyVoice3 (Alex Fine-tuned)

CosyVoice3 파인튜닝 모델로 alex TTS를 제공합니다.
LLM만 파인튜닝, Flow/HiFiGAN은 프리트레인 유지.

배포:
    modal deploy cosyvoice3_alex_modal_server.py

로컬 테스트:
    modal serve cosyvoice3_alex_modal_server.py
"""

import io
import os
import modal

app = modal.App("cosyvoice3-alex-tts-server")

hf_secret = modal.Secret.from_name("huggingface")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "git", "ffmpeg", "sox", "libsox-dev",
        "build-essential", "cmake",
    )
    .pip_install(
        "torch==2.5.1", "torchaudio==2.5.1",
        extra_index_url="https://download.pytorch.org/whl/cu121",
    )
    .run_commands(
        # Colab 노트북 cell-7과 동일한 설치 순서
        "pip install setuptools wget",
        # ML 핵심
        "pip install onnxruntime-gpu conformer hyperpyyaml 'protobuf>=5.26,<6'",
        # 학습 프레임워크
        "pip install lightning accelerate diffusers hydra-core 'transformers==4.51.3'",
        # 오디오 + 유틸
        "pip install soundfile librosa inflect pyarrow pydantic tiktoken more-itertools huggingface_hub pyworld",
        # whisper (no-deps로 의존성 충돌 방지)
        "pip install --upgrade numba",
        "pip install openai-whisper --no-deps",
        # 추론용 + matplotlib (Matcha-TTS utils에서 필요)
        "pip install modelscope x_transformers einops gdown matplotlib",
        # CosyVoice clone + Matcha-TTS (build_ext --inplace)
        "cd /opt && git clone --depth 1 https://github.com/FunAudioLLM/CosyVoice.git",
        "cd /opt/CosyVoice && git submodule update --init --recursive",
        "cd /opt/CosyVoice/third_party/Matcha-TTS && pip install cython && python setup.py build_ext --inplace",
        "pip install numpy==1.26.4",
        "pip install 'fastapi[standard]'",
        # vLLM 제거: transformers 4.51.3과 호환 안 됨
        "pip uninstall -y vllm || true",
        # transformers 재고정 (vLLM이 올렸을 수 있음)
        "pip install 'transformers==4.51.3'",
    )
    .env({
        "PYTHONPATH": "/opt/CosyVoice/third_party/Matcha-TTS:/opt/CosyVoice",
    })
)

volume = modal.Volume.from_name("cosyvoice3-alex-model-cache", create_if_missing=True)

HF_MODEL_REPO = "2R4mi/cosyvoice3-eternal-return"
SPEAKERS = ["alex"]


@app.cls(
    image=image,
    gpu="A10G",
    timeout=300,
    volumes={"/cache": volume},
    secrets=[hf_secret],
    scaledown_window=120,
    max_containers=1,
    allow_concurrent_inputs=5,
)
class CosyVoice3Model:
    """CosyVoice3 파인튜닝 모델 (Alex LLM SFT)"""

    @modal.enter()
    def load_model(self):
        """컨테이너 시작시 모델 로드"""
        import sys
        import logging
        logging.basicConfig(level=logging.WARNING)
        for name in ["transformers", "vllm", "torch", "lightning", "diffusers",
                      "modelscope", "huggingface_hub", "urllib3", "matplotlib",
                      "numba", "httpx", "filelock"]:
            logging.getLogger(name).setLevel(logging.WARNING)

        sys.path.insert(0, "/opt/CosyVoice")

        from huggingface_hub import snapshot_download

        self.model = None
        self.load_errors = []

        try:
            model_path = "/cache/cosyvoice3-alex-model"

            # 모델 다운로드 (캐시 없으면)
            if not os.path.exists(model_path) or not os.listdir(model_path):
                print(f"Downloading model: {HF_MODEL_REPO}")
                snapshot_download(
                    repo_id=HF_MODEL_REPO,
                    local_dir=model_path,
                    token=os.environ.get("HF_TOKEN"),
                )
                volume.commit()
                print("Model downloaded")

            # llm.pt에서 학습 메타데이터 키 제거 (epoch, step)
            import torch
            llm_path = f"{model_path}/llm.pt"
            if os.path.exists(llm_path):
                ckpt = torch.load(llm_path, map_location="cpu", weights_only=True)
                removed = [k for k in ["epoch", "step"] if k in ckpt]
                if removed:
                    for k in removed:
                        del ckpt[k]
                    torch.save(ckpt, llm_path)
                    print(f"Removed training keys from llm.pt: {removed}")
                del ckpt

            # CosyVoice3 모델 로드
            print(f"Loading CosyVoice3 from {model_path}")
            from cosyvoice.cli.cosyvoice import CosyVoice3
            self.model = CosyVoice3(model_path, load_vllm=False, load_trt=False, fp16=True)

            # 워밍업 추론
            print("Warming up...")
            ref_wav = self._get_reference_wav("alex")
            if ref_wav:
                for _ in self.model.inference_instruct2(
                    "워밍업 테스트",
                    "You are a helpful assistant.<|endofprompt|>",
                    ref_wav,
                    stream=False,
                ):
                    pass
                print("Warmup done")
            else:
                print("No reference wav for warmup - skipping")

            print("CosyVoice3 model ready")

        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"Failed to load model: {error_msg}")
            self.load_errors.append(error_msg)

    def _get_reference_wav(self, speaker: str) -> str:
        """스피커별 레퍼런스 wav 경로 반환"""
        ref_path = f"/cache/references/{speaker}.wav"
        if os.path.exists(ref_path):
            return ref_path

        # 레퍼런스가 없으면 모델 디렉토리에서 찾기
        model_ref = f"/cache/cosyvoice3-alex-model/references/{speaker}.wav"
        if os.path.exists(model_ref):
            return model_ref

        return None

    def _generate_full(self, text: str, speaker: str = "alex", style: str = "[calm]") -> tuple:
        """전체 음성 생성 -> 24kHz mono WAV (작은 크기로 빠른 전송)"""
        import torch
        import soundfile as sf
        import numpy as np

        if self.model is None:
            raise RuntimeError("Model not loaded")

        ref_wav = self._get_reference_wav(speaker)
        if ref_wav is None:
            raise ValueError(f"Reference wav not found for: {speaker}")

        instruction = f"You are a helpful assistant.<|endofprompt|>{style}"

        output_wav = None
        for result in self.model.inference_instruct2(
            text,
            instruction,
            ref_wav,
            stream=False,
        ):
            output_wav = result["tts_speech"]

        if output_wav is None:
            raise RuntimeError("TTS generation failed - no output")

        audio = output_wav.numpy().flatten()
        sr = 24000

        buffer = io.BytesIO()
        sf.write(buffer, audio, sr, format="WAV")
        buffer.seek(0)

        return buffer.read(), sr

    def _generate_streaming(self, text: str, speaker: str = "alex", style: str = "[calm]"):
        """스트리밍 음성 생성 (청크 단위 yield)"""
        import numpy as np

        if self.model is None:
            raise RuntimeError("Model not loaded")

        ref_wav = self._get_reference_wav(speaker)
        if ref_wav is None:
            raise ValueError(f"Reference wav not found for: {speaker}")

        instruction = f"You are a helpful assistant.<|endofprompt|>{style}"

        for result in self.model.inference_instruct2(
            text,
            instruction,
            ref_wav,
            stream=True,
        ):
            audio_chunk = result["tts_speech"].numpy().flatten()
            sr = 24000
            yield audio_chunk, sr

    @modal.fastapi_endpoint(method="POST", docs=True)
    def tts(self, request: dict):
        """HTTP POST /tts - 전체 음성 반환"""
        from fastapi.responses import Response

        text = request.get("text", "")
        speaker = request.get("speaker", "alex")
        style = request.get("style", "[calm]")

        guild_name = request.get("guild_name", "unknown")
        channel_name = request.get("channel_name", "unknown")
        user_name = request.get("user_name", "unknown")

        print(f"[TTS] {guild_name} | {channel_name} | {user_name} | {speaker} | {text[:50]}{'...' if len(text) > 50 else ''}")

        if not text.strip():
            return {"error": "Text is empty"}

        if len(text) > 500:
            text = text[:500]

        try:
            audio_bytes, sr = self._generate_full(text, speaker, style)
            return Response(
                content=audio_bytes,
                media_type="audio/wav",
                headers={"X-Sample-Rate": str(sr)},
            )
        except Exception as e:
            import traceback
            return {"error": str(e), "traceback": traceback.format_exc()}

    @modal.fastapi_endpoint(method="POST", docs=True)
    def tts_stream(self, request: dict):
        """HTTP POST /tts_stream - 스트리밍 (청크 단위)"""
        import soundfile as sf
        from fastapi.responses import StreamingResponse

        text = request.get("text", "")
        speaker = request.get("speaker", "alex")
        style = request.get("style", "[calm]")

        guild_name = request.get("guild_name", "unknown")
        channel_name = request.get("channel_name", "unknown")
        user_name = request.get("user_name", "unknown")

        print(f"[TTS Stream] {guild_name} | {channel_name} | {user_name} | {speaker} | {text[:50]}{'...' if len(text) > 50 else ''}")

        if not text.strip():
            return {"error": "Text is empty"}

        if len(text) > 500:
            text = text[:500]

        def stream_chunks():
            try:
                for audio_chunk, sr in self._generate_streaming(text, speaker, style):
                    chunk_buffer = io.BytesIO()
                    sf.write(chunk_buffer, audio_chunk, sr, format="WAV")
                    chunk_bytes = chunk_buffer.getvalue()

                    # 헤더: 청크 크기(4바이트) + 샘플레이트(4바이트) + WAV 데이터
                    header = len(chunk_bytes).to_bytes(4, "big") + sr.to_bytes(4, "big")
                    yield header + chunk_bytes
            except Exception as e:
                print(f"[TTS Stream Error] {e}")

        return StreamingResponse(
            stream_chunks(),
            media_type="application/octet-stream",
            headers={"X-Stream-Format": "chunked-wav"},
        )

    @modal.fastapi_endpoint(method="GET")
    def health(self):
        """헬스 체크"""
        import transformers
        import torch
        attn_impl = None
        if self.model is not None:
            try:
                attn_impl = str(self.model.model.llm.model.config._attn_implementation)
            except Exception:
                attn_impl = "unknown"
        return {
            "status": "running" if self.model is not None else "error",
            "engine": "CosyVoice3 (Alex Fine-tuned LLM SFT)",
            "speakers": SPEAKERS,
            "errors": self.load_errors if hasattr(self, "load_errors") else [],
            "transformers_version": transformers.__version__,
            "torch_version": torch.__version__,
            "attn_implementation": attn_impl,
        }


@app.function(image=image, volumes={"/cache": volume})
def upload_reference(local_path: str, speaker: str):
    """
    레퍼런스 wav를 Modal Volume에 업로드

    사용법:
        modal run cosyvoice3_alex_modal_server.py::upload_reference --local-path ./alex_ref.wav --speaker alex
    """
    import shutil

    ref_dir = "/cache/references"
    os.makedirs(ref_dir, exist_ok=True)

    dst = f"{ref_dir}/{speaker}.wav"
    shutil.copy2(local_path, dst)
    print(f"Uploaded {local_path} -> {dst}")

    volume.commit()
    print("Volume committed")


if __name__ == "__main__":
    pass
