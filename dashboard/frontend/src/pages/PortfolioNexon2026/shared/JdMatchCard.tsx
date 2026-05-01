import { C, FONT_MONO } from './colors'

interface JdMatchProps {
  n: number
  jdTitle: string
  jdSub: string
  evidence: readonly string[]
}

export default function JdMatchCard({ n, jdTitle, jdSub, evidence }: JdMatchProps) {
  return (
    <article
      style={{
        background: C.bgWhite,
        borderRadius: 24,
        padding: '36px 32px',
        border: `1px solid ${C.cardBorder}`,
        boxShadow: C.cardShadow,
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        position: 'relative',
        overflow: 'hidden',
        transition: 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-6px)'
        e.currentTarget.style.boxShadow = C.cardShadowHover
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = C.cardShadow
      }}
    >
      {/* Top Accent Line */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 6, background: C.nexonBlue }} />

      {/* 번호 칩 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 36,
            height: 36,
            borderRadius: 12,
            background: C.bgSoft,
            color: C.nexonBlue,
            fontFamily: FONT_MONO,
            fontSize: 14,
            fontWeight: 800,
          }}
        >
          {String(n).padStart(2, '0')}
        </span>
        <span style={{ fontFamily: FONT_MONO, fontSize: 12, color: C.inkMuted, letterSpacing: '0.1em', fontWeight: 700 }}>
          JD MATCH
        </span>
      </div>

      {/* JD Title */}
      <div>
        <h3
          style={{
            fontSize: 22,
            fontWeight: 800,
            lineHeight: 1.4,
            color: C.ink,
            margin: 0,
            marginBottom: 8,
            letterSpacing: '-0.02em',
          }}
        >
          {jdTitle}
        </h3>
        <p style={{ fontSize: 14, color: C.inkMuted, margin: 0, lineHeight: 1.5, fontWeight: 500 }}>{jdSub}</p>
      </div>

      {/* Evidence list */}
      <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {evidence.map((e, i) => (
          <li
            key={i}
            style={{
              fontSize: 15,
              lineHeight: 1.65,
              color: C.inkSoft,
              paddingLeft: 28,
              position: 'relative',
              fontWeight: 500,
            }}
          >
            <svg
              style={{ position: 'absolute', left: 0, top: 4 }}
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke={C.nexonLightBlue}
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            {e}
          </li>
        ))}
      </ul>
    </article>
  )
}
