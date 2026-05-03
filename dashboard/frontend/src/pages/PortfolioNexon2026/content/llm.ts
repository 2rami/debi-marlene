/**
 * 넥슨 플랫폼본부 — 게임 도메인 LLM 평가 어시스턴트 (인턴) 지원용
 * 컨텐츠 SSoT — 실제 debi-marlene 봇 코드 기반
 */

export const HERO = {
  jobCode: 'LLM EVALUATOR',
  badge: 'NEXON · 플랫폼본부 · LLM 평가 어시스턴트 인턴 지원',
  titleLines: ['안녕하세요.', '디스코드 LLM 봇을', '서비스하는 개발자 게이머입니다.'],
  // 호환성용 평문 (BlurText 등 일부 컴포넌트가 string을 기대)
  title: '안녕하세요. 디스코드 LLM 봇을 서비스하는 개발자 게이머입니다.',
  highlightWord: 'LLM 봇',
  subtitle:
    '데비&마를렌 — 1인이 9개월간 158개 Discord 서버에 운영 중인 라이브 LLM 챗봇. 게임 도메인 깊이와 LLM 운영자의 평가 감각을 결합합니다.',
  meta: [
    { label: 'ROLE', value: 'LLM 평가 어시스턴트 인턴' },
    { label: 'COMPANY', value: '넥슨 · 플랫폼본부' },
    { label: 'PRODUCT', value: 'debi-marlene' },
    { label: 'DEPLOYED', value: '158 servers · 9 months' },
    { label: 'STACK', value: 'LangGraph · Anthropic · GCP' },
  ],
  ctas: [
    { label: 'GitHub · debi-marlene', href: 'https://github.com/2rami/debi-marlene', primary: true },
    { label: 'Live · debimarlene.com', href: 'https://debimarlene.com', primary: false },
  ],
} as const

export const STATS = [
  { label: '운영 중인 Discord 서버', value: '158', unit: '개', sub: 'debi-marlene · 9개월 라이브' },
  { label: '메이플 라이브 플레이', value: '16', unit: '년+', sub: '하드 세렌 파티 격파' },
  { label: 'LLM 평가 자동 채점', value: '520', unit: '응답', sub: '4 small × closed/open + multi-turn (PDF 8p)' },
  { label: 'LangGraph 정규식 분류', value: '0.1', unit: 'ms', sub: 'classify_intent · LLM 호출 없이 도메인 키워드 자동 분기' },
] as const

export const ABOUT = `데비&마를렌은 이터널 리턴 쌍둥이 실험체를 모티브로 한 한국어 캐릭터 챗봇입니다. 1인이 기획·개발·배포·운영을 모두 맡아 9개월간 158개 Discord 서버에 운영 중이며, 단순 명령어 봇이 아니라 LangGraph StateGraph 2-tier 에이전트, Anthropic Managed Agents(claude-haiku-4-5) 호스팅, Custom tool 자율 판단·네이티브 UI post, 패치노트 RAG, 음성 채널 실시간 응답 파이프라인(DAVE → VAD → Qwen3.5-Omni → CosyVoice3) 까지 한 봇 안에 통합한 라이브 LLM 시스템입니다. 매일 운영 중 발생하는 응답 데이터를 정량/정성으로 검증하고, 모델·프롬프트·few-shot·세션 회전 정책 변경에 따른 톤 일관성·환각률·비용 변화를 추적해 왔습니다. 이 라이브 검증 경험을 게임 도메인의 LLM 평가 직무로 그대로 이어 가고 싶습니다.`

