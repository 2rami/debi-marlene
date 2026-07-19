/**
 * [AI본부 메이플AX실] 웹 프론트엔드 엔지니어 (인턴) — 넥슨코리아
 * 라우트: /portfolio/nexon/frontend (대표 · 제출용)
 * 공고: careers.nexon.com/recruit/10027
 *
 * 사이오닉 슬라이드덱 엔진(shared/SlideDeck) 재사용 + content/frontend 콘텐츠.
 * 다크/라이트 토글(좌하단) · 우측 진행바 · 은은한 배경 · 가로 카드 스택.
 * 구조: Hero → 선언 → About(+STACK 마퀴) → JD매칭 → Cases → 자격·우대 → Closing+Footer
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { motion, useScroll, useTransform, animate } from 'framer-motion'
import Aurora from '../../components/common/Aurora'
import BlurText from '../../components/common/BlurText'
import Ballpit from '../../components/common/Ballpit'
import TextType from '../../components/reactbits/TextType'
import FloatingShapes from './shared/FloatingShapes'
import SlideDeck, { type Slide } from './shared/SlideDeck'
import MapleChatbot from './shared/MapleChatbot'
import { HERO, STATS, ABOUT, JD_MATCHES, PREFERRED, ELIGIBILITY, CASES, CONTACT, ARCHITECTURE, GAMES } from './content/frontend'

const FONT = "'Pretendard Variable', 'Pretendard', 'Paperlogy', -apple-system, BlinkMacSystemFont, sans-serif"
const ACCENT = '#0091CC' // 넥슨 블루
const BLUE_LIGHT = '#5BC0E5'
const BAND = '#0A1326' // 마퀴·Footer 강조 밴드 (모드 무관 다크)

// 넥슨 메이플AX실 공고 조직소개 인용 (About 슬라이드 blockquote)
const NEXON_QUOTE =
  '단순한 AI API 호출을 넘어, 브라우저에서 시각 요소를 자유롭게 편집하고 실시간으로 협업할 수 있는 리치 애플리케이션을 지향합니다.'

const KEY_TRAITS = [
  '디자이너 출신 프론트엔드', 'React · Vite · TypeScript', 'three.js · WebGL · wgpu', 'GSAP · Lenis 스크롤',
  'Rust GPU 터미널(kasaterm)', '디자인 시스템 · 토큰', 'SSE 실시간 스트리밍', 'MCP · hook 하네스',
]
const STACK_A = ['React 19', 'Vite', 'TypeScript', 'Tailwind', 'GSAP', 'ScrollTrigger', 'Lenis', 'framer-motion', 'three.js', 'WebGL']
const STACK_B = ['Rust', 'wgpu', 'winit', 'vt100', 'damage tracking', 'P3 / Bradford', 'Managed Agents', 'SSE', 'MCP · hook', 'LiteLLM', 'RAG']

// 03 STACK 상세 — 카테고리별 헤드라인 + chips (스크롤 포폴 Ch2WhatFE 에서 이관)
const STACK_DETAIL: { category: string; headline: string; chips: string[] }[] = [
  { category: 'FRONTEND · 프레임워크', headline: 'React 19 + Vite + TypeScript + Tailwind — 이 페이지의 뼈대', chips: ['React 19', 'Vite', 'TypeScript', 'Tailwind'] },
  { category: 'FRONTEND · 스크롤·모션', headline: 'GSAP ScrollTrigger + Lenis + framer-motion 을 한 루프로', chips: ['GSAP', 'ScrollTrigger', 'Lenis', 'framer-motion'] },
  { category: 'FRONTEND · 3D·그래픽스', headline: 'three.js 배경 + WebGL 셰이더를 섹션별로 교체', chips: ['three.js', 'WebGL', 'Ballpit', 'Aurora'] },
  { category: 'NATIVE · GPU 터미널', headline: 'kasaterm — Rust 로 직접 짠 GPU 셀 렌더러', chips: ['Rust', 'wgpu', 'winit', 'vt100'] },
  { category: 'NATIVE · 렌더 최적화', headline: 'damage tracking + P3/Bradford 색 파이프라인 (1.25GB→113MB)', chips: ['damage tracking', 'P3', 'Bradford', 'GPU readback'] },
  { category: 'AI · 모델 연동', headline: 'Anthropic Managed Agent SSE 스트리밍 챗봇 (이 페이지 하단)', chips: ['Managed Agents', 'SSE', 'streaming'] },
  { category: 'AI · 개발 하네스', headline: 'MCP + hook + 서브에이전트 + LiteLLM 멀티모델 스위칭', chips: ['MCP', 'hook', '서브에이전트', 'LiteLLM'] },
  { category: 'INFRA · 배포', headline: 'PWA + Cloudflare 캐시 + GCP · Docker', chips: ['PWA', 'Cloudflare', 'GCP', 'Docker'] },
]

// 슬라이드 index별 캐릭터 말풍선 — SlideDeck onIndexChange 로 char-say 이벤트 dispatch.
// 스크롤이 없는 덱이라 캐릭터가 섹션 전환을 스크롤로 감지 못 함 → 여기서 직접 먹여준다.
const SECTION_BUBBLES = [
  '안녕하세요!\n디지털 클론 양건호예요 👋',
  '디자인도 개발도\n제가 다 합니다 💪',
  '제 소개, 읽어봐 주세요 📖',
  '이 페이지, 어떻게\n만들었는지 볼까요? 🛠️',
  '이 화면을 굴리는\n기술 스택이에요 ⚙️',
  '넥슨 JD랑 어떻게\n맞물리는지 볼까요? 🎯',
  '지원 자격, 저는\n이미 매일 씁니다 ✅',
  '메이플 16년 차\n헤비 게이머예요 🍁',
  '직접 해결한\n사례들이에요 🔧',
  '끝까지 봐주셔서\n감사합니다 💙',
]

// ─────────────────────────────────────────────
// 테마
// ─────────────────────────────────────────────

function makeTheme(isDark: boolean) {
  return {
    isDark,
    pageBg: isDark ? '#070D1C' : '#F4F7FB',
    sec: isDark ? '#0C1528' : '#FFFFFF',
    secAlt: isDark ? '#080F20' : '#F4F7FB',
    ink: isDark ? '#FFFFFF' : '#0A1224',
    sub: isDark ? 'rgba(255,255,255,0.68)' : '#3F4A5F',
    muted: isDark ? 'rgba(255,255,255,0.5)' : '#8A95A6',
    card: isDark ? 'rgba(255,255,255,0.05)' : '#FFFFFF',
    cardSolid: isDark ? '#0E1A33' : '#FFFFFF',
    cardBorder: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(10,18,36,0.08)',
    cardShadow: isDark ? '0 24px 60px -16px rgba(0,0,0,0.5)' : '0 24px 60px -16px rgba(10,18,36,0.16)',
    accentSoft: isDark ? 'rgba(0,145,204,0.16)' : '#E6F5FB',
    line: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(10,18,36,0.1)',
  }
}
type Theme = ReturnType<typeof makeTheme>

function ThemeToggle({ isDark, toggle }: { isDark: boolean; toggle: () => void }) {
  return (
    <button
      onClick={toggle}
      aria-label="다크/라이트 전환"
      style={{
        position: 'fixed', bottom: 24, left: 24, zIndex: 200, width: 50, height: 50, borderRadius: 9999,
        border: `1px solid ${isDark ? 'rgba(255,255,255,0.22)' : 'rgba(10,18,36,0.12)'}`,
        background: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.92)',
        backdropFilter: 'blur(10px)', boxShadow: '0 8px 24px rgba(0,0,0,0.22)', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: isDark ? '#FFD166' : '#0A1224', transition: 'all 200ms',
      }}
    >
      {isDark ? (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" /></svg>
      ) : (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" /></svg>
      )}
    </button>
  )
}

// ─────────────────────────────────────────────
// CountUp / Marquee / 모션
// ─────────────────────────────────────────────

function CountUp({ value }: { value: string }) {
  const target = parseInt(String(value).replace(/[^0-9]/g, ''), 10) || 0
  const [disp, setDisp] = useState('0')
  useEffect(() => {
    const controls = animate(0, target, { duration: 1.4, delay: 0.35, ease: [0.22, 1, 0.36, 1], onUpdate: (v) => setDisp(Math.round(v).toLocaleString()) })
    return () => controls.stop()
  }, [target])
  return <span>{disp}</span>
}

function Marquee({ items, reverse = false, duration = 28 }: { items: readonly string[]; reverse?: boolean; duration?: number }) {
  const doubled = [...items, ...items]
  return (
    <div style={{ overflow: 'hidden', maskImage: 'linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent)', WebkitMaskImage: 'linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent)' }}>
      <motion.div style={{ display: 'flex', gap: 14, width: 'max-content', paddingBlock: 6 }} animate={{ x: reverse ? ['-50%', '0%'] : ['0%', '-50%'] }} transition={{ duration, ease: 'linear', repeat: Infinity }}>
        {doubled.map((it, i) => (
          <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: 9, padding: '11px 20px', borderRadius: 9999, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', color: 'rgba(255,255,255,0.9)', fontFamily: FONT, fontSize: 14.5, fontWeight: 600, whiteSpace: 'nowrap', letterSpacing: '-0.005em' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: BLUE_LIGHT, flexShrink: 0 }} />
            {it}
          </span>
        ))}
      </motion.div>
    </div>
  )
}

function FadeIn({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.05 }} transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}>
      {children}
    </motion.div>
  )
}

// 슬라이드별 배경 이펙트 — variant 로 종류를 달리해 Aurora 도배를 피한다.
// 인접 슬라이드끼리 같은 종류가 겹치지 않게 매핑(Shapes·Aurora·Ballpit).
type BgVariant = 'aurora-blue' | 'aurora-violet' | 'shapes' | 'shapes-flip' | 'ballpit'
function SectionBg({ t, variant = 'aurora-blue' }: { t: Theme; variant?: BgVariant }) {
  if (variant === 'shapes' || variant === 'shapes-flip') {
    return (
      <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 0, opacity: t.isDark ? 0.55 : 0.7, transform: variant === 'shapes-flip' ? 'scaleX(-1)' : undefined }}>
        <FloatingShapes />
      </div>
    )
  }
  if (variant === 'ballpit') {
    return (
      <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 0, opacity: t.isDark ? 0.9 : 0.72 }}>
        <Ballpit colors={[0x0091cc, 0x5bc0e5, 0xbfe6f5]} count={110} gravity={0.4} friction={0.995} maxSize={1.1} minSize={0.4} followCursor />
      </div>
    )
  }
  const stops = variant === 'aurora-violet' ? ['#6D5EF7', '#00B4D8', '#48CAE4'] : [ACCENT, '#5BC0E5', '#BFE6F5']
  return (
    <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 0, opacity: t.isDark ? 0.34 : 0.22 }}>
      <Aurora colorStops={stops} amplitude={1.0} speed={0.35} />
    </div>
  )
}

function SectionHeader({ no, kicker, title, t }: { no: string; kicker: string; title: string; t: Theme }) {
  return (
    <FadeIn>
      <div style={{ marginBottom: 56 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 24 }}>
          <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.18em' }}>{no}</span>
          <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 600, color: t.muted, letterSpacing: '0.18em' }}>{kicker}</span>
          <span style={{ flex: 1, height: 1, background: t.line }} />
        </div>
        <h2 style={{ fontFamily: FONT, fontSize: 'clamp(30px, 4.2vw, 50px)', fontWeight: 800, lineHeight: 1.2, letterSpacing: '-0.025em', color: t.ink, margin: 0, whiteSpace: 'pre-line', wordBreak: 'keep-all' }}>{title}</h2>
      </div>
    </FadeIn>
  )
}

// 풀스크린 텍스트 슬라이드 — 큰 한 줄 + 부제 (BlurText 어절 등장)
function Statement({ text, sub, kicker, bg, t, bgVariant = 'aurora-blue' }: { text: string; sub?: string; kicker: string; bg: string; t: Theme; bgVariant?: BgVariant }) {
  return (
    <section style={{ position: 'absolute', inset: 0, padding: 'clamp(48px, 6vw, 96px)', background: bg, overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <SectionBg t={t} variant={bgVariant} />
      <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 'clamp(26px, 4.2vh, 48px)' }}>
          <span style={{ width: 24, height: 1, background: ACCENT }} />
          <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.24em' }}>{kicker}</span>
        </div>
        <div style={{ fontFamily: FONT, fontSize: 'clamp(28px, 4.6vw, 58px)', fontWeight: 800, lineHeight: 1.24, letterSpacing: '-0.035em', color: t.ink, wordBreak: 'keep-all' }}>
          {text.split('\n').map((line, i) => (
            <BlurText key={i} text={line} delay={55} animateBy="words" direction="bottom" className="!m-0" />
          ))}
        </div>
        {sub && (
          <p style={{ fontFamily: FONT, fontSize: 'clamp(15px, 1.7vw, 20px)', fontWeight: 500, lineHeight: 1.65, color: t.sub, margin: 'clamp(24px, 3.6vh, 44px) 0 0', maxWidth: 720, wordBreak: 'keep-all' }}>{sub}</p>
        )}
      </div>
    </section>
  )
}

function Kicker({ label, no }: { label: string; no?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 'clamp(20px, 3vh, 30px)' }}>
      <span style={{ width: 24, height: 1, background: ACCENT }} />
      {no && <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.18em' }}>{no}</span>}
      <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.22em' }}>{label}</span>
    </div>
  )
}

// 섹션↔캐릭터 상호작용 칩 — 누르면 우하단 캐릭터(챗봇)가 열리며 이 질문을 자동 전송한다.
function AskChip({ prompt, label, t }: { prompt: string; label?: string; t: Theme }) {
  return (
    <button
      onClick={() => window.dispatchEvent(new CustomEvent('nexon:char-ask', { detail: { prompt } }))}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 9, padding: '10px 16px', borderRadius: 9999, background: t.accentSoft, border: `1px solid ${ACCENT}44`, color: ACCENT, fontFamily: FONT, fontSize: 13, fontWeight: 700, letterSpacing: '-0.005em', cursor: 'pointer', transition: 'transform 180ms, box-shadow 180ms' }}
      onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = `0 8px 20px ${ACCENT}33` }}
      onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={ACCENT} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" /></svg>
      <span>{label ?? prompt}</span>
      <span style={{ fontSize: 11, fontWeight: 800, opacity: 0.65 }}>· 물어보기</span>
    </button>
  )
}

function SlidePane({ children, bg, t, withBg = true, center = true, pad, bgVariant = 'aurora-blue' }: { children: React.ReactNode; bg: string; t: Theme; withBg?: boolean; center?: boolean; pad?: string; bgVariant?: BgVariant }) {
  return (
    <section style={{ position: 'absolute', inset: 0, background: bg, overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: center ? 'center' : 'flex-start', padding: pad ?? 'clamp(56px, 8vh, 104px) clamp(28px, 6vw, 96px)' }}>
      {withBg && <SectionBg t={t} variant={bgVariant} />}
      <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>{children}</div>
    </section>
  )
}

function PanelShell({ children }: { children: React.ReactNode }) {
  return (
    <section style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 'clamp(56px, 8vh, 104px) clamp(40px, 7vw, 120px)' }}>
      <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>{children}</div>
    </section>
  )
}

// ─────────────────────────────────────────────
// Hero
// ─────────────────────────────────────────────

function Hero({ t }: { t: Theme }) {
  const heroRef = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '18%'])
  const heroBg = t.isDark
    ? 'radial-gradient(125% 95% at 50% 0%, #0B1E42 0%, #070D20 55%, #04060F 100%)'
    : 'radial-gradient(125% 95% at 50% 0%, #E4EEFF 0%, #F4F7FB 58%, #F4F7FB 100%)'

  return (
    <section ref={heroRef} style={{ position: 'absolute', inset: 0, padding: 'clamp(36px, 5vw, 56px) clamp(28px, 6vw, 48px)', overflow: 'hidden', background: heroBg, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      {/* 첫 화면 배경 = Ballpit(three.js). 커서를 따라 공이 밀린다 — 도입부 인터랙션. */}
      <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 0, opacity: t.isDark ? 0.9 : 0.62 }}>
        <Ballpit colors={[0x0091cc, 0x5bc0e5, 0xbfe6f5]} count={90} gravity={0.32} friction={0.997} maxSize={1.0} minSize={0.4} followCursor />
      </div>

      <header style={{ position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', maxWidth: 1180, margin: '0 auto', paddingBottom: 24, borderBottom: `1px solid ${t.line}`, color: t.isDark ? BLUE_LIGHT : ACCENT, flexWrap: 'wrap', gap: 16 }}>
        <span style={{ fontFamily: FONT, fontSize: 11, letterSpacing: '0.12em', opacity: 0.9, fontWeight: 700 }}>PORTFOLIO · {HERO.jobCode}</span>
        <span style={{ fontFamily: FONT, fontSize: 11, letterSpacing: '0.08em', opacity: 0.9, fontWeight: 700 }}>YANG · GEONHO / 2026</span>
      </header>

      <motion.div style={{ y: textY, maxWidth: 1180, margin: '0 auto', position: 'relative', zIndex: 1, paddingTop: 88, paddingBottom: 56 }}>
        <FadeIn delay={0}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10, marginBottom: 36, fontFamily: FONT, fontSize: 12.5, fontWeight: 700, color: t.isDark ? BLUE_LIGHT : ACCENT, letterSpacing: '0.03em' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: ACCENT, boxShadow: `0 0 0 4px ${ACCENT}28` }} />
            {HERO.badge}
          </div>
        </FadeIn>

        <FadeIn delay={0.15}>
          <div style={{ fontFamily: FONT, fontSize: 'clamp(40px, 7vw, 84px)', fontWeight: 900, lineHeight: 1.1, letterSpacing: '-0.04em', color: t.ink, wordBreak: 'keep-all', textShadow: t.isDark ? '0 2px 50px rgba(0,145,204,0.4)' : 'none' }}>
            <TextType text={HERO.titleLines.join('\n')} as="span" typingSpeed={46} initialDelay={350} loop={false} showCursor cursorCharacter="_" cursorClassName="text-[#0091CC]" />
          </div>
        </FadeIn>

        <FadeIn delay={0.22}>
          <p style={{ fontFamily: FONT, fontSize: 'clamp(17px, 1.9vw, 22px)', fontWeight: 500, lineHeight: 1.65, color: t.sub, maxWidth: 780, margin: '32px 0 48px', wordBreak: 'keep-all' }}>{HERO.subtitle}</p>
        </FadeIn>

        <FadeIn delay={0.3}>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
            {HERO.ctas.map((cta) => (
              <a key={cta.label} href={cta.href} target="_blank" rel="noopener noreferrer"
                style={{ display: 'inline-flex', alignItems: 'center', padding: '14px 26px', fontFamily: FONT, fontSize: 15, fontWeight: 700, borderRadius: 9999, textDecoration: 'none', transition: 'transform 200ms',
                  ...(cta.primary ? { background: ACCENT, color: '#fff', boxShadow: `0 8px 24px ${ACCENT}59` } : { background: t.isDark ? 'rgba(255,255,255,0.08)' : '#fff', color: t.isDark ? '#fff' : ACCENT, border: `1.5px solid ${t.isDark ? 'rgba(255,255,255,0.24)' : 'rgba(0,145,204,0.3)'}` }) }}
                onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-3px)' }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)' }}>{cta.label}</a>
            ))}
            <AskChip prompt="양건호는 어떤 사람?" t={t} />
          </div>
        </FadeIn>

        <FadeIn delay={0.4}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'clamp(24px, 3.4vw, 52px)', marginTop: 'clamp(56px, 8vh, 88px)', maxWidth: 960, borderTop: `1px solid ${t.line}`, paddingTop: 'clamp(32px, 4vh, 48px)' }}>
            {STATS.map((s) => (
              <div key={s.label}>
                <div style={{ fontFamily: FONT, fontSize: 'clamp(36px, 4.2vw, 50px)', fontWeight: 800, color: t.ink, lineHeight: 0.96, letterSpacing: '-0.035em' }}>
                  <CountUp value={s.value} />{'unit' in s && s.unit && <span style={{ fontSize: '0.42em', fontWeight: 700, marginLeft: 3, color: t.isDark ? BLUE_LIGHT : ACCENT }}>{s.unit}</span>}
                </div>
                <div style={{ fontFamily: FONT, fontSize: 13, color: t.sub, marginTop: 14, fontWeight: 600, lineHeight: 1.45, wordBreak: 'keep-all' }}>{s.label}</div>
              </div>
            ))}
          </div>
        </FadeIn>
      </motion.div>
    </section>
  )
}

