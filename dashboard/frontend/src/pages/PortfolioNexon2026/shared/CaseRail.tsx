import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { C, FONT_MONO } from './colors'
import CaseCard from './CaseCard'

type CaseItem = {
  no: number
  title: string
  problem: string
  approach: string
  result: string
  bridge: string
}

export default function CaseRail({ cases }: { cases: readonly CaseItem[] }) {
  const railRef = useRef<HTMLDivElement>(null)
  const cardRefs = useRef<(HTMLDivElement | null)[]>([])
  const [active, setActive] = useState(0)

  // 가운데 위치한 카드 감지
  useEffect(() => {
    const rail = railRef.current
    if (!rail) return

    const observer = new IntersectionObserver(
      (entries) => {
        // 가장 가시도가 높은 카드 찾기
        let bestIdx = active
        let bestRatio = 0
        entries.forEach((entry) => {
          const idx = Number(entry.target.getAttribute('data-idx'))
          if (entry.intersectionRatio > bestRatio) {
            bestRatio = entry.intersectionRatio
            bestIdx = idx
          }
        })
        if (bestRatio > 0) setActive(bestIdx)
      },
      {
        root: rail,
        threshold: [0.4, 0.6, 0.8, 1],
      },
    )

    cardRefs.current.forEach((el) => el && observer.observe(el))
    return () => observer.disconnect()
  }, [])

  const scrollTo = (idx: number) => {
    const target = cardRefs.current[idx]
    if (!target) return
    target.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
  }

  return (
    <div style={{ position: 'relative' }}>
      {/* Top: progress + nav */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          marginBottom: 24,
          padding: '0 4px',
        }}
      >
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 12,
            color: C.nexonBlue,
            fontWeight: 500,
            letterSpacing: '0.08em',
          }}
        >
          {String(active + 1).padStart(2, '0')} / {String(cases.length).padStart(2, '0')}
        </div>
        <div
          style={{
            display: 'flex',
            gap: 6,
            flex: 1,
          }}
        >
          {cases.map((c, i) => (
            <button
              key={c.no}
              onClick={() => scrollTo(i)}
              aria-label={`Case ${i + 1}`}
              style={{
                flex: 1,
                height: 4,
                borderRadius: 999,
                border: 'none',
                cursor: 'pointer',
                padding: 0,
                background:
                  i === active
                    ? C.nexonBlue
                    : i < active
                      ? 'rgba(0, 98, 223, 0.4)'
                      : 'rgba(0, 98, 223, 0.12)',
                transition: 'background 0.3s ease',
              }}
            />
          ))}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <NavButton
            direction="prev"
            disabled={active === 0}
            onClick={() => scrollTo(Math.max(0, active - 1))}
          />
          <NavButton
            direction="next"
            disabled={active === cases.length - 1}
            onClick={() => scrollTo(Math.min(cases.length - 1, active + 1))}
          />
        </div>
      </div>

      {/* Horizontal scroll rail */}
      <div
        ref={railRef}
        style={{
          display: 'flex',
          gap: 24,
          overflowX: 'auto',
          scrollSnapType: 'x mandatory',
          scrollPadding: '0 calc((100% - min(80vw, 720px)) / 2)',
          paddingBottom: 24,
          paddingTop: 8,
          paddingLeft: 'calc((100% - min(80vw, 720px)) / 2)',
          paddingRight: 'calc((100% - min(80vw, 720px)) / 2)',
          scrollbarWidth: 'none',
          WebkitOverflowScrolling: 'touch',
          // 좌우 페이드 마스크
          maskImage:
            'linear-gradient(to right, transparent 0, black 4%, black 96%, transparent 100%)',
          WebkitMaskImage:
            'linear-gradient(to right, transparent 0, black 4%, black 96%, transparent 100%)',
        }}
      >
        <style>{`.case-rail::-webkit-scrollbar { display: none; }`}</style>
        {cases.map((c, i) => (
          <motion.div
            key={c.no}
            ref={(el) => {
              cardRefs.current[i] = el
            }}
            data-idx={i}
            animate={{
              scale: i === active ? 1 : 0.94,
              opacity: i === active ? 1 : 0.55,
            }}
            transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
            style={{
              flex: '0 0 min(80vw, 720px)',
              scrollSnapAlign: 'center',
            }}
          >
            <CaseCard
              no={c.no}
              title={c.title}
              problem={c.problem}
              approach={c.approach}
              result={c.result}
              bridge={c.bridge}
            />
          </motion.div>
        ))}
      </div>

      <p
        style={{
          textAlign: 'center',
          fontFamily: FONT_MONO,
          fontSize: 11,
          color: C.inkMuted,
          letterSpacing: '0.08em',
          marginTop: 12,
          margin: '12px 0 0',
        }}
      >
        ← swipe / drag →
      </p>
    </div>
  )
}

function NavButton({
  direction,
  disabled,
  onClick,
}: {
  direction: 'prev' | 'next'
  disabled: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={direction === 'prev' ? '이전' : '다음'}
      style={{
        width: 36,
        height: 36,
        borderRadius: 999,
        border: `1px solid ${disabled ? 'rgba(0, 98, 223, 0.15)' : 'rgba(0, 98, 223, 0.3)'}`,
        background: disabled ? 'transparent' : C.bgWhite,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.4 : 1,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: C.nexonBlue,
        fontSize: 14,
        transition: 'all 0.2s ease',
        padding: 0,
      }}
    >
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        {direction === 'prev' ? (
          <path
            d="M9 11L4 7L9 3"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ) : (
          <path
            d="M5 3L10 7L5 11"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}
      </svg>
    </button>
  )
}
