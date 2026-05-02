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
import MapleChatbot from './shared/MapleChatbot'
import Wordmark from './shared/Wordmark'
import NexonGate from './shared/NexonGate'
import Button from './shared/Button'
import SectionShell from './shared/SectionShell'
import TextType from '../../components/reactbits/TextType'
import ScrollReveal from '../../components/reactbits/ScrollReveal'
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
      id="intro"
      style={{
        position: 'relative',
        minHeight: '100vh',
        padding: '120px clamp(48px, 8vw, 120px) 120px',
        overflow: 'hidden',
        background: C.bgWhite,
      }}
    >
      {/* Aurora Background — Nexon CI 톤다운 (블루만) */}
      <div className="absolute inset-0 opacity-20 mix-blend-screen pointer-events-none" style={{ zIndex: 0 }}>
        <Aurora colorStops={[C.nexonBlue, C.nexonLightBlue, C.nexonBlueAlt]} amplitude={0.9} speed={0.4} />
      </div>

      <motion.div style={{ y: shapesY, position: 'absolute', inset: 0, zIndex: 0, pointerEvents: 'none', opacity: 0.3 }}>
        <FloatingShapes />
      </motion.div>

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
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              {HERO.ctas.map((cta) => (
                <Button
                  key={cta.label}
                  href={cta.href}
                  label={cta.label}
                  variant="outline"
                />
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
      <MapleChatbot />

      <SideNav
        sections={[
          { id: 'hero', no: 'CH 0', label: 'GATE' },
          { id: 'intro', no: 'CH 1', label: 'WHO' },
          { id: 'architecture', no: 'CH 2', label: 'WHAT' },
          { id: 'jdmatch', no: 'CH 3', label: 'WHY' },
          { id: 'contact', no: 'CH 4', label: 'REACH' },
        ]}
      />

      <NexonGate />

      <Wordmark text="CH 1 WHO." />

      <Hero />

      {/* 01. ABOUT — aside 패턴 (좌 sticky 라벨 + 우 narrow column) */}
      <SectionShell
        id="about"
        ch="CH 1"
        no="01"
        kicker="WHO · ABOUT"
        title="저는 이런 사람입니다"
        variant="aside"
      >
          <div style={{ margin: '0 0 80px' }}>
            <ScrollReveal
              baseOpacity={0.15}
              baseRotation={2}
              blurStrength={3}
              textStyle={{
                fontFamily: FONT_DISPLAY,
                fontSize: 'clamp(22px, 2.6vw, 32px)',
                fontWeight: 700,
                lineHeight: 1.4,
                color: C.ink,
                letterSpacing: '-0.022em',
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
                marginTop: 80,
                paddingTop: 32,
                borderTop: `1px solid ${C.cardBorder}`,
              }}
            >
              <summary
                style={{
                  cursor: 'pointer',
                  fontFamily: FONT_BODY,
                  fontSize: 12,
                  fontWeight: 700,
                  color: C.nexonBlue,
                  letterSpacing: '0.18em',
                  textTransform: 'uppercase',
                  listStyle: 'none',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                전체 자기소개 읽기 ▾
              </summary>

              {/* 북디자인 본문 — 4단락 구조 + 핵심 명사 강조 + 마지막 pull quote */}
              <div style={{ marginTop: 40, display: 'flex', flexDirection: 'column', gap: 28, maxWidth: 640 }}>
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
      </SectionShell>

      <Wordmark text="CH 2 WHAT." />

      {/* 02. 시스템 아키텍처 — scroll-driven beam diagram */}
      <div id="architecture">
        <ArchitectureDiagram steps={ARCHITECTURE.steps} title={ARCHITECTURE.title} />
      </div>

      {/* 03. 기술 스택 — bleed 패턴 (풀블리드 + 박스 제거) */}
      <SectionShell
        id="tech"
        ch="CH 2"
        no="03"
        kicker="TECH STACK · 기술 스택"
        title="LLM · 인프라 · 프론트엔드 3블록으로 정리한 운영 스택"
        variant="bleed"
        background={C.bgSoft}
      >
          <FadeIn delay={0.05}>
            <div style={{ maxWidth: 1480, margin: '0 auto', padding: '0 clamp(20px, 3vw, 80px)' }}>
              <TechStackChips stack={TECH_STACK} highlightCount={3} />
            </div>
          </FadeIn>
      </SectionShell>

      <Wordmark text="CH 3 WHY." />

      {/* 04. 주요 업무 매칭 — aside 패턴 */}
      <SectionShell
        id="jdmatch"
        ch="CH 3"
        no="04"
        kicker="JOB DESCRIPTION · 주요 업무"
        title="공고 4가지 업무에 대한 1:1 매칭"
        variant="aside"
        background={C.bgWhite}
      >
          <FadeIn delay={0.05}>
            <JdMatchAccordion items={JD_MATCHES} />
          </FadeIn>
      </SectionShell>

      {/* 05. 지원 자격 — split 패턴 (좌 메이플 텍스트 / 우 캐릭터) */}
      <SectionShell
        id="eligibility"
        ch="CH 3"
        no="05"
        kicker="ELIGIBILITY · 지원 자격"
        title="메이플 16년, 하드 세렌까지"
        variant="split"
        background={C.bgLight}
        rightAccessory={
          <FadeIn delay={0.05}>
            <div
              style={{
                marginTop: 40,
                padding: '32px 0',
                borderTop: `1px solid ${C.cardBorder}`,
              }}
            >
              <div
                style={{
                  fontFamily: FONT_BODY,
                  fontSize: 11,
                  letterSpacing: '0.22em',
                  color: C.nexonBlue,
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  marginBottom: 12,
                }}
              >
                Heavy User · 16년+
              </div>
              <div
                style={{
                  fontFamily: FONT_DISPLAY,
                  fontSize: 'clamp(28px, 3vw, 38px)',
                  fontWeight: 800,
                  lineHeight: 1.15,
                  letterSpacing: '-0.025em',
                  color: C.ink,
                  marginBottom: 24,
                }}
              >
                메이플스토리<br />
                <span style={{ color: C.nexonBlue }}>프로즌샤 · 284 LV</span>
              </div>
              <p
                style={{
                  fontSize: 15,
                  lineHeight: 1.85,
                  color: C.inkSoft,
                  margin: 0,
                  fontWeight: 500,
                  maxWidth: 460,
                  wordBreak: 'keep-all',
                }}
              >
                {ELIGIBILITY.body}
              </p>
            </div>
          </FadeIn>
        }
      >
          <FadeIn delay={0.12}>
            <CharacterBox character={CHARACTER} />
          </FadeIn>
      </SectionShell>

      {/* 06. 우대 사항 — bleed 패턴 (풀블리드 + 박스 제거) */}
      <SectionShell
        id="preferred"
        ch="CH 3"
        no="06"
        kicker="PREFERRED · 우대 사항"
        title="다양한 장르 · LLM 평가 경험 · 명확한 문서화"
        variant="bleed"
        background={C.bgWhite}
      >
          <div style={{ maxWidth: 1480, margin: '0 auto', padding: '0 clamp(20px, 3vw, 80px)' }}>
            <FadeIn delay={0.05}>
              <div
                style={{
                  paddingTop: 32,
                  paddingBottom: 56,
                  borderTop: `1px solid ${C.cardBorder}`,
                  borderBottom: `1px solid ${C.cardBorder}`,
                }}
              >
                <div
                  style={{
                    fontFamily: FONT_BODY,
                    fontSize: 11,
                    letterSpacing: '0.22em',
                    color: C.nexonBlue,
                    fontWeight: 800,
                    textTransform: 'uppercase',
                    marginBottom: 12,
                  }}
                >
                  PREFERRED · 01 · 다양한 장르
                </div>
                <h3
                  style={{
                    fontFamily: FONT_DISPLAY,
                    fontSize: 'clamp(22px, 2.4vw, 30px)',
                    fontWeight: 700,
                    color: C.ink,
                    margin: '0 0 32px',
                    letterSpacing: '-0.015em',
                    wordBreak: 'keep-all',
                    maxWidth: 800,
                  }}
                >
                  MMORPG · FPS · 어드벤처 · 슈팅 · 수집형까지 — 5종 5장르
                </h3>
                <GameList games={GAMES} />
              </div>
            </FadeIn>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 0, marginTop: 0 }}>
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
      </SectionShell>

      {/* 07. 협업 사례 — aside 패턴 (좁은 quote) */}
      <SectionShell
        id="collab"
        ch="CH 3"
        no="07"
        kicker="COLLABORATION · 협업"
        title="데이터 위에서 합의를 만듭니다"
        variant="aside"
        background={C.bgLight}
      >
          <FadeIn delay={0.05}>
            <p
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 'clamp(20px, 2.2vw, 28px)',
                lineHeight: 1.5,
                fontWeight: 700,
                color: C.ink,
                letterSpacing: '-0.018em',
                margin: '0 0 56px',
                wordBreak: 'keep-all',
                paddingLeft: 24,
                borderLeft: `3px solid ${C.nexonBlue}`,
              }}
            >
              {COLLAB.title}
            </p>
          </FadeIn>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
            {(
              [
                { label: '문제', body: COLLAB.problem, accent: false, bridge: false },
                { label: '접근', body: COLLAB.approach, accent: false, bridge: false },
                { label: '결과', body: COLLAB.result, accent: true, bridge: false },
                { label: '직무 연결', body: COLLAB.bridge, accent: false, bridge: true },
              ] as const
            ).map((row, i) => (
              <FadeIn key={row.label} delay={0.05 + i * 0.04}>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '92px 1fr',
                    gap: 24,
                    alignItems: 'baseline',
                    paddingTop: 20,
                    borderTop: `1px solid ${row.bridge ? C.nexonBlue : C.cardBorder}`,
                  }}
                >
                  <span
                    style={{
                      fontFamily: FONT_BODY,
                      fontSize: 11,
                      letterSpacing: '0.22em',
                      color: row.bridge ? C.nexonBlue : C.inkMuted,
                      fontWeight: 800,
                      textTransform: 'uppercase',
                    }}
                  >
                    {row.label}
                  </span>
                  <p
                    style={{
                      fontSize: 15,
                      lineHeight: 1.85,
                      color: row.bridge ? C.nexonBlue : C.inkSoft,
                      margin: 0,
                      fontWeight: row.bridge ? 600 : 500,
                      wordBreak: 'keep-all',
                    }}
                  >
                    {row.body}
                  </p>
                </div>
              </FadeIn>
            ))}
          </div>
      </SectionShell>

      <Wordmark text="CH 4 REACH." />

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
