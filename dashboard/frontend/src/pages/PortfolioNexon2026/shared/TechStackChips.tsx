import { C, FONT_MONO } from './colors'

type StackItem = { label: string; value: string }

const TITLE_BY_KEY: Record<string, string> = {
  llm: 'LLM · AI',
  infra: 'INFRA · BACKEND',
  frontend: 'FRONTEND · WEB',
}

export default function TechStackChips({
  stack,
  highlightCount = 3,
}: {
  stack: { llm: readonly StackItem[]; infra: readonly StackItem[]; frontend: readonly StackItem[] }
  highlightCount?: number
}) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 56,
      }}
    >
      {(['llm', 'infra', 'frontend'] as const).map((key) => (
        <Block
          key={key}
          title={TITLE_BY_KEY[key]}
          items={stack[key]}
          highlightCount={highlightCount}
        />
      ))}
    </div>
  )
}

function Block({
  title,
  items,
  highlightCount,
}: {
  title: string
  items: readonly StackItem[]
  highlightCount: number
}) {
  const top = items.slice(0, highlightCount)

  return (
    <article
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 24,
        paddingBottom: 40,
        marginBottom: 16,
        borderBottom: `1px solid ${C.cardBorder}`,
      }}
    >
      <header style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            letterSpacing: '0.22em',
            color: C.nexonBlue,
            fontWeight: 800,
            textTransform: 'uppercase',
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            color: C.inkMuted,
            fontWeight: 600,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
          }}
        >
          {items.length} items · top {top.length}
        </div>
      </header>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 'clamp(16px, 2vw, 28px)',
        }}
      >
        {top.map((it) => (
          <Row key={it.label} item={it} />
        ))}
      </div>
    </article>
  )
}

function Row({ item }: { item: StackItem }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        paddingTop: 12,
        borderTop: `1px solid ${C.cardBorder}`,
      }}
    >
      <span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          letterSpacing: '0.1em',
          color: C.inkMuted,
          fontWeight: 600,
        }}
      >
        {item.label}
      </span>
      <span
        style={{
          fontSize: 18,
          lineHeight: 1.35,
          color: C.ink,
          fontWeight: 500,
          letterSpacing: '-0.01em',
        }}
      >
        {item.value}
      </span>
    </div>
  )
}
