/**
 * 넥슨네트웍스 · 게임서비스 채용연계형 인턴 — 자회사
 * 라우트: /portfolio/nexon/service
 *
 * 페이지 구조 (게임서비스 공고 순서)
 *   Hero
 *   01 ABOUT
 *   02 STATS
 *   03 주요 업무 매칭 (JD Match × 5)
 *   04 지원 자격 (메이플 헤비유저 + CharacterBox)
 *   05 우대 사항 (PREFERRED × 3 + Cases)
 *   Footer
 */

import { useEffect, useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import Lenis from 'lenis'
import GradientText from '../../components/common/GradientText'
import { C, FONT_BODY, FONT_MONO } from './shared/colors'
import FloatingShapes from './shared/FloatingShapes'
import StatGrid from './shared/StatGrid'
import JdMatchCard from './shared/JdMatchCard'
import CaseCard from './shared/CaseCard'
import CharacterBox from './shared/CharacterBox'
import Footer from './shared/Footer'
import {
  HERO,
  STATS,
  ABOUT,
  JD_MATCHES,
  CHARACTER,
  CASES,
  CONTACT,
  PREFERRED,
  ELIGIBILITY,
} from './content/service'

// ─────────────────────────────────────────────
// 공통 모션 wrapper
// ─────────────────────────────────────────────

function FadeIn({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.05 }}
      transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}

function SectionHeader({
  no,
  kicker,
  title,
  dark = false,
}: {
  no: string
  kicker: string
  title: string
  dark?: boolean
}) {
  return (
    <FadeIn>
      <div style={{ marginBottom: 56 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 24 }}>
          <span style={{ fontFamily: FONT_MONO, fontSize: 11, fontWeight: 700, color: C.honey, letterSpacing: '0.18em' }}>
            {no}
          </span>
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              fontWeight: 600,
              color: dark ? 'rgba(245, 250, 249, 0.7)' : C.inkMuted,
              letterSpacing: '0.18em',
            }}
          >
            {kicker}
          </span>
          <span
            style={{
              flex: 1,
              height: 1,
              background: dark ? 'rgba(245, 250, 249, 0.25)' : 'rgba(26, 43, 71, 0.12)',
            }}
          />
        </div>
        <h2
          style={{
            fontSize: 'clamp(32px, 4.4vw, 52px)',
            fontWeight: 800,
            lineHeight: 1.2,
            letterSpacing: '-0.025em',
            color: dark ? C.inverse : C.ink,
            margin: 0,
            whiteSpace: 'pre-line',
          }}
        >
          {title}
        </h2>
      </div>
    </FadeIn>
  )
}

// ─────────────────────────────────────────────
// Hero
// ─────────────────────────────────────────────

