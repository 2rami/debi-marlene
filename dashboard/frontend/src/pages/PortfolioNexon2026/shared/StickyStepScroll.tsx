import { useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'

/**
 * 스크롤리텔링(Scrollytelling) 컴포넌트
 * - 바깥쪽 컨테이너는 여러 화면(VH) 높이를 가짐
 * - 안쪽 컨테이너는 화면에 고정(sticky)됨
 * - 스크롤을 내릴 때마다 지정된 스텝(children)들이 페이드인/아웃됨
 */
export default function StickyStepScroll({
  children,
  stepCount,
}: {
  children: React.ReactNode[]
  stepCount: number
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  
  // 전체 높이는 스텝 개수 * 100vh
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  })

  return (
    <div
      ref={containerRef}
      style={{
        height: `${stepCount * 100}vh`, // 스크롤할 수 있는 빈 공간
        position: 'relative',
      }}
    >
      <div
        style={{
          position: 'sticky',
          top: 0,
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        }}
      >
        {children.map((child, i) => {
          // 각 스텝이 보여질 스크롤 구간 계산 (예: 3스텝이면 0~0.33, 0.33~0.66, 0.66~1.0)
          const stepSize = 1 / stepCount
          const start = Math.max(0, i * stepSize - 0.1)
          const peak = i * stepSize + stepSize / 2
          const end = Math.min(1, (i + 1) * stepSize + 0.1)

          // 해당 구간에서 투명도 0 -> 1 -> 0 으로 변함
          const opacity = useTransform(
            scrollYProgress,
            [start, peak, end],
            [0, 1, 0]
          )
          
          // 아래에서 위로 살짝 올라오는 효과
          const y = useTransform(
            scrollYProgress,
            [start, peak, end],
            [50, 0, -50]
          )

          return (
            <motion.div
              key={i}
              style={{
                position: 'absolute',
                width: '100%',
                opacity,
                y,
                pointerEvents: 'none', // 투명할 때 클릭 방지
              }}
            >
              <div style={{ pointerEvents: 'auto' }}>
                {child}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
