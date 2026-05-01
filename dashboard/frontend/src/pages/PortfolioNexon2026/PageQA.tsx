/**
 * 게임 QA — 채용연계형 인턴 (넥슨네트웍스) 지원용 포트폴리오
 * 라우트: /portfolio/nexon/qa
 *
 * 페이지 구조 (공고 순서)
 *   Hero
 *   01 ABOUT
 *   02 주요 업무 매칭 (JD Match × 5)
 *   03 지원 자격 (게임 헤비유저 + 5장르 + 협업 / 기획서 / 결함 학습 / 기록 공유)
 *   04 우대 사항 (자동화 도구 + CS·SW 인접 + 5년 비전 + 운영 트러블슈팅 케이스 6건)
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
import GameList from './shared/GameList'
import Footer from './shared/Footer'
import {
  HERO,
  STATS,
  ABOUT,
  JD_MATCHES,
  ELIGIBILITY_TRAITS,
  PREFERRED,
  CHARACTER,
  GAMES,
  CASES,
  CONTACT,
} from './content/qa'

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

function SectionHeader({ no, kicker, title, dark = false }: { no: string; kicker: string; title: string; dark?: boolean }) {
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
      {/* 그라디언트 BG 블롭 */}
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

      {/* 매거진 헤더 */}
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

        {/* 타이틀: GradientText + 큰 산세리프 */}
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

        {/* Hero 하단 정량 4개 */}
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

