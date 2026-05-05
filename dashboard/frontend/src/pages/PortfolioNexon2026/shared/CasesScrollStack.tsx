import { useRef } from 'react'
import { motion, useScroll, useTransform, type MotionValue } from 'framer-motion'
import { C, FONT_BODY, FONT_DISPLAY, FONT_MONO } from './colors'
import { useRevealOff } from './useRevealOff'

interface CaseItem {
  readonly no: number
  readonly title: string
  readonly problem: string
  readonly approach: string
  readonly result: string
  readonly bridge: string
}

interface Props {
  items: readonly CaseItem[]
}

type Row = 'problem' | 'approach' | 'result' | 'bridge'
const ROWS: { key: Row; label: string; accent: string; sub: string }[] = [
  { key: 'problem',  label: '문제',     accent: '#E5615A', sub: 'Issue' },
  { key: 'approach', label: '접근',     accent: '#F2A93B', sub: 'Approach' },
  { key: 'result',   label: '결과',     accent: '#3FAE7E', sub: 'Result' },
  { key: 'bridge',   label: '직무 연결', accent: C.nexonBlue, sub: 'Bridge' },
]

/**
 * CH 3·07 TROUBLESHOOTING — sticky-pinned scroll stack.
 *
 * 외곽 section: items × 100vh.
 * sticky 100vh inner — 사용자가 화면에 핀된 채 카드가 차례로 등장/스택.
 * 카드 i: 스크롤 진행도 p 에 따라
 *   - p < i: 아래에서 슬라이드 업 (incoming)
 *   - p ≈ i: 가운데 핀 (front)
 *   - p > i: 살짝 위로 + scale 작아짐 (stacked behind)
 */

const STACK_OFFSET = 28 // 뒤로 갈수록 위로 px (peek 더 보이게)
const STACK_SCALE_STEP = 0.04

export default function CasesScrollStack({ items }: Props) {
  const ref = useRef<HTMLDivElement>(null)
  const revealOff = useRevealOff()
  const total = items.length

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end end'],
  })

  const progress = useTransform(scrollYProgress, [0, 1], [0, total - 0.0001])

  if (revealOff) {
    return (
      <section
        id="troubleshooting"
        style={{
          background: C.bgWhite,
          padding: 'clamp(80px, 10vh, 120px) clamp(40px, 6vw, 120px)',
        }}
      >
        <Header total={total} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'clamp(40px, 6vh, 80px)', maxWidth: 880, margin: '0 auto' }}>
          {items.map((it) => <CaseCard key={it.no} item={it} />)}
        </div>
      </section>
    )
  }

  return (
    <section
      ref={ref}
      id="troubleshooting"
      style={{
        position: 'relative',
        height: `${total * 100}vh`,
        background: C.bgWhite,
      }}
    >
      <div
        style={{
          position: 'sticky',
          top: 0,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          padding: 'clamp(60px, 8vh, 96px) clamp(40px, 6vw, 120px) 80px',
          overflow: 'hidden',
        }}
      >
        <Header total={total} progress={progress} />

        {/* 카드 stack 영역 */}
        <div style={{ flex: 1, position: 'relative' }}>
          {items.map((it, i) => (
            <StackedCard key={it.no} index={i} progress={progress} item={it} />
          ))}
        </div>

        {/* progress dots */}
        <ProgressDots total={total} progress={progress} />
      </div>
    </section>
  )
}

// ─────────────────────────────────────────────

function Header({ total, progress }: { total: number; progress?: MotionValue<number> }) {
  // 카운터: 활성 카드 인덱스 (floor(progress) + 1, but clamp)
  const counter = useTransform(progress ?? createDummyMotion(), (p) =>
    String(Math.min(total, Math.floor(p) + 1)).padStart(2, '0'),
  )
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 28 }}>
      <span style={metaStyle(C.nexonBlue)}>CH 3 · 07</span>
      <span style={metaStyle(C.inkMuted)}>Troubleshooting · 운영 결함</span>
      <span style={{ flex: 1, height: 1, background: C.cardBorder, minWidth: 60 }} />
      <motion.span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 700,
          color: C.inkMuted,
          letterSpacing: '0.18em',
        }}
      >
        {progress ? counter : String(total).padStart(2, '0')}
      </motion.span>
      <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.18em' }}>
        {' '}/ {String(total).padStart(2, '0')}
      </span>
    </div>
  )
}

// dummy MotionValue for static (revealOff) header
function createDummyMotion(): MotionValue<number> {
  // never actually used because progress fallback handled above
  return { get: () => 0 } as unknown as MotionValue<number>
}