// ─────────────────────────────────────────────
// About + STACK 마퀴
// ─────────────────────────────────────────────

function AboutStackSlide({ t }: { t: Theme }) {
  return (
    <section style={{ position: 'absolute', inset: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'flex-start', background: t.sec }}>
      <SectionBg t={t} />
      <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%', padding: 'clamp(72px, 11vh, 128px) clamp(28px, 6vw, 96px) clamp(20px, 3vh, 36px)', position: 'relative', zIndex: 1 }}>
        <Kicker no="01" label="ABOUT · 자기소개" />
        <blockquote style={{ margin: '0 0 clamp(16px,2.2vh,28px)', padding: '16px 24px', borderLeft: `3px solid ${ACCENT}`, background: t.accentSoft, borderRadius: '0 12px 12px 0', fontFamily: FONT, fontSize: 'clamp(15px, 1.7vw, 19px)', fontWeight: 700, lineHeight: 1.48, color: t.ink, letterSpacing: '-0.015em', wordBreak: 'keep-all' }}>
          {NEXON_QUOTE}
          <div style={{ fontSize: 12, fontWeight: 600, color: ACCENT, marginTop: 8 }}>— 넥슨 메이플AX실 채용 공고</div>
        </blockquote>
        <div style={{ maxWidth: 900, display: 'flex', flexDirection: 'column', gap: 'clamp(8px,1.2vh,14px)', marginBottom: 'clamp(16px,2.4vh,28px)' }}>
          {ABOUT.split('\n\n').map((para, i) => (
            <p key={i} style={{ fontFamily: FONT, fontSize: 'clamp(14px,1.35vw,16.5px)', lineHeight: 1.62, color: t.sub, margin: 0, fontWeight: 500, wordBreak: 'keep-all' }}>{para}</p>
          ))}
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {KEY_TRAITS.map((kt) => (
            <span key={kt} style={{ fontFamily: FONT, fontSize: 12.5, fontWeight: 600, color: t.ink, background: t.accentSoft, border: `1px solid ${ACCENT}33`, padding: '7px 13px', borderRadius: 9999, wordBreak: 'keep-all' }}>{kt}</span>
          ))}
        </div>
        <div style={{ marginTop: 'clamp(14px, 2.2vh, 22px)' }}>
          <AskChip prompt="봇 9개월 운영, 어땠어?" t={t} />
        </div>
      </div>
      <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%', padding: '0 clamp(28px, 6vw, 96px) clamp(28px, 4vh, 52px)', position: 'relative', zIndex: 1, marginTop: 'auto' }}>
        <div style={{ background: BAND, borderRadius: 20, padding: 'clamp(20px, 3vh, 34px) 0', overflow: 'hidden' }}>
          <div style={{ padding: '0 clamp(22px, 3vw, 40px)', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 14 }}>
              <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: BLUE_LIGHT, letterSpacing: '0.18em' }}>STACK</span>
              <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.55)', letterSpacing: '0.14em' }}>직접 다루는 기술</span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Marquee items={STACK_A} duration={32} />
            <Marquee items={STACK_B} duration={36} reverse />
          </div>
        </div>
      </div>
    </section>
  )
}

