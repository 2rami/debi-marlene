import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { C, FONT_BODY, FONT_MONO } from './colors'
import CaseCard from './CaseCard'

type CaseItem = {
  no: number
  title: string
  problem: string
  approach: string
  result: string
  bridge: string
}

export default function CaseTabs({ cases }: { cases: readonly CaseItem[] }) {
  const [activeIdx, setActiveIdx] = useState(0)

  return (
    <div
      style={{
        display: 'flex',
        gap: 32,
        height: 520, // 고정 높이로 한 화면에 들어오게 함
        alignItems: 'stretch',
        fontFamily: FONT_BODY,
      }}
    >
      {/* 왼쪽: 탭 리스트 */}
      <div
        style={{
          flex: '0 0 320px',
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          overflowY: 'auto',
          paddingRight: 16,
        }}
      >
        {cases.map((c, i) => {
          const isActive = i === activeIdx
          return (
            <button
              key={c.no}
              onClick={() => setActiveIdx(i)}
              style={{
                textAlign: 'left',
                background: isActive ? C.nexonBlue : C.bgWhite,
                color: isActive ? C.bgWhite : C.inkSoft,
                border: `1px solid ${isActive ? C.nexonBlue : C.cardBorder}`,
                borderRadius: 16,
                padding: '20px 24px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: 6,
                boxShadow: isActive ? '0 8px 24px rgba(0, 98, 223, 0.2)' : 'none',
              }}
            >
              <span
                style={{
                  fontFamily: FONT_MONO,
                  fontSize: 11,
                  letterSpacing: '0.1em',
                  color: isActive ? 'rgba(255,255,255,0.8)' : C.nexonBlue,
                  fontWeight: 700,
                }}
              >
                CASE {String(c.no).padStart(2, '0')}
              </span>
              <span
                style={{
                  fontSize: 15,
                  fontWeight: isActive ? 700 : 600,
                  lineHeight: 1.4,
                  letterSpacing: '-0.01em',
                }}
              >
                {c.title}
              </span>
            </button>
          )
        })}
      </div>

      {/* 오른쪽: 활성화된 케이스 디테일 */}
      <div style={{ flex: 1, position: 'relative' }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={activeIdx}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            style={{ height: '100%' }}
          >
            <div style={{ height: '100%', overflowY: 'auto', paddingRight: 12 }}>
              <CaseCard {...cases[activeIdx]} />
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