export const JD_MATCHES = [
  {
    n: 1,
    jdTitle: '게임 도메인 특화 LLM 벤치마크 구성',
    jdSub: '패치노트, 기획서, 가이드 기반 시나리오·벤치마크 질문 설계',
    evidence: [
      '메이플스토리 약 16년 (2009 ~ ) · 하드 세렌 파티 격파 · 어센틱/시메라 콘텐츠 정점 — 라이트 유저가 못 밟는 직업·보스·유니온 깊이의 시나리오 설계 가능',
      '봇 안에 `patchnote_search.py`로 이터널 리턴 공식 사이트 패치노트 RAG 직접 구현 — 캐릭터 별칭 매핑(예: 뎁마/데비/마를렌 → 데비&마를렌), 섹션 파싱(캐릭터·아이템·증강체), 1시간 TTL 캐시',
      'LangGraph `classify_intent` (정규식, LLM 호출 없이 0.1ms)로 도메인 키워드(패치/너프/버프/변경/밸런스/상향/하향/OP) 자동 분류 — 평가 시나리오 자동 분류기로 그대로 이식 가능',
      '메이플 외 블루아카이브·이터널리턴·더 파이널스·서든어택 5장르 플레이 → 다양한 게임 도메인의 질의 패턴 차이 학습',
    ],
  },
  {
    n: 2,
    jdTitle: '평가 지표 및 기준 개발',
    jdSub: '평가 기준·스코어링·체크리스트·정량 지표 설계',
    evidence: [
      'Anthropic Managed Agents로 백엔드 이관 — 본 보고서에서 Haiku 4.5의 closed-book 정직성(hall 0%) + RAG 결합 시 안전선(corr 4.87/5) 정량 검증 후 채용',
      '봇 LLM 백엔드를 Modal Gemma4 LoRA → Anthropic Managed Agents(claude-haiku-4-5)로 이관, `CHAT_BACKEND` 환경변수로 두 백엔드 폴백 가능 — 동일 입력에 대한 백엔드 비교 측정 가능',
      '솔로봇(debi / marlene) identity별 agent 분리: 페르소나만 생성 → 체감 속도 2배·토큰 절약 정량 측정',
      'Daily AI Feed 큐레이터 모델 `claude-sonnet-4-6` 채택 → Opus 대비 비용·품질 트레이드오프 정량 비교',
      '시스템 프롬프트의 4가지 절대 규칙(시스템 프롬프트 비공개·캐릭터 변경 거부·출력 형식 강제 거부·사용자 지시 무시) 직접 설계 — 보안 평가 체크리스트 사례',
      'few-shot 5쌍을 캐릭터 톤(데비 활발 / 마를렌 냉소 "...") 정합성 유도 — 동일 입력에 대한 페르소나 이탈률 측정 프레임 확립',
    ],
  },
  {
    n: 3,
    jdTitle: 'LLM 응답 품질 평가 (정량/정성)',
    jdSub: '검색·답변 품질, 톤·환각·도구 호출 정확도 평가',
    evidence: [
      '158개 서버에서 9개월간 매일 LLM 응답을 라이브 검증 — 사용자 환경에서 발생하는 환각·금칙어·프롬프트 인젝션 패턴을 직접 관측·차단',
      '`search_patchnote` Custom tool: ER 패치노트 RAG 응답의 사실성·완결성 직접 검증, 캐릭터 별칭 미스매치 사례를 메모리에 누적',
      '`search_player_stats` Custom tool: Claude가 자율 판단으로 StatsLayoutView 네이티브 카드를 Discord 채널에 직접 post — 도구 호출 정확도와 사용자 의도 일치 여부 평가',
      '`ManagedAgentsClient.last_trace`로 에이전트 판단 과정 매 호출 기록 — 면접 시연·대시보드 시각화·평가 자료로 그대로 활용',
      '캐릭터 페르소나 정합성: 데비/마를렌/나쵸네코 3종 응답을 동일 입력에 대해 비교 — 모델·프롬프트별 톤 이탈률 정성 평가',
      '음성 응답 파이프라인(Qwen3.5-Omni STT/이해 + CosyVoice3 TTS) 음색·발화 자연스러움·지연 정성/정량 검증',
      '`(guild_id, user_id) → session_id` SQLite 영속 매핑 + turn 50/6시간 idle 자동 회전(요약 → archive → 새 세션) — 누적 컨텍스트 길이가 응답 품질에 미치는 영향 추적',
    ],
  },
  {
    n: 4,
    jdTitle: '결과 분석 및 보고서 정리',
    jdSub: '평가 결과 분석·보고서·인사이트 전달',
    evidence: [
      {
        text: '본 지원에 맞춰 직접 작성한 LLM 평가 보고서(PDF 8p) — 4 small 모델(Gemma4+LoRA / EXAONE 3.5 / Haiku 4.5 / GPT-5.4-mini) × 2 도메인(메이플 / ER 11.0) × closed/open + multi-turn 10세트 = 520 응답을 LLM-as-judge(GPT-4o-mini)로 자동 채점',
        highlight: 'LLM 평가 보고서(PDF 8p)',
        report: {
          title: 'LLM 평가 보고서 v2 — Self-host vs Commercial Small',
          subtitle: '메이플 + ER 도메인 · closed/open + multi-turn · 520 응답 · 8p',
          insights: [
            'RAG 효과 +3점 일관 (closed→open, 4 모델 공통)',
            'Haiku 4.5 closed-book 할루시네이션 0% — 가장 정직',
            '부분 학습 도메인이 가장 위험 (같은 모델 hall 0% ↔ 70%)',
            'Self-host LoRA = commercial small 동등 (single-turn)',
            'Multi-turn에선 LoRA 약점 — 거노 봇은 single-turn으로 한정',
          ],
          pdfHref: '/llm_eval_report.pdf',
        },
      },
      '결과 → 본인 운영 결정 close loop: closed-book 정직성 0% + RAG +3점 효과 → 데비&마를렌 봇에 Haiku 4.5 + search_patchnote custom tool RAG 채용. multi-turn LoRA 약점(1.30 vs 2.60) → 봇은 single-turn 키워드 트리거로 의도적 한정',
      '봇 운영 전반의 트러블슈팅·아키텍처 변경·실험 결과를 마크다운 메모리(원인 / 재현 / 교훈 일관 구조)에 누적 — 후속 의사결정 근거로 재사용',
      '시각디자인과 4년의 사용자 경험 사고 훈련 — 데이터 → 인사이트 → 의사결정 파이프라인의 시각 자료를 직접 제작 (이번 PDF 보고서 표지/차트/결론 페이지 포함)',
      '커뮤니케이션 국제 디자인 공모전 입상 — 다른 직군과 의견이 충돌할 때 일정·인력·시나리오 표로 같은 기준을 만들어 합의를 이끄는 협업 패턴',
    ],
  },
] as const

