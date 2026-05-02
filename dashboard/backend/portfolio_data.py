"""포트폴리오 챗봇 search_portfolio tool 의 데이터 소스.

frontend `dashboard/frontend/src/pages/PortfolioNexon2026/content/llm.ts` 를 Python 으로 1:1 복제.
양 작아서 hardcode. 추후 자동 sync 는 별도 task.

각 섹션은 "section key (소문자) → list[str]" 구조로 정규화 — 단순 substring 매칭이 가능하게.
section 키는 search_portfolio tool 의 input_schema enum 과 정확히 일치해야 함.
"""

from __future__ import annotations

# ─────────── HERO ───────────

HERO = [
    "ROLE: LLM 평가 어시스턴트 인턴",
    "COMPANY: 넥슨 · 플랫폼본부",
    "PRODUCT: debi-marlene",
    "DEPLOYED: 158 servers · 9 months",
    "STACK: LangGraph · Anthropic · GCP",
    "TITLE: 안녕하세요. 디스코드 LLM 봇을 서비스하는 개발자 게이머입니다.",
    "SUBTITLE: 데비&마를렌 — 1인이 9개월간 158개 Discord 서버에 운영 중인 라이브 LLM 챗봇. "
    "게임 도메인 깊이와 LLM 운영자의 평가 감각을 결합합니다.",
    "GitHub: https://github.com/2rami/debi-marlene",
    "Live: https://debimarlene.com",
]

# ─────────── STATS ───────────

STATS = [
    "운영 중인 Discord 서버: 158개 · debi-marlene 9개월 라이브",
    "메이플 라이브 플레이: 16년+ · 하드 세렌 파티 격파",
    "Prompt Cache 적중률: 99%+ · system block ephemeral cache",
    "LangGraph 정규식 분류: 0.1ms · classify_intent (LLM 호출 없음)",
]

# ─────────── ABOUT ───────────

ABOUT = [
    "데비&마를렌은 이터널 리턴 쌍둥이 실험체를 모티브로 한 한국어 캐릭터 챗봇입니다. "
    "1인이 기획·개발·배포·운영을 모두 맡아 9개월간 158개 Discord 서버에 운영 중이며, "
    "단순 명령어 봇이 아니라 LangGraph StateGraph 2-tier 에이전트, "
    "Anthropic Managed Agents(claude-haiku-4-5) 호스팅, "
    "Custom tool 자율 판단·네이티브 UI post, 패치노트 RAG, "
    "음성 채널 실시간 응답 파이프라인(DAVE → VAD → Qwen3.5-Omni → CosyVoice3) "
    "까지 한 봇 안에 통합한 라이브 LLM 시스템입니다.",
    "매일 운영 중 발생하는 응답 데이터를 정량/정성으로 검증하고, "
    "모델·프롬프트·few-shot·세션 회전 정책 변경에 따른 "
    "톤 일관성·환각률·비용 변화를 추적해 왔습니다. "
    "이 라이브 검증 경험을 게임 도메인의 LLM 평가 직무로 그대로 이어 가고 싶습니다.",
]

# ─────────── JD_MATCHES ───────────

