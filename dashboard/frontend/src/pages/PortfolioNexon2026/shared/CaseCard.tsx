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
        background: C.inverse,
        borderRadius: 16,
        padding: 32,
        boxShadow: C.cardShadow,
        border: `1px solid rgba(26, 43, 71, 0.06)`,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      <header style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 4 }}>
        <span
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            letterSpacing: '0.12em',
            color: C.honey,
            fontWeight: 700,
          }}
        >
          CASE {String(no).padStart(2, '0')}
        </span>
        <span style={{ flex: 1, height: 1, background: 'rgba(26, 43, 71, 0.1)' }} />
      </header>

      <h3
        style={{
          fontSize: 22,
          fontWeight: 700,
          lineHeight: 1.35,
          color: C.ink,
          margin: 0,
          letterSpacing: '-0.01em',
        }}
      >
        {title}
      </h3>

      <Row label="문제" body={problem} />
      <Row label="접근" body={approach} />
      <Row label="결과" body={result} accent />
      <Row label="직무 연결" body={bridge} bridge />
    </article>
  )
}

function Row({ label, body, accent, bridge }: { label: string; body: string; accent?: boolean; bridge?: boolean }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '64px 1fr', gap: 16, alignItems: 'baseline' }}>
      <span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 10,
          letterSpacing: '0.1em',
          color: bridge ? C.bgDeep : accent ? C.honey : C.inkMuted,
          fontWeight: 700,
          textTransform: 'uppercase',
        }}
      >
        {label}
      </span>
      <p
        style={{
          fontSize: 14,
          lineHeight: 1.7,
          color: bridge ? C.bgDeep : C.inkSoft,
          margin: 0,
          fontWeight: bridge ? 600 : 500,
        }}
      >
        {body}
      </p>
    </div>
  )
}
