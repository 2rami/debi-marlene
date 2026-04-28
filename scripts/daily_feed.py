"""거노 일일 AI 피드 — fetch + dedup + LLM curate + Discord DM.

흐름:
    Sources (Smol AI / GitHub / HF / HN) → 원본 fetch
    → Firestore feed_seen 으로 중복 제거
    → Claude 에게 거노 관점 코멘트 + 점수 부탁
    → 점수 ≥ threshold 만 거노 DM
    → 보낸 항목 feed_seen + daily_feeds 에 적재

매일 1회 cron (오전 9시 KST = 0시 UTC) 실행 가정.

전제 (.env / Secret Manager):
    ANTHROPIC_API_KEY
    COMPANION_BOT_TOKEN (나쵸네코 봇 토큰)
    OWNER_ID (거노 Discord user id)
    GOOGLE_APPLICATION_CREDENTIALS or gcloud ADC

수동 실행:
    python3 scripts/daily_feed.py             # 정상 실행
    python3 scripts/daily_feed.py --dry-run   # DM 안 보내고 출력만
    python3 scripts/daily_feed.py --max 10    # 상위 10개만
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import anthropic
import requests
from google.cloud import firestore

ROOT = Path(__file__).resolve().parent.parent

GCP_PROJECT_ID = "ironic-objectivist-465713-a6"
DEDUP_COLLECTION = "feed_seen"
DAILY_COLLECTION = "daily_feeds"
DEDUP_TTL_DAYS = 30  # 30일 지난 항목은 다시 보낼 수 있음

CURATOR_MODEL = "claude-opus-4-7"
CURATOR_MAX_INPUT_ITEMS = 40  # 너무 많으면 비용/시간 ↑
DEFAULT_DM_LIMIT = 7
DEFAULT_SCORE_THRESHOLD = 5  # 5점 미만은 무시


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _gcp_secret(name: str) -> str:
    """Secret Manager 에서 latest 가져오기. .env 없을 때 fallback."""
    out = subprocess.run(
        ["gcloud", "secrets", "versions", "access", "latest",
         f"--secret={name}", f"--project={GCP_PROJECT_ID}"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def _hash_id(url: str) -> str:
    """URL 정규화 후 해시 — feed_seen 키."""
    parsed = urlparse(url)
    norm = f"{parsed.netloc}{parsed.path}".rstrip("/").lower()
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


# ─────────── Sources ───────────

def fetch_smol_ai(limit: int = 3) -> list[dict]:
    """Smol AI / news.smol.ai daily digest — RSS는 buttondown 옛 주소에 남아있음."""
    try:
        r = requests.get("https://buttondown.com/ainews/rss", timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[smol_ai] fetch fail: {e}")
        return []
    items = []
    for m in re.finditer(r"<item>(.*?)</item>", r.text, re.S):
        block = m.group(1)
        title = re.search(r"<title>(.*?)</title>", block, re.S)
        link = re.search(r"<link>(.*?)</link>", block, re.S)
        pub = re.search(r"<pubDate>(.*?)</pubDate>", block, re.S)
        if not (title and link):
            continue
        items.append({
            "source": "smol-ai",
            "title": re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", title.group(1)).strip(),
            "url": link.group(1).strip(),
            "published": pub.group(1).strip() if pub else "",
            "summary": "",
        })
        if len(items) >= limit:
            break
    return items


def fetch_github_trending(limit: int = 15, days: int = 7) -> list[dict]:
    """gh api search — 지난 N일 stars > 100 신규 레포 정렬."""
    from datetime import timedelta
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        out = subprocess.run(
            ["gh", "api", "-X", "GET", "search/repositories",
             "-f", f"q=created:>{since} stars:>100",
             "-f", "sort=stars", "-f", "order=desc",
             "-f", f"per_page={limit}"],
            capture_output=True, text=True, check=True, timeout=15,
        )
    except Exception as e:
        print(f"[github] fetch fail: {e}")
        return []
    data = json.loads(out.stdout)
    items = []
    for repo in data.get("items", []):
        items.append({
            "source": "github-trending",
            "title": f"{repo['full_name']}",
            "stars": repo["stargazers_count"],
            "downloads": None,
            "url": repo["html_url"],
            "summary": (repo.get("description") or "")[:200],
            "language": repo.get("language") or "",
        })
    return items


def fetch_hf_trending(limit: int = 15) -> list[dict]:
    """HuggingFace 모델 트렌딩 — likes7d 기준."""
    try:
        r = requests.get(
            "https://huggingface.co/api/models",
            params={"sort": "likes7d", "limit": limit, "direction": -1, "full": True},
            timeout=10,
        )
        r.raise_for_status()
    except Exception as e:
        print(f"[hf] fetch fail: {e}")
        return []
    items = []
    for m in r.json():
        repo_id = m.get("id") or m.get("modelId")
        if not repo_id:
            continue
        likes = m.get("likes", 0)
        downloads = m.get("downloads", 0)
        tags = m.get("tags", []) or []
        pipeline = m.get("pipeline_tag") or ""
        items.append({
            "source": "hf-trending",
            "title": repo_id,
            "stars": likes,
            "downloads": downloads,
            "url": f"https://huggingface.co/{repo_id}",
            "summary": pipeline + " · " + ", ".join(tags[:5]),
        })
    return items


def fetch_hn_ai(limit: int = 15) -> list[dict]:
    """Hacker News Algolia 검색 — AI/Claude/Anthropic/LLM 키워드 + 100 이상 점수."""
    try:
        r = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": "AI OR Claude OR Anthropic OR LLM OR \"language model\"",
                "tags": "story",
                "numericFilters": "points>100",
                "hitsPerPage": limit,
            },
            timeout=10,
        )
        r.raise_for_status()
    except Exception as e:
        print(f"[hn] fetch fail: {e}")
        return []
    items = []
    for hit in r.json().get("hits", []):
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        items.append({
            "source": "hn-ai",
            "title": f"{hit.get('title','')} ({hit.get('points',0)}pts, {hit.get('num_comments',0)}c)",
            "url": url,
            "summary": (hit.get("story_text") or "")[:200],
        })
    return items


# ─────────── Dedup ───────────

def filter_new(db: firestore.Client, items: list[dict]) -> list[dict]:
    new_items = []
    for it in items:
        h = _hash_id(it["url"])
        ref = db.collection(DEDUP_COLLECTION).document(h)
        if ref.get().exists:
            continue
        it["_hash"] = h
        new_items.append(it)
    return new_items


def mark_seen(db: firestore.Client, items: list[dict]) -> None:
    batch = db.batch()
    now = datetime.now(timezone.utc)
    for it in items:
        ref = db.collection(DEDUP_COLLECTION).document(it["_hash"])
        batch.set(ref, {
            "url": it["url"],
            "source": it["source"],
            "first_seen": now,
        })
    batch.commit()


# ─────────── Curator (Claude) ───────────

CURATOR_SYSTEM = """너는 거노(양건호)의 일일 AI 피드 큐레이터.

