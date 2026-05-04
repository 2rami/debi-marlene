import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { C, FONT_DISPLAY } from './colors'

/**
 * 스크롤 시 화면 중앙에 있던 큰 워드마크(CH 1 WHO.)가
 * 부드럽게 축소되면서 좌측 상단으로 이동하여 고정되는 컴포넌트입니다.
 * 여기에 "전체 섹션 진입 연출(Scale-up)"을 추가했습니다.
 */
export default function StickyChapterTitle({
  text,
  children,
}: {
  text: string
  children: React.ReactNode
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  const textContainerRef = useRef<HTMLDivElement>(null)
  const textRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger)
    const container = containerRef.current
    const textContainer = textContainerRef.current
    const textEl = textRef.current
    const contentEl = contentRef.current
    if (!container || !textContainer || !textEl || !contentEl) return

    const ctx = gsap.context(() => {
      // ── 1. 전체 섹션 진입 연출 (사용자 요청: 다 작아지고 올라오게) ──
      // 워드마크와 내용물 전체를 감싸서 진입 모션 적용
      gsap.fromTo([textEl, contentEl], 
        { scale: 0.7, y: 150, opacity: 0 },
        {
          scale: 1,
          y: 0,
          opacity: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: container,
            start: 'top 90%', 
            end: 'top 20%',
            scrub: 1,
          }
        }
      )

      // ── 2. 워드마크 축소 및 이동 (기존 로직) ──
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: container,
          start: 'top top',
          end: '+=100%', 
          scrub: 1,
        },
      })

      const finalScale = 0.15
      tl.to(textEl, {
        scale: finalScale,
        xPercent: 45,
        yPercent: -45,
        opacity: 0.3,
        ease: 'power2.inOut',
        duration: 1,
      })
    }, container)

    return () => ctx.revert()
  }, [])

  return (
    <div ref={containerRef} style={{ position: 'relative', width: '100%' }}>
      {/* 고정되는 텍스트 영역 */}
      <div
        ref={textContainerRef}
        style={{
          position: 'sticky',
          top: 0,
          width: '100%',
          padding: '12vh 0',
          pointerEvents: 'none',
          zIndex: 50,
          overflow: 'hidden',
        }}
      >
        <div
          ref={textRef}
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(80px, 18vw, 224px)',
            fontWeight: 900,
            lineHeight: 0.85,
            letterSpacing: '-0.05em',
            color: C.nexonBlue,
            whiteSpace: 'nowrap',
            willChange: 'transform',
            transformOrigin: 'center center',
          }}
        >
          {text}
        </div>
      </div>
      
      {/* 실제 챕터 내용 (contentRef로 감싸서 전체 애니메이션 적용) */}
      <div ref={contentRef} style={{ position: 'relative', zIndex: 1 }}>
        {children}
      </div>
    </div>
  )
}
