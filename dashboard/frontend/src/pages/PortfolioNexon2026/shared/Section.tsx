import { C, FONT_MONO } from './colors'

interface SectionProps {
  no: string  // "01", "02"
  kicker: string  // "ABOUT", "JD MATCH"
  title: string
  children: React.ReactNode
  bg?: 'light' | 'dark'  // light = 화이트 카드 영역 / dark = 그라디언트 위
}

export default function Section({ no, kicker, title, children, bg = 'light' }: SectionProps) {
  const isDark = bg === 'dark'
  return (
    <section
      style={{
        padding: '96px 48px',
        background: isDark ? 'transparent' : C.inverse,
        color: isDark ? C.inverse : C.ink,
      }}
    >
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* 섹션 헤더 (매거진 톤) */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 32 }}>
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              letterSpacing: '0.15em',
              color: isDark ? C.nexonBlue : C.nexonBlue,
              fontWeight: 700,
            }}
          >
            {no}
          </span>
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              letterSpacing: '0.15em',
              color: isDark ? 'rgba(245, 250, 249, 0.7)' : C.inkMuted,
              fontWeight: 600,
            }}
          >
            {kicker}
          </span>
          <span
            style={{
              flex: 1,
              height: 1,
              background: isDark ? 'rgba(245, 250, 249, 0.3)' : 'rgba(26, 43, 71, 0.15)',
            }}
          />
        </div>

        <h2
          style={{
            fontSize: 'clamp(28px, 4vw, 44px)',
            fontWeight: 800,
            lineHeight: 1.25,
            letterSpacing: '-0.02em',
            color: isDark ? C.inverse : C.ink,
            margin: 0,
            marginBottom: 48,
          }}
        >
          {title}
        </h2>

        {children}
      </div>
    </section>
  )
}
