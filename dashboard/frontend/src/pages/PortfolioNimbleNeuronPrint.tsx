/**
 * 님블뉴런 캐릭터 QA 포트폴리오 - PDF 전용 페이지
 * /portfolio/nimble-neuron/print
 * 한 섹션 = 한 페이지. 애니메이션 없음. A4 최적화.
 */

/* ── dak.gg CDN ── */
const CDN = 'https://cdn.dak.gg/assets/er'
const GAME_ASSETS = `${CDN}/game-assets/10.6.0`
const TIER_IMG = (id: number) => `${CDN}/images/rank/full/${id}.png`
const CHAR_PROFILE = (key: string) => `${GAME_ASSETS}/CharProfile_${key}_S000.png`
const ALEX_FULL = `${GAME_ASSETS}/CharResult_Alex_S000.png`

const POPULAR_CHARS = [
  { key: 'Alex', name: '알렉스' }, { key: 'Aya', name: '아야' },
  { key: 'Hyunwoo', name: '현우' }, { key: 'Fiora', name: '피오라' },
  { key: 'Cathy', name: '캐시' }, { key: 'Nadine', name: '나딘' },
  { key: 'Sua', name: '수아' }, { key: 'Eleven', name: '일레븐' },
  { key: 'Lenox', name: '레녹스' }, { key: 'Jackie', name: '재키' },
  { key: 'Hart', name: '하트' }, { key: 'Yuki', name: '유키' },
]

const ALL_TIERS = [
  { id: 1, name: '아이언' }, { id: 2, name: '브론즈' }, { id: 3, name: '실버' },
  { id: 4, name: '골드' }, { id: 5, name: '플래티넘' }, { id: 6, name: '다이아몬드' },
  { id: 66, name: '미스릴' }, { id: 63, name: '메테오라이트' },
  { id: 7, name: '데미갓' }, { id: 8, name: '이터니티' },
]

/* ── Styles ── */
const C = {
  bg: '#1e1f2e',
  card: '#252638',
  cardAlt: '#2a2b40',
  cyan: '#3cabc9',
  pink: '#e58fb6',
  white: '#f0f0f5',
  gray: '#a0a5b4',
  muted: '#6e7382',
  border: '#2d2f41',
  red: '#ed4245',
  yellow: '#faa61a',
  green: '#43b581',
}

/* ── Page wrapper (A4 한 페이지) ── */
function Page({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      background: C.bg,
      padding: '40px 48px',
      pageBreakAfter: 'always',
      minHeight: '100vh',
      boxSizing: 'border-box',
    }}>
      {children}
    </div>
  )
}

/* ── Section Title ── */
function Title({ children, sub }: { children: string; sub?: string }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <h2 style={{ fontSize: 32, fontWeight: 800, margin: 0, color: C.cyan }}>{children}</h2>
      {sub && <p style={{ color: C.gray, fontSize: 14, marginTop: 6 }}>{sub}</p>}
      <div style={{ width: 40, height: 3, background: C.cyan, marginTop: 12, borderRadius: 2 }} />
    </div>
  )
}

/* ── Card ── */
function Card({ children, accent, style: s }: { children: React.ReactNode; accent?: string; style?: React.CSSProperties }) {
  return (
    <div style={{
      background: C.card, border: `1px solid ${C.border}`, borderRadius: 12,
      padding: 16, position: 'relative', overflow: 'hidden', ...s,
    }}>
      {accent && <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 3, background: accent }} />}
      {children}
    </div>
  )
}

/* ── Label ── */
function Label({ children, color = C.cyan }: { children: string; color?: string }) {
  return <span style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.5, color }}>{children}</span>
}

/* ── Tag ── */
function Tag({ children, color = C.cyan }: { children: string; color?: string }) {
  return (
    <span style={{
      display: 'inline-block', padding: '3px 10px', borderRadius: 20, fontSize: 11,
      color, border: `1px solid ${color}33`, background: `${color}11`, marginRight: 6, marginBottom: 4,
    }}>{children}</span>
  )
}

