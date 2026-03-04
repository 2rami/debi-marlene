"""GPT-SoVITS v2Pro Modal Server - official TTS class"""

import modal

app = modal.App("sovits-tts-server")
volume = modal.Volume.from_name("sovits-models", create_if_missing=True)

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.1.0-runtime-ubuntu22.04", add_python="3.11"
    )
    .apt_install("git", "ffmpeg", "libsndfile1", "libsox-dev", "cmake", "build-essential")
    .run_commands(
        "git clone --depth 1 https://github.com/RVC-Boss/GPT-SoVITS.git /opt/sovits",
    )
    .pip_install(
        "torch==2.5.1", "torchaudio==2.5.1",
        "numpy<2", "scipy", "librosa==0.10.2", "numba",
        "pytorch-lightning>=2.4",
        "onnxruntime-gpu",
        "transformers>=4.43,<=4.50", "peft<0.18.0",
        "sentencepiece", "soundfile", "matplotlib",
        "cn2an", "pypinyin", "g2pk2", "ko_pron", "jamo",
        "jieba", "split-lang", "fast_langdetect>=0.3.1", "wordsegment",
        "rotary_embedding_torch", "x_transformers",
        "opencc", "chardet", "PyYAML", "psutil",
        "torchmetrics<=1.5", "pydantic<=2.10.6",
        "einops", "vector_quantize_pytorch",
        "ToJyutping", "g2p_en", "av", "fastapi[standard]",
        extra_index_url="https://download.pytorch.org/whl/cu121",
        gpu="A10G",
    )
    .run_commands(
        "cd /opt/sovits && python -c \""
        "from huggingface_hub import snapshot_download; "
        "snapshot_download('lj1995/GPT-SoVITS', local_dir='GPT_SoVITS/pretrained_models'); "
        "\"",
    )
)


@app.cls(
    image=image,
    gpu="A10G",
    timeout=120,
    volumes={"/models": volume},
    scaledown_window=300,
    startup_timeout=600,
)
class SoVITSModel:
    @modal.enter()
    def load_model(self):
        import os, sys, shutil

        os.chdir("/opt/sovits")
        sys.path.insert(0, "/opt/sovits")
        sys.path.insert(0, "/opt/sovits/GPT_SoVITS")

        # Copy trained models from volume
        shutil.copy2("/models/debi_e8_s328.pth", "/opt/sovits/SoVITS_weights_v2Pro/debi_e8_s328.pth")
        shutil.copy2("/models/debi-e15.ckpt", "/opt/sovits/GPT_weights_v2Pro/debi-e15.ckpt")
        shutil.copy2("/models/ref_debi.wav", "/tmp/ref_debi.wav")

        os.makedirs("SoVITS_weights_v2Pro", exist_ok=True)
        os.makedirs("GPT_weights_v2Pro", exist_ok=True)

        # Use official TTS class
        from TTS_infer_pack.TTS import TTS, TTS_Config

        configs = TTS_Config.default_configs["v2Pro"].copy()
        configs["device"] = "cuda"
        configs["is_half"] = True
        configs["version"] = "v2Pro"
        configs["t2s_weights_path"] = "/opt/sovits/GPT_weights_v2Pro/debi-e15.ckpt"
        configs["vits_weights_path"] = "/opt/sovits/SoVITS_weights_v2Pro/debi_e8_s328.pth"
        configs["cnhuhbert_base_path"] = "/opt/sovits/GPT_SoVITS/pretrained_models/chinese-hubert-base"
        configs["bert_base_path"] = "/opt/sovits/GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large"

        tts_config = TTS_Config(configs)
        self.tts = TTS(tts_config)

        # Default reference audio
        self.ref_audio = "/tmp/ref_debi.wav"
        self.ref_text = "따라올 수 있지!"
        self.ref_lang = "ko"

        print("TTS model loaded!")

    @modal.fastapi_endpoint(method="POST")
    def tts(self, request: dict):
        from io import BytesIO
        from fastapi.responses import Response
        import soundfile as sf
        import numpy as np

        text = request.get("text", "")
        if not text:
            return Response(
                content=b'{"error":"no text"}',
                status_code=400,
                media_type="application/json",
            )

        text_lang = request.get("text_language", "ko")

        inputs = {
            "text": text,
            "text_lang": text_lang,
            "ref_audio_path": self.ref_audio,
            "prompt_text": self.ref_text,
            "prompt_lang": self.ref_lang,
            "top_k": 20,
            "top_p": 0.6,
            "temperature": 0.6,
            "text_split_method": "cut5",
            "batch_size": 1,
            "speed_factor": 1.0,
            "streaming_mode": False,
            "repetition_penalty": 1.35,
        }

        # tts.run() returns a generator of (sr, audio_numpy) tuples
        audio_chunks = []
        sr = 24000
        for sr_out, audio_np in self.tts.run(inputs):
            sr = sr_out
            audio_chunks.append(audio_np)

        if not audio_chunks:
            return Response(
                content=b'{"error":"no audio generated"}',
                status_code=500,
                media_type="application/json",
            )

        full_audio = np.concatenate(audio_chunks)
        buf = BytesIO()
        sf.write(buf, full_audio, sr, format="wav")
        buf.seek(0)

        return Response(content=buf.read(), media_type="audio/wav")

    @modal.fastapi_endpoint(method="GET")
    def health(self):
        return {"status": "running", "engine": "gpt-sovits-v2pro", "speaker": "debi"}


@app.local_entrypoint()
def upload_models():
    import os

    local_files = {
        "debi_e8_s328.pth": r"C:\Users\2rami\Desktop\TTS\GPT-SoVITS-v2pro-20250604\SoVITS_weights_v2Pro\debi_e8_s328.pth",
        "debi-e15.ckpt": r"C:\Users\2rami\Desktop\TTS\GPT-SoVITS-v2pro-20250604\GPT_weights_v2Pro\debi-e15.ckpt",
        "ref_debi.wav": r"C:\Users\2rami\Desktop\TTS\GPT-SoVITS-v2pro-20250604\data\debi\Debi_accelerationLine_1_01.wav",
    }
    with volume.batch_upload() as batch:
        for remote_name, local_path in local_files.items():
            if os.path.exists(local_path):
                print(f"Uploading {remote_name} ({os.path.getsize(local_path)/1e6:.1f}MB)")
                batch.put_file(local_path, f"/{remote_name}")
    print("Upload complete!")