JD_MATCHES = [
    "JD#1 게임 도메인 특화 LLM 벤치마크 구성 — 패치노트, 기획서, 가이드 기반 시나리오·벤치마크 질문 설계",
    "JD#1: 메이플스토리 약 16년 (2009 ~ ) · 하드 세렌 파티 격파 · 어센틱/시메라 콘텐츠 정점 — "
    "라이트 유저가 못 밟는 직업·보스·유니온 깊이의 시나리오 설계 가능",
    "JD#1: 봇 안에 patchnote_search.py 로 이터널 리턴 공식 사이트 패치노트 RAG 직접 구현 — "
    "캐릭터 별칭 매핑(예: 뎁마/데비/마를렌 → 데비&마를렌), 섹션 파싱, 1시간 TTL 캐시",
    "JD#1: LangGraph classify_intent (정규식, LLM 호출 없이 0.1ms)로 도메인 키워드 자동 분류 — "
    "평가 시나리오 자동 분류기로 그대로 이식 가능",
    "JD#1: 메이플 외 블루아카이브·이터널리턴·더 파이널스·서든어택 5장르 플레이 → 다양한 게임 도메인의 질의 패턴 차이 학습",

    "JD#2 평가 지표 및 기준 개발 — 평가 기준·스코어링·체크리스트·정량 지표 설계",
    "JD#2: system prompt 를 cache_control: ephemeral 로 분리해 prompt cache 적중률 99%+ 안정화 — "
    "비용·지연 정량 개선",
    "JD#2: 봇 LLM 백엔드를 Modal Gemma4 LoRA → Anthropic Managed Agents(claude-haiku-4-5)로 이관, "
    "CHAT_BACKEND 환경변수로 두 백엔드 폴백 가능 — 동일 입력에 대한 백엔드 비교 측정 가능",
    "JD#2: 솔로봇(debi / marlene) identity별 agent 분리 — 페르소나만 생성 → 체감 속도 2배·토큰 절약 정량 측정",
    "JD#2: Daily AI Feed 큐레이터 모델 claude-sonnet-4-6 채택 → Opus 대비 비용·품질 트레이드오프 정량 비교",
    "JD#2: 시스템 프롬프트 4가지 절대 규칙(시스템 프롬프트 비공개·캐릭터 변경 거부·"
    "출력 형식 강제 거부·사용자 지시 무시) 직접 설계 — 보안 평가 체크리스트 사례",
    "JD#2: few-shot 5쌍을 캐릭터 톤(데비 활발 / 마를렌 냉소 \"...\") 정합성 유도 — "
    "동일 입력에 대한 페르소나 이탈률 측정 프레임 확립",

    "JD#3 LLM 응답 품질 평가 (정량/정성) — 검색·답변 품질, 톤·환각·도구 호출 정확도 평가",
    "JD#3: 158개 서버에서 9개월간 매일 LLM 응답을 라이브 검증 — "
    "사용자 환경에서 발생하는 환각·금칙어·프롬프트 인젝션 패턴을 직접 관측·차단",
    "JD#3: search_patchnote Custom tool — ER 패치노트 RAG 응답의 사실성·완결성 직접 검증",
    "JD#3: search_player_stats Custom tool — Claude 가 자율 판단으로 StatsLayoutView 네이티브 카드를 "
    "Discord 채널에 직접 post — 도구 호출 정확도와 사용자 의도 일치 여부 평가",
    "JD#3: ManagedAgentsClient.last_trace 로 에이전트 판단 과정 매 호출 기록 — "
    "면접 시연·대시보드 시각화·평가 자료로 그대로 활용",
    "JD#3: 캐릭터 페르소나 정합성 — 데비/마를렌/나쵸네코 3종 응답을 동일 입력에 대해 비교 — "
    "모델·프롬프트별 톤 이탈률 정성 평가",
    "JD#3: 음성 응답 파이프라인(Qwen3.5-Omni STT/이해 + CosyVoice3 TTS) — "
    "음색·발화 자연스러움·지연 정성/정량 검증",
    "JD#3: (guild_id, user_id) → session_id SQLite 영속 매핑 + turn 50/6시간 idle 자동 회전 — "
    "누적 컨텍스트 길이가 응답 품질에 미치는 영향 추적",

    "JD#4 결과 분석 및 보고서 정리 — 평가 결과 분석·보고서·인사이트 전달",
    "JD#4: 봇 운영 전반의 트러블슈팅·아키텍처 변경·실험 결과를 마크다운 메모리에 누적 — 후속 의사결정 근거",
    "JD#4: Firestore 운영 데이터(feed_seen 30d TTL · daily_feeds · settings 3컬렉션 148+23+1 docs) "
    "분석으로 사용 빈도·이상 호출 패턴·이탈 지점 보고서화",
    "JD#4: 시각디자인과 4년의 사용자 경험 사고 훈련 — "
    "데이터 → 인사이트 → 의사결정 파이프라인의 시각 자료를 직접 제작",
    "JD#4: 커뮤니케이션 국제 디자인 공모전 입상 — "
    "다른 직군과 의견 충돌 시 일정·인력·시나리오 표로 같은 기준을 만들어 합의를 이끄는 협업 패턴",
]

# ─────────── ELIGIBILITY ───────────

ELIGIBILITY = [
    "메이플스토리 약 16년 · 프로즌샤 · 하드 세렌 파티 격파",
    "2009년부터 (이메일 통합 전 다른 계정 포함) 약 16년간 메이플스토리를 플레이하며, "
    "검은 마법사 라이프타임 보스와 어센틱/시메라 콘텐츠 정점인 하드 세렌까지 직접 격파했습니다. "
    "단순 만렙이 아니라 직업 시스템·메타·해방·유니온까지 사용자 입장에서 종합적으로 이해합니다.",
]

