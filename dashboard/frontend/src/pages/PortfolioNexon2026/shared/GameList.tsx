import { C, FONT_MONO } from './colors'

interface Game {
  title: string
  period: string
  detail: string
}

export default function GameList({ games }: { games: readonly Game[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {games.map((g, i) => (
        <div
          key={g.title}
          style={{
            display: 'grid',
            gridTemplateColumns: '40px minmax(140px, 200px) minmax(120px, 180px) 1fr',
            gap: 16,
            alignItems: 'baseline',
            padding: '16px 20px',
            background: i === 0 ? C.cream : C.inverse,
            borderRadius: 12,
            border: i === 0 ? `2px solid ${C.honey}` : `1px solid rgba(26, 43, 71, 0.08)`,
          }}
        >
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              color: C.honey,
              letterSpacing: '0.1em',
              fontWeight: 700,
            }}
          >
            {String(i + 1).padStart(2, '0')}
          </span>
          <span
            style={{
              fontSize: 16,
              fontWeight: 700,
              color: C.ink,
              letterSpacing: '-0.01em',
            }}
          >
            {g.title}
          </span>
          <span style={{ fontSize: 13, color: C.inkMuted, fontFamily: FONT_MONO }}>{g.period}</span>
          <span style={{ fontSize: 13, color: C.inkSoft, lineHeight: 1.5 }}>{g.detail}</span>
        </div>
      ))}
    </div>
  )
}
