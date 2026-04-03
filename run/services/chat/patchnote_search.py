"""
패치노트 검색 서비스

최신 패치노트를 가져와서 키워드로 검색.
캐릭터 이름 -> 관련 패치 내용 + 관련 아이템 변경사항 추출.
"""

import re
import asyncio
import logging
import time
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

PATCHNOTE_LIST_URL = "https://playeternalreturn.com/posts/news?categoryPath=patchnote"
PATCHNOTE_BASE_URL = "https://playeternalreturn.com/posts/news"

# 캐시
_patchnote_cache: dict = {}  # {post_id: {"title": ..., "content": ..., "fetched_at": ...}}
_patchnote_list: list = []
CACHE_TTL = 3600  # 1시간


# 캐릭터 이름 매핑 (별칭 -> 정식명)
CHARACTER_ALIASES = {
    "에이든": "에이든", "아덴": "에이든",
    "뎁마": "데비&마를렌", "데비": "데비&마를렌", "마를렌": "데비&마를렌",
    "알렉스": "알렉스", "알렉": "알렉스",
    "현우": "현우", "리다이린": "리다이린", "리 다이린": "리다이린",
    "피오라": "피오라", "에키온": "에키온",
    "바바라": "바바라", "쇼이치": "쇼이치",
    "이삭": "이삭", "프리야": "프리야",
    "코랄린": "코랄린", "클로이": "클로이",
    "카밀로": "카밀로", "이스트반": "이스트반",
    "츠바메": "츠바메", "가넷": "가넷",
    "라우라": "라우라", "레니": "레니",
    "레온": "레온", "레노레": "레노레",
    "마르티나": "마르티나", "마이": "마이",
    "베르니체": "베르니체", "셀린": "셀린",
    "수아": "수아", "슈엘린": "슈엘린",
    "시셀라": "시셀라", "아디나": "아디나",
    "이솔": "이솔", "알론소": "알론소",
    "에스텔": "에스텔", "엠마": "엠마",
    "유키": "유키", "이렘": "이렘",
    "카티": "카티", "키아라": "키아라",
    "펜리르": "펜리르", "실비아": "실비아",
}


async def fetch_patchnote_list() -> list:
    """패치노트 목록 가져오기"""
    global _patchnote_list
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                PATCHNOTE_LIST_URL, headers=headers,
                allow_redirects=False, timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return _patchnote_list
                html = await resp.text()
                pattern = re.compile(
                    r'href="[^"]*?/posts/news/(\d+)"[^>]*>.*?'
                    r'er-article__title">([^<]+)</h4>',
                    re.DOTALL,
                )
                posts = []
                for m in pattern.finditer(html):
                    post_id, title = m.groups()
                    posts.append({
                        "id": post_id,
                        "title": title.strip(),
                        "url": f"{PATCHNOTE_BASE_URL}/{post_id}",
                    })
                _patchnote_list = posts[:5]
                return _patchnote_list
    except Exception as e:
        logger.error("패치노트 목록 가져오기 실패: %s", e)
        return _patchnote_list


async def fetch_patchnote_content(post_id: str) -> Optional[str]:
    """패치노트 본문을 WebFetch 스타일로 가져오기 (HTML -> 텍스트)"""
    # 캐시 확인
    if post_id in _patchnote_cache:
        cached = _patchnote_cache[post_id]
        if time.time() - cached["fetched_at"] < CACHE_TTL:
            return cached["content"]

    url = f"{PATCHNOTE_BASE_URL}/{post_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()
                # er-post__body 클래스에서 본문 추출
                body_match = re.search(
                    r'class="er-post__body">(.*?)</div>\s*</(?:div|main|article)',
                    html, re.DOTALL,
                )
                if body_match:
                    text = re.sub(r"<[^>]+>", "\n", body_match.group(1))
                else:
                    text = re.sub(r"<[^>]+>", "\n", html)
                text = re.sub(r"&nbsp;", " ", text)
                text = re.sub(r"&[a-z]+;", " ", text)
                text = re.sub(r"\n{3,}", "\n\n", text)
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                content = "\n".join(lines)

                _patchnote_cache[post_id] = {
                    "content": content,
                    "fetched_at": time.time(),
                }
                return content
    except Exception as e:
        logger.error("패치노트 본문 가져오기 실패: %s", e)
        return None


def search_patchnote(content: str, keyword: str) -> str:
    """패치노트 내용에서 키워드 관련 섹션 추출"""
    if not content:
        return ""

    lines = content.split("\n")
    results = []
    keyword_lower = keyword.lower()

    for i, line in enumerate(lines):
        if keyword_lower in line.lower():
            # 키워드가 포함된 줄 + 전후 5줄
            start = max(0, i - 2)
            end = min(len(lines), i + 6)
            chunk = "\n".join(lines[start:end])
            results.append(chunk)

    if not results:
        return ""

    # 중복 제거 후 합치기
    return "\n---\n".join(results[:5])  # 최대 5개 섹션


def detect_search_intent(message: str) -> Optional[dict]:
    """메시지에서 패치노트 검색 의도 감지"""
    # 패치 관련 키워드
    patch_keywords = ["패치", "너프", "버프", "변경", "수정", "밸런스", "상향", "하향"]
    has_patch_keyword = any(k in message for k in patch_keywords)

    if not has_patch_keyword:
        return None

    # 캐릭터 이름 감지
    for alias, name in CHARACTER_ALIASES.items():
        if alias in message:
            return {"type": "character_patch", "character": name, "alias": alias}

    # 아이템 관련
    item_keywords = ["아이템", "무기", "방어구", "장비"]
    for k in item_keywords:
        if k in message:
            return {"type": "item_patch", "keyword": k}

    # 일반 패치 질문
    return {"type": "general_patch"}


async def get_patch_context(message: str) -> Optional[str]:
    """메시지를 분석해서 패치노트 컨텍스트를 반환"""
    intent = detect_search_intent(message)
    if not intent:
        return None

    # 최신 패치노트 목록 가져오기
    posts = await fetch_patchnote_list()
    if not posts:
        return None

    latest = posts[0]
    content = await fetch_patchnote_content(latest["id"])
    if not content:
        return None

    if intent["type"] == "character_patch":
        char_name = intent["character"]
        result = search_patchnote(content, char_name)
        if result:
            trimmed = result[:400]
            return f"[{latest['title']}] {char_name} 변경사항:\n{trimmed}"
        else:
            return f"[{latest['title']}] {char_name}: 이번 패치에 변경사항 없음."

    elif intent["type"] == "item_patch":
        keyword = intent["keyword"]
        result = search_patchnote(content, keyword)
        if result:
            trimmed = result[:300]
            return f"[{latest['title']}] {keyword} 변경:\n{trimmed}"
        else:
            return f"[{latest['title']}] {keyword}: 이번 패치에 변경사항 없음."

    else:
        return f"[{latest['title']}] 최신 패치 적용됨."
