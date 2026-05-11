/**
 * 넥슨 플랫폼본부 — 게임 도메인 LLM 평가 어시스턴트 (인턴) 지원용
 * 컨텐츠 SSoT — 실제 debi-marlene 봇 코드 기반
 */

export const HERO = {
  jobCode: 'LLM EVALUATOR',
  badge: 'NEXON · 플랫폼본부 · LLM 평가 어시스턴트 인턴 지원',
  titleLines: ['안녕하세요.', '디스코드 LLM 봇을', '직접 운영하는 개발자 게이머입니다.'],
  // 호환성용 평문 (BlurText 등 일부 컴포넌트가 string을 기대)
  title: '안녕하세요. 디스코드 LLM 봇을 직접 운영하는 개발자 게이머입니다.',
  highlightWord: 'LLM 봇',
  subtitle:
    '데비&마를렌 — 1인 운영 LLM 챗봇. 9개월째 158개 Discord 서버에서 라이브로 돌아갑니다. 게임 도메인 경험과 LLM 운영자의 평가 감각을 함께 보여드립니다.',
  meta: [
    { label: 'ROLE', value: 'LLM 평가 어시스턴트 인턴' },
    { label: 'COMPANY', value: '넥슨 · 플랫폼본부' },
    { label: 'PRODUCT', value: 'debi-marlene' },
    { label: 'DEPLOYED', value: '158 servers · 9 months' },
    { label: 'STACK', value: 'LangGraph · Anthropic · GCP' },
  ],
  ctas: [
    { label: 'REPORT · LLM 평가 8p PDF', href: '/llm_eval_report.pdf', primary: true },
    { label: 'GitHub · debi-marlene', href: 'https://github.com/2rami/debi-marlene', primary: false },
    { label: 'Live · debimarlene.com', href: 'https://debimarlene.com', primary: false },
  ],
} as const

export const STATS = [
  { label: '운영 중인 Discord 서버', value: '158', unit: '개', sub: 'debi-marlene · 9개월 라이브' },
  { label: '메이플 플레이 경력', value: '16', unit: '년+', sub: '하드 세렌 파티 격파' },
  { label: 'LLM 평가 자동 채점', value: '520', unit: '개', sub: '모델 4종 × 게임 2종 = 답변 520개를 자동 채점 (PDF 8p)' },
  { label: 'Tier 1 정규식 분류', value: '0.1', unit: 'ms', sub: 'classify_intent · LLM 호출 없이 키워드 분류' },
] as const

export const ABOUT = `데비&마를렌은 이터널 리턴 쌍둥이 실험체를 모티브로 한 한국어 캐릭터 챗봇입니다. 1인이 기획·개발·배포·운영을 전부 맡아 9개월간 158개 Discord 서버에서 운영 중입니다. 단순 명령어 봇이 아닙니다. LangGraph StateGraph 2단 에이전트, Anthropic Managed Agents(claude-haiku-4-5) 호스팅, Claude가 스스로 판단해 도구를 호출하고 Discord UI를 직접 만들어내는 구조, 패치노트 검색(RAG), 음성 채널 실시간 응답 파이프라인(DAVE → VAD → Qwen3.5-Omni → CosyVoice3)을 한 봇에 통합한 LLM 시스템입니다. 매일 사용자 응답 데이터를 숫자(점수·환각률·비용)와 직접 읽기 두 가지로 점검합니다. 모델·프롬프트·few-shot·세션 회전 정책을 바꿀 때마다 톤이 흔들리는 정도, 거짓말하는 비율, 비용이 어떻게 변하는지 추적해 왔습니다. 이 운영 검증 경험을 넥슨의 LLM 평가 직무로 이어 가고 싶습니다.`