// ─────────────────────────────────────────────
// 가로 카드 스택 (JD 매칭 / 케이스)
// ─────────────────────────────────────────────

function JdCard({ item, t }: { item: { n: number; jdTitle: string; jdSub: string; evidence: readonly string[] }; t: Theme }) {
  return (
    <PanelShell>
      <article style={{ background: t.cardSolid, border: `1px solid ${t.cardBorder}`, borderRadius: 24, boxShadow: t.cardShadow, padding: 'clamp(26px, 3vw, 44px)', backdropFilter: t.isDark ? 'blur(12px)' : undefined }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 'clamp(12px, 2vh, 18px)' }}>
          <span style={{ fontFamily: FONT, fontSize: 'clamp(38px, 4.6vw, 60px)', fontWeight: 800, color: ACCENT, letterSpacing: '-0.05em', lineHeight: 0.9 }}>{String(item.n).padStart(2, '0')}</span>
          <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.2em' }}>JD MATCH</span>
        </div>
        <h3 style={{ fontFamily: FONT, fontSize: 'clamp(19px, 2.4vw, 30px)', fontWeight: 800, lineHeight: 1.24, letterSpacing: '-0.03em', color: t.ink, margin: '0 0 6px', wordBreak: 'keep-all' }}>{item.jdTitle}</h3>
        <p style={{ fontFamily: FONT, fontSize: 'clamp(12.5px, 1.15vw, 14.5px)', color: t.muted, margin: '0 0 clamp(18px, 2.6vh, 28px)', fontWeight: 600, wordBreak: 'keep-all' }}>{item.jdSub}</p>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 'clamp(9px, 1.5vh, 14px)' }}>
          {item.evidence.map((e, i) => (
            <li key={i} style={{ display: 'flex', gap: 12, fontFamily: FONT, fontSize: 'clamp(12px, 1vw, 14px)', lineHeight: 1.6, color: t.sub, fontWeight: 500, wordBreak: 'keep-all', overflowWrap: 'anywhere' }}>
              <span style={{ color: ACCENT, fontWeight: 800, flexShrink: 0 }}>—</span>
              <span>{e}</span>
            </li>
          ))}
        </ul>
      </article>
    </PanelShell>
  )
}