function Hero() {
  const heroRef = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '20%'])
  const shapesY = useTransform(scrollYProgress, [0, 1], ['0%', '8%'])

  return (
    <section
      ref={heroRef}
      style={{
        position: 'relative',
        minHeight: '100vh',
        padding: '64px 48px',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 80,
          left: '8%',
          width: 600,
          height: 600,
          borderRadius: '50%',
          filter: 'blur(150px)',
          background: 'rgba(215, 232, 74, 0.18)',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: 200,
          right: '8%',
          width: 520,
          height: 520,
          borderRadius: '50%',
          filter: 'blur(150px)',
          background: 'rgba(232, 185, 72, 0.22)',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />

      <motion.div style={{ y: shapesY, position: 'absolute', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
        <FloatingShapes />
      </motion.div>

      <header
        style={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          maxWidth: 1280,
          margin: '0 auto',
          paddingBottom: 24,
          borderBottom: `1px solid rgba(245, 250, 249, 0.25)`,
          color: C.inverse,
          flexWrap: 'wrap',
          gap: 16,
        }}
      >
        <span style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: '0.12em', opacity: 0.85 }}>
          PORTFOLIO · {HERO.jobCode}
        </span>
        <span style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: '0.08em', opacity: 0.85 }}>
          YANG · GEONHO / 2026
        </span>
      </header>

      <motion.div
        style={{
          y: textY,
          maxWidth: 1280,
          margin: '0 auto',
          position: 'relative',
          zIndex: 1,
          paddingTop: 96,
          paddingBottom: 64,
        }}
      >
        <FadeIn delay={0}>
          <div
            style={{
              display: 'inline-block',
              padding: '8px 18px',
              background: C.lime,
              color: C.ink,
              fontFamily: FONT_MONO,
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              borderRadius: 9999,
              marginBottom: 32,
            }}
          >
            {HERO.badge}
          </div>
        </FadeIn>

        <FadeIn delay={0.08}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 32 }}>
            <span style={{ fontFamily: FONT_MONO, fontSize: 13, color: C.honey, letterSpacing: '0.05em' }}>
              {HERO.jobCode} — 양건호
            </span>
            <span style={{ flex: 1, height: 1, background: 'rgba(245, 250, 249, 0.3)' }} />
          </div>
        </FadeIn>

        <FadeIn delay={0.15}>
          <GradientText
            colors={[C.lime, C.honey, C.inverse, C.lime]}
            animationSpeed={6}
            className="!mx-0"
          >
            <h1
              style={{
                fontSize: 'clamp(44px, 8vw, 88px)',
                fontWeight: 900,
                lineHeight: 1.05,
                letterSpacing: '-0.03em',
                margin: 0,
                whiteSpace: 'pre-line',
              }}
            >
              {HERO.title}
            </h1>
          </GradientText>
        </FadeIn>

        <FadeIn delay={0.22}>
          <p
            style={{
              fontSize: 'clamp(17px, 2vw, 22px)',
              fontWeight: 500,
              lineHeight: 1.7,
              color: 'rgba(245, 250, 249, 0.92)',
              maxWidth: 760,
              margin: '32px 0 56px',
            }}
          >
            {HERO.subtitle}
          </p>
        </FadeIn>

        <FadeIn delay={0.3}>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {HERO.ctas.map((cta) => (
              <a
                key={cta.label}
                href={cta.href}
                target={cta.href.startsWith('http') ? '_blank' : undefined}
                rel={cta.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '14px 26px',
                  fontSize: 16,
                  fontWeight: 700,
                  borderRadius: 9999,
                  textDecoration: 'none',
                  transition: 'all 220ms cubic-bezier(0.4, 0, 0.2, 1)',
                  ...(cta.primary
                    ? {
                        background: C.inverse,
                        color: C.ink,
                        border: `1.5px solid ${C.inverse}`,
                      }
                    : {
                        background: 'rgba(245, 250, 249, 0.06)',
                        color: C.inverse,
                        border: '1.5px solid rgba(245, 250, 249, 0.45)',
                        backdropFilter: 'blur(8px)',
                      }),
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)'
                  e.currentTarget.style.boxShadow = '0 8px 28px rgba(26, 43, 71, 0.2)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                {cta.label}
              </a>
            ))}
          </div>
        </FadeIn>

        <FadeIn delay={0.4}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: 12,
              marginTop: 64,
              maxWidth: 880,
            }}
          >
            {STATS.map((s, i) => (
              <div
                key={s.label}
                style={{
                  padding: '18px 20px',
                  borderRadius: 18,
                  background: 'rgba(245, 250, 249, 0.07)',
                  border: '1px solid rgba(245, 250, 249, 0.18)',
                  backdropFilter: 'blur(12px)',
                }}
              >
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 10,
                    color: C.honey,
                    letterSpacing: '0.12em',
                    fontWeight: 700,
                    marginBottom: 6,
                  }}
                >
                  {String(i + 1).padStart(2, '0')}
                </div>
                <div
                  style={{
                    fontSize: 28,
                    fontWeight: 800,
                    color: C.inverse,
                    lineHeight: 1,
                    fontVariantNumeric: 'tabular-nums',
                    letterSpacing: '-0.02em',
                  }}
                >
                  {s.value}
                  {s.unit && (
                    <span style={{ fontSize: '0.5em', fontWeight: 700, marginLeft: 4, opacity: 0.85 }}>{s.unit}</span>
                  )}
                </div>
                <div style={{ fontSize: 12, color: 'rgba(245, 250, 249, 0.78)', marginTop: 6, fontWeight: 600 }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </FadeIn>
      </motion.div>
    </section>
  )
}

// ─────────────────────────────────────────────
// 페이지
// ─────────────────────────────────────────────

