/**
 * 코코네 — [Cocone Internship] AI Engineer 지원용
 * 컨텐츠 SSoT — 실제 debi-marlene / kasaterm 결과물 기반
 *
 * 공고 핵심: 'I AM(Identity in Avatar Metaverse)' · AI(PyTorch/생성형AI/LLM) 또는
 *   Claude Code 같은 AI 어시스턴트로 과제 해결 · 포트폴리오 필수(AI 활용 구현 프로젝트 또는 AI 연구 결과물).
 *   강조 키워드: Diffusion 생성형 AI · LLM · Harness Engineering · 2D 아바타 Animation · World Model · Vibe Coding.
 *
 * 거짓 방지: Diffusion '추론 최적화'는 안 함 → '학습/생성'으로만. Claude API 프로덕션 운영 X(키만 보유).
 *   실제 프로덕션 캐릭터 대화는 Gemma4 LoRA 파인튜닝 + Anthropic Managed Agents(2026-04 전환).
 */

// 코코네 브랜드 액센트 (핑크/마젠타 — 아바타·메타버스 톤) — PageKokone 로컬에서 사용
export const ACCENT = '#FF2E88'
export const ACCENT_SOFT = '#FFE7F1'

export const HERO = {
  jobCode: 'AI ENGINEER · INTERNSHIP',
  badge: 'COCONE · AI Engineer 인턴십 지원',
  title: '캐릭터를 좋아해서\nAI 모델을 직접 만들었습니다',
  subtitle:
    '좋아하는 캐릭터를 직접 움직이게 만들고 싶어 코드를 시작했고, 지금은 그 캐릭터를 생성하는 Diffusion LoRA와 대화시키는 LLM을 직접 파인튜닝·서빙합니다.',
  ctas: [
    { label: 'GitHub · @2rami', href: 'https://github.com/2rami', primary: true },
    { label: 'Live · debimarlene.com', href: 'https://debimarlene.com', primary: false },
  ],
} as const

export const QUOTE = '아이디어와 AI 기술로, 아바타로 진짜 나를 표현하는 메타버스의 새로운 기준을 설계한다 — I AM.'

// 슬라이드 텍스트 statement — 큰 한 줄 + 부제
export const MANIFESTO = {
  intro: '저는 캐릭터를 좋아해서 코드를 시작했습니다.',
  introSub: '지금은 그 캐릭터를 만들어내는 AI 모델을 직접 파인튜닝하고, AI 어시스턴트로 풀스택 서비스를 혼자 만들어 운영합니다. 좋아하는 마음이 모델을 끝까지 길들이게 했습니다.',
  closing: '아바타로 정체성을 표현하듯, 저는 AI로 상상한 캐릭터를 살아 움직이게 만듭니다.',
  closingSub: '데이터 수집부터 LoRA 파인튜닝·서빙까지 직접 다루고, 무엇을·왜는 제가 판단하고 구현 속도는 AI로. 그렇게 코코네의 R&D 과제를 데모가 아니라 실제 작동하는 결과물로 만들고 싶습니다.',
} as const

export const STATS = [
  { label: '오리지널 캐릭터 LoRA 학습', value: '2', unit: '종', sub: 'Illustrious·NoobAI-XL 베이스 · kohya 레시피로 캐릭터 일관 생성' },
  { label: 'LLM 캐릭터 챗봇 파인튜닝', value: '1', unit: '종', sub: 'Gemma 4 E4B LoRA(Unsloth·TRL) → Modal A10G 서빙' },
  { label: 'VL 게임 아이템 인식', value: '3,806', unit: '종', sub: 'Qwen2.5-VL-3B LoRA 파인튜닝' },
  { label: 'TTS 엔진 정량 비교', value: '6', unit: '종', sub: '음질·속도·커스텀성 평가 후 CosyVoice3 채택·서빙' },
] as const

export const ABOUT = `시각디자인을 전공했지만, 좋아하는 캐릭터를 직접 움직이게 만들고 싶어 코드를 시작했습니다.

코드 경험 0에서 8개월. 게임 커뮤니티용 풀스택 AI 서비스를 혼자 만들어 운영하면서, 생성형 AI 파이프라인을 데이터 수집부터 LoRA 파인튜닝·서빙까지 직접 다뤘습니다.

AI는 자동완성이 아니라 작업 방식 그 자체입니다. 캐릭터 생성(Diffusion)·대화(LLM)·음성(TTS) 모델을 직접 길들이고, Claude Code 같은 AI 어시스턴트로는 Rust GPU 터미널까지 만듭니다.`

