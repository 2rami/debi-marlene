import { useState, useEffect, useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { C, FONT_MONO } from './colors'
import FloatingShapes from './FloatingShapes'

function Typewriter({ text, delay = 0, speed = 50 }: { text: string, delay?: number, speed?: number }) {
  const [displayed, setDisplayed] = useState('')
  
  useEffect(() => {
    let i = 0
    let timeout: ReturnType<typeof setTimeout>
    const startTimeout = setTimeout(() => {
      const type = () => {
        if (i < text.length) {
          setDisplayed(text.slice(0, i + 1))
          i++
          timeout = setTimeout(type, speed)
        }
      }
      type()
    }, delay)
    return () => {
      clearTimeout(startTimeout)
      clearTimeout(timeout)
    }
  }, [text, delay, speed])

  return <>{displayed}</>
}

interface HeroProps {
  badge: string
  jobCode: string  // 직무 코드 (LLM EVALUATOR / GAME SERVICE / GAME QA)
  title: string  // 두 줄 가능 (\n)
  subtitle: string
  ctas: { label: string; href: string; primary?: boolean }[]
}

export default function Hero({ badge, jobCode, title, subtitle, ctas }: HeroProps) {
  const { scrollY } = useScroll()
  
  // 0px ~ 400px 스크롤할 때 투명도는 1 -> 0, Y위치는 0 -> -50px 로 이동 (퇴장 애니메이션)
  const opacity = useTransform(scrollY, [0, 400], [1, 0])
  const y = useTransform(scrollY, [0, 400], [0, -50])

  return (
    <motion.section
      style={{
        position: 'relative',
        minHeight: '80vh',
        padding: '32px 48px',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        opacity,
        y,
      }}
    >
      <FloatingShapes />

      {/* 매거진 헤더 (Smilegate 패턴 차용) */}
      <header
        style={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          maxWidth: 1200,
          margin: '0 auto',
          paddingBottom: 24,
          borderBottom: `1px solid rgba(245, 250, 249, 0.3)`,
          color: C.inverse,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
          <span style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: '0.08em', opacity: 0.85 }}>
            PORTFOLIO · {jobCode}
          </span>
        </div>
        <span style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: '0.05em', opacity: 0.85 }}>
          YANG · GEONHO / 2026
        </span>
      </header>

      {/* 본 컨텐츠 */}
      <div
        style={{
          maxWidth: 1200,
          margin: 'auto',
          position: 'relative',
          zIndex: 1,
          paddingTop: 40,
          paddingBottom: 20,
          width: '100%',
        }}
      >
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
          style={{
            display: 'inline-block',
            padding: '6px 14px',
            background: C.lime,
            color: C.ink,
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            borderRadius: 9999,
            marginBottom: 20,
          }}
        >
          {badge}
        </motion.div>

        {/* No 표기 + 본명 */}
        <motion.div 
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 0.2 }}
          style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 20 }}
        >
          <span style={{ fontFamily: FONT_MONO, fontSize: 13, color: C.nexonBlue, letterSpacing: '0.05em' }}>
            {jobCode} — 양건호
          </span>
          <span style={{ flex: 1, height: 1, background: 'rgba(245, 250, 249, 0.3)' }} />
        </motion.div>

        {/* Title */}
        <h1
          style={{
            fontSize: 'clamp(28px, 5.5vw, 64px)',
            fontWeight: 800,
            lineHeight: 1.15,
            letterSpacing: '-0.02em',
            color: C.inverse,
            margin: 0,
            marginBottom: 28,
            whiteSpace: 'pre-line',
            textShadow: '0 2px 16px rgba(26, 43, 71, 0.2)',
            minHeight: '2.3em', // 타이핑 도중 높이 유지
          }}
        >
          <Typewriter text={title} delay={300} speed={40} />
        </h1>

        {/* CTAs */}
        <motion.div 
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 1.2 }}
          style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 36 }}
        >
          {ctas.map((cta) => (
            <a
              key={cta.label}
              href={cta.href}
              target={cta.href.startsWith('http') ? '_blank' : undefined}
              rel={cta.href.startsWith('http') ? 'noopener noreferrer' : undefined}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '12px 20px',
                fontSize: 15,
                fontWeight: 600,
                borderRadius: 9999,
                textDecoration: 'none',
                transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
                ...(cta.primary
                  ? {
                      background: C.inverse,
                      color: C.ink,
                      border: `1.5px solid ${C.inverse}`,
                    }
                  : {
                      background: 'transparent',
                      color: C.inverse,
                      border: '1.5px solid rgba(245, 250, 249, 0.7)',
                    }),
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 4px 24px rgba(26, 43, 71, 0.15)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              {cta.label}
            </a>
          ))}
        </motion.div>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 1.6 }} // 타이핑 끝날 즈음 등장
          style={{
            fontSize: 'clamp(16px, 2vw, 20px)',
            fontWeight: 500,
            lineHeight: 1.7,
            color: 'rgba(245, 250, 249, 0.92)',
            maxWidth: 720,
            margin: 0,
            marginBottom: 20,
          }}
        >
          {subtitle}
        </motion.p>
      </div>
    </motion.section>
  )
}
