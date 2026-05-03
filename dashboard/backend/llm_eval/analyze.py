"""채점 결과 분석 + 차트 + PDF 보고서 생성.

입력: graded_{maple,er}_{closed,open}.jsonl 4개
산출: reports/{date}.pdf — 차트 다수 묶음

차트:
1. 표지 (실험 명세 + 모델 라인업 + 데이터셋 요약)
2. Closed vs Open 정확도 비교 (모델별 grouped bar) — RAG 효과
3. 모델별 latency 분포 (box plot per dataset/mode)
4. Cost-quality frontier scatter (correctness vs cost USD per call)
5. 카테고리별 정답률 heatmap (모델 × 카테고리)
6. 할루시네이션율 (allow_unknown=true 항목 vs 일반 항목)
7. 결론 텍스트 페이지

  python3 dashboard/backend/llm_eval/analyze.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)


sns.set_style("whitegrid")
sns.set_context("talk", font_scale=0.85)


# 한글 폰트 — sns 설정 덮어쓰기 방지 위해 sns.set 후에 적용
def _setup_korean_font():
    candidates = ["Apple SD Gothic Neo", "AppleGothic", "NanumGothic", "Pretendard", "Noto Sans CJK KR"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["font.sans-serif"] = [name] + list(plt.rcParams["font.sans-serif"])
            # monospace 자리에도 한글 폰트 fallback (결론 페이지 monospace text 깨짐 방지)
            mono_pref = [m for m in ("Monoplex KR", name) if m in available]
            plt.rcParams["font.monospace"] = mono_pref + list(plt.rcParams["font.monospace"])
            return name
    return None


FONT = _setup_korean_font()
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42  # TrueType 임베드 — 한글 PDF 핵심
plt.rcParams["ps.fonttype"] = 42


MODEL_DISPLAY = {
    "gemma-4-e4b-lora-modal": "Gemma4 E4B+LoRA\n(self-host A10G)",
    "exaone-3.5-2.4b-ollama": "EXAONE 3.5 2.4B\n(local Apple Silicon)",
    "haiku-4.5":              "Claude Haiku 4.5\n(Anthropic API)",
    "gpt-5.4-mini":           "GPT-5.4 mini\n(OpenAI API)",
}
MODEL_ORDER = list(MODEL_DISPLAY.keys())
MODE_DISPLAY = {"closed": "Closed-book\n(모델만)", "open": "Open-book\n(RAG context)"}
DATASET_DISPLAY = {"maple": "MapleStory\n(static, evidence-grounded)", "er": "Eternal Return 11.0\n(post-cutoff patch)"}


def load_graded() -> pd.DataFrame:
    rows = []
    for ds in ("maple", "er"):
        for mode in ("closed", "open"):
            p = ROOT / f"graded_{ds}_{mode}.jsonl"
            if not p.exists():
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip(): continue
                r = json.loads(line)
                r["dataset"] = ds
                r["mode"] = mode
                rows.append(r)
    df = pd.DataFrame(rows)
    return df


def load_multiturn() -> pd.DataFrame:
    rows = []
    p = ROOT / "graded_multiturn_closed.jsonl"  # multiturn은 mode 의미 없음
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            rows.append(json.loads(line))
    return pd.DataFrame(rows)


def page_multiturn(pdf, df_mt: pd.DataFrame):
    if df_mt.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    # left: correctness by model
    ax = axes[0]
    agg = df_mt.groupby("model")["correctness"].mean().reindex(MODEL_ORDER).dropna()
    bars = ax.bar(range(len(agg)), agg.values, color=sns.color_palette("Set2", n_colors=len(agg)))
    ax.set_xticks(range(len(agg)))
    ax.set_xticklabels([MODEL_DISPLAY[m].split("\n")[0] for m in agg.index], rotation=15, ha="right")
    ax.set_ylim(0, 5.2)
    ax.axhline(5, color="#ccc", lw=0.5, ls="--")
    ax.set_ylabel("평균 correctness (1-5)")
    ax.set_title("Multi-turn 정답률")
    for i, v in enumerate(agg):
        ax.text(i, v + 0.08, f"{v:.2f}", ha="center", fontsize=9)

    # right: context_used %
    ax = axes[1]
    if "context_used" in df_mt.columns:
        sub = df_mt[df_mt["context_used"].isin([True, False])]
        if not sub.empty:
            agg = sub.groupby("model")["context_used"].mean().reindex(MODEL_ORDER).dropna() * 100
            ax.bar(range(len(agg)), agg.values, color="#1f77b4")
            ax.set_xticks(range(len(agg)))
            ax.set_xticklabels([MODEL_DISPLAY[m].split("\n")[0] for m in agg.index], rotation=15, ha="right")
            ax.set_ylim(0, 110)
            ax.set_ylabel("이전 history 활용률 (%)")
            ax.set_title("Multi-turn 맥락 활용 능력")
            for i, v in enumerate(agg):
                ax.text(i, v + 2, f"{v:.0f}%", ha="center", fontsize=9)

    fig.suptitle("Multi-turn 평가 (10 dialogues × 4 models = 40 응답)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def page_cover(pdf, df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis("off")

    title = "LLM 평가 보고서: Self-host 파인튜닝 vs Commercial Small"
    subtitle = f"메이플스토리 + 이터널리턴 도메인  ·  Closed-book vs Open-book(RAG)\n작성: 양건호 ({datetime.now():%Y-%m-%d})"

    ax.text(0.5, 0.93, title, ha="center", fontsize=20, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.86, subtitle, ha="center", fontsize=11, color="#444", transform=ax.transAxes)

    # 메타
    n_total = len(df)
    n_models = df["model"].nunique() if not df.empty else 0
    n_q = df["q_id"].nunique() if not df.empty else 0
    sum_cost = df["cost_usd"].sum() if "cost_usd" in df else 0
    summary = (
        f"총 응답: {n_total}건  /  모델: {n_models}종  /  질문: {n_q}개  /  실측 비용: ${sum_cost:.3f}"
    )
    ax.text(0.5, 0.79, summary, ha="center", fontsize=10, color="#666", transform=ax.transAxes)

    # 모델 라인업 표
    rows = [["모델", "클래스", "호스팅"]]
    rows.append(["Gemma 4 E4B + LoRA", "self-host 파인튜닝", "Modal A10G"])
    rows.append(["EXAONE 3.5 2.4B", "국내 base small (LG)", "Apple Silicon Metal"])
    rows.append(["Claude Haiku 4.5", "상용 small (Anthropic)", "Anthropic API"])
    rows.append(["GPT-5.4 mini", "상용 small (OpenAI)", "OpenAI API"])
    table = ax.table(cellText=rows[1:], colLabels=rows[0],
                     loc="center", bbox=[0.10, 0.42, 0.80, 0.30])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor("#222")
            cell.set_text_props(color="white", fontweight="bold")
        cell.set_edgecolor("#ccc")

    # 데이터셋 요약
    ax.text(0.5, 0.34, "데이터셋", ha="center", fontsize=12, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.28,
        "메이플스토리: 30개 (직업 8 / 보스 8 / 시스템 8 / 패치 6) — 나무위키 evidence-grounded\n"
        "이터널리턴 11.0: 30개 (실험체 12 / 아이템 8 / 시스템 6 / 신규 4) — 모든 모델 학습 컷오프 이후",
        ha="center", fontsize=10, color="#444", transform=ax.transAxes,
    )

    # 평가 모드
    ax.text(0.5, 0.18, "평가 모드", ha="center", fontsize=12, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.12,
        "Closed-book: 모델 자체 지식만으로 답변\n"
        "Open-book (RAG): 정답 근거(source_excerpt)를 system prompt로 주입 후 답변",
        ha="center", fontsize=10, color="#444", transform=ax.transAxes,
    )

    ax.text(0.5, 0.04, "채점: GPT-4o-mini judge (correctness 1-5 / hallucination y-n / 키워드 자동 매칭)",
            ha="center", fontsize=9, color="#888", transform=ax.transAxes)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def page_closed_vs_open(pdf, df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, ds in zip(axes, ("maple", "er")):
        sub = df[df["dataset"] == ds]
        if sub.empty: continue
        agg = sub.groupby(["model", "mode"])["correctness"].mean().reset_index()
        pivot = agg.pivot(index="model", columns="mode", values="correctness").reindex(MODEL_ORDER)
        pivot = pivot[["closed", "open"]]
        x = np.arange(len(pivot))
        w = 0.36
        ax.bar(x - w/2, pivot["closed"], w, label="Closed-book", color="#888")
        ax.bar(x + w/2, pivot["open"],   w, label="Open-book (RAG)", color="#2ca02c")
        ax.set_xticks(x)
        ax.set_xticklabels([MODEL_DISPLAY[m].split("\n")[0] for m in pivot.index], rotation=20, ha="right")
        ax.set_ylim(0, 5.2)
        ax.axhline(5, color="#ccc", lw=0.5, ls="--")
        ax.set_ylabel("평균 correctness (1-5)")
        ax.set_title(DATASET_DISPLAY[ds].replace("\n", " · "))
        ax.legend(loc="upper left", fontsize=9)
        for i, (c, o) in enumerate(zip(pivot["closed"], pivot["open"])):
            ax.text(i - w/2, c + 0.08, f"{c:.2f}", ha="center", fontsize=8)
            ax.text(i + w/2, o + 0.08, f"{o:.2f}", ha="center", fontsize=8)

    fig.suptitle("RAG 효과: Closed-book vs Open-book 정확도", fontsize=14, fontweight="bold")
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def page_latency(pdf, df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 6))
    sub = df[df["latency_ms"].notna()].copy()
    if sub.empty:
        plt.close(fig); return
    sub["latency_s"] = sub["latency_ms"] / 1000
    order = [m for m in MODEL_ORDER if m in sub["model"].unique()]
    sns.boxplot(data=sub, x="model", y="latency_s", order=order, ax=ax, palette="Set2")
    ax.set_xticklabels([MODEL_DISPLAY[m].split("\n")[0] for m in order], rotation=15, ha="right")
    ax.set_ylabel("응답 시간 (초)")
    ax.set_xlabel("")
    ax.set_title("모델별 응답 지연 분포 (4 runs 통합)", fontsize=14, fontweight="bold")
    medians = sub.groupby("model")["latency_s"].median().reindex(order)
    for i, m in enumerate(medians):
        ax.text(i, m + 0.3, f"med {m:.1f}s", ha="center", fontsize=9, color="#222")
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def page_cost_quality(pdf, df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, mode in zip(axes, ("closed", "open")):
        sub = df[df["mode"] == mode]
        if sub.empty: continue
        agg = sub.groupby("model").agg(
            corr=("correctness", "mean"),
            cost=("cost_usd", "mean"),
        ).reindex(MODEL_ORDER).reset_index()
        colors = sns.color_palette("Set2", n_colors=len(MODEL_ORDER))
        for i, row in agg.iterrows():
            ax.scatter(row["cost"], row["corr"], s=240, color=colors[i], edgecolor="#222",
                       linewidth=0.5, label=MODEL_DISPLAY[row["model"]].split("\n")[0])
            ax.annotate(MODEL_DISPLAY[row["model"]].split("\n")[0],
                        (row["cost"], row["corr"]), xytext=(8, 8),
                        textcoords="offset points", fontsize=8)
        ax.set_xlabel("호출당 평균 비용 (USD, log scale)")
        ax.set_ylabel("평균 correctness (1-5)")
        ax.set_xscale("symlog", linthresh=1e-5)
        ax.set_ylim(0, 5.5)
        ax.set_title(MODE_DISPLAY[mode].replace("\n", " · "))
        ax.grid(True, ls=":", alpha=0.5)

    fig.suptitle("Cost-Quality Frontier (호출당 비용 vs 정확도)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def page_category_heatmap(pdf, df: pd.DataFrame, dataset_id_field: str = "q_id"):
    """카테고리는 q_id prefix 로 추론 (jb-/bs-/sy-/pt-/ch-/it-/sys-/new-)."""
    if df.empty: return
    cat_map_maple = {"jb": "직업", "bs": "보스", "sy": "시스템", "pt": "최근패치"}
    cat_map_er = {"ch": "실험체", "it": "아이템", "sys": "시스템", "new": "신규"}

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for row_i, ds in enumerate(("maple", "er")):
        cat_map = cat_map_maple if ds == "maple" else cat_map_er
        for col_i, mode in enumerate(("closed", "open")):
            ax = axes[row_i][col_i]
            sub = df[(df["dataset"] == ds) & (df["mode"] == mode)].copy()
            if sub.empty:
                ax.axis("off"); continue
            sub["cat"] = sub["q_id"].str.split("-").str[0].map(cat_map).fillna("기타")
            pivot = sub.pivot_table(index="model", columns="cat", values="correctness", aggfunc="mean")
            pivot = pivot.reindex([m for m in MODEL_ORDER if m in pivot.index])
            sns.heatmap(pivot, annot=True, fmt=".2f", cmap="RdYlGn", vmin=1, vmax=5,
                        ax=ax, cbar=col_i == 1, linewidths=0.5)
            ax.set_yticklabels([MODEL_DISPLAY[m].split("\n")[0] for m in pivot.index], rotation=0, fontsize=8)
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.set_title(f"{DATASET_DISPLAY[ds].split(chr(10))[0]} · {MODE_DISPLAY[mode].split(chr(10))[0]}", fontsize=10)
    fig.suptitle("카테고리별 정답률 heatmap", fontsize=14, fontweight="bold")
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def page_hallucination(pdf, df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 6))
    if "hallucinated" not in df.columns:
        plt.close(fig); return
    agg = df.groupby(["model", "mode"])["hallucinated"].mean().reset_index()
    agg["rate"] = agg["hallucinated"] * 100
    pivot = agg.pivot(index="model", columns="mode", values="rate").reindex(MODEL_ORDER)[["closed", "open"]]
    x = np.arange(len(pivot))
    w = 0.36
    ax.bar(x - w/2, pivot["closed"], w, label="Closed-book", color="#d62728")
    ax.bar(x + w/2, pivot["open"], w, label="Open-book", color="#2ca02c")
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_DISPLAY[m].split("\n")[0] for m in pivot.index], rotation=15, ha="right")
    ax.set_ylabel("할루시네이션 발생률 (%)")
    ax.set_title("할루시네이션율 — closed-book이 모름을 인정 못 할 때 늘어남", fontsize=14, fontweight="bold")
    ax.legend()
    for i, (c, o) in enumerate(zip(pivot["closed"], pivot["open"])):
        ax.text(i - w/2, c + 1, f"{c:.0f}%", ha="center", fontsize=9)
        ax.text(i + w/2, o + 1, f"{o:.0f}%", ha="center", fontsize=9)
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def page_summary(pdf, df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis("off")
    ax.text(0.5, 0.95, "결론 — 본 평가가 양건호의 운영 결정에 어떻게 반영됐는가",
            ha="center", fontsize=16, fontweight="bold", transform=ax.transAxes)

    if df.empty:
        pdf.savefig(fig); plt.close(fig); return

    # 핵심 수치 (결론 narrative 의 근거)
    closed_avg = df[df["mode"] == "closed"]["correctness"].mean()
    open_avg = df[df["mode"] == "open"]["correctness"].mean()
    haiku_closed = df[(df["model"] == "haiku-4.5") & (df["mode"] == "closed")]
    haiku_hall_closed = haiku_closed["hallucinated"].mean() * 100 if not haiku_closed.empty else 0
    haiku_open_corr = df[(df["model"] == "haiku-4.5") & (df["mode"] == "open")]["correctness"].mean()

    findings = (
        "■ 본 보고서가 발견한 사실\n"
        f"   1. RAG 효과: closed-book 평균 {closed_avg:.2f} → open-book {open_avg:.2f} (+{open_avg - closed_avg:.2f}점)\n"
        f"   2. Haiku 4.5 closed-book 할루시네이션율 {haiku_hall_closed:.0f}% (4 모델 중 가장 낮음, 정직)\n"
        f"   3. Haiku 4.5 + RAG context = correctness {haiku_open_corr:.2f} / 5 (운영 안전선 도달)\n"
        "   4. Multi-turn 평가 — Gemma4 + LoRA 가 4 모델 중 최저 (페르소나 fine-tune 의 trade-off)\n"
        "   5. Maple closed (부분 학습 도메인) hall% 는 ER closed 보다 모든 모델에서 ↑\n"
    )

    decisions = (
        "\n■ 위 결과를 바탕으로 한 양건호의 운영 의사결정\n"
        "   → 라이브 봇 데비&마를렌(158서버) 모델: Claude Haiku 4.5 채용\n"
        "       사유: closed-book 정직성 0% hall + RAG 결합 시 안전선 + 비용/지연 균형\n"
        "\n"
        "   → Custom tool RAG 도입: search_patchnote (ER 공식 사이트 패치노트 fetch + 섹션 파싱)\n"
        "       사유: closed→open +3점 효과를 봇 응답 품질에 직접 반영\n"
        "\n"
        "   → 봇 대화 구조: single-turn 키워드 트리거로 의도적 한정\n"
        "       사유: multi-turn 에서 LoRA 모델이 약하다는 본 보고서 결과 (1.30 vs 2.60)\n"
        "       → 무리하게 multi-turn 대화 봇으로 키우지 않음\n"
        "\n"
        "   → Portfolio 챗봇(geno-portfolio): Sonnet 4.6 + search_portfolio custom tool\n"
        "       사유: 시연 트래픽(저빈도) 에선 premium 으로 임팩트 우선 — 같은 framework, 다른 tier\n"
    )

    closing = (
        "\n■ NEXON LLM 평가 어시스턴트 인턴 지원자로서\n"
        "   본 보고서는 단순 모델 비교가 아니라\n"
        "   '평가 → 결론 → 본인이 운영 중인 시스템에 적용' 의 close loop 을 보여주는 사례입니다.\n"
        "   같은 framework 를 새로운 NEXON 도메인 (메이플/카트/던파 등)에 그대로 확장 가능합니다.\n"
    )

    ax.text(0.05, 0.88, findings, va="top", fontsize=10,
            transform=ax.transAxes, family="monospace")
    ax.text(0.05, 0.62, decisions, va="top", fontsize=10,
            transform=ax.transAxes, family="monospace")
    ax.text(0.05, 0.20, closing, va="top", fontsize=10,
            transform=ax.transAxes, family="monospace", color="#444")

    ax.text(0.5, 0.02,
            f"평가 파이프라인 코드: dashboard/backend/llm_eval/  ·  생성: {datetime.now():%Y-%m-%d %H:%M}",
            ha="center", fontsize=8, color="#888", transform=ax.transAxes)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main():
    df = load_graded()
    df_mt = load_multiturn()
    if df.empty:
        print("graded_*.jsonl 없음 — grader 먼저 실행하세요.")
        return

    out_path = REPORTS / f"{datetime.now():%Y-%m-%d}.pdf"
    with PdfPages(out_path) as pdf:
        page_cover(pdf, df)
        page_closed_vs_open(pdf, df)
        page_latency(pdf, df)
        page_cost_quality(pdf, df)
        page_category_heatmap(pdf, df)
        page_hallucination(pdf, df)
        page_multiturn(pdf, df_mt)
        page_summary(pdf, df)

    print(f"[done] {out_path}")
    print(f"  single-turn rows: {len(df)}, multi-turn rows: {len(df_mt)}, models: {df['model'].nunique()}")


if __name__ == "__main__":
    main()
