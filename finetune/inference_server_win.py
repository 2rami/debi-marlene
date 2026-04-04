"""
데비&마를렌 추론 서버 (Windows / NVIDIA GPU)

Qwen3.5-9B + LoRA adapter, 4-bit 양자화.
키워드 감지 -> 패치노트 검색 -> context 주입 방식 RAG.

사용법: cd finetune && python inference_server_win.py

환경변수:
  ADAPTER_PATH: LoRA adapter 경로 (기본: ./adapter_qwen3)
  BASE_MODEL: 베이스 모델 (기본: Qwen/Qwen3.5-9B)
  PORT: 서버 포트 (기본: 5050)
"""

import re
import os
import time
import logging
import asyncio
from pathlib import Path

import aiohttp as _aiohttp
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

BASE_MODEL = os.environ.get("BASE_MODEL", "Qwen/Qwen3.5-9B")
ADAPTER_PATH = os.environ.get("ADAPTER_PATH", str(Path(__file__).parent / "adapter_qwen3"))
PORT = int(os.environ.get("PORT", "5050"))

_model = None
_tokenizer = None

SYSTEM_PROMPT = (
    "너는 이터널 리턴의 쌍둥이 실험체 데비&마를렌이야. 한국어로만 대답해.\n"
    "데비(언니): 활발, 천진난만, 장난기. 직설적이고 솔직함.\n"
    '마를렌(동생): 냉소적, 과묵, 신중. 말이 짧고 차분함.\n'
    "형식: 데비: (대사) + 마를렌: (대사). 각자 1-2문장으로 짧게."
)

CJK_PATTERN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff]+")
EN_PATTERN = re.compile(r"[A-Za-z]{3,}")
THINK_PATTERN = re.compile(r"<think>.*?</think>\s*", re.DOTALL)

# --- 패치노트 검색 (키워드 감지 방식) ---

PATCHNOTE_LIST_URL = "https://playeternalreturn.com/posts/news?categoryPath=patchnote"
PATCHNOTE_BASE_URL = "https://playeternalreturn.com/posts/news"
_patchnote_cache: dict = {}
_patchnote_list: list = []

CHARACTER_ALIASES = {
    "에이든": "에이든", "뎁마": "데비&마를렌", "데비": "데비&마를렌",
    "마를렌": "데비&마를렌", "알렉스": "알렉스", "현우": "현우",
    "피오라": "피오라", "에키온": "에키온", "바바라": "바바라",
    "쇼이치": "쇼이치", "이삭": "이삭", "프리야": "프리야",
    "코랄린": "코랄린", "클로이": "클로이", "카밀로": "카밀로",
    "츠바메": "츠바메", "가넷": "가넷", "라우라": "라우라",
    "레니": "레니", "레온": "레온", "마이": "마이",
    "수아": "수아", "시셀라": "시셀라", "유키": "유키",
    "이렘": "이렘", "키아라": "키아라", "실비아": "실비아",
}

PATCH_KEYWORDS = ["패치", "너프", "버프", "변경", "수정", "밸런스", "상향", "하향", "바뀌"]