export const JD_MATCHES = [
  {
    n: 1,
    jdTitle: '게임 도메인 특화 LLM 벤치마크 구성',
    jdSub: '패치노트, 기획서, 가이드 기반 시나리오·벤치마크 질문 설계',
    evidence: [
      '메이플스토리 약 16년 (2009 ~ ). 모험가 마법사 → 메카닉 → 비숍 → 썬콜 본캐로 6차전직까지 실제로 플레이하면서 거쳐 왔습니다. 군 전역 후 검은 마법사 직접 격파, 하드 세렌 파티 격파, 신직업도 거의 다 플레이. 라이트 유저는 잘 모르는 직업·보스·유니온 깊이까지 알기 때문에 평가용 질문을 직접 만들 수 있습니다',
      '봇 안에 `patchnote_search.py`로 이터널 리턴 공식 사이트 패치노트 RAG 직접 구현. 캐릭터 별칭 매핑(뎁마/데비/마를렌 → 데비&마를렌), 섹션 파싱(캐릭터·아이템·증강체), 1시간 TTL 캐시 포함',
      'LangGraph `classify_intent`가 정규식으로 도메인 키워드(패치/너프/버프/변경/밸런스/상향/하향/OP)를 0.1ms 만에 자동 분류. LLM을 부르지 않고 처리. 같은 코드를 평가용 질문 분류기로 그대로 옮겨 쓸 수 있습니다',
      '메이플 외에 블루아카이브·이터널리턴·더 파이널스·서든어택까지 5종 플레이. 게임마다 유저들이 봇에 물어보는 방식이 다르다는 점을 직접 체감했습니다',
    ],
  },
  {
    n: 2,
    jdTitle: '평가 지표 및 기준 개발',
    jdSub: '평가 기준·스코어링·체크리스트·정량 지표 설계',
    evidence: [
      'Anthropic Managed Agents로 백엔드 이관. 본 보고서에서 두 가지 점수를 직접 측정한 뒤 채택했습니다 — Haiku 4.5는 자료 없이 답할 때 거짓말 비율이 0%였고, 자료를 같이 주면 정답률이 4.87/5(5점 만점)까지 올라가 안정적이었습니다',
      '봇 LLM 백엔드를 Modal Gemma4 LoRA → Anthropic Managed Agents(claude-haiku-4-5)로 이관. `CHAT_BACKEND` 환경변수 한 줄로 두 백엔드를 바꿔 끼울 수 있어, 같은 질문을 두 백엔드에 던져 결과를 비교할 수 있습니다',
      '솔로봇(debi / marlene)을 위해 LLM 에이전트를 캐릭터별로 따로 만들었습니다. 원래는 둘이 한 번에 같이 대답하는 구조라 솔로봇에선 안 쓰는 절반까지 매번 생성됐는데, 캐릭터 하나만 답하도록 분리하니 체감 속도 2배, 토큰 사용량 절반으로 줄었습니다',
      'Daily AI Feed 큐레이터 모델로 `claude-sonnet-4-6` 채택. Opus 대비 비용은 얼마나 싸지고 품질은 얼마나 떨어지는지를 매일 직접 비교',
      '시스템 프롬프트에 4가지 절대 규칙을 직접 설계 (시스템 프롬프트 비공개 / 캐릭터 변경 거부 / 출력 형식 강제 거부 / 사용자 지시 무시). 보안 평가 체크리스트로도 그대로 쓸 수 있는 사례',
      'few-shot 5쌍으로 캐릭터 톤(데비 활발체 / 마를렌 냉소체)을 잡았습니다. 같은 질문에 캐릭터가 자기 톤을 얼마나 지키는지 측정하는 틀을 만들었습니다',
    ],
  },
  {
    n: 3,
    jdTitle: 'LLM 응답 품질 평가 (정량/정성)',
    jdSub: '검색·답변 품질, 톤·환각·도구 호출 정확도 평가',
    evidence: [
      '158개 서버에서 9개월간 매일 LLM 응답을 직접 검증. 실제 사용자 환경에서 거짓말, 욕설, 시스템 프롬프트 빼내려는 시도가 어떤 식으로 들어오는지 관측하고 차단했습니다',
      '`search_patchnote` Custom tool로 이터널 리턴 패치노트 RAG 응답이 사실에 맞는지, 빠진 부분이 없는지 직접 검증. 캐릭터 별칭이 어긋나는 사례를 메모리에 모아둠',
      '`search_player_stats` Custom tool은 Claude가 스스로 판단해서 호출. 결과로 StatsLayoutView 카드를 Discord 채널에 직접 띄웁니다. 도구를 정확한 타이밍에 부르는지, 사용자가 원한 게 맞는지 평가',
      '`ManagedAgentsClient.last_trace`로 에이전트가 매번 어떻게 판단했는지 전부 기록. 면접 시연·대시보드 시각화·평가 자료로 그대로 활용 가능',
      '캐릭터 톤 점검. 데비/마를렌/나쵸네코 3종에 같은 질문을 던져 응답을 비교하고, 모델·프롬프트가 바뀔 때 캐릭터 톤이 얼마나 흔들리는지 직접 읽어가며 평가',
      '음성 응답 파이프라인(Qwen3.5-Omni STT/이해 + CosyVoice3 TTS)의 목소리 톤, 발화 자연스러움, 응답 지연을 직접 듣고 + 숫자로 검증',
      '`(guild_id, user_id) → session_id` SQLite 영속 매핑. 50턴 또는 6시간 동안 대화가 없으면 자동 회전(이전 대화 요약 → 보관함으로 옮김 → 새 세션 시작). 누적된 대화 길이가 응답 품질에 주는 영향을 추적',
    ],
  },
  {
    n: 4,
    jdTitle: '결과 분석 및 보고서 정리',
    jdSub: '평가 결과 분석·보고서·인사이트 전달',
    evidence: [
      {
        text: '이번 지원에 맞춰 직접 작성한 LLM 평가 보고서(PDF 8p). 작은 사이즈 모델 4종(Gemma4+LoRA / EXAONE 3.5 / Haiku 4.5 / GPT-5.4-mini)에 게임 2종(메이플 / 이터널 리턴 11.0)을 시켰습니다. 자료 없이 답하기, 자료 주고 답하기, 여러 번 이어지는 대화 10세트 — 합쳐서 답변 520개가 나왔고, 이걸 GPT-4o-mini가 채점관 역할로 자동 채점',
        highlight: 'LLM 평가 보고서(PDF 8p)',
        report: {
          title: 'LLM 평가 보고서 v2 — Self-host vs Commercial Small',
          subtitle: '메이플 + ER 도메인 · closed/open + multi-turn · 520 응답 · 8p',
          insights: [
            '자료를 같이 주면 점수가 +3점씩 일관되게 오름 (모델 4종 공통)',
            'Haiku 4.5는 자료 없이 답할 때 거짓말 비율 0% — 가장 정직',
            '어설프게 학습된 도메인이 가장 위험 (같은 모델인데 거짓말 0% ↔ 70%)',
            '자체 호스팅 LoRA = 상용 소형 모델 동등 (한 번 묻고 답하는 경우)',
            '여러 턴 이어지는 대화에선 LoRA가 약함 — 그래서 봇은 한 번 질문 받고 답하는 방식으로 의도적 한정',
          ],
          pdfHref: '/llm_eval_report.pdf',
        },
      },
      '평가 결과를 봇 운영 결정으로 바로 연결. 자료 없이 답할 때 거짓말 비율 0%, 자료 주면 +3점 효과를 보고 봇에 Haiku 4.5 + search_patchnote 검색 도구를 도입. 여러 턴 대화에서 LoRA가 약하다는 결과(1.30 vs 2.60)를 보고, 봇은 한 번 질문 받고 답하는 방식으로 한정',
      '봇 운영 중 생긴 트러블슈팅·구조 변경·실험 결과를 마크다운 메모리에 모으는 중. "원인 / 재현 / 교훈" 형식으로 통일해 다음 의사결정 때 다시 꺼내 씁니다',
      '시각디자인 전공 4년의 사용자 경험 훈련. 데이터 → 인사이트 → 의사결정으로 이어지는 시각 자료를 직접 제작 (이번 PDF 보고서 표지·차트·결론 페이지 포함)',
      '커뮤니케이션 국제 디자인 공모전 입상. 직군 간 의견이 부딪칠 때 일정·인력·시나리오를 표로 정리해 같은 기준을 만들고, 그 위에서 합의를 끌어낸 경험이 있습니다',
    ],
  },
] as const

