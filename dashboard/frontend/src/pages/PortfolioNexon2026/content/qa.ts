/**
 * 넥슨네트웍스 — 게임 QA (채용연계형 인턴) 지원용
 * 컨텐츠 SSoT — 봇 운영 중 직접 추적·재현·문서화한 결함 사례 기반
 *
 * 톤: QA에 진심. 결함 추적·재현·재발 차단 사이클이 메인.
 *     자동화 도구는 학습 의지 + 미래 비전으로만.
 *
 * 5년 비전: AI 자동화 QA 엔지니어
 *   LLM 기반 테스트 케이스 자동 생성 → 라이브 로그 분석 → 결함 재현 파이프라인
 */

export const HERO = {
  jobCode: 'GAME QA',
  badge: 'NEXON NETWORKS · 게임 QA · 채용연계형 인턴 지원',
  title: '메이플 헤비유저이자\n결함을 끝까지 추적하는 봇 운영자',
  subtitle:
    '데비&마를렌 — 1인이 9개월간 158개 Discord 서버에 운영 중인 봇. 매일 발생하는 결함을 직접 재현·분류·기록하며, 같은 결함이 두 번 나오지 않게 만들어 왔습니다. 게임 사용자로서의 도메인 깊이와 운영자로서의 결함 추적 습관을 게임 QA로 이어 가고 싶습니다.',
  ctas: [
    { label: 'GitHub · debi-marlene', href: 'https://github.com/2rami/debi-marlene', primary: true },
    { label: 'Live · debimarlene.com', href: 'https://debimarlene.com', primary: false },
  ],
} as const

export const STATS = [
  { label: '운영 중인 Discord 서버', value: '158', unit: '개', sub: 'debi-marlene · 9개월 라이브' },
  { label: '메이플 직업 월드 랭킹', value: '989', unit: '위', sub: '오로라 · 아크메이지(썬,콜) Lv.284' },
  { label: '음성 파이프라인 결함 추적', value: '11', unit: '건', sub: '원인·재현·교훈 마크다운 누적' },
  { label: '플레이 장르', value: '5', unit: '종', sub: 'MMORPG · MOBA · 어드벤처 · FPS · 수집형' },
] as const

export const ABOUT = `데비&마를렌은 이터널 리턴 쌍둥이 실험체를 모티브로 한 한국어 캐릭터 챗봇입니다. 1인이 기획·개발·배포·운영을 모두 맡아 9개월간 158개 Discord 서버에 라이브로 돌리고 있으며, 그 과정에서 매일 새로운 결함을 만나고 있습니다. 음성 채널 무한 재연결, opus 디코딩 에러로 패킷 라우터 스레드 죽음, on_ready 시 정리 race로 settings 일부 유실, GCS JSON 단일 저장소가 멀티 컨테이너에서 split-brain 발생, docker restart로 env 갱신 안 되는 함정, pkill -f가 다른 파이썬 프로세스까지 죽이는 함정 — 발견한 결함은 모두 마크다운 메모리에 「원인 / 재현 / 교훈」 일관 구조로 누적해 왔습니다. 한편 봇 캐릭터의 본 IP 이터널리턴부터 메이플스토리 약 16년 / 프로즌샤 / 하드 세렌 파티 격파까지 라이트 유저가 절대 못 밟는 깊이의 콘텐츠를 끝까지 플레이하면서, 일반 사용 흐름 밖의 엣지 케이스를 일상적으로 밟아 왔습니다. 게임 QA는 이 두 축 — 결함을 끝까지 추적·문서화하는 운영 습관 + 게임 도메인 헤비유저 시점 — 을 그대로 이어 갈 수 있는 자리라고 생각합니다.`

