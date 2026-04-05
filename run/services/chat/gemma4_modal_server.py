"""
Modal Serverless Chat Server - Gemma 4 E4B + LoRA

데비&마를렌 캐릭터 대화. 패치노트 RAG는 봇 cog에서 context로 전달.

배포:
    modal deploy run/services/chat/gemma4_modal_server.py

로컬 테스트:
    modal serve run/services/chat/gemma4_modal_server.py
"""

import os
import re
import time
import modal

app = modal.App("gemma4-chat-server")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.6.0",
        extra_index_url="https://download.pytorch.org/whl/cu124",
    )
    .pip_install(
        "unsloth",
        "unsloth_zoo",
        "peft",
        "accelerate",
        "bitsandbytes",
    )
    .pip_install(
        "fastapi[standard]",
    )
)

volume = modal.Volume.from_name("gemma4-chat-cache", create_if_missing=True)

ADAPTER_VOLUME_PATH = "/cache/adapter_gemma4"
BASE_MODEL = "unsloth/gemma-4-E4B-it"

SYSTEM_PROMPT = (
    "너는 이터널 리턴의 쌍둥이 실험체 데비&마를렌이야. 한국어로만 대답해. 이모지 사용하지 마.\n"
    "데비(언니): 활발, 천진난만, 장난기. 직설적이고 솔직한 10대 소녀 말투.\n"
    '마를렌(동생): 냉소적이지만 자연스러운 10대 소녀. 말이 짧고 차분함. "..."으로 시작하기도 함.\n'
    "형식: 데비: (대사) + 마를렌: (대사). 각자 1-2문장으로 짧게."
)

BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
EMOJI_RE = re.compile(
    "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF]+",
    flags=re.UNICODE,
)
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff]+")


@app.cls(
    image=image,
    gpu="A10G",
    timeout=300,
    volumes={"/cache": volume},
    scaledown_window=300,
    max_containers=1,
)
@modal.concurrent(max_inputs=3)
class Gemma4Chat:
    """Gemma 4 E4B + LoRA 추론"""

    @modal.enter()
    def load(self):
        import torch
        from unsloth import FastModel
        from unsloth.chat_templates import get_chat_template

        print(f"GPU: {torch.cuda.get_device_name(0)}")

        self.model, self.tokenizer = FastModel.from_pretrained(
            model_name=BASE_MODEL,
            max_seq_length=512,
            load_in_4bit=True,
            full_finetuning=False,
        )

        # adapter 로드 (volume에 있으면)
        if os.path.exists(ADAPTER_VOLUME_PATH):
            # ClippableLinear 교체 (PEFT 호환)
            from transformers.models.gemma4.modeling_gemma4 import Gemma4ClippableLinear
            for name, module in list(self.model.named_modules()):
                if isinstance(module, Gemma4ClippableLinear):
                    parts = name.split(".")
                    parent = self.model
                    for p in parts[:-1]:
                        parent = getattr(parent, p)
                    setattr(parent, parts[-1], module.linear)

            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, ADAPTER_VOLUME_PATH)
            print(f"LoRA adapter 적용: {ADAPTER_VOLUME_PATH}")

        self.model.eval()
        self.tokenizer = get_chat_template(self.tokenizer, chat_template="gemma-4")

        vram = torch.cuda.memory_allocated() / 1024**3
        print(f"로드 완료 (VRAM: {vram:.1f} GB)")

    def _clean(self, text: str) -> str:
        text = BOLD_RE.sub(r"\1", text)
        text = EMOJI_RE.sub("", text)
        text = CJK_RE.sub("", text)
        text = re.sub(r"(.{2,6})\1{2,}", r"\1", text)
        lines = [l.strip() for l in text.split("\n")
                 if l.strip() and l.strip() not in ("데비:", "마를렌:")]
        return "\n".join(lines)

    @modal.fastapi_endpoint(method="POST")
    async def chat(self, body: dict):
        import torch

        message = body.get("message", "")
        history = body.get("history", [])
        context = body.get("context")

        if not message:
            return {"error": "message required"}

        start = time.time()

        system = SYSTEM_PROMPT
        if context:
            system += f"\n\n[패치노트 정보 - 반드시 아래 수치를 인용해서 대답해]\n{context[:600]}"

        messages = [{"role": "system", "content": system}]
        if history:
            for h in history[-5:]:
                messages.append({"role": "user", "content": h["user"]})
                messages.append({"role": "assistant", "content": h["assistant"]})
        messages.append({"role": "user", "content": message})

        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text=[text], return_tensors="pt").to(self.model.device)

        max_tok = 120 if context else 80

        with torch.no_grad():
            output = self.model.generate(
                **inputs, max_new_tokens=max_tok,
                temperature=0.5, top_p=0.9, do_sample=True,
            )

        response = self.tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        response = self._clean(response)
        elapsed = time.time() - start

        return {"response": response, "elapsed": round(elapsed, 2)}

    @modal.method()
    def health(self):
        """health check (내부용, 엔드포인트 아님)"""
        import torch
        vram = torch.cuda.memory_allocated() / 1024**3
        return {
            "status": "running",
            "model": BASE_MODEL,
            "adapter": ADAPTER_VOLUME_PATH,
            "vram_gb": round(vram, 1),
        }


