/**
 * 사이오닉에이아이 — AI Native Engineer Fellowship 지원용
 * 컨텐츠 SSoT — 실제 kasaterm / debi-marlene 결과물 기반
 * 공고 핵심: "학위가 아니라 실제 문제에 대한 집요한 해결력"
 *
 * 거짓 방지: Claude API 프로덕션 운영 X(키만 보유). 실제 프로덕션 캐릭터 대화는
 * Gemma4 LoRA 파인튜닝 + Anthropic Managed Agents(2026-04 전환).
 */

// 사이오닉 브랜드 액센트 (#007FF5 — sionic.ai 추출) — PageSionic 로컬에서 사용
export const ACCENT = '#007FF5'
export const ACCENT_SOFT = '#E6F2FF'

export const HERO = {
  jobCode: 'AI NATIVE ENGINEER',
  badge: 'SIONIC AI · AI Native Engineer Fellowship 지원',
  title: '학위가 아니라\n동작하는 결과물로 증명합니다',
  subtitle:
    '시각디자인에서 출발해, 8개월 만에 풀스택 AI 서비스를 혼자 만들어 운영했습니다. 지금은 Rust로 GPU 터미널을 만들고 있습니다.',
  ctas: [
    { label: 'GitHub · @2rami', href: 'https://github.com/2rami', primary: true },
    { label: 'Live · debimarlene.com', href: 'https://debimarlene.com', primary: false },
  ],
} as const

export const QUOTE = '탁월한 엔지니어링 역량은 "학위"가 아니라 "실제 문제에 대한 집요한 해결력"에서 나온다.'

// 슬라이드 텍스트 statement — 큰 한 줄 + 부제
export const MANIFESTO = {
  intro: '8개월 전, 저는 코드 한 줄 못 짰습니다.',
  introSub: '지금은 풀스택 AI 서비스를 혼자 만들어 운영하고, Rust로 GPU 터미널을 만듭니다. 도구가 대신 풀어주지 않는 문제 앞에서 도망치지 않은 결과입니다.',
  closing: '대신 풀어주지 않는 문제 앞에서, 도망치지 않았습니다.',
  closingSub: '판단은 제가, 속도는 AI가. 그렇게 AI와 함께 더 큰 문제를 끝까지 푸는 엔지니어가 되고 싶습니다.',
} as const

export const STATS = [
  { label: '코드 0 → 프로덕션 운영', value: '8', unit: '개월', sub: '비전공·무연차에서 풀스택 AI 서비스 단독 구축·배포' },
  { label: 'kasaterm 메모리 감축', value: '91', unit: '%', sub: '1.25GB → 113MB · vmmap/malloc_history 추적' },
  { label: 'TTS 엔진 정량 비교', value: '6', unit: '종', sub: '음질·속도·커스텀성 평가 후 CosyVoice3 채택' },
  { label: 'VL 게임 아이템 인식', value: '3,806', unit: '종', sub: 'Qwen2.5-VL-3B LoRA 파인튜닝' },
] as const

export const ABOUT = `디자인을 전공했지만, 상상한 걸 직접 움직이게 만들고 싶어 코드를 시작했습니다.

코드 경험 0에서 8개월. 게임 커뮤니티용 풀스택 AI 서비스를 혼자 만들어 운영했고, 지금은 Rust로 GPU 터미널을 만듭니다.

AI는 자동완성이 아니라 작업 방식 그 자체입니다. 무엇을·왜 만들지는 제가 판단하고, AI는 빠르게 구현·검증합니다.`

// 기술 스택 마퀴 (흐르는 띠 2줄)
export const STACK = {
  ai: [
    'Gemma 4 E4B LoRA',
    'Qwen2.5-VL-3B',
    'CosyVoice3 TTS',
    'Modal Serverless GPU',
    'Anthropic Managed Agents',
    'LangGraph',
    'Unsloth · TRL',
    'RAG',
  ],
  infra: [
    'Rust · wgpu',
    'React 19',
    'TypeScript',
    'GCP Compute Engine',
    'Docker',
    'Firestore',
    'Toss Payments',
    'nginx · Cloudflare',
    'GitHub Actions',
  ],
} as const