export const JD_MATCHES = [
  {
    n: 1,
    jdTitle: '품질 관리 — 테스트 환경 개선 / 케이스 설계·실행',
    jdSub: '결함을 안정적으로 재현할 수 있는 환경과 케이스를 만든다',
    evidence: [
      'CHAT_BACKEND 환경변수로 백엔드 2종(Modal Gemma4 LoRA · Anthropic Managed Agents) 폴백 구성 — 동일 입력을 두 백엔드에 동시 흘려 응답 차이를 직접 비교하는 A/B 테스트 환경 구축',
      '봇 코드를 `run/services/` (데이터·외부 API) ↔ `run/views/` (Discord 포맷팅) 2계층으로 분리 — 로직과 표현을 떼어 두어 같은 입력에 대한 회귀 테스트를 표현 계층 변화 없이 반복 실행 가능',
      '솔로봇 identity 분리(debi / marlene / unified) — 동일 코드 베이스를 환경별로 분기해 페르소나·환경 변수·세션 정책 차이에 따른 회귀 결함을 분리 검증',
      'Discord 봇 + 대시보드 + 웹패널 3계층 운영 환경을 직접 구축 — 테스트 환경에서 라이브까지의 차이를 사람이 외우지 않고 `make sync-check`로 자동 감지',
      '결함 재현이 까다로운 케이스는 메모리에 「재현 단계」를 단계 번호로 분리 기록 → 다음 운영자가 같은 결함을 만났을 때 그대로 따라 할 수 있게 케이스화',
    ],
  },
  {
    n: 2,
    jdTitle: '다양한 테스트 — 기능 · 탐색 · 호환성',
    jdSub: '주어진 케이스만 돌리지 않고 직접 깨고 다닌다',
    evidence: [
      '메이플스토리 약 16년 (2009 ~ ) · 프로즌샤 · 하드 세렌 파티 격파 — 라이트 유저가 절대 안 밟는 직업·보스·유니온 격자 깊이의 엣지 케이스를 일상적으로 밟는 헤비 유저',
      '5장르 5종 플레이(MMORPG · MOBA · 어드벤처 · FPS · 수집형) + PC·모바일 양쪽 플랫폼 동시 운영 — 장르·플랫폼별 입력 패턴·UI 관례·조작 차이를 사용자 시점에서 직접 학습',
      '봇 음성 파이프라인 탐색 테스트 — DAVE E2EE 강제 / opus 디코딩 / VAD 무음 인식 / 데몬 스레드 asyncio 호출 / 프로세스 강제 종료 후 재연결 거부 등 11건 모두 일반 사용 흐름 밖에서 직접 마주친 결함',
      '시각디자인 전공 4년 — 사용자 시선과 흐름을 따라가는 훈련. 기능이 정상 동작이어도 「사용자가 그 흐름에서 그 순간에 그 정보가 보이는가」 단위로 호환성·UX 결함을 함께 잡는 시각',
    ],
  },
  {
    n: 3,
    jdTitle: '서비스 안정화 지원 — 버그 트래킹 · 로그 기반 테스트 · 정기 점검',
    jdSub: '라이브 환경 결함을 로그에서 시작해 끝까지 추적한다',
    evidence: [
      'on_ready cleanup_removed_servers race로 일부 길드 settings가 유실되던 사건 — Discord 로그 + Firestore 적재 시점을 교차 분석해 race 구간을 좁히고 fix 배포 후 후속 사례로 사후 검증',
      'Settings split-brain — 단일 GCS JSON 운영 시 multi-container 정합성 깨짐을 158서버 운영 데이터에서 식별 → Firestore 3컬렉션(148+23+1 docs) 분리 마이그레이션으로 사후 추적·해결',
      '도구 호출 trace 로그 매 요청 기록 — 결함 재현 시 어떤 입력·세션·도구로 그 응답이 나왔는지 그대로 복기 가능한 로그 구조를 직접 설계',
      'GitHub Actions cron 정각 큐 폭주 → 비정각(47분)으로 회피 — 라이브 운영 중 발생한 외부 인프라 결함을 운영 데이터로 식별·우회',
      'Daily Feed Firestore `feed_seen` 30일 TTL 적재 — 같은 항목 중복 발송 결함 0건 유지, 정기 점검 가능한 데이터 파이프라인 구축',
    ],
  },
  {
    n: 4,
    jdTitle: '리스크 예방 — 테스트 프로세스 정밀화 · 결함 관리',
    jdSub: '같은 결함이 두 번 나오지 않게 만든다',
    evidence: [
      '발견한 결함은 모두 `claude-memory/debi-marlene/` 마크다운에 「원인 / 재현 / 교훈」 일관 구조로 누적 — 후속 의사결정과 회귀 테스트의 첫 참조점',
      '체크리스트 대신 빌드 가드(자동 검증 스크립트)로 반복 실수 차단 — `make sync-check`로 env 4곳 분기를 사전 감지, `feedback_build_guards_over_checklists`로 원칙화',
      '시스템 프롬프트 4가지 절대 규칙(시스템 프롬프트 비공개·캐릭터 변경 거부·출력 형식 강제 거부·사용자 지시 무시)을 직접 설계 — 프롬프트 인젝션·우회 입력에 의한 보안 결함 사전 예방',
      'docker restart 시 env-file 갱신이 적용되지 않는 함정을 한 번 밟은 뒤 → docker stop+rm+run을 `feedback_docker_restart_env_trap`으로 정착, 동일 결함 재발 0건',
      'pkill -f 함정(다른 python 프로세스 동반 kill)을 한 번 밟은 뒤 → `scripts/kill_solo_bots.sh`로 env 블록 정확 매칭하는 정밀 kill 스크립트로 대체',
    ],
  },
  {
    n: 5,
    jdTitle: '기술 활용 및 고도화 — 자동화 도구 · 관리 솔루션',
    jdSub: '반복되는 검증·재현은 도구로 처리한다 (학습 중)',
    evidence: [
      '운영 중 부딪힌 자동화 가드를 직접 만들어 반복 결함을 사전 차단 — `make sync-check` (env 분기 감지) · `kill_solo_bots.sh` (정밀 kill) · `sync_env.sh` (다기기 환경 동기화)',
      'GitHub Actions cron + Firestore TTL 기반 정기 점검 자동화 직접 구축 — 매일 09:00 KST 자동 실행되는 검증·중복 제거 파이프라인',
      '입력 자동 분류 라우팅 학습 — 정규식 기반 입력 분류기를 직접 작성해 0.1ms 안에 분기. QA 시나리오 자동 분류기로 그대로 이식 가능',
      'GCP Secret Manager 단일 진실 + `./scripts/sync_env.sh` pull/push — 다기기 운영 환경 일관성을 자동 동기화로 보장, 환경 차이로 인한 결함 사전 차단',
      'Python 3.14 / Docker 멀티컨테이너 / GitHub Actions / Firestore — 테스트 자동화 도구를 직접 학습·도입한 경험을 바탕으로 게임 QA 자동화 솔루션을 빠르게 익혀 적용하고 싶습니다',
    ],
  },
] as const