// 기술 스택 마퀴 (흐르는 띠 2줄)
export const STACK = {
  ai: [
    'Diffusion LoRA (Illustrious·NoobAI-XL)',
    'Gemma 4 E4B LoRA',
    'Qwen2.5-VL-3B',
    'CosyVoice3 TTS',
    'kohya · Unsloth · TRL · PEFT',
    'Modal Serverless GPU',
    'Anthropic Managed Agents',
    'LangGraph',
    'ComfyUI',
  ],
  infra: [
    'PyTorch',
    'Claude Code 하네스 (MCP·hook·subagent)',
    'Rust · wgpu',
    'React 19 · TypeScript',
    'GCP Compute Engine',
    'Docker',
    'Firestore',
    'nginx · Cloudflare',
  ],
} as const

// 프로젝트 케이스 — 문제 → 접근 → 결과 → 코코네 연결
// tag 로 두 프로젝트(AI 모델 파이프라인 / AI 어시스턴트 하네스)로 분기.
export const CASES = [
  {
    no: 1,
    tag: 'debi-marlene',
    title: 'Diffusion LoRA로 오리지널 캐릭터를 일관되게 생성 — 코코네 아바타 생성과 1:1',
    problem:
      '오리지널 마스코트 캐릭터를 매번 같은 얼굴·복장·분위기로 생성하고 싶음. 범용 모델은 같은 캐릭터를 그릴 때마다 디테일이 흔들림.',
    approach:
      'Illustrious / NoobAI-XL 베이스로 캐릭터 LoRA를 직접 학습(kohya 레시피). 트리거 토큰을 설계하고 데이터셋을 구성하며, cp949/PYTHONUTF8 인코딩 트랩까지 직접 부딪혀 캐릭터 일관성을 잡음. ComfyUI 노드 그래프로 생성 파이프라인을 자동화.',
    result: '트리거 토큰 하나로 동일 캐릭터를 다양한 포즈·배경으로 양산. "Diffusion 기반 생성형 AI로 2D 아바타를 만든다"는 코코네 핵심 과제를 직접 해본 사례.',
    bridge: '코코네의 Diffusion 기반 2D 아바타 생성·캐릭터 일관성 과제와 정확히 같은 작업.',
  },
  {
    no: 2,
    tag: 'debi-marlene',
    title: 'Gemma 4 LoRA 캐릭터 챗봇 — 데이터부터 서빙까지 LLM 전 과정',
    problem:
      '게임 커뮤니티 봇에 캐릭터 말투를 입힌 대화 기능이 필요. 범용 LLM API로는 캐릭터성과 비용을 동시에 잡기 어려움.',
    approach:
      'Gemma 4 E4B를 LoRA 파인튜닝(Unsloth+TRL, Colab A100)해 캐릭터 말투를 학습시키고 Modal A10G에 bfloat16·모델 bake-in으로 서빙. 단순 호출이 아니라 LangGraph StateGraph로 의도 분류·키워드 트리거·대화 상태를 설계. 이후 Anthropic Managed Agents로 전환해 세션 영속화 + custom tool 5종까지 구현.',
    result: '실제 사용자가 쓰는 캐릭터 챗봇을 프로덕션으로 운영. "API를 호출했다"가 아니라 "모델을 만들어 띄웠다".',
    bridge: '코코네의 "LLM 기반 에이전트 설계" 과제 — 아바타에 정체성·말투를 부여하는 작업과 직결.',
  },
  {
    no: 3,
    tag: 'debi-marlene',
    title: '멀티모달 — Qwen2.5-VL LoRA로 게임 아이템 3,806종 인식',
    problem:
      '게임 스크린샷에서 아이템을 인식해야 하는데, 도메인 특화 아이템은 범용 비전 모델이 못 알아봄.',
    approach:
      'Qwen2.5-VL-3B를 LoRA 파인튜닝해 게임 아이템 3,806종을 인식하도록 길들임. 데이터셋 구성부터 학습·평가까지 비전 모델을 도메인에 맞게 적응시키는 작업을 처음부터 끝까지 수행.',
    result: '도메인 특화 비전 인식을 프로덕션 수준으로 확보. 텍스트·이미지를 함께 다루는 멀티모달 파인튜닝 경험.',
    bridge: '아바타·이미지를 다루는 코코네의 멀티모달·생성 과제에 바로 이어지는 비전 모델 적응 역량.',
  },
  {
    no: 4,
    tag: 'debi-marlene',
    title: 'TTS 엔진 6종 정량 비교 — "써봤다"가 아니라 "골랐다"',
    problem:
      '캐릭터 음성 합성에 쓸 TTS를 정해야 함. 후보가 많고 음질·속도·커스텀성·비용이 다 다름.',
    approach:
      'CosyVoice3 · Edge TTS · Fish-Speech · Qwen3-TTS · SoVITS · Google Cloud TTS 6종을 실제로 돌려 음질/지연/커스텀성으로 정량 비교. CosyVoice3를 선택해 파인튜닝 후 Modal에 서빙, T4 bfloat16 호환성 문제를 직접 패치.',
    result: '근거 있는 선택 + 캐릭터 음성을 커스텀 합성해 프로덕션 운영. 비용/성능 트레이드오프로 모델을 고르고 안 되는 부분을 디버깅한 사례.',
    bridge: '최신 모델을 비교·선택·디버깅해 서비스에 녹이는, 코코네가 찾는 R&D 실행력.',
    audio: [
      { label: '데비 — CosyVoice3 커스텀', src: '/audio/demo_debi_desc.wav' },
      { label: '마를렌 — CosyVoice3 커스텀', src: '/audio/demo_marlene_desc.wav' },
    ],
  },
  {
    no: 5,
    tag: 'kasaterm',
    title: '나만의 AI 하네스 — MCP · hook · 서브에이전트 · board (Harness Engineering)',
    problem:
      'AI에게 코드를 받아쓰는 것만으로는 1인이 AI 파이프라인과 시스템 프로그래밍을 동시에 운영하기 어려움. 에이전트가 더 잘 일할 환경 자체가 필요.',
    approach:
      'MCP 서버로 터미널을 제어하고, hook으로 작업 컨텍스트를 자동 주입하고, 서브에이전트로 빌드·리뷰·탐색을 병렬화. 여러 AI pane이 같은 레포를 충돌 없이 협업하는 board 시스템까지 직접 구축 — 컨텍스트·하네스 엔지니어링을 말이 아니라 손으로 체득.',
    result: '반복은 AI·자동화로 줄이고 나는 문제 정의·설계·검증에 집중하는 작업 방식을 확립. 1인이 시스템 프로그래밍과 생성형 AI를 동시에 다룸.',
    bridge: '코코네가 명시한 Harness Engineering · Vibe Coding · "Claude Code 같은 AI 어시스턴트로 과제 해결"과 정확히 같은 방향.',
  },
  {
    no: 6,
    tag: 'kasaterm',
    title: 'AI 어시스턴트로 Rust GPU 터미널을 완성 — 비전공이 시스템 프로그래밍까지',
    problem:
      '시각디자인 전공자가 Rust·wgpu 같은 저수준 시스템 프로그래밍을, AI를 도구 삼아 어디까지 끝낼 수 있는가.',
    approach:
      '무엇을·왜 만들지와 버그의 진짜 원인은 내가 판단하고, 구현 속도는 AI로. 메모리 1.25GB의 범인(폰트 fs::read)을 vmmap/malloc_history로 추적해 mmap으로 교체(113MB), 색 불일치를 9가지 시도 끝에 sRGB→DisplayP3 변환으로 해결.',
    result: 'tmux를 대체하는 크로스플랫폼 GPU 터미널을 8개월 만에 직접 완성. "AI 어시스턴트를 활용해 본인만의 프로젝트를 완성"한 결과물.',
    bridge: '코코네 우대사항 — AI 어시스턴트로 본인만의 프로젝트를 끝까지 완성해 본 경험 그 자체.',
  },
] as const

