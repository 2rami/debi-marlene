/**
 * Hero 비교 페이지 — v1(다크 인디고·골드) vs v2(밝은 크림·명조)
 * /portfolio/smilegate-compare
 * 거노 결정용 임시 라우트. 결정 후 PortfolioSmilegate.tsx 에 통일 적용.
 */

const FONT_BODY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, '맑은 고딕', 'Malgun Gothic', Pretendard, 'Apple SD Gothic Neo', sans-serif"
const FONT_DISPLAY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, '맑은 고딕', 'Malgun Gothic', Pretendard, sans-serif"
const FONT_SERIF = "'Charter', 'Iowan Old Style', 'Noto Serif KR', 'KoPub Batang', '바탕', Georgia, serif"
const FONT_MONO = "'JetBrains Mono', 'IBM Plex Mono', 'SF Mono', Menlo, Consolas, monospace"

// ────────────────────────────────────────────────
// V1: 다크 인디고 + 골드 + 텍스처
// ────────────────────────────────────────────────

function HeroV1() {
  const C = {
    bg: '#0a0e1a',
    bgRadial: 'radial-gradient(ellipse at 80% 20%, rgba(212, 168, 58, 0.12), transparent 55%), radial-gradient(ellipse at 10% 85%, rgba(120, 80, 200, 0.08), transparent 50%)',
    surface: 'rgba(255, 255, 255, 0.03)',
    border: 'rgba(255, 255, 255, 0.08)',
    borderSoft: 'rgba(255, 255, 255, 0.04)',
    ink: '#f4ecd8',
    inkSoft: '#a8a293',
    inkMuted: '#62604f',
    gold: '#e0b96b',
    goldDeep: '#b8923d',
    accent: '#f0c870',
  }

  return (
    <div style={{
      background: C.bg,
      backgroundImage: C.bgRadial,
      fontFamily: FONT_BODY,
      color: C.ink,
      minHeight: '100vh',
      padding: '64px 80px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* film grain */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.85\' /%3E%3CfeColorMatrix values=\'0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.4 0\' /%3E%3C/filter%3E%3Crect width=\'200\' height=\'200\' filter=\'url(%23n)\' /%3E%3C/svg%3E")',
        opacity: 0.04,
        mixBlendMode: 'overlay',
      }} />

      <div style={{ maxWidth: 1080, margin: '0 auto', position: 'relative' }}>
        {/* Top bar */}
        <header style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          paddingBottom: 24, borderBottom: `1px solid ${C.border}`,
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
            <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.gold, letterSpacing: '0.1em' }}>
              V1 · DARK INDIGO
            </span>
            <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.08em' }}>
              SMILEGATE RPG / LOST ARK / DBA
            </span>
          </div>
          <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted }}>
            2026.04 · 신입 지원
          </span>
        </header>

        {/* Main asymmetric composition */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '7fr 4fr',
          gap: 48,
          marginTop: 88,
          alignItems: 'start',
        }}>
          {/* Left — headline */}
          <div>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 12,
              marginBottom: 36,
            }}>
              <span style={{ width: 32, height: 1, background: C.gold }} />
              <span style={{
                fontFamily: FONT_MONO, fontSize: 11, color: C.gold,
                letterSpacing: '0.18em', textTransform: 'uppercase',
              }}>
                Portfolio · Geonho Yang
              </span>
            </div>

            <h1 style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 92,
              fontWeight: 800,
              lineHeight: 0.98,
              letterSpacing: '-0.035em',
              margin: '0 0 32px',
              color: C.ink,
            }}>
              데이터를 <span style={{ color: C.gold, fontStyle: 'italic', fontWeight: 700 }}>다치게 하지</span> 않는 일.
            </h1>

            <p style={{
              fontSize: 17, lineHeight: 1.75, color: C.inkSoft,
              maxWidth: 520, margin: 0,
            }}>
              디스코드 봇을 1인으로 24/7 운영하며 데이터 모델 설계,
              무중단 마이그레이션, 정합성 진단을 현장에서 익혀 왔습니다.
              화려한 산출물보다 라이브 서비스의 데이터를 지켜내는 일이
              가장 단단한 기여라고 믿습니다.
            </p>
          </div>

          {/* Right — vertical metric stack */}
          <aside style={{
            border: `1px solid ${C.border}`,
            background: C.surface,
            backdropFilter: 'blur(8px)',
            padding: '32px 28px',
          }}>
            <div style={{
              fontFamily: FONT_MONO, fontSize: 10, color: C.gold,
              letterSpacing: '0.18em', textTransform: 'uppercase',
              marginBottom: 24, paddingBottom: 12,
              borderBottom: `1px solid ${C.borderSoft}`,
            }}>
              Operating · Live
            </div>
            {[
              { v: '6+', l: '개월 24/7 운영', sub: 'GCP Compute Engine' },
              { v: '148', l: '디스코드 길드', sub: '실서비스 배포 환경' },
              { v: '172', l: '문서 무중단 이관', sub: 'GCS → Firestore' },
              { v: '7년+', l: '로스트아크 누적', sub: '오픈베타~현재' },
            ].map((m, i, arr) => (
              <div key={i} style={{
                paddingTop: i === 0 ? 0 : 18,
                paddingBottom: i === arr.length - 1 ? 0 : 18,
                borderBottom: i === arr.length - 1 ? 'none' : `1px solid ${C.borderSoft}`,
                display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12,
              }}>
                <div>
                  <div style={{ fontSize: 12, color: C.ink, fontWeight: 500 }}>{m.l}</div>
                  <div style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.inkMuted, marginTop: 2 }}>{m.sub}</div>
                </div>
                <div style={{
                  fontFamily: FONT_DISPLAY, fontSize: 32, fontWeight: 700,
                  color: C.gold, letterSpacing: '-0.02em', lineHeight: 1,
                }}>{m.v}</div>
              </div>
            ))}
          </aside>
        </div>

        {/* Bottom strip */}
        <footer style={{
          marginTop: 96,
          paddingTop: 24,
          borderTop: `1px solid ${C.border}`,
          display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.05em',
        }}>
          <span>github.com/2rami/debi-marlene</span>
          <span>goenho0613@gmail.com</span>
          <span style={{ color: C.gold }}>신구대 시각디자인 · 2026.02 졸업</span>
        </footer>
      </div>
    </div>
  )
}

