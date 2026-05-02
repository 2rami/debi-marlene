import { CSSProperties, ReactNode } from 'react'
import { C, FONT_BODY, FONT_DISPLAY } from './colors'

/**
 * 섹션 레이아웃 3패턴 — 단조한 풀블리드 흰 카드를 깬다.
 *
 * - aside: 좌 220px sticky 라벨 + 우 narrow column (480~720px). 매거진 톤.
 * - bleed: 풀블리드, 좌우 작은 padding. 박스 없이 타이포 + 그리드.
 * - split: 두 칼럼 비대칭 (이미지/텍스트, 라벨/콘텐츠 등).
 */

type Variant = 'aside' | 'bleed' | 'split'

interface Props {
  id: string
  ch: string // 'CH 2'
  no: string // '03'
  kicker: string // 'TECH STACK · 기술 스택'
  title: string
  variant?: Variant
  background?: string
  children: ReactNode
  rightAccessory?: ReactNode // split 패턴 좌측 슬롯 (이미지 등)
  paddingY?: string // override
}

export default function SectionShell({
  id,
  ch,
  no,
  kicker,
  title,
  variant = 'aside',
  background = C.bgWhite,
  children,
  rightAccessory,
  paddingY = '160px',
}: Props) {
  if (variant === 'bleed') {
    return (
      <section
        id={id}
        style={{
          padding: `${paddingY} clamp(20px, 3vw, 80px)`,
          background,
        }}
      >
        <Header ch={ch} no={no} kicker={kicker} title={title} variant="bleed" />
        <div>{children}</div>
      </section>
    )
  }

  if (variant === 'split') {
    return (
      <section
        id={id}
        style={{
          padding: `${paddingY} clamp(40px, 6vw, 120px)`,
          background,
        }}
      >
        <div
          style={{
            maxWidth: 1280,
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'minmax(0, 1.05fr) minmax(0, 1fr)',
            gap: 'clamp(40px, 6vw, 120px)',
            alignItems: 'start',
          }}
        >
          <div>
            <Header
              ch={ch}
              no={no}
              kicker={kicker}
              title={title}
              variant="split"
            />
            {rightAccessory}
          </div>
          <div>{children}</div>
        </div>
      </section>
    )
  }

  // aside (default)
  return (
    <section
      id={id}
      style={{
        padding: `${paddingY} clamp(40px, 6vw, 120px)`,
        background,
      }}
    >
      <div
        style={{
          maxWidth: 1280,
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'minmax(160px, 220px) minmax(0, 1fr)',
          gap: 'clamp(32px, 5vw, 80px)',
          alignItems: 'start',
        }}
      >
        <div>
          <div
            style={{
              position: 'sticky',
              top: 'clamp(120px, 14vh, 180px)',
            }}
          >
            <StickyLabel ch={ch} no={no} kicker={kicker} />
          </div>
        </div>
        <div style={{ maxWidth: 760 }}>
          <h2
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(28px, 3.4vw, 44px)',
              fontWeight: 700,
              lineHeight: 1.22,
              letterSpacing: '-0.025em',
              color: C.ink,
              margin: '0 0 56px',
              wordBreak: 'keep-all',
            }}
          >
            {title}
          </h2>
          {children}
        </div>
      </div>
    </section>
  )
}

function Header({
  ch,
  no,
  kicker,
  title,
  variant,
}: {
  ch: string
  no: string
  kicker: string
  title: string
  variant: 'bleed' | 'split'
}) {
  if (variant === 'bleed') {
    return (
      <div
        style={{
          maxWidth: 1480,
          margin: '0 auto 80px',
          padding: '0 clamp(20px, 3vw, 80px)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 24 }}>
          <StickyLabel ch={ch} no={no} kicker={kicker} inline />
        </div>
        <h2
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(40px, 5.6vw, 80px)',
            fontWeight: 800,
            lineHeight: 1.05,
            letterSpacing: '-0.035em',
            color: C.ink,
            margin: 0,
            wordBreak: 'keep-all',
            maxWidth: 1100,
          }}
        >
          {title}
        </h2>
      </div>
    )
  }

  // split — 좌 칼럼 헤더
  return (
    <div style={{ marginBottom: 32 }}>
      <StickyLabel ch={ch} no={no} kicker={kicker} />
      <h2
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 'clamp(32px, 4.2vw, 56px)',
          fontWeight: 800,
          lineHeight: 1.12,
          letterSpacing: '-0.03em',
          color: C.ink,
          margin: '24px 0 0',
          wordBreak: 'keep-all',
        }}
      >
        {title}
      </h2>
    </div>
  )
}

function StickyLabel({
  ch,
  no,
  kicker,
  inline,
}: {
  ch: string
  no: string
  kicker: string
  inline?: boolean
}) {
  const labelStyle: CSSProperties = {
    fontFamily: FONT_BODY,
    fontSize: 11,
    fontWeight: 800,
    letterSpacing: '0.22em',
    textTransform: 'uppercase',
  }
  return (
    <div
      style={{
        display: inline ? 'flex' : 'block',
        gap: inline ? 16 : 0,
        alignItems: 'baseline',
      }}
    >
      <div style={{ ...labelStyle, color: C.nexonBlue, marginBottom: inline ? 0 : 6 }}>
        {ch} · {no}
      </div>
      <div style={{ ...labelStyle, color: C.inkMuted }}>{kicker}</div>
    </div>
  )
}
