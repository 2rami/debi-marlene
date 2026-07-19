/**
 * 넥슨 AI본부 메이플AX실 — 웹 프론트엔드 엔지니어 (인턴) 지원용
 * 컨텐츠 SSoT — kasaterm(Rust GPU 터미널) · debi-marlene 대시보드 · 이 포트폴리오 자체 기반
 * 공고: careers.nexon.com/recruit/10027
 */

export const HERO = {
  jobCode: 'WEB FRONTEND',
  badge: 'NEXON · AI본부 메이플AX실 · 웹 프론트엔드 엔지니어 인턴 지원',
  titleLines: ['안녕하세요.', '생성형 AI 제작 도구를', '브라우저에서 직접 만드는 프론트엔드입니다.'],
  // 호환성용 평문 (BlurText 등 일부 컴포넌트가 string을 기대)
  title: '안녕하세요. 생성형 AI 제작 도구를 브라우저에서 직접 만드는 프론트엔드입니다.',
  highlightWord: '제작 도구',
  subtitle:
    'Rust로 GPU 터미널을 짜고, React·Vite로 라이브 서비스를 굴리고, 지금 보고 계신 이 페이지까지 — 디자인 설계와 프론트엔드 구현을 한 사람이 합니다.',
  meta: [
    { label: 'ROLE', value: '웹 프론트엔드 엔지니어 인턴' },
    { label: 'TEAM', value: '넥슨 · AI본부 메이플AX실' },
    { label: 'FOCUS', value: '생성형 AI 제작 도구 · 3D 렌더 · 리치 UI' },
    { label: 'STACK', value: 'React · Vite · TS · three.js · GSAP' },
    { label: 'ALSO', value: 'Rust · wgpu — kasaterm GPU 터미널' },
  ],
  ctas: [
    { label: 'GitHub · 2rami', href: 'https://github.com/2rami', primary: true },
    { label: 'Live · debimarlene.com', href: 'https://debimarlene.com', primary: false },
    { label: '이 페이지가 곧 포트폴리오', href: 'https://debimarlene.com/portfolio/nexon/frontend', primary: false },
  ],
} as const

export const STATS = [
  { label: 'GPU 터미널 메모리 최적화', value: '113', unit: 'MB', sub: 'kasaterm — 1.25GB에서 약 91% 절감한 렌더 최적화' },
  { label: '라이브 React 서비스 운영', value: '9', unit: '개월+', sub: 'debimarlene.com 대시보드·웹패널 (Vite·TS·Tailwind)' },
  { label: '직접 구성한 3D·스크롤 엔진', value: '3', unit: '종', sub: '이 페이지 — three.js · GSAP ScrollTrigger · Lenis' },
  { label: '시각디자인 → 프론트엔드', value: '4', unit: '년', sub: '디자인 설계와 구현을 한 사람이 (디자이너 출신)' },
] as const

export const ABOUT = `저는 디자이너 출신 프론트엔드 엔지니어입니다. 시각디자인 4년을 전공한 뒤, 화면을 그리는 데서 멈추지 않고 직접 구현까지 하고 싶어 프론트엔드로 넘어왔습니다. Rust로 GPU 터미널(kasaterm)을 밑바닥부터 혼자 짜면서 렌더링 파이프라인과 성능 최적화를 다뤘고, React·Vite·TypeScript로 158개 Discord 서버 봇의 운영 대시보드를 9개월째 라이브로 굴리고 있습니다. 지금 보고 계신 이 포트폴리오 페이지도 React 19 + Vite + TypeScript로, GSAP·Lenis·three.js·framer-motion을 직접 엮어 만들었습니다. MCP·hook·서브에이전트로 개발 하네스를 직접 구축해, 생성형 AI 모델을 실제 인터페이스에 연결하는 일을 반복해 왔습니다. 메이플AX실이 만드는 "브라우저에서 시각 요소를 자유롭게 편집하고 실시간으로 협업하는 생성형 AI 제작 도구"는 제가 이미 손으로 만들어 온 것과 정확히 같은 방향입니다.`