function CasePanel({ item, no, kicker, t }: { item: { title: string; problem: string; approach: string; result: string; bridge: string }; no: number; kicker: string; t: Theme }) {
  const rows = [
    { label: '문제', sub: 'Problem', body: item.problem, c: '#E5615A' },
    { label: '접근', sub: 'Approach', body: item.approach, c: '#F2A93B' },
    { label: '결과', sub: 'Result', body: item.result, c: '#3FAE7E' },
    { label: '넥슨 연결', sub: 'Bridge', body: item.bridge, c: ACCENT },
  ]
  return (
    <PanelShell>
      <article style={{ background: t.cardSolid, border: `1px solid ${t.cardBorder}`, borderRadius: 24, boxShadow: t.cardShadow, padding: 'clamp(28px, 3vw, 48px)', backdropFilter: t.isDark ? 'blur(12px)' : undefined }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 'clamp(14px, 2.2vh, 24px)' }}>
          <span style={{ fontFamily: FONT, fontSize: 'clamp(40px, 5vw, 64px)', fontWeight: 800, color: ACCENT, letterSpacing: '-0.05em', lineHeight: 0.9 }}>{String(no).padStart(2, '0')}</span>
          <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.2em' }}>{kicker}</span>
        </div>
        <h3 style={{ fontFamily: FONT, fontSize: 'clamp(21px, 2.7vw, 34px)', fontWeight: 800, lineHeight: 1.22, letterSpacing: '-0.03em', color: t.ink, margin: '0 0 clamp(22px, 3.2vh, 40px)', wordBreak: 'keep-all' }}>{item.title}</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'clamp(20px, 2.4vw, 36px)' }}>
          {rows.map((r) => (
            <div key={r.label} style={{ paddingTop: 13, borderTop: `2px solid ${r.c}` }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 10 }}>
                <span style={{ fontFamily: FONT, fontSize: 15.5, fontWeight: 800, color: r.c, letterSpacing: '-0.01em' }}>{r.label}</span>
                <span style={{ fontFamily: FONT, fontSize: 9.5, fontWeight: 700, color: t.muted, letterSpacing: '0.18em', textTransform: 'uppercase' }}>{r.sub}</span>
              </div>
              <p style={{ fontFamily: FONT, fontSize: 'clamp(12.5px, 1vw, 14px)', lineHeight: 1.72, color: t.sub, margin: 0, fontWeight: 500, wordBreak: 'keep-all', overflowWrap: 'anywhere' }}>{r.body}</p>
            </div>
          ))}
        </div>
      </article>
    </PanelShell>
  )
}