/* ── Bullet ── */
function Bullet({ children, color = C.cyan }: { children: string; color?: string }) {
  return (
    <div style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: color, marginTop: 7, flexShrink: 0 }} />
      <span style={{ fontSize: 13, color: C.gray, lineHeight: 1.6 }}>{children}</span>
    </div>
  )
}

/* ── Troubleshoot Card ── */
function TroubleCard({ title, problem, cause, solution, color }: {
  title: string; problem: string; cause: string; solution: string; color: string
}) {
  return (
    <Card accent={color} style={{ marginBottom: 10 }}>
      <div style={{ paddingLeft: 8 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: C.white, marginBottom: 10 }}>{title}</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div>
            <Label color={C.red}>Problem</Label>
            <p style={{ fontSize: 11, color: C.gray, marginTop: 4, lineHeight: 1.5 }}>{problem}</p>
          </div>
          <div>
            <Label color={C.yellow}>Root Cause</Label>
            <p style={{ fontSize: 11, color: C.gray, marginTop: 4, lineHeight: 1.5 }}>{cause}</p>
          </div>
          <div>
            <Label color={C.green}>Solution</Label>
            <p style={{ fontSize: 11, color: C.gray, marginTop: 4, lineHeight: 1.5 }}>{solution}</p>
          </div>
        </div>
      </div>
    </Card>
  )
}