export const JD_MATCHES = [
  {
    n: 1,
    jdTitle: '생성형 AI 제작 도구의 웹 프론트엔드 개발·아키텍처 설계',
    jdSub: '제작 도구형 웹 애플리케이션의 프론트엔드 구조 설계와 구현',
    evidence: [
      'kasaterm — Rust로 GPU 터미널을 밑바닥부터 직접 만들고, 그 위에 자연어로 도구를 조립하는 GUI 레이어를 얹었습니다. wgpu 셀 렌더러, 입력 → vt100 파서 → 셀 그리드 → GPU 프레임으로 이어지는 파이프라인과 pane 드래그 아키텍처를 혼자 설계·구현했습니다',
      'debi-marlene 대시보드/웹패널 — 158개 Discord 서버 봇의 운영 콘솔을 React·Vite·TypeScript·Tailwind로 직접 설계해 9개월째 라이브 운영 중입니다. 서버 설정·크레딧 결제·이미지 생성 UI까지 프론트 전체를 혼자 맡았습니다',
      '지금 보고 계신 이 포트폴리오 페이지 자체가 제작 도구형 프론트엔드입니다. 콘텐츠를 SSoT 한 파일로 분리하고 스크롤리텔링 컴포넌트를 props 구동으로 설계해, 직군만 갈아끼우면 새 지원 페이지가 찍혀 나오는 구조로 만들었습니다',
      'MCP·hook·서브에이전트로 개발 하네스를 직접 구축했습니다. 도구를 조합해 워크플로우를 만드는 사고방식이 곧 제작 도구를 설계하는 관점과 같습니다',
    ],
  },
  {
    n: 2,
    jdTitle: '내부/외부 생성형 AI 모델과 연동되는 고성능 웹 애플리케이션',
    jdSub: 'AI 모델을 프론트엔드에 연결하고 실시간으로 렌더링',
    evidence: [
      '이 페이지 하단 챗봇은 Anthropic Managed Agent를 `/api/portfolio/ask/stream` 으로 붙여 SSE 스트리밍으로 응답합니다. 프론트에서 토큰이 도착하는 대로 실시간 렌더링하고, 취소·큐잉·이미지 첨부까지 처리합니다',
      'kasaterm 프록시 — `ANTHROPIC_BASE_URL` 을 가로채 SSE 응답을 tee 하고, LiteLLM 으로 여러 모델 백엔드를 교체할 수 있게 구성했습니다. 내부/외부 모델을 한 인터페이스로 스위칭합니다',
      'debi-marlene 봇 백엔드는 Anthropic Managed Agents(claude-haiku-4-5)와 Modal Gemma4 LoRA를 `CHAT_BACKEND` 환경변수 한 줄로 바꿔 낍니다. RAG·LangGraph 오케스트레이션까지 프론트와 연동했습니다',
      '이미지 생성 — 자연어를 도트 스프라이트로 만드는 파이프라인, ComfyUI·codex imagegen 등 멀티모달 생성 모델을 실제 제작 워크플로우에 연결해 써 왔습니다',
    ],
  },
  {
    n: 3,
    jdTitle: '캔버스·드래그앤드롭·실시간 프리뷰·협업 — 제작 도구형 리치 UI/UX',
    jdSub: '단순 폼을 넘어선 인터랙티브 편집 인터페이스',
    evidence: [
      'kasaterm — pane 을 드래그해 merge/split 하는 드롭존, 파일트리 DnD, 이미지 pane(키티 그래픽 프로토콜), Warp 풍 명령 블록 인터랙션을 직접 구현했습니다. 터미널을 편집 가능한 캔버스처럼 다뤘습니다',
      '이 페이지의 메이플 캐릭터는 스크롤을 따라 화면 네 코너를 순회하고, 드래그로 옮길 수 있습니다. 도킹 슬롯을 공유하는 컨텍스트가 매 프레임 lerp/spring 으로 캐릭터를 추종시킵니다. 롯데월드 메이플 콜라보 때 QR 로그인으로 내 캐릭터가 전광판 타워에 뜨던 경험에서 가져온 인터랙션입니다',
      'GSAP ScrollTrigger + Lenis 스무스 스크롤로 스크롤리텔링을 만들었습니다. 챕터 전환과 JD 매칭 카드가 스크롤 위치에 실시간으로 반응합니다',
      'kasaspace 아로나 UI — EdgeRail 접기, 멀티뷰, 실시간 pane 협업(board 동기화)으로 여러 에이전트가 같은 화면에서 함께 일하는 인터페이스를 구현했습니다',
    ],
  },
  {
    n: 4,
    jdTitle: '일관된 UI 품질과 개발 생산성을 위한 컴포넌트 디자인 시스템',
    jdSub: '재사용 컴포넌트와 디자인 토큰으로 품질·생산성 동시 확보',
    evidence: [
      '시각디자인 4년 전공에 실제 디자인 시스템을 운영합니다. 브랜드 컬러 토큰(`colors.ts`), kasaterm 테마 토큰(`theme.rs` · AtomicU32 원자적 교체), 한국어 디자인 스킬(kdesign)까지 직접 만들었습니다',
      '이 포트폴리오는 콘텐츠 SSoT + 재사용 스크롤리텔링 컴포넌트(JD 매칭·케이스 스택·아키텍처 다이어그램)를 props 구동으로 설계했습니다. 지금 이 웹 프론트엔드 지원 페이지도 그 구조에서 콘텐츠만 갈아끼워 찍어냈습니다',
      '디자이너 출신이라 컴포넌트의 시각 품질과 구현을 한 사람이 책임집니다. 디자인과 개발을 오갈 때 생기는 전달 손실·왕복 비용이 없습니다',
      'Paperlogy·NEXON Lv2 Gothic 웹폰트, P3 색공간·Bradford 색 변환까지 다루며 색과 타이포의 일관성을 코드로 관리해 왔습니다',
    ],
  },
] as const

