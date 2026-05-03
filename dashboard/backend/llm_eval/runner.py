"""4 모델 응답 수집기.

dataset.json 의 모든 질문을 4 개 모델에 던지고 응답을 results.jsonl 로 적재.

  python3 dashboard/backend/llm_eval/runner.py [--limit N] [--models gemma,haiku,sonnet,gpt]

각 응답 항목:
  {q_id, model, response, latency_ms, input_tokens, output_tokens, cost_usd, error?}

비용은 모델별 단가표(2026-05 기준)로 사후 계산.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import aiohttp

ROOT = Path(__file__).parent

# 평가용 system prompt — 4 모델 동일하게 적용 (공정성)
SYSTEM_PROMPT = (
    "당신은 메이플스토리 게임 도메인 질의응답 어시스턴트입니다. "
    "사용자 질문에 사실 기반으로 정확하고 간결하게 답하세요. "
    "확실히 알지 못하는 정보는 추측하지 말고 '확실치 않습니다' 또는 '확인 불가'라고 답하세요. "
    "답변은 1-3문장으로 짧게 작성하고 불필요한 군더더기 없이 핵심만 전하세요."
)

# 모델별 단가 (USD per 1M tokens, 2026-05 기준). self-host 는 시간당 인프라 비용을 호출당으로 환산
PRICING = {
    "gemma-4-e4b-lora-modal": {"input": 0.0,  "output": 0.0,  "infra_per_call_usd": 0.0012},  # A10G $1.10/h, ~3s/call
    "exaone-3.5-2.4b-ollama": {"input": 0.0,  "output": 0.0,  "infra_per_call_usd": 0.0},     # 로컬 추론, infra cost 0
    "haiku-4.5":              {"input": 1.0,  "output": 5.0},
    "gpt-5.4-mini":           {"input": 0.75, "output": 4.5},
}

GEMMA_MODAL_URL = "https://goenho0613--gemma4-chat-server-gemma4chat-chat.modal.run"
OLLAMA_URL = "http://localhost:11434/api/chat"
EXAONE_TAG = "exaone3.5:2.4b"


# ---------- 모델 호출 ----------

async def call_gemma(session: aiohttp.ClientSession, prompt: str, context: str | None = None, history: list | None = None) -> dict:
    """Modal LoRA endpoint. system_prompt 던져서 페르소나 우회. context 있으면 RAG 모드. history 있으면 multi-turn."""
    sys_prompt = SYSTEM_PROMPT
    if context:
        sys_prompt += f"\n\n[참고 자료 - 답변 시 반드시 이 내용을 우선 인용]\n{context}"
    body = {
        "message": prompt,
        "system_prompt": sys_prompt,
        "max_tokens": 250,
    }
    if history:
        # Modal endpoint history 포맷: [{user, assistant}, ...] (run/services/chat/gemma4_modal_server.py 참조)
        pairs = []
        u = None
        for t in history:
            if t["role"] == "user":
                u = t["content"]
            elif t["role"] == "assistant" and u is not None:
                pairs.append({"user": u, "assistant": t["content"]})
                u = None
        body["history"] = pairs
    t0 = time.perf_counter()
    async with session.post(GEMMA_MODAL_URL, json=body, timeout=aiohttp.ClientTimeout(total=120)) as r:
        data = await r.json()
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    if "response" not in data:
        return {"error": data.get("error", "no response field"), "latency_ms": elapsed_ms}
    return {
        "response": data["response"].strip(),
        "latency_ms": elapsed_ms,
        "input_tokens": None,
        "output_tokens": None,
    }


async def call_ollama(session: aiohttp.ClientSession, model_tag: str, prompt: str, context: str | None = None, history: list | None = None) -> dict:
    """Ollama 로컬. /api/chat. context 있으면 system 에 합침. history 있으면 multi-turn."""
    sys_prompt = SYSTEM_PROMPT
    if context:
        sys_prompt += f"\n\n[참고 자료 - 답변 시 반드시 이 내용을 우선 인용]\n{context}"
    msgs = [{"role": "system", "content": sys_prompt}]
    if history:
        msgs.extend(history)
    msgs.append({"role": "user", "content": prompt})
    body = {
        "model": model_tag,
        "messages": msgs,
        "stream": False,
        "options": {"num_predict": 300, "temperature": 0.3},
    }
    t0 = time.perf_counter()
    async with session.post(OLLAMA_URL, json=body, timeout=aiohttp.ClientTimeout(total=180)) as r:
        data = await r.json()
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    if "message" not in data:
        return {"error": data.get("error", str(data)), "latency_ms": elapsed_ms}
    return {
        "response": data["message"]["content"].strip(),
        "latency_ms": elapsed_ms,
        "input_tokens": data.get("prompt_eval_count"),
        "output_tokens": data.get("eval_count"),
    }


async def call_anthropic(session: aiohttp.ClientSession, model: str, prompt: str, api_key: str, context: str | None = None, history: list | None = None) -> dict:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    sys_prompt = SYSTEM_PROMPT
    if context:
        sys_prompt += f"\n\n[참고 자료 - 답변 시 반드시 이 내용을 우선 인용]\n{context}"
    msgs = list(history) if history else []
    msgs.append({"role": "user", "content": prompt})
    body = {
        "model": model,
        "max_tokens": 300,
        "system": sys_prompt,
        "messages": msgs,
    }
    t0 = time.perf_counter()
    async with session.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers, json=body,
        timeout=aiohttp.ClientTimeout(total=120),
    ) as r:
        data = await r.json()
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    if r.status != 200:
        return {"error": data.get("error", {}).get("message", str(data)), "latency_ms": elapsed_ms, "status": r.status}
    text = data["content"][0]["text"].strip()
    usage = data.get("usage", {})
    return {
        "response": text,
        "latency_ms": elapsed_ms,
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
    }


async def call_openai(session: aiohttp.ClientSession, model: str, prompt: str, api_key: str, context: str | None = None, history: list | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    sys_prompt = SYSTEM_PROMPT
    if context:
        sys_prompt += f"\n\n[참고 자료 - 답변 시 반드시 이 내용을 우선 인용]\n{context}"
    msgs = [{"role": "system", "content": sys_prompt}]
    if history:
        msgs.extend(history)
    msgs.append({"role": "user", "content": prompt})
    body = {
        "model": model,
        "max_completion_tokens": 400,
        "messages": msgs,
    }
    t0 = time.perf_counter()
    async with session.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers, json=body,
        timeout=aiohttp.ClientTimeout(total=120),
    ) as r:
        data = await r.json()
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    if r.status != 200:
        return {"error": data.get("error", {}).get("message", str(data)), "latency_ms": elapsed_ms, "status": r.status}
    text = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage", {})
    return {
        "response": text,
        "latency_ms": elapsed_ms,
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
    }


def calc_cost(model_key: str, in_tok: int | None, out_tok: int | None) -> float:
    p = PRICING.get(model_key, {})
    if "infra_per_call_usd" in p:
        return p["infra_per_call_usd"]
    if in_tok is None or out_tok is None:
        return 0.0
    return (in_tok / 1_000_000) * p.get("input", 0.0) + (out_tok / 1_000_000) * p.get("output", 0.0)


# ---------- 메인 루프 ----------

async def run_one(session, model_key: str, q_id: str, prompt: str, keys: dict, context: str | None = None, history: list | None = None) -> dict:
    try:
        if model_key == "gemma-4-e4b-lora-modal":
            r = await call_gemma(session, prompt, context=context, history=history)
        elif model_key == "exaone-3.5-2.4b-ollama":
            r = await call_ollama(session, EXAONE_TAG, prompt, context=context, history=history)
        elif model_key == "haiku-4.5":
            r = await call_anthropic(session, "claude-haiku-4-5", prompt, keys["anthropic"], context=context, history=history)
        elif model_key == "gpt-5.4-mini":
            r = await call_openai(session, "gpt-5.4-mini", prompt, keys["openai"], context=context, history=history)
        else:
            return {"q_id": q_id, "model": model_key, "error": "unknown model"}
    except Exception as e:
        return {"q_id": q_id, "model": model_key, "error": f"{type(e).__name__}: {e}"}
    out = {"q_id": q_id, "model": model_key, **r}
    if "response" in out:
        out["cost_usd"] = round(calc_cost(model_key, out.get("input_tokens"), out.get("output_tokens")), 6)
    return out


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["maple", "er", "multiturn"], help="maple/er/multiturn")
    ap.add_argument("--mode", required=True, choices=["closed", "open"], help="closed-book vs open-book(RAG context 주입). multiturn 에선 무시 가능")
    ap.add_argument("--limit", type=int, default=None, help="첫 N개 질문만 (디버그용)")
    ap.add_argument("--models", default="gemma-4-e4b-lora-modal,exaone-3.5-2.4b-ollama,haiku-4.5,gpt-5.4-mini")
    ap.add_argument("--concurrency", type=int, default=4, help="모델 간 병렬도")
    args = ap.parse_args()

    keys = {
        "anthropic": os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
    }
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if "haiku-4.5" in models and not keys["anthropic"]:
        sys.exit("ANTHROPIC_API_KEY / CLAUDE_API_KEY 없음")
    if "gpt-5.4-mini" in models and not keys["openai"]:
        sys.exit("OPENAI_API_KEY 없음")

    ds_path = ROOT / {
        "maple": "dataset.json",
        "er": "dataset_er.json",
        "multiturn": "dataset_multiturn.json",
    }[args.dataset]
    ds = json.loads(ds_path.read_text(encoding="utf-8"))
    items = ds["items"]
    if args.limit:
        items = items[: args.limit]

    out_path = ROOT / f"results_{args.dataset}_{args.mode}.jsonl"
    out_path.write_text("", encoding="utf-8")
    print(f"[runner] {args.dataset} / {args.mode} — {len(items)} 질문 × {len(models)} 모델 = {len(items)*len(models)} 호출")

    sem = asyncio.Semaphore(args.concurrency)

    async def bounded(coro_fn, *a, **kw):
        async with sem:
            return await coro_fn(*a, **kw)

    async with aiohttp.ClientSession() as session:
        for q in items:
            # open-book: 항목별 source_excerpt를 retrieval 시뮬레이션으로 주입
            ctx = q.get("source_excerpt") if args.mode == "open" else None

            # multiturn 데이터셋: history + final_user_turn 사용
            if args.dataset == "multiturn":
                prompt = q["final_user_turn"]
                history = q.get("history", [])
            else:
                prompt = q["question"]
                history = None

            tasks = [bounded(run_one, session, m, q["id"], prompt, keys, ctx, history) for m in models]
            results = await asyncio.gather(*tasks)
            with out_path.open("a", encoding="utf-8") as f:
                for r in results:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            done_models = [r["model"] for r in results if "response" in r]
            errored = [(r["model"], r.get("error")) for r in results if "error" in r]
            print(f"  {q['id']}: ok={done_models} err={errored}")

    print(f"\n[done] {out_path} — {len(items)*len(models)} 행")


if __name__ == "__main__":
    asyncio.run(main())
