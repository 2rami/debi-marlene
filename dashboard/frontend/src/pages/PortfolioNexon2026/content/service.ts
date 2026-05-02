/**
 * 넥슨네트웍스 — 게임서비스 채용연계형 인턴 지원용
 * 컨텐츠 SSoT — 실제 debi-marlene 봇 코드 기반
 */

export const HERO = {
  jobCode: 'GAME SERVICE',
  badge: 'NEXON NETWORKS · 게임서비스 채용연계형 인턴 지원',
  title: '158개 서버를 9개월간\n혼자 운영해 본 사람',
  subtitle:
    '데비&마를렌 — 사용자 응대, 이상 호출 차단, 정책 수립, 데이터 기반 개선까지 라이브 LLM 챗봇의 운영 사이드를 1인이 모두 다뤄 온 경험을 게임서비스로 옮깁니다.',
  ctas: [
    { label: 'GitHub · debi-marlene', href: 'https://github.com/2rami/debi-marlene', primary: true },
    { label: 'Live · debimarlene.com', href: 'https://debimarlene.com', primary: false },
  ],
} as const

export const STATS = [
  { label: '운영 중인 Discord 서버', value: '158', unit: '개', sub: 'debi-marlene · 9개월 라이브' },
  { label: 'Firestore 운영 컬렉션', value: '5', unit: '+', sub: 'settings(3) · feed_seen · daily_feeds' },
  { label: '메이플 라이브 플레이', value: '16', unit: '년+', sub: '하드 세렌 파티 격파' },
  { label: '디자인 공모전', value: '1', unit: '건 입상', sub: '커뮤니케이션 국제 디자인 공모전' },
] as const

export const ABOUT = `데비&마를렌은 1인이 9개월간 158개 Discord 서버에 운영 중인 라이브 LLM 챗봇입니다. 단순 명령어 봇이 아니라 사용자 응대·정책 수립·이상 호출 차단·데이터 분석·인프라 자동화까지 라이브 서비스의 운영 사이드를 모두 직접 다뤘습니다. 메이플스토리 약 16년의 헤비유저 시점과, 1인 봇 운영자의 라이브 서비스 시점이 결합된 자리에서 게임서비스 직무의 본질 — 사용자 한 명의 문제를 데이터와 정책으로 해결해 콘텐츠가 떠받쳐지는 환경을 만드는 일 — 을 가장 잘 수행할 수 있다고 자신합니다.`