// 사이오닉 공고 "우리는 어떤 사람을 찾나요? — 핵심 역량" 6항목에 결과물로 1:1 매칭
export const MATCHES = [
  {
    n: 1,
    jdTitle: '문제를 받기만 하지 않고\n스스로 다시 정의하는 사람',
    jdSub: '문제를 재정의하고 복잡한 요구를 기술 문제로 번역',
    evidence: [
      'kasaterm의 느린 응답을 "최적화할 부분"이 아니라 "데몬 기반 구조 자체가 원인"으로 재정의 — 계측으로 병목을 규명하고 GUI가 PTY를 직접 소유하는 로컬 모드로 아키텍처를 전면 재설계',
      '"tmux의 GUI 경험이 답답하다"는 추상적 불만을, GPU로 셀 그리드를 직접 렌더하는 크로스플랫폼 터미널을 만든다는 구체적 기술 과제로 번역',
      '디자이너 출신으로 "보이는 것(색이 안 맞는다)"을 "돌아가는 것(sRGB→DisplayP3 Bradford matrix 변환)"으로 옮기는 번역을 일상적으로 함',
    ],
  },
  {
    n: 2,
    jdTitle: 'AI를 자동완성이 아니라\n사고·생산성을 증폭시키는 파트너로',
    jdSub: '에이전트가 더 잘 일하도록 환경 자체를 설계',
    evidence: [
      'MCP 서버로 터미널을 제어하고, hook으로 작업 컨텍스트를 자동 주입하고, 서브에이전트를 띄워 빌드·리뷰·탐색을 병렬화하는 나만의 개발 하네스를 직접 구축',
      '여러 AI pane이 같은 코드베이스를 충돌 없이 협업하는 board 시스템까지 만들어, 컨텍스트 엔지니어링과 하네스 엔지니어링의 차이를 말이 아니라 손으로 체득',
      '판단(무엇을·왜·버그의 진짜 원인)은 내가, 구현 속도는 AI로 — 역할을 명확히 분담해 1인이 시스템 프로그래밍과 AI 파이프라인을 동시에 다룸',
    ],
  },
  {
    n: 3,
    jdTitle: '빠르게 배우고, 바로 적용하고,\n결과를 검증하는 사람',
    jdSub: '새로운 도구를 빠르게 익혀 프로덕션에 적용',
    evidence: [
      '비전공·무연차에서 8개월 만에 Rust GPU 프로그래밍과 LLM 파인튜닝·서빙까지 — 새 기술을 받아 바로 실제 서비스에 적용하고 운영으로 검증',
      'TTS 엔진을 "써봤다"가 아니라 6종을 음질·속도·커스텀성으로 정량 비교·평가한 뒤 CosyVoice3를 선택 — 비용/성능 트레이드오프로 의사결정',
      '봇 대화를 Anthropic Managed Agents 베타로 직접 전환하고 custom tool 5종을 붙이는 등, 새 API가 나오면 바로 프로덕션에 적용',
    ],
  },
  {
    n: 4,
    jdTitle: '반복 작업은 AI·자동화로 줄이고\n판단과 설계에 집중하는 사람',
    jdSub: '자동화로 여유를 만들어 더 중요한 일에 집중',
    evidence: [
      'Makefile 배포 자동화 + GitHub Actions cron + Daily AI Feed 파이프라인(4소스 fetch → LLM 큐레이션 → 중복 제거 → DM)으로 반복 운영을 자동화',
      '12,896줄 단일 파일을 8개 도메인 모듈로 분리해, 사람이 판단해야 할 영역과 기계가 반복할 영역의 경계를 코드 구조로 정리',
      '큐레이터 모델을 비교해 비용·품질 트레이드오프를 정량 측정하고, 반복 작업에 맞는 모델을 선택',
    ],
  },
  {
    n: 5,
    jdTitle: '"그럴듯한 결과"에 만족하지 않고\n실제로 작동하는 결과물을 끝까지',
    jdSub: 'AI가 만든 결과물까지 최종 품질을 책임',
    evidence: [
      'kasaterm 색 불일치를 "대충 비슷하게"가 아니라 9가지 시도 끝에 sRGB→DisplayP3 변환으로 정확히 해결',
      '메모리 1.25GB의 진짜 범인(폰트 fs::read)을 vmmap/malloc_history로 추적해 mmap으로 교체, 113MB까지 감축 — 추정이 아니라 계측으로 끝을 봄',
      '8개월간 0에서 프로덕션 서비스 운영까지 — "데모"가 아니라 실제 사용자가 쓰는 결과물을 책임지고 유지',
    ],
  },
  {
    n: 6,
    jdTitle: '학위가 아니라\n결과물로 증명하는 사람',
    jdSub: '스스로 탐구하고 만들어 본 경험으로 실력을 증명',
    evidence: [
      'GitHub(@2rami)에 쌓인 결과물과 라이브 서비스(debimarlene.com)가 곧 이력서 — 자격증이 아니라 동작하는 것으로 증명',
      'AI/ML 전 과정(데이터 수집 → 전처리 → LoRA 파인튜닝 → Modal GPU 서빙)을 Gemma 4·Qwen-VL·CosyVoice3로 직접 수행',
      '시각디자인이라는 전혀 다른 출발점에서 시스템 프로그래밍까지 스스로 도달한 학습 경로 자체가 "정규 교육 밖에서 증명한 실행력"',
    ],
  },
] as const

