import { useEffect, useRef, useState } from 'react'
import {
  motion,
  useMotionValue,
  useMotionValueEvent,
  useScroll,
  useSpring,
  useTransform,
  type MotionValue,
} from 'framer-motion'
import { C, FONT_BODY, FONT_DISPLAY, FONT_MONO } from './colors'
import { useRevealOff } from './useRevealOff'
import TooltipCard from './TooltipCard'
import type { EvidenceItem, ReportTooltip } from './JdMatchCard'

interface JdItem {
  readonly n: number
  readonly jdTitle: string
  readonly jdSub: string
  readonly evidence: readonly EvidenceItem[]
}

interface Props {
  items: readonly JdItem[]
}

/**
 * CH 3·04 JD MATCH — sticky scroll-pinned, split-reveal slideshow.
 *
 * 각 JD 마다 stage = 1 (header: 번호 + jdTitle + jdSub) + evidence.length
 * 한 stage 가 STEP_VH 길이. 스크롤이 진행되면서:
 *   stage 0 → 헤더만 visible
 *   stage 1 → + evidence[0]
 *   stage 2 → + evidence[1]
 *   ...
 *   다음 JD 로 넘어가면 AnimatePresence 페이드 swap
 *
 * ?reveal=off 면 모든 슬라이드 + 모든 evidence 한 번에 노출 (Figma 캡처용)
 */
const STEP_VH = 200 // 한 step (header / 각 evidence) 당 2 viewport — 느린 진행

export default function JdScrollytelling({ items }: Props) {
  const ref = useRef<HTMLDivElement>(null)
  const revealOff = useRevealOff()

  const stepCounts = items.map((i) => 1 + i.evidence.length)
  const totalSteps = stepCounts.reduce((a, b) => a + b, 0)

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end end'],
  })

  const [active, setActive] = useState<{ jdIdx: number; subIdx: number }>({ jdIdx: 0, subIdx: -1 })
  // globalPos — 모든 JD 의 슬롯을 단일 stack 으로 보고 연속 위치 (0..totalSteps)
  const globalPos = useMotionValue(0)

  const stepFloat = useTransform(scrollYProgress, [0, 1], [0, totalSteps])
  useMotionValueEvent(stepFloat, 'change', (v) => {
    const clamped = Math.max(0, Math.min(totalSteps - 0.0001, v))
    globalPos.set(clamped)
    // VaultDial / ProgressBar 용 정수 activeIdx 도 같이 산출
    let cumStep = 0
    for (let i = 0; i < items.length; i++) {
      const cap = stepCounts[i]
      if (clamped < cumStep + cap || i === items.length - 1) {
        const localStep = clamped - cumStep
        const subIdxNew = Math.max(-1, Math.floor(localStep) - 1)
        setActive((cur) =>
          cur.jdIdx === i && cur.subIdx === subIdxNew ? cur : { jdIdx: i, subIdx: subIdxNew },
        )
        return
      }
      cumStep += cap
    }
  })

  if (revealOff) {
    return (
      <section style={{ background: C.bgWhite, padding: 'clamp(80px, 10vh, 120px) clamp(40px, 6vw, 120px)' }}>
        <Header active={items.length - 1} total={items.length} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'clamp(64px, 8vh, 96px)', maxWidth: 1280, margin: '0 auto' }}>
          {items.map((it) => (
            <StaticSlide key={it.n} item={it} />
          ))}
        </div>
      </section>
    )
  }


  // 클릭/드래그로 JD 점프 — 해당 JD 의 첫 step 위치로 페이지 스크롤
  const jumpToJd = (jdIdx: number) => {
    const section = ref.current
    if (!section) return
    let firstStep = 0
    for (let i = 0; i < jdIdx; i++) firstStep += stepCounts[i]
    const progress = totalSteps === 0 ? 0 : firstStep / totalSteps
    const sectionTop = section.offsetTop
    const sectionHeight = section.offsetHeight
    const vh = window.innerHeight
    // +1 px 살짝 더해서 ScrollTrigger 가 새 step 안에 진입하도록
    const targetY = sectionTop + progress * (sectionHeight - vh) + 1

    const lenis = (window as { __lenis?: { scrollTo: (y: number, opts?: { immediate?: boolean }) => void } }).__lenis
    // immediate — 중간 step 들 거치며 다이얼 연쇄 트리거되는 거 방지
    if (lenis) lenis.scrollTo(targetY, { immediate: true })
    else window.scrollTo({ top: targetY })
  }

  return (
    <section
      ref={ref}
      style={{
        position: 'relative',
        height: `${totalSteps * STEP_VH}vh`,
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
          padding: 'clamp(80px, 10vh, 120px) clamp(40px, 6vw, 120px)',
          overflow: 'hidden',
        }}
      >
        <Header active={active.jdIdx} total={items.length} />

        {/* 본문 — 좌 VaultDial / 우 ContentDial */}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(160px, 220px) minmax(0, 600px)',
              columnGap: 'clamp(40px, 5vw, 80px)',
              alignItems: 'center',
              width: 'fit-content',
              maxWidth: '100%',
            }}
          >
            <VaultDial items={items} activeIdx={active.jdIdx} onSelect={jumpToJd} />
            <ContentDial items={items} globalPos={globalPos} />
          </div>
        </div>

        {/* progress — JD bar + sub-step ticks */}
        <ProgressBar active={active} stepCounts={stepCounts} />
      </div>
    </section>
  )
}