// 오른쪽에서 들어와 가운데 핀 → 왼쪽으로 scale 줄며 쌓인다.
function HStackCard({ index, progress, children }: { index: number; progress: number; children: React.ReactNode }) {
  const dist = index - progress
  const x = dist > 1 ? 108 : dist >= 0 ? dist * 100 : dist * 5
  const scale = Math.max(0.84, 1 - Math.max(0, progress - index) * 0.06)
  const opacity = dist > 1.04 ? 0 : dist < 0 ? Math.max(0.28, 1 + dist * 0.62) : 1
  return <div style={{ position: 'absolute', inset: 0, transform: `translateX(${x}%) scale(${scale})`, opacity, zIndex: index, willChange: 'transform, opacity', transition: 'transform 300ms cubic-bezier(0.33,1,0.68,1), opacity 280ms ease' }}>{children}</div>
}

function StackDots({ total, progress, t }: { total: number; progress: number; t: Theme }) {
  const active = Math.round(progress)
  return (
    <div style={{ position: 'absolute', bottom: 'clamp(20px, 4vh, 40px)', left: '50%', transform: 'translateX(-50%)', display: 'flex', gap: 7, zIndex: 30 }}>
      {Array.from({ length: total }).map((_, i) => (
        <span key={i} aria-hidden style={{ width: active === i ? 26 : 8, height: 8, borderRadius: 9999, background: active === i ? ACCENT : t.line, display: 'block', transition: 'all 250ms ease' }} />
      ))}
    </div>
  )
}