// 공개 GitHub 레포 카드
export const PROJECTS = [
  {
    name: 'debi-marlene',
    desc: '풀스택 AI 디스코드 봇 + 웹 대시보드. Diffusion 캐릭터 LoRA·Gemma4 LoRA 챗봇·Qwen-VL·CosyVoice3 TTS까지 AI 파이프라인을 1인 구축·운영.',
    tags: ['Diffusion LoRA', 'Gemma4 LoRA', 'Qwen-VL', 'CosyVoice3'],
    repo: 'https://github.com/2rami/debi-marlene',
    live: 'https://debimarlene.com',
  },
  {
    name: 'kasaterm',
    desc: 'Rust GPU 터미널 + Claude Code 하네스. MCP·hook·서브에이전트·board로 AI 협업 환경을 직접 설계. tmux를 대체하는 자체 터미널.',
    tags: ['Rust', 'wgpu', 'AI Harness'],
    repo: 'https://github.com/2rami/kasaterm',
    live: '',
  },
  {
    name: 'ai-trending-feed',
    desc: '매일 4개 소스에서 AI 트렌드를 수집·LLM 큐레이션해 DM으로 보내는 자동 파이프라인.',
    tags: ['GitHub Actions', 'LLM curator', 'Firestore'],
    repo: 'https://github.com/2rami/ai-trending-feed',
    live: '',
  },
] as const