export default function PageQA() {
  // Lenis smooth scroll
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
                헤비유저로서의 게임 도메인 깊이와<br />
                봇 운영자로서의 결함 추적 습관이 결합된<br />
                <span style={{ color: C.bgDeep }}>지점이 게임 QA 직무의 본질입니다.</span>
              </p>
              <p style={{ fontSize: 16, lineHeight: 1.85, color: C.inkSoft, margin: 0 }}>
                {ABOUT}
              </p>
            </div>
          </FadeIn>

          <FadeIn delay={0.15}>
            <div style={{ marginTop: 64 }}>
              <StatGrid stats={STATS} />
            </div>
          </FadeIn>
        </div>
      </section>

      {/* 02. 주요 업무 매칭 */}
      <section
        style={{
          padding: '120px 48px',
          background: '#F4F8FA',
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="02"
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

      {/* 03. 지원 자격 */}
      <section
        style={{
          padding: '120px 48px',
          background: C.inverse,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="03"
            kicker="ELIGIBILITY · 지원 자격"
            title={`게임을 끝까지 파고드는\n사용자 시점과 협업 훈련`}
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
              <div style={{ position: 'relative', display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 2fr)', gap: 48, alignItems: 'center' }}>
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
                  2014년 10월부터 약 10년 7개월간 메이플스토리를 플레이하며,
                  검은 마법사 라이프타임 보스와 그란디스 어센틱 지역까지
                  거의 모든 라이프타임 콘텐츠를 직접 거쳤습니다.
                  단순 만렙이 아니라 직업 시스템·메타·재화 흐름까지 사용자 입장에서 종합적으로 이해하며,
                  라이트 유저가 절대 못 밟는 엣지 케이스를 일상적으로 밟습니다.
                </div>
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={0.12}>
            <CharacterBox character={CHARACTER} />
          </FadeIn>

          {/* 5장르 게임 리스트 (콘텐츠·플랫폼 이해도) */}
          <FadeIn delay={0.18}>
            <div
              style={{
                background: '#F4F8FA',
                borderRadius: 20,
                padding: 32,
                marginTop: 32,
              }}
            >
              <div
                style={{
                  fontFamily: FONT_MONO,
                  fontSize: 11,
                  letterSpacing: '0.15em',
                  color: C.honey,
                  fontWeight: 700,
                  marginBottom: 8,
                }}
              >
                ELIGIBILITY · 콘텐츠 · 플랫폼 이해도
              </div>
              <h3
                style={{
                  fontSize: 22,
                  fontWeight: 700,
                  color: C.ink,
                  margin: '0 0 24px',
                  letterSpacing: '-0.01em',
                }}
              >
                MMORPG · MOBA · 어드벤처 · FPS · 수집형 — 5종 5장르
              </h3>
              <GameList games={GAMES} />
            </div>
          </FadeIn>

          {/* 자격 요건 4축 (협업 / 기획서 / 결함 학습 / 기록 공유) */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: 20,
              marginTop: 32,
            }}
          >
            {ELIGIBILITY_TRAITS.map((t, i) => (
              <FadeIn key={t.label} delay={0.05 + i * 0.05}>
                <div
                  style={{
                    background: '#F4F8FA',
                    borderRadius: 16,
                    padding: 24,
                    border: '1px solid rgba(26, 43, 71, 0.06)',
                    height: '100%',
                  }}
                >
                  <div
                    style={{
                      fontFamily: FONT_MONO,
                      fontSize: 10,
                      letterSpacing: '0.15em',
                      color: C.honey,
                      fontWeight: 700,
                      marginBottom: 10,
                    }}
                  >
                    ELIGIBILITY · {String(i + 1).padStart(2, '0')}
                  </div>
                  <h4
                    style={{
                      fontSize: 16,
                      fontWeight: 700,
                      color: C.ink,
                      margin: '0 0 10px',
                      letterSpacing: '-0.005em',
                    }}
                  >
                    {t.label}
                  </h4>
                  <p
                    style={{
                      fontSize: 13.5,
                      lineHeight: 1.7,
                      color: C.inkSoft,
                      margin: 0,
                    }}
                  >
                    {t.body}
                  </p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* 04. 우대 사항 매칭 */}
      <section
        style={{
          padding: '120px 48px',
          background: '#F4F8FA',
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="04"
            kicker="PREFERRED · 우대 사항"
            title={`자동화 도구 활용 · CS·SW 인접\n· 5년 비전`}
          />

          {/* 우대 사항 3축 */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: 20,
              marginBottom: 56,
            }}
          >
            {PREFERRED.map((p, i) => (
              <FadeIn key={p.n} delay={i * 0.06}>
                <div
                  style={{
                    background: C.inverse,
                    borderRadius: 20,
                    padding: 28,
                    boxShadow: C.cardShadow,
                    height: '100%',
                  }}
                >
                  <div
                    style={{
                      fontFamily: FONT_MONO,
                      fontSize: 11,
                      letterSpacing: '0.15em',
                      color: C.honey,
                      fontWeight: 700,
                      marginBottom: 10,
                    }}
                  >
                    PREFERRED · {String(p.n).padStart(2, '0')}
                  </div>
                  <h3
                    style={{
                      fontSize: 18,
                      fontWeight: 700,
                      color: C.ink,
                      margin: '0 0 14px',
                      letterSpacing: '-0.01em',
                      lineHeight: 1.35,
                    }}
                  >
                    {p.title}
                  </h3>
                  <p style={{ fontSize: 14, lineHeight: 1.75, color: C.inkSoft, margin: 0 }}>
                    {p.body}
                  </p>
                </div>
              </FadeIn>
            ))}
          </div>

          {/* 운영 트러블슈팅 케이스 6건 — QA 사이클 직접 사례 */}
          <FadeIn>
            <div style={{ marginBottom: 32 }}>
              <div
                style={{
                  fontFamily: FONT_MONO,
                  fontSize: 11,
                  letterSpacing: '0.18em',
                  color: C.inkMuted,
                  fontWeight: 700,
                  marginBottom: 8,
                }}
              >
                CASES · 결함 추적·재현·재발 차단 사이클
              </div>
              <h3
                style={{
                  fontSize: 28,
                  fontWeight: 800,
                  color: C.ink,
                  margin: 0,
                  letterSpacing: '-0.02em',
                  lineHeight: 1.25,
                }}
              >
                실제로 운영하며 추적·해결·메모리화한 결함 6건
              </h3>
            </div>
          </FadeIn>

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