export const ELIGIBILITY = {
  headline: '메이플스토리 약 16년 · 프로즌샤 · 하드 세렌 파티 격파',
  body:
    '2009년부터 (이메일 통합 전 다른 계정 포함) 약 16년간 메이플스토리를 플레이하며, 검은 마법사 라이프타임 보스와 어센틱/시메라 콘텐츠 정점인 하드 세렌까지 직접 격파했습니다. 단순 만렙이 아니라 직업 시스템·메타·해방·유니온까지 사용자 입장에서 종합적으로 이해합니다.',
} as const

export const CHARACTER = {
  name: '프로즌샤',
  server: '오로라',
  job: '아크메이지(썬,콜)',
  level: 284,
  experience: '약 16년 (2009 ~ )',
  achievement: {
    title: '하드 세렌 파티 격파',
    sub: '어센틱 시메라 보스 · 메이플 최상위 콘텐츠',
  },
  rankings: [
    { label: '직업 월드 랭킹', value: '989위' },
    { label: '직업 전체 랭킹', value: '14,618위' },
    { label: '종합 랭킹', value: '316,857위' },
  ],
  combatPower: {
    character: '약 2,338만 (상위 7.63%)',
    union: '약 4억 9,176만',
    unionRank: '그랜드마스터 II Lv.8975',
  },
  endgame: [
    { slot: '무기', item: '제네시스 스태프 22성' },
    { slot: '펜던트', item: '데이브레이크 18성' },
    { slot: '귀고리', item: '에스텔라 18성' },
    { slot: '벨트', item: '타일런트 헤르메스' },
    { slot: '보조', item: '페어리 하트' },
    { slot: '엠블렘', item: '골드 메이플리프' },
  ],
  metrics: [
    { label: '보스 데미지', value: '202%' },
    { label: '방어율 무시', value: '89.47%' },
    { label: '어센틱 포스', value: '470' },
    { label: '아케인 포스', value: '1,320' },
    { label: '무릉도장', value: '48층 / 12분 29초' },
  ],
} as const