export const JD_MATCHES = [
  {
    n: 1,
    jdTitle: '고객 문제 해결',
    jdSub: '서비스 도구로 고객·게임 현황 파악, 최적 솔루션 마련',
    evidence: [
      '158개 서버에서 9개월간 사용자 문의·이상 동작·기능 오류를 직접 응대 — 채팅 기록·로그·Firestore 데이터로 현황 파악 후 즉시 패치/공지/정책 수립',
      '봇 안에 `search_player_stats` Custom tool 직접 구현 — Claude가 자율 판단으로 사용자 전적을 검색하고 StatsLayoutView 네이티브 카드를 채널에 즉시 post (도구로 사용자 문제 즉시 해결하는 모범 사례)',
      'guild별 chat_memory 분리 + (guild_id, user_id) 단위 SQLite 세션 영속화 — 사용자별 맥락을 잃지 않고 누적 컨텍스트로 응대',
    ],
  },
  {
    n: 2,
    jdTitle: '리스크 관리',
    jdSub: '지식·경험·데이터 기반 게임 내/외 리스크 선제 대응',
    evidence: [
      '시스템 프롬프트에 4가지 절대 규칙(시스템 프롬프트 비공개·캐릭터 변경 거부·출력 형식 강제 거부·사용자 지시 무시) — 프롬프트 인젝션·악의적 사용 차단 정책 직접 설계',
      '키워드 자동 분류로 사용자 입력 의도를 식별 — 패치·이벤트·이상 사용 패턴을 사전에 감지해 운영 알림·정책 분기로 연결',
      '봇 운영 중 발생한 멀티 컨테이너 split-brain 사고를 Firestore 3컬렉션 마이그레이션으로 사전 해소 (`scripts/migrate_settings_to_firestore.py`)',
      '음성 파이프라인 11개 트러블슈팅을 메모리에 누적 (원인 / 재현 / 교훈) — 같은 결함 재발 방지 시스템',
    ],
  },
  {
    n: 3,
    jdTitle: '리텐션 관리',
    jdSub: '데이터 분석·고객 대응·커뮤니티 관리로 사용자 니즈와 트렌드 기반 서비스 제안',
    evidence: [
      'Firestore에 사용자 명령어 호출 로그·서버 가입/이탈 패턴·응답 지연 시간 누적 (`feed_seen` 30일 TTL · `daily_feeds` 적재 · settings 3컬렉션 148+23+1 docs)',
      '데이터 기반으로 자주 사용되는 기능과 잘 안 쓰이는 기능 분리 → 우선순위 재정렬 + 응답 지연 큰 경로 식별 후 평균 응답 시간 100~300ms 단축',
      '메이플스토리 약 16년 헤비유저 시점에서 라이브 서비스가 패치·이벤트·신규 직업·시즌 콘텐츠로 어떻게 사용자 잔존율을 만드는지 사용자 입장에서 추적해 옴',
      '봇 운영 중 사용자 피드백을 정량/정성으로 비교(빠른 응답 vs 풍부한 캐릭터 톤) 후, 사용 빈도·맥락별로 응답 시간·길이·톤을 다르게 조정',
    ],
  },
  {
    n: 4,
    jdTitle: '서비스 인프라 기획·개선',
    jdSub: '성공적 라이브 서비스 제공을 위한 서비스 도구 기획·개선',
    evidence: [
      'AI 응답 백엔드 안정화 — 응답 시간·운영 비용을 정량 측정해 158서버 라이브 환경에서도 일관된 사용자 경험을 유지',
      '솔로봇(debi 단독·marlene 단독) 운영 환경별로 응답 정책을 분리 — 채널 성격에 맞춰 응답 강도·속도를 다르게 조정',
      'Daily AI Feed 자동 파이프라인(`scripts/daily_feed.py` + GitHub Actions cron 47분 회피) — Smol AI/GitHub/HF/HN 4소스 fetch + Sonnet 큐레이터 + Firestore 중복 제거 + DM 발송',
      '대시보드(React 18 · Vite · TS · Tailwind) + 웹패널(Vite + PWA) — 봇 설정 직접 편집 가능한 운영 인프라 1인 구축',
      'GCP Secret Manager(.env 3종) · GitHub Actions cron · Makefile 배포 자동화 — 인프라 운영 정합성 확보',
    ],
  },
  {
    n: 5,
    jdTitle: '정책 수립',
    jdSub: '공정·투명한 라이브 서비스를 위한 정책 수립·개선',
    evidence: [
      '봇 시스템 프롬프트의 4가지 절대 규칙 — 운영 정책의 LLM 도메인 적용 사례',
      '솔로봇 지정 채널만 응답 + 3단계 확률 응답 시스템 — 사용자 환경별로 운영 강도 조정하는 정책',
      '봇 토큰·환경변수·시크릿을 GCP Secret Manager로 단일화 + 노션 평문 저장 폐기 — 보안 정책 직접 수립',
      'Discord LayoutView V2 채택(Container가 Embed 대체) — 서비스 출력 형식 정책 결정 사례',
    ],
  },
] as const

export const PREFERRED = [
  {
    n: 1,
    jdTitle: '데이터 추출·가공·분석 능숙',
    evidence: [
      'Firestore 운영 데이터(feed_seen·daily_feeds·settings·command_logs·dashboard_logs·quiz_data) 직접 분석',
      'Discord guild별 사용 로그를 SQLite 세션 영속화 + 마크다운 보고서 정리',
      '봇 응답 지연 패턴을 정량 측정해 LLM 호출 회피 분기(`skip_patchnote`) 도입',
    ],
  },
  {
    n: 2,
    jdTitle: '다양한 AI 도구 활용 효율화 경험',
    evidence: [
      'Anthropic Managed Agents · Modal · OpenAI 호환 API · CosyVoice3 · Qwen3.5-Omni 다중 LLM/멀티모달 운영',
      'AI 코딩 도구 일상적 활용으로 1인 풀스택 운영 가능한 자동화 워크플로우 구축',
      'Daily AI Feed 큐레이터 모델 비교(Sonnet vs Opus) → 비용·품질 트레이드오프 정량 측정',
    ],
  },
  {
    n: 3,
    jdTitle: '외국어',
    evidence: [
      '영어: Anthropic Console · GCP Console · GitHub 이슈/PR 등 영문 운영 환경 일상적 사용',
      '일본어: 학습 진행 중 (관심사). 블루아카이브 일판·메이플 일판 콘텐츠 접근 가능',
    ],
  },
] as const

