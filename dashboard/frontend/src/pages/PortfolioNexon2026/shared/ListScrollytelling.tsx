import { useRef, useState } from 'react'
import { motion, AnimatePresence, useScroll, useMotionValueEvent } from 'framer-motion'
import { C, FONT_BODY } from './colors'

interface ListScrollytellingProps<T> {
  items: readonly T[]
  renderItem: (item: T, index: number) => React.ReactNode
  heightPerItem?: number // vh 단위
}

export default function ListScrollytelling<T>({ items, renderItem, heightPerItem = 70 }: ListScrollytellingProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [activeIndex, setActiveIndex] = useState(0)

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start center', 'end center']
  })

  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    const total = items.length
    let idx = Math.floor(latest * total)
    if (idx >= total) idx = total - 1
    if (idx < 0) idx = 0
    
    if (idx !== activeIndex) {
      setActiveIndex(idx)
    }
  })

  const totalHeight = `${items.length * heightPerItem}vh`

  return (
    <div ref={containerRef} style={{ height: totalHeight, position: 'relative' }}>
      <div
        style={{
          position: 'sticky',
          top: '25vh',
          height: 'auto',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div style={{ display: 'flex', gap: 6, marginBottom: 24, paddingLeft: 4 }}>
          {items.map((_, i) => (
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

        <div style={{ position: 'relative' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activeIndex}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            >
              {renderItem(items[activeIndex], activeIndex)}
            </motion.div>
          </AnimatePresence>
        </div>
        
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
          스크롤해서 다음 내용 보기
        </div>
      </div>
    </div>
  )
}