export const ELIGIBILITY = {
  headline: '메이플스토리 약 16년 · 프로즌샤 · 하드 세렌 파티 격파',
  body:
    '2009년부터 (이메일 통합 전 다른 계정 포함) 약 16년간 메이플스토리를 플레이하며, 검은 마법사 라이프타임 보스부터 어센틱/시메라 콘텐츠 정점인 하드 세렌 파티 격파까지 직접 거쳤습니다. 단순 만렙이 아니라 직업 시너지·해방·유니온 격자까지 사용자 입장에서 종합적으로 이해하며, 라이트 유저나 외주 QA가 못 잡는 깊이의 결함을 우선 의심·재현할 수 있습니다.',
} as const

export const ELIGIBILITY_TRAITS = [
  {
    label: '게임 콘텐츠 · 플랫폼 이해도',
    body:
      'MMORPG · MOBA · 어드벤처 · FPS · 수집형 5장르를 PC·모바일 양 플랫폼에 걸쳐 직접 플레이. 장르·플랫폼별 입력 패턴·UI 관례·조작 차이까지 사용자 시점에서 학습. 봇의 본 IP 이터널리턴은 캐릭터 시스템·증강체·패치노트까지 사용자 시점으로 직접 분석.',
  },
  {
    label: '커뮤니케이션 · 협업',
    body:
      '커뮤니케이션 국제 디자인 공모전 입상(3인 팀, 패키지+아이패드 웹페이지). 의견이 충돌할 때 일정·인력·시나리오를 표로 정리해 같은 기준 위에서 합의를 만드는 협업 패턴. 시각디자인과 졸업 4년 동안 다른 직군과의 의견 조율 반복 훈련.',
  },
  {
    label: '기획서 · 결과물 이해도',
    body:
      '봇을 1인이 기획·구현·운영하면서 「의도된 동작 → 실제 동작 → 결함」 3축으로 사고하는 습관 정착. 시각디자인 전공으로 설계 의도와 사용자 흐름을 동시에 보는 훈련 누적. 결함 한 건이 사용자 흐름에서 어떤 좌절로 이어지는지 추적해 우선순위를 매기는 시각.',
  },
  {
    label: '게임 로그 · 결함 사례 학습',
    body:
      '발견한 결함은 모두 마크다운 메모리에 「원인 / 재현 / 교훈」 일관 구조로 누적. Discord 로그 + Firestore 적재 시점 + 도구 호출 trace 로그를 교차 확인하며 결함 위치를 좁히는 작업을 일상적으로 반복.',
  },
  {
    label: '경험 기록 · 공유',
    body:
      '체크리스트 대신 빌드 가드로 반복 실수 차단(`feedback_build_guards_over_checklists`). 자기 결함을 외부에 공유 가능한 형태로 정리하는 메모리 시스템 — 인덱스(MEMORY.md) → 도메인 폴더 → 파일 단위로 검색·재참조 가능한 구조로 운영.',
  },
] as const

