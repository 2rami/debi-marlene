import React, { useEffect, useRef, useMemo, ReactNode, RefObject } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

interface ScrollRevealProps {
  children: ReactNode
  scrollContainerRef?: RefObject<HTMLElement>
  enableBlur?: boolean
  baseOpacity?: number
  baseRotation?: number
  blurStrength?: number
  containerClassName?: string
  textClassName?: string
  textStyle?: React.CSSProperties
  rotationEnd?: string
  wordAnimationEnd?: string
}

const ScrollReveal: React.FC<ScrollRevealProps> = ({
  children,
  scrollContainerRef,
  enableBlur = true,
  baseOpacity = 0.1,
  baseRotation = 3,
  blurStrength = 4,
  containerClassName = '',
  textClassName = '',
  textStyle,
  rotationEnd = 'bottom bottom',
  wordAnimationEnd = 'bottom bottom',
}) => {
  const containerRef = useRef<HTMLDivElement>(null)

  const splitText = useMemo(() => {
    const text = typeof children === 'string' ? children : ''
    return text.split(/(\s+)/).map((word, index) => {
      if (word.match(/^\s+$/)) return word
      return (
        <span className="inline-block word" key={index}>
          {word}
        </span>
      )
    })
  }, [children])

  useEffect(() => {
    const el = containerRef.current
    if (!el) return

    // ?reveal=off 가드 — Figma html-to-design 등 정적 캡처용
    if (typeof window !== 'undefined') {
      try {
        if (new URLSearchParams(window.location.search).get('reveal') === 'off') {
          const wordEls = el.querySelectorAll<HTMLElement>('.word')
          wordEls.forEach((w) => {
            w.style.opacity = '1'
            w.style.filter = 'blur(0px)'
          })
          el.style.transform = 'none'
          return
        }
      } catch {}
    }

    const scroller = scrollContainerRef && scrollContainerRef.current ? scrollContainerRef.current : window

    // gsap.context 로 묶어서 자기 만든 trigger 만 cleanup
    const ctx = gsap.context(() => {
      gsap.fromTo(
        el,
        { transformOrigin: '0% 50%', rotate: baseRotation },
        {
          ease: 'none',
          rotate: 0,
          scrollTrigger: {
            trigger: el,
            scroller,
            start: 'top bottom',
            end: rotationEnd,
            scrub: true,
          },
        },
      )

      const wordElements = el.querySelectorAll<HTMLElement>('.word')

      gsap.fromTo(
        wordElements,
        { opacity: baseOpacity, willChange: 'opacity' },
        {
          ease: 'none',
          opacity: 1,
          stagger: 0.1,
          scrollTrigger: {
            trigger: el,
            scroller,
            start: 'top bottom-=20%',
            end: wordAnimationEnd,
            scrub: true,
          },
        },
      )

      if (enableBlur) {
        gsap.fromTo(
          wordElements,
          { filter: `blur(${blurStrength}px)` },
          {
            ease: 'none',
            filter: 'blur(0px)',
            stagger: 0.1,
            scrollTrigger: {
              trigger: el,
              scroller,
              start: 'top bottom-=20%',
              end: wordAnimationEnd,
              scrub: true,
            },
          },
        )
      }
    }, el)

    return () => {
      ctx.revert() // 자기 컨텍스트 trigger 만 정리 (다른 컴포넌트 trigger 보존)
    }
  }, [scrollContainerRef, enableBlur, baseRotation, baseOpacity, rotationEnd, wordAnimationEnd, blurStrength])

  return (
    <div ref={containerRef} className={containerClassName} data-no-reveal>
      <p className={textClassName} style={textStyle}>{splitText}</p>
    </div>
  )
}

export default ScrollReveal
