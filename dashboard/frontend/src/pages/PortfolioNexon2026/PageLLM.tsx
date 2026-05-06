/**
 * [플랫폼본부] 게임 도메인 LLM 평가 어시스턴트 (인턴) — 본사
 * 라우트: /portfolio/nexon/llm
 *
 * 페이지 구조 — 챕터별 컴포넌트 조합
 *   NexonGate (Hero)
 *   Ch1About    — 01 ABOUT, 02 ABOUT-DETAILS
 *   Ch2What     — 02 ARCHITECTURE, 03 TECH STACK
 *   Ch3Why      — 04 JD, 05 ELIGIBILITY, 06 PREFERRED, 07 TROUBLESHOOTING, 08 COLLAB
 *   Ch4Reach    — CTA + Footer
 */

import { useEffect, useRef } from 'react'
import Lenis from 'lenis'
import { trackEvent } from '../../lib/analytics'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { C, FONT_BODY } from './shared/colors'
import SideNav from './shared/SideNav'
import CornerLabels from './shared/CornerLabels'
import MapleChatbot from './shared/MapleChatbot'
import NexonGate from './shared/NexonGate'
import { useRevealOff } from './shared/useRevealOff'
import { CharacterDockProvider } from './shared/dockContext'

import Ch1About from './sections/Ch1About'
import Ch2What from './sections/Ch2What'
import Ch3Why from './sections/Ch3Why'
import Ch4Reach from './sections/Ch4Reach'

// 챕터별 진입 1회 발사. IntersectionObserver 25% 임계, fired flag 로 dedup.
function ChapterTrack({ chapter, children }: { chapter: string; children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  const fired = useRef(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting && !fired.current) {
            fired.current = true
            trackEvent('portfolio_chapter_view', { chapter })
            io.disconnect()
          }
        }
      },
      // viewport 위/아래 25% 를 잘라낸 가운데 50% 영역에 target 의 어떤 부분이라도
      // 들어오면 fire. 챕터 높이가 viewport 보다 큰 경우에도 안전하게 트리거됨.
      { threshold: 0, rootMargin: '-25% 0px -25% 0px' },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [chapter])
  return <div ref={ref}>{children}</div>
}

export default function PageLLM() {
  const revealOff = useRevealOff()

  // Lenis smooth scroll + GSAP ticker 연동
  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger)

    const lenis = new Lenis({
      // 쫀득한 스크롤 — 휠 입력 후 잠시 미끄러지듯 따라옴
      duration: 4,
      // lerp 가 작을수록 더 부드럽고 길게 미끄러짐 (default 0.1)
      lerp: 0.8,
      wheelMultiplier: 0.85,
      easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    })
    ;(window as any).__lenis = lenis
    lenis.scrollTo(0, { immediate: true })

    lenis.on('scroll', ScrollTrigger.update)
    const tickerCb = (time: number) => lenis.raf(time * 1000)
    gsap.ticker.add(tickerCb)
    gsap.ticker.lagSmoothing(0)

    return () => {
      gsap.ticker.remove(tickerCb)
      ScrollTrigger.getAll().forEach((st) => st.kill())
      lenis.destroy()
      ;(window as any).__lenis = null
    }
  }, [])

  return (
    <CharacterDockProvider>
    <div
      data-reveal-off={revealOff ? 'true' : undefined}
      style={{
        fontFamily: FONT_BODY,
        color: C.ink,
        letterSpacing: '-0.01em',
        background: C.bgLight,
        minHeight: '100vh',
        overflowX: 'clip',
      }}
    >
      {revealOff && (
        <style>{`
          /* ?reveal=off — Figma html-to-design / 정적 캡처용 일괄 visible */
          [data-reveal-off="true"] *,
          [data-reveal-off="true"] *::before,
          [data-reveal-off="true"] *::after {
            opacity: 1 !important;
            filter: none !important;
            visibility: visible !important;
            clip-path: none !important;
          }
          [data-reveal-off="true"] .word,
          [data-reveal-off="true"] .word-piece {
            opacity: 1 !important;
            filter: none !important;
            transform: none !important;
          }
        `}</style>
      )}

      <CornerLabels ctaLabel="GO TO BOT" ctaHref="https://debimarlene.com" />
      <MapleChatbot />

      <SideNav
        sections={[
          { id: 'hero', no: 'CH 0', label: 'GATE' },
          { id: 'about', no: 'CH 1', label: 'WHO' },
          { id: 'architecture', no: 'CH 2', label: 'WHAT' },
          { id: 'jdmatch', no: 'CH 3', label: 'WHY' },
          { id: 'contact', no: 'CH 4', label: 'REACH' },
        ]}
      />

      <NexonGate />
      <ChapterTrack chapter="ch1_about"><Ch1About /></ChapterTrack>
      <ChapterTrack chapter="ch2_what"><Ch2What /></ChapterTrack>
      <ChapterTrack chapter="ch3_why"><Ch3Why /></ChapterTrack>
      <ChapterTrack chapter="ch4_reach"><Ch4Reach /></ChapterTrack>
    </div>
    </CharacterDockProvider>
  )
}