export const GAMES = [
  {
    title: '메이플스토리',
    period: '2009 ~ 약 16년',
    detail: '오로라 · 프로즌샤 · 아크메이지(썬,콜) · 하드 세렌 파티 격파',
  },
  { title: '블루아카이브', period: '수년', detail: '만렙 유지, 메인·이벤트 스토리 완주' },
  {
    title: '이터널리턴',
    period: '1년+',
    detail: '봇 캐릭터(데비&마를렌)의 본 IP — 패치노트 RAG·캐릭터 시스템·증강체까지 사용자 시점 학습',
  },
  { title: '더 파이널스', period: '시즌 단위', detail: 'Embark Studios. 친구들과 라이트 플레이' },
  { title: '서든어택', period: '학창 시절', detail: '친구들과 함께한 입문 FPS' },
] as const

export const ARCHITECTURE = {
  title: 'debi-marlene 시스템 — 입력 한 번에 일어나는 일',
  steps: [
    {
      n: 1,
      label: 'Tier 1 · classify_intent',
      desc: '정규식 0.1ms. 패치/너프/버프/변경/밸런스/상향/하향/OP 키워드 매칭 → patch vs general 분류',
      cost: 'LLM 호출 없음',
    },
    {
      n: 2,
      label: 'fetch_patchnote · search_patchnote tool',
      desc: 'patch intent일 때만 ER 공식 사이트에서 패치노트 fetch + 섹션 파싱 + 캐릭터 별칭 매핑. 1h TTL 캐시',
      cost: 'general 입력은 네트워크 0회',
    },
    {
      n: 3,
      label: 'fetch_memory',
      desc: '(guild_id, user_id) → session_id SQLite 영속 매핑. turn 50 / 6h idle 시 자동 회전(요약 → archive → 새 세션)',
      cost: 'history는 Anthropic 세션이 자동 유지',
    },
    {
      n: 4,
      label: 'call_llm · Managed Agents',
      desc: 'claude-haiku-4-5 호스팅 에이전트 호출. system prompt + few-shot 5쌍 + 4가지 방어 규칙',
      cost: 'Anthropic 세션 자동 관리 · 모델 교체 1줄로 가능',
    },
    {
      n: 5,
      label: 'Custom tool 자율 판단',
      desc: 'Claude가 search_player_stats 호출 시 StatsLayoutView 네이티브 카드를 Discord 채널에 직접 post',
      cost: 'last_trace에 판단 과정 기록',
    },
  ],
} as const

export const TECH_STACK = {
  llm: [
    { label: '에이전트 호스팅', value: 'Anthropic Managed Agents (claude-haiku-4-5)' },
    { label: '폴백 백엔드', value: 'Modal Gemma4 LoRA (CHAT_BACKEND=modal)' },
    { label: '오케스트레이션', value: 'LangGraph StateGraph 2-tier (langgraph 1.1.8)' },
    { label: 'Custom Tool', value: 'search_patchnote · search_player_stats · recall_about_user' },
    { label: 'Daily Feed 큐레이터', value: 'claude-sonnet-4-6' },
    { label: 'Voice STT/이해', value: 'Qwen3.5-Omni (OpenAI 호환 API)' },
    { label: 'Voice TTS', value: 'CosyVoice3 (파인튜닝, Modal 배포)' },
  ],
  infra: [
    { label: '런타임', value: 'Python 3.14 · discord.py · anthropic 0.96+' },
    { label: '음성', value: 'discord-ext-voice-recv · davey (DAVE) · webrtcvad' },
    { label: '스토리지', value: 'Firestore (feed_seen 30d TTL · daily_feeds · settings 3컬렉션) · GCS' },
    { label: '컴퓨트', value: 'GCP VM · Cloud Run · Modal' },
    { label: '컨테이너', value: 'Docker — 3컨테이너 (debi-marlene · solo-debi · solo-marlene)' },
    { label: 'CI/CD', value: 'GitHub Actions cron (47분 회피) · Makefile 배포 자동화' },
    { label: '시크릿', value: 'GCP Secret Manager (.env 3종)' },
  ],
  frontend: [
    { label: '대시보드', value: 'React 18 · Vite · TypeScript · Tailwind' },
    { label: '웹패널', value: 'Vite + PWA (vite-plugin-pwa)' },
    { label: '도메인', value: 'debimarlene.com (Cloudflare 캐시)' },
  ],
} as const

