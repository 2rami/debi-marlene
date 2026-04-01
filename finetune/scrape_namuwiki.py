"""
나무위키 데비&마를렌 데이터 수집 스크래퍼
- 캐릭터 메인 페이지
- 대사 페이지
- 스토리/배경 페이지
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://namu.wiki/",
}

PAGES = {
    "main": "https://namu.wiki/w/%EB%8D%B0%EB%B9%84%26%EB%A7%88%EB%A5%BC%EB%A0%88%EB%84%A4",
    "quotes": "https://namu.wiki/w/%EB%8D%B0%EB%B9%84%26%EB%A7%88%EB%A5%BC%EB%A0%88%EB%84%A4/%EB%8C%80%EC%82%AC",
    "story": "https://namu.wiki/w/%EC%9D%B4%ED%84%B0%EB%84%90%20%EB%A6%AC%ED%84%B4/%EC%8A%A4%ED%86%A0%EB%A6%AC",
}


def scrape_page(url: str, name: str) -> str | None:
    print(f"[*] Scraping: {name} ({url})")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        print(f"    Status: {resp.status_code}")

        if resp.status_code != 200:
            print(f"    Failed!")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # 나무위키 본문 영역
        article = soup.select_one("article") or soup.select_one(".wiki-content") or soup.select_one("#app")
        if not article:
            # fallback: body 전체
            article = soup.body

        # 스크립트/스타일 제거
        for tag in article.find_all(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        text = article.get_text(separator="\n", strip=True)

        # 빈 줄 정리
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned = "\n".join(lines)

        output_path = os.path.join(OUTPUT_DIR, f"namuwiki_{name}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"    Saved: {output_path} ({len(cleaned)} chars)")
        return cleaned

    except Exception as e:
        print(f"    Error: {e}")
        return None


def main():
    results = {}
    for name, url in PAGES.items():
        text = scrape_page(url, name)
        results[name] = {
            "url": url,
            "success": text is not None,
            "chars": len(text) if text else 0,
        }
        time.sleep(2)  # 예의바른 크롤링

    # 결과 요약
    summary_path = os.path.join(OUTPUT_DIR, "scrape_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n=== Summary ===")
    for name, info in results.items():
        status = "OK" if info["success"] else "FAIL"
        print(f"  {name}: {status} ({info['chars']} chars)")


if __name__ == "__main__":
    main()