export const ELIGIBILITY = {
  headline: '메이플 16년 · 빅뱅·5차·V·6차 패치를 매번 직접 겪어 온 유저',
  body:
    '2009년경 모험가 마법사로 시작했습니다. 빅뱅 이후 메카닉으로 본격 진입했고, 신직업이 나올 때마다 거의 다 플레이했습니다. 2016년 5차전직 V 매트릭스 공개와 함께 썬콜로 자유전직, 지금까지 본캐로 운영 중입니다. 2018년 스토리 속 인물이던 검은 마법사가 보스로 출시됐고, 모험가들의 염원이 모인 그 시기를 함께했습니다. 군 전역 후 6차전직과 함께 본격적으로 강해져 검은 마법사를 직접 격파했고, 전투력 1억과 하드 세렌 파티 격파까지 도달했습니다. 단순히 만렙을 찍은 게 아니라, 빅뱅·5차·V·6차로 이어진 큰 패치를 매번 유저로서 직접 거쳐 온 경험입니다.',
} as const

export const CHARACTER = {
  name: '프로즌샤',
  server: '오로라',
  job: '아크메이지(썬,콜)',
  level: 284,
  experience: '약 16년 (2009 ~ )',
  achievement: {
    title: '하드 세렌 파티 격파',
    sub: '메이플 최상위 콘텐츠 · 6차전직 이후 도달',
  },
} as const