# 거노 프로필
- 신구대 시각디자인 졸업(2026.02), 게임회사 취업 준비
- 봇 프로젝트 운영: debi-marlene (Discord, Python, GCP, 디자인 = 본인 강점)
- 관심: AI/ML, 디자인, 한국어, Live2D, 일본어, 게임, 디스코드, audio/voice
- 약함: C++, 언리얼, Aseprite, Blender (미경험)
- 코딩 스타일: 바이브 코딩 (Claude Code 위주), 본인은 방향 설계
- 진행 중: 스마일게이트 DBA 지원, 봇 Firestore 이관, 누나 버튜버 LoRA, Companion Agent

# 너의 임무
받은 N개 AI 트렌딩/뉴스 항목 각각에:
1. 거노가 **실제 적용 가능한지** 0~10 점수
2. 한 줄 코멘트 (한국어, 반말) — 왜 좋은지 OR 왜 별로인지 거노 맥락에서

점수 기준:
- 9~10: 즉시 시도 가치, 진행 중 일과 직접 연결
- 7~8: 관심사 맞고 학습 가치 있음
- 5~6: 흥미롭지만 우선순위 낮음
- 0~4: 거노한테 안 맞음 (게임 무관 SaaS, C++ 라이브러리 등)

# 출력 형식 (JSON 배열만, 다른 텍스트 없이)
[{"i": 0, "score": 8, "comment": "한 줄"}, ...]