// ────────────────────────────────────────────────
// V2: 밝은 크림 + 명조 + 골드
// ────────────────────────────────────────────────

function HeroV2() {
  const C = {
    bg: '#f5f0e6',
    bgSoft: '#ebe4d3',
    surface: '#ffffff',
    ink: '#1a1816',
    inkSoft: '#5c574d',
    inkMuted: '#8a847a',
    border: '#d6cfbf',
    borderSoft: '#e4ddcc',
    gold: '#a07f30',
    goldSoft: '#c19c44',
  }

  return (
    <div style={{
      background: C.bg,
      fontFamily: FONT_BODY,
      color: C.ink,
      minHeight: '100vh',
      padding: '64px 80px',
      position: 'relative',
    }}>
      {/* faint texture */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(ellipse at 100% 0%, rgba(160, 127, 48, 0.08), transparent 55%)',
      }} />

      <div style={{ maxWidth: 1080, margin: '0 auto', position: 'relative' }}>
        {/* Top bar */}
        <header style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          paddingBottom: 24, borderBottom: `1px solid ${C.border}`,
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
            <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.gold, letterSpacing: '0.1em' }}>
              V2 · WARM PAPER
            </span>
            <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.08em' }}>
              SMILEGATE RPG / LOST ARK / DBA
            </span>
          </div>
          <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted }}>
            2026.04 · 신입 지원
          </span>
        </header>

        {/* Editorial composition */}
        <div style={{ marginTop: 100, marginBottom: 100 }}>
          <div style={{
            display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 28,
          }}>
            <span style={{
              fontFamily: FONT_SERIF, fontSize: 13, color: C.gold, fontStyle: 'italic',
            }}>
              No. 04 — 경력기술서
            </span>
            <span style={{ flex: 1, height: 1, background: C.border }} />
            <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.05em' }}>
              YANG · GEONHO
            </span>
          </div>

          <h1 style={{
            fontFamily: FONT_SERIF,
            fontSize: 110,
            fontWeight: 400,
            lineHeight: 1.02,
            letterSpacing: '-0.025em',
            margin: '0 0 56px',
            color: C.ink,
          }}>
            데이터를<br />
            <em style={{ fontStyle: 'italic', color: C.gold }}>다치게 하지</em><br />
            않는 일.
          </h1>

          <div style={{
            display: 'grid', gridTemplateColumns: '5fr 6fr', gap: 64,
            paddingTop: 32, borderTop: `2px solid ${C.ink}`,
          }}>
            <p style={{
              fontFamily: FONT_SERIF,
              fontSize: 19, lineHeight: 1.75, color: C.ink,
              margin: 0,
            }}>
              디스코드 봇을 1인으로 24/7 운영하며 데이터 모델 설계,
              무중단 마이그레이션, 정합성 진단을 현장에서 익혀 왔습니다.
            </p>
            <p style={{
              fontSize: 14, lineHeight: 1.85, color: C.inkSoft, margin: 0,
            }}>
              화려한 산출물보다 라이브 서비스의 데이터를 지켜내는 일이
              가장 단단한 기여라고 믿습니다. 단일 GCS JSON에서 출발해
              Firestore 3컬렉션 분리로 정합성을 회복한 운영 사례를 가지고
              스마일게이트 RPG의 라이브 데이터 곁으로 가고자 합니다.
            </p>
          </div>
        </div>

        {/* Numbered metrics */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 0,
          borderTop: `1px solid ${C.border}`, borderBottom: `1px solid ${C.border}`,
        }}>
          {[
            { n: '01', v: '6개월+', l: '24/7 라이브 운영' },
            { n: '02', v: '148', l: '디스코드 길드' },
            { n: '03', v: '172', l: '문서 무중단 이관' },
            { n: '04', v: '7년+', l: '로스트아크 누적' },
          ].map((m, i) => (
            <div key={i} style={{
              padding: '28px 24px',
              borderRight: i < 3 ? `1px solid ${C.borderSoft}` : 'none',
            }}>
              <div style={{
                fontFamily: FONT_MONO, fontSize: 10, color: C.gold,
                letterSpacing: '0.15em', marginBottom: 14,
              }}>{m.n}</div>
              <div style={{
                fontFamily: FONT_SERIF, fontSize: 38, fontWeight: 400,
                letterSpacing: '-0.02em', color: C.ink, lineHeight: 1,
              }}>{m.v}</div>
              <div style={{ fontSize: 11, color: C.inkMuted, marginTop: 10 }}>{m.l}</div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <footer style={{
          marginTop: 64,
          display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.05em',
        }}>
          <span>github.com/2rami/debi-marlene</span>
          <span>goenho0613@gmail.com</span>
          <span style={{ color: C.gold }}>신구대 시각디자인 · 2026.02 졸업</span>
        </footer>
      </div>
    </div>
  )
}

// ────────────────────────────────────────────────

export default function PortfolioSmilegateCompare() {
  return (
    <div>
      {/* Comparison header */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 10,
        background: '#0a0a0b', color: '#fff',
        padding: '14px 24px', borderBottom: '1px solid #2a2a30',
        fontFamily: FONT_MONO, fontSize: 12,
        display: 'flex', justifyContent: 'space-between',
      }}>
        <span style={{ color: '#e0b96b' }}>HERO 톤 비교 — 위 / 아래로 스크롤하며 비교 후 결정</span>
        <span style={{ color: '#666' }}>V1: 다크 인디고 · V2: 밝은 크림 명조</span>
      </div>

      <HeroV1 />
      <HeroV2 />

      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        em { font-style: italic; }
      `}</style>
    </div>
  )
}
