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
        display: 'grid',
        gridTemplateColumns: 'minmax(220px, 320px) minmax(0, 1fr)',
        gap: 64,
        alignItems: 'start',
        paddingBottom: 56,
        borderBottom: `1px solid ${C.cardBorder}`,
      }}
    >
      <div>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            letterSpacing: '0.2em',
            color: C.nexonBlue,
            fontWeight: 500,
            marginBottom: 12,
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 13,
            color: C.inkMuted,
            fontWeight: 500,
            letterSpacing: '0.04em',
          }}
        >
          {items.length} ITEMS · TOP {top.length}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
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
        paddingLeft: 16,
        borderLeft: `2px solid ${C.nexonBlue}`,
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
