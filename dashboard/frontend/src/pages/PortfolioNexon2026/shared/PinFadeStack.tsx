import { useLayoutEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

/**
 * 자식 카드들을 자연 스크롤로 통과시키되, 들어올 때 디졸브 페이드인 / 나갈 때 페이드아웃.
 *
 * NOTE: 이전 버전은 ScrollTrigger pin 으로 카드 스택 효과 시도했으나, 콘텐츠가 viewport
 * 100vh 보다 길면 잘림 + pin spacing 으로 빈 화면 발생 문제로 pin 제거. 카드는 자체 height
 * 그대로 자연 스크롤. fade in/out 만 trigger 로 처리.
 *
 * 사용:
 *   <PinFadeStack>
 *     <div data-pinfade>...</div>
 *     <div data-pinfade>...</div>
 *   </PinFadeStack>
 */
export default function PinFadeStack({
  children,
  /** @deprecated pin 모드 제거됨. prop 유지는 사용처 호환성 위함. */
  fadeLast: _fadeLast,
}: {
  children: React.ReactNode
  fadeLast?: boolean
}) {
  void _fadeLast
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

      // PinFadeStack reveal 비활성 — 카드 안 모든 element 가 자연 스크롤로 그대로 보임
      // 자체 reveal 효과를 가진 컴포넌트 (ScrollReveal 등) 만 자기 모션으로 동작
      void items
    }, root)

    return () => ctx.revert()
  }, [])

  return (
    <div ref={stackRef} style={{ position: 'relative' }}>
      {children}
    </div>
  )
}
