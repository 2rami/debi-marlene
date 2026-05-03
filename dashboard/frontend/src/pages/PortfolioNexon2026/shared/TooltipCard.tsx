import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { useState, type ReactNode, type MouseEvent } from 'react'

interface TooltipCardProps {
  children: ReactNode  // 트리거 (hover 대상)
  card: ReactNode      // 카드 안에 보일 내용
  width?: number       // 카드 가로 px (default 360)
}

/** Aceternity 풍 마우스 추적 tooltip card. spring + parallax tilt. */
export default function TooltipCard({ children, card, width = 360 }: TooltipCardProps) {
  const [open, setOpen] = useState(false)

  const x = useMotionValue(0)
  // -50 ~ +50 px 범위 마우스 위치 → -8 ~ +8 deg 회전
  const rotateY = useSpring(useTransform(x, [-100, 100], [-8, 8]), {
    stiffness: 220,
    damping: 18,
  })
  const translateX = useSpring(useTransform(x, [-100, 100], [-12, 12]), {
    stiffness: 200,
    damping: 22,
  })

  function handleMove(e: MouseEvent<HTMLSpanElement>) {
    const rect = e.currentTarget.getBoundingClientRect()
    const half = rect.width / 2
    x.set(e.clientX - rect.left - half)
  }

  return (
    <span
      style={{ position: 'relative', display: 'inline', cursor: 'help' }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onMouseMove={handleMove}
    >
      <span
        style={{
          background: 'linear-gradient(180deg, transparent 60%, rgba(0, 80, 220, 0.18) 60%)',
          padding: '0 1px',
          fontWeight: 700,
        }}
      >
        {children}
      </span>
      <AnimatePresence mode="wait">
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.94 }}
            animate={{ opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 260, damping: 22 } }}
            exit={{ opacity: 0, y: 8, scale: 0.96, transition: { duration: 0.15 } }}
            style={{
              position: 'absolute',
              top: 'calc(100% + 8px)',
              left: '50%',
              transformOrigin: 'top center',
              translateX: '-50%',
              width,
              maxWidth: '90vw',
              zIndex: 50,
              pointerEvents: 'auto',
            }}
          >
            <motion.div
              style={{
                rotateY,
                x: translateX,
                background: 'rgba(20, 22, 28, 0.96)',
                color: '#f5f5f5',
                borderRadius: 14,
                padding: '18px 20px',
                boxShadow: '0 18px 60px -12px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255,255,255,0.08)',
                fontSize: 13,
                lineHeight: 1.55,
                backdropFilter: 'blur(6px)',
              }}
            >
              {card}
            </motion.div>
            {/* tail (위쪽으로 향하는 화살표) */}
            <div
              style={{
                position: 'absolute',
                top: -6,
                left: '50%',
                transform: 'translateX(-50%) rotate(45deg)',
                width: 12,
                height: 12,
                background: 'rgba(20, 22, 28, 0.96)',
                boxShadow: '-1px -1px 0 0 rgba(255,255,255,0.08)',
              }}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  )
}