export const GAMES = [
  {
    title: '메이플스토리',
    period: '2009 ~ 약 16년',
    detail: '오로라 · 프로즌샤 · 아크메이지(썬,콜) · 검은 마법사 보스 격파 · 하드 세렌 파티 격파',
  },
  { title: '블루아카이브', period: '약 3년', detail: '넥슨게임즈 자회사 IP. 만렙 유지, 메인·이벤트 스토리 완주' },
  {
    title: '이터널리턴',
    period: '1년+',
    detail: '봇 캐릭터(데비&마를렌)의 본 IP — 패치노트 RAG·캐릭터 시스템·증강체까지 사용자 시점 학습',
  },
  { title: '더 파이널스', period: '시즌 단위', detail: 'Embark Studios (넥슨 자회사). 친구들과 라이트 플레이' },
  { title: '서든어택', period: '학창 시절', detail: '넥슨 본사 IP. 친구들과 함께한 입문 FPS' },
] as const

export const ARCHITECTURE = {
  title: 'debi-marlene 아키텍처 — 입력부터 응답까지',
  steps: [
    {
      n: 1,
      label: 'Tier 1 · classify_intent',
      desc: '정규식으로 0.1ms 분류. 패치/너프/버프/변경/밸런스/상향/하향/OP 키워드를 보고 patch vs general 판정',
      cost: 'LLM 호출 없음',
    },
    {
      n: 2,
      label: 'fetch_patchnote · search_patchnote tool',
      desc: 'patch intent일 때만 ER 공식 사이트에서 패치노트 fetch. 섹션 파싱과 캐릭터 별칭 매핑까지 처리. 1h TTL 캐시',
      cost: 'general 입력은 네트워크 0회',
    },
    {
      n: 3,
      label: 'fetch_memory',
      desc: '(guild_id, user_id) → session_id SQLite 영속 매핑. turn 50 / 6h idle 시 자동 회전 (요약 → archive → 새 세션)',
      cost: 'history는 Anthropic 세션이 자동 유지',
    },
    {
      n: 4,
      label: 'call_llm · Managed Agents',
      desc: 'claude-haiku-4-5 호스팅 에이전트 호출. system prompt + few-shot 5쌍 + 4가지 방어 규칙 적용',
      cost: 'Anthropic 세션 자동 관리. 모델 교체는 1줄로 가능',
    },
    {
      n: 5,
      label: 'Custom tool 자율 판단',
      desc: 'Claude가 search_player_stats를 호출하면 StatsLayoutView 네이티브 카드를 Discord 채널에 직접 발행',
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
      '자체 호스팅 LoRA의 응답 시간·비용·일관성이 들쭉날쭉했습니다. Modal 크레딧도 고갈. 안정적이고 측정 가능한 LLM 백엔드가 필요했습니다.',
    approach:
      '`CHAT_BACKEND` 환경변수로 modal/managed 두 백엔드를 분기. Managed Agents(claude-haiku-4-5) 채택. Custom tool 2종(search_patchnote·search_player_stats), 4가지 방어 규칙 system prompt, (guild_id, user_id) 단위 SQLite 세션 영속화까지 함께 도입.',
    result:
      '본 평가 보고서에서 Haiku 4.5의 두 가지 점수를 직접 검증한 뒤 채택했습니다. 자료 없이 답할 때 거짓말 비율 0%였고, 자료를 같이 주면 정답률이 4.87/5(5점 만점)까지 올라가 안정적이었습니다. 두 백엔드를 갈아끼울 수 있는 구조라, 다음에 모델을 바꿔도 같은 측정 방식을 그대로 다시 쓸 수 있습니다.',
    bridge:
      '점수 기준 정의 → 측정 → 모델 교체 → 재측정. 이게 평가 파이프라인 그 자체이고, 평가 지표 개발 직무와 1:1로 맞물립니다.',
  },
  {
    no: 2,
    title: 'LangGraph StateGraph 2-tier — 정규식 0.1ms × LLM 분기',
    problem: '모든 사용자 메시지를 LLM에 던지면 비용과 응답 지연이 폭증합니다. 단순 인사·키워드까지 LLM을 부르는 건 낭비입니다.',
    approach:
      '1단(`classify_intent`)에서 정규식(PATCH_KEYWORDS)으로 0.1ms 만에 분류. 패치 관련 질문이면 `fetch_patchnote`로 빠지고, 그 외 일반 잡담은 검색을 건너뜁니다. 대화 기록은 패치 맥락만 컨텍스트에 넣고, 사용자 정보 정정은 Claude의 `recall_about_user` 도구로 따로 분리했습니다.',
    result:
      '일반 잡담 메시지에선 검색용 네트워크 호출이 0회. 평균 응답 시간이 100~300ms 단축됐고, 메시지 종류별 비용을 분리해 측정할 수 있습니다.',
    bridge:
      '같은 분류기 코드를 평가 파이프라인에 그대로 옮기면, 질문 유형별로 모델 응답 품질을 나눠서 측정할 수 있습니다.',
  },
  {
    no: 3,
    title: '솔로봇용으로 LLM 에이전트를 캐릭터별로 분리 — 토큰·체감 속도 절감',
    problem:
      '원래는 쌍둥이 형식("데비: 대사 + 마를렌: 대사")이라 항상 두 명이 같이 답합니다. 그런데 솔로봇(데비만 / 마를렌만 도는 봇)에선 안 쓰는 절반까지 매번 생성돼서 비용이 낭비됐습니다.',
    approach:
      'LLM 에이전트를 3종(`MANAGED_AGENT_ID_DEBI` / `MANAGED_AGENT_ID_MARLENE` / `MANAGED_AGENT_ID` 통합)으로 분리. 봇 컨테이너의 BOT_IDENTITY 환경변수로 어느 에이전트를 부를지 정하게 했습니다. 각 에이전트의 시스템 프롬프트도 캐릭터 한 명만 답하도록 따로 작성.',
    result: '솔로봇 응답 토큰을 약 절반 줄였고, 체감 속도는 약 2배로 빨라졌습니다. 같은 질문에 캐릭터별로 어떻게 답하는지 비교도 가능합니다.',
    bridge:
      '에이전트를 캐릭터별로 따로 만들어 비용·속도 차이를 직접 측정해 본 경험. 모델·캐릭터 비교 평가에 그대로 적용됩니다.',
  },
  {
    no: 4,
    title: 'Daily AI Feed — Sonnet Curator + Firestore 중복 제거',
    problem:
      '매일 09:00 KST 자동 피드를 위해 Smol AI / GitHub / HF / HN 4소스에서 항목을 fetch해 큐레이션 후 DM으로 보냅니다. Opus 큐레이터는 비용 부담이 크고, 같은 항목이 중복 발송될 위험도 있었습니다.',
    approach:
      '`scripts/daily_feed.py` + GitHub Actions cron(정각 큐 폭주 회피용 47분 트리거). 큐레이터 모델은 `claude-sonnet-4-6` 채택. Firestore `feed_seen`(30일 TTL)로 중복 제거하고 `daily_feeds`에 적재. 발송은 별도 봇 토큰(나쵸네코)으로 거노 OWNER_ID에 DM.',
    result: 'Opus 대비 큐레이션 비용을 큰 폭으로 절감했습니다. 중복 제거 덕분에 같은 정보 반복 노출은 0. 매일 돌아가는 LLM 큐레이션 워크플로우입니다.',
    bridge: '같은 입력에 대해 모델 사이즈별 cost-quality 트레이드오프를 매일 직접 비교하는 워크플로우.',
  },
  {
    no: 5,
    title: '음성 파이프라인 — DAVE × VAD × Qwen3.5-Omni × CosyVoice3',
    problem:
      'Discord 음성채널에서 실시간 대화 응답이 필요했습니다. Discord 음성은 두 단계로 암호화돼 있어(전송 구간 + DAVE 종단간 암호화), 풀어내고 → 발화 감지 → 음성 이해 → 음성 합성까지 4단계 파이프라인이 필요합니다.',
    approach:
      'discord-ext-voice-recv로 1차 암호화 해제 → davey로 DAVE 2차 암호화 해제 → discord.opus.Decoder로 PCM 음성 데이터로 변환 → webrtcvad로 사용자가 말하는 구간 감지 → 발화 시작 0.5초 전부터 WAV로 녹음 → Qwen3.5-Omni API로 키워드 추출과 응답 생성 → CosyVoice3(Modal 배포) 음성 합성으로 마무리.',
    result: '파이프라인 프로토타입은 완성, 현재 안정화 단계. 음성 모델별로 응답 품질·지연·목소리 톤을 비교한 데이터를 쌓는 중입니다.',
    bridge:
      '음성·텍스트를 같이 다루는 LLM(Qwen3.5-Omni)과 음성 합성 모델(CosyVoice3)의 응답 품질을 직접 듣고 + 숫자로 평가한 경험.',
  },
  {
    no: 6,
    title: '서버 설정 동기화 깨짐 해결 — GCS JSON → Firestore 3컬렉션',
    problem:
      '서버 설정을 GCS의 단일 JSON 파일로 관리했는데, 컨테이너 3개(debi-marlene + solo-debi + solo-marlene)가 각자 다르게 읽고 쓰면서 같은 서버 설정이 컨테이너마다 어긋나는 문제가 생겼습니다. 158서버 중 일부에서 설정이 안 맞기 시작했습니다.',
    approach:
      '`scripts/migrate_settings_to_firestore.py`로 GCS JSON을 Firestore 3컬렉션(148 + 23 + 1 docs)으로 분리 마이그레이션. 컨테이너 단위 배포를 자동화. command_logs / dashboard_logs / quiz_data도 분리했습니다.',
    result: '컨테이너 3개의 설정이 다시 맞아 들어갔고, 158서버를 안정적으로 운영 중. 사용자 응대와 운영 정책까지 1인이 맡고 있습니다.',
    bridge:
      '실제 서비스 응답 데이터를 숫자로 분석해 온 운영 기반. LLM 평가가 기대고 있어야 하는 데이터 파이프라인을 직접 만들어 본 경험입니다.',
  },
] as const

export const COLLAB = {
  title: '커뮤니케이션 국제 디자인 공모전 입상',
  problem: '3인 팀에서 졸업 전시 작품을 "인쇄 단일" vs "디지털 결합"으로 두고 의견이 갈렸습니다.',
  approach:
    '일정·인력·관람객 시나리오를 표로 정리해 두 안을 같은 기준 위에서 비교했습니다. 디자인 컨셉을 흐트러뜨리지 않는 선에서 인터랙티브 웹페이지 인터페이스 방향을 직접 제안.',
  result: '시각적 일관성과 사용자 흐름을 결합한 결과물로 공모전에 입상했습니다.',
  bridge:
    '다른 직군과 의견이 충돌할 때 데이터·시나리오 위에서 같은 기준을 만드는 협업 방식.',
} as const

export const CONTACT = {
  email: 'goenho0613@gmail.com',
  github: 'https://github.com/2rami',
  domain: 'https://debimarlene.com',
  edu: '신구대학교 시각디자인과 졸업 (2026.02)',
} as const
