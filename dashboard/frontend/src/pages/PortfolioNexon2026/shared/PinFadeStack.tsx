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
      if (items.length === 0) return

      // ── 1. 첫 번째 섹션 진입 연출 (Scale-up + Slide-up) ──
      // Hero에서 넘어올 때 작게 시작해서 커지면서 올라옴
      const first = items[0]
      gsap.fromTo(first, 
        { scale: 0.85, y: 100, opacity: 0 },
        {
          scale: 1,
          y: 0,
          opacity: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: first,
            start: 'top 95%', // 화면 하단에 살짝 보일 때 시작
            end: 'top 15%',  // 상단에 거의 붙을 때 완성
            scrub: 0.8,
          }
        }
      )

      // ── 2. 섹션 간 전환 로직 ──
      items.forEach((item, i) => {
        const next = items[i + 1]
        if (!next) return

        // 현재 섹션을 고정(pin)
        ScrollTrigger.create({
          trigger: item,
          start: 'top top',
          endTrigger: next,
          end: 'top top',
          pin: true,
          pinSpacing: false,
        })

        if (i === 0) {
          // 첫 번째 카드(예: Hero CH1 WHO): 작아지면서 사라짐
          // 다음 카드 진입의 앞 60% 구간에서 scale-down + fade out 완료
          gsap.to(item, {
            opacity: 0,
            scale: 0.7,
            y: -60,
            ease: 'power2.in',
            scrollTrigger: {
              trigger: next,
              start: 'top bottom',
              end: 'top 40%', // 빨리 사라짐 — next 가 viewport top 닿기 전에 완료
              scrub: 0.4,
            },
          })

          // 두 번째 카드: 첫 번째가 다 작아진 후 디졸브 페이드인
          gsap.fromTo(next,
            { opacity: 0 },
            {
              opacity: 1,
              ease: 'none',
              scrollTrigger: {
                trigger: next,
                start: 'top 40%', // 첫 번째가 거의 사라진 시점부터
                end: 'top top',
                scrub: 0.4,
              },
            }
          )
        } else {
          // 나머지 카드: 순수 디졸브 (opacity 만)
          gsap.to(item, {
            opacity: 0,
            ease: 'none',
            scrollTrigger: {
              trigger: next,
              start: 'top bottom',
              end: 'top top',
              scrub: 0.4,
            },
          })
        }
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
