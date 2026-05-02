import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { C, FONT_MONO } from './colors'

interface JdItem {
  n: number
  jdTitle: string
  jdSub: string
  evidence: readonly string[]
}

const HOOK_CHIPS: Record<number, string[]> = {
  1: ['메이플 16년 · 하드 세렌', '5장르 플레이', 'patchnote RAG 자체 구현'],
  2: ['cache 99%+', '2-tier 폴백', 'few-shot 5쌍'],
  3: ['158서버 × 9개월', 'Custom tool 3종', 'last_trace 기록'],
  4: ['Firestore 분석', '시각디자인 4년', '공모전 입상'],
}

export default function JdMatchAccordion({ items }: { items: readonly JdItem[] }) {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      {items.map((item) => {
        const isOpen = open === item.n
        const hooks = HOOK_CHIPS[item.n] ?? []
        return (
          <motion.article
            key={item.n}
            layout
            transition={{ layout: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } }}
            style={{
              background: C.bgWhite,
              borderRadius: 18,
              padding: '48px 56px',
              border: `1px solid ${isOpen ? C.nexonBlue : C.cardBorder}`,
              boxShadow: isOpen ? C.cardShadowHover : C.cardShadow,
              position: 'relative',
              overflow: 'hidden',
              transition: 'border 0.3s ease, box-shadow 0.3s ease',
            }}
          >
            {/* Top accent */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: 4,
                background: C.nexonBlue,
                opacity: isOpen ? 1 : 0.5,
                transition: 'opacity 0.3s ease',
              }}
            />

            {/* 좌우 분할 카드 내부 */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.5fr)',
                gap: 56,
                alignItems: 'start',
              }}
            >
              {/* 좌: 큰 번호 + 제목 */}
              <div>
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 'clamp(56px, 6vw, 88px)',
                    fontWeight: 800,
                    color: C.nexonBlue,
                    lineHeight: 1,
                    letterSpacing: '-0.05em',
                    marginBottom: 24,
                  }}
                >
                  {String(item.n).padStart(2, '0')}
                </div>
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 11,
                    color: C.inkMuted,
                    letterSpacing: '0.2em',
                    fontWeight: 700,
                    marginBottom: 20,
                  }}
                >
                  JD MATCH · {String(item.n).padStart(2, '0')}
                </div>
                <h3
                  style={{
                    fontSize: 'clamp(22px, 2.2vw, 30px)',
                    fontWeight: 800,
                    lineHeight: 1.25,
                    color: C.ink,
                    margin: 0,
                    letterSpacing: '-0.02em',
                    wordBreak: 'keep-all',
                  }}
                >
                  {item.jdTitle}
                </h3>
              </div>

              {/* 우: 부제 + 칩 + 토글 */}
              <div>
                <p
                  style={{
                    fontSize: 16,
                    color: C.inkSoft,
                    margin: '0 0 24px',
                    lineHeight: 1.65,
                    fontWeight: 600,
                  }}
                >
                  {item.jdSub}
                </p>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 24 }}>
                  {hooks.map((h) => (
                    <span
                      key={h}
                      style={{
                        fontFamily: FONT_MONO,
                        fontSize: 11,
                        fontWeight: 700,
                        color: C.nexonBlue,
                        background: 'rgba(0, 145, 204, 0.08)',
                        padding: '6px 10px',
                        borderRadius: 8,
                        letterSpacing: '0.02em',
                      }}
                    >
                      {h}
                    </span>
                  ))}
                </div>

                <button
                  onClick={() => setOpen(isOpen ? null : item.n)}
                  style={{
                    appearance: 'none',
                    border: `1px solid ${isOpen ? C.nexonBlue : 'rgba(0, 145, 204, 0.25)'}`,
                    background: isOpen ? C.nexonBlue : 'transparent',
                    color: isOpen ? C.inverse : C.nexonBlue,
                    padding: '10px 16px',
                    borderRadius: 999,
                    fontFamily: FONT_MONO,
                    fontSize: 12,
                    fontWeight: 700,
                    letterSpacing: '0.04em',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    transition: 'all 0.2s ease',
                  }}
                >
                  <span>{isOpen ? '접기' : `근거 ${item.evidence.length}건 보기`}</span>
                  <motion.span
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.25 }}
                    style={{ display: 'inline-flex' }}
                  >
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                      <path
                        d="M2 4L5 7L8 4"
                        stroke="currentColor"
                        strokeWidth="1.6"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </motion.span>
                </button>
              </div>
            </div>

            {/* Evidence reveal */}
            <AnimatePresence initial={false}>
              {isOpen && (
                <motion.div
                  key="evidence"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                  style={{ overflow: 'hidden' }}
                >
                  <ul
                    style={{
                      margin: '20px 0 0',
                      padding: '20px 0 0',
                      listStyle: 'none',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 12,
                      borderTop: `1px dashed rgba(0, 98, 223, 0.2)`,
                    }}
                  >
                    {item.evidence.map((e, i) => (
                      <motion.li
                        key={i}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.05 + i * 0.04, duration: 0.3 }}
                        style={{
                          fontSize: 14.5,
                          lineHeight: 1.65,
                          color: C.inkSoft,
                          paddingLeft: 26,
                          position: 'relative',
                          fontWeight: 700,
                        }}
                      >
                        <svg
                          style={{ position: 'absolute', left: 0, top: 4 }}
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke={C.nexonLightBlue}
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                        {e}
                      </motion.li>
                    ))}
                  </ul>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.article>
        )
      })}
    </div>
  )
}