// 카드 배열을 가로 스택으로. 휠 1회 = 카드 1단계(subProgress).
function CardStackSlide({ cards, subProgress, bg, t, bgVariant = 'aurora-blue' }: { cards: React.ReactNode[]; subProgress: number; bg: string; t: Theme; bgVariant?: BgVariant }) {
  return (
    <div style={{ position: 'absolute', inset: 0, background: bg, overflow: 'hidden' }}>
      <SectionBg t={t} variant={bgVariant} />
      <div style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
        {cards.map((node, i) => (
          <HStackCard key={i} index={i} progress={subProgress}>{node}</HStackCard>
        ))}
      </div>
      <StackDots total={cards.length} progress={subProgress} t={t} />
    </div>
  )
}

// ─────────────────────────────────────────────
// 자격 · 우대
// ─────────────────────────────────────────────

function FitSlide({ t }: { t: Theme }) {
  return (
    <SlidePane bg={t.sec} t={t} center={false} bgVariant="aurora-blue">
      <SectionHeader no="05" kicker="FIT · 자격 · 우대" title={'지원 자격은 이미 매일 굴리는 도구입니다'} t={t} />
      <div style={{ display: 'grid', gap: 'clamp(18px, 3vh, 32px)' }}>
        <FadeIn>
          <div style={{ background: t.cardSolid, border: `1px solid ${t.cardBorder}`, borderRadius: 20, padding: 'clamp(22px, 2.6vw, 36px)', boxShadow: t.cardShadow, backdropFilter: t.isDark ? 'blur(12px)' : undefined }}>
            <div style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.18em', marginBottom: 12 }}>지원 자격</div>
            <div style={{ fontFamily: FONT, fontSize: 'clamp(17px, 1.9vw, 23px)', fontWeight: 800, color: t.ink, marginBottom: 12, letterSpacing: '-0.02em', wordBreak: 'keep-all' }}>{ELIGIBILITY.headline}</div>
            <p style={{ fontFamily: FONT, fontSize: 'clamp(13px, 1.15vw, 15px)', lineHeight: 1.68, color: t.sub, margin: 0, fontWeight: 500, wordBreak: 'keep-all' }}>{ELIGIBILITY.body}</p>
          </div>
        </FadeIn>
        <div>
          <div style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.18em', marginBottom: 14 }}>우대 사항</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
            {PREFERRED.map((p, i) => (
              <FadeIn key={p.jdTitle} delay={i * 0.06}>
                <div style={{ height: '100%', background: t.card, border: `1px solid ${t.cardBorder}`, borderRadius: 16, padding: 'clamp(18px, 2vw, 26px)', borderTop: `2px solid ${ACCENT}` }}>
                  <div style={{ fontFamily: FONT, fontSize: 'clamp(14px, 1.3vw, 16px)', fontWeight: 800, color: t.ink, marginBottom: 10, letterSpacing: '-0.01em', wordBreak: 'keep-all' }}>{p.jdTitle}</div>
                  <p style={{ fontFamily: FONT, fontSize: 'clamp(12px, 1vw, 13.5px)', lineHeight: 1.62, color: t.sub, margin: 0, fontWeight: 500, wordBreak: 'keep-all' }}>{p.evidence}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
        <div>
          <AskChip prompt="지원 자격 충족돼?" t={t} />
        </div>
      </div>
    </SlidePane>
  )
}

// ─────────────────────────────────────────────
// 02 ARCHITECTURE / 03 STACK / 06 GAMES — 복원 번호 섹션
// ─────────────────────────────────────────────

// 02 — content SSoT 파이프라인 5단계를 가로 스텝 플로우로. 노드 사이 화살표.
function ArchitectureSlide({ t }: { t: Theme }) {
  return (
    <SlidePane bg={t.secAlt} t={t} center={false} bgVariant="shapes-flip">
      <SectionHeader no="02" kicker="ARCHITECTURE · 이 페이지의 파이프라인" title={'스크롤부터 3D까지, 한 프레임 루프로'} t={t} />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'clamp(10px, 1.4vw, 16px)', rowGap: 'clamp(14px, 2vh, 22px)' }}>
        {ARCHITECTURE.steps.map((s, i) => (
          <FadeIn key={s.n} delay={i * 0.08}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'clamp(10px, 1.4vw, 16px)' }}>
              <div style={{ width: 'clamp(166px, 15vw, 212px)', background: t.cardSolid, border: `1px solid ${t.cardBorder}`, borderRadius: 18, padding: 'clamp(16px, 1.6vw, 22px)', boxShadow: t.cardShadow, backdropFilter: t.isDark ? 'blur(12px)' : undefined }}>
                <div style={{ fontFamily: FONT, fontSize: 'clamp(26px, 2.6vw, 36px)', fontWeight: 800, color: ACCENT, letterSpacing: '-0.04em', lineHeight: 0.9, marginBottom: 12 }}>{String(s.n).padStart(2, '0')}</div>
                <div style={{ fontFamily: FONT, fontSize: 'clamp(14px, 1.2vw, 16px)', fontWeight: 800, color: t.ink, marginBottom: 8, letterSpacing: '-0.01em', wordBreak: 'keep-all' }}>{s.label}</div>
                <p style={{ fontFamily: FONT, fontSize: 'clamp(11.5px, 0.95vw, 13px)', lineHeight: 1.55, color: t.sub, margin: '0 0 10px', fontWeight: 500, wordBreak: 'keep-all' }}>{s.desc}</p>
                <div style={{ fontFamily: FONT, fontSize: 10.5, fontWeight: 700, color: t.isDark ? BLUE_LIGHT : ACCENT, letterSpacing: '0.04em', wordBreak: 'keep-all' }}>{s.cost}</div>
              </div>
              {i < ARCHITECTURE.steps.length - 1 && (
                <span aria-hidden style={{ color: t.muted, fontSize: 18, fontWeight: 700, flexShrink: 0 }}>→</span>
              )}
            </div>
          </FadeIn>
        ))}
      </div>
      <div style={{ marginTop: 'clamp(20px, 3vh, 34px)' }}>
        <AskChip prompt="이 페이지 어떻게 만들었어?" t={t} />
      </div>
    </SlidePane>
  )
}

