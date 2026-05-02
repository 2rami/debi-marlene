import { C, FONT_MONO } from './colors'

/**
 * 풀블리드 페이지 전체에 떠있는 두 코너 라벨.
 * freesentation.blog 패턴: TL 정체성 / TR 액션.
 */
export default function CornerLabels({
  ctaLabel = 'GO TO PROJECT',
  ctaHref = 'https://github.com/2rami/debi-marlene',
}: {
  ctaLabel?: string
  ctaHref?: string
}) {
  return (
    <>
      {/* 좌상단 — 정체성 */}
      <div
        style={{
          position: 'fixed',
          top: 'clamp(20px, 3vh, 36px)',
          left: 'clamp(20px, 3vw, 100px)',
          zIndex: 110,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          mixBlendMode: 'difference',
          color: '#FFFFFF',
        }}
      >
        <span
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
          }}
        >
          NEXON · LLM EVAL
        </span>
      </div>

      {/* 우상단 — Outlined CTA */}
      <a
        href={ctaHref}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          position: 'fixed',
          top: 'clamp(20px, 3vh, 36px)',
          right: 'clamp(20px, 3vw, 100px)',
          zIndex: 110,
          padding: '8px 14px',
          borderRadius: 999,
          border: `1px solid ${C.nexonBlue}`,
          color: C.nexonBlue,
          background: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(8px)',
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 700,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          textDecoration: 'none',
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          transition: 'all 0.2s ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = C.nexonBlue
          e.currentTarget.style.color = '#FFFFFF'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.7)'
          e.currentTarget.style.color = C.nexonBlue
        }}
      >
        {ctaLabel}
        <span style={{ fontSize: 12 }}>↗</span>
      </a>
    </>
  )
}