// 프로젝트 헤더 — WORK를 프로젝트 중심으로 재편
export const PROJECT_DEBI = {
  no: '01',
  tag: 'AI 모델 파이프라인',
  title: '캐릭터를 만드는\nAI 파이프라인',
  tagline: 'Diffusion 캐릭터 생성(LoRA)·LLM 캐릭터 챗봇(Gemma4)·멀티모달 인식(Qwen-VL)·음성 합성(CosyVoice3)까지 — 데이터 수집부터 파인튜닝·서빙·운영을 1인이 직접. 158개 서버에서 돌아가는 라이브 서비스.',
  repo: 'https://github.com/2rami/debi-marlene',
  live: 'https://debimarlene.com',
  stats: [
    { value: '4', unit: '종', label: 'AI 모델 직접 학습·서빙' },
    { value: '3,806', unit: '종', label: 'VL 아이템 인식' },
    { value: '158', unit: '+', label: 'Discord 서버 운영' },
  ],
} as const

export const PROJECT_KASA = {
  no: '02',
  tag: 'AI 어시스턴트 · 하네스',
  title: 'AI로 만든\nRust GPU 터미널',
  tagline: 'Claude Code 같은 AI 어시스턴트를 도구 삼아 비전공자가 시스템 프로그래밍까지 — MCP·hook·서브에이전트·board로 나만의 AI 협업 하네스를 직접 설계한 Harness Engineering · Vibe Coding 결과물.',
  repo: 'https://github.com/2rami/kasaterm',
  live: '',
  stats: [
    { value: '113', unit: 'MB', label: '메모리 (1.25GB→113MB)' },
    { value: '4', unit: '종', label: 'AI 협업 하네스 (MCP·hook·subagent·board)' },
    { value: '2', unit: 'OS', label: 'macOS · Windows' },
  ],
  gui: {
    title: 'SCHALE OS — AI를 게임 UI로 시각화',
    body: '터미널 Claude Code의 토큰·컨텍스트·서브에이전트를 블루아카이브풍 게임 UI(SCHALE OS)로 시각화·조작하는 컨트롤 패널을 만들고 있습니다. "보이지 않는 AI 상태"를 캐릭터와 교실 UI로 보이게 만드는 작업 — 아바타로 정보를 표현하는 코코네의 방향과 맞닿은 현재 진행형 프로젝트.',
  },
} as const

// 코코네 핏 — 별도 FIT 섹션 대신 About에 칩으로 흡수, 프로젝트가 증명
export const KEY_TRAITS = [
  'AI 모델을 직접 파인튜닝',
  'Diffusion으로 캐릭터 생성',
  'AI 어시스턴트로 풀스택 구현',
  '모델을 비교·선택·디버깅',
  '캐릭터·아바타 도메인 친화',
  '디자인 + 개발을 한 사람이',
] as const

export const CONTACT = {
  email: 'goenho0613@gmail.com',
  github: 'https://github.com/2rami',
  domain: 'https://debimarlene.com',
} as const