// 프로젝트 케이스 — 문제 → 접근 → 결과 → 사이오닉 연결
export const CASES = [
  {
    no: 1,
    tag: 'kasaterm',
    title: 'kasaterm 메모리 1.25GB → 113MB — 추정이 아니라 계측으로',
    problem:
      'Rust GPU 터미널 kasaterm이 idle 상태에서 1.25GB를 점유. "어디선가 새는 것 같다"는 추정만으로는 범인을 못 잡음.',
    approach:
      'vmmap / malloc_history로 메모리를 분해해 폰트 로딩(fs::read로 폰트 파일 전체를 힙에 올림)이 주범임을 특정. fs::read를 mmap으로 교체하고, damage tracking으로 불필요한 GPU 패스를 skip.',
    result: '113MB까지 감축(약 91%). 추측이 아니라 계측·가설·검증의 사이클로 저수준 문제를 끝까지 추적한 사례.',
    bridge: '"진짜 원인을 내가 판단하고 AI는 구현·검증 파트너로 둔다"는 작업 방식이 그대로 드러나는 사례.',
  },
  {
    no: 2,
    tag: 'kasaterm',
    title: 'wgpu 색 파이프라인 — 9가지 시도 끝의 sRGB→DisplayP3',
    problem:
      '터미널 셀 색이 의도한 값과 미묘하게 어긋남. 디자이너로서 "색이 틀렸다"는 건 보이는데, GPU 파이프라인 어디서 깨지는지가 안 보임.',
    approach:
      '감마 블렌딩·색 공간·서브레이어 합성을 하나씩 의심하며 9가지 시도. 최종적으로 셰이더에서 sRGB→DisplayP3 Bradford matrix 변환 + P3 태깅으로 해결. swash glyph atlas와 결합.',
    result: '의도한 색을 정확히 재현. "보이는 것"을 "돌아가는 것"으로 번역하는 디자이너+엔지니어 조합의 강점이 드러난 사례.',
    bridge: '복잡한 문제를 구조화해 기술 문제로 번역하고 끝까지 작동시키는 과정 그 자체.',
  },
  {
    no: 3,
    tag: 'debi-marlene',
    title: 'Gemma 4 LoRA 캐릭터 챗봇 — 데이터부터 서빙까지 전 과정',
    problem:
      '게임 커뮤니티 봇에 캐릭터 말투를 입힌 대화 기능이 필요. 범용 LLM API로는 캐릭터성과 비용을 동시에 잡기 어려움.',
    approach:
      'Gemma 4 E4B를 LoRA 파인튜닝(Unsloth+TRL)해 캐릭터 말투를 학습시키고, Modal A10G에 bfloat16·모델 bake-in으로 서빙. 이후 Anthropic Managed Agents 베타로 전환해 세션 영속화 + custom tool 5종(전적/패치/메모리)까지 직접 구현.',
    result: '실제 사용자가 쓰는 캐릭터 챗봇을 프로덕션으로 운영. "API를 호출했다"가 아니라 "모델을 만들어 띄웠다".',
    bridge: 'AI를 비교·파인튜닝·서빙·디버깅까지 다룰 수 있다는 — 도구를 쓰는 게 아니라 다룬다는 증거.',
  },
  {
    no: 4,
    tag: 'debi-marlene',
    title: 'TTS 엔진 6종 정량 비교 — "써봤다"가 아니라 "골랐다"',
    problem:
      '캐릭터 음성 합성에 쓸 TTS를 정해야 함. 후보가 많고 음질·속도·커스텀성·비용이 다 다름.',
    approach:
      'CosyVoice3 · Edge TTS · Fish-Speech · Qwen3-TTS · SoVITS · Google Cloud TTS 6종을 실제로 돌려 음질/지연/커스텀성으로 정량 비교. CosyVoice3를 선택해 파인튜닝 후 Modal에 서빙, T4 bfloat16 호환성 문제를 직접 패치.',
    result: '근거 있는 선택 + 3개 캐릭터 음성을 커스텀 합성해 프로덕션 운영. 비용/성능 트레이드오프로 의사결정한 사례.',
    bridge: '"빠르게 배우고 비교하고 검증해 고른다"는 핵심역량을 그대로 보여주는 사례.',
    audio: [
      { label: '데비 — CosyVoice3 커스텀', src: '/audio/demo_debi_desc.wav' },
      { label: '마를렌 — CosyVoice3 커스텀', src: '/audio/demo_marlene_desc.wav' },
    ],
  },
  {
    no: 5,
    tag: 'debi-marlene',
    title: '1인 풀스택 운영 — 봇·대시보드·웹패널·결제·인프라 전부',
    problem:
      '캐릭터 챗봇 하나가 아니라, 사용자가 직접 쓰는 서비스 전체(웹 대시보드·설정·결제·배포·모니터링)를 혼자 만들고 굴려야 함.',
    approach:
      'React 19 + Vite + Tailwind 4 웹 대시보드와 PWA 웹패널, Flask 백엔드, Toss Payments 결제(멱등·환불), Firestore 5개 컬렉션, GCP Compute Engine + Docker 멀티컨테이너 + Secret Manager + nginx/Cloudflare, Makefile 자동 배포까지 단독 구축.',
    result: 'debimarlene.com에서 158개 이상의 Discord 서버에 실서비스로 운영. 기획·디자인·프론트·백·인프라·결제를 한 사람이 책임짐.',
    bridge: '"AI 시대의 기업 솔루션 문제"를 끝까지 책임지고 운영해 본 풀스택 실행력.',
  },
  {
    no: 6,
    tag: 'kasaterm',
    title: '나만의 개발 하네스 — MCP · hook · 서브에이전트 · board',
    problem:
      'AI에게 코드를 받아쓰는 것만으로는 1인이 시스템 프로그래밍과 AI 파이프라인을 동시에 운영하기 어려움. 에이전트가 더 잘 일할 환경이 필요.',
    approach:
      'MCP 서버로 터미널을 제어하고, hook으로 작업 컨텍스트를 자동 주입하고, 서브에이전트로 빌드·리뷰·탐색을 병렬화. 여러 AI pane이 같은 레포를 충돌 없이 협업하는 board 시스템까지 직접 구축.',
    result: '반복은 AI·자동화로 줄이고 나는 문제 정의·설계·검증에 집중하는 작업 방식을 손으로 체득.',
    bridge: '사이오닉이 찾는 "AI를 작업 방식 자체로 내재화한 사람"과 정확히 같은 방향.',
  },
] as const

