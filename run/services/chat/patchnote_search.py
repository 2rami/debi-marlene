"""
패치노트 검색 서비스

ER 공식 사이트에서 최신 패치노트를 가져와서 섹션별로 파싱.
캐릭터/아이템/증강체 등 질문에 해당하는 섹션을 통째로 추출해서 LLM context로 전달.
"""

import re
import logging
import time
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

PATCHNOTE_LIST_URL = "https://playeternalreturn.com/posts/news?categoryPath=patchnote"
PATCHNOTE_BASE_URL = "https://playeternalreturn.com/posts/news"

# 캐시
_parsed_cache: dict = {}
_patchnote_list: list = []
CACHE_TTL = 3600

PATCH_KEYWORDS = [
    "패치", "너프", "버프", "변경", "수정", "밸런스", "상향", "하향", "바뀌",
    "추가", "신규", "새로", "등장", "개편", "조정", "업데이트", "노트",
]

# 캐릭터 별칭 -> 패치노트에 표기되는 한글 정식명
# 패치노트 실제 표기 기준 (10.6 기준 확인)
CHARACTER_ALIASES = {
    # 유저가 부를 수 있는 별칭 -> 패치노트 표기명
    "에이든": "에이든", "아덴": "에이든",
    "뎁마": "데비&마를렌", "데비": "데비&마를렌", "마를렌": "데비&마를렌",
    "알렉스": "알렉스", "알렉": "알렉스",
    "현우": "현우",
    "리다이린": "리 다이린", "리 다이린": "리 다이린", "다이린": "리 다이린",
    "피오라": "피오라", "에키온": "에키온",
    "바바라": "바바라", "쇼이치": "쇼이치",
    "프리야": "프리야", "가넷": "가넷",
    "카밀로": "카밀로", "츠바메": "츠바메",
    "라우라": "라우라", "레니": "레니",
    "레온": "레온", "마르티나": "마르티나", "마이": "마이",
    "셀린": "셀린", "수아": "수아",
    "시셀라": "시셀라", "아디나": "아디나",
    "알론소": "알론소", "에스텔": "에스텔", "엠마": "엠마",
    "유키": "유키", "이렘": "이렘",
    "키아라": "키아라", "펜리르": "펜리르", "실비아": "실비아",
    # 패치노트 표기와 다른 별칭
    "베르니체": "버니스", "버니스": "버니스",
    "레노레": "르노어", "르노어": "르노어",
    "슈엘린": "슈린", "슈린": "슈린",
    "이솔": "아이솔", "아이솔": "아이솔",
    "이삭": "아이작", "아이작": "아이작",
    "이스트반": "이슈트반", "이슈트반": "이슈트반",
    "카티": "캐시", "캐시": "캐시",
    "클로이": "클로에", "클로에": "클로에",
    "코랄린": "코렐라인", "코렐라인": "코렐라인",
    # 기타
    "나딘": "나딘", "나타폰": "나타폰",
    "다니엘": "다니엘", "드라": "드라",
    "루크": "루크", "리오": "리오",
    "매그너스": "매그너스", "빅터": "빅터",
    "아드리아나": "아드리아나", "아야": "아야",
    "얀": "얀", "재키": "재키",
    "제니": "제니", "하트": "하트",
    "하제": "하제", "혜진": "혜진",
    "보리": "보리", "띠아": "띠아",
    "미르카": "미르카",
}


async def _fetch_patchnote_list() -> list:
    """패치노트 목록 가져오기"""
    global _patchnote_list
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "ko-KR,ko;q=0.9"}
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
                posts = [
                    {"id": m.group(1), "title": m.group(2).strip()}
                    for m in pattern.finditer(html)
                ]
                _patchnote_list = posts[:5]
                return _patchnote_list
    except Exception as e:
        logger.error("패치노트 목록 실패: %s", e)
        return _patchnote_list