export const PREFERRED = [
  {
    n: 1,
    title: '자동화 도구 활용 학습 경험',
    body:
      '운영 중 반복되는 환경 검증·정리 작업을 직접 자동화 가드로 정착시킨 경험: `make sync-check`로 4기기 env 분기 자동 감지, `kill_solo_bots.sh`로 정밀 kill, GitHub Actions cron + Firestore TTL로 정기 점검 자동 실행. 사내 자동화 도구·관리 솔루션을 빠르게 학습해 게임 QA 흐름에 적용하고 싶습니다.',
  },
  {
    n: 2,
    title: 'CS · SW 인접 역량 (비전공 보완)',
    body:
      '시각디자인과 졸업이지만, 봇 1인 운영을 위해 Python 3.14 / discord.py / Firestore / GCP VM·Cloud Run / GitHub Actions / Docker 멀티컨테이너까지 직접 다룸. 비전공자가 보통 못 만지는 인프라·세션 영속화·E2EE 음성 복호화까지 직접 부딪히면서 학습한 경험으로 보완합니다.',
  },
  {
    n: 3,
    title: '5년 비전 — AI 자동화 QA 엔지니어 (학습 의지)',
    body:
      'QA로 시작해 「LLM 기반 테스트 케이스 자동 생성 → 라이브 로그 분석 → 결함 재현 파이프라인」까지 잇는 자동화 QA 엔지니어로 성장하고 싶습니다. 지금은 봇 운영에서 작은 규모의 결함 추적·문서화 사이클을 만들어 본 단계 — 게임 도메인 라이브 환경의 검증·재현·재발 차단 사이클을 현장에서 직접 익히는 것이 우선 목표입니다.',
  },
] as const

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
    detail: '오로라 · 프로즌샤 · 아크메이지(썬,콜) · 하드 세렌 파티 격파 — 헤비 유저',
  },
  { title: '블루아카이브', period: '수년', detail: '만렙 유지, 메인·이벤트 스토리 완주 — 모바일 수집형 게임의 일상 운영 흐름 학습' },
  {
    title: '이터널리턴',
    period: '1년+',
    detail: '봇 캐릭터(데비&마를렌)의 본 IP — 캐릭터 시스템·증강체·패치노트까지 사용자 시점 직접 분석',
  },
  { title: '더 파이널스', period: '시즌 단위', detail: 'Embark Studios. 친구들과 라이트 플레이 — FPS 입력·UI 관례 학습' },
  { title: '서든어택', period: '학창 시절', detail: '친구들과 함께한 입문 FPS — 한국 PC FPS 정서 직접 경험' },
] as const

