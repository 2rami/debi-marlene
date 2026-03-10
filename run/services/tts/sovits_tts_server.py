"""GPT-SoVITS v2Pro Modal Server - local code mount"""

import modal
from pydantic import BaseModel

LOCAL_SOVITS = r"C:\Users\2rami\Desktop\TTS\GPT-SoVITS-v2pro-20250604"

IGNORE_PATTERNS = [
    "/pretrained_models/", "/__pycache__/", "/TEMP/",
    "/SoVITS_weights", "/GPT_weights",
    "/tools/asr/models/", "/tools/uvr5/",
    "/.git/", "/data/", "/runtime/", "/logs/", "/filelists/", ".zip",
]


class TTSRequest(BaseModel):
    text: str
    text_language: str = "ko"

app = modal.App("sovits-tts-server")
volume = modal.Volume.from_name("sovits-models", create_if_missing=True)

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.1.0-runtime-ubuntu22.04", add_python="3.11"
    )
    .apt_install("ffmpeg", "libsndfile1", "libsox-dev", "cmake", "build-essential", "clang")
    .pip_install(
        "torch==2.5.1", "torchaudio==2.5.1",
        "numpy<2", "scipy", "librosa==0.10.2", "numba",
        "pytorch-lightning>=2.4",
        "onnxruntime-gpu",
        "transformers>=4.43,<=4.50", "peft<0.18.0",
        "sentencepiece", "soundfile", "matplotlib",
        "cn2an", "pypinyin", "g2pk2", "ko_pron", "jamo",
        "jieba", "jieba_fast", "split-lang", "fast_langdetect>=0.3.1", "wordsegment",
        "rotary_embedding_torch", "x_transformers",
        "opencc", "chardet", "PyYAML", "psutil",
        "torchmetrics<=1.5", "pydantic<=2.10.6",
        "einops", "vector_quantize_pytorch",
        "ToJyutping", "g2p_en", "av", "fastapi[standard]", "ffmpeg-python", "gradio",
        extra_index_url="https://download.pytorch.org/whl/cu121",
        gpu="A10G",
    )
    .run_commands(
        "mkdir -p /pretrained_models",
        "python -c \""
        "from huggingface_hub import snapshot_download; "
        "snapshot_download('lj1995/GPT-SoVITS', local_dir='/pretrained_models'); "
        "\"",
        "python -c \""
        "from fast_langdetect import detect; print(detect('hello world')); "
        "import nltk; "
        "nltk.download('averaged_perceptron_tagger_eng', quiet=True); "
        "nltk.download('cmudict', quiet=True); "
        "\"",
    )
    .add_local_dir(
        LOCAL_SOVITS,
        remote_path="/opt/sovits",
        ignore=lambda fp: any(x in ("/" + str(fp).replace("\\", "/") + "/") for x in IGNORE_PATTERNS),
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

        # Create directories first, then copy trained models from volume
        os.makedirs("SoVITS_weights_v2Pro", exist_ok=True)
        os.makedirs("GPT_weights_v2Pro", exist_ok=True)

        shutil.copy2("/models/debi_e8_s328.pth", "/opt/sovits/SoVITS_weights_v2Pro/debi_e8_s328.pth")
        shutil.copy2("/models/debi-e15.ckpt", "/opt/sovits/GPT_weights_v2Pro/debi-e15.ckpt")
        shutil.copy2("/models/ref_debi.wav", "/tmp/ref_debi.wav")
        shutil.copy2("/models/ref_aux1.wav", "/tmp/ref_aux1.wav")
        shutil.copy2("/models/ref_aux2.wav", "/tmp/ref_aux2.wav")

        # Symlink pretrained_models from image build to expected location
        pretrained_dst = "/opt/sovits/GPT_SoVITS/pretrained_models"
        if not os.path.exists(pretrained_dst):
            os.makedirs("/opt/sovits/GPT_SoVITS", exist_ok=True)
            os.symlink("/pretrained_models", pretrained_dst)

        # fast_langdetect needs this cache dir + warmup
        os.makedirs(f"{pretrained_dst}/fast_langdetect", exist_ok=True)
        from fast_langdetect import detect
        detect("warmup")

        import nltk
        nltk.download("averaged_perceptron_tagger_eng", quiet=True)
        nltk.download("cmudict", quiet=True)

        from TTS_infer_pack.TTS import TTS, TTS_Config

        tts_config = TTS_Config({"custom": {
            "device": "cuda",
            "is_half": True,
            "version": "v2Pro",
            "t2s_weights_path": "/opt/sovits/GPT_weights_v2Pro/debi-e15.ckpt",
            "vits_weights_path": "/opt/sovits/SoVITS_weights_v2Pro/debi_e8_s328.pth",
            "cnhuhbert_base_path": "/pretrained_models/chinese-hubert-base",
            "bert_base_path": "/pretrained_models/chinese-roberta-wwm-ext-large",
        }})
        self.tts = TTS(tts_config)

        # Explicitly load fine-tuned weights (config fallback uses pretrained)
        self.tts.init_vits_weights("/opt/sovits/SoVITS_weights_v2Pro/debi_e8_s328.pth")
        self.tts.init_t2s_weights("/opt/sovits/GPT_weights_v2Pro/debi-e15.ckpt")

        # Default reference audio (main + aux for tone fusion)
        self.ref_audio = "/tmp/ref_debi.wav"
        self.ref_text = ""
        self.ref_lang = "ko"
        self.aux_refs = ["/tmp/ref_aux1.wav", "/tmp/ref_aux2.wav"]

        print("TTS model loaded!")

    @modal.fastapi_endpoint(method="POST")
    def tts(self, request: TTSRequest):
        from io import BytesIO
        from fastapi.responses import Response
        import soundfile as sf
        import numpy as np

        text = request.text
        if not text:
            return Response(
                content=b'{"error":"no text"}',
                status_code=400,
                media_type="application/json",
            )

        text_lang = request.text_language

        inputs = {
            "text": text,
            "text_lang": text_lang,
            "ref_audio_path": self.ref_audio,
            "aux_ref_audio_paths": self.aux_refs,
            "prompt_text": self.ref_text,
            "prompt_lang": self.ref_lang,
            "top_k": 15,
            "top_p": 1.0,
            "temperature": 1.0,
            "text_split_method": "cut5",
            "batch_size": 1,
            "speed_factor": 1.0,
            "split_bucket": True,
            "parallel_infer": True,
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
        "ref_debi.wav": r"C:\Users\2rami\Desktop\TTS\GPT-SoVITS-v2pro-20250604\data\debi\Debi_taunt_1_01.wav",
        "ref_aux1.wav": r"C:\Users\2rami\Desktop\TTS\GPT-SoVITS-v2pro-20250604\data\debi\Debi_exitSuccess_3_01.wav",
        "ref_aux2.wav": r"C:\Users\2rami\Desktop\TTS\GPT-SoVITS-v2pro-20250604\data\debi\Debi_moveInFactory_3_01_01.wav",
    }
    with volume.batch_upload(force=True) as batch:
        for remote_name, local_path in local_files.items():
            if os.path.exists(local_path):
                print(f"Uploading {remote_name} ({os.path.getsize(local_path)/1e6:.1f}MB)")
                batch.put_file(local_path, f"/{remote_name}")
    print("Upload complete!")