// 공개 GitHub 레포 카드
export const PROJECTS = [
  {
    name: 'debi-marlene',
    desc: '풀스택 AI 디스코드 봇 + 웹 대시보드. Gemma4 LoRA 캐릭터 챗봇·TTS·전적·결제까지 1인 구축·운영.',
    tags: ['Gemma4 LoRA', 'Managed Agents', 'React 19', 'GCP'],
    repo: 'https://github.com/2rami/debi-marlene',
    live: 'https://debimarlene.com',
  },
  {
    name: 'kasaterm',
    desc: 'Rust GPU 터미널. wgpu 셀 렌더 · 메모리 113MB · macOS/Windows 크로스플랫폼. tmux를 대체하는 자체 터미널.',
    tags: ['Rust', 'wgpu', 'Cross-platform'],
    repo: 'https://github.com/2rami/kasaterm',
    live: '',
  },
  {
    name: 'ai-trending-feed',
    desc: '매일 4개 소스에서 AI 트렌드를 수집·큐레이션해 DM으로 보내는 자동 파이프라인.',
    tags: ['GitHub Actions', 'Claude curator', 'Firestore'],
    repo: 'https://github.com/2rami/ai-trending-feed',
    live: '',
  },
] as const

// 프로젝트 헤더 — WORK를 프로젝트 중심으로 재편
export const PROJECT_DEBI = {
  no: '01',
  tag: 'debi-marlene',
  title: '풀스택 AI\n디스코드 봇',
  tagline: 'Gemma4 LoRA 캐릭터 챗봇·TTS·전적·결제까지 1인이 만들고 158개 서버에 운영하는 라이브 서비스. 데이터 수집부터 파인튜닝·서빙·프론트·인프라까지 단독 구축.',
  repo: 'https://github.com/2rami/debi-marlene',
  live: 'https://debimarlene.com',
  stats: [
    { value: '158', unit: '+', label: 'Discord 서버 운영' },
    { value: '6', unit: '종', label: 'TTS 엔진 정량 비교' },
    { value: '3,806', unit: '종', label: 'VL 아이템 인식' },
  ],
} as const

