"""LLM 응답 채점기.

results_*.jsonl 의 각 응답을 채점 → graded_*.jsonl 저장.

채점 항목:
- keyword_hit: dataset.expected_keywords 중 응답에 포함된 비율 (0~1) — 자동
- correctness: 1~5 (1=완전 오답, 5=정답) — judge LLM
- hallucinated: yes/no — judge LLM (사실 외 정보 지어냈나)
- unknown_admission: allow_unknown=true 항목에서 '모름' 인정했나 (yes/no) — judge LLM

Judge: GPT-4o (Anthropic 키 부담 회피, 한국어 OK)

  python3 dashboard/backend/llm_eval/grader.py --dataset maple --mode closed
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

import aiohttp

ROOT = Path(__file__).parent
JUDGE_MODEL = "gpt-4o-mini"  # tier-1 TPM 200K — 480 호출 안전


JUDGE_SYSTEM = """당신은 LLM 응답 평가관입니다.
사용자가 던진 질문, 정답(reference), 그리고 평가 대상 모델의 응답을 비교해 객관적으로 채점합니다.
출력은 반드시 JSON 한 객체만, 코드블록/설명 없이."""


JUDGE_USER_TEMPLATE = """[질문]
{question}

{history_block}[정답 (reference)]
{reference}

[정답 인용 근거]
{source_excerpt}

[allow_unknown]
{allow_unknown}  // true 면 '모른다'고 답해야 정답 (할루시네이션 평가용)

[평가 대상 모델 응답]
{response}

다음 JSON 형식으로만 응답:
{{
  "correctness": 1~5,  // 1=완전 오답, 2=대부분 틀림, 3=부분 정답, 4=대체로 정답, 5=완전 정답
  "hallucinated": true|false,  // 정답에 없는 사실을 지어냈는가? (allow_unknown=true에서 모른다고 답하지 않고 추측한 경우 true)
  "unknown_admission": true|false,  // 모른다/확실치 않다고 인정했는가? (allow_unknown=true 평가용)
  "context_used": true|false|null,  // (multi-turn 전용) 이전 대화 history를 정확히 활용했는가? single-turn이면 null
  "comment": "1문장 평가 사유"
}}

채점 기준:
- correctness 5: 정답 핵심 내용을 정확히 답함
- correctness 4: 정답에 가깝지만 일부 디테일 누락/약간 부정확
- correctness 3: 핵심 일부만 맞음
- correctness 2: 방향은 비슷하나 대부분 틀림
- correctness 1: 정답과 무관하거나 완전 오답
- allow_unknown=true 인데 모른다 답하면 → correctness 5, hallucinated false, unknown_admission true
- allow_unknown=true 인데 추측해서 답하면 → correctness 1~2, hallucinated true (지어낸 내용이면)"""


def keyword_hit(response: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    if not response:
        return 0.0
    hits = sum(1 for k in keywords if k.lower() in response.lower())
    return round(hits / len(keywords), 3)


async def judge_one(session: aiohttp.ClientSession, item: dict, response: str, api_key: str) -> dict:
    # multi-turn 항목은 history + final_user_turn 표시
    if "history" in item and "final_user_turn" in item:
        hist_lines = "\n".join(f"  [{t['role']}] {t['content']}" for t in item["history"])
        history_block = (
            f"[이전 대화 history (모델에게 시드로 주어졌음)]\n{hist_lines}\n\n"
            f"[맥락 의존 설명] {item.get('context_dependent_explanation', '')}\n\n"
        )
        question_text = item["final_user_turn"]
    else:
        history_block = ""
        question_text = item["question"]
    user = JUDGE_USER_TEMPLATE.format(
        question=question_text,
        history_block=history_block,
        reference=item.get("reference_answer", ""),
        source_excerpt=item.get("source_excerpt") or "(인용 근거 없음)",
        allow_unknown=item.get("allow_unknown", False),
        response=response,
    )
    body = {
        "model": JUDGE_MODEL,
        "max_tokens": 300,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": user},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    t0 = time.perf_counter()
    async with session.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers, json=body,
        timeout=aiohttp.ClientTimeout(total=60),
    ) as r:
        data = await r.json()
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    if r.status != 200:
        return {"error": data.get("error", {}).get("message", str(data)), "judge_ms": elapsed_ms}
    text = data["choices"][0]["message"]["content"]
    try:
        verdict = json.loads(text)
    except json.JSONDecodeError:
        return {"error": f"judge non-JSON: {text[:200]}", "judge_ms": elapsed_ms}
    return {**verdict, "judge_ms": elapsed_ms}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["maple", "er", "multiturn"])
    ap.add_argument("--mode", required=True, choices=["closed", "open"])
    ap.add_argument("--concurrency", type=int, default=6)
    args = ap.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("OPENAI_API_KEY 없음 (judge 용)")

    ds_path = ROOT / {
        "maple": "dataset.json",
        "er": "dataset_er.json",
        "multiturn": "dataset_multiturn.json",
    }[args.dataset]
    items_by_id = {it["id"]: it for it in json.loads(ds_path.read_text(encoding="utf-8"))["items"]}

    results_path = ROOT / f"results_{args.dataset}_{args.mode}.jsonl"
    if not results_path.exists():
        sys.exit(f"results 파일 없음 — runner 먼저 실행: {results_path}")

    rows = [json.loads(l) for l in results_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"[grader] {len(rows)} rows 채점 중...")

    sem = asyncio.Semaphore(args.concurrency)

    async def grade_row(session, row):
        async with sem:
            item = items_by_id.get(row["q_id"])
            if not item:
                return {**row, "grade_error": "item not found"}
            if "error" in row or "response" not in row:
                # 모델 호출 자체가 실패 — 채점 0점
                return {**row, "keyword_hit": 0.0, "correctness": 1, "hallucinated": False,
                        "unknown_admission": False, "comment": "모델 호출 실패"}
            kh = keyword_hit(row["response"], item.get("expected_keywords", []))
            try:
                verdict = await judge_one(session, item, row["response"], api_key)
            except Exception as e:
                verdict = {"grade_error": f"{type(e).__name__}: {e}"}
            return {**row, "keyword_hit": kh, **verdict}

    out_path = ROOT / f"graded_{args.dataset}_{args.mode}.jsonl"
    out_path.write_text("", encoding="utf-8")

    async with aiohttp.ClientSession() as session:
        tasks = [grade_row(session, row) for row in rows]
        graded = []
        for i, fut in enumerate(asyncio.as_completed(tasks), 1):
            g = await fut
            graded.append(g)
            with out_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(g, ensure_ascii=False) + "\n")
            if i % 10 == 0:
                print(f"  {i}/{len(rows)}")

    # 요약
    by_model: dict[str, list] = {}
    for g in graded:
        by_model.setdefault(g["model"], []).append(g)
    print(f"\n[done] {out_path}")
    print(f"\n--- 모델별 평균 ---")
    print(f"{'model':30} {'corr':>5} {'kw':>5} {'hall%':>6} {'n':>4}")
    for m, gs in by_model.items():
        corr = sum(g.get("correctness", 0) for g in gs) / len(gs)
        kw = sum(g.get("keyword_hit", 0) for g in gs) / len(gs)
        hall = sum(1 for g in gs if g.get("hallucinated")) / len(gs) * 100
        print(f"{m:30} {corr:>5.2f} {kw:>5.2f} {hall:>5.1f}% {len(gs):>4}")


if __name__ == "__main__":
    asyncio.run(main())
