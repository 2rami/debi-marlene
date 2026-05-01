import { C, FONT_MONO } from './colors'

interface Stat {
  label: string
  value: string
  unit?: string
  sub: string
}

export default function StatGrid({ stats }: { stats: readonly Stat[] }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${stats.length}, 1fr)`,
        gap: 0,
        background: C.cream,
        borderRadius: 16,
        overflow: 'hidden',
        border: `2px solid ${C.honey}`,
      }}
    >
      {stats.map((s, i) => (
        <div
          key={s.label}
          style={{
            padding: '32px 24px',
            borderRight: i < stats.length - 1 ? `1px solid rgba(26, 43, 71, 0.1)` : 'none',
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
          }}
        >
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 10,
              letterSpacing: '0.12em',
              color: C.inkMuted,
              fontWeight: 600,
              textTransform: 'uppercase',
            }}
          >
            {String(i + 1).padStart(2, '0')}
          </span>
          <div
            style={{
              fontSize: 'clamp(28px, 3.6vw, 44px)',
              fontWeight: 800,
              lineHeight: 1,
              color: C.ink,
              fontVariantNumeric: 'tabular-nums',
              letterSpacing: '-0.02em',
            }}
          >
            {s.value}
            {s.unit && (
              <span style={{ fontSize: '0.5em', fontWeight: 700, marginLeft: 4, color: C.inkSoft }}>
                {s.unit}
              </span>
            )}
          </div>
          <div
            style={{
              fontSize: 13,
              fontWeight: 600,
              color: C.ink,
              marginTop: 4,
            }}
          >
            {s.label}
          </div>
          <div style={{ fontSize: 12, color: C.inkSoft, lineHeight: 1.5 }}>{s.sub}</div>
        </div>
      ))}
    </div>
  )
}