export const PROJECT_KASA = {
  no: '02',
  tag: 'kasaterm',
  title: 'Rust GPU\n터미널',
  tagline: 'wgpu로 셀 그리드를 직접 렌더하고 메모리·색·아키텍처 같은 저수준 문제를 끝까지 파는 크로스플랫폼 터미널. tmux를 대체하는 자체 GUI 터미널.',
  repo: 'https://github.com/2rami/kasaterm',
  live: '',
  stats: [
    { value: '113', unit: 'MB', label: '메모리 (1.25GB→113MB)' },
    { value: '9', unit: '회', label: '색 파이프라인 시도' },
    { value: '2', unit: 'OS', label: 'macOS · Windows' },
  ],
  gui: {
    title: 'SCHALE OS — 터미널을 게임처럼',
    body: '터미널 Claude Code를 블루아카이브풍 게임처럼 조작하는 컨트롤 패널(SCHALE OS)을 만들고 있습니다. 토큰·컨텍스트·서브에이전트를 캐릭터와 교실 UI로 시각화 — 디자이너 출신답게 "보이는 것"과 "돌아가는 것"을 한 사람이 잇는 작업, 지금도 손으로 만드는 현재 진행형입니다.',
  },
} as const

// 사이오닉 핵심역량 — 별도 FIT 섹션 대신 About에 칩으로 흡수, 프로젝트가 증명
export const KEY_TRAITS = [
  '문제를 스스로 재정의',
  'AI를 작업 방식으로 내재화',
  '빠르게 배우고 바로 검증',
  '반복은 AI·자동화로',
  '끝까지 작동하는 결과물',
  '학위가 아니라 결과물로 증명',
] as const

export const CONTACT = {
  email: 'goenho0613@gmail.com',
  github: 'https://github.com/2rami',
  domain: 'https://debimarlene.com',
} as const
