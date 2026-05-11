import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { C, FONT_BODY, FONT_DISPLAY, GATE_COLORS, FONT_MONO } from './colors'
import Button from './Button'
import Aurora from '../../../components/common/Aurora'
import FloatingShapes from './FloatingShapes'
import { useRevealOff } from './useRevealOff'
import useIsMobile from './useIsMobile'

import { HERO, STATS } from '../content/llm'

/**
 * CH 0 — GATE → HERO
 *
 * 마운트 즉시 자동 재생. phase 3단계로 명확히 분리:
 *   - assemble (0 ~ 2.0s): facets 회전·스케일 풀리며 합체. blur 없음
 *   - hold     (2.0 ~ 3.0s): 완전 합체된 로고 정지. blur 없음
 *   - exit     (3.0 ~ 4.0s): scale 축소 + blur + fade out
 *
 * Hero content 는 hold 끝물부터 stagger 등장 (exit 과 살짝 겹침)
 *
 * ?reveal=off 이면 모든 단계 instant (Figma 캡처용).
 */

const ASSEMBLE_DUR = 2.0
const ASSEMBLE_EASE = [0.16, 1, 0.3, 1] as const
const HOLD_DUR = 1.0
const EXIT_DUR = 1.0
const HERO_DELAY = ASSEMBLE_DUR + HOLD_DUR - 0.1 // 2.9s — exit 직전부터 등장
const HERO_STAGGER = 0.12

type Phase = 'assemble' | 'hold' | 'exit'