function ProgressBar({
  active,
  stepCounts,
}: {
  active: { jdIdx: number; subIdx: number }
  stepCounts: number[]
}) {
  return (
    <div
      style={{
        display: 'flex',
        gap: 14,
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: 24,
      }}
    >
      {stepCounts.map((count, i) => {
        const isActive = i === active.jdIdx
        const filled = isActive ? Math.max(0, active.subIdx + 1) : i < active.jdIdx ? count : 0
        return (
          <div key={i} style={{ display: 'flex', gap: 4 }}>
            {Array.from({ length: count }).map((_, j) => (
              <span
                aria-hidden
                key={j}
                style={{
                  width: isActive ? 14 : 6,
                  height: 2,
                  background: j < filled ? C.nexonBlue : C.cardBorder,
                  transition: 'width 220ms ease, background 220ms ease',
                  display: 'block',
                }}
              />
            ))}
          </div>
        )
      })}
    </div>
  )
}

// ─────────────────────────────────────────────

function Header({ active, total }: { active: number; total: number }) {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 32 }}>
      <span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 800,
          color: C.nexonBlue,
          letterSpacing: '0.22em',
          textTransform: 'uppercase',
        }}
      >
        CH 3 · 04
      </span>
      <span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 800,
          color: C.inkMuted,
          letterSpacing: '0.22em',
          textTransform: 'uppercase',
        }}
      >
        Job Description · 주요 업무
      </span>
      <span style={{ flex: 1, height: 1, background: C.cardBorder }} />
      <span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 700,
          color: C.inkMuted,
          letterSpacing: '0.18em',
        }}
      >
        {String(active + 1).padStart(2, '0')} / {String(total).padStart(2, '0')}
      </span>
    </div>
  )
}

const SLIDE_HEIGHT = 480 // px — 우측 콘텐츠 영역 높이

const NUM_H = 140 // dial 한 숫자 박스 높이