function metaStyle(color: string): React.CSSProperties {
  return {
    fontFamily: FONT_MONO,
    fontSize: 11,
    fontWeight: 800,
    color,
    letterSpacing: '0.22em',
    textTransform: 'uppercase',
  }
}

// ─────────────────────────────────────────────

function StackedCard({
  index,
  progress,
  item,
}: {
  index: number
  progress: MotionValue<number>
  item: CaseItem
}) {
  const y = useTransform(progress, (p) => {
    const dist = index - p
    if (dist > 1) return 1400 // off-screen below
    if (dist >= 0) return dist * 700 // sliding up from below
    // behind: 살짝 위로 (음수 y)
    return dist * STACK_OFFSET
  })
  const scale = useTransform(progress, (p) => {
    const depth = Math.max(0, p - index)
    return Math.max(0.78, 1 - depth * STACK_SCALE_STEP)
  })
  const opacity = useTransform(progress, (p) => {
    const dist = index - p
    if (dist > 1.05) return 0
    if (dist > 1) return 1 - (dist - 1) * 20
    return 1
  })

  return (
    <motion.div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        y,
        scale,
        opacity,
        zIndex: index,
        pointerEvents: 'none',
        willChange: 'transform, opacity',
      }}
    >
      <CaseCard item={item} />
    </motion.div>
  )
}

function CaseCard({ item }: { item: CaseItem }) {
  return (
    <article
      style={{
        background: C.bgWhite,
        border: `1px solid ${C.cardBorder}`,
        borderRadius: 24,
        padding: 'clamp(22px, 2.6vw, 36px) clamp(28px, 3vw, 44px)',
        boxShadow: '0 18px 40px rgba(10, 18, 36, 0.08)',
        maxWidth: 1080,
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        pointerEvents: 'auto',
      }}
    >
      {/* header + title 한 줄 — 세로 압축 */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'auto minmax(0, 1fr)',
          columnGap: 24,
          alignItems: 'baseline',
        }}
      >
        <span
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(40px, 5vw, 60px)',
            fontWeight: 800,
            color: C.nexonBlue,
            letterSpacing: '-0.05em',
            lineHeight: 1,
          }}
        >
          {String(item.no).padStart(2, '0')}
        </span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, minWidth: 0 }}>
          <span style={metaStyle(C.inkMuted)}>Case · {String(item.no).padStart(2, '0')}</span>
          <h3
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(18px, 2vw, 24px)',
              fontWeight: 800,
              lineHeight: 1.25,
              color: C.ink,
              margin: 0,
              letterSpacing: '-0.022em',
              wordBreak: 'keep-all',
            }}
          >
            {item.title}
          </h3>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: 'clamp(24px, 2.8vw, 40px)',
        }}
      >
        {ROWS.map((r) => (
          <div
            key={r.key}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 10,
              paddingTop: 12,
              borderTop: `2px solid ${r.accent}`,
              minWidth: 0, // grid item 안 overflow 방지
            }}
          >
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
              <span
                style={{
                  fontFamily: FONT_DISPLAY,
                  fontSize: 16,
                  fontWeight: 800,
                  color: r.accent,
                  letterSpacing: '-0.015em',
                  lineHeight: 1,
                }}
              >
                {r.label}
              </span>
              <span style={{ ...metaStyle(C.inkMuted), fontSize: 9.5, letterSpacing: '0.2em' }}>{r.sub}</span>
            </div>
            <p
              style={{
                fontFamily: FONT_BODY,
                fontSize: 13.5,
                lineHeight: 1.8,
                color: C.inkSoft,
                margin: 0,
                fontWeight: 500,
                // 한국어 단어는 보존하되, 긴 코드 토큰은 셀 밖 안 나가게 fallback break
                wordBreak: 'keep-all',
                overflowWrap: 'anywhere',
              }}
            >
              {item[r.key]}
            </p>
          </div>
        ))}
      </div>
    </article>
  )
}

// ─────────────────────────────────────────────

function ProgressDots({ total, progress }: { total: number; progress: MotionValue<number> }) {
  return (
    <div style={{ display: 'flex', gap: 6, alignItems: 'center', justifyContent: 'center', paddingTop: 16 }}>
      {Array.from({ length: total }).map((_, i) => (
        <DotTick key={i} index={i} progress={progress} />
      ))}
    </div>
  )
}

function DotTick({ index, progress }: { index: number; progress: MotionValue<number> }) {
  const fill = useTransform(progress, (p) => (p >= index ? C.nexonBlue : C.cardBorder))
  return <motion.span aria-hidden style={{ width: 28, height: 2, background: fill, display: 'block' }} />
}