// 03 — 카테고리별 스택을 번호 매긴 매거진 리스트로. 8행 stagger.
function StackDetailSlide({ t }: { t: Theme }) {
  return (
    <SlidePane bg={t.sec} t={t} center={false} bgVariant="aurora-violet">
      <SectionHeader no="03" kicker="STACK · 직접 다루는 기술" title={'이 화면을 굴리는 전체 스택'} t={t} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', columnGap: 'clamp(28px, 4vw, 60px)' }}>
        {STACK_DETAIL.map((item, i) => (
          <FadeIn key={item.category} delay={i * 0.04}>
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(42px, 54px) 1fr', gap: 'clamp(12px, 1.4vw, 20px)', padding: 'clamp(11px, 1.5vh, 16px) 0', borderTop: `1px solid ${t.line}`, alignItems: 'baseline' }}>
              <span style={{ fontFamily: FONT, fontSize: 'clamp(20px, 2.2vw, 28px)', fontWeight: 800, color: t.isDark ? 'rgba(255,255,255,0.22)' : 'rgba(10,18,36,0.18)', letterSpacing: '-0.04em', lineHeight: 1 }}>{String(i + 1).padStart(2, '0')}</span>
              <div>
                <div style={{ fontFamily: FONT, fontSize: 10, fontWeight: 800, color: ACCENT, letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 5 }}>{item.category}</div>
                <div style={{ fontFamily: FONT, fontSize: 'clamp(13px, 1.2vw, 15.5px)', fontWeight: 700, color: t.ink, lineHeight: 1.38, letterSpacing: '-0.01em', wordBreak: 'keep-all', marginBottom: 8 }}>{item.headline}</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                  {item.chips.map((c) => (
                    <span key={c} style={{ fontFamily: FONT, fontSize: 10.5, fontWeight: 600, color: t.sub, background: t.card, border: `1px solid ${t.cardBorder}`, padding: '3px 8px', borderRadius: 9999 }}>{c}</span>
                  ))}
                </div>
              </div>
            </div>
          </FadeIn>
        ))}
      </div>
    </SlidePane>
  )
}

// 06 — 넥슨 IP 중심 게임 이력. 번호 리스트, 첫 행(메이플) 강조.
function GamesSlide({ t }: { t: Theme }) {
  return (
    <SlidePane bg={t.secAlt} t={t} center={false} bgVariant="shapes-flip">
      <SectionHeader no="06" kicker="GAMES · 넥슨 IP 경험" title={'플레이어로 쌓은 게임 도메인 이해'} t={t} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'clamp(10px, 1.5vh, 16px)' }}>
        {GAMES.map((g, i) => (
          <FadeIn key={g.title} delay={i * 0.06}>
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(44px, 58px) minmax(116px, 188px) 1fr', gap: 'clamp(12px, 2vw, 24px)', alignItems: 'baseline', padding: 'clamp(15px, 2vh, 21px) clamp(18px, 2vw, 26px)', background: i === 0 ? t.accentSoft : t.card, border: i === 0 ? `1.5px solid ${ACCENT}66` : `1px solid ${t.cardBorder}`, borderRadius: 16 }}>
              <span style={{ fontFamily: FONT, fontSize: 'clamp(20px, 2.2vw, 28px)', fontWeight: 800, color: ACCENT, letterSpacing: '-0.04em', lineHeight: 1 }}>{String(i + 1).padStart(2, '0')}</span>
              <div>
                <div style={{ fontFamily: FONT, fontSize: 'clamp(15px, 1.5vw, 19px)', fontWeight: 800, color: t.ink, letterSpacing: '-0.02em', wordBreak: 'keep-all' }}>{g.title}</div>
                <div style={{ fontFamily: FONT, fontSize: 12, fontWeight: 600, color: t.isDark ? BLUE_LIGHT : ACCENT, marginTop: 4 }}>{g.period}</div>
              </div>
              <p style={{ fontFamily: FONT, fontSize: 'clamp(12.5px, 1.1vw, 14.5px)', lineHeight: 1.6, color: t.sub, margin: 0, fontWeight: 500, wordBreak: 'keep-all' }}>{g.detail}</p>
            </div>
          </FadeIn>
        ))}
      </div>
      <div style={{ marginTop: 'clamp(18px, 2.6vh, 30px)' }}>
        <AskChip prompt="메이플 어디까지 했어?" t={t} />
      </div>
    </SlidePane>
  )
}

// ─────────────────────────────────────────────
// Closing + Footer
// ─────────────────────────────────────────────