# ========== 오디오 이해 (Gemma 4 E4B omni + LoRA) ==========

audio_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "libsndfile1")
    .pip_install(
        "torch==2.6.0",
        "torchvision==0.21.0",
        extra_index_url="https://download.pytorch.org/whl/cu124",
    )
    .pip_install(
        "transformers>=4.52.0",
        "accelerate",
        "peft",
        "bitsandbytes",
    )
    .pip_install(
        "pillow",
        "soundfile",
        "librosa",
        "fastapi[standard]",
        "python-multipart",
    )
)

AUDIO_MODEL_ID = "google/gemma-4-E4B-it"


@app.cls(
    image=audio_image,
    gpu="A10G",
    timeout=300,
    volumes={"/cache": volume},
    scaledown_window=120,
    max_containers=1,
    secrets=[modal.Secret.from_name("huggingface")],
)
@modal.concurrent(max_inputs=2)
class Gemma4Audio:
    """Gemma 4 E4B omni - 오디오 이해 + LoRA 캐릭터 말투"""

    @modal.enter()
    def load(self):
        import torch
        from transformers import AutoProcessor, AutoModelForMultimodalLM

        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Loading {AUDIO_MODEL_ID}...")

        self.processor = AutoProcessor.from_pretrained(AUDIO_MODEL_ID)
        self.model = AutoModelForMultimodalLM.from_pretrained(
            AUDIO_MODEL_ID,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

        # LoRA 어댑터 적용 (캐릭터 말투)
        if os.path.exists(ADAPTER_VOLUME_PATH):
            try:
                from peft import PeftModel
                self.model = PeftModel.from_pretrained(self.model, ADAPTER_VOLUME_PATH)
                print(f"LoRA adapter 적용: {ADAPTER_VOLUME_PATH}")
            except Exception as e:
                print(f"LoRA 적용 실패 (기본 모델로 진행): {e}")

        self.model.eval()

        vram = torch.cuda.memory_allocated() / 1024**3
        print(f"오디오 모델 로드 완료 (VRAM: {vram:.1f} GB)")

    @modal.fastapi_endpoint(method="POST")
    async def audio_chat(self, body: dict):
        """오디오 + 텍스트 -> 캐릭터 응답

        body: {"audio_base64": "...", "message": "..."}
        """
        import torch
        import base64
        import tempfile
        import soundfile as sf

        audio_b64 = body.get("audio_base64", "")
        message = body.get("message", "이 사람이 한국어로 뭐라고 했는지 듣고 대답해줘.")
        use_character = body.get("character", True)  # False면 시스템 프롬프트 없이

        if not audio_b64:
            return {"error": "audio_base64 required"}

        start = time.time()

        audio_bytes = base64.b64decode(audio_b64)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.write(audio_bytes)
        tmp.flush()
        audio_path = tmp.name

        import librosa
        import numpy as np

        audio_data, sr = librosa.load(audio_path, sr=16000, mono=True)
        duration = len(audio_data) / sr
        print(f"오디오: {duration:.1f}초, {sr}Hz, samples: {len(audio_data)}")

        os.unlink(audio_path)

        if duration > 30:
            return {"error": "오디오 최대 30초"}

        messages = []
        if use_character:
            messages.append({"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]})
        messages.append({
            "role": "user",
            "content": [
                {"type": "audio", "audio": audio_data},
                {"type": "text", "text": message},
            ],
        })

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            sampling_rate=16000,
        )
        # 디버그: 오디오 토큰이 포함됐는지 확인
        has_features = "input_features" in inputs
        n_tokens = inputs["input_ids"].shape[1] if "input_ids" in inputs else 0
        print(f"input_features: {has_features}, tokens: {n_tokens}, keys: {list(inputs.keys())}")
        inputs = inputs.to(self.model.device, dtype=self.model.dtype)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=120,
                temperature=0.5,
                top_p=0.9,
                do_sample=True,
            )

        response = self.processor.batch_decode(
            output[:, inputs["input_ids"].shape[1]:],
            skip_special_tokens=True,
        )[0]

        elapsed = time.time() - start

        return {
            "response": response,
            "audio_duration": round(duration, 1),
            "elapsed": round(elapsed, 2),
        }

@app.local_entrypoint()
def upload_adapter():
    """로컬 adapter를 Modal Volume에 업로드"""
    import pathlib

    local_adapter = pathlib.Path("finetune/adapter_gemma4")
    if not local_adapter.exists():
        print(f"adapter 없음: {local_adapter}")
        return

    vol = modal.Volume.from_name("gemma4-chat-cache", create_if_missing=True)

    files = [f for f in local_adapter.iterdir() if not f.name.startswith(".")]
    print(f"업로드할 파일: {len(files)}개")

    with vol.batch_upload() as batch:
        for f in files:
            remote_path = f"/adapter_gemma4/{f.name}"
            print(f"  {f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)")
            batch.put_file(str(f), remote_path)

    print("업로드 완료!")
