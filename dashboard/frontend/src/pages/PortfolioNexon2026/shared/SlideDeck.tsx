import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { ACCENT } from '../content/sionic'

/**
 * 사이오닉 슬라이드 덱.
 * - 일반 슬라이드: 휠/키 1회 = 다음 슬라이드 크로스페이드.
 * - substeps 슬라이드(프로젝트 카드 스택): 휠 deltaY 를 누적해 subProgress(0..substeps, float)를
 *   부드럽게 굴린다 → 카드가 스크롤처럼 연속 이동, 진행바도 연속. 경계(0/substeps)에서 슬라이드 전환.
 *   스크롤 컨테이너에 의존하지 않아 전환 타이밍과 무관하게 동작.
 * - scroll 슬라이드(푸터): 내부 세로 스크롤이 끝에 닿아야 전환.
 */

export interface Slide {
  node?: React.ReactNode
  render?: (subProgress: number) => React.ReactNode
  scroll?: boolean
  substeps?: number
}

export default function SlideDeck({ slides, accent = ACCENT }: { slides: Slide[]; accent?: string }) {
  const [index, setIndex] = useState(0)
  const [subProgress, setSubProgress] = useState(0)
  const lock = useRef(false)
  const touchY = useRef(0)
  const scrollerRef = useRef<HTMLDivElement>(null)
  const lastDir = useRef(1)
  const total = slides.length

  useEffect(() => {
    const el = scrollerRef.current
    if (!el) return
    const id = requestAnimationFrame(() => { el.scrollTop = lastDir.current < 0 ? el.scrollHeight : 0 })
    return () => cancelAnimationFrame(id)
  }, [index])

  useEffect(() => {
    const lockNow = (ms: number) => { lock.current = true; window.setTimeout(() => { lock.current = false }, ms) }
    const goSlide = (d: number) => {
      const next = Math.min(total - 1, Math.max(0, index + d))
      if (next === index) return
      lastDir.current = d
      lockNow(440) // 전환 직후 잠깐만 잠가 중복 전환 방지(짧게 — 다음 슬라이드에서 바로 휠 누적되게)
      setIndex(next)
      const nextSub = slides[next]?.substeps ?? 0
      setSubProgress(d < 0 ? (nextSub > 0 ? nextSub : 1) : 0)
    }
    const consumedByInner = (deltaY: number) => {
      if (!slides[index]?.scroll) return false
      const el = scrollerRef.current
      if (!el) return false
      const atTop = el.scrollTop <= 0
      const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 2
      if (deltaY > 0 && !atBottom) return true
      if (deltaY < 0 && !atTop) return true
      return false
    }
    const stepDiscrete = (dir: number, maxSub: number) => {
      if (lock.current) return
      const cur = Math.round(subProgress)
      if (dir > 0) { if (cur < maxSub) setSubProgress(cur + 1); else goSlide(1) }
      else { if (cur > 0) setSubProgress(cur - 1); else goSlide(-1) }
    }
    const onWheel = (e: WheelEvent) => {
      if (consumedByInner(e.deltaY)) return
      e.preventDefault()
      if (lock.current) return
      const sub = slides[index]?.substeps ?? 0
      // 일반 슬라이드도 1단계(maxSub=1)로 휠을 누적 → 조금만 굴려도 진행바가 즉시 차오른다(전환 순간에만 차는 것 방지).
      const maxSub = sub > 0 ? sub : 1
      const div = sub > 0 ? 900 : 240 // 카드 스택은 천천히(자세히), 일반 슬라이드는 빠르게 전환
      const np = subProgress + e.deltaY / div
      if (np >= maxSub) goSlide(1)
      else if (np <= 0 && e.deltaY < 0) goSlide(-1)
      else setSubProgress(Math.max(0, Math.min(maxSub, np)))
    }
    const onKey = (e: KeyboardEvent) => {
      const fwd = ['ArrowDown', 'PageDown', 'ArrowRight', ' '].includes(e.key)
      const bwd = ['ArrowUp', 'PageUp', 'ArrowLeft'].includes(e.key)
      if (!fwd && !bwd) return
      if (consumedByInner(fwd ? 1 : -1)) return
      e.preventDefault()
      const maxSub = slides[index]?.substeps ?? 0
      if (maxSub > 0) stepDiscrete(fwd ? 1 : -1, maxSub)
      else if (!lock.current) goSlide(fwd ? 1 : -1)
    }
    const onTouchStart = (e: TouchEvent) => { touchY.current = e.touches[0].clientY }
    const onTouchEnd = (e: TouchEvent) => {
      const dy = touchY.current - e.changedTouches[0].clientY
      if (Math.abs(dy) < 40 || consumedByInner(dy)) return
      const maxSub = slides[index]?.substeps ?? 0
      if (maxSub > 0) stepDiscrete(dy > 0 ? 1 : -1, maxSub)
      else if (!lock.current) goSlide(dy > 0 ? 1 : -1)
    }
    window.addEventListener('wheel', onWheel, { passive: false })
    window.addEventListener('keydown', onKey)
    window.addEventListener('touchstart', onTouchStart, { passive: true })
    window.addEventListener('touchend', onTouchEnd, { passive: true })
    return () => {
      window.removeEventListener('wheel', onWheel)
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('touchstart', onTouchStart)
      window.removeEventListener('touchend', onTouchEnd)
    }
  }, [index, subProgress, total, slides])

  const cur = slides[index]
  const sub = cur?.substeps ?? 0
  const maxSub = sub > 0 ? sub : 1
  const subFraction = subProgress / maxSub
  const overall = total > 1 ? (index + subFraction) / (total - 1) : 0
  const goTo = (i: number) => { lastDir.current = i > index ? 1 : -1; setSubProgress(0); setIndex(i) }

  // 진행바 = 스크롤값(overall) 추적. 카드 구간은 연속, 일반 슬라이드 전환의 점프도 spring 으로 스르륵 차오름.
  const progressTarget = useMotionValue(0)
  const progressSpring = useSpring(progressTarget, { stiffness: 150, damping: 30, mass: 0.5 })
  const barWidth = useTransform(progressSpring, (v) => `${Math.min(100, Math.max(0, v * 100))}%`)
  useEffect(() => { progressTarget.set(Math.min(1, Math.max(0, overall))) }, [overall, progressTarget])

  return (
    <div style={{ position: 'fixed', inset: 0, overflow: 'hidden' }}>
      {/* 상단 진행바 — subProgress 까지 반영해 연속으로 차오름 */}
      <div style={{ position: 'fixed', top: 0, left: 0, right: 0, height: 3, background: 'rgba(140,150,165,0.16)', zIndex: 70 }}>
        <motion.div style={{ height: '100%', width: barWidth, background: accent }} />
      </div>

      <AnimatePresence mode="sync">
        <motion.div key={index} initial={{ opacity: 0, scale: 1.045, filter: 'blur(9px)' }} animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }} exit={{ opacity: 0, scale: 0.975, filter: 'blur(9px)' }} transition={{ duration: 0.72, ease: [0.45, 0, 0.2, 1] }} style={{ position: 'absolute', inset: 0 }}>
          {cur?.render ? cur.render(subProgress) : cur?.scroll ? (
            <div ref={scrollerRef} style={{ height: '100vh', overflowY: 'auto', overflowX: 'hidden' }}>{cur.node}</div>
          ) : (
            cur?.node
          )}
        </motion.div>
      </AnimatePresence>

      <div style={{ position: 'fixed', right: 26, top: '50%', transform: 'translateY(-50%)', display: 'flex', flexDirection: 'column', gap: 11, zIndex: 60 }}>
        {slides.map((s, i) => (
          <button key={i} onClick={() => goTo(i)} aria-label={`슬라이드 ${i + 1}`}
            style={{ width: s.substeps ? 7 : 8, height: s.substeps ? 16 : 8, borderRadius: s.substeps ? 4 : '50%', border: 'none', padding: 0, cursor: 'pointer', background: i === index ? accent : 'rgba(140,150,165,0.4)', transform: i === index ? 'scale(1.4)' : 'scale(1)', transition: 'all 260ms cubic-bezier(0.45,0,0.2,1)' }} />
        ))}
      </div>

      {index === 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.2 }}
          style={{ position: 'fixed', bottom: 30, left: '50%', transform: 'translateX(-50%)', display: 'flex', alignItems: 'center', gap: 9, zIndex: 60, color: 'rgba(150,160,175,0.85)', fontSize: 12, fontWeight: 600, letterSpacing: '0.04em', pointerEvents: 'none' }}>
          <motion.span animate={{ y: [0, 5, 0] }} transition={{ duration: 1.6, repeat: Infinity }}>스크롤 · 방향키로 넘기기</motion.span>
        </motion.div>
      )}
    </div>
  )
}