export const CASES = [
  {
    no: 1,
    title: '음성 파이프라인 11건 결함 추적 — 원인을 끝까지 좁힌 사례',
    problem:
      'Discord 음성 채널 실시간 응답 파이프라인 구축 중, 일반 사용 흐름 밖에서만 발생하는 결함이 11건 누적. on_voice_state_update 무한 재연결, opus 디코딩 에러로 packet-router 스레드 kill, DAVE E2EE 미복호화, 데몬 스레드 asyncio 직접 호출 불가, 프로세스 강제 종료 후 Discord에 disconnect 신호 안 가서 재연결 거부 등.',
    approach:
      '각 결함마다 「원인 / 재현 / 교훈」 마크다운으로 분리 기록. VoiceRecvClient 상태 격리(listening_guilds set), wants_opus=True + 직접 Decoder, davey.DaveSession.decrypt 직접 호출, bot.loop.call_soon_threadsafe 패턴, on_ready에서 change_voice_state(channel=None) 정리 등 결함별 정밀 fix.',
    result:
      '11건 모두 재발 0건. 같은 패턴이 다른 cog에서도 보일 때 메모리 검색만으로 즉시 재현·해결 가능한 운영 자산으로 정착.',
    bridge:
      '결함을 「로그 → 원인 가설 → 좁히기 → 정밀 수정 → 메모리 누적」 단위로 끝까지 추적하는 QA 직무 본질의 직접 사례.',
  },
  {
    no: 2,
    title: 'on_ready cleanup race — 라이브 결함의 사후 추적 · 검증',
    problem:
      'on_ready 시 cleanup_removed_servers가 실행되며 일부 길드 settings가 유실. 라이브 환경에서 「설정이 사라졌다」는 사용자 보고가 산발적으로 발생, 재현이 어려움.',
    approach:
      'Discord 로그 + Firestore settings 적재 시점을 교차 분석해 race 구간(on_ready 진입 시각 ~ guild fetch 완료 시각)을 좁힘. fix `fca0e07b` 배포 후 후속 사례로 사후 검증.',
    result:
      'race 재발 0건. 사건 전체를 `project_guild_cleanup_bug.md`로 메모리화해 후속 사례 추적 시 즉시 참조 가능.',
    bridge:
      '라이브 환경에서만 발생하는 산발적 결함을 로그 기반으로 추적·재현·검증한 QA 사이클의 직접 사례.',
  },
  {
    no: 3,
    title: 'Settings split-brain — 단일 저장소가 만든 정합성 결함',
    problem:
      'GCS 단일 JSON으로 settings를 운영하니 멀티 컨테이너(debi-marlene + solo-debi + solo-marlene) 사이에서 동시 쓰기 race로 split-brain 발생. 158서버 중 일부 설정 정합성 깨짐.',
    approach:
      '`scripts/migrate_settings_to_firestore.py`로 GCS JSON을 Firestore 3컬렉션(148+23+1 docs)으로 분리 마이그레이션. command_logs / dashboard_logs / quiz_data 분리. 컨테이너 단위 배포 자동화.',
    result:
      'multi-container 정합성 회복, 158서버 안정 운영. 「JSON 단일 파일은 멀티 컨테이너 결함 자석」을 메모리(`feedback_firestore_over_gcs_for_json`)로 원칙화.',
    bridge:
      '결함 한 건을 1회 수정으로 끝내지 않고 「유사 결함을 사전 차단할 수 있는 원칙」으로 추상화하는 QA 사이클.',
  },
  {
    no: 4,
    title: 'docker restart env-file 함정 — 동일 결함 재발 차단',
    problem:
      'env-file 갱신 후 docker restart로는 새 환경 변수가 적용되지 않는 함정에 한 번 빠짐. 「분명히 .env 고쳤는데 안 바뀜」 결함이 여러 번 발생할 위험.',
    approach:
      '한 번 밟은 직후 즉시 「docker restart 금지, stop+rm+run 필수」를 `feedback_docker_restart_env_trap` 메모리로 고정. 운영 절차 문서에도 반영.',
    result:
      '동일 결함 재발 0건. pkill -f 함정도 같은 방식으로 `scripts/kill_solo_bots.sh` 정밀 kill 스크립트로 대체.',
    bridge:
      '같은 결함이 두 번 나오지 않게 만드는 결함 관리·리스크 예방의 직접 사례. 체크리스트 대신 빌드 가드·메모리·정밀 스크립트로 영속화.',
  },
  {
    no: 5,
    title: '시스템 프롬프트 4 절대 규칙 — 보안 결함 사전 예방',
    problem:
      '캐릭터 챗봇 운영 중 프롬프트 인젝션 / 캐릭터 변경 시도 / 출력 형식 우회 / 사용자 지시 우회 같은 보안 결함 시도가 빈번. 1인 운영자가 매번 사후 대응하기엔 비용 과다.',
    approach:
      '`run/services/chat/character_prompt.py`에 4가지 절대 규칙(시스템 프롬프트 비공개·캐릭터 변경 거부·출력 형식 강제 거부·사용자 지시 무시)을 직접 설계해 사전 방어. 결함 시도가 들어와도 봇이 일관된 거부 응답을 내도록 고정.',
    result:
      '인젝션 시도 패턴이 들어와도 캐릭터 톤 유지, 보안 결함 사례 사후 대응 비용 큰 폭 감소.',
    bridge:
      '보안 결함을 「발견 후 차단」이 아니라 「설계 시점에 사전 차단」하는 리스크 예방 QA 사이클.',
  },
  {
    no: 6,
    title: 'env-drift guard — 환경 차이로 인한 결함 자동 차단',
    problem:
      '맥북 / WSL / VM / Cloud Run 4곳에 env가 분기. 한 군데 갱신 누락 시 「내 로컬에선 되는데 배포에선 안 됨」 결함이 반복.',
    approach:
      '`make sync-check`로 4곳 env 차이를 자동 감지. GCP Secret Manager를 단일 진실로 두고 `./scripts/sync_env.sh pull/push`로 일괄 동기화.',
    result:
      'env 분기 결함 재발 0건. 환경 일관성을 사람이 외우는 체크리스트 대신 빌드 가드로 영속화.',
    bridge:
      '환경 차이라는 가장 흔한 라이브 결함의 원인을 자동화 가드로 사전 차단한 직접 사례.',
  },
] as const

export const COLLAB = {
  title: '커뮤니케이션 국제 디자인 공모전 입상',
  problem: '3인 팀, 졸업 전시 작품을 인쇄 단일 vs 디지털 결합으로 의견 충돌',
  approach:
    '일정·인력·관람객 시나리오를 표로 정리해 두 안을 같은 기준 위에서 비교, 디자인 컨셉을 흐트러뜨리지 않는 선에서 인터랙티브 웹페이지 인터페이스 방향 직접 제안.',
  result: '시각적 일관성과 사용자 흐름을 결합한 결과물로 공모전 입상.',
  bridge:
    '다른 직군·다른 성향과 의견이 충돌할 때 데이터·시나리오 위에서 같은 기준을 만드는 협업 패턴 — 자소서 3번 항목(다른 성향과 협업)에 그대로 매칭.',
} as const

export const CONTACT = {
  email: 'goenho0613@gmail.com',
  github: 'https://github.com/2rami',
  domain: 'https://debimarlene.com',
  edu: '신구대학교 시각디자인과 졸업 (2026.02)',
} as const