function DialNumber({
  idx,
  item,
  idxSpring,
  onSelect,
}: {
  idx: number
  item: JdItem
  idxSpring: MotionValue<number>
  onSelect: (i: number) => void
}) {
  // 활성과의 연속 거리에 따라 opacity gradient — 인접 숫자도 보여서 "롤링" 연결감
  const opacity = useTransform(idxSpring, (s) => {
    const d = Math.abs(s - idx)
    if (d <= 0.4) return 1
    if (d >= 2) return 0.12
    return 1 - ((d - 0.4) / 1.6) * 0.88
  })
  // 색상도 거리 기반 — 가운데 lock 영역이면 nexonBlue, 멀어지면 ink
  const color = useTransform(idxSpring, (s) => (Math.abs(s - idx) <= 0.5 ? C.nexonBlue : C.ink))
  return (
    <motion.button
      type="button"
      onClick={() => onSelect(idx)}
      style={{
        fontFamily: FONT_DISPLAY,
        fontSize: 'clamp(96px, 12vw, 140px)',
        lineHeight: 1,
        fontWeight: 800,
        color,
        opacity,
        letterSpacing: '-0.05em',
        height: NUM_H,
        display: 'flex',
        alignItems: 'center',
        fontVariantNumeric: 'tabular-nums',
        background: 'none',
        border: 0,
        padding: 0,
        cursor: 'pointer',
        textAlign: 'left',
      }}
    >
      {String(item.n).padStart(2, '0')}
    </motion.button>
  )
}

function VaultDial({
  items,
  activeIdx,
  onSelect,
}: {
  items: readonly JdItem[]
  activeIdx: number
  onSelect: (idx: number) => void
}) {
  const WINDOW_H = SLIDE_HEIGHT
  // activeIdx 를 spring 으로 부드럽게 보간 — 정수 jump 가 부드러운 회전으로 변환
  const idxMotion = useMotionValue(activeIdx)
  useEffect(() => {
    idxMotion.set(activeIdx)
  }, [activeIdx, idxMotion])
  const idxSpring = useSpring(idxMotion, { stiffness: 180, damping: 24, mass: 0.7 })
  const dialY = useTransform(idxSpring, (s) => (WINDOW_H - NUM_H) / 2 - s * NUM_H)

  return (
    <div
      style={{
        position: 'relative',
        height: WINDOW_H,
        width: '100%',
        overflow: 'hidden',
        WebkitMaskImage:
          'linear-gradient(180deg, transparent 0%, black 22%, black 78%, transparent 100%)',
        maskImage:
          'linear-gradient(180deg, transparent 0%, black 22%, black 78%, transparent 100%)',
        cursor: 'grab',
        touchAction: 'none',
        userSelect: 'none',
      }}
    >
      <motion.div
        drag="y"
        dragConstraints={{ top: 0, bottom: 0 }}
        dragElastic={0.35}
        dragMomentum={false}
        onDragEnd={(_, info) => {
          const stepDelta = Math.round(-info.offset.y / NUM_H)
          if (stepDelta === 0) return
          const next = Math.max(0, Math.min(items.length - 1, activeIdx + stepDelta))
          if (next !== activeIdx) onSelect(next)
        }}
        whileDrag={{ cursor: 'grabbing' }}
        style={{ y: dialY, display: 'flex', flexDirection: 'column' }}
      >
        {items.map((it, i) => (
          <DialNumber key={it.n} idx={i} item={it} idxSpring={idxSpring} onSelect={onSelect} />
        ))}
      </motion.div>
      {/* 가운데 활성 라인 — 다이얼 lock 느낌 */}
      <span
        aria-hidden
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: '50%',
          height: 1,
          background: C.cardBorder,
          pointerEvents: 'none',
        }}
      />
    </div>
  )
}

/**
 * ContentDial — 모든 JD 의 헤더 + evidence 를 단일 vertical stack 으로 렌더.
 *
 * globalPos: 전체 step 안 stack 위치 (continuous, 0..totalSteps).
 * 스크롤이 직접 y / opacity 를 구동.
 * JD boundary 도 stack 안 두 슬롯 사이일 뿐이라 jdTitle 이 자연스럽게 밑에서 올라옴.
 */
const ITEM_H = 240 // 본문 dial 한 슬롯 높이 (긴 문단 여유)
const VERTICAL_OFFSET = -36 // 활성 슬롯을 윈도우 중심보다 36px 위로

