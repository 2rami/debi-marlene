import { useRef, useState } from 'react'
import { motion, AnimatePresence, useScroll, useMotionValueEvent } from 'framer-motion'
import { C, FONT_BODY } from './colors'
import CaseCard from './CaseCard'

type CaseItem = {
  no: number
  title: string
  problem: string
  approach: string
  result: string
  bridge: string
}

export default function CaseScrollytelling({ cases }: { cases: readonly CaseItem[] }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [activeIndex, setActiveIndex] = useState(0)

  // 컨테이너 영역에 대한 스크롤 진행도를 추적 (0.0 ~ 1.0)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start center', 'end center']
  })

  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    // latest 값(0~1)을 배열 인덱스로 매핑
    const total = cases.length
    // 예: 6개면 0~0.16은 0번, 0.16~0.33은 1번...
    let idx = Math.floor(latest * total)
    if (idx >= total) idx = total - 1
    if (idx < 0) idx = 0
    
    if (idx !== activeIndex) {
      setActiveIndex(idx)
    }
  })

  // 각 케이스마다 스크롤할 높이를 확보 (1개당 70vh)
  const totalHeight = `${cases.length * 70}vh`

  return (
    <div ref={containerRef} style={{ height: totalHeight, position: 'relative' }}>
      
      {/* 우측 스티키 컨테이너: 화면에 고정되어 카드 하나만 보여줌 */}
      <div
        style={{
          position: 'sticky',
          top: '25vh', // 화면 중간쯤에 고정
          height: 'auto',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* 진행률 인디케이터 (현재 몇 번째 케이스인지) */}
        <div style={{ display: 'flex', gap: 6, marginBottom: 24, paddingLeft: 4 }}>
          {cases.map((_, i) => (
            <div
              key={i}
              style={{
                flex: 1,
                height: 4,
                borderRadius: 999,
                background: i === activeIndex 
                  ? C.nexonBlue 
                  : i < activeIndex 
                    ? 'rgba(0, 98, 223, 0.3)' 
                    : 'rgba(0, 98, 223, 0.1)',
                transition: 'background 0.3s ease'
              }}
            />
          ))}
        </div>

        {/* 현재 카드 애니메이션 렌더링 */}
        <div style={{ position: 'relative' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activeIndex}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            >
              <CaseCard {...cases[activeIndex]} />
            </motion.div>
          </AnimatePresence>
        </div>
        
        {/* 스크롤 유도 문구 */}
        <div 
          style={{ 
            marginTop: 24, 
            textAlign: 'center', 
            fontFamily: FONT_BODY, 
            color: C.inkMuted, 
            fontSize: 13,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8
          }}
        >
          <motion.div
            animate={{ y: [0, 5, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          >
            ↓
          </motion.div>
          스크롤해서 다음 케이스 보기
        </div>
      </div>
    </div>
  )
}
