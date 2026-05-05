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

import { useEffect } from 'react'
import Lenis from 'lenis'
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
      <Ch1About />
      <Ch2What />
      <Ch3Why />
      <Ch4Reach />
    </div>
    </CharacterDockProvider>
  )
}