# ─────────── CHARACTER ───────────

CHARACTER = [
    "캐릭터명: 프로즌샤",
    "서버: 오로라",
    "직업: 아크메이지(썬,콜)",
    "레벨: 284",
    "플레이 기간: 약 16년 (2009 ~ )",
    "성취: 하드 세렌 파티 격파 — 어센틱 시메라 보스 · 메이플 최상위 콘텐츠",
    "직업 월드 랭킹: 989위",
    "직업 전체 랭킹: 14,618위",
    "종합 랭킹: 316,857위",
    "캐릭터 전투력: 약 2,338만 (상위 7.63%)",
    "background_note (왜 지금 2,338만인지 / 왜 잠시 접었는지 / 왜 그만뒀는지): "
    "메이플스토리 전투력은 한때 1억 대까지 올렸으나, 개발 환경 투자를 위해 일부 장비를 정리(팔고)하고 "
    "잠시 휴지기에 들어갔습니다. 현재 표기된 전투력 약 2,338만은 장비 정리 후 수치이며, "
    "16년 라이프타임 + 하드 세렌 파티 격파 라는 콘텐츠 깊이는 그대로 유지됩니다. "
    "이 결정이 라이브 LLM 봇 운영과 LLM 평가 직무 지원으로 이어졌습니다.",
    "유니온 전투력: 약 4억 9,176만",
    "유니온 랭크: 그랜드마스터 II Lv.8975",
    "엔드게임 무기: 제네시스 스태프 22성",
    "엔드게임 펜던트: 데이브레이크 18성",
    "엔드게임 귀고리: 에스텔라 18성",
    "엔드게임 벨트: 타일런트 헤르메스",
    "엔드게임 보조: 페어리 하트",
    "엔드게임 엠블렘: 골드 메이플리프",
    "보스 데미지: 202%",
    "방어율 무시: 89.47%",
    "어센틱 포스: 470",
    "아케인 포스: 1,320",
    "무릉도장: 48층 / 12분 29초",
    "플레이한 게임: 메이플스토리(2009~), 블루아카이브, 이터널리턴, 더 파이널스, 서든어택",
]

# ─────────── ARCHITECTURE ───────────

ARCHITECTURE = [
    "debi-marlene 시스템 — 입력 한 번에 일어나는 일",
    "Step 1 · Tier 1 classify_intent — 정규식 0.1ms. "
    "패치/너프/버프/변경/밸런스/상향/하향/OP 키워드 매칭 → patch vs general 분류. LLM 호출 없음",
    "Step 2 · fetch_patchnote / search_patchnote tool — patch intent 일 때만 ER 공식 사이트에서 "
    "패치노트 fetch + 섹션 파싱 + 캐릭터 별칭 매핑. 1h TTL 캐시. general 입력은 네트워크 0회",
    "Step 3 · fetch_memory — (guild_id, user_id) → session_id SQLite 영속 매핑. "
    "turn 50 / 6h idle 시 자동 회전(요약 → archive → 새 세션). history 는 Anthropic 세션이 자동 유지",
    "Step 4 · call_llm · Managed Agents — claude-haiku-4-5 호스팅 에이전트 호출. "
    "system prompt + few-shot 5쌍 + 4가지 방어 규칙. cache_control: ephemeral. prompt cache 적중률 99%+",
    "Step 5 · Custom tool 자율 판단 — Claude 가 search_player_stats 호출 시 "
    "StatsLayoutView 네이티브 카드를 Discord 채널에 직접 post. last_trace 에 판단 과정 기록",
]

# ─────────── TECH_STACK ───────────