export default function NexonGate() {
  const revealOff = useRevealOff()
  const isMobile = useIsMobile()
  const [phase, setPhase] = useState<Phase>(revealOff ? 'exit' : 'assemble')

  useEffect(() => {
    if (revealOff) return
    const toHold = window.setTimeout(() => setPhase('hold'), ASSEMBLE_DUR * 1000)
    const toExit = window.setTimeout(() => setPhase('exit'), (ASSEMBLE_DUR + HOLD_DUR) * 1000)
    return () => {
      window.clearTimeout(toHold)
      window.clearTimeout(toExit)
    }
  }, [revealOff])

  const T = revealOff ? 0 : 1

  return (
    <section
      id="hero"
      style={{
        position: 'relative',
        minHeight: '100vh',
        background: C.bgWhite,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'relative',
          minHeight: '100vh',
          height: isMobile ? 'auto' : '100vh',
          padding: isMobile ? '24px 0' : 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* 배경 */}
        <div style={{ position: 'absolute', inset: 0 }}>
          <div className="absolute inset-0 opacity-20 mix-blend-screen pointer-events-none">
            <Aurora colorStops={[C.nexonBlue, C.nexonLightBlue, C.nexonBlueAlt]} amplitude={0.9} speed={0.4} />
          </div>
          <div style={{ position: 'absolute', inset: 0, opacity: 0.3 }}>
            <FloatingShapes />
          </div>
        </div>

        {/* 로고 컨테이너 — phase 'exit' 일 때만 축소 + blur + fade */}
        <motion.div
          initial={{ scale: 1, opacity: 1, filter: 'blur(0px)' }}
          animate={
            phase === 'exit'
              ? { scale: 0.12, opacity: 0, filter: 'blur(14px)' }
              : { scale: 1, opacity: 1, filter: 'blur(0px)' }
          }
          transition={{
            duration: phase === 'exit' ? EXIT_DUR * T : 0,
            ease: ASSEMBLE_EASE,
          }}
          style={{ zIndex: 10, pointerEvents: 'none', position: 'absolute' }}
        >
          <svg viewBox="0 0 493.85 480.16" width={isMobile ? 'min(72vw, 320px)' : 'min(60vw, 540px)'}>
            <Facet
              fill={GATE_COLORS.blue}
              points="128.74 196.98 128.74 286.79 247.95 223.4"
              fromX={-460}
              fromY={260}
              fromRotate={-32}
              fromScale={1.6}
              T={T}
            />
            <Facet
              fill={GATE_COLORS.navy}
              points="247.95 52.49 128.74 115.88 128.74 196.98 247.95 223.4"
              fromX={-120}
              fromY={-420}
              fromRotate={28}
              fromScale={1.5}
              T={T}
            />
            <Facet
              fill={GATE_COLORS.lime}
              points="247.95 223.4 128.74 286.79 276.58 319.58 395.79 256.18"
              fromX={520}
              fromY={200}
              fromRotate={-22}
              fromScale={1.7}
              T={T}
            />
            {/* NEXON 글자 — 합체 후반에 페이드 */}
            <motion.g
              fill={GATE_COLORS.black}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.7 * T,
                delay: ASSEMBLE_DUR * 0.6 * T,
                ease: ASSEMBLE_EASE,
              }}
            >
              <polygon points="193.73 414.2 145.75 414.2 145.75 402.01 193.73 402.01 193.73 388.45 145.75 388.45 145.75 377.56 193.73 377.56 193.73 364.07 128.74 364.07 128.74 427.67 193.73 427.67 193.73 414.2" />
              <polygon points="400.46 389.22 440.75 427.67 453.58 427.67 453.58 364.07 436.57 364.07 436.57 402.53 396.28 364.07 383.45 364.07 383.45 427.67 400.46 427.67 400.46 389.22" />
              <path d="M365.12,364.07h-70.14v63.59h70.14v-63.59ZM348.12,414.2h-36.12v-36.65h36.12v36.65Z" />
              <polygon points="57.28 389.22 97.58 427.67 110.41 427.67 110.41 364.07 93.4 364.07 93.4 402.53 53.1 364.07 40.26 364.07 40.26 427.67 57.28 427.67 57.28 389.22" />
              <polygon points="244.4 408.03 261.82 427.67 283.31 427.67 255.14 395.9 283.38 364.07 261.86 364.07 244.4 383.79 226.93 364.07 205.43 364.07 233.64 395.9 205.49 427.67 226.99 427.67 244.4 408.03" />
            </motion.g>
          </svg>
        </motion.div>

        {/* Hero content */}
        <div
          style={{
            width: '100%',
            height: '100%',
            padding: isMobile ? '80px 22px 32px' : '60px clamp(48px, 8vw, 120px) 40px',
            display: 'flex',
            alignItems: 'center',
            position: 'relative',
            zIndex: 5,
          }}
        >
          <div
            style={{
              maxWidth: 1480,
              margin: '0 auto',
              display: 'grid',
              gridTemplateColumns: isMobile ? '1fr' : 'minmax(0, 1.6fr) minmax(280px, 1fr)',
              gap: isMobile ? 36 : 64,
              alignItems: 'start',
              width: '100%',
            }}
          >
            <div>
              <HeroIn delayIndex={0} fromX={-80} T={T}>
                <div
                  style={{
                    display: 'inline-block',
                    padding: '6px 14px',
                    color: C.nexonBlue,
                    border: `1px solid ${C.nexonBlue}`,
                    borderRadius: 9999,
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: '0.18em',
                    textTransform: 'uppercase',
                    marginBottom: 32,
                  }}
                >
                  {HERO.badge}
                </div>
              </HeroIn>

              <h1
                style={{
                  fontFamily: FONT_DISPLAY,
                  fontSize: 'clamp(36px, 5.5vw, 76px)',
                  fontWeight: 700,
                  lineHeight: 1.08,
                  letterSpacing: '-0.04em',
                  color: C.ink,
                  margin: '0 0 24px',
                  wordBreak: 'keep-all',
                }}
              >
                {HERO.titleLines.map((line, i) => {
                  const idx = line.indexOf(HERO.highlightWord)
                  const before = idx >= 0 ? line.slice(0, idx) : line
                  const after = idx >= 0 ? line.slice(idx + HERO.highlightWord.length) : ''
                  return (
                    <HeroIn key={i} delayIndex={1 + i} fromX={-80} T={T}>
                      <span style={{ display: 'block' }}>
                        {before}
                        {idx >= 0 && (
                          <span style={{ color: C.nexonBlue }}>{HERO.highlightWord}</span>
                        )}
                        {after}
                      </span>
                    </HeroIn>
                  )
                })}
              </h1>

              <HeroIn delayIndex={4} fromX={-80} T={T}>
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 28 }}>
                  {HERO.ctas.map((cta) => (
                    <Button
                      key={cta.label}
                      label={cta.label}
                      href={cta.href}
                      variant={cta.primary ? 'primary' : 'outline'}
                      external={cta.href.startsWith('http') || cta.href.endsWith('.pdf')}
                    />
                  ))}
                </div>
              </HeroIn>

              <HeroIn delayIndex={5} fromX={80} T={T}>
                <div
                  style={{
                    fontSize: 'clamp(15px, 1.3vw, 19px)',
                    fontWeight: 500,
                    lineHeight: 1.7,
                    color: C.inkSoft,
                    maxWidth: 720,
                    minHeight: '4em',
                    fontFamily: FONT_BODY,
                  }}
                >
                  {HERO.subtitle}
                </div>
              </HeroIn>
            </div>

            <HeroIn delayIndex={3} fromX={80} T={T}>
              <div style={{ padding: '32px 0 0', borderTop: `2px solid ${C.ink}` }}>
                <div style={{ fontFamily: FONT_MONO, fontSize: 10, letterSpacing: '0.2em', color: C.nexonBlue, fontWeight: 700, marginBottom: 24 }}>
                  INFO
                </div>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <tbody>
                    {HERO.meta.map((row) => (
                      <tr key={row.label} style={{ borderBottom: `1px solid ${C.cardBorder}` }}>
                        <td style={{ fontFamily: FONT_MONO, fontSize: 10.5, letterSpacing: '0.16em', color: C.inkMuted, fontWeight: 700, padding: '14px 0', width: 100, verticalAlign: 'top' }}>
                          {row.label}
                        </td>
                        <td style={{ fontSize: 14.5, color: C.ink, fontWeight: 600, padding: '14px 0', lineHeight: 1.45 }}>
                          {row.value}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <div style={{ marginTop: 32, paddingTop: 24, borderTop: `1px dashed ${C.cardBorder}`, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24 }}>
                  {STATS.map((s) => (
                    <div key={s.label}>
                      <div style={{ fontSize: 28, fontWeight: 800, lineHeight: 1, letterSpacing: '-0.025em', color: C.ink }}>
                        {s.value}
                        {s.unit && (
                          <span style={{ fontSize: '0.45em', fontWeight: 700, marginLeft: 3, color: C.inkMuted }}>
                            {s.unit}
                          </span>
                        )}
                      </div>
                      <div style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.inkMuted, letterSpacing: '0.08em', fontWeight: 700, marginTop: 6 }}>
                        {s.label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </HeroIn>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─────────────────────────────────────────────

function Facet({
  fill,
  points,
  fromX,
  fromY,
  fromRotate,
  fromScale,
  T,
}: {
  fill: string
  points: string
  fromX: number
  fromY: number
  fromRotate: number
  fromScale: number
  T: number
}) {
  return (
    <motion.g
      initial={{ x: fromX, y: fromY, rotate: fromRotate, scale: fromScale, opacity: 0 }}
      animate={{ x: 0, y: 0, rotate: 0, scale: 1, opacity: 1 }}
      transition={{ duration: ASSEMBLE_DUR * T, ease: ASSEMBLE_EASE }}
      style={{ transformOrigin: '247.95px 223.4px', transformBox: 'fill-box' as const }}
    >
      <polygon fill={fill} points={points} />
    </motion.g>
  )
}

function HeroIn({
  children,
  delayIndex,
  fromX,
  T,
}: {
  children: React.ReactNode
  delayIndex: number
  fromX: number
  T: number
}) {
  return (
    <motion.div
      initial={{ x: fromX, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{
        duration: 0.7 * T,
        delay: (HERO_DELAY + delayIndex * HERO_STAGGER) * T,
        ease: ASSEMBLE_EASE,
      }}
    >
      {children}
    </motion.div>
  )
}