export default function PageService() {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 0.6,
      wheelMultiplier: 0.9,
      easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    })
    ;(window as any).__lenis = lenis
    lenis.scrollTo(0, { immediate: true })
    function raf(time: number) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }
    requestAnimationFrame(raf)
    return () => {
      lenis.destroy()
      ;(window as any).__lenis = null
    }
  }, [])

  return (
    <div
      style={{
        fontFamily: FONT_BODY,
        color: C.ink,
        letterSpacing: '-0.01em',
        background: `linear-gradient(180deg, ${C.bgDeep} 0%, ${C.bgMid} 30%, ${C.bgLight} 100%)`,
        minHeight: '100vh',
        overflowX: 'clip',
      }}
    >
      <Hero />

      {/* 01. ABOUT */}
      <section
        id="about"
        style={{
          padding: '96px 48px',
          background: C.inverse,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader no="01" kicker="ABOUT" title="저는 이런 사람입니다" />
          <FadeIn delay={0.05}>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 5fr) minmax(0, 7fr)',
                gap: 64,
                alignItems: 'start',
              }}
            >
              <p
                style={{
                  fontSize: 22,
                  fontWeight: 700,
                  lineHeight: 1.5,
                  color: C.ink,
                  margin: 0,
                  letterSpacing: '-0.015em',
                }}
              >
                메이플 헤비유저의 사용자 시점과<br />
                1인 봇 운영자의 라이브 서비스 시점이<br />
                <span style={{ color: C.bgDeep }}>결합된 자리에서 게임서비스를 합니다.</span>
              </p>
              <p style={{ fontSize: 16, lineHeight: 1.85, color: C.inkSoft, margin: 0 }}>{ABOUT}</p>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* 02. STATS */}
      <section
        style={{
          padding: '96px 48px',
          background: '#F4F8FA',
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="02"
            kicker="STATS · 정량 지표"
            title={`라이브 서비스 운영을\n증명하는 4가지 숫자`}
          />
          <FadeIn delay={0.05}>
            <StatGrid stats={STATS} />
          </FadeIn>
        </div>
      </section>

      {/* 03. 주요 업무 매칭 */}
      <section
        style={{
          padding: '120px 48px',
          background: C.inverse,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="03"
            kicker="JOB DESCRIPTION · 주요 업무"
            title={`공고 5가지 주요 업무에\n대한 1:1 매칭 근거`}
          />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24 }}>
            {JD_MATCHES.map((m, i) => (
              <FadeIn key={m.n} delay={i * 0.06}>
                <JdMatchCard n={m.n} jdTitle={m.jdTitle} jdSub={m.jdSub} evidence={m.evidence} />
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* 04. 지원 자격 */}
      <section
        style={{
          padding: '120px 48px',
          background: '#F4F8FA',
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="04"
            kicker="ELIGIBILITY · 지원 자격"
            title={ELIGIBILITY.headline}
          />

          <FadeIn delay={0.05}>
            <div
              style={{
                background: `linear-gradient(135deg, ${C.bgDeep} 0%, ${C.bgMid} 100%)`,
                borderRadius: 24,
                padding: '40px 48px',
                color: C.inverse,
                marginBottom: 32,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  right: -80,
                  top: -80,
                  width: 280,
                  height: 280,
                  borderRadius: '50%',
                  background: `${C.lime}40`,
                  filter: 'blur(80px)',
                }}
              />
              <div
                style={{
                  position: 'relative',
                  display: 'grid',
                  gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 2fr)',
                  gap: 48,
                  alignItems: 'center',
                }}
              >
                <div>
                  <div
                    style={{
                      fontFamily: FONT_MONO,
                      fontSize: 11,
                      letterSpacing: '0.15em',
                      color: C.lime,
                      fontWeight: 700,
                      marginBottom: 12,
                    }}
                  >
                    HEAVY USER · 10년 7개월
                  </div>
                  <div style={{ fontSize: 36, fontWeight: 800, lineHeight: 1.15, letterSpacing: '-0.02em' }}>
                    메이플스토리<br />
                    <span style={{ color: C.lime }}>284 LV</span>
                  </div>
                </div>
                <div style={{ fontSize: 16, lineHeight: 1.8, color: 'rgba(245, 250, 249, 0.92)' }}>
                  {ELIGIBILITY.body}
                </div>
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={0.12}>
            <CharacterBox character={CHARACTER} />
          </FadeIn>
        </div>
      </section>

      {/* 05. 우대 사항 */}
      <section
        style={{
          padding: '120px 48px',
          background: C.inverse,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="05"
            kicker="PREFERRED · 우대 사항"
            title={`데이터 분석 · 다양한 AI 도구\n· 외국어`}
          />

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: 20,
              marginBottom: 48,
            }}
          >
            {PREFERRED.map((p, i) => (
              <FadeIn key={p.n} delay={i * 0.06}>
                <article
                  style={{
                    background: '#F4F8FA',
                    borderRadius: 18,
                    padding: 28,
                    border: '1px solid rgba(26, 43, 71, 0.06)',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 18,
                  }}
                >
                  <header style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: 32,
                        height: 32,
                        borderRadius: 9999,
                        background: C.lime,
                        color: C.ink,
                        fontFamily: FONT_MONO,
                        fontSize: 13,
                        fontWeight: 800,
                      }}
                    >
                      {String(p.n).padStart(2, '0')}
                    </span>
                    <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em' }}>
                      PREFERRED
                    </span>
                  </header>
                  <h3
                    style={{
                      fontSize: 18,
                      fontWeight: 700,
                      lineHeight: 1.4,
                      color: C.ink,
                      margin: 0,
                      letterSpacing: '-0.01em',
                    }}
                  >
                    {p.jdTitle}
                  </h3>
                  <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {p.evidence.map((e, idx) => (
                      <li
                        key={idx}
                        style={{
                          fontSize: 14,
                          lineHeight: 1.65,
                          color: C.inkSoft,
                          paddingLeft: 18,
                          position: 'relative',
                        }}
                      >
                        <span
                          style={{
                            position: 'absolute',
                            left: 0,
                            top: 9,
                            width: 6,
                            height: 6,
                            borderRadius: '50%',
                            background: C.honey,
                          }}
                        />
                        {e}
                      </li>
                    ))}
                  </ul>
                </article>
              </FadeIn>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24 }}>
            {CASES.map((c, i) => (
              <FadeIn key={c.no} delay={i * 0.06}>
                <CaseCard
                  no={c.no}
                  title={c.title}
                  problem={c.problem}
                  approach={c.approach}
                  result={c.result}
                  bridge={c.bridge}
                />
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      <Footer email={CONTACT.email} github={CONTACT.github} domain={CONTACT.domain} edu={CONTACT.edu} />
    </div>
  )
}