i = 입력 인덱스 (0부터)."""


def curate(client: anthropic.Anthropic, items: list[dict]) -> list[dict]:
    """Claude 에게 점수+코멘트 받아서 items 에 머지."""
    if not items:
        return []
    payload = "\n".join(
        f"[{i}] {it['source']} | {it['title']} | {it['url']}\n    {it.get('summary','')}".strip()
        for i, it in enumerate(items)
    )
    r = client.messages.create(
        model=CURATOR_MODEL,
        max_tokens=4096,
        system=CURATOR_SYSTEM,
        messages=[{"role": "user", "content": payload}],
    )
    text = "".join(block.text for block in r.content if block.type == "text")
    # 추출
    m = re.search(r"\[\s*\{.*?\}\s*\]", text, re.S)
    if not m:
        print(f"[curator] JSON 추출 실패. raw: {text[:300]}")
        return items
    try:
        scored = json.loads(m.group(0))
    except Exception as e:
        print(f"[curator] parse 실패: {e}")
        return items
    score_map = {s["i"]: s for s in scored}
    for i, it in enumerate(items):
        s = score_map.get(i, {})
        it["score"] = s.get("score", 0)
        it["comment"] = s.get("comment", "")
    return items


# ─────────── Discord DM ───────────

SOURCE_LABEL = {
    "smol-ai": "[NEWS]",
    "github-trending": "[GH]",
    "hf-trending": "[HF]",
    "hn-ai": "[HN]",
}


def _format_metrics(it: dict) -> str:
    """⭐ stars + ⬇ downloads 한 줄. 둘 다 없으면 빈 문자열."""
    parts = []
    if it.get("stars"):
        parts.append(f"⭐ {it['stars']:,}")
    if it.get("downloads"):
        parts.append(f"⬇ {it['downloads']:,}")
    return " · ".join(parts)


def _build_container(items: list[dict], date_str: str) -> dict:
    """Discord Components V2 Container 1개에 모든 항목 묶기.

    구조:
      Container (accent_color)
        ├─ TextDisplay 헤더
        ├─ Separator
        ├─ for each item:
        │    TextDisplay (제목+점수+코멘트+메트릭)
        │    Separator (마지막 제외)
    """
    header = f"## AI 피드 {date_str}\n신규 {len(items)}개 — 거노 맥락 점수순"
    nested = [
        {"type": 10, "content": header},
        {"type": 14, "divider": True, "spacing": 2},
    ]
    for i, it in enumerate(items):
        label = SOURCE_LABEL.get(it["source"], "[?]")
        score = it.get("score", "?")
        title = it["title"][:200]
        url = it["url"]
        comment = it.get("comment", "")[:300]
        metrics = _format_metrics(it)

        body_lines = [f"**[{score}/10] {label} [{title}]({url})**"]
        if metrics:
            body_lines.append(metrics)
        if comment:
            body_lines.append(f"> {comment}")
        nested.append({"type": 10, "content": "\n".join(body_lines)})
        if i < len(items) - 1:
            nested.append({"type": 14, "divider": True, "spacing": 1})

    return {
        "type": 17,
        "accent_color": 0x00C7CE,
        "components": nested,
    }


def post_dm(token: str, owner_id: str, items: list[dict], dry_run: bool = False) -> None:
    """봇 토큰 + owner-id 로 DM 채널 만들고 Components V2 Container 전송."""
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    base = "https://discord.com/api/v10"
    today = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    container = _build_container(items, today)

    if dry_run:
        print("\n=== DRY RUN — DM 안 보냄 ===")
        for it in items:
            metrics = _format_metrics(it)
            print(f"  [{it.get('score','?')}] {it['source']} {it['title']} {metrics}")
            print(f"     → {it.get('comment','')}")
            print(f"     {it['url']}")
        print("\n--- Container payload preview ---")
        print(json.dumps(container, ensure_ascii=False, indent=2)[:600] + "...")
        return

    r = requests.post(f"{base}/users/@me/channels", headers=headers,
                      json={"recipient_id": owner_id}, timeout=10)
    r.raise_for_status()
    dm_id = r.json()["id"]

    # IS_COMPONENTS_V2 flag = 1 << 15 = 32768
    payload = {
        "flags": 32768,
        "components": [container],
    }
    r = requests.post(f"{base}/channels/{dm_id}/messages", headers=headers,
                      json=payload, timeout=10)
    if r.status_code >= 400:
        print(f"[discord] {r.status_code} {r.text[:500]}")
        r.raise_for_status()


# ─────────── Main ───────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="DM 안 보내고 출력만")
    parser.add_argument("--max", type=int, default=DEFAULT_DM_LIMIT, help="DM 상위 N개")
    parser.add_argument("--threshold", type=int, default=DEFAULT_SCORE_THRESHOLD,
                        help="이 점수 미만은 제외")
    args = parser.parse_args()

    _load_env(ROOT / ".env")
    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY 필요")
        sys.exit(1)

    discord_token = os.getenv("COMPANION_BOT_TOKEN") or _gcp_secret("companion-bot-token")
    owner_id = os.getenv("OWNER_ID") or _gcp_secret("owner-id")

    print(f"=== Daily Feed @ {datetime.now()} ===")

    # 1. Fetch
    print("[1/4] Fetching sources...")
    raw = []
    raw += fetch_smol_ai(limit=2)
    raw += fetch_github_trending(limit=15, days=7)
    raw += fetch_hf_trending(limit=15)
    raw += fetch_hn_ai(limit=15)
    print(f"  raw items: {len(raw)}")
    if len(raw) > CURATOR_MAX_INPUT_ITEMS:
        raw = raw[:CURATOR_MAX_INPUT_ITEMS]

    # 2. Dedup
    print("[2/4] Dedup against Firestore...")
    db = firestore.Client(project=GCP_PROJECT_ID)
    new_items = filter_new(db, raw)
    print(f"  new items: {len(new_items)} (skipped {len(raw)-len(new_items)} duplicates)")
    if not new_items:
        print("→ 신규 항목 없음. DM 안 보냄.")
        return

    # 3. Curate
    print("[3/4] Claude curating...")
    client = anthropic.Anthropic(api_key=api_key)
    scored = curate(client, new_items)
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    selected = [it for it in scored if it.get("score", 0) >= args.threshold][:args.max]
    print(f"  selected: {len(selected)} (threshold ≥ {args.threshold}, max {args.max})")

    if not selected:
        print("→ threshold 통과 항목 없음. DM 안 보냄.")
        # 그래도 본 항목들은 mark seen (다음 fetch에서 재계산 안 하게)
        if not args.dry_run:
            mark_seen(db, new_items)
        return

    # 4. DM + persist
    print("[4/4] DM + Firestore save...")
    post_dm(discord_token, owner_id, selected, dry_run=args.dry_run)

    if not args.dry_run:
        # 보낸 항목 + 안 보낸 신규 항목 모두 mark seen
        mark_seen(db, new_items)
        # 일일 기록 저장 (대시보드 용도)
        today = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
        db.collection(DAILY_COLLECTION).document(today).set({
            "date": today,
            "sent_at": datetime.now(timezone.utc),
            "selected_count": len(selected),
            "raw_count": len(raw),
            "new_count": len(new_items),
            "items": selected,
        })
        print("  ✓ Firestore daily_feeds 적재 완료")

    print("DONE")


if __name__ == "__main__":
    main()