export const PREFERRED = [
  {
    jdTitle: 'Three.js · WebGL 3D 그래픽스 렌더링 최적화',
    evidence:
      '이 페이지 배경은 three.js 로 만든 3종(Ballpit · Aurora · Lightning)을 섹션별로 교체합니다. kasaterm 에서는 wgpu 로 GPU 셀 렌더러를 짜면서 damage tracking 으로 바뀐 셀만 다시 그리고, 메모리를 1.25GB → 113MB 로 줄였습니다. GPU 렌더 파이프라인을 웹과 네이티브 양쪽에서 다뤄 봤습니다.',
  },
  {
    jdTitle: 'WebSocket · 실시간 동시 편집/협업',
    evidence:
      '여러 에이전트가 같은 화면에서 협업하도록 pane 단위 상태 공유(board 동기화)를 직접 설계·구현했습니다. Yjs·CRDT 는 아직 써 보지 않았지만, 실시간 상태를 어떻게 공유하고 병합하는지에 대한 구조는 kasaterm 협업 시스템에서 손으로 만들어 봤습니다.',
  },
  {
    jdTitle: '멀티모달 생성형 AI 서비스에 대한 이해',
    evidence:
      '텍스트·이미지·음성을 모두 다뤄 왔습니다. 자연어 → 도트 스프라이트 생성, ComfyUI 이미지 파이프라인, Qwen3.5-Omni 음성 이해 + CosyVoice3 TTS 를 실제 서비스에 연결했습니다. 모델의 출력을 사용자 경험으로 잇는 작업을 반복해 왔습니다.',
  },
] as const

export const ELIGIBILITY = {
  headline: 'HTML5·CSS3·JS(ES6+)·TypeScript · React·Vite — 라이브로 굴려 온 스택',
  body:
    'debi-marlene 대시보드와 웹패널을 React·Vite·TypeScript·Tailwind로 직접 만들어 9개월째 라이브 운영 중입니다. 상태 관리·라우팅·PWA·Cloudflare 캐시까지 실제 서비스 환경에서 굴렸습니다. 지금 보고 계신 이 포트폴리오 페이지도 React 19 + Vite + TypeScript로, GSAP·Lenis·three.js·framer-motion을 직접 엮어 만들었습니다. 그 위에 Rust로 GPU 터미널(kasaterm)까지 혼자 짜면서 렌더링 파이프라인과 성능 최적화를 밑바닥부터 다뤘습니다. 지원 자격의 HTML5·CSS3·JavaScript(ES6+)·TypeScript·React·Vite는 배워서 아는 게 아니라 매일 굴리는 도구입니다.',
} as const

export const CHARACTER = {
  name: '프로즌샤',
  server: '오로라',
  job: '아크메이지(썬,콜)',
  level: 284,
  experience: '약 16년 (2009 ~ )',
  achievement: {
    title: '하드 세렌 파티 격파',
    sub: '메이플 최상위 콘텐츠 · 게임 도메인 이해의 증거',
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
    detail: '제 봇(데비&마를렌)의 본 IP — 패치노트 RAG·캐릭터 시스템까지 사용자 시점으로 학습',
  },
  { title: '더 파이널스', period: '시즌 단위', detail: 'Embark Studios (넥슨 자회사). 친구들과 라이트 플레이' },
  { title: '서든어택', period: '학창 시절', detail: '넥슨 본사 IP. 친구들과 함께한 입문 FPS' },
] as const