export const CASES = [
  {
    no: 1,
    title: 'Modal Gemma4 LoRA → Anthropic Managed Agents 이관',
    problem:
      '자체 호스팅 LoRA의 응답 시간·비용·일관성이 들쭉날쭉 + Modal 크레딧 고갈. 안정적이고 측정 가능한 LLM 백엔드 필요.',
    approach:
      '`CHAT_BACKEND` 환경변수로 modal/managed 2종 백엔드 분기. Managed Agents(claude-haiku-4-5) 채택. Custom tool 2종(search_patchnote·search_player_stats) + 4가지 방어 규칙 system prompt + (guild_id, user_id) 단위 SQLite 세션 영속화.',
    result:
      '본 LLM 평가 보고서에서 Haiku 4.5의 closed-book 정직성(hall 0%) + RAG 결합 안전선(corr 4.87/5) 정량 검증 후 채택. 폴백 가능한 2-tier 아키텍처로 다음 모델 교체 시 동일 측정 프레임워크 재사용 가능.',
    bridge:
      '정량 지표 정의 → 측정 → 모델 교체 → 재측정의 평가 파이프라인 그 자체. 평가 지표 개발 직무와 1:1 대응.',
  },
  {
    no: 2,
    title: 'LangGraph StateGraph 2-tier — 정규식 0.1ms × LLM 분기',
    problem: '모든 사용자 메시지를 LLM에 던지면 비용·지연 폭증. 단순 인사·키워드까지 LLM 호출은 낭비.',
    approach:
      'Tier 1 `classify_intent` (정규식 PATCH_KEYWORDS, LLM 없이 0.1ms) → patch면 `fetch_patchnote` 분기, general이면 `skip_patchnote`. fetch_memory는 patch_context만 컨텍스트에 포함. corrections는 Claude의 `recall_about_user` 도구로 분리.',
    result:
      'general 메시지는 RAG 네트워크 호출 0회 → 평균 응답 시간 100~300ms 단축. 입력 패턴별 비용 분리 측정 가능.',
    bridge:
      '입력 시나리오 자동 분류기를 평가용으로 그대로 이식 → 시나리오별 모델 응답 품질 분리 측정 가능.',
  },
  {
    no: 3,
    title: '솔로봇 identity별 agent 분리 — 토큰·체감 속도 절감',
    problem:
      '쌍둥이 형식("데비: 대사 + 마를렌: 대사")은 항상 두 명을 동시 생성 → 솔로봇(debi 단독·marlene 단독) 운영 시 불필요한 절반 생성 비용 발생.',
    approach:
      '`MANAGED_AGENT_ID_DEBI` / `MANAGED_AGENT_ID_MARLENE` / `MANAGED_AGENT_ID`(unified) 3종 분리. 봇 컨테이너 BOT_IDENTITY 환경변수로 라우팅. 각 agent의 시스템 프롬프트는 단일 페르소나만 생성하도록 변형.',
    result: '솔로봇 응답 토큰 약 절반 절감 + 체감 속도 약 2배. 동일 사용자 질문에 대한 페르소나별 응답 비교 가능.',
    bridge:
      '에이전트 분기 구조와 정량 비용 측정 — 모델·페르소나 비교 평가의 직접 사례.',
  },
  {
    no: 4,
    title: 'Daily AI Feed — Sonnet Curator + Firestore 중복 제거',
    problem:
      '매일 09:00 KST 자동 피드를 위해 Smol AI / GitHub / HF / HN 4소스에서 항목 fetch → 큐레이션 → DM 발송. Opus 큐레이터는 비용 부담, 같은 항목 중복 발송 위험.',
    approach:
      '`scripts/daily_feed.py` + GitHub Actions cron(정각 큐 폭주 회피 47분). 큐레이터 모델 `claude-sonnet-4-6` 채택. Firestore `feed_seen`(30일 TTL) 중복 제거, `daily_feeds`에 적재. 발송은 별도 봇 토큰(나쵸네코)으로 거노 OWNER_ID에 DM.',
    result: 'Opus 대비 큐레이션 비용 큰 폭 절감. 중복 제거로 같은 정보 반복 노출 0. 매일 운영되는 LLM 큐레이션 워크플로우.',
    bridge: '동일 입력에 대한 모델 사이즈별 cost-quality 정량 비교 = 모델 평가 직접 사례.',
  },
  {
    no: 5,
    title: '음성 파이프라인 — DAVE × VAD × Qwen3.5-Omni × CosyVoice3',
    problem:
      'Discord 음성채널 실시간 대화 응답. E2EE 암호화·발화 감지·음성 이해·TTS까지 4단계 파이프라인 필요.',
    approach:
      'discord-ext-voice-recv로 transport 복호화 → davey로 DAVE E2EE 2차 복호화 → discord.opus.Decoder로 PCM → webrtcvad로 발화 감지 → pre-buffer 0.5s 포함 WAV 녹음 → Qwen3.5-Omni API로 키워드 + 응답 생성 → CosyVoice3(Modal 배포) TTS.',
    result: '파이프라인 프로토타입 완성, 안정화 단계. 음성 모델별 응답 품질·지연·음색 정량 비교 데이터 축적.',
    bridge:
      '멀티모달 LLM(Qwen3.5-Omni)·TTS(CosyVoice3) 응답 품질을 정성/정량으로 평가한 직접 경험.',
  },
  {
    no: 6,
    title: 'Settings split-brain 해소 — GCS JSON → Firestore 3컬렉션',
    problem:
      '단일 GCS JSON으로 settings를 관리하니 멀티 컨테이너(debi-marlene + solo-debi + solo-marlene) 사이에서 split-brain 발생. 158서버 중 일부 설정 정합성 깨짐.',
    approach:
      '`scripts/migrate_settings_to_firestore.py`로 GCS JSON을 Firestore 3컬렉션(148 + 23 + 1 docs)으로 분리 마이그레이션. 컨테이너 단위 배포 자동화. command_logs / dashboard_logs / quiz_data 분리.',
    result: '멀티 컨테이너 정합성 회복, 158서버 안정 운영, 사용자 응대·정책 수립까지 1인 운영.',
    bridge:
      '라이브 환경 응답 데이터를 정량 분석한 운영 기반 — LLM 평가가 의지할 데이터 파이프라인 직접 구축.',
  },
] as const

export const COLLAB = {
  title: '커뮤니케이션 국제 디자인 공모전 입상',
  problem: '3인 팀, 졸업 전시 작품을 인쇄 단일 vs 디지털 결합으로 의견 충돌',
  approach:
    '일정·인력·관람객 시나리오를 표로 정리해 두 안을 같은 기준 위에서 비교, 디자인 컨셉을 흐트러뜨리지 않는 선에서 인터랙티브 웹페이지 인터페이스 방향 직접 제안.',
  result: '시각적 일관성과 사용자 흐름을 결합한 결과물로 공모전 입상.',
  bridge:
    '다른 직군과 의견이 충돌할 때 데이터·시나리오 위에서 같은 기준을 만드는 협업 패턴.',
} as const

export const CONTACT = {
  email: 'goenho0613@gmail.com',
  github: 'https://github.com/2rami',
  domain: 'https://debimarlene.com',
  edu: '신구대학교 시각디자인과 졸업 (2026.02)',
} as const
