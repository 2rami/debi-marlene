import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { C, FONT_MONO } from './colors'
import useIsMobile from './useIsMobile'

export type NavSection = {
  id: string
  no: string
  label: string
}

export default function SideNav({ sections }: { sections: NavSection[] }) {
  const [activeId, setActiveId] = useState<string>(sections[0]?.id ?? '')
  const [progress, setProgress] = useState(0)
  const isMobile = useIsMobile()

  useEffect(() => {
    const onScroll = () => {
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const ratio = Math.min(1, Math.max(0, window.scrollY / docHeight))
      setProgress(ratio)

      const viewportMid = window.innerHeight * 0.4
      let bestId = sections[0]?.id ?? ''
      let bestDist = Infinity
      sections.forEach((s) => {
        const el = document.getElementById(s.id)
        if (!el) return
        const rect = el.getBoundingClientRect()
        const dist = Math.abs(rect.top - viewportMid)
        if (rect.top < viewportMid && rect.bottom > viewportMid) {
          bestId = s.id
          bestDist = -1
          return
        }
        if (dist < bestDist) {
          bestDist = dist
          bestId = s.id
        }
      })
      setActiveId(bestId)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [sections])

  const scrollTo = (id: string) => {
    const el = document.getElementById(id)
    if (!el) return
    // CH 3·04 다이얼처럼 immediate 점프 — 핀 스크롤 챕터를 통과하지 않고 한 번에 이동
    const targetY = el.getBoundingClientRect().top + window.scrollY
    const lenis = (window as { __lenis?: { scrollTo: (y: number, opts?: { immediate?: boolean }) => void } }).__lenis
    if (lenis) lenis.scrollTo(targetY, { immediate: true })
    else window.scrollTo({ top: targetY })
  }

  if (isMobile) return null

  return (
    <nav
      aria-label="Section navigation"
      style={{
        position: 'fixed',
        right: 'clamp(20px, 3vw, 36px)',
        top: '50%',
        transform: 'translateY(-50%)',
        zIndex: 100,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
        pointerEvents: 'auto',
      }}
    >
      {/* Progress label */}
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 9,
          color: 'rgba(10, 18, 36, 0.45)',
          mixBlendMode: 'difference',
          textAlign: 'center',
          letterSpacing: '0.16em',
          fontWeight: 700,
          marginBottom: 4,
        }}
      >
        {String(Math.round(progress * 100)).padStart(2, '0')}%
      </div>

      {sections.map((s) => {
        const isActive = s.id === activeId
        return (
          <button
            key={`${s.id}-${s.no}`}
            onClick={() => scrollTo(s.id)}
            aria-label={`${s.no} ${s.label}`}
            style={{
              appearance: 'none',
              border: 'none',
              background: 'transparent',
              padding: 0,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              gap: 12,
              position: 'relative',
            }}
            onMouseEnter={(e) => {
              const tooltip = e.currentTarget.querySelector('[data-nav-tooltip]') as HTMLDivElement | null
              if (tooltip) tooltip.style.opacity = '1'
            }}
            onMouseLeave={(e) => {
              const tooltip = e.currentTarget.querySelector('[data-nav-tooltip]') as HTMLDivElement | null
              if (tooltip) tooltip.style.opacity = '0'
            }}
          >
            <div
              data-nav-tooltip
              style={{
                position: 'absolute',
                right: 'calc(100% + 14px)',
                top: '50%',
                transform: 'translateY(-50%)',
                whiteSpace: 'nowrap',
                fontFamily: FONT_MONO,
                fontSize: 10,
                fontWeight: 700,
                letterSpacing: '0.14em',
                color: C.ink,
                background: 'rgba(255, 255, 255, 0.95)',
                border: `1px solid ${C.cardBorder}`,
                padding: '6px 10px',
                borderRadius: 999,
                opacity: 0,
                transition: 'opacity 0.2s ease',
                pointerEvents: 'none',
                backdropFilter: 'blur(8px)',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
              }}
            >
              {s.no} · {s.label}
            </div>

            <motion.span
              animate={{ opacity: isActive ? 1 : 0, x: isActive ? 0 : 8 }}
              transition={{ duration: 0.25 }}
              style={{
                fontFamily: FONT_MONO,
                fontSize: 10,
                fontWeight: 700,
                color: C.nexonBlue,
                letterSpacing: '0.1em',
                mixBlendMode: 'difference',
              }}
            >
              {s.no}
            </motion.span>

            <motion.span
              animate={{
                width: isActive ? 28 : 12,
                background: isActive ? C.nexonBlue : 'rgba(10, 18, 36, 0.3)',
              }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              style={{
                display: 'inline-block',
                height: 2,
                borderRadius: 999,
              }}
            />
          </button>
        )
      })}
    </nav>
  )
}