export const ARCHITECTURE = {
  title: '이 포트폴리오의 프론트엔드 파이프라인 — 스크롤부터 3D까지',
  steps: [
    {
      n: 1,
      label: 'Lenis · 스무스 스크롤',
      desc: '네이티브 스크롤을 가로채 관성·보간으로 다시 그립니다. duration·lerp·wheelMultiplier 를 직접 튜닝했습니다',
      cost: 'raf 기반 · 프레임당 1회 보간',
    },
    {
      n: 2,
      label: 'GSAP ticker 통합',
      desc: 'Lenis 의 raf 를 GSAP ticker 에 물려 스크롤과 애니메이션을 한 루프로 합치고, ScrollTrigger 로 섹션을 스크롤 위치에 맞춰 reveal',
      cost: 'lagSmoothing 0 · 단일 프레임 루프',
    },
    {
      n: 3,
      label: 'CharacterDock · 캐릭터 추종',
      desc: '도킹 슬롯을 공유하는 컨텍스트가 매 프레임 lerp/spring 으로 캐릭터를 목표 위치까지 따라잡게 합니다',
      cost: 'dockEl 슬롯 · 16% 비율 spring',
    },
    {
      n: 4,
      label: 'three.js 배경 렌더',
      desc: 'Ballpit·Aurora·Lightning 을 WebGL 로 렌더하고 섹션별로 교체. 화면 밖에선 GPU 부하를 낮춥니다',
      cost: '가시 영역만 활성',
    },
    {
      n: 5,
      label: 'content SSoT → 직군 페이지',
      desc: '콘텐츠를 한 파일로 모으고 컴포넌트를 props 구동으로 설계해, 직군만 바꾸면 새 지원 페이지가 나옵니다',
      cost: '이 웹 프론트엔드 페이지가 그 산출물',
    },
  ],
} as const

export const TECH_STACK = {
  frontend: [
    { label: '프레임워크', value: 'React 19 · Vite · TypeScript · Tailwind' },
    { label: '스크롤·모션', value: 'GSAP ScrollTrigger · Lenis · framer-motion' },
    { label: '3D·그래픽스', value: 'three.js (Ballpit · Aurora · Lightning) · WebGL' },
    { label: '배포', value: 'PWA (vite-plugin-pwa) · Cloudflare 캐시 · debimarlene.com' },
  ],
  native: [
    { label: 'GPU 터미널', value: 'kasaterm — Rust · wgpu · winit' },
    { label: '렌더', value: 'vt100 파서 · 셀 그리드 · damage tracking · P3/Bradford' },
  ],
  ai: [
    { label: '모델 연동', value: 'Anthropic Managed Agents · SSE 스트리밍' },
    { label: '하네스', value: 'MCP · hook · 서브에이전트 · LiteLLM 멀티모델' },
    { label: '오케스트레이션', value: 'RAG · LangGraph StateGraph' },
  ],
} as const