def _html_to_text(html: str) -> str:
    """HTML -> 텍스트 변환"""
    text = re.sub(r"<br\s*/?>", "\n", html)
    text = re.sub(r"</?(?:strong|b)>", "**", text)
    text = re.sub(r"</?(?:em|i)>", "", text)
    text = re.sub(r"<li[^>]*>", "\n- ", text)
    text = re.sub(r"<h[1-6][^>]*>", "\n### ", text)
    text = re.sub(r"</h[1-6]>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _parse_character_sections(text: str) -> dict:
    """실험체 섹션 텍스트에서 캐릭터별 블록 추출.

    패치노트는 줄바꿈 없이 이전 캐릭터 끝에 다음 캐릭터가 붙어있을 수 있음:
      "- 쿨다운 15초 → **10**초 **라우라**라우라는..."
    그래서 먼저 **이름** 앞에 줄바꿈을 삽입해서 정규화한 후 파싱.
    """
    all_names = sorted(set(CHARACTER_ALIASES.values()), key=len, reverse=True)
    # 이름 패턴: **가넷**, **데비&마를렌**, **보리 (B0-R1)** 등
    name_pattern = "|".join(re.escape(n) for n in all_names)

    # **캐릭터명** 앞에 줄바꿈 삽입 (정규화)
    normalized = re.sub(
        rf"(?<!\n)\*\*({name_pattern})\s*\*\*",
        r"\n**\1**",
        text,
    )

    # 이제 **이름** 기준으로 분리
    char_pattern = re.compile(rf"\*\*({name_pattern})\s*\*\*")
    matches = list(char_pattern.finditer(normalized))

    sections = {}
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(normalized)
        section_text = normalized[start:end].strip()
        if section_text:
            sections[name] = f"{name}\n{section_text}"

    return sections


def _find_section_by_keyword(text: str, keyword: str) -> Optional[str]:
    """전체 텍스트에서 keyword가 제목에 포함된 ### 섹션 모두 찾아 합치기.

    핫픽스/메인 패치 한 문서 안에도 같은 키워드 섹션이 여러 개 있을 수 있음
    (예: '아이템 스킬' + '신규 아이템'). 첫 매칭만 반환하면 누락 발생.
    """
    header_pattern = re.compile(r"^#{2,5}\s+\*{0,2}([^*\n]+?)\*{0,2}\s*$", re.MULTILINE)
    matches = list(header_pattern.finditer(text))

    parts: list[str] = []
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        if keyword in title:
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            parts.append(f"### {title}\n{body}")
    if not parts:
        return None
    return "\n\n".join(parts)


async def _fetch_and_parse(post_id: str) -> Optional[dict]:
    """패치노트를 가져와서 구조화된 형태로 파싱"""
    if post_id in _parsed_cache:
        cached = _parsed_cache[post_id]
        if time.time() - cached["fetched_at"] < CACHE_TTL:
            return cached

    url = f"{PATCHNOTE_BASE_URL}/{post_id}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "ko-KR,ko;q=0.9"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

                body_match = re.search(
                    r'class="er-post__body">(.*?)</div>\s*</(?:div|main|article)',
                    html, re.DOTALL,
                )
                body_html = body_match.group(1) if body_match else html
                content = _html_to_text(body_html)

                # "실험체" 섹션 찾아서 캐릭터별로 파싱
                char_section_text = _find_section_by_keyword(content, "실험체")
                char_sections = {}
                if char_section_text:
                    char_sections = _parse_character_sections(char_section_text)

                parsed = {
                    "post_id": post_id,
                    "characters": char_sections,
                    "full_text": content,
                    "fetched_at": time.time(),
                }
                _parsed_cache[post_id] = parsed
                return parsed
    except Exception as e:
        logger.error("패치노트 파싱 실패: %s", e)
        return None


def _parse_changes(section_text: str) -> list:
    """캐릭터 섹션에서 수치 변경사항을 구조화.

    Returns: [{"skill": "짓뭉개기&꿰뚫기(Q)", "changes": ["이동 속도 감소 35% → 40%"]}, ...]
    """
    lines = section_text.split("\n")
    changes = []
    current_skill = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith(("*", "#")):
            continue

        # - 스킬이름(Q) 형태
        skill_match = re.match(r"^-\s+(.+?\([A-Za-z패]\))\s*$", line)
        if skill_match:
            current_skill = skill_match.group(1)
            continue

        # - 수치 변경 (→ 포함)
        if "→" in line and line.startswith("-"):
            change_text = line.lstrip("- ").strip()
            # **bold** 제거
            change_text = re.sub(r"\*\*([^*]+)\*\*", r"\1", change_text)
            if current_skill:
                # 기존 스킬에 추가
                found = False
                for c in changes:
                    if c["skill"] == current_skill:
                        c["changes"].append(change_text)
                        found = True
                        break
                if not found:
                    changes.append({"skill": current_skill, "changes": [change_text]})
            else:
                # 스킬 없이 기본 스탯 변경 (무기 숙련도 등)
                changes.append({"skill": "기본", "changes": [change_text]})

    return changes


async def get_patch_context(message: str) -> tuple:
    """메시지를 분석해서 (LLM context 문자열, V2 표시용 dict) 반환.

    V2 dict: {"title": "10.6 패치노트", "character": "바바라", "changes": [...]} 또는 None
    캐릭터 변경사항이 없거나 일반 질문이면 V2 dict는 None.
    """
    has_patch_keyword = any(k in message for k in PATCH_KEYWORDS)
    if not has_patch_keyword:
        return None, None

    posts = await _fetch_patchnote_list()
    if not posts:
        return None, None

    # 최신 패치노트부터 검색 (핫픽스에 없으면 메인 패치로 fallback)
    detected_char = None
    for alias, name in CHARACTER_ALIASES.items():
        if alias in message:
            detected_char = name
            break

    if detected_char:
        for post in posts[:3]:
            parsed = await _fetch_and_parse(post["id"])
            if not parsed:
                continue
            chars = parsed.get("characters", {})
            if detected_char in chars:
                section = chars[detected_char]
                context = f"[{post['title']}] {detected_char} 변경사항:\n{section}"
                patch_info = {
                    "title": post["title"],
                    "character": detected_char,
                    "changes": _parse_changes(section),
                }
                return context, patch_info
        return f"[{posts[0]['title']}] {detected_char}: 최근 패치에 변경사항 없음.", None

    # 캐릭터 특정 안 되면 일반 패치 — 핫픽스/메인 패치 모두 모아서 합치기.
    # 첫 매칭에서 stop하면 핫픽스만 보고 "신규 추가 없다"는 식의 결론으로 빠짐.
    # 메시지 키워드 → 섹션 헤더 substring. _find_section_by_keyword가 substring 매칭.
    section_keywords = {"아이템": "아이템", "무기": "무기", "방어구": "방어구", "증강": "특성", "전술": "전술"}
    for kw, section_name in section_keywords.items():
        if kw in message:
            parts: list[str] = []
            post_titles: list[str] = []
            merged_changes: list = []
            for post in posts[:3]:
                parsed = await _fetch_and_parse(post["id"])
                if not parsed:
                    continue
                section = _find_section_by_keyword(parsed["full_text"], section_name)
                if section:
                    parts.append(f"[{post['title']}] {section_name}:\n{section[:300]}")
                    post_titles.append(post["title"])
                    merged_changes.extend(_parse_changes(section))
            if parts:
                patch_info = (
                    {
                        "title": " + ".join(post_titles),
                        "character": section_name,  # 임베드 카드 라벨로 재사용 (섹션명)
                        "changes": merged_changes,
                    }
                    if merged_changes
                    else None
                )
                return "\n\n".join(parts), patch_info

    return f"[{posts[0]['title']}] 최신 패치 적용됨.", None
