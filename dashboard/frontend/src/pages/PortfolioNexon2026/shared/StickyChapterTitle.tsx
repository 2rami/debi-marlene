import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { C, FONT_DISPLAY } from './colors'

/**
 * 스크롤 시 화면 중앙에 있던 큰 워드마크(CH 1 WHO.)가
 * 부드럽게 축소되면서 좌측 상단으로 이동하여 고정되는 컴포넌트입니다.
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

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger)
    const container = containerRef.current
    const textContainer = textContainerRef.current
    const textEl = textRef.current
    if (!container || !textContainer || !textEl) return

    // 타임라인 생성: 챕터 시작부터 100vh 스크롤 동안 작아짐
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: container,
        start: 'top top',
        end: '+=100%', // 1 화면 높이 동안 애니메이션 진행
        scrub: 1, // 부드러운 스크러빙
      },
    })

    // 초기 상태: 중앙에 거대한 텍스트
    gsap.set(textContainer, {
      position: 'sticky',
      top: 0,
      padding: '12vh 0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    })

    // 화면 크기에 따른 스케일 비율 (최종 크기는 약 32px 정도)
    const finalScale = 0.15

    // 화면 중앙(초기 위치)과 좌측 상단(목표 위치)의 거리 계산
    tl.to(textEl, {
      scale: finalScale,
      xPercent: 45, // 중앙에서 우측으로
      yPercent: -45, // 중앙에서 상단으로
      opacity: 0.3, // 너무 튀지 않게 투명도 조절
      ease: 'power2.inOut',
      duration: 1,
    })

    return () => {
      tl.kill()
    }
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
          pointerEvents: 'none', // 클릭 방해 방지
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
      
      {/* 실제 챕터 내용 (워드마크 아래에서부터 스크롤되어 올라옴) */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        {children}
      </div>
    </div>
  )
}
