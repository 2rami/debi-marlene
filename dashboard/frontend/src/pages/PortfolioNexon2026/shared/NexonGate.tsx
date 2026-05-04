import { useRef } from 'react'
import { motion, useScroll, useTransform, type MotionValue } from 'framer-motion'
import { C, FONT_BODY, FONT_DISPLAY, GATE_COLORS } from './colors'

/**
 * CH 0 GATE + Hero 크로스페이드 (디졸브)
 *
 * 280vh 스크롤 영역:
 *   0–0.25  : NEXON 로고 facet 모임
 *   0.25–0.45: 로고 완성, 라벨 표시
 *   0.40–0.55: 로고 축소 + 블러 디졸브
 *   0.48–0.65: Hero 콘텐츠 크로스페이드인
 *   0.65–1.0 : Hero 유지 → unstick
 */
export default function NexonGate({
  children,
}: {
  children?: (progress: MotionValue<number>) => React.ReactNode
}) {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end start'],
  })

  // ── facet 등장 (0 → 0.25) ──
  const facetOpacity = useTransform(scrollYProgress, [0, 0.06, 0.22], [0, 0.4, 1])
  const blueX = useTransform(scrollYProgress, [0, 0.22], [-360, 0])
  const blueY = useTransform(scrollYProgress, [0, 0.22], [180, 0])
  const navyX = useTransform(scrollYProgress, [0, 0.22], [-60, 0])
  const navyY = useTransform(scrollYProgress, [0, 0.22], [-340, 0])
  const limeX = useTransform(scrollYProgress, [0, 0.22], [400, 0])
  const limeY = useTransform(scrollYProgress, [0, 0.22], [140, 0])

  // ── 로고 축소 + 디졸브 (0.25 → 0.55) ──
  const scale = useTransform(scrollYProgress, [0, 0.25, 0.55], [1, 1, 0.12])
  const logoOpacity = useTransform(scrollYProgress, [0.38, 0.52], [1, 0])
  // 디졸브 블러 효과: 사라지면서 흐려짐
  const logoBlur = useTransform(scrollYProgress, [0.38, 0.52], [0, 20])

  // ── 코너 라벨 ──
  const labelOpacity = useTransform(scrollYProgress, [0.15, 0.28, 0.38, 0.48], [0, 1, 1, 0])
  // ── 진입 힌트 ──
  const hintOpacity = useTransform(scrollYProgress, [0.22, 0.30, 0.36, 0.44], [0, 1, 1, 0])

  // ── children (Hero) 크로스페이드 (0.48 → 0.60) ──
  const childrenOpacity = useTransform(scrollYProgress, [0.48, 0.60], [0, 1])

  return (
    <section
      ref={ref}
      id="hero"
      style={{
        position: 'relative',
        height: '280vh',
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

        {/* 우상단 */}
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

        {/* 중앙 로고 — 축소 + 블러 디졸브 */}
        <motion.div style={{
          scale,
          opacity: logoOpacity,
          filter: useTransform(logoBlur, (v) => `blur(${v}px)`),
          willChange: 'transform, filter',
        }}>
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

            {/* NEXON 워드마크 */}
            <motion.g fill={GATE_COLORS.black} style={{ opacity: facetOpacity }}>
              <polygon points="193.73 414.2 145.75 414.2 145.75 402.01 193.73 402.01 193.73 388.45 145.75 388.45 145.75 377.56 193.73 377.56 193.73 364.07 128.74 364.07 128.74 427.67 193.73 427.67 193.73 414.2" />
              <polygon points="400.46 389.22 440.75 427.67 453.58 427.67 453.58 364.07 436.57 364.07 436.57 402.53 396.28 364.07 383.45 364.07 383.45 427.67 400.46 427.67 400.46 389.22" />
              <path d="M365.12,364.07h-70.14v63.59h70.14v-63.59ZM348.12,414.2h-36.12v-36.65h36.12v36.65Z" />
              <polygon points="57.28 389.22 97.58 427.67 110.41 427.67 110.41 364.07 93.4 364.07 93.4 402.53 53.1 364.07 40.26 364.07 40.26 427.67 57.28 427.67 57.28 389.22" />
              <polygon points="244.4 408.03 261.82 427.67 283.31 427.67 255.14 395.9 283.38 364.07 261.86 364.07 244.4 383.79 226.93 364.07 205.43 364.07 233.64 395.9 205.49 427.67 226.99 427.67 244.4 408.03" />
            </motion.g>
          </svg>
        </motion.div>

        {/* 진입 힌트 */}
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

        {/* ── Children (Hero) — 로고 디졸브 후 크로스페이드 ── */}
        {children && (
          <motion.div
            style={{
              opacity: childrenOpacity,
              position: 'absolute',
              inset: 0,
              zIndex: 10,
            }}
          >
            {children(scrollYProgress)}
          </motion.div>
        )}
      </div>
    </section>
  )
}