export const CASES = [
  {
    no: 1,
    title: 'kasaterm — GPU 터미널 메모리 1.25GB → 113MB',
    problem:
      'Rust GPU 터미널 초기 구현이 메모리를 1.25GB 넘게 먹었습니다. 변화가 없는 프레임에도 셀을 매번 다시 그리는 구조가 원인이었습니다.',
    approach:
      'damage tracking 을 도입해 바뀐 셀(dirty)만 다시 그리고, 변화 없는 프레임은 GPU 제출을 통째로 건너뛰게 했습니다. 글리프 아틀라스와 색 파이프라인(P3/Bradford)도 재구성했습니다.',
    result:
      '메모리를 113MB 로 약 91% 줄였습니다. GPU 프레임을 PNG 로 리드백해 렌더 결과를 자동 검증하는 루프까지 붙여, 회귀를 눈이 아니라 스크립트로 잡습니다.',
    bridge:
      'GPU 렌더 파이프라인을 밑바닥에서 최적화한 경험 — three.js/WebGL 렌더링 최적화 우대사항과 그대로 이어집니다.',
  },
  {
    no: 2,
    title: '이 포트폴리오 — content SSoT + props 구동 컴포넌트로 직군별 페이지',
    problem:
      '지원처마다 페이지를 새로 짜면 컴포넌트가 복제되고 유지보수가 무너집니다. 콘텐츠와 화면이 뒤엉키는 게 문제였습니다.',
    approach:
      '콘텐츠를 content 파일 하나로 모으고, JD 매칭·케이스 스택·아키텍처 다이어그램을 props 만 받는 순수 컴포넌트로 설계했습니다. 페이지는 콘텐츠를 주입하는 얇은 오케스트레이터로 남겼습니다.',
    result:
      '넥슨 LLM·서비스·QA, 사이오닉, 코코네, 그리고 지금 이 웹 프론트엔드 버전까지 같은 엔진에서 콘텐츠만 갈아끼워 찍어냈습니다.',
    bridge: '컴포넌트 디자인 시스템으로 개발 생산성을 확보하는 방식 그 자체입니다.',
  },
  {
    no: 3,
    title: '캐릭터 도킹 인터랙션 — 스크롤을 따라다니는 캐릭터',
    problem: '정적인 포트폴리오는 기억에 남지 않습니다. 시선을 끌면서도 읽기를 방해하지 않는 인터랙션이 필요했습니다.',
    approach:
      '롯데월드 메이플 콜라보에서 QR 로그인으로 내 캐릭터가 전광판 타워에 뜨던 경험을 그대로 가져왔습니다. 도킹 슬롯을 공유하는 컨텍스트를 만들고, 캐릭터가 매 프레임 lerp/spring 으로 스크롤 위치를 추종하며 네 코너를 순회하게 했습니다. 드래그로 옮길 수도 있습니다.',
    result: '캐릭터가 페이지 전체를 따라다니다 하단 챗봇으로 이어집니다. 인터랙션이 곧 내비게이션이 됐습니다.',
    bridge: '실시간 프리뷰·드래그 인터랙션을 제작 도구 UI 에 녹여 넣는 감각.',
  },
  {
    no: 4,
    title: 'Lenis × GSAP — 스크롤과 애니메이션을 한 루프로',
    problem: '스무스 스크롤과 GSAP 애니메이션이 각자 raf 를 돌리면 프레임이 어긋나 스크롤이 끊깁니다.',
    approach:
      'Lenis 의 raf 를 GSAP ticker 에 물려 단일 루프로 합치고, lagSmoothing 을 0 으로 꺼 ScrollTrigger 가 Lenis 스크롤 값을 그대로 읽게 했습니다.',
    result: '스크롤·섹션 reveal·캐릭터 추종이 같은 프레임에서 움직여 끊김이 사라졌습니다.',
    bridge: '프레임 예산 안에서 여러 렌더 소스를 동기화하는 성능 감각.',
  },
  {
    no: 5,
    title: 'kasaterm — pane 드래그 merge/split 드롭존',
    problem: '터미널 분할을 키보드 단축키로만 하면 직관적이지 않습니다. 마우스로 레이아웃을 바꾸고 싶었습니다.',
    approach:
      'pane 을 잡아 다른 pane 위로 끌면 merge/split 드롭존이 나타나고, 놓는 위치에 따라 레이아웃이 바뀌게 했습니다. iTerm 풍 per-pane 헤더와 드롭 하이라이트도 붙였습니다.',
    result: '마우스만으로 레이아웃을 자유롭게 재구성합니다. 드래그앤드롭 편집 인터페이스의 실전 구현입니다.',
    bridge: 'JD 의 드래그앤드롭 제작 도구 UI 요구와 1:1 로 맞물립니다.',
  },
  {
    no: 6,
    title: 'debi-marlene 대시보드 — 158서버 운영 콘솔 React',
    problem: '158개 서버 봇의 설정·결제·통계를 코드로만 만지는 건 지속 불가능했습니다.',
    approach:
      'React·Vite·TypeScript·Tailwind 로 운영 대시보드와 웹패널(PWA)을 만들고, 로그인·서버별 설정·크레딧 충전(Toss)·이미지 생성 UI 를 붙였습니다. Cloudflare 캐시로 배포했습니다.',
    result: '9개월째 라이브. 실제 사용자와 결제가 도는 프로덕션 React 서비스를 혼자 설계·개발·운영하고 있습니다.',
    bridge: '라이브 웹 애플리케이션을 설계부터 운영까지 혼자 책임져 본 경험.',
  },
] as const

export const COLLAB = {
  title: '커뮤니케이션 국제 디자인 공모전 입상',
  problem: '3인 팀에서 졸업 전시 작품을 "인쇄 단일" vs "디지털 결합"으로 두고 의견이 갈렸습니다.',
  approach:
    '일정·인력·관람객 시나리오를 표로 정리해 두 안을 같은 기준 위에서 비교했습니다. 디자인 컨셉을 흐트러뜨리지 않는 선에서 인터랙티브 웹페이지 인터페이스 방향을 직접 제안했습니다.',
  result: '시각적 일관성과 사용자 흐름을 결합한 결과물로 공모전에 입상했습니다.',
  bridge: '협업 구성원과 소통하며 더 나은 제품 경험을 위해 주도적으로 의견을 내는 방식 — 우대사항과 맞닿아 있습니다.',
} as const

export const CONTACT = {
  email: 'goenho0613@gmail.com',
  github: 'https://github.com/2rami',
  domain: 'https://debimarlene.com',
  edu: '신구대학교 시각디자인과 졸업 (2026.02)',
} as const
