"""
Modal Serverless Chat Server - Gemma 4 E4B + LoRA

데비&마를렌 캐릭터 대화 + 패치노트 RAG.

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

# adapter는 HuggingFace private repo 또는 Drive에서 가져옴
# 여기서는 Volume에 미리 업로드하는 방식
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
        "aiohttp",
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

PATCH_KEYWORDS = ["패치", "너프", "버프", "변경", "수정", "밸런스", "상향", "하향", "바뀌"]
CHARACTER_ALIASES = {
    "에이든": "에이든", "뎁마": "데비&마를렌", "데비": "데비&마를렌",
    "마를렌": "데비&마를렌", "알렉스": "알렉스", "현우": "현우",
    "피오라": "피오라", "에키온": "에키온", "바바라": "바바라",
    "쇼이치": "쇼이치", "이삭": "이삭", "프리야": "프리야",
    "코랄린": "코랄린", "클로이": "클로이", "카밀로": "카밀로",
    "츠바메": "츠바메", "가넷": "가넷", "실비아": "실비아",
}

PATCHNOTE_LIST_URL = "https://playeternalreturn.com/posts/news?categoryPath=patchnote"
PATCHNOTE_BASE_URL = "https://playeternalreturn.com/posts/news"


@app.cls(
    image=image,
    gpu="A10G",
    timeout=300,
    volumes={"/cache": volume},
    scaledown_window=300,
    max_containers=1,
    allow_concurrent_inputs=3,
)
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

        self._patchnote_cache = {}
        self._patchnote_list = []

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

    async def _search_patchnote(self, message: str):
        import aiohttp

        if not any(k in message for k in PATCH_KEYWORDS):
            return None

        keyword = None
        for alias, name in CHARACTER_ALIASES.items():
            if alias in message:
                keyword = name
                break
        if not keyword:
            keyword = "패치"

        try:
            async with aiohttp.ClientSession() as session:
                # 목록
                async with session.get(PATCHNOTE_LIST_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return None
                    html = await resp.text()
                    pat = re.compile(r'href="[^"]*?/posts/news/(\d+)"[^>]*>.*?er-article__title">([^<]+)</h4>', re.DOTALL)
                    posts = [{"id": m.group(1), "title": m.group(2).strip()} for m in pat.finditer(html)][:3]
                    if not posts:
                        return None

                # 본문
                async with session.get(f"{PATCHNOTE_BASE_URL}/{posts[0]['id']}", headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return None
                    html = await resp.text()
                    body = re.search(r'class="er-post__body">(.*?)</div>\s*</(?:div|main|article)', html, re.DOTALL)
                    text = re.sub(r"<[^>]+>", "\n", body.group(1) if body else html)
                    text = re.sub(r"&\w+;", " ", text)
                    content = "\n".join(l.strip() for l in text.split("\n") if l.strip())
        except Exception:
            return None

        lines = content.split("\n")
        results = []
        kw = keyword.lower()
        for i, line in enumerate(lines):
            if kw in line.lower():
                s, e = max(0, i - 2), min(len(lines), i + 6)
                results.append("\n".join(lines[s:e]))

        if results:
            return f"[{posts[0]['title']}] {keyword} 관련:\n" + "\n---\n".join(results[:3])
        return f"[{posts[0]['title']}] {keyword}: 이번 패치에 변경사항 없음."

    @modal.fastapi_endpoint(method="POST")
    async def chat(self, body: dict):
        import torch

        message = body.get("message", "")
        history = body.get("history", [])
        context = body.get("context")

        if not message:
            return {"error": "message required"}

        start = time.time()

        # RAG
        if not context:
            context = await self._search_patchnote(message)

        system = SYSTEM_PROMPT
        if context:
            system += f"\n\n[게임 정보]\n{context[:400]}\n위 정보를 바탕으로 대답해. 모르면 모른다고 해."

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

    @modal.fastapi_endpoint(method="GET")
    async def health(self):
        import torch
        vram = torch.cuda.memory_allocated() / 1024**3
        return {
            "status": "running",
            "model": BASE_MODEL,
            "adapter": ADAPTER_VOLUME_PATH,
            "vram_gb": round(vram, 1),
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
