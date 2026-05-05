import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { C, FONT_DISPLAY } from './colors'

gsap.registerPlugin(ScrollTrigger)

/**
 * 챕터 워드마크 + content wrapper.
 * 워드마크는 단어별로 split → stagger reveal (NexonGate Hero 의 순차 등장 패턴).
 */
type StickyMode = 'off' | 'entry' | 'full'

export default function StickyChapterTitle({
  text,
  children,
}: {
  text: string
  children: React.ReactNode
  mode?: StickyMode
}) {
  const containerRef = useRef<HTMLDivElement>(null)

  // 단어별 split — "CH 1 WHO." → ["CH", "1", "WHO."]
  const words = text.split(/\s+/).filter(Boolean)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const wordEls = container.querySelectorAll<HTMLElement>('.word-piece')
    if (wordEls.length === 0) return

    // ?reveal=off — 정적 캡처용 instant visible
    if (typeof window !== 'undefined') {
      try {
        if (new URLSearchParams(window.location.search).get('reveal') === 'off') {
          wordEls.forEach((w) => { w.style.opacity = '1' })
          return
        }
      } catch {}
    }

    const ctx = gsap.context(() => {
      // ScrollReveal 패턴 — 모든 단어가 흐릿하게 보이고, 스크롤 진행에 따라 한 단어씩 진해짐
      gsap.fromTo(wordEls,
        { opacity: 0.15 },
        {
          opacity: 1,
          stagger: 0.2,
          ease: 'none',
          scrollTrigger: {
            trigger: container,
            start: 'top 85%',
            end: 'top 25%',
            scrub: true,
            invalidateOnRefresh: true,
          },
        }
      )
    }, container)

    return () => ctx.revert()
  }, [])

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <div
        ref={containerRef}
        style={{
          padding: '12vh 0',
          textAlign: 'center',
          overflow: 'hidden',
          pointerEvents: 'none',
          fontFamily: FONT_DISPLAY,
          fontSize: 'clamp(80px, 18vw, 224px)',
          fontWeight: 900,
          lineHeight: 0.85,
          letterSpacing: '-0.05em',
          color: C.nexonBlue,
          whiteSpace: 'nowrap',
        }}
      >
        {words.map((w, i) => (
          <span
            key={i}
            className="word-piece"
            style={{
              display: 'inline-block',
              willChange: 'transform, clip-path',
              marginRight: i < words.length - 1 ? '0.25em' : 0,
            }}
          >
            {w}
          </span>
        ))}
      </div>

      <div style={{ position: 'relative' }}>{children}</div>
    </div>
  )
}