function NexonFooter() {
  const links = [
    { label: 'Email', value: CONTACT.email, href: `mailto:${CONTACT.email}` },
    { label: 'GitHub', value: 'github.com/2rami', href: CONTACT.github },
    { label: 'Live', value: 'debimarlene.com', href: CONTACT.domain },
  ]
  return (
    <footer style={{ position: 'relative', background: BAND, color: '#fff', overflow: 'hidden' }}>
      <div style={{ padding: 'clamp(64px, 9vh, 110px) clamp(28px, 6vw, 96px) clamp(44px, 6vh, 72px)' }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%' }}>
          <div style={{ fontFamily: FONT, fontSize: 'clamp(34px, 5.4vw, 68px)', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.18, wordBreak: 'keep-all' }}>생성형 AI 제작 도구를<br /><span style={{ color: BLUE_LIGHT }}>브라우저에서 끝까지 만드는 사람</span>이 되고 싶습니다.</div>
        </div>
      </div>
      <div style={{ height: 1, background: 'rgba(255,255,255,0.2)', width: '100%' }} />
      <div style={{ padding: 'clamp(28px, 4vh, 44px) clamp(28px, 6vw, 96px) clamp(36px, 5vh, 56px)' }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 20 }}>
            {links.map((l) => (
              <a key={l.label} href={l.href} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
                <div style={{ fontFamily: FONT, fontSize: 11, color: BLUE_LIGHT, letterSpacing: '0.16em', fontWeight: 700, marginBottom: 8 }}>{l.label.toUpperCase()}</div>
                <div style={{ fontFamily: FONT, fontSize: 16, color: '#fff', fontWeight: 600 }}>{l.value}</div>
              </a>
            ))}
          </div>
          <div style={{ fontFamily: FONT, fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 36 }}>양건호 (Geonho Yang) · 2026 · NEXON 메이플AX실 웹 프론트엔드 엔지니어 인턴 지원</div>
        </div>
      </div>
    </footer>
  )
}

function ClosingFooterSlide({ t }: { t: Theme }) {
  return (
    <div style={{ background: t.secAlt }}>
      <section style={{ minHeight: '100vh', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 'clamp(48px, 6vw, 96px)' }}>
        <SectionBg t={t} variant="ballpit" />
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
          <Kicker label="CLOSING" />
          <div style={{ fontFamily: FONT, fontSize: 'clamp(28px, 4.6vw, 58px)', fontWeight: 800, lineHeight: 1.24, letterSpacing: '-0.035em', color: t.ink, wordBreak: 'keep-all' }}>
            <TextType text={'AI 제작 도구를 브라우저에서 끝까지 만드는 프론트엔드가 되겠습니다.'} as="span" typingSpeed={45} initialDelay={300} loop={false} showCursor cursorCharacter="_" startOnVisible cursorClassName="text-[#0091CC]" />
          </div>
          <p style={{ fontFamily: FONT, fontSize: 'clamp(15px, 1.7vw, 20px)', fontWeight: 500, lineHeight: 1.65, color: t.sub, margin: 'clamp(24px, 3.6vh, 44px) 0 0', maxWidth: 720, wordBreak: 'keep-all' }}>메이플AX실이 지향하는 방향은, 제가 이미 손으로 만들어 온 것과 같습니다.</p>
          <div style={{ marginTop: 'clamp(24px, 3.6vh, 40px)' }}>
            <AskChip prompt="왜 넥슨 지원했어?" t={t} />
          </div>
          <div style={{ marginTop: 'clamp(28px, 4vh, 48px)', display: 'flex', alignItems: 'center', gap: 10, color: t.muted, fontFamily: FONT, fontSize: 12.5, fontWeight: 600 }}>
            <span>아래로 스크롤</span>
            <motion.span animate={{ y: [0, 5, 0] }} transition={{ duration: 1.5, repeat: Infinity }}>↓</motion.span>
          </div>
        </div>
      </section>
      <NexonFooter />
    </div>
  )
}

// ─────────────────────────────────────────────
// 페이지
// ─────────────────────────────────────────────

export default function PageFrontendDeck() {
  const [isDark, setIsDark] = useState(false) // 라이트모드가 기본
  const t = makeTheme(isDark)

  useEffect(() => {
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    window.scrollTo(0, 0)
    return () => { document.body.style.overflow = prevOverflow }
  }, [])

  // 슬라이드가 바뀌면 그 섹션 대사를 캐릭터 말풍선으로 — 스크롤 없는 덱의 상호작용 보강
  const handleIndexChange = useCallback((i: number) => {
    const text = SECTION_BUBBLES[i]
    if (text) window.dispatchEvent(new CustomEvent('nexon:char-say', { detail: { text } }))
  }, [])

  const jdCards = JD_MATCHES.map((jd) => <JdCard key={jd.n} item={jd} t={t} />)
  const caseCards = CASES.map((c) => <CasePanel key={c.no} item={c} no={c.no} kicker="CASE" t={t} />)

  const slides: Slide[] = [
    { node: <Hero t={t} /> },
    {
      node: (
        <Statement
          kicker="MANIFESTO"
          text={'디자인 설계와 프론트엔드 구현을\n한 사람이 합니다.'}
          sub="화면을 그리는 데서 멈추지 않고 Rust로 GPU 터미널까지 직접 짰습니다. 브라우저에서 시각 요소를 편집하고 실시간으로 협업하는 제작 도구 — 이미 만들어 온 방향입니다."
          bg={t.secAlt}
          t={t}
          bgVariant="shapes"
        />
      ),
    },
    { node: <AboutStackSlide t={t} /> },
    { node: <ArchitectureSlide t={t} /> },
    { node: <StackDetailSlide t={t} /> },
    { render: (sub) => <CardStackSlide cards={jdCards} subProgress={sub} bg={t.sec} t={t} bgVariant="shapes" />, substeps: JD_MATCHES.length - 1 },
    { node: <FitSlide t={t} /> },
    { node: <GamesSlide t={t} /> },
    { render: (sub) => <CardStackSlide cards={caseCards} subProgress={sub} bg={t.secAlt} t={t} bgVariant="aurora-violet" />, substeps: CASES.length - 1 },
    { node: <ClosingFooterSlide t={t} />, scroll: true },
  ]

  return (
    <div style={{ fontFamily: FONT, color: t.ink, letterSpacing: '-0.01em', background: t.pageBg, minHeight: '100vh', overflowX: 'clip' }}>
      <ThemeToggle isDark={isDark} toggle={() => setIsDark((v) => !v)} />
      <MapleChatbot roam={false} intro="안녕하세요, 디지털 클론 양건호입니다. 롯데월드 메이플 콜라보 때 전광판 타워에서 QR로 소환됐던 캐릭터처럼, 우측 아래에서 대기 중이에요. 프론트엔드나 kasaterm, 뭐든 물어보세요." />
      <SlideDeck slides={slides} accent={ACCENT} onIndexChange={handleIndexChange} />
    </div>
  )
}
