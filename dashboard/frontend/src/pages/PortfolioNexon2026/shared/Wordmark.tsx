import { C, FONT_DISPLAY } from './colors'

/**
 * 풀블리드 워드마크 섹션 브레이커.
 * freesentation 패턴 — 섹션 사이 큰 블루 텍스트로 끊어줌.
 */
export default function Wordmark({
  text = 'DEBI&MARLENE.',
  variant = 'light',
}: {
  text?: string
  variant?: 'light' | 'dark'
}) {
  const isDark = variant === 'dark'

  return (
    <section
      aria-hidden
      style={{
        background: isDark ? '#0D0E11' : '#FFFFFF',
        padding: '120px 0',
        overflow: 'hidden',
        width: '100%',
      }}
    >
      <div
        style={{
          padding: '0 clamp(20px, 3vw, 100px)',
        }}
      >
        <div
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(80px, 18vw, 224px)',
            fontWeight: 900,
            lineHeight: 0.85,
            letterSpacing: '-0.05em',
            color: C.nexonBlue,
            margin: 0,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'clip',
          }}
        >
          {text}
        </div>
      </div>
    </section>
  )
}
