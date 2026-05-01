import { C, FONT_MONO } from './colors'

interface CaseCardProps {
  no: number
  title: string
  problem: string
  approach: string
  result: string
  bridge: string  // 직무와의 연결
}

export default function CaseCard({ no, title, problem, approach, result, bridge }: CaseCardProps) {
  return (
    <article
      style={{
        background: C.bgWhite,
        borderRadius: 24,
        padding: 36,
        boxShadow: C.cardShadow,
        border: `1px solid ${C.cardBorder}`,
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        position: 'relative',
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
      <header style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 12,
            letterSpacing: '0.12em',
            color: C.inverse,
            background: C.nexonBlue,
            fontWeight: 800,
            padding: '6px 14px',
            borderRadius: 999,
          }}
        >
          CASE {String(no).padStart(2, '0')}
        </div>
      </header>

      <h3
        style={{
          fontSize: 22,
          fontWeight: 800,
          lineHeight: 1.4,
          color: C.ink,
          margin: 0,
          letterSpacing: '-0.02em',
          paddingBottom: 16,
          borderBottom: `1px dashed rgba(0, 98, 223, 0.2)`,
        }}
      >
        {title}
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginTop: 4 }}>
        <Row label="문제" body={problem} type="default" />
        <Row label="접근" body={approach} type="default" />
        <Row label="결과" body={result} type="accent" />
        <Row label="직무 연결" body={bridge} type="bridge" />
      </div>
    </article>
  )
}

function Row({ label, body, type }: { label: string; body: string; type: 'default' | 'accent' | 'bridge' }) {
  const getBadgeColor = () => {
    if (type === 'bridge') return { bg: C.lime, text: C.ink }
    if (type === 'accent') return { bg: 'rgba(255, 75, 75, 0.1)', text: C.coral }
    return { bg: 'rgba(0, 98, 223, 0.08)', text: C.nexonBlue }
  }
  const colors = getBadgeColor()

  return (
    <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
      <span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          letterSpacing: '0.05em',
          color: colors.text,
          background: colors.bg,
          fontWeight: 800,
          padding: '4px 8px',
          borderRadius: 8,
          whiteSpace: 'nowrap',
          marginTop: 2,
        }}
      >
        {label}
      </span>
      <p
        style={{
          fontSize: 15,
          lineHeight: 1.6,
          color: type === 'bridge' ? C.ink : C.inkSoft,
          margin: 0,
          fontWeight: type === 'bridge' ? 700 : 500,
        }}
      >
        {body}
      </p>
    </div>
  )
}
