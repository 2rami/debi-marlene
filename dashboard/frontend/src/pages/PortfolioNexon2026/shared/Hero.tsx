import { C, FONT_MONO } from './colors'
import FloatingShapes from './FloatingShapes'

interface HeroProps {
  badge: string
  jobCode: string  // 직무 코드 (LLM EVALUATOR / GAME SERVICE / GAME QA)
  title: string  // 두 줄 가능 (\n)
  subtitle: string
  ctas: { label: string; href: string; primary?: boolean }[]
}

export default function Hero({ badge, jobCode, title, subtitle, ctas }: HeroProps) {
  return (
    <section
      style={{
        position: 'relative',
        minHeight: 'min(900px, 100vh)',
        padding: '64px 48px',
        overflow: 'hidden',
      }}
    >
      <FloatingShapes />

      {/* 매거진 헤더 (Smilegate 패턴 차용) */}
      <header
        style={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          maxWidth: 1200,
          margin: '0 auto',
          paddingBottom: 24,
          borderBottom: `1px solid rgba(245, 250, 249, 0.3)`,
          color: C.inverse,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
          <span style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: '0.08em', opacity: 0.85 }}>
            PORTFOLIO · {jobCode}
          </span>
        </div>
        <span style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: '0.05em', opacity: 0.85 }}>
          YANG · GEONHO / 2026
        </span>
      </header>

      {/* 본 컨텐츠 */}
      <div
        style={{
          maxWidth: 1200,
          margin: '0 auto',
          position: 'relative',
          zIndex: 1,
          paddingTop: 80,
          paddingBottom: 40,
        }}
      >
        {/* Badge */}
        <div
          style={{
            display: 'inline-block',
            padding: '8px 16px',
            background: C.lime,
            color: C.ink,
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            borderRadius: 9999,
            marginBottom: 32,
          }}
        >
          {badge}
        </div>

        {/* No 표기 + 본명 */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 28 }}>
          <span style={{ fontFamily: FONT_MONO, fontSize: 13, color: C.honey, letterSpacing: '0.05em' }}>
            {jobCode} — 양건호
          </span>
          <span style={{ flex: 1, height: 1, background: 'rgba(245, 250, 249, 0.3)' }} />
        </div>

        {/* Title */}
        <h1
          style={{
            fontSize: 'clamp(40px, 7.5vw, 84px)',
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: '-0.02em',
            color: C.inverse,
            margin: 0,
            marginBottom: 32,
            whiteSpace: 'pre-line',
            textShadow: '0 2px 16px rgba(26, 43, 71, 0.2)',
          }}
        >
          {title}
        </h1>

        {/* Subtitle */}
        <p
          style={{
            fontSize: 'clamp(17px, 2.2vw, 22px)',
            fontWeight: 500,
            lineHeight: 1.7,
            color: 'rgba(245, 250, 249, 0.92)',
            maxWidth: 720,
            margin: 0,
            marginBottom: 56,
          }}
        >
          {subtitle}
        </p>

        {/* CTAs */}
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          {ctas.map((cta) => (
            <a
              key={cta.label}
              href={cta.href}
              target={cta.href.startsWith('http') ? '_blank' : undefined}
              rel={cta.href.startsWith('http') ? 'noopener noreferrer' : undefined}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '14px 24px',
                fontSize: 16,
                fontWeight: 600,
                borderRadius: 9999,
                textDecoration: 'none',
                transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
                ...(cta.primary
                  ? {
                      background: C.inverse,
                      color: C.ink,
                      border: `1.5px solid ${C.inverse}`,
                    }
                  : {
                      background: 'transparent',
                      color: C.inverse,
                      border: '1.5px solid rgba(245, 250, 249, 0.7)',
                    }),
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 4px 24px rgba(26, 43, 71, 0.15)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              {cta.label}
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}