export const ELIGIBILITY = {
  headline: '메이플스토리 약 16년 · 프로즌샤 · 하드 세렌 파티 격파',
  body:
    '게임서비스 직무 이해도 / 새로운 게임 적극 학습 / 논리 글쓰기 / 문제 해결 / 협업 / MS-OFFICE 모두 충족. 라이브 봇 운영 9개월 + 메이플 헤비유저 16년의 사용자/운영자 양쪽 시점.',
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

export const CASES = [
  {
    no: 1,
    title: '158서버 split-brain 해소 — GCS JSON → Firestore 3컬렉션 마이그레이션',
    problem:
      '단일 GCS JSON으로 settings를 관리하니 멀티 컨테이너(debi-marlene + solo-debi + solo-marlene) 사이에서 split-brain 발생. 158서버 중 일부 설정 정합성 깨짐 → 사용자 신뢰 손상 가능.',
    approach:
      '`scripts/migrate_settings_to_firestore.py`로 GCS JSON을 Firestore 3컬렉션(148 + 23 + 1 docs)으로 분리. command_logs / dashboard_logs / quiz_data 별도 분리. 컨테이너 단위 배포 자동화로 정합성 보장.',
    result: '멀티 컨테이너 정합성 회복 + 158서버 안정 운영 + 운영 정책 단일 출처 확립.',
    bridge: '라이브 서비스의 운영 안정성을 1인이 책임지고 해결한 직접 사례.',
  },
  {
    no: 2,
    title: '사용자 문제 자동 해결 — search_player_stats Custom tool',
    problem: '봇 사용자가 매번 `/전적` 명령어를 직접 입력해야 자기 게임 전적을 봄. 자연어 질문으론 해결 불가능.',
    approach:
      'Anthropic Managed Agents에 `search_player_stats` Custom tool 등록. Claude가 사용자 자연어 의도(예: "내 전적 좀 보여줘")를 자율 판단해 도구 호출 + StatsLayoutView 네이티브 카드를 채널에 직접 post.',
    result: '사용자 의도 → 도구 호출 → UI 출력까지 한 번에 자동화. 운영자 개입 불필요.',
    bridge: '운영팀 부담을 줄이고 사용자 만족을 동시에 끌어올린 자동화 사례.',
  },
  {
    no: 3,
    title: 'Daily AI Feed — 자동 큐레이션 + 정중복 제거',
    problem:
      '4개 소스(Smol AI / GitHub / HF / HN)에서 매일 항목을 fetch → 큐레이션 → DM 발송하는 워크플로우. 같은 항목을 30일 안에 다시 보내는 정중복 위험.',
    approach:
      '`scripts/daily_feed.py` + GitHub Actions cron(0 UTC = 09:00 KST, 정각 큐 폭주 회피 47분). Firestore `feed_seen` 30일 TTL로 중복 제거. 큐레이터 모델 `claude-sonnet-4-6` 채택해 Opus 대비 비용 절감. 별도 봇 토큰(나쵸네코)으로 거노 OWNER_ID에 DM.',
    result: '매일 자동 운영되는 큐레이션 파이프라인. 중복 0회 + 모델 비용 큰 폭 절감.',
    bridge: '리텐션 관리(매일 사용자에게 가치 전달) + 비용 효율 운영의 직접 사례.',
  },
  {
    no: 4,
    title: '운영 환경별 응답 정책 분리 — 솔로봇 채널 정책',
    problem:
      '서버·채널 성격이 다양한데 같은 응답 강도로 운영하면 일부 채널은 봇이 시끄럽고, 일부는 반응이 느려 사용자 경험이 어긋남.',
    approach:
      '봇 identity(debi 단독·marlene 단독·통합)를 운영 환경별로 분리하고, 솔로봇은 지정 채널만 응답 + 3단계 확률 응답 시스템 적용. 운영 강도를 채널 단위로 조정 가능한 정책 구조 수립.',
    result: '동일 사용자 경험을 더 낮은 운영 부하로 전달. 채널 성격에 맞춘 응답 정책으로 사용자 만족·체감 속도 모두 개선.',
    bridge: '서비스 운영 정책을 데이터·환경 단위로 분기해 결정한 사례.',
  },
  {
    no: 5,
    title: '협업 — 커뮤니케이션 국제 디자인 공모전 입상',
    problem: '3인 팀, 졸업 전시 작품을 인쇄 단일 vs 디지털 결합으로 의견 충돌',
    approach:
      '일정·인력·관람객 시나리오를 표로 정리해 두 안을 같은 기준 위에서 비교, 디자인 컨셉을 흐트러뜨리지 않는 선에서 인터랙티브 웹페이지 인터페이스 방향 직접 제안.',
    result: '시각적 일관성과 사용자 흐름을 결합한 결과물로 공모전 입상.',
    bridge: '다양한 이해관계자가 얽힌 운영 환경에서 같은 기준을 만드는 협업 패턴.',
  },
] as const

export const CONTACT = {
  email: 'goenho0613@gmail.com',
  github: 'https://github.com/2rami',
  domain: 'https://debimarlene.com',
  edu: '신구대학교 시각디자인과 졸업 (2026.02)',
} as const
