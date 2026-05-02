import { C, FONT_MONO } from './colors'

interface Stat {
  label: string
  value: string
  unit?: string
  sub: string
}

export default function StatGrid({ stats }: { stats: readonly Stat[] }) {
  // 넥슨 트렌디 색상을 번갈아가며 카드 상단 포인트로 사용
  const borderColors = [C.nexonBlue, C.lime, C.coral, C.yellow]

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(auto-fit, minmax(220px, 1fr))`,
        gap: 24,
      }}
    >
      {stats.map((s, i) => (
        <div
          key={s.label}
          style={{
            background: C.bgWhite,
            borderRadius: 24,
            padding: '32px 24px',
            borderTop: `6px solid ${borderColors[i % borderColors.length]}`,
            boxShadow: C.cardShadow,
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
            cursor: 'default',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-8px) scale(1.02)'
            e.currentTarget.style.boxShadow = C.cardShadowHover
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0) scale(1)'
            e.currentTarget.style.boxShadow = C.cardShadow
          }}
        >
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 12,
              letterSpacing: '0.12em',
              color: borderColors[i % borderColors.length],
              fontWeight: 800,
              textTransform: 'uppercase',
            }}
          >
            POINT {String(i + 1).padStart(2, '0')}
          </span>
          <div
            style={{
              fontSize: 'clamp(32px, 4vw, 48px)',
              fontWeight: 800,
              lineHeight: 1,
              color: C.ink,
              fontVariantNumeric: 'tabular-nums',
              letterSpacing: '-0.03em',
              marginTop: 4,
            }}
          >
            {s.value}
            {s.unit && (
              <span style={{ fontSize: '0.45em', fontWeight: 800, marginLeft: 4, color: C.inkMuted }}>
                {s.unit}
              </span>
            )}
          </div>
          <div
            style={{
              fontSize: 15,
              fontWeight: 700,
              color: C.ink,
              marginTop: 8,
            }}
          >
            {s.label}
          </div>
          <div style={{ fontSize: 13, color: C.inkSoft, lineHeight: 1.6, fontWeight: 700 }}>
            {s.sub}
          </div>
        </div>
      ))}
    </div>
  )
}