async def _fetch_patchnote_list():
    global _patchnote_list
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "ko-KR,ko;q=0.9"}
    try:
        async with _aiohttp.ClientSession() as session:
            async with session.get(PATCHNOTE_LIST_URL, headers=headers, timeout=_aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return _patchnote_list
                html = await resp.text()
                pattern = re.compile(r'href="[^"]*?/posts/news/(\d+)"[^>]*>.*?er-article__title">([^<]+)</h4>', re.DOTALL)
                _patchnote_list = [{"id": m.group(1), "title": m.group(2).strip()} for m in pattern.finditer(html)][:5]
                return _patchnote_list
    except Exception as e:
        logger.error("패치노트 목록 실패: %s", e)
        return _patchnote_list


async def _fetch_patchnote_content(post_id: str):
    if post_id in _patchnote_cache and time.time() - _patchnote_cache[post_id]["t"] < 3600:
        return _patchnote_cache[post_id]["c"]
    try:
        async with _aiohttp.ClientSession() as session:
            async with session.get(f"{PATCHNOTE_BASE_URL}/{post_id}", headers={"User-Agent": "Mozilla/5.0"}, timeout=_aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()
                body = re.search(r'class="er-post__body">(.*?)</div>\s*</(?:div|main|article)', html, re.DOTALL)
                text = re.sub(r"<[^>]+>", "\n", body.group(1) if body else html)
                text = re.sub(r"&\w+;", " ", text)
                text = "\n".join(l.strip() for l in text.split("\n") if l.strip())
                _patchnote_cache[post_id] = {"c": text, "t": time.time()}
                return text
    except Exception as e:
        logger.error("패치노트 본문 실패: %s", e)
        return None


def _detect_and_search(message: str) -> str | None:
    """키워드 감지 -> 패치노트 검색 -> context 반환"""
    has_patch = any(k in message for k in PATCH_KEYWORDS)
    if not has_patch:
        return None

    # 캐릭터 이름 감지
    keyword = None
    for alias, name in CHARACTER_ALIASES.items():
        if alias in message:
            keyword = name
            break

    if not keyword:
        for k in ["아이템", "무기", "방어구", "장비"]:
            if k in message:
                keyword = k
                break

    if not keyword:
        keyword = "패치"

    loop = asyncio.new_event_loop()
    try:
        posts = loop.run_until_complete(_fetch_patchnote_list())
        if not posts:
            return None
        content = loop.run_until_complete(_fetch_patchnote_content(posts[0]["id"]))
        if not content:
            return None
    finally:
        loop.close()

    lines = content.split("\n")
    results = []
    kw = keyword.lower()
    for i, line in enumerate(lines):
        if kw in line.lower():
            start, end = max(0, i - 2), min(len(lines), i + 6)
            results.append("\n".join(lines[start:end]))

    if results:
        return f"[{posts[0]['title']}] {keyword} 관련:\n" + "\n---\n".join(results[:3])
    return f"[{posts[0]['title']}] {keyword}: 이번 패치에 변경사항 없음."


# --- 모델 ---

def load_model():
    global _model, _tokenizer
    if _model is not None:
        return

    import torch
    from transformers import Qwen3_5ForConditionalGeneration, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)

    logger.info("모델 로딩: %s (4-bit)", BASE_MODEL)
    _model = Qwen3_5ForConditionalGeneration.from_pretrained(BASE_MODEL, quantization_config=bnb, device_map="auto", trust_remote_code=True)

    if os.path.exists(ADAPTER_PATH):
        logger.info("LoRA: %s", ADAPTER_PATH)
        _model = PeftModel.from_pretrained(_model, ADAPTER_PATH)
        # merge 안 함 — 4-bit merge는 극도로 느림. LoRA를 런타임에 얹은 채로 추론.

    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    _model.eval()

    import torch as _t
    logger.info("로드 완료 (VRAM: %.1f GB)", _t.cuda.memory_allocated() / 1024**3)


def clean_response(text: str) -> str:
    text = THINK_PATTERN.sub("", text)
    text = CJK_PATTERN.sub("", text)
    text = EN_PATTERN.sub("", text)
    text = re.sub(r"(.{2,6})\1{2,}", r"\1", text)
    lines = [l.strip() for l in text.split("\n") if l.strip() and l.strip() not in ("데비:", "마를렌:")]
    return "\n".join(lines)


def generate_response(user_message: str, history: list = None, context: str = None) -> str:
    import torch

    load_model()

    # 키워드 감지 RAG
    if not context:
        context = _detect_and_search(user_message)
        if context:
            logger.info("RAG context: %s", context[:80])

    system = SYSTEM_PROMPT
    if context:
        system += f"\n\n[게임 정보]\n{context[:400]}\n위 정보를 바탕으로 대답해. 모르면 모른다고 해."

    messages = [{"role": "system", "content": system}]
    if history:
        for h in history[-5:]:
            messages.append({"role": "user", "content": h["user"]})
            messages.append({"role": "assistant", "content": h["assistant"]})
    messages.append({"role": "user", "content": user_message})

    text = _tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    inputs = _tokenizer(text, return_tensors="pt").to(_model.device)

    max_tok = 120 if context else 80

    with torch.no_grad():
        output = _model.generate(**inputs, max_new_tokens=max_tok, temperature=0.5, top_p=0.9, do_sample=True)

    response = _tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return clean_response(response)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    history = data.get("history", [])
    context = data.get("context")

    if not message:
        return jsonify({"error": "message required"}), 400

    start = time.time()
    response = generate_response(message, history, context)
    elapsed = time.time() - start

    logger.info("[%.1fs] Q: %s -> A: %s", elapsed, message[:50], response[:80])
    return jsonify({"response": response, "elapsed": round(elapsed, 2)})


@app.route("/health", methods=["GET"])
def health():
    import torch
    vram = torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0
    return jsonify({"status": "running", "model": BASE_MODEL, "adapter": ADAPTER_PATH, "vram_gb": round(vram, 1)})


if __name__ == "__main__":
    load_model()
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
