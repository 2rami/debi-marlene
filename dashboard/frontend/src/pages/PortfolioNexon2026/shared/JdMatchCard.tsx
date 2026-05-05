import { C, FONT_MONO, FONT_DISPLAY } from './colors'
import TooltipCard from './TooltipCard'

export interface ReportTooltip {
  title: string
  subtitle: string
  insights: readonly string[]
  pdfHref: string
}

export type EvidenceItem =
  | string
  | { text: string; highlight: string; report: ReportTooltip }

interface JdMatchProps {
  n: number
  jdTitle: string
  jdSub: string
  evidence: readonly EvidenceItem[]
}

function ReportCard({ report }: { report: ReportTooltip }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ fontFamily: FONT_MONO, fontSize: 10, letterSpacing: '0.18em', color: '#7dd3fc', fontWeight: 700 }}>
        REPORT · PDF
      </div>
      <div style={{ fontSize: 14, fontWeight: 800, color: '#fff', lineHeight: 1.35 }}>
        {report.title}
      </div>
      <div style={{ fontSize: 11, color: '#a8a8b3', lineHeight: 1.5 }}>{report.subtitle}</div>
      <ul style={{ margin: '6px 0 4px', padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 4 }}>
        {report.insights.map((v, i) => (
          <li key={i} style={{ fontSize: 11.5, color: '#e0e0e8', paddingLeft: 12, position: 'relative', lineHeight: 1.5 }}>
            <span style={{ position: 'absolute', left: 0, color: '#7dd3fc' }}>·</span>
            {v}
          </li>
        ))}
      </ul>
      <a
        href={report.pdfHref}
        target="_blank"
        rel="noopener"
        style={{ marginTop: 4, display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: FONT_MONO, fontSize: 11, color: '#7dd3fc', textDecoration: 'none', fontWeight: 700, pointerEvents: 'auto', letterSpacing: '0.04em' }}
        onClick={(e) => e.stopPropagation()}
      >
        <span>PDF 열기 →</span>
      </a>
    </div>
  )
}

export default function JdMatchCard({ n, jdTitle, jdSub, evidence }: JdMatchProps) {
  return (
    <article
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: 'clamp(28px, 4vw, 56px)',
        alignItems: 'start',
        position: 'relative',
        paddingTop: 32,
        borderTop: `1px solid ${C.cardBorder}`,
      }}
    >
      {/* 좌 — 번호 + 제목 + 부제 (sticky 가능 영역) */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 20,
          position: 'sticky',
          top: 'clamp(120px, 14vh, 180px)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
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
            {String(n).padStart(2, '0')}
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
            JD Match · 0{n}
          </span>
        </div>

        <div>
          <h3
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(22px, 2.4vw, 28px)',
              fontWeight: 800,
              lineHeight: 1.32,
              color: C.ink,
              margin: 0,
              marginBottom: 10,
              letterSpacing: '-0.022em',
              wordBreak: 'keep-all',
            }}
          >
            {jdTitle}
          </h3>
          <p style={{ fontSize: 14, color: C.inkMuted, margin: 0, lineHeight: 1.6, fontWeight: 500, wordBreak: 'keep-all' }}>{jdSub}</p>
        </div>
      </div>

      {/* Evidence list */}
      <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {evidence.map((e, i) => {
          const text = typeof e === 'string' ? e : e.text
          const isReport = typeof e !== 'string'
          let body: React.ReactNode = text
          if (isReport && e.highlight && text.includes(e.highlight)) {
            const [before, after] = text.split(e.highlight)
            body = (
              <>
                {before}
                <TooltipCard card={<ReportCard report={e.report} />} width={400}>
                  {e.highlight}
                </TooltipCard>
                {after}
              </>
            )
          }

          return (
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
                <polyline points="20 6 9 17 4 12" />
              </svg>
              {body}
            </li>
          )
        })}
      </ul>
    </article>
  )
}
