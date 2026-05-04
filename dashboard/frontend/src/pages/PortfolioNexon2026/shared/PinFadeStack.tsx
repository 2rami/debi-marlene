import { useLayoutEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

/**
 * 자식 요소들을 카드 스택으로 만든다.
 * 각 자식은 viewport에 pin되고, 다음 자식이 들어오면서 crossfade out.
 *
 * 사용:
 *   <PinFadeStack>
 *     <div data-pinfade>...</div>
 *     <div data-pinfade>...</div>
 *   </PinFadeStack>
 *
 * 모바일(<=1024px)에서는 비활성 — 일반 세로 스크롤로 두는 게 UX 안전.
 */
export default function PinFadeStack({ children }: { children: React.ReactNode }) {
  const stackRef = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    if (typeof window === 'undefined') return
    if (window.matchMedia('(max-width: 1024px)').matches) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const root = stackRef.current
    if (!root) return

    const ctx = gsap.context(() => {
      const items = gsap.utils.toArray<HTMLElement>('[data-pinfade]', root)
      if (items.length < 2) return

      items.forEach((item, i) => {
        const next = items[i + 1]
        if (!next) return

        ScrollTrigger.create({
          trigger: item,
          start: 'top top',
          endTrigger: next,
          end: 'top top',
          pin: true,
          pinSpacing: false,
        })

        gsap.to(item, {
          opacity: 0,
          y: -32,
          scale: 0.97,
          ease: 'power2.inOut',
          scrollTrigger: {
            trigger: next,
            start: 'top bottom',
            end: 'top top',
            scrub: 0.6,
          },
        })
      })
    }, root)

    return () => ctx.revert()
  }, [])

  return (
    <div ref={stackRef} style={{ position: 'relative' }}>
      {children}
    </div>
  )
}
