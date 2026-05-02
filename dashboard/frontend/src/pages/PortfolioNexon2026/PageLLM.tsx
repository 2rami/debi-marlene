/**
 * [플랫폼본부] 게임 도메인 LLM 평가 어시스턴트 (인턴) — 본사
 * 라우트: /portfolio/nexon/llm
 *
 * 페이지 구조
 *   Hero
 *   01 ABOUT
 *   02 시스템 아키텍처 (ARCHITECTURE)
 *   03 기술 스택 (TECH_STACK)
 *   04 주요 업무 매칭 (JD Match × 4)
 *   05 지원 자격 (게임 도메인 깊이 + 캐릭터)
 *   06 우대 사항 매칭 (다양한 장르 / LLM 평가 / 문서화)
 *   07 협업 사례 (COLLAB)
 *   Footer
 */

import { useEffect, useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import Lenis from 'lenis'
import Aurora from '../../components/common/Aurora'
import { C, FONT_BODY, FONT_MONO, FONT_DISPLAY } from './shared/colors'
import nexonLogoUrl from '../../assets/portfolio-nexon-2026/nexon-logo.png'
import FloatingShapes from './shared/FloatingShapes'
import StatGrid from './shared/StatGrid'
import JdMatchAccordion from './shared/JdMatchAccordion'
import CharacterBox from './shared/CharacterBox'
import GameList from './shared/GameList'
import Footer from './shared/Footer'
import ArchitectureDiagram from './shared/ArchitectureDiagram'
import TechStackChips from './shared/TechStackChips'
import CtaSection from './shared/CtaSection'
import SideNav from './shared/SideNav'
import CornerLabels from './shared/CornerLabels'
import Wordmark from './shared/Wordmark'
import TextType from '../../components/reactbits/TextType'
import ScrollReveal from '../../components/reactbits/ScrollReveal'
import MagicBento from '../../components/reactbits/MagicBento'
import CaseCard from './shared/CaseCard'
import {
  HERO,
  STATS,
  JD_MATCHES,
  CHARACTER,
  GAMES,
  CASES,
  CONTACT,
  ARCHITECTURE,
  TECH_STACK,
  ELIGIBILITY,
  COLLAB,
} from './content/llm'

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
  variant = 'auto',
}: {
  no: string
  kicker: string
  title: string
  dark?: boolean
  variant?: 'auto' | 'short' | 'quote'
}) {
  // auto: 14자 넘으면 quote 스타일 (긴 제목은 인용구처럼 흐릿하게)
  const resolved = variant === 'auto' ? (title.length > 14 ? 'quote' : 'short') : variant
  const isQuote = resolved === 'quote'

  return (
    <FadeIn>
      <div style={{ marginBottom: isQuote ? 56 : 72 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 18, marginBottom: isQuote ? 28 : 32 }}>
          <span style={{ fontFamily: FONT_MONO, fontSize: 12, fontWeight: 700, color: C.nexonBlue, letterSpacing: '0.2em' }}>
            {no}
          </span>
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              fontWeight: 800,
              color: dark ? 'rgba(245, 250, 249, 0.7)' : C.inkMuted,
              letterSpacing: '0.2em',
            }}
          >
            {kicker}
          </span>
          <span
            style={{
              flex: 1,
              height: 1,
              background: dark ? 'rgba(245, 250, 249, 0.18)' : 'rgba(10, 18, 36, 0.1)',
            }}
          />
        </div>

        {isQuote ? (
          <blockquote
            style={{
              margin: 0,
              padding: '0 0 0 28px',
              borderLeft: `3px solid ${dark ? 'rgba(245,250,249,0.35)' : C.nexonBlue}`,
              maxWidth: 920,
            }}
          >
            <p
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 'clamp(22px, 2.4vw, 32px)',
                fontWeight: 600,
                lineHeight: 1.55,
                letterSpacing: '-0.015em',
                color: dark ? 'rgba(245, 250, 249, 0.6)' : 'rgba(10, 18, 36, 0.5)',
                margin: 0,
                wordBreak: 'keep-all',
                fontStyle: 'normal',
              }}
            >
              <span style={{
                fontFamily: FONT_DISPLAY,
                fontSize: '1.4em',
                lineHeight: 0,
                color: dark ? 'rgba(245,250,249,0.3)' : 'rgba(0, 145, 204, 0.3)',
                marginRight: 6,
                verticalAlign: '-0.1em',
              }}>
                "
              </span>
              {title}
            </p>
          </blockquote>
        ) : (
          <h2
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(36px, 5.2vw, 64px)',
              fontWeight: 700,
              lineHeight: 1.18,
              letterSpacing: '-0.03em',
              color: dark ? C.inverse : C.ink,
              margin: 0,
              maxWidth: 980,
              wordBreak: 'keep-all',
            }}
          >
            {title}
          </h2>
        )}
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
      id="hero"
      style={{
        position: 'relative',
        minHeight: '100vh',
        padding: '40px clamp(48px, 8vw, 120px) 80px',
        overflow: 'hidden',
      }}
    >
      {/* Aurora Background — Nexon CI 컬러로 톤다운 */}
      <div className="absolute inset-0 opacity-25 mix-blend-screen pointer-events-none" style={{ zIndex: 0 }}>
        <Aurora colorStops={[C.nexonBlue, C.lime, C.nexonBlueAlt]} amplitude={0.9} speed={0.4} />
      </div>

      <motion.div style={{ y: shapesY, position: 'absolute', inset: 0, zIndex: 0, pointerEvents: 'none', opacity: 0.4 }}>
        <FloatingShapes />
      </motion.div>

      {/* 매거진 코너 라벨 ─ 좌상단 로고 / 우상단 카운터 */}
      <header
        style={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          maxWidth: 1480,
          margin: '0 auto',
          marginBottom: 80,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <img src={nexonLogoUrl} alt="NEXON" style={{ height: 32, width: 'auto', objectFit: 'contain' }} />
          <span style={{ height: 20, width: 1, background: 'rgba(10, 31, 60, 0.18)' }} />
          <span style={{ fontFamily: FONT_MONO, fontSize: 11, letterSpacing: '0.14em', color: C.inkMuted, fontWeight: 700 }}>
            PORTFOLIO · {HERO.jobCode}
          </span>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.inkMuted, letterSpacing: '0.18em', fontWeight: 700 }}>
            YANG GEONHO
          </div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.inkMuted, letterSpacing: '0.18em', fontWeight: 700, marginTop: 4 }}>
            ISSUE / 2026.05
          </div>
        </div>
      </header>

      {/* 매거진 본문 — 좌우 비대칭 */}
      <motion.div
        style={{
          y: textY,
          maxWidth: 1480,
          margin: '0 auto',
          position: 'relative',
          zIndex: 1,
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1.6fr) minmax(280px, 1fr)',
          gap: 80,
          alignItems: 'start',
        }}
      >
        {/* 좌: 큰 타이틀 */}
        <div>
          <FadeIn delay={0}>
            <div
              style={{
                display: 'inline-block',
                padding: '6px 14px',
                background: 'transparent',
                color: C.nexonBlue,
                fontFamily: FONT_MONO,
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: '0.18em',
                textTransform: 'uppercase',
                borderRadius: 9999,
                marginBottom: 48,
                border: `1px solid ${C.nexonBlue}`,
              }}
            >
              {HERO.badge}
            </div>
          </FadeIn>

          <h1
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(44px, 6.6vw, 92px)',
              fontWeight: 700,
              lineHeight: 1.04,
              letterSpacing: '-0.04em',
              color: C.ink,
              margin: 0,
              wordBreak: 'keep-all',
            }}
          >
            {HERO.titleLines.map((line, i) => {
              const isHighlight = line.includes(HERO.highlightWord)
              return (
                <FadeIn key={i} delay={0.15 + i * 0.12}>
                  <span style={{ display: 'block' }}>
                    {isHighlight ? (
                      <>
                        <span style={{ color: C.nexonBlue }}>{HERO.highlightWord}</span>
                        {line.replace(HERO.highlightWord, '')}
                      </>
                    ) : (
                      line
                    )}
                  </span>
                </FadeIn>
              )
            })}
          </h1>

          <FadeIn delay={0.6}>
            <div
              style={{
                fontSize: 'clamp(17px, 1.4vw, 21px)',
                fontWeight: 500,
                lineHeight: 1.7,
                color: C.inkSoft,
                maxWidth: 720,
                margin: '64px 0 48px',
                minHeight: '5em',
                fontFamily: FONT_BODY,
              }}
            >
              <TextType
                text={HERO.subtitle}
                typingSpeed={28}
                initialDelay={1500}
                loop={false}
                showCursor
                cursorCharacter="_"
                cursorClassName="text-[--color-ink]"
              />
            </div>
          </FadeIn>

          <FadeIn delay={0.7}>
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
                    gap: 8,
                    padding: '14px 24px',
                    fontSize: 15,
                    fontWeight: 700,
                    fontFamily: FONT_BODY,
                    borderRadius: 9999,
                    textDecoration: 'none',
                    transition: 'all 220ms cubic-bezier(0.4, 0, 0.2, 1)',
                    ...(cta.primary
                      ? { background: C.nexonBlue, color: C.inverse, boxShadow: '0 8px 24px rgba(0, 145, 204, 0.3)' }
                      : { background: 'transparent', color: C.ink, border: `1.5px solid rgba(10, 18, 36, 0.18)` }),
                  }}
                >
                  {cta.label}
                  <span style={{ fontSize: 14, opacity: 0.8 }}>↗</span>
                </a>
              ))}
            </div>
          </FadeIn>
        </div>

        {/* 우: 매거진 INFO 테이블 */}
        <FadeIn delay={0.4}>
          <div
            style={{
              padding: '32px 0 0',
              borderTop: `2px solid ${C.ink}`,
            }}
          >
            <div
              style={{
                fontFamily: FONT_MONO,
                fontSize: 10,
                letterSpacing: '0.2em',
                color: C.nexonBlue,
                fontWeight: 700,
                marginBottom: 24,
              }}
            >
              INFO
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                {HERO.meta.map((row) => (
                  <tr key={row.label} style={{ borderBottom: `1px solid ${C.cardBorder}` }}>
                    <td
                      style={{
                        fontFamily: FONT_MONO,
                        fontSize: 10.5,
                        letterSpacing: '0.16em',
                        color: C.inkMuted,
                        fontWeight: 700,
                        padding: '14px 0',
                        width: 100,
                        verticalAlign: 'top',
                      }}
                    >
                      {row.label}
                    </td>
                    <td
                      style={{
                        fontSize: 14.5,
                        color: C.ink,
                        fontWeight: 600,
                        padding: '14px 0',
                        lineHeight: 1.45,
                      }}
                    >
                      {row.value}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Quick stats — 매거진 마지널 */}
            <div
              style={{
                marginTop: 40,
                paddingTop: 28,
                borderTop: `1px dashed ${C.cardBorder}`,
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: 28,
              }}
            >
              {STATS.slice(0, 4).map((s) => (
                <div key={s.label}>
                  <div style={{ fontSize: 32, fontWeight: 800, lineHeight: 1, letterSpacing: '-0.025em', color: C.ink, fontVariantNumeric: 'tabular-nums' }}>
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
        </FadeIn>
      </motion.div>
    </section>
  )
}

// ─────────────────────────────────────────────
// 페이지
// ─────────────────────────────────────────────

export default function PageLLM() {
  // Lenis smooth scroll (Krafton 패턴)
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
        background: C.bgLight,
        minHeight: '100vh',
        overflowX: 'clip',
      }}
    >
      <CornerLabels ctaLabel="GO TO BOT" ctaHref="https://debimarlene.com" />

      <SideNav
        sections={[
          { id: 'hero', no: '00', label: 'INTRO' },
          { id: 'about', no: '01', label: 'ABOUT' },
          { id: 'architecture', no: '02', label: 'ARCHITECTURE' },
          { id: 'tech', no: '03', label: 'TECH STACK' },
          { id: 'jdmatch', no: '04', label: 'JD MATCH' },
          { id: 'eligibility', no: '05', label: 'ELIGIBILITY' },
          { id: 'preferred', no: '06', label: 'PREFERRED' },
          { id: 'collab', no: '07', label: 'COLLAB' },
          { id: 'highlights', no: '08', label: 'HIGHLIGHTS' },
          { id: 'contact', no: '09', label: 'CONTACT' },
        ]}
      />

      <Hero />

      {/* 01. ABOUT */}
      <section
        id="about"
        style={{
          padding: '200px clamp(48px, 8vw, 120px)',
          background: C.inverse,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader no="01" kicker="ABOUT" title="저는 이런 사람입니다" />

          <div style={{ margin: '0 0 160px', maxWidth: 1100 }}>
            <ScrollReveal
              baseOpacity={0.15}
              baseRotation={2}
              blurStrength={3}
              textStyle={{
                fontFamily: FONT_DISPLAY,
                fontSize: 'clamp(28px, 3.6vw, 44px)',
                fontWeight: 700,
                lineHeight: 1.38,
                color: C.ink,
                letterSpacing: '-0.025em',
                margin: 0,
              }}
            >
              게임 사용자의 도메인 깊이와 LLM 운영자의 평가 감각이 결합된 지점, 그것이 LLM 평가 어시스턴트 직무의 본질입니다.
            </ScrollReveal>
          </div>

          <FadeIn delay={0.15}>
            <StatGrid stats={STATS} />
          </FadeIn>

          <FadeIn delay={0.25}>
            <details
              style={{
                marginTop: 96,
                paddingTop: 40,
                borderTop: `1px solid ${C.cardBorder}`,
              }}
            >
              <summary
                style={{
                  cursor: 'pointer',
                  fontFamily: FONT_MONO,
                  fontSize: 12,
                  fontWeight: 700,
                  color: C.nexonBlue,
                  letterSpacing: '0.14em',
                  listStyle: 'none',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                전체 자기소개 읽기 ▾
              </summary>

              {/* 북디자인 본문 — 4단락 구조 + 핵심 명사 강조 + 마지막 pull quote */}
              <div style={{ marginTop: 56, display: 'flex', flexDirection: 'column', gap: 32, maxWidth: 640 }}>
                {/* Lede — 정체성 한 줄 */}
                <p
                  style={{
                    fontSize: 19,
                    lineHeight: 1.6,
                    fontWeight: 700,
                    color: C.ink,
                    margin: 0,
                    letterSpacing: '-0.015em',
                  }}
                >
                  <span style={{
                    fontFamily: FONT_DISPLAY,
                    fontSize: 36,
                    fontWeight: 800,
                    color: C.nexonBlue,
                    lineHeight: 1,
                    float: 'left',
                    marginRight: 8,
                    marginTop: 4,
                  }}>D</span>
                  데비&마를렌은 이터널 리턴 쌍둥이 실험체를 모티브로 한{' '}
                  <span style={{ color: C.nexonBlue }}>한국어 캐릭터 챗봇</span>입니다.
                </p>

                {/* Para 2 — 운영 + 시스템 구성 */}
                <p
                  style={{
                    fontSize: 16,
                    lineHeight: 1.85,
                    color: C.inkSoft,
                    margin: 0,
                    fontWeight: 400,
                    letterSpacing: '-0.005em',
                  }}
                >
                  <strong style={{ color: C.ink, fontWeight: 700 }}>1인이</strong> 기획·개발·배포·운영을 모두 맡아{' '}
                  <strong style={{ color: C.ink, fontWeight: 700 }}>9개월간 158개 Discord 서버</strong>에 운영 중이며, 단순 명령어 봇이 아니라{' '}
                  <strong style={{ color: C.ink, fontWeight: 700 }}>LangGraph StateGraph 2-tier 에이전트</strong>,{' '}
                  <strong style={{ color: C.ink, fontWeight: 700 }}>Anthropic Managed Agents(claude-haiku-4-5)</strong> 호스팅, Custom tool 자율 판단·네이티브 UI post,{' '}
                  <strong style={{ color: C.ink, fontWeight: 700 }}>패치노트 RAG</strong>, 음성 채널 실시간 응답 파이프라인(DAVE → VAD → Qwen3.5-Omni → CosyVoice3)까지 한 봇 안에 통합한 라이브 LLM 시스템입니다.
                </p>

                {/* Para 3 — 검증 활동 */}
                <p
                  style={{
                    fontSize: 16,
                    lineHeight: 1.85,
                    color: C.inkSoft,
                    margin: 0,
                    fontWeight: 400,
                    letterSpacing: '-0.005em',
                  }}
                >
                  매일 운영 중 발생하는 응답 데이터를{' '}
                  <strong style={{ color: C.ink, fontWeight: 700 }}>정량/정성으로 검증</strong>하고, 모델·프롬프트·few-shot·세션 회전 정책 변경에 따른{' '}
                  <strong style={{ color: C.ink, fontWeight: 700 }}>톤 일관성·환각률·비용 변화</strong>를 추적해 왔습니다.
                </p>

                {/* Pull quote — 직무 연결 */}
                <blockquote
                  style={{
                    margin: '16px 0 0',
                    padding: '24px 0 0 28px',
                    borderLeft: `3px solid ${C.nexonBlue}`,
                    borderTop: `1px dashed ${C.cardBorder}`,
                  }}
                >
                  <p
                    style={{
                      fontFamily: FONT_DISPLAY,
                      fontSize: 22,
                      lineHeight: 1.55,
                      fontWeight: 700,
                      color: C.ink,
                      margin: 0,
                      letterSpacing: '-0.02em',
                    }}
                  >
                    이 라이브 검증 경험을 게임 도메인의<br />
                    <span style={{ color: C.nexonBlue }}>LLM 평가 직무</span>로 그대로 이어 가고 싶습니다.
                  </p>
                </blockquote>
              </div>
            </details>
          </FadeIn>
        </div>
      </section>

      <Wordmark text="DEBI&MARLENE." />

      {/* 02. 시스템 아키텍처 — scroll-driven beam diagram */}
      <div id="architecture">
        <ArchitectureDiagram steps={ARCHITECTURE.steps} title={ARCHITECTURE.title} />
      </div>

      {/* 03. 기술 스택 */}
      <section
        id="tech"
        style={{
          padding: '200px clamp(48px, 8vw, 120px)',
          background: C.inverse,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="03"
            kicker="TECH STACK · 기술 스택"
            title="LLM · 인프라 · 프론트엔드 3블록으로 정리한 운영 스택"
          />

          <FadeIn delay={0.05}>
            <TechStackChips stack={TECH_STACK} highlightCount={3} />
          </FadeIn>
        </div>
      </section>

      {/* 04. 주요 업무 매칭 */}
      <section
        id="jdmatch"
        style={{
          padding: '200px clamp(48px, 8vw, 120px)',
          background: C.bgLight,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="04"
            kicker="JOB DESCRIPTION · 주요 업무"
            title="공고 4가지 주요 업무에 대한 1:1 매칭 근거"
          />
          <FadeIn delay={0.05}>
            <JdMatchAccordion items={JD_MATCHES} />
          </FadeIn>
        </div>
      </section>

      <Wordmark text="LIVE LLM." />

      {/* 05. 지원 자격 */}
      <section
        id="eligibility"
        style={{
          padding: '200px clamp(48px, 8vw, 120px)',
          background: C.inverse,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="05"
            kicker="ELIGIBILITY · 지원 자격"
            title="메이플 16년, 하드 세렌까지 — 라이트 유저가 못 밟는 깊이"
          />

          <FadeIn delay={0.05}>
            <div
              style={{
                background: `linear-gradient(135deg, ${C.nexonBlue} 0%, ${C.nexonLightBlue} 100%)`,
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
                      fontSize: 12,
                      letterSpacing: '0.15em',
                      color: C.lime,
                      fontWeight: 800,
                      marginBottom: 16,
                      background: 'rgba(255, 255, 255, 0.15)',
                      padding: '6px 14px',
                      display: 'inline-block',
                      borderRadius: 999,
                    }}
                  >
                    HEAVY USER · 10년 7개월
                  </div>
                  <div style={{ fontSize: 36, fontWeight: 800, lineHeight: 1.15, letterSpacing: '-0.02em' }}>
                    메이플스토리<br />
                    <span style={{ color: C.lime }}>284 LV</span>
                  </div>
                </div>
                <div style={{ fontSize: 16, lineHeight: 1.8, color: 'rgba(255, 255, 255, 0.9)' }}>
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

      {/* 06. 우대 사항 매칭 */}
      <section
        id="preferred"
        style={{
          padding: '200px clamp(48px, 8vw, 120px)',
          background: C.bgLight,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="06"
            kicker="PREFERRED · 우대 사항"
            title="다양한 장르 · LLM 평가 경험 · 명확한 문서화"
          />

          <FadeIn delay={0.05}>
            <div
              style={{
                background: C.inverse,
                borderRadius: 20,
                padding: 32,
                marginBottom: 32,
                boxShadow: C.cardShadow,
              }}
            >
              <div
                style={{
                  fontFamily: FONT_MONO,
                  fontSize: 11,
                  letterSpacing: '0.15em',
                  color: C.nexonBlue,
                  fontWeight: 700,
                  marginBottom: 8,
                }}
              >
                PREFERRED · 01 · 다양한 장르 플레이 경험
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
                MMORPG · FPS · 어드벤처 · 슈팅 · 수집형까지 — 5종 5장르
              </h3>
              <GameList games={GAMES} />
            </div>
          </FadeIn>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
            {CASES.map((c, i) => (
              <FadeIn key={c.no} delay={i * 0.04}>
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

      <Wordmark text="GENO." />

      {/* 07. 협업 사례 */}
      <section
        id="collab"
        style={{
          padding: '200px clamp(48px, 8vw, 120px)',
          background: C.inverse,
        }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto' }}>
          <SectionHeader
            no="07"
            kicker="COLLABORATION · 협업"
            title="다른 직군과 부딪힐 때 데이터 위에서 합의를 만들어 왔습니다"
          />

          <FadeIn delay={0.05}>
            <article
              style={{
                background: C.bgLight,
                borderRadius: 20,
                padding: 40,
                border: '1px solid rgba(26, 43, 71, 0.06)',
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.6fr)',
                gap: 48,
              }}
            >
              <div>
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 11,
                    letterSpacing: '0.15em',
                    color: C.nexonBlue,
                    fontWeight: 700,
                    marginBottom: 12,
                  }}
                >
                  PROBLEM · APPROACH · RESULT
                </div>
                <h3
                  style={{
                    fontSize: 24,
                    fontWeight: 800,
                    lineHeight: 1.3,
                    color: C.ink,
                    margin: 0,
                    letterSpacing: '-0.015em',
                  }}
                >
                  {COLLAB.title}
                </h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                {(
                  [
                    { label: '문제', body: COLLAB.problem, accent: false, bridge: false },
                    { label: '접근', body: COLLAB.approach, accent: false, bridge: false },
                    { label: '결과', body: COLLAB.result, accent: true, bridge: false },
                    { label: '직무 연결', body: COLLAB.bridge, accent: false, bridge: true },
                  ] as const
                ).map((row) => (
                  <div
                    key={row.label}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '72px 1fr',
                      gap: 16,
                      alignItems: 'baseline',
                    }}
                  >
                    <span
                      style={{
                        fontFamily: FONT_MONO,
                        fontSize: 11,
                        letterSpacing: '0.1em',
                        color: row.bridge ? C.nexonBlue : row.accent ? C.nexonBlue : C.inkMuted,
                        fontWeight: 700,
                      }}
                    >
                      {row.label}
                    </span>
                    <p
                      style={{
                        fontSize: 14,
                        lineHeight: 1.75,
                        color: row.bridge ? C.nexonBlue : C.inkSoft,
                        margin: 0,
                        fontWeight: row.bridge ? 600 : 500,
                      }}
                    >
                      {row.body}
                    </p>
                  </div>
                ))}
              </div>
            </article>
          </FadeIn>
        </div>
      </section>

      {/* HIGHLIGHTS — Magic Bento (라이트 안에 다크 카드로 인셋) */}
      <section id="highlights" style={{ padding: '120px clamp(24px, 5vw, 80px)', background: C.bgLight }}>
        <div style={{
          maxWidth: 1480,
          margin: '0 auto',
          background: '#070B14',
          borderRadius: 32,
          padding: 'clamp(56px, 7vw, 96px)',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div style={{ marginBottom: 80 }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 18, marginBottom: 32 }}>
              <span style={{ fontFamily: FONT_MONO, fontSize: 12, fontWeight: 700, color: C.lime, letterSpacing: '0.2em' }}>
                HIGHLIGHTS
              </span>
              <span style={{ fontFamily: FONT_MONO, fontSize: 11, fontWeight: 700, color: 'rgba(255,255,255,0.5)', letterSpacing: '0.2em' }}>
                AT A GLANCE
              </span>
              <span style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.18)' }} />
            </div>
            <h2 style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(36px, 5vw, 64px)',
              fontWeight: 700,
              lineHeight: 1.12,
              letterSpacing: '-0.03em',
              color: C.inverse,
              margin: 0,
            }}>
              핵심 6가지를 한눈에
            </h2>
          </div>
          <MagicBento
            glowColor="0, 145, 204"
            spotlightRadius={320}
            items={[
              {
                label: 'LIVE',
                title: '158서버 × 9개월',
                description: '1인 라이브 LLM 챗봇 운영. 매일 응답 데이터 직접 관측.',
                span: { col: 2 },
              },
              {
                label: 'CACHE',
                title: '99%+ 적중률',
                description: 'system block ephemeral cache 적용 — 비용·지연 정량 개선.',
              },
              {
                label: 'SPEED',
                title: '0.1ms 분류',
                description: 'classify_intent (정규식, LLM 호출 없음) — 비용 분리 측정.',
              },
              {
                label: 'STACK',
                title: '2-tier 폴백 아키텍처',
                description: 'LangGraph StateGraph + Anthropic Managed Agents (haiku-4-5).',
                span: { col: 2 },
              },
              {
                label: 'GAME',
                title: '메이플 16년 · 하드 세렌',
                description: '프로즌샤 · 어센틱/시메라 콘텐츠 정점까지 직접 격파.',
              },
              {
                label: 'EVAL',
                title: '정량/정성 평가 감각',
                description: '모델·프롬프트·세션 회전 변화에 따른 톤·환각·비용 추적.',
              },
            ]}
          />
        </div>
      </section>

      <div id="contact">
        <CtaSection
          kicker="LET'S TALK"
          headline={`라이브 LLM을 운영해 본 사람이\n넥슨 LLM 평가에 합류하면 좋겠습니다`}
          sub="158서버 × 9개월 × 매일 측정. 게임 도메인 16년의 사용자 시점과 LLM 운영자의 평가 감각이 한 자리에서 만나는 자리, LLM 평가 어시스턴트가 그 자리라고 확신합니다."
          items={[
            { label: 'GitHub · debi-marlene', href: CONTACT.github, primary: true },
            { label: 'Live · debimarlene.com', href: CONTACT.domain },
            { label: `Email · ${CONTACT.email}`, href: `mailto:${CONTACT.email}` },
          ]}
        />
      </div>
      <Footer email={CONTACT.email} github={CONTACT.github} domain={CONTACT.domain} edu={CONTACT.edu} />
    </div>
  )
}
