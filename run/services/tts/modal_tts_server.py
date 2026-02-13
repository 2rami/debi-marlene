"""
Modal Serverless TTS Server - Qwen3-TTS

GPU가 있는 Modal 서버리스 환경에서 실행되는 TTS API입니다.
사용할 때만 과금되므로 경제적입니다.

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

# Modal 앱 정의
app = modal.App("qwen3-tts-server")

# GPU 이미지 정의 - Flash Attention 포함 (pre-built wheel 사용)
# torch 2.10 + CUDA 12.8 + Python 3.11 호환 wheel
# https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/tag/v0.7.12
FLASH_ATTN_WHEEL = (
    "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.12/"
    "flash_attn-2.7.4%2Bcu128torch2.10-cp311-cp311-linux_x86_64.whl"
)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "sox", "libsox-dev")
    # qwen-tts 먼저 설치 (torch 2.10.0 포함)
    .pip_install("qwen-tts")
    # flash_attn은 qwen-tts가 설치한 torch 2.10에 맞는 버전으로 설치
    .pip_install(
        FLASH_ATTN_WHEEL,
        extra_options="--no-build-isolation",
    )
    .run_commands("python -c 'import flash_attn; print(f\"Flash Attention {flash_attn.__version__} installed\")'")
)

# 모델 캐시용 볼륨 (다운로드 시간 절약)
volume = modal.Volume.from_name("tts-model-cache", create_if_missing=True)

# HuggingFace 모델 ID
HUGGINGFACE_MODELS = {
    "debi": "2R4mi/qwen3-tts-debi-light",
    "marlene": "2R4mi/qwen3-tts-marlene",
}


@app.cls(
    image=image,
    gpu="A10G",  # A10G: 0.6B 모델 최적 가성비 ($0.000306/초, ~$1.10/h)
    timeout=300,
    volumes={"/cache": volume},
    scaledown_window=300,  # 5분간 요청 없으면 종료 (cold start 빈도 감소)
)
class TTSModel:
    """Qwen3-TTS 모델 클래스"""

    @modal.enter()
    def load_model(self):
        """컨테이너 시작시 모델 로드 (한 번만 실행)"""
        import torch
        from qwen_tts import Qwen3TTSModel
        from huggingface_hub import snapshot_download

        self.device = "cuda"
        # INT8 양자화를 위해 None으로 설정 (load_in_8bit와 함께 사용)
        self.dtype = None
        self.use_8bit = True  # 8bit 양자화 활성화

        # Flash Attention 사용 가능 여부 확인
        try:
            import flash_attn
            self.attn_impl = "flash_attention_2"
            print("Flash Attention 2 enabled")
        except ImportError:
            self.attn_impl = "eager"
            print("Using eager attention (flash_attn not available)")

        self.models = {}
        self.load_errors = []

        # HuggingFace에서 모델 다운로드 및 로드
        for speaker, hf_repo_id in HUGGINGFACE_MODELS.items():
            try:
                # 캐시 경로
                cache_path = f"/cache/{speaker}"

                # 캐시에 없으면 HuggingFace에서 다운로드
                if not os.path.exists(cache_path) or not os.listdir(cache_path):
                    print(f"Downloading {speaker} model from HuggingFace: {hf_repo_id}")
                    snapshot_download(
                        repo_id=hf_repo_id,
                        local_dir=cache_path,
                        token=os.environ.get("HF_TOKEN"),
                    )
                    volume.commit()  # 볼륨에 저장
                    print(f"Downloaded and cached: {cache_path}")

                # 캐시 내용 확인
                cache_files = os.listdir(cache_path) if os.path.exists(cache_path) else []
                print(f"Cache files for {speaker}: {cache_files}")

                print(f"Loading model for {speaker}: {cache_path}")

                # 순수 bfloat16 (양자화 없음)
                import torch
                model = Qwen3TTSModel.from_pretrained(
                    cache_path,
                    device_map=self.device,
                    dtype=torch.bfloat16,
                    attn_implementation=self.attn_impl,
                )

                self.models[speaker] = model
                print(f"Model loaded for {speaker} (bfloat16)")

            except Exception as e:
                import traceback
                error_msg = f"{speaker}: {str(e)}\n{traceback.format_exc()}"
                print(f"Failed to load model: {error_msg}")
                self.load_errors.append(error_msg)

        print(f"Loaded models: {list(self.models.keys())}")

    def _generate_internal(self, text: str, speaker: str = "debi") -> tuple:
        """음성 생성 (내부 메서드)"""
        import soundfile as sf

        if speaker not in self.models:
            raise ValueError(f"Speaker not found: {speaker}. Available: {list(self.models.keys())}")

        model = self.models[speaker]

        # 속도 최적화 파라미터
        # - max_new_tokens: 기본값 4096을 512로 제한 (짧은 문장에 충분)
        # - temperature: 0.6으로 낮춤 (더 결정적, 빠름)
        # - do_sample: False (greedy decoding, 샘플링보다 2배 빠름)
        wavs, sr = model.generate_custom_voice(
            text=text,
            speaker=speaker,
            max_new_tokens=512,
            temperature=0.6,
            do_sample=False,
        )

        # WAV 바이트로 변환
        buffer = io.BytesIO()
        sf.write(buffer, wavs[0], sr, format="WAV")
        buffer.seek(0)

        return buffer.read(), sr

    @modal.fastapi_endpoint(method="POST", docs=True)
    def tts(self, request: dict):
        """HTTP POST /tts 엔드포인트"""
        from fastapi.responses import Response

        text = request.get("text", "")
        speaker = request.get("speaker", "debi")

        # 메타데이터 (로깅용)
        guild_name = request.get("guild_name", "알수없음")
        channel_name = request.get("channel_name", "알수없음")
        user_name = request.get("user_name", "알수없음")

        # 요청 로깅
        print(f"[TTS 요청] 서버: {guild_name} | 채널: {channel_name} | 유저: {user_name} | 텍스트: {text[:50]}{'...' if len(text) > 50 else ''}")

        if not text.strip():
            return {"error": "Text is empty"}

        if len(text) > 500:
            text = text[:500]

        try:
            audio_bytes, sr = self._generate_internal(text, speaker)
            return Response(
                content=audio_bytes,
                media_type="audio/wav",
                headers={"X-Sample-Rate": str(sr)}
            )
        except Exception as e:
            return {"error": str(e)}

    @modal.fastapi_endpoint(method="GET")
    def health(self):
        """헬스 체크"""
        return {
            "status": "running",
            "models_loaded": list(self.models.keys()),
            "attention": self.attn_impl,
            "errors": self.load_errors if hasattr(self, 'load_errors') else [],
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


# 로컬 테스트용
if __name__ == "__main__":
    # modal serve modal_tts_server.py 로 실행
    pass