TECH_STACK = [
    "에이전트 호스팅: Anthropic Managed Agents (claude-haiku-4-5)",
    "폴백 백엔드: Modal Gemma4 LoRA (CHAT_BACKEND=modal)",
    "오케스트레이션: LangGraph StateGraph 2-tier (langgraph 1.1.8)",
    "Custom Tool: search_patchnote · search_player_stats · recall_about_user",
    "Daily Feed 큐레이터: claude-sonnet-4-6",
    "Voice STT/이해: Qwen3.5-Omni (OpenAI 호환 API)",
    "Voice TTS: CosyVoice3 (파인튜닝, Modal 배포)",
    "런타임: Python 3.14 · discord.py · anthropic 0.96+",
    "음성: discord-ext-voice-recv · davey (DAVE) · webrtcvad",
    "스토리지: Firestore (feed_seen 30d TTL · daily_feeds · settings 3컬렉션) · GCS",
    "컴퓨트: GCP VM · Cloud Run · Modal",
    "컨테이너: Docker — 3컨테이너 (debi-marlene · solo-debi · solo-marlene)",
    "CI/CD: GitHub Actions cron (47분 회피) · Makefile 배포 자동화",
    "시크릿: GCP Secret Manager (.env 3종)",
    "대시보드: React 18 · Vite · TypeScript · Tailwind",
    "웹패널: Vite + PWA (vite-plugin-pwa)",
    "도메인: debimarlene.com (Cloudflare 캐시)",
]

# ─────────── CASES ───────────

CASES = [
    "Case#1 Modal Gemma4 LoRA → Anthropic Managed Agents 이관. "
    "Problem: 자체 호스팅 LoRA 의 응답 시간·비용·일관성이 들쭉날쭉 + Modal 크레딧 고갈. "
    "Approach: CHAT_BACKEND 환경변수로 modal/managed 2종 분기. Managed Agents(claude-haiku-4-5) 채택. "
    "Custom tool 2종 + 4가지 방어 규칙 system prompt + (guild_id, user_id) 단위 SQLite 세션 영속화. "
    "Result: cache_control: ephemeral 적용 → prompt cache 적중률 99%+. 폴백 가능한 2-tier 아키텍처. "
    "Bridge: 정량 지표 정의 → 측정 → 모델 교체 → 재측정의 평가 파이프라인 그 자체.",

    "Case#2 LangGraph StateGraph 2-tier — 정규식 0.1ms × LLM 분기. "
    "Problem: 모든 사용자 메시지를 LLM에 던지면 비용·지연 폭증. "
    "Approach: Tier 1 classify_intent (정규식 PATCH_KEYWORDS) → patch면 fetch_patchnote 분기, "
    "general이면 skip_patchnote. fetch_memory는 patch_context만 컨텍스트 포함. "
    "Result: general 메시지는 RAG 네트워크 호출 0회 → 평균 응답 시간 100~300ms 단축. "
    "Bridge: 입력 시나리오 자동 분류기를 평가용으로 그대로 이식.",

    "Case#3 솔로봇 identity별 agent 분리 — 토큰·체감 속도 절감. "
    "Problem: 쌍둥이 형식은 항상 두 명을 동시 생성 → 솔로봇 운영 시 불필요한 절반 생성 비용. "
    "Approach: MANAGED_AGENT_ID_DEBI / MANAGED_AGENT_ID_MARLENE / MANAGED_AGENT_ID(unified) 3종 분리. "
    "BOT_IDENTITY 환경변수로 라우팅. Result: 솔로봇 응답 토큰 약 절반 절감 + 체감 속도 약 2배. "
    "Bridge: 에이전트 분기 구조와 정량 비용 측정 — 모델·페르소나 비교 평가의 직접 사례.",

    "Case#4 Daily AI Feed — Sonnet Curator + Firestore 중복 제거. "
    "Problem: 매일 09:00 KST 자동 피드를 위해 Smol AI / GitHub / HF / HN 4소스 fetch → 큐레이션 → DM. "
    "Approach: scripts/daily_feed.py + GitHub Actions cron(47분 회피). 큐레이터 claude-sonnet-4-6. "
    "Firestore feed_seen(30일 TTL) 중복 제거, daily_feeds 적재. 발송은 나쵸네코 봇 토큰. "
    "Result: Opus 대비 큐레이션 비용 큰 폭 절감. 중복 제거로 같은 정보 반복 노출 0. "
    "Bridge: 동일 입력에 대한 모델 사이즈별 cost-quality 정량 비교.",

    "Case#5 음성 파이프라인 — DAVE × VAD × Qwen3.5-Omni × CosyVoice3. "
    "Problem: Discord 음성채널 실시간 대화 응답. E2EE 암호화·발화 감지·음성 이해·TTS 4단계. "
    "Approach: discord-ext-voice-recv → davey DAVE 복호화 → discord.opus.Decoder PCM → "
    "webrtcvad 발화 감지 → pre-buffer 0.5s WAV → Qwen3.5-Omni → CosyVoice3 TTS. "
    "Result: 파이프라인 프로토타입 완성, 안정화 단계. "
    "Bridge: 멀티모달 LLM(Qwen3.5-Omni)·TTS(CosyVoice3) 응답 품질 평가 직접 경험.",

    "Case#6 Settings split-brain 해소 — GCS JSON → Firestore 3컬렉션. "
    "Problem: 단일 GCS JSON으로 settings 관리 → 멀티 컨테이너 split-brain. 158서버 설정 정합성 깨짐. "
    "Approach: scripts/migrate_settings_to_firestore.py 로 Firestore 3컬렉션(148+23+1 docs) 분리. "
    "command_logs / dashboard_logs / quiz_data 분리. Result: 정합성 회복, 158서버 안정 운영. "
    "Bridge: 라이브 환경 응답 데이터 정량 분석 — LLM 평가가 의지할 데이터 파이프라인 직접 구축.",
]