/* ══════════════════════════════════════════════ */
export default function PortfolioNimbleNeuronPrint() {
  return (
    <div style={{ fontFamily: "'Pretendard', 'Apple SD Gothic Neo', sans-serif", color: C.white, background: C.bg }}>

      {/* ═══ PAGE 1: HERO ═══ */}
      <Page>
        <div style={{ display: 'flex', alignItems: 'center', minHeight: 'calc(100vh - 80px)' }}>
          <div style={{ flex: 1 }}>
            <div style={{
              display: 'inline-block', padding: '4px 14px', borderRadius: 20, fontSize: 11,
              fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase',
              color: C.muted, border: `1px solid ${C.border}`, marginBottom: 20,
            }}>Nimble Neuron -- Character QA</div>

            <h1 style={{ fontSize: 48, fontWeight: 800, lineHeight: 1.2, margin: '0 0 8px', color: C.cyan }}>양건호</h1>

            <h2 style={{ fontSize: 36, fontWeight: 800, margin: '0 0 24px', color: C.white }}>
              이터널 리턴 <span style={{ color: C.cyan }}>캐릭터 QA</span>
            </h2>

            <p style={{ fontSize: 16, color: C.gray, lineHeight: 1.7, maxWidth: 400, marginBottom: 32 }}>
              1,100시간의 코어 플레이 경험과<br />
              게임 데이터 분석 역량을 갖춘 QA 지원자.
            </p>

            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, maxWidth: 480 }}>
              {[
                { img: TIER_IMG(63), value: '메테오라이트', label: '현재 티어' },
                { img: null, value: '1,100+', label: '플레이 시간' },
                { img: TIER_IMG(66), value: '미스릴+', label: '시즌7~' },
                { img: CHAR_PROFILE('Alex'), value: '알렉스', label: '주 캐릭터' },
              ].map((s, i) => (
                <div key={i} style={{ textAlign: 'center', padding: '14px 8px', background: C.card, borderRadius: 12, border: `1px solid ${C.border}` }}>
                  {s.img ? <img src={s.img} alt="" style={{ width: 32, height: 32, objectFit: 'contain', marginBottom: 6 }} />
                         : <div style={{ width: 32, height: 32, marginBottom: 6 }} />}
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.cyan }}>{s.value}</div>
                  <div style={{ fontSize: 10, color: C.muted, marginTop: 2 }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Links */}
            <div style={{ marginTop: 28, padding: '14px 18px', background: C.card, border: `1px solid ${C.border}`, borderRadius: 12 }}>
              <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: C.cyan, marginBottom: 8 }}>
                Web Portfolio (더 자세한 내용)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <svg viewBox="0 0 24 24" fill="none" stroke={C.cyan} strokeWidth={1.5} width={14} height={14}><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                <span style={{ fontSize: 13, color: C.white, fontWeight: 500 }}>debimarlene.com/portfolio/nimble-neuron</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <svg viewBox="0 0 24 24" fill={C.gray} width={14} height={14}><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                <span style={{ fontSize: 13, color: C.gray }}>github.com/2rami/debi-marlene</span>
              </div>
              <p style={{ fontSize: 11, color: C.muted, marginTop: 8 }}>
                * 인터랙티브 UI, 실험체 이미지, 트러블슈팅 상세 등 웹에서 더 자세히 확인할 수 있습니다.
              </p>
            </div>
          </div>

          {/* Alex */}
          <div style={{ width: 280, flexShrink: 0, textAlign: 'right' }}>
            <img src={ALEX_FULL} alt="Alex" style={{ width: '100%', objectFit: 'contain', opacity: 0.85 }} />
          </div>
        </div>
      </Page>

      {/* ═══ PAGE 2: 공고 매칭 ═══ */}
      <Page>
        <Title sub="필수/우대 요건에 대한 경험 매칭">공고 매칭</Title>

        <Label>REQUIRED</Label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginTop: 10, marginBottom: 24 }}>
          {[
            { n: '1', title: '전투 시스템 이해', req: 'MOBA, PvP 전투 시스템 높은 이해도', match: '메테오라이트 티어, 1,100시간+. 스킬 구조, 빌드 경로, 전투 타이밍, 메타 변화에 대한 깊은 이해.' },
            { n: '2', title: '전투 메커니즘 분석', req: '스킬 구조, 상성 분석 및 논리적 설명', match: 'dak.gg API로 50+ 캐릭터 승률/픽률/티어 통계 시스템 직접 설계. 밸런스 변동을 정량적으로 분석.' },
            { n: '3', title: '커뮤니케이션', req: '이슈 원인 파악 + 유관 부서 소통', match: '디스코드 커뮤니티 운영. dak.gg API 리버스 엔지니어링으로 이슈 원인 추적. 개발 경험 기반 기술적 소통.' },
          ].map(item => (
            <Card key={item.n}>
              <div style={{ width: 24, height: 24, borderRadius: '50%', background: `${C.cyan}1a`, border: `1px solid ${C.cyan}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: C.cyan }}>{item.n}</span>
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.white, marginBottom: 4 }}>{item.title}</div>
              <div style={{ fontSize: 10, color: C.muted, marginBottom: 8 }}>{item.req}</div>
              <div style={{ fontSize: 12, color: C.gray, lineHeight: 1.6 }}>{item.match}</div>
            </Card>
          ))}
        </div>

        <Label color={C.pink}>PREFERRED</Label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginTop: 10 }}>
          {[
            { n: '1', title: '협업 툴', req: 'Jira, Confluence, Slack 등', match: 'Git/GitHub 버전 관리 및 이슈 트래킹. Discord 커뮤니티 운영. Docker/Makefile 배포 자동화.' },
            { n: '2', title: '코어 플레이어', req: '코어 레벨 수준 게임 플레이', match: '메테오라이트 티어 (상위). 4시즌 연속 플레이로 메타 변화 전체를 체감.' },
            { n: '3', title: 'QA 포트폴리오', req: '게임 분석서 혹은 QA 포트폴리오', match: '이터널 리턴 전적/통계 분석 봇을 직접 개발 운영. 데이터 수집/시각화 시스템이 곧 포트폴리오.' },
          ].map(item => (
            <Card key={item.n}>
              <div style={{ width: 24, height: 24, borderRadius: '50%', background: `${C.pink}1a`, border: `1px solid ${C.pink}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: C.pink }}>{item.n}</span>
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.white, marginBottom: 4 }}>{item.title}</div>
              <div style={{ fontSize: 10, color: C.muted, marginBottom: 8 }}>{item.req}</div>
              <div style={{ fontSize: 12, color: C.gray, lineHeight: 1.6 }}>{item.match}</div>
            </Card>
          ))}
        </div>
      </Page>

      {/* ═══ PAGE 3: 게임 데이터 분석 ═══ */}
      <Page>
        <Title sub="Debi & Marlene Discord Bot -- 이터널 리턴 전적/통계 분석 시스템">게임 데이터 분석</Title>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 16 }}>
          <Card accent={C.cyan}>
            <div style={{ paddingLeft: 8 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.cyan, marginBottom: 8 }}>데이터 수집 및 구조화</div>
              <Bullet>dak.gg Network 탭 분석으로 비공개 API 엔드포인트 전수 수집/문서화</Bullet>
              <Bullet>50+ 캐릭터, 무기, 특성, 전술스킬, 아이템, 날씨 데이터 구조화</Bullet>
              <Bullet>캐릭터-무기-특성 조합별 승률/픽률 데이터 정규화</Bullet>
            </div>
          </Card>
          <Card accent={C.pink}>
            <div style={{ paddingLeft: 8 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.pink, marginBottom: 8 }}>시각화 및 UI</div>
              <Bullet color={C.pink}>matplotlib MMR 추이 그래프 (다크테마 최적화)</Bullet>
              <Bullet color={C.pink}>Components V2 LayoutView 모던 UI</Bullet>
              <Bullet color={C.pink}>티어별/기간별 필터, 승률/픽률/티어순 정렬</Bullet>
            </div>
          </Card>
        </div>

        {/* 실험체 그리드 */}
        <Card style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: C.muted, marginBottom: 10 }}>
            봇이 관리하는 실험체 데이터 (dak.gg CDN)
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {POPULAR_CHARS.map(c => (
              <div key={c.key} style={{ textAlign: 'center' }}>
                <img src={CHAR_PROFILE(c.key)} alt={c.name} style={{
                  width: 40, height: 40, borderRadius: 8, objectFit: 'cover',
                  border: c.key === 'Alex' ? `2px solid ${C.cyan}` : `1px solid ${C.border}`,
                }} />
                <div style={{ fontSize: 9, color: c.key === 'Alex' ? C.cyan : C.muted, marginTop: 2 }}>{c.name}</div>
              </div>
            ))}
            <div style={{ width: 40, height: 40, borderRadius: 8, border: `1px dashed ${C.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ fontSize: 12, color: C.muted }}>+75</span>
            </div>
          </div>
        </Card>

        {/* 티어 */}
        <Card>
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: C.muted, marginBottom: 10 }}>
            티어별 데이터 필터링 시스템
          </div>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            {ALL_TIERS.map(t => (
              <div key={t.id} style={{
                textAlign: 'center', padding: '4px 6px', borderRadius: 8,
                ...(t.id === 63 ? { background: `${C.cyan}15`, outline: `1px solid ${C.cyan}44` } : {}),
              }}>
                <img src={TIER_IMG(t.id)} alt={t.name} style={{ width: 28, height: 28, objectFit: 'contain' }} />
                <div style={{ fontSize: 8, color: t.id === 63 ? C.cyan : C.muted, fontWeight: t.id === 63 ? 700 : 400 }}>{t.name}</div>
              </div>
            ))}
          </div>
        </Card>
      </Page>

      {/* ═══ PAGE 4: 트러블슈팅 ═══ */}
      <Page>
        <Title sub="봇 개발/운영 중 만난 실제 문제들과 해결 과정">트러블슈팅</Title>

        <Label>API & DATA</Label>
        <div style={{ marginTop: 8, marginBottom: 16 }}>
          <TroubleCard color={C.cyan}
            title="dak.gg API 리버스 엔지니어링"
            problem="공식 API 문서가 존재하지 않아 봇에 필요한 데이터를 확보할 수 없었음."
            cause="dak.gg는 내부 API만 사용. 엔드포인트 구조, 파라미터, 응답 형식이 모두 비공개."
            solution="Chrome DevTools Network 탭에서 API 호출 패턴을 체계적으로 분석. 요청/응답 구조 문서화, 파라미터 조합 테스트로 전체 엔드포인트 수집."
          />
          <TroubleCard color={C.cyan}
            title="API 응답 구조 예고 없는 변경"
            problem="dak.gg API 응답 필드가 예고 없이 변경되어 봇 명령어 일괄 오류 발생."
            cause="비공개 API 특성상 변경 공지 없음. 응답 JSON 필드명/구조 변경 시 파서가 즉시 깨짐."
            solution="에러 로그 + 유저 리포트로 즉시 감지. 필드 구조 분석 후 파서 업데이트, 방어적 코딩 추가."
          />
        </div>

        <Label color={C.pink}>VOICE & TTS</Label>
        <div style={{ marginTop: 8 }}>
          <TroubleCard color={C.pink}
            title="음성 채널 TTS/음악 동시접속 충돌"
            problem="TTS와 음악 재생이 동시에 같은 음성 클라이언트를 사용하면서 오디오 충돌."
            cause="discord.py VoiceClient는 단일 AudioSource만 지원. TTS와 음악이 서로 덮어쓰는 구조."
            solution="VoiceManager로 음성 클라이언트 중앙 관리. TTS/음악 우선순위 큐 구현으로 충돌 없이 순차 재생."
          />
          <TroubleCard color={C.pink}
            title="CosyVoice3 TTS 비트박스 현상"
            problem="T4 GPU에서 파인튜닝된 CosyVoice3 모델 추론 시 음성 대신 비트박스 소리 출력."
            cause="pretrained checkpoint가 bfloat16 저장. T4는 bfloat16 하드웨어 미지원. 모델 로드 시 weight가 다시 bfloat16으로 덮어씌워짐."
            solution="T4에서 bfloat16 소프트웨어 에뮬레이션 강제. transformers 4.51.3 버전 고정으로 attention 충돌 방지."
          />
        </div>
      </Page>

      {/* ═══ PAGE 5: 플레이 경험 ═══ */}
      <Page>
        <Title>플레이 경험</Title>

        {/* Player info */}
        <Card style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ position: 'relative', flexShrink: 0 }}>
            <img src={CHAR_PROFILE('Alex')} alt="Alex" style={{ width: 56, height: 56, borderRadius: 12, objectFit: 'cover' }} />
            <img src={TIER_IMG(63)} alt="" style={{ width: 22, height: 22, position: 'absolute', bottom: -4, right: -4, objectFit: 'contain' }} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: C.white }}>양건호</div>
            <div style={{ fontSize: 12, color: C.muted }}>메테오라이트 | 알렉스 | 1,100시간+ | 시즌7~</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {[{ l: '시즌', v: '4' }, { l: '시간', v: '1,100+' }, { l: '최고', v: '메테오라이트' }].map(s => (
              <div key={s.l} style={{ textAlign: 'center', padding: '6px 12px', background: C.cardAlt, borderRadius: 8 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: C.cyan }}>{s.v}</div>
                <div style={{ fontSize: 9, color: C.muted }}>{s.l}</div>
              </div>
            ))}
          </div>
        </Card>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: C.white, marginBottom: 10 }}>게임 이해도</div>
            <Bullet>캐릭터별 스킬 구조, 쿨다운, 계수, 상호작용 메커니즘 숙지</Bullet>
            <Bullet>캐릭터 상성 관계 및 매치업별 전략 이해</Bullet>
            <Bullet>패치 노트 분석을 통한 메타 변화 예측 및 적응</Bullet>
            <Bullet>빌드 경로(무기/방어구/특성/전술스킬) 최적화 경험</Bullet>
            <Bullet>고티어 환경에서의 엣지 케이스 및 비정상 상호작용 인지</Bullet>
          </div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: C.white, marginBottom: 10 }}>커뮤니티 활동</div>
            <p style={{ fontSize: 13, color: C.gray, lineHeight: 1.7, marginBottom: 16 }}>
              디스코드 서버를 운영하며 유저들의 피드백을 수집하고,
              게임 내 이슈나 밸런스에 대한 토론을 주도한 경험이 있습니다.
              유저 관점에서의 불편함과 개발자 관점에서의 기술적 제약을
              동시에 이해하며 소통할 수 있습니다.
            </p>

            <div style={{ fontSize: 14, fontWeight: 700, color: C.white, marginBottom: 10 }}>부가 기능</div>
            <Bullet color={C.pink}>AI 대화 -- Claude API 기반 캐릭터 페르소나 대화</Bullet>
            <Bullet color={C.pink}>TTS -- CosyVoice3 파인튜닝 모델로 캐릭터 음성 합성</Bullet>
            <Bullet color={C.pink}>음악 -- YouTube 기반 음악 재생 + 노래 퀴즈</Bullet>
          </div>
        </div>
      </Page>

      {/* ═══ PAGE 6: 개발 역량 ═══ */}
      <Page>
        <Title sub="버그 리포트 품질과 유관 부서 소통에 도움이 되는 기술적 배경">개발 역량</Title>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 20 }}>
          {[
            { title: 'Backend', color: C.cyan, techs: ['Python', 'discord.py', 'Flask', 'Gunicorn'] },
            { title: 'Frontend', color: C.pink, techs: ['React 19', 'TypeScript', 'Vite', 'Tailwind 4'] },
            { title: 'Infra', color: '#7DE8ED', techs: ['GCP VM', 'GCS', 'Docker', 'nginx', 'Makefile'] },
          ].map(g => (
            <Card key={g.title}>
              <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: g.color, marginBottom: 10 }}>{g.title}</div>
              <div>{g.techs.map(t => <Tag key={t} color={g.color}>{t}</Tag>)}</div>
            </Card>
          ))}
        </div>

        <div style={{ fontSize: 14, fontWeight: 700, color: C.white, marginBottom: 12 }}>QA 역량과의 연결</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 24 }}>
          {[
            { n: '1', title: '테스트 케이스 설계', desc: '블랙박스 상태의 시스템에서 동작을 분석하고 문서화하는 능력' },
            { n: '2', title: '버그 재현 및 원인 분석', desc: '예상과 다른 응답을 발견했을 때 근본 원인을 추적하는 습관' },
            { n: '3', title: '리스크 평가', desc: '변경사항이 전체 시스템에 미치는 영향을 파악하는 시각' },
          ].map(item => (
            <Card key={item.n}>
              <div style={{ width: 24, height: 24, borderRadius: '50%', background: `${C.cyan}1a`, border: `1px solid ${C.cyan}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: C.cyan }}>{item.n}</span>
              </div>
              <div style={{ fontSize: 12, fontWeight: 700, color: C.white, marginBottom: 4 }}>{item.title}</div>
              <div style={{ fontSize: 11, color: C.gray, lineHeight: 1.5 }}>{item.desc}</div>
            </Card>
          ))}
        </div>

        {/* 끝맺음 */}
        <div style={{ textAlign: 'center', paddingTop: 20, borderTop: `1px solid ${C.border}` }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: C.white, marginBottom: 8 }}>
            이터널 리턴을 가장 많이 플레이한 QA가 되겠습니다.
          </div>
          <p style={{ fontSize: 13, color: C.gray }}>
            1,100시간의 코어 플레이 경험과 데이터 분석 역량으로, 게임의 품질을 유저 눈높이에서 지키겠습니다.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 12 }}>
            <span style={{ fontSize: 12, color: C.muted }}>github.com/2rami/debi-marlene</span>
            <span style={{ color: C.border }}>|</span>
            <span style={{ fontSize: 12, color: C.muted }}>debimarlene.com</span>
          </div>
        </div>
      </Page>

      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        @page { margin: 0; size: A4; }
        @media print { * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; } }
        img { display: inline-block; }
      `}</style>
    </div>
  )
}
