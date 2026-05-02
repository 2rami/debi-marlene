import { useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { C, FONT_BODY, FONT_DISPLAY, GATE_COLORS } from './colors'

/**
 * CH 0 GATE.
 *
 * NEXON CI 로고를 4개 polygon 으로 분해해 scroll 진행에 따라 facet 별로
 * 흩어지며 페이지 본문으로 빨려 들어가는 진입 모션.
 * 라임/네이비/블루 facet 은 본 컴포넌트에서만 사용 (페이지 본문은 nexonBlue 1 색).
 */
export default function NexonGate() {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end start'],
  })

  // Phase A (0 → 0.35): 흩어진 facet 들이 중앙으로 모이며 등장
  // Phase B (0.45 → 1.0): 합쳐진 로고가 작아지며 페이드 아웃
  const facetOpacity = useTransform(scrollYProgress, [0, 0.1, 0.35], [0, 0.4, 1])
  const scale = useTransform(scrollYProgress, [0, 0.35, 1], [1, 1, 0.28])
  const logoOpacity = useTransform(scrollYProgress, [0.7, 1], [1, 0])

  // facet 별 진입 — 멀리서 중앙으로
  const blueX = useTransform(scrollYProgress, [0, 0.35], [-360, 0])
  const blueY = useTransform(scrollYProgress, [0, 0.35], [180, 0])
  const navyX = useTransform(scrollYProgress, [0, 0.35], [-60, 0])
  const navyY = useTransform(scrollYProgress, [0, 0.35], [-340, 0])
  const limeX = useTransform(scrollYProgress, [0, 0.35], [400, 0])
  const limeY = useTransform(scrollYProgress, [0, 0.35], [140, 0])

  // 코너 라벨 — 합쳐지기 시작하면 등장, 작아질 때 사라짐
  const labelOpacity = useTransform(scrollYProgress, [0.2, 0.4, 0.7, 0.9], [0, 1, 1, 0])
  // 진입 힌트 — 로고가 모인 직후 잠깐
  const hintOpacity = useTransform(scrollYProgress, [0.35, 0.45, 0.6, 0.7], [0, 1, 1, 0])

  return (
    <section
      ref={ref}
      id="hero"
      style={{
        position: 'relative',
        height: '180vh',
        background: C.bgWhite,
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
        {/* 좌상단: CH 번호 */}
        <motion.div
          style={{
            opacity: labelOpacity,
            position: 'absolute',
            top: 'clamp(80px, 9vh, 120px)',
            left: 'clamp(40px, 6vw, 120px)',
            display: 'flex',
            alignItems: 'baseline',
            gap: 14,
          }}
        >
          <span
            style={{
              fontFamily: FONT_BODY,
              fontSize: 11,
              letterSpacing: '0.24em',
              fontWeight: 800,
              color: C.nexonBlue,
            }}
          >
            CH 0 / 4
          </span>
          <span
            style={{
              fontFamily: FONT_BODY,
              fontSize: 11,
              letterSpacing: '0.24em',
              fontWeight: 800,
              color: C.inkMuted,
            }}
          >
            GATE.
          </span>
        </motion.div>

        {/* 우상단: 호 */}
        <motion.div
          style={{
            opacity: labelOpacity,
            position: 'absolute',
            top: 'clamp(80px, 9vh, 120px)',
            right: 'clamp(40px, 6vw, 120px)',
            textAlign: 'right',
            fontFamily: FONT_BODY,
          }}
        >
          <div style={{ fontSize: 11, fontWeight: 800, color: C.inkMuted, letterSpacing: '0.24em' }}>
            ISSUE / 2026.05
          </div>
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              color: C.inkMuted,
              letterSpacing: '0.24em',
              marginTop: 4,
            }}
          >
            YANG GEONHO · 9802
          </div>
        </motion.div>

        {/* 중앙 로고 — facet 흩어진 상태에서 합쳐졌다가 작아짐 */}
        <motion.div style={{ scale, opacity: logoOpacity, willChange: 'transform' }}>
          <svg
            viewBox="0 0 493.85 480.16"
            width="min(60vw, 540px)"
            height="auto"
            aria-label="NEXON"
            style={{ display: 'block' }}
          >
            <motion.g style={{ x: blueX, y: blueY, opacity: facetOpacity }}>
              <polygon
                fill={GATE_COLORS.blue}
                points="128.74 196.98 128.74 286.79 247.95 223.4"
              />
            </motion.g>
            <motion.g style={{ x: navyX, y: navyY, opacity: facetOpacity }}>
              <polygon
                fill={GATE_COLORS.navy}
                points="247.95 52.49 128.74 115.88 128.74 196.98 247.95 223.4"
              />
            </motion.g>
            <motion.g style={{ x: limeX, y: limeY, opacity: facetOpacity }}>
              <polygon
                fill={GATE_COLORS.lime}
                points="247.95 223.4 128.74 286.79 276.58 319.58 395.79 256.18"
              />
            </motion.g>

            {/* NEXON 워드마크 — facet 합쳐질 때 함께 등장 */}
            <motion.g fill={GATE_COLORS.black} style={{ opacity: facetOpacity }}>
              <polygon points="193.73 414.2 145.75 414.2 145.75 402.01 193.73 402.01 193.73 388.45 145.75 388.45 145.75 377.56 193.73 377.56 193.73 364.07 128.74 364.07 128.74 427.67 193.73 427.67 193.73 414.2" />
              <polygon points="400.46 389.22 440.75 427.67 453.58 427.67 453.58 364.07 436.57 364.07 436.57 402.53 396.28 364.07 383.45 364.07 383.45 427.67 400.46 427.67 400.46 389.22" />
              <path d="M365.12,364.07h-70.14v63.59h70.14v-63.59ZM348.12,414.2h-36.12v-36.65h36.12v36.65Z" />
              <polygon points="57.28 389.22 97.58 427.67 110.41 427.67 110.41 364.07 93.4 364.07 93.4 402.53 53.1 364.07 40.26 364.07 40.26 427.67 57.28 427.67 57.28 389.22" />
              <polygon points="244.4 408.03 261.82 427.67 283.31 427.67 255.14 395.9 283.38 364.07 261.86 364.07 244.4 383.79 226.93 364.07 205.43 364.07 233.64 395.9 205.49 427.67 226.99 427.67 244.4 408.03" />
            </motion.g>
          </svg>
        </motion.div>

        {/* 진입 힌트 — 살짝 떴다 사라짐 */}
        <motion.div
          style={{
            opacity: hintOpacity,
            position: 'absolute',
            bottom: 'clamp(40px, 7vh, 96px)',
            left: '50%',
            transform: 'translateX(-50%)',
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(12px, 1vw, 14px)',
            fontWeight: 700,
            letterSpacing: '0.4em',
            color: C.ink,
            textTransform: 'uppercase',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 18,
          }}
        >
          <span>ENTER</span>
          <motion.span
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 1.6, repeat: Infinity, ease: 'easeInOut' }}
            style={{
              width: 1,
              height: 56,
              background: `linear-gradient(180deg, ${C.ink}, transparent)`,
              display: 'block',
            }}
          />
        </motion.div>
      </div>
    </section>
  )
}
