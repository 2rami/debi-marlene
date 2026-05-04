import { useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { C, FONT_BODY, FONT_DISPLAY, GATE_COLORS, FONT_MONO } from './colors'
import Button from './Button'
import Aurora from '../../../components/common/Aurora'
import FloatingShapes from './FloatingShapes'

// 원본 데이터
import { HERO, STATS } from '../content/llm'

export default function NexonGate() {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollY } = useScroll()

  // ── 1. 로고 합체 (0 ~ 1200px) ──
  const facetOpacity = useTransform(scrollY, [0, 300, 800], [0, 0.7, 1])
  const blueX = useTransform(scrollY, [0, 1000], [-400, 0])
  const blueY = useTransform(scrollY, [0, 1000], [200, 0])
  const navyX = useTransform(scrollY, [0, 1000], [-100, 0])
  const navyY = useTransform(scrollY, [0, 1000], [-350, 0])
  const limeX = useTransform(scrollY, [0, 1000], [450, 0])
  const limeY = useTransform(scrollY, [0, 1000], [150, 0])

  // ── 2. 로고 축소 및 퇴장 (1200 ~ 2200px) ──
  const logoScale = useTransform(scrollY, [1200, 2000], [1, 0.12])
  const logoOpacity = useTransform(scrollY, [1500, 2200], [1, 0])

  // ── 3. Hero 등장 (1300 ~ 2700px) ──
  // 등장 후 유지되다가 마지막에 퇴장(Fade-out) 하도록 구간 추가
  // 2900px부터 서서히 사라지기 시작해서 3300px에 완전 소멸
  const heroOpacity = useTransform(scrollY, [1400, 2400, 2900, 3300], [0, 1, 1, 0])
  
  const badgeOpacity = useTransform(scrollY, [1500, 1900, 2900, 3300], [0, 1, 1, 0])
  const badgeX = useTransform(scrollY, [1500, 1900], [-80, 0])
  
  const title1Opacity = useTransform(scrollY, [1600, 2000, 2900, 3300], [0, 1, 1, 0])
  const title1X = useTransform(scrollY, [1600, 2000], [-80, 0])
  
  const title2Opacity = useTransform(scrollY, [1700, 2100, 2900, 3300], [0, 1, 1, 0])
  const title2X = useTransform(scrollY, [1700, 2100], [-80, 0])
  
  const title3Opacity = useTransform(scrollY, [1800, 2200, 2900, 3300], [0, 1, 1, 0])
  const title3X = useTransform(scrollY, [1800, 2200], [-80, 0])
  
  const ctaOpacity = useTransform(scrollY, [1900, 2300, 2900, 3300], [0, 1, 1, 0])
  const ctaX = useTransform(scrollY, [1900, 2300], [-80, 0])
  
  const subtitleOpacity = useTransform(scrollY, [2000, 2500, 2900, 3300], [0, 1, 1, 0])
  const subtitleX = useTransform(scrollY, [2000, 2500], [80, 0])
  
  const infoOpacity = useTransform(scrollY, [1800, 2600, 2900, 3300], [0, 1, 1, 0])
  const infoX = useTransform(scrollY, [1800, 2600], [80, 0])

  const titleTransforms = [
    { opacity: title1Opacity, x: title1X },
    { opacity: title2Opacity, x: title2X },
    { opacity: title3Opacity, x: title3X },
  ]

  return (
    <section
      ref={ref}
      id="hero"
      style={{
        position: 'relative',
        height: '500vh', // 퇴장 구간 확보를 위해 전체 길이를 살짝 더 늘림
        background: C.bgWhite,
        zIndex: 10,
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
        {/* 오로라 배경 (마지막에 같이 사라짐) */}
        <motion.div style={{ opacity: heroOpacity, position: 'absolute', inset: 0 }}>
          <div className="absolute inset-0 opacity-20 mix-blend-screen pointer-events-none">
            <Aurora colorStops={[C.nexonBlue, C.nexonLightBlue, C.nexonBlueAlt]} amplitude={0.9} speed={0.4} />
          </div>
          <div style={{ position: 'absolute', inset: 0, opacity: 0.3 }}>
            <FloatingShapes />
          </div>
        </motion.div>

        {/* 로고 레이어 */}
        <motion.div style={{ scale: logoScale, opacity: logoOpacity, zIndex: 10, pointerEvents: 'none', position: 'absolute' }}>
          <svg viewBox="0 0 493.85 480.16" width="min(60vw, 540px)">
            <motion.g style={{ x: blueX, y: blueY, opacity: facetOpacity }}>
              <polygon fill={GATE_COLORS.blue} points="128.74 196.98 128.74 286.79 247.95 223.4" />
            </motion.g>
            <motion.g style={{ x: navyX, y: navyY, opacity: facetOpacity }}>
              <polygon fill={GATE_COLORS.navy} points="247.95 52.49 128.74 115.88 128.74 196.98 247.95 223.4" />
            </motion.g>
            <motion.g style={{ x: limeX, y: limeY, opacity: facetOpacity }}>
              <polygon fill={GATE_COLORS.lime} points="247.95 223.4 128.74 286.79 276.58 319.58 395.79 256.18" />
            </motion.g>
            <motion.g fill={GATE_COLORS.black} style={{ opacity: facetOpacity }}>
              <polygon points="193.73 414.2 145.75 414.2 145.75 402.01 193.73 402.01 193.73 388.45 145.75 388.45 145.75 377.56 193.73 377.56 193.73 364.07 128.74 364.07 128.74 427.67 193.73 427.67 193.73 414.2" />
              <polygon points="400.46 389.22 440.75 427.67 453.58 427.67 453.58 364.07 436.57 364.07 436.57 402.53 396.28 364.07 383.45 364.07 383.45 427.67 400.46 427.67 400.46 389.22" />
              <path d="M365.12,364.07h-70.14v63.59h70.14v-63.59ZM348.12,414.2h-36.12v-36.65h36.12v36.65Z" />
              <polygon points="57.28 389.22 97.58 427.67 110.41 427.67 110.41 364.07 93.4 364.07 93.4 402.53 53.1 364.07 40.26 364.07 40.26 427.67 57.28 427.67 57.28 389.22" />
              <polygon points="244.4 408.03 261.82 427.67 283.31 427.67 255.14 395.9 283.38 364.07 261.86 364.07 244.4 383.79 226.93 364.07 205.43 364.07 233.64 395.9 205.49 427.67 226.99 427.67 244.4 408.03" />
            </motion.g>
          </svg>
        </motion.div>

        <div
          style={{
            width: '100%',
            height: '100%',
            padding: '60px clamp(48px, 8vw, 120px) 40px',
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
              gridTemplateColumns: 'minmax(0, 1.6fr) minmax(280px, 1fr)',
              gap: 64,
              alignItems: 'start',
              width: '100%',
            }}
          >
            <div>
              <motion.div style={{ opacity: badgeOpacity, x: badgeX }}>
                <div style={{ display: 'inline-block', padding: '6px 14px', color: C.nexonBlue, border: `1px solid ${C.nexonBlue}`, borderRadius: 9999, fontSize: 11, fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase', marginBottom: 32 }}>
                  {HERO.badge}
                </div>
              </motion.div>

              <h1 style={{ fontFamily: FONT_DISPLAY, fontSize: 'clamp(36px, 5.5vw, 76px)', fontWeight: 700, lineHeight: 1.08, letterSpacing: '-0.04em', color: C.ink, margin: '0 0 24px', wordBreak: 'keep-all' }}>
                {HERO.titleLines.map((line, i) => {
                  const isHighlight = line.includes(HERO.highlightWord)
                  const t = titleTransforms[i] || titleTransforms[titleTransforms.length - 1]
                  return (
                    <motion.span key={i} style={{ display: 'block', opacity: t.opacity, x: t.x }}>
                      {isHighlight ? (
                        <>
                          <span style={{ color: C.nexonBlue }}>{HERO.highlightWord}</span>
                          {line.replace(HERO.highlightWord, '')}
                        </>
                      ) : (
                        line
                      )}
                    </motion.span>
                  )
                })}
              </h1>

              <motion.div style={{ opacity: ctaOpacity, x: ctaX, display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 28 }}>
                {HERO.ctas.map(cta => <Button key={cta.label} label={cta.label} href={cta.href} variant="outline" />)}
              </motion.div>
              
              <motion.div style={{ opacity: subtitleOpacity, x: subtitleX, fontSize: 'clamp(15px, 1.3vw, 19px)', fontWeight: 500, lineHeight: 1.7, color: C.inkSoft, maxWidth: 720, minHeight: '4em', fontFamily: FONT_BODY }}>
                {HERO.subtitle}
              </motion.div>
            </div>

            <motion.div style={{ opacity: infoOpacity, x: infoX }}>
              <div style={{ padding: '32px 0 0', borderTop: `2px solid ${C.ink}` }}>
                <div style={{ fontFamily: FONT_MONO, fontSize: 10, letterSpacing: '0.2em', color: C.nexonBlue, fontWeight: 700, marginBottom: 24 }}>INFO</div>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <tbody>
                    {HERO.meta.map(row => (
                      <tr key={row.label} style={{ borderBottom: `1px solid ${C.cardBorder}` }}>
                        <td style={{ fontFamily: FONT_MONO, fontSize: 10.5, letterSpacing: '0.16em', color: C.inkMuted, fontWeight: 700, padding: '14px 0', width: 100, verticalAlign: 'top' }}>{row.label}</td>
                        <td style={{ fontSize: 14.5, color: C.ink, fontWeight: 600, padding: '14px 0', lineHeight: 1.45 }}>{row.value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <div style={{ marginTop: 32, paddingTop: 24, borderTop: `1px dashed ${C.cardBorder}`, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24 }}>
                  {STATS.map((s) => (
                    <div key={s.label}>
                      <div style={{ fontSize: 28, fontWeight: 800, lineHeight: 1, letterSpacing: '-0.025em', color: C.ink }}>
                        {s.value}
                        {s.unit && <span style={{ fontSize: '0.45em', fontWeight: 700, marginLeft: 3, color: C.inkMuted }}>{s.unit}</span>}
                      </div>
                      <div style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.inkMuted, letterSpacing: '0.08em', fontWeight: 700, marginTop: 6 }}>
                        {s.label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
}
