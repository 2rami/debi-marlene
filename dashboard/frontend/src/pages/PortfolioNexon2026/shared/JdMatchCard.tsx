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
        background: C.inverse,
        borderRadius: 16,
        padding: '32px 32px 28px',
        border: `1px solid rgba(26, 43, 71, 0.08)`,
        borderLeft: `4px solid ${C.honey}`,
        boxShadow: C.cardShadow,
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
      }}
    >
      {/* 번호 칩 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 32,
            height: 32,
            borderRadius: 9999,
            background: C.lime,
            color: C.ink,
            fontFamily: FONT_MONO,
            fontSize: 13,
            fontWeight: 800,
          }}
        >
          {String(n).padStart(2, '0')}
        </span>
        <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em' }}>
          JD MATCH
        </span>
      </div>

      {/* JD Title */}
      <div>
        <h3
          style={{
            fontSize: 20,
            fontWeight: 700,
            lineHeight: 1.4,
            color: C.ink,
            margin: 0,
            marginBottom: 6,
          }}
        >
          {jdTitle}
        </h3>
        <p style={{ fontSize: 13, color: C.inkMuted, margin: 0, lineHeight: 1.5 }}>{jdSub}</p>
      </div>

      {/* Evidence list */}
      <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {evidence.map((e, i) => (
          <li
            key={i}
            style={{
              fontSize: 14,
              lineHeight: 1.65,
              color: C.inkSoft,
              paddingLeft: 18,
              position: 'relative',
            }}
          >
            <span
              style={{
                position: 'absolute',
                left: 0,
                top: 9,
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: C.honey,
              }}
            />
            {e}
          </li>
        ))}
      </ul>
    </article>
  )
}
