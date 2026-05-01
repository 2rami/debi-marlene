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
            background: i === 0 ? 'rgba(0, 98, 223, 0.05)' : C.bgWhite,
            borderRadius: 16,
            border: i === 0 ? `2px solid ${C.nexonBlue}` : `1px solid ${C.cardBorder}`,
            transition: 'transform 0.2s',
            cursor: 'default',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = 'translateX(8px)')}
          onMouseLeave={(e) => (e.currentTarget.style.transform = 'translateX(0)')}
        >
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 12,
              color: i === 0 ? C.nexonBlue : C.inkMuted,
              letterSpacing: '0.1em',
              fontWeight: 800,
            }}
          >
            {String(i + 1).padStart(2, '0')}
          </span>
          <span
            style={{
              fontSize: 17,
              fontWeight: 800,
              color: i === 0 ? C.nexonBlue : C.ink,
              letterSpacing: '-0.01em',
            }}
          >
            {g.title}
          </span>
          <span style={{ fontSize: 13, color: C.inkSoft, fontFamily: FONT_MONO, fontWeight: 500 }}>{g.period}</span>
          <span style={{ fontSize: 14, color: C.inkSoft, lineHeight: 1.5, fontWeight: 500 }}>{g.detail}</span>
        </div>
      ))}
    </div>
  )
}
