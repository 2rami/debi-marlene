"""
CosyVoice3 Local API Server

로컬 GPU에서 CosyVoice3를 실행하고 FastAPI로 서빙.
ngrok으로 공개 URL을 만들어 VM 봇이 접근 가능하게 함.

실행:
    python cosyvoice3_local_server.py
"""

import io
import os
import sys
import time

COSYVOICE_DIR = r'C:\Users\2rami\Desktop\TTS\CosyVoice'
sys.path.insert(0, os.path.join(COSYVOICE_DIR, 'third_party', 'Matcha-TTS'))
sys.path.insert(0, COSYVOICE_DIR)

PRETRAINED = os.path.join(COSYVOICE_DIR, 'pretrained_models', 'Fun-CosyVoice3-0.5B')
CHECKPOINT = r'C:\Users\2rami\Desktop\KASA\debi-marlene-cosyvoice\tts_training\epoch_26_whole.pt'
REF_DIR = os.path.join(os.path.dirname(__file__), 'references')

PORT = 8200


def create_app():
    import torch
    import soundfile as sf
    import numpy as np
    from fastapi import FastAPI
    from fastapi.responses import Response
    from pydantic import BaseModel
    from typing import Optional
    from cosyvoice.cli.cosyvoice import CosyVoice3

    app = FastAPI()

    # 모델 로드
    print(f"Loading CosyVoice3 from {PRETRAINED}")
    model = CosyVoice3(PRETRAINED, load_trt=False, fp16=True)

    # 파인튜닝 체크포인트 로드
    ckpt_path = os.path.abspath(CHECKPOINT)
    if os.path.exists(ckpt_path):
        print(f"Loading finetuned LLM from {ckpt_path}")
        ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=True)
        ckpt.pop("epoch", None)
        ckpt.pop("step", None)
        model.model.llm.load_state_dict(ckpt, strict=True)
        model.model.llm.to(model.model.device).eval()
        del ckpt
        torch.cuda.empty_cache()
        print("Finetuned LLM loaded")
    else:
        print(f"WARNING: Checkpoint not found: {ckpt_path}")

    # 워밍업
    ref_wav = os.path.join(REF_DIR, 'debi_ref.wav')
    if os.path.exists(ref_wav):
        print("Warming up...")
        for _ in model.inference_instruct2("test", "You are a helpful assistant.<|endofprompt|>[calm]", ref_wav, stream=False):
            pass
        print("Warmup done")

    class TTSRequest(BaseModel):
        text: str
        speaker: str = "debi"
        style: str = "[calm]"
        guild_name: Optional[str] = None
        channel_name: Optional[str] = None
        user_name: Optional[str] = None

    def get_ref_wav(speaker: str) -> str:
        for name in [f"{speaker}_ref.wav", f"{speaker}.wav"]:
            path = os.path.join(REF_DIR, name)
            if os.path.exists(path):
                return path
        return None

    @app.post("/tts")
    def tts(req: TTSRequest):
        print(f"[TTS] {req.speaker} | {req.text[:50]}")

        if not req.text.strip():
            return {"error": "Text is empty"}

        text = req.text[:500]
        ref_wav = get_ref_wav(req.speaker)
        if ref_wav is None:
            return {"error": f"Reference wav not found for: {req.speaker}"}

        instruction = f"You are a helpful assistant.<|endofprompt|>{req.style}"

        t0 = time.time()
        output_wav = None
        for result in model.inference_instruct2(text, instruction, ref_wav, stream=False):
            output_wav = result["tts_speech"]

        if output_wav is None:
            return {"error": "TTS generation failed"}

        elapsed = time.time() - t0
        audio = output_wav.numpy().flatten()
        duration = len(audio) / 24000
        print(f"  -> {duration:.1f}s audio, {elapsed:.1f}s inference")

        buffer = io.BytesIO()
        sf.write(buffer, audio, 24000, format="WAV")
        buffer.seek(0)

        return Response(content=buffer.read(), media_type="audio/wav", headers={"X-Sample-Rate": "24000"})

    @app.get("/health")
    def health():
        return {"status": "running", "engine": "CosyVoice3 Local", "speakers": ["debi", "marlene"]}

    return app


if __name__ == "__main__":
    import uvicorn
    import threading
    import subprocess
    import re

    app = create_app()

    # cloudflared 터널 (계정 불필요)
    def start_tunnel():
        proc = subprocess.Popen(
            [r"C:\Users\2rami\AppData\Local\cloudflared\cloudflared.exe", "tunnel", "--url", f"http://localhost:{PORT}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace'
        )
        for line in proc.stdout:
            match = re.search(r'(https://[a-z0-9-]+\.trycloudflare\.com)', line)
            if match:
                url = match.group(1)
                print(f"\n{'='*60}")
                print(f"Local:  http://localhost:{PORT}")
                print(f"Public: {url}")
                print(f"\nVM .env에 설정:")
                print(f"  COSYVOICE3_API_URL={url}/tts")
                print(f"  COSYVOICE3_HEALTH_URL={url}/health")
                print(f"{'='*60}\n")

    threading.Thread(target=start_tunnel, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=PORT)
