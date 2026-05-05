import { C, FONT_MONO, FONT_DISPLAY } from './colors'

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
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: 'clamp(28px, 4vw, 56px)',
        alignItems: 'start',
        position: 'relative',
        paddingTop: 32,
        borderTop: `1px solid ${C.cardBorder}`,
      }}
    >
      {/* 좌 — 번호 + 제목 (sticky) */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 20,
          position: 'sticky',
          top: 'clamp(120px, 14vh, 180px)',
        }}
      >
        <header style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
          <span
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(40px, 5vw, 56px)',
              fontWeight: 800,
              color: C.nexonBlue,
              lineHeight: 1,
              letterSpacing: '-0.04em',
            }}
          >
            {String(no).padStart(2, '0')}
          </span>
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              color: C.inkMuted,
              letterSpacing: '0.22em',
              fontWeight: 800,
              textTransform: 'uppercase',
            }}
          >
            Case · {String(no).padStart(2, '0')}
          </span>
        </header>

        <h3
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(22px, 2.4vw, 28px)',
            fontWeight: 800,
            lineHeight: 1.32,
            color: C.ink,
            margin: 0,
            letterSpacing: '-0.022em',
            wordBreak: 'keep-all',
          }}
        >
          {title}
        </h3>
      </div>

      {/* 우 — 4 row 본문 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        <Row label="문제" body={problem} type="default" />
        <Row label="접근" body={approach} type="default" />
        <Row label="결과" body={result} type="accent" />
        <Row label="직무 연결" body={bridge} type="bridge" />
      </div>
    </article>
  )
}

function Row({ label, body, type }: { label: string; body: string; type: 'default' | 'accent' | 'bridge' }) {
  const labelColor = type === 'bridge' ? C.nexonBlue : C.inkMuted

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '92px 1fr',
        gap: 24,
        alignItems: 'baseline',
      }}
    >
      <span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          letterSpacing: '0.22em',
          color: labelColor,
          fontWeight: 800,
          textTransform: 'uppercase',
        }}
      >
        {label}
      </span>
      <p
        style={{
          fontSize: 15,
          lineHeight: 1.85,
          color: type === 'bridge' ? C.nexonBlue : type === 'accent' ? C.ink : C.inkSoft,
          margin: 0,
          fontWeight: type === 'bridge' ? 600 : type === 'accent' ? 600 : 500,
          wordBreak: 'keep-all',
        }}
      >
        {body}
      </p>
    </div>
  )
}