type SlotData =
  | { kind: 'header'; item: JdItem }
  | { kind: 'evidence'; item: JdItem; evidence: EvidenceItem; idx: number; total: number }

function ContentDial({ items, globalPos }: { items: readonly JdItem[]; globalPos: MotionValue<number> }) {
  // flat slot list — JD i 의 [header, ev0, ev1, ...] 를 순서대로 펼침
  const slots: SlotData[] = []
  items.forEach((item) => {
    slots.push({ kind: 'header', item })
    item.evidence.forEach((evidence, idx) => {
      slots.push({ kind: 'evidence', item, evidence, idx, total: item.evidence.length })
    })
  })

  const y = useTransform(
    globalPos,
    (p) => (SLIDE_HEIGHT - ITEM_H) / 2 - p * ITEM_H + VERTICAL_OFFSET,
  )

  return (
    <div
      style={{
        position: 'relative',
        height: SLIDE_HEIGHT,
        width: '100%',
        overflow: 'hidden',
        WebkitMaskImage:
          'linear-gradient(180deg, transparent 0%, black 18%, black 82%, transparent 100%)',
        maskImage:
          'linear-gradient(180deg, transparent 0%, black 18%, black 82%, transparent 100%)',
      }}
    >
      <motion.div
        style={{
          y,
          display: 'flex',
          flexDirection: 'column',
          width: '100%',
        }}
      >
        {slots.map((slot, i) => (
          <Slot key={i} index={i} pos={globalPos}>
            {slot.kind === 'header' ? (
              <HeaderInner item={slot.item} />
            ) : (
              <EvidenceInner evidence={slot.evidence} idx={slot.idx} total={slot.total} />
            )}
          </Slot>
        ))}
      </motion.div>
    </div>
  )
}

function Slot({
  index,
  pos,
  children,
}: {
  index: number
  pos: MotionValue<number>
  children: React.ReactNode
}) {
  // 거리 기반 연속 opacity: 가운데 → 1, 1 거리 → ~0.4, 2+ → 0.1
  const opacity = useTransform(pos, (p) => {
    const d = Math.abs(p - index)
    if (d <= 0.45) return 1
    if (d >= 2) return 0.1
    return 1 - ((d - 0.45) / (2 - 0.45)) * (1 - 0.1)
  })
  return (
    <motion.div
      style={{
        height: ITEM_H,
        display: 'flex',
        alignItems: 'flex-start',
        paddingTop: 24,
        opacity,
      }}
    >
      <div style={{ width: '100%', maxWidth: 600 }}>{children}</div>
    </motion.div>
  )
}

function HeaderInner({ item }: { item: JdItem }) {
  return (
    <>
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: '0.22em',
          color: C.nexonBlue,
          textTransform: 'uppercase',
          marginBottom: 14,
        }}
      >
        JD Match · {String(item.n).padStart(2, '0')}
      </div>
      <h3
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 'clamp(24px, 2.8vw, 34px)',
          fontWeight: 800,
          lineHeight: 1.22,
          color: C.ink,
          margin: 0,
          marginBottom: 14,
          letterSpacing: '-0.025em',
          wordBreak: 'keep-all',
        }}
      >
        {item.jdTitle}
      </h3>
      <p
        style={{
          fontFamily: FONT_BODY,
          fontSize: 'clamp(13.5px, 1.1vw, 16px)',
          lineHeight: 1.65,
          color: C.inkSoft,
          margin: 0,
          fontWeight: 500,
          wordBreak: 'keep-all',
        }}
      >
        {item.jdSub}
      </p>
    </>
  )
}

function EvidenceInner({
  evidence,
  idx,
  total,
}: {
  evidence: EvidenceItem
  idx: number
  total: number
}) {
  return (
    <>
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: '0.22em',
          color: C.inkMuted,
          textTransform: 'uppercase',
          marginBottom: 14,
        }}
      >
        Evidence · {String(idx + 1).padStart(2, '0')} / {String(total).padStart(2, '0')}
      </div>
      <EvidenceLarge item={evidence} />
    </>
  )
}