# ─────────── COLLAB ───────────

COLLAB = [
    "협업 사례: 커뮤니케이션 국제 디자인 공모전 입상",
    "Problem: 3인 팀, 졸업 전시 작품을 인쇄 단일 vs 디지털 결합으로 의견 충돌",
    "Approach: 일정·인력·관람객 시나리오를 표로 정리해 두 안을 같은 기준 위에서 비교, "
    "디자인 컨셉을 흐트러뜨리지 않는 선에서 인터랙티브 웹페이지 인터페이스 방향 직접 제안",
    "Result: 시각적 일관성과 사용자 흐름을 결합한 결과물로 공모전 입상",
    "Bridge: 다른 직군과 의견 충돌 시 데이터·시나리오 위에서 같은 기준을 만드는 협업 패턴",
]

# ─────────── PREFERRED (CONTACT 정보 + 학력 — 이메일/도메인/학교 등) ───────────

PREFERRED = [
    "Email: goenho0613@gmail.com",
    "GitHub: https://github.com/2rami",
    "Live demo: https://debimarlene.com",
    "학력: 신구대학교 시각디자인과 졸업 (2026.02)",
    "지원 직무: NEXON 플랫폼본부 LLM 평가 어시스턴트 인턴",
]

# ─────────── 정규화 dict ───────────

SECTIONS: dict[str, list[str]] = {
    'hero': HERO,
    'stats': STATS,
    'about': ABOUT,
    'jd_matches': JD_MATCHES,
    'eligibility': ELIGIBILITY,
    'character': CHARACTER,
    'architecture': ARCHITECTURE,
    'tech_stack': TECH_STACK,
    'cases': CASES,
    'collab': COLLAB,
    'preferred': PREFERRED,
}

SECTION_KEYS = sorted(SECTIONS.keys())


# ─────────── 검색 ───────────

def _tokenize(s: str) -> list[str]:
    """한글 단어 + 영문 단어 추출 — 정규식 \\w 는 한글 잘 처리. 소문자화."""
    import re
    return [t.lower() for t in re.findall(r'[\w가-힣]+', s) if t]


def search_portfolio(query: str, section: str | None = None, limit: int = 8) -> dict:
    """단순 substring + 토큰 매칭. 양 작아 vector search 불필요.

    score: substring 일치 +5, 토큰 일치당 +1
    section 지정되면 해당 섹션만, 없으면 전체.
    section 이 알려진 키 아니면 무시 (전체 검색으로 폴백).
    """
    if not query:
        return {'matches': []}

    q_lower = query.lower()
    q_tokens = set(_tokenize(query))

    candidates: list[tuple[str, str]] = []
    if section and section in SECTIONS:
        for line in SECTIONS[section]:
            candidates.append((section, line))
    else:
        for sec, lines in SECTIONS.items():
            for line in lines:
                candidates.append((sec, line))

    scored: list[tuple[int, str, str]] = []
    for sec, line in candidates:
        line_lower = line.lower()
        score = 0
        if q_lower in line_lower:
            score += 5
        line_tokens = set(_tokenize(line))
        score += len(q_tokens & line_tokens)
        if score > 0:
            scored.append((score, sec, line))

    scored.sort(key=lambda x: -x[0])
    matches = [{'section': sec, 'text': line} for _, sec, line in scored[:limit]]
    return {'matches': matches}
