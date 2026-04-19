"""
대시보드 TTS 데모 음성 생성 스크립트

Usage:
    python scripts/generate_demo_voices.py

Output:
    dashboard/frontend/public/audio/demo_debi_*.wav
    dashboard/frontend/public/audio/demo_marlene_*.wav
"""

import io
import os
import sys
import time

COSYVOICE_DIR = r'C:\Users\2rami\Desktop\TTS\CosyVoice'
sys.path.insert(0, os.path.join(COSYVOICE_DIR, 'third_party', 'Matcha-TTS'))
sys.path.insert(0, COSYVOICE_DIR)

PRETRAINED = os.path.join(COSYVOICE_DIR, 'pretrained_models', 'Fun-CosyVoice3-0.5B')
# HF에서 파인튜닝된 llm.pt 다운로드 (epoch_26_whole.pt와 동일)
HF_REPO = "2R4mi/cosyvoice3-debi-marlene"
REF_DIR = os.path.join(os.path.dirname(__file__), '..', 'run', 'services', 'tts', 'references')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'frontend', 'public', 'audio')

DEMO_LINES = [
    ("debi", "desc", "데비와 마를렌의 목소리로 채팅을 읽어줍니다! AI 파인튜닝 모델 기반의 자연스러운 캐릭터 음성이야"),
    ("marlene", "desc", "데비와 마를렌의 목소리로 채팅을 읽어줍니다! AI 파인튜닝 모델 기반의 자연스러운 캐릭터 음성이야"),
]


def main():
    import torch
    import soundfile as sf
    from cosyvoice.cli.cosyvoice import CosyVoice3

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    from huggingface_hub import hf_hub_download

    print(f"Loading model from {PRETRAINED}")
    model = CosyVoice3(PRETRAINED, load_trt=False, fp16=True)

    print(f"Downloading finetuned llm.pt from {HF_REPO}")
    ckpt_path = hf_hub_download(HF_REPO, "llm.pt")
    print(f"Loading checkpoint from {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=True)
    ckpt.pop("epoch", None)
    ckpt.pop("step", None)
    model.model.llm.load_state_dict(ckpt, strict=True)
    model.model.llm.to(model.model.device).eval()
    del ckpt
    torch.cuda.empty_cache()

    # Warmup
    ref_wav = os.path.join(REF_DIR, 'debi_ref.wav')
    print("Warming up...")
    for _ in model.inference_instruct2("test", "You are a helpful assistant.<|endofprompt|>[calm]", ref_wav, stream=False):
        pass
    print("Warmup done\n")

    for speaker, tag, text in DEMO_LINES:
        ref_path = os.path.join(REF_DIR, f'{speaker}_ref.wav')
        instruction = "You are a helpful assistant.<|endofprompt|>[calm]"

        print(f"Generating: [{speaker}] {text}")
        t0 = time.time()

        output_wav = None
        for result in model.inference_instruct2(text, instruction, ref_path, stream=False):
            output_wav = result["tts_speech"]

        if output_wav is None:
            print(f"  FAILED!")
            continue

        audio = output_wav.numpy().flatten()
        duration = len(audio) / 24000
        elapsed = time.time() - t0
        print(f"  -> {duration:.1f}s audio, {elapsed:.1f}s inference")

        out_path = os.path.join(OUTPUT_DIR, f'demo_{speaker}_{tag}.wav')
        sf.write(out_path, audio, 24000)
        print(f"  -> Saved: {out_path}\n")

    print("Done! Generated files:")
    for f in os.listdir(OUTPUT_DIR):
        if f.startswith('demo_'):
            print(f"  {f}")


if __name__ == "__main__":
    main()