function EvidenceLarge({ item }: { item: EvidenceItem }) {
  const text = typeof item === 'string' ? item : item.text
  const isReport = typeof item !== 'string'
  let body: React.ReactNode = text
  if (isReport && item.highlight && text.includes(item.highlight)) {
    const [before, after] = text.split(item.highlight)
    body = (
      <>
        {before}
        <TooltipCard card={<ReportCard report={item.report} />} width={400}>
          {item.highlight}
        </TooltipCard>
        {after}
      </>
    )
  }
  return (
    <p
      style={{
        fontFamily: FONT_BODY,
        fontSize: 'clamp(18px, 1.85vw, 22px)',
        lineHeight: 1.6,
        fontWeight: 500,
        color: C.inkSoft,
        margin: 0,
        letterSpacing: '-0.012em',
        wordBreak: 'keep-all',
      }}
    >
      {body}
    </p>
  )
}

function StaticSlide({ item }: { item: JdItem }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(140px, 200px) minmax(0, 600px)',
        columnGap: 'clamp(32px, 4vw, 64px)',
        alignItems: 'start',
      }}
    >
      <span
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 'clamp(72px, 9vw, 116px)',
          fontWeight: 800,
          lineHeight: 0.85,
          color: C.nexonBlue,
          letterSpacing: '-0.05em',
        }}
      >
        {String(item.n).padStart(2, '0')}
      </span>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 18, maxWidth: 600 }}>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            fontWeight: 800,
            letterSpacing: '0.22em',
            color: C.nexonBlue,
            textTransform: 'uppercase',
          }}
        >
          JD Match · {String(item.n).padStart(2, '0')}
        </div>
        <h3
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(22px, 2.6vw, 30px)',
            fontWeight: 800,
            lineHeight: 1.22,
            color: C.ink,
            margin: 0,
            letterSpacing: '-0.025em',
            wordBreak: 'keep-all',
          }}
        >
          {item.jdTitle}
        </h3>
        <p
          style={{
            fontFamily: FONT_BODY,
            fontSize: 'clamp(13.5px, 1.05vw, 15.5px)',
            lineHeight: 1.65,
            color: C.inkSoft,
            margin: 0,
            fontWeight: 500,
            wordBreak: 'keep-all',
          }}
        >
          {item.jdSub}
        </p>
        <ul
          style={{
            margin: 0,
            padding: 0,
            listStyle: 'none',
            display: 'flex',
            flexDirection: 'column',
            gap: 10,
            marginTop: 4,
          }}
        >
          {item.evidence.map((e, i) => {
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
                  fontSize: 13.5,
                  lineHeight: 1.6,
                  color: C.inkSoft,
                  paddingLeft: 22,
                  position: 'relative',
                  fontWeight: 500,
                  wordBreak: 'keep-all',
                }}
              >
                <svg
                  style={{ position: 'absolute', left: 0, top: 4 }}
                  width="16"
                  height="16"
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
      </div>
    </div>
  )
}

function ReportCard({ report }: { report: ReportTooltip }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ fontFamily: FONT_MONO, fontSize: 10, letterSpacing: '0.18em', color: '#7dd3fc', fontWeight: 700 }}>
        REPORT · PDF
      </div>
      <div style={{ fontSize: 14, fontWeight: 800, color: '#fff', lineHeight: 1.35 }}>{report.title}</div>
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
        style={{
          marginTop: 4,
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          fontFamily: FONT_MONO,
          fontSize: 11,
          color: '#7dd3fc',
          textDecoration: 'none',
          fontWeight: 700,
          pointerEvents: 'auto',
          letterSpacing: '0.04em',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <span>PDF 열기 →</span>
      </a>
    </div>
  )
}
