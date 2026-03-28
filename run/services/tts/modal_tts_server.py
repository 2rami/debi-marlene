"""
Modal Serverless TTS Server - Qwen3-TTS (faster-qwen3-tts)

faster-qwen3-tts로 CUDA Graphs + Static KV Cache 최적화.
기존 대비 5-7x 속도 향상, 스트리밍 지원.

배포:
    modal deploy modal_tts_server.py

로컬 테스트:
    modal serve modal_tts_server.py

환경 변수:
    HF_TOKEN: HuggingFace 토큰 (private repo 사용시)
"""

import io
import os
import modal

app = modal.App("qwen3-tts-server")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "sox", "libsox-dev")
    .pip_install("faster-qwen3-tts")
)

# 모델 캐시용 볼륨 (다운로드 시간 절약)
volume = modal.Volume.from_name("tts-model-cache", create_if_missing=True)

# HuggingFace 모델 ID
HUGGINGFACE_MODELS = {
    "debi": os.environ.get("MODAL_DEBI_MODEL", "2R4mi/qwen3-tts-debi-light"),
    "marlene": os.environ.get("MODAL_MARLENE_MODEL", "2R4mi/qwen3-tts-marlene"),
}


@app.cls(
    image=image,
    gpu="A10G",
    timeout=300,
    volumes={"/cache": volume},
    scaledown_window=300,
)
class TTSModel:
    """Qwen3-TTS 모델 (faster-qwen3-tts CUDA Graphs 최적화)"""

    @modal.enter()
    def load_model(self):
        """컨테이너 시작시 모델 로드 + CUDA Graph 워밍업"""
        import torch
        from faster_qwen3_tts import FasterQwen3TTS
        from huggingface_hub import snapshot_download

        torch.set_float32_matmul_precision("high")

        self.models = {}
        self.load_errors = []

        for speaker, hf_repo_id in HUGGINGFACE_MODELS.items():
            try:
                cache_path = f"/cache/{speaker}"

                if not os.path.exists(cache_path) or not os.listdir(cache_path):
                    print(f"Downloading {speaker}: {hf_repo_id}")
                    snapshot_download(
                        repo_id=hf_repo_id,
                        local_dir=cache_path,
                        token=os.environ.get("HF_TOKEN"),
                    )
                    volume.commit()

                print(f"Loading {speaker}: {cache_path}")

                model = FasterQwen3TTS.from_pretrained(
                    cache_path,
                    device="cuda",
                    dtype=torch.bfloat16,
                )

                # CUDA Graph 캡처를 위한 워밍업 추론
                # 첫 2-3번 추론이 느리고 (그래프 캡처), 이후부터 5-7x 빨라짐
                print(f"Warming up {speaker} (CUDA graph capture)...")
                for i in range(3):
                    wavs, sr = model.generate_custom_voice(
                        text="워밍업 테스트입니다",
                        speaker=speaker,
                        language="Korean",
                        max_new_tokens=64,
                        do_sample=False,
                    )
                    print(f"  warmup {i + 1}/3 done")

                self.models[speaker] = model
                print(f"Model ready: {speaker}")

            except Exception as e:
                import traceback
                error_msg = f"{speaker}: {str(e)}\n{traceback.format_exc()}"
                print(f"Failed to load: {error_msg}")
                self.load_errors.append(error_msg)

        print(f"Loaded models: {list(self.models.keys())}")

    def _generate_full(self, text: str, speaker: str = "debi") -> tuple:
        """전체 음성 생성 (non-streaming)"""
        import soundfile as sf

        if speaker not in self.models:
            raise ValueError(f"Speaker not found: {speaker}. Available: {list(self.models.keys())}")

        model = self.models[speaker]

        wavs, sr = model.generate_custom_voice(
            text=text,
            speaker=speaker,
            language="Korean",
            max_new_tokens=512,
            do_sample=False,
        )

        buffer = io.BytesIO()
        sf.write(buffer, wavs[0], sr, format="WAV")
        buffer.seek(0)

        return buffer.read(), sr

    def _generate_streaming(self, text: str, speaker: str = "debi", chunk_size: int = 8):
        """스트리밍 음성 생성 (chunk 단위 yield)"""
        if speaker not in self.models:
            raise ValueError(f"Speaker not found: {speaker}. Available: {list(self.models.keys())}")

        model = self.models[speaker]

        for audio_chunk, sr, timing in model.generate_custom_voice_streaming(
            text=text,
            speaker=speaker,
            language="Korean",
            max_new_tokens=512,
            do_sample=False,
            chunk_size=chunk_size,
        ):
            yield audio_chunk, sr, timing

    @modal.fastapi_endpoint(method="POST", docs=True)
    def tts(self, request: dict):
        """HTTP POST /tts - 전체 음성 반환 (기존 호환)"""
        from fastapi.responses import Response

        text = request.get("text", "")
        speaker = request.get("speaker", "debi")

        guild_name = request.get("guild_name", "알수없음")
        channel_name = request.get("channel_name", "알수없음")
        user_name = request.get("user_name", "알수없음")

        print(f"[TTS] {guild_name} | {channel_name} | {user_name} | {text[:50]}{'...' if len(text) > 50 else ''}")

        if not text.strip():
            return {"error": "Text is empty"}

        if len(text) > 500:
            text = text[:500]

        try:
            audio_bytes, sr = self._generate_full(text, speaker)
            return Response(
                content=audio_bytes,
                media_type="audio/wav",
                headers={"X-Sample-Rate": str(sr)},
            )
        except Exception as e:
            return {"error": str(e)}

    @modal.fastapi_endpoint(method="POST", docs=True)
    def tts_stream(self, request: dict):
        """HTTP POST /tts_stream - 스트리밍 (청크 단위 전송)"""
        import json
        import numpy as np
        from fastapi.responses import StreamingResponse

        text = request.get("text", "")
        speaker = request.get("speaker", "debi")
        chunk_size = request.get("chunk_size", 8)

        guild_name = request.get("guild_name", "알수없음")
        channel_name = request.get("channel_name", "알수없음")
        user_name = request.get("user_name", "알수없음")

        print(f"[TTS Stream] {guild_name} | {channel_name} | {user_name} | {text[:50]}{'...' if len(text) > 50 else ''}")

        if not text.strip():
            return {"error": "Text is empty"}

        if len(text) > 500:
            text = text[:500]

        def stream_chunks():
            """청크를 생성하며 바로 전송"""
            import soundfile as sf

            try:
                for audio_chunk, sr, timing in self._generate_streaming(text, speaker, chunk_size):
                    # 각 청크를 WAV 바이트로 변환
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
        return {
            "status": "running",
            "models_loaded": list(self.models.keys()),
            "engine": "faster-qwen3-tts (CUDA Graphs)",
            "errors": self.load_errors if hasattr(self, "load_errors") else [],
        }


@app.function(image=image, volumes={"/cache": volume})
def upload_model(local_path: str, speaker: str):
    """
    로컬 모델을 Modal Volume에 업로드

    사용법:
        modal run modal_tts_server.py::upload_model --local-path ./checkpoint-epoch-9 --speaker debi
    """
    import shutil

    remote_path = f"/cache/checkpoint-{speaker}"

    if os.path.exists(remote_path):
        shutil.rmtree(remote_path)

    shutil.copytree(local_path, remote_path)
    print(f"Uploaded {local_path} -> {remote_path}")

    volume.commit()
    print("Volume committed")


if __name__ == "__main__":
    pass
