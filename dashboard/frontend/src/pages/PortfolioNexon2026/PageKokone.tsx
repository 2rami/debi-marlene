/**
 * 코코네 · [Cocone Internship] AI Engineer — 지원용 포트폴리오
 * 라우트: /portfolio/kokone
 *
 * 다크/라이트 토글(좌하단 버튼) — 페이지 로컬 테마. 기본 다크.
 * makeTheme(isDark)로 전 섹션 색을 분기. 마퀴·Footer는 강조 밴드(항상 다크 플럼).
 * 브랜드 액센트 = 핑크/마젠타(아바타·메타버스 톤). 사이오닉(블루) 포크.
 *
 * 구조: Hero → MANIFESTO → About(+핵심역량 칩) → STACK 마퀴 →
 *   PROJECT 01 AI 모델 파이프라인(debi) / 02 AI 어시스턴트·하네스(kasa) → BUILDS → Closing/Footer
 * 포폴 프레임: ① AI로 구현한 프로젝트 ② AI 연구 결과물 (코코네 포폴 요건).
 */

import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion, useScroll, useTransform, animate } from 'framer-motion'
import Aurora from '../../components/common/Aurora'
import Ballpit from '../../components/common/Ballpit'
import BlurText from '../../components/common/BlurText'
import SlideDeck, { type Slide } from './shared/SlideDeck'
import LiveServersMarquee from './shared/LiveServersMarquee'
import shotDashboard from '../../assets/images/event/screenshot_dashboard.png'
import shotWebpanel from '../../assets/images/event/screenshot_webpanel.png'
import shotTts from '../../assets/images/event/screenshot_tts_settings.png'
import shotAiChat from '../../assets/images/event/screenshot_ai_chat.png'
import shotKasatermGui from '../../assets/images/event/kasaterm-schale-os.png'
import KokoneChatbot from './shared/KokoneChatbot'
import {
  HERO,
  QUOTE,
  MANIFESTO,
  STATS,
  ABOUT,
  STACK,
  KEY_TRAITS,
  CASES,
  PROJECTS,
  PROJECT_DEBI,
  PROJECT_KASA,
  CONTACT,
  ACCENT,
} from './content/kokone'

const FONT = "'Pretendard Variable', 'Pretendard', 'Paperlogy', -apple-system, BlinkMacSystemFont, sans-serif"
const PINK_LIGHT = '#FF8FC0' // 강조 보조(밝은 핑크)
const BAND = '#1C0816' // 마퀴·Footer 강조 밴드 (모드 무관 다크 플럼)

// ─────────────────────────────────────────────
// 테마
// ─────────────────────────────────────────────

function makeTheme(isDark: boolean) {
  return {
    isDark,
    pageBg: isDark ? '#120410' : '#FFF5FA',
    sec: isDark ? '#1A0715' : '#FFFFFF',
    secAlt: isDark ? '#13040F' : '#FFF5FA',
    ink: isDark ? '#FFFFFF' : '#1A0614',
    sub: isDark ? 'rgba(255,255,255,0.68)' : '#5F3F50',
    muted: isDark ? 'rgba(255,255,255,0.5)' : '#A6889A',
    card: isDark ? 'rgba(255,255,255,0.05)' : '#FFFFFF',
    cardSolid: isDark ? '#2A0E22' : '#FFFFFF',
    cardBorder: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(26,6,20,0.08)',
    cardShadow: isDark ? '0 24px 60px -16px rgba(0,0,0,0.5)' : '0 24px 60px -16px rgba(26,6,20,0.16)',
    accentSoft: isDark ? 'rgba(255,46,136,0.16)' : '#FFE7F1',
    line: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(26,6,20,0.1)',
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
        border: `1px solid ${isDark ? 'rgba(255,255,255,0.22)' : 'rgba(26,6,20,0.12)'}`,
        background: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.92)',
        backdropFilter: 'blur(10px)', boxShadow: '0 8px 24px rgba(0,0,0,0.22)', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: isDark ? '#FFD166' : '#1A0614', transition: 'all 200ms',
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
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: PINK_LIGHT, flexShrink: 0 }} />
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

// 섹션 공통 Aurora 배경 (은은하게)
function SectionBg({ t }: { t: Theme }) {
  return (
    <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 0, opacity: t.isDark ? 0.34 : 0.22 }}>
      <Aurora colorStops={[ACCENT, PINK_LIGHT, '#FFC2DD']} amplitude={1.0} speed={0.35} />
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
function Statement({ text, sub, kicker, bg, t }: { text: string; sub?: string; kicker: string; bg: string; t: Theme }) {
  return (
    <section style={{ position: 'absolute', inset: 0, padding: 'clamp(48px, 6vw, 96px)', background: bg, overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <SectionBg t={t} />
      <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 'clamp(26px, 4.2vh, 48px)' }}>
          <span style={{ width: 24, height: 1, background: ACCENT }} />
          <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.24em' }}>{kicker}</span>
        </div>
        <div style={{ fontFamily: FONT, fontSize: 'clamp(28px, 4.6vw, 58px)', fontWeight: 800, lineHeight: 1.24, letterSpacing: '-0.035em', color: t.ink, wordBreak: 'keep-all' }}>
          <BlurText text={text} delay={55} animateBy="words" direction="bottom" className="!m-0" />
        </div>
        {sub && (
          <p style={{ fontFamily: FONT, fontSize: 'clamp(15px, 1.7vw, 20px)', fontWeight: 500, lineHeight: 1.65, color: t.sub, margin: 'clamp(24px, 3.6vh, 44px) 0 0', maxWidth: 720, wordBreak: 'keep-all' }}>{sub}</p>
        )}
      </div>
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
    ? 'radial-gradient(125% 95% at 50% 0%, #3A0E2A 0%, #1A0716 55%, #0C040A 100%)'
    : 'radial-gradient(125% 95% at 50% 0%, #FFE0EF 0%, #FFF5FA 58%, #FFF5FA 100%)'

  return (
    <section ref={heroRef} style={{ position: 'absolute', inset: 0, padding: 'clamp(36px, 5vw, 56px) clamp(28px, 6vw, 48px)', overflow: 'hidden', background: heroBg, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div className="absolute inset-0" style={{ zIndex: 0, opacity: t.isDark ? 0.85 : 0.7 }}>
        <Ballpit
          count={90}
          gravity={0.35}
          friction={0.9975}
          wallBounce={0.95}
          followCursor
          colors={t.isDark ? [0xff2e88, 0xff8fc0, 0xffc2dd] : [0xff5fa2, 0xffa6cd, 0xffe0ef]}
          ambientColor={t.isDark ? 0xff8fc0 : 0xffffff}
          ambientIntensity={t.isDark ? 1.1 : 1.4}
          lightIntensity={180}
          minSize={0.6}
          maxSize={1.3}
        />
      </div>

      <header style={{ position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', maxWidth: 1180, margin: '0 auto', paddingBottom: 24, borderBottom: `1px solid ${t.line}`, color: t.isDark ? PINK_LIGHT : ACCENT, flexWrap: 'wrap', gap: 16 }}>
        <span style={{ fontFamily: FONT, fontSize: 11, letterSpacing: '0.12em', opacity: 0.9, fontWeight: 700 }}>PORTFOLIO · {HERO.jobCode}</span>
        <span style={{ fontFamily: FONT, fontSize: 11, letterSpacing: '0.08em', opacity: 0.9, fontWeight: 700 }}>YANG · GEONHO / 2026</span>
      </header>

      <motion.div style={{ y: textY, maxWidth: 1180, margin: '0 auto', position: 'relative', zIndex: 1, paddingTop: 88, paddingBottom: 56 }}>
        <FadeIn delay={0}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10, marginBottom: 36, fontFamily: FONT, fontSize: 12.5, fontWeight: 700, color: t.isDark ? PINK_LIGHT : ACCENT, letterSpacing: '0.03em' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: ACCENT, boxShadow: `0 0 0 4px ${ACCENT}28` }} />
            {HERO.badge}
          </div>
        </FadeIn>

        <FadeIn delay={0.15}>
          <div style={{ fontFamily: FONT, fontSize: 'clamp(44px, 8vw, 96px)', fontWeight: 900, lineHeight: 1.08, letterSpacing: '-0.04em', color: t.ink, wordBreak: 'keep-all', textShadow: t.isDark ? '0 2px 50px rgba(255,46,136,0.4)' : 'none' }}>
            {HERO.title.split('\n').map((line, i) => (
              <BlurText key={i} text={line} delay={90} animateBy="words" direction="bottom" className="!m-0" />
            ))}
          </div>
        </FadeIn>

        <FadeIn delay={0.22}>
          <p style={{ fontFamily: FONT, fontSize: 'clamp(17px, 1.9vw, 22px)', fontWeight: 500, lineHeight: 1.65, color: t.sub, maxWidth: 780, margin: '32px 0 48px', wordBreak: 'keep-all' }}>{HERO.subtitle}</p>
        </FadeIn>

        <FadeIn delay={0.3}>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {HERO.ctas.map((cta) => (
              <a key={cta.label} href={cta.href} target="_blank" rel="noopener noreferrer"
                style={{ display: 'inline-flex', alignItems: 'center', padding: '14px 26px', fontFamily: FONT, fontSize: 15, fontWeight: 700, borderRadius: 9999, textDecoration: 'none', transition: 'transform 200ms',
                  ...(cta.primary ? { background: ACCENT, color: '#fff', boxShadow: `0 8px 24px ${ACCENT}59` } : { background: t.isDark ? 'rgba(255,255,255,0.08)' : '#fff', color: t.isDark ? '#fff' : ACCENT, border: `1.5px solid ${t.isDark ? 'rgba(255,255,255,0.24)' : 'rgba(255,46,136,0.3)'}` }) }}
                onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-3px)' }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)' }}>{cta.label}</a>
            ))}
          </div>
        </FadeIn>

        <FadeIn delay={0.4}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'clamp(24px, 3.4vw, 52px)', marginTop: 'clamp(56px, 8vh, 88px)', maxWidth: 960, borderTop: `1px solid ${t.line}`, paddingTop: 'clamp(32px, 4vh, 48px)' }}>
            {STATS.map((s) => (
              <div key={s.label}>
                <div style={{ fontFamily: FONT, fontSize: 'clamp(36px, 4.2vw, 50px)', fontWeight: 800, color: t.ink, lineHeight: 0.96, letterSpacing: '-0.035em' }}>
                  <CountUp value={s.value} />{'unit' in s && s.unit && <span style={{ fontSize: '0.42em', fontWeight: 700, marginLeft: 3, color: t.isDark ? PINK_LIGHT : ACCENT }}>{s.unit}</span>}
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
// 프로젝트 헤더 / 스샷 / GUI WIP
// ─────────────────────────────────────────────

function ProjectHeader({ no, tag, title, tagline, repo, live, stats, t }: { no: string; tag: string; title: string; tagline: string; repo: string; live: string; stats: readonly { value: string; unit: string; label: string }[]; t: Theme }) {
  return (
    <div style={{ marginBottom: 56 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 22 }}>
        <span style={{ fontFamily: FONT, fontSize: 'clamp(40px,5vw,58px)', fontWeight: 800, color: ACCENT, lineHeight: 1, letterSpacing: '-0.04em' }}>{no}</span>
        <span style={{ fontFamily: FONT, fontSize: 12, fontWeight: 700, color: ACCENT, background: t.accentSoft, padding: '6px 14px', borderRadius: 9999 }}>{tag}</span>
      </div>
      <div style={{ fontFamily: FONT, fontSize: 'clamp(34px,5.4vw,58px)', fontWeight: 900, lineHeight: 1.08, letterSpacing: '-0.03em', color: t.ink, marginBottom: 22, wordBreak: 'keep-all' }}>
        {title.split('\n').map((line, i) => (<BlurText key={i} text={line} delay={80} animateBy="words" direction="bottom" className="!m-0" />))}
      </div>
      <p style={{ fontFamily: FONT, fontSize: 'clamp(16px,1.8vw,19px)', fontWeight: 500, lineHeight: 1.7, color: t.sub, maxWidth: 740, margin: '0 0 28px', wordBreak: 'keep-all' }}>{tagline}</p>
      <div style={{ display: 'flex', gap: 12, marginBottom: 40, flexWrap: 'wrap' }}>
        <a href={repo} target="_blank" rel="noopener noreferrer" style={{ fontFamily: FONT, fontSize: 14, fontWeight: 700, color: t.ink, textDecoration: 'none', padding: '10px 18px', borderRadius: 9999, border: `1.5px solid ${t.cardBorder}` }}>GitHub →</a>
        {live && <a href={live} target="_blank" rel="noopener noreferrer" style={{ fontFamily: FONT, fontSize: 14, fontWeight: 700, color: '#fff', textDecoration: 'none', padding: '10px 18px', borderRadius: 9999, background: ACCENT }}>Live →</a>}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 14, maxWidth: 640 }}>
        {stats.map((s) => (
          <div key={s.label} style={{ borderLeft: `2px solid ${ACCENT}`, paddingLeft: 16 }}>
            <div style={{ fontFamily: FONT, fontSize: 28, fontWeight: 800, color: t.ink, lineHeight: 1, letterSpacing: '-0.02em' }}><CountUp value={s.value} /><span style={{ fontSize: '0.5em', marginLeft: 3, color: ACCENT }}>{s.unit}</span></div>
            <div style={{ fontFamily: FONT, fontSize: 12.5, color: t.muted, marginTop: 7, fontWeight: 600, wordBreak: 'keep-all' }}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function GuiWip({ gui, t }: { gui: { title: string; body: string }; t: Theme }) {
  return (
    <div style={{ display: 'grid', gap: 'clamp(22px, 3vh, 38px)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.05fr)', gap: 'clamp(24px, 4vw, 56px)', alignItems: 'end' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 9, marginBottom: 16 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: ACCENT, boxShadow: `0 0 0 4px ${ACCENT}33` }} />
            <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.18em' }}>IN PROGRESS</span>
          </div>
          <h3 style={{ fontFamily: FONT, fontSize: 'clamp(24px,3vw,38px)', fontWeight: 800, color: t.ink, margin: 0, letterSpacing: '-0.025em', wordBreak: 'keep-all', lineHeight: 1.2 }}>{gui.title}</h3>
        </div>
        <p style={{ fontFamily: FONT, fontSize: 'clamp(13.5px,1.2vw,15.5px)', lineHeight: 1.68, color: t.sub, margin: 0, fontWeight: 500, wordBreak: 'keep-all' }}>{gui.body}</p>
      </div>
      <figure style={{ margin: 0 }}>
        <img src={shotKasatermGui} alt="kasaterm SCHALE OS" loading="lazy" style={{ maxWidth: '100%', maxHeight: '56vh', width: 'auto', height: 'auto', display: 'block', margin: '0 auto', borderRadius: 14, border: `1px solid ${t.cardBorder}`, boxShadow: t.cardShadow }} />
        <figcaption style={{ fontFamily: FONT, fontSize: 12, fontWeight: 600, color: t.sub, marginTop: 12, wordBreak: 'keep-all' }}>SCHALE OS — AI 토큰·컨텍스트·서브에이전트를 게임 UI로 시각화</figcaption>
      </figure>
    </div>
  )
}

function ProjectCard({ name, desc, tags, repo, live, t }: { name: string; desc: string; tags: readonly string[]; repo: string; live: string; t: Theme }) {
  return (
    <article style={{ background: t.card, borderRadius: 20, border: `1px solid ${t.cardBorder}`, boxShadow: t.cardShadow, padding: 28, display: 'flex', flexDirection: 'column', gap: 16, height: '100%', backdropFilter: t.isDark ? 'blur(12px)' : undefined }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ width: 9, height: 9, borderRadius: '50%', background: ACCENT }} />
        <h3 style={{ fontFamily: FONT, fontSize: 20, fontWeight: 800, color: t.ink, margin: 0, letterSpacing: '-0.01em' }}>{name}</h3>
      </div>
      <p style={{ fontFamily: FONT, fontSize: 14.5, lineHeight: 1.65, color: t.sub, margin: 0, flex: 1, wordBreak: 'keep-all' }}>{desc}</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7 }}>
        {tags.map((tg) => (<span key={tg} style={{ fontFamily: FONT, fontSize: 12, fontWeight: 600, color: ACCENT, background: t.accentSoft, padding: '5px 11px', borderRadius: 8 }}>{tg}</span>))}
      </div>
      <div style={{ display: 'flex', gap: 16, borderTop: `1px solid ${t.cardBorder}`, paddingTop: 16 }}>
        <a href={repo} target="_blank" rel="noopener noreferrer" style={{ fontFamily: FONT, fontSize: 13.5, fontWeight: 700, color: t.ink, textDecoration: 'none' }}>GitHub →</a>
        {live && <a href={live} target="_blank" rel="noopener noreferrer" style={{ fontFamily: FONT, fontSize: 13.5, fontWeight: 700, color: ACCENT, textDecoration: 'none' }}>Live →</a>}
      </div>
    </article>
  )
}

function KokoneFooter() {
  const links = [
    { label: 'Email', value: CONTACT.email, href: `mailto:${CONTACT.email}` },
    { label: 'GitHub', value: 'github.com/2rami', href: CONTACT.github },
    { label: 'Live', value: 'debimarlene.com', href: CONTACT.domain },
  ]
  return (
    <footer style={{ position: 'relative', background: BAND, color: '#fff', overflow: 'hidden' }}>
      <div style={{ padding: 'clamp(64px, 9vh, 110px) clamp(28px, 6vw, 96px) clamp(44px, 6vh, 72px)' }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%' }}>
          <div style={{ fontFamily: FONT, fontSize: 'clamp(36px, 5.8vw, 72px)', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.16, wordBreak: 'keep-all' }}>AI로 캐릭터에 생명을 불어넣는<br /><span style={{ color: PINK_LIGHT }}>엔지니어</span>가 되고 싶습니다.</div>
        </div>
      </div>
      <div style={{ height: 1, background: 'rgba(255,255,255,0.2)', width: '100%' }} />
      <div style={{ padding: 'clamp(28px, 4vh, 44px) clamp(28px, 6vw, 96px) clamp(36px, 5vh, 56px)' }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 20 }}>
            {links.map((l) => (
              <a key={l.label} href={l.href} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
                <div style={{ fontFamily: FONT, fontSize: 11, color: PINK_LIGHT, letterSpacing: '0.16em', fontWeight: 700, marginBottom: 8 }}>{l.label.toUpperCase()}</div>
                <div style={{ fontFamily: FONT, fontSize: 16, color: '#fff', fontWeight: 600 }}>{l.value}</div>
              </a>
            ))}
          </div>
          <div style={{ fontFamily: FONT, fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 36 }}>양건호 (Geonho Yang) · 2026 · COCONE AI Engineer 인턴십 지원</div>
        </div>
      </div>
    </footer>
  )
}

// ─────────────────────────────────────────────
// 슬라이드 — 각 100vh 풀스크린, 스크롤 없이 크로스페이드 전환
// ─────────────────────────────────────────────

function Kicker({ label }: { label: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 'clamp(20px, 3vh, 30px)' }}>
      <span style={{ width: 24, height: 1, background: ACCENT }} />
      <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: ACCENT, letterSpacing: '0.22em' }}>{label}</span>
    </div>
  )
}

// ABOUT + STACK 합본 슬라이드 — 위는 자기소개(t.sec), 아래는 기술 마퀴 밴드(다크)
function AboutStackSlide({ t }: { t: Theme }) {
  return (
    <section style={{ position: 'absolute', inset: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'flex-start', background: t.sec }}>
      <SectionBg t={t} />
      <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%', padding: 'clamp(72px, 11vh, 128px) clamp(28px, 6vw, 96px) clamp(20px, 3vh, 36px)', position: 'relative', zIndex: 1 }}>
        <Kicker label="ABOUT · 자기소개" />
        <blockquote style={{ margin: '0 0 clamp(16px,2.2vh,28px)', padding: '16px 24px', borderLeft: `3px solid ${ACCENT}`, background: t.accentSoft, borderRadius: '0 12px 12px 0', fontFamily: FONT, fontSize: 'clamp(15px, 1.7vw, 19px)', fontWeight: 700, lineHeight: 1.48, color: t.ink, letterSpacing: '-0.015em', wordBreak: 'keep-all' }}>
          {QUOTE}
          <div style={{ fontSize: 12, fontWeight: 600, color: ACCENT, marginTop: 8 }}>— 코코네 채용 공고 · I AM</div>
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
      </div>
      <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%', padding: '0 clamp(28px, 6vw, 96px) clamp(28px, 4vh, 52px)', position: 'relative', zIndex: 1, marginTop: 'auto' }}>
        <div style={{ background: BAND, borderRadius: 20, padding: 'clamp(20px, 3vh, 34px) 0', overflow: 'hidden' }}>
          <div style={{ padding: '0 clamp(22px, 3vw, 40px)', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 14 }}>
              <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 800, color: PINK_LIGHT, letterSpacing: '0.18em' }}>STACK</span>
              <span style={{ fontFamily: FONT, fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.55)', letterSpacing: '0.14em' }}>직접 다루는 기술</span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Marquee items={STACK.ai} duration={32} />
            <Marquee items={STACK.infra} duration={36} reverse />
          </div>
        </div>
      </div>
    </section>
  )
}

function BuildsSlide({ t }: { t: Theme }) {
  return (
    <SlidePane bg={t.sec} t={t}>
      <SectionHeader no="03" kicker="BUILDS · 공개 레포" title={'코드로 직접 확인하세요'} t={t} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        {PROJECTS.map((p, i) => (<FadeIn key={p.name} delay={i * 0.06}><ProjectCard {...p} t={t} /></FadeIn>))}
      </div>
    </SlidePane>
  )
}

function SlidePane({ children, bg, t, withBg = true, center = true, pad }: { children: React.ReactNode; bg: string; t: Theme; withBg?: boolean; center?: boolean; pad?: string }) {
  return (
    <section style={{ position: 'absolute', inset: 0, background: bg, overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: center ? 'center' : 'flex-start', padding: pad ?? 'clamp(56px, 8vh, 104px) clamp(28px, 6vw, 96px)' }}>
      {withBg && <SectionBg t={t} />}
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

function ImageZoom({ src, label }: { src: string; label: string }) {
  if (typeof document === 'undefined') return null
  return createPortal(
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, transition: { duration: 0.18 } }}
      style={{ position: 'fixed', inset: 0, zIndex: 9998, background: 'rgba(12,4,10,0.86)', backdropFilter: 'blur(5px)', display: 'flex', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
      <motion.figure initial={{ opacity: 0, scale: 0.92 }} animate={{ opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 240, damping: 22 } }} exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.15 } }}
        style={{ margin: 0, maxWidth: 'min(1040px, 92vw)', maxHeight: '86vh', borderRadius: 16, overflow: 'hidden', boxShadow: '0 50px 140px rgba(0,0,0,0.7)' }}>
        <img src={src} alt={label} style={{ display: 'block', width: '100%', height: 'auto', maxHeight: '78vh', objectFit: 'contain', background: '#1a0814' }} />
        <figcaption style={{ fontFamily: FONT, fontSize: 13, fontWeight: 600, color: '#fff', padding: '13px 18px', background: 'rgba(26,8,20,0.92)', textAlign: 'center' }}>{label}</figcaption>
      </motion.figure>
    </motion.div>,
    document.body,
  )
}

function IntroPanel({ project, kicker, shots, t }: { project: { no: string; tag: string; title: string; tagline: string; repo: string; live: string; stats: readonly { value: string; unit: string; label: string }[] }; kicker: string; shots?: { src: string; label: string }[]; t: Theme }) {
  const [hovered, setHovered] = useState<number | null>(null)
  return (
    <section style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 'clamp(48px, 7vh, 92px) clamp(40px, 7vw, 120px)' }}>
      <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
        <Kicker label={`${kicker} — ${project.tag}`} />
        {shots ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 0.94fr) minmax(0, 1.06fr)', gap: 'clamp(28px, 4vw, 68px)', alignItems: 'center' }}>
            <div><ProjectHeader {...project} t={t} /></div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              {shots.map((s, i) => (
                <figure key={s.label}
                  onMouseEnter={() => setHovered(i)}
                  onMouseLeave={() => setHovered(null)}
                  style={{
                    margin: 0, borderRadius: 14, overflow: 'hidden', border: `1px solid ${hovered === i ? ACCENT : t.cardBorder}`, background: '#1a0814', position: 'relative', cursor: 'pointer',
                    boxShadow: hovered === i ? `0 22px 56px -18px rgba(0,0,0,0.5)` : t.cardShadow,
                    transition: 'box-shadow 320ms ease, border-color 320ms ease',
                  }}>
                  <img src={s.src} alt={s.label} loading="lazy" style={{ width: '100%', display: 'block', aspectRatio: '16/10', objectFit: 'cover', objectPosition: 'top left' }} />
                  <figcaption style={{ fontFamily: FONT, fontSize: 11, fontWeight: 600, color: t.sub, padding: '8px 11px', background: t.card, borderTop: `1px solid ${t.cardBorder}` }}>{s.label}</figcaption>
                  <span style={{ position: 'absolute', top: 8, right: 8, width: 24, height: 24, borderRadius: 7, background: 'rgba(0,0,0,0.5)', color: '#fff', fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: hovered === i ? 1 : 0, transition: 'opacity 280ms' }}>⤢</span>
                </figure>
              ))}
            </div>
          </div>
        ) : (
          <ProjectHeader {...project} t={t} />
        )}
        {shots && (
          <div style={{ marginTop: 'clamp(26px, 4vh, 52px)' }}>
            <LiveServersMarquee compact />
          </div>
        )}
      </div>
      <AnimatePresence>
        {hovered !== null && shots && <ImageZoom key={hovered} src={shots[hovered].src} label={shots[hovered].label} />}
      </AnimatePresence>
    </section>
  )
}

function GuiPanel({ gui, t }: { gui: { title: string; body: string }; t: Theme }) {
  return (
    <section style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 'clamp(56px, 8vh, 104px) clamp(40px, 7vw, 120px)' }}>
      <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
        <Kicker label="PROJECT 02 · kasaterm" />
        <GuiWip gui={gui} t={t} />
      </div>
    </section>
  )
}

function AudioPlayer({ label, src, t }: { label: string; src: string; t: Theme }) {
  const ref = useRef<HTMLAudioElement>(null)
  const [playing, setPlaying] = useState(false)
  const [prog, setProg] = useState(0)
  const toggle = () => {
    const a = ref.current
    if (!a) return
    if (playing) a.pause(); else void a.play()
    setPlaying((v) => !v)
  }
  useEffect(() => {
    const a = ref.current
    if (!a) return
    const onTime = () => setProg(a.duration ? (a.currentTime / a.duration) * 100 : 0)
    const onEnd = () => { setPlaying(false); setProg(0) }
    a.addEventListener('timeupdate', onTime)
    a.addEventListener('ended', onEnd)
    return () => { a.removeEventListener('timeupdate', onTime); a.removeEventListener('ended', onEnd) }
  }, [])
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', borderRadius: 12, background: t.accentSoft, border: `1px solid ${ACCENT}33` }}>
      <audio ref={ref} src={src} preload="metadata" />
      <button onClick={toggle} aria-label="음성 재생" style={{ width: 34, height: 34, borderRadius: '50%', border: 'none', cursor: 'pointer', background: ACCENT, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: 11, paddingLeft: playing ? 0 : 2 }}>{playing ? '❚❚' : '▶'}</button>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: FONT, fontSize: 12.5, fontWeight: 700, color: t.ink, marginBottom: 5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{label}</div>
        <div style={{ height: 4, borderRadius: 2, background: t.isDark ? 'rgba(255,255,255,0.14)' : 'rgba(26,6,20,0.1)', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${prog}%`, background: ACCENT, transition: 'width 120ms linear' }} />
        </div>
      </div>
    </div>
  )
}

function CasePanel({ item, no, kicker, t }: { item: { title: string; problem: string; approach: string; result: string; bridge: string; audio?: { label: string; src: string }[] }; no: number; kicker: string; t: Theme }) {
  const rows = [
    { label: '문제', sub: 'Problem', body: item.problem, c: '#E5615A' },
    { label: '접근', sub: 'Approach', body: item.approach, c: '#F2A93B' },
    { label: '결과', sub: 'Result', body: item.result, c: '#3FAE7E' },
    { label: '코코네 연결', sub: 'Bridge', body: item.bridge, c: ACCENT },
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
        {item.audio && (
          <div style={{ marginTop: 'clamp(20px, 3vh, 32px)', paddingTop: 'clamp(18px, 2.6vh, 28px)', borderTop: `1px solid ${t.cardBorder}` }}>
            <div style={{ fontFamily: FONT, fontSize: 10.5, fontWeight: 800, color: t.muted, letterSpacing: '0.16em', textTransform: 'uppercase', marginBottom: 12 }}>실제 합성 음성 — 들어보기</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 12 }}>
              {item.audio.map((a) => <AudioPlayer key={a.src} label={a.label} src={a.src} t={t} />)}
            </div>
          </div>
        )}
      </article>
    </PanelShell>
  )
}

function HStackCard({ index, progress, slideOut, children }: { index: number; progress: number; slideOut?: boolean; children: React.ReactNode }) {
  const dist = index - progress
  const x = dist > 1 ? 108 : dist >= 0 ? dist * 100 : slideOut ? dist * 100 : dist * 5
  const scale = slideOut ? 1 : Math.max(0.84, 1 - Math.max(0, progress - index) * 0.06)
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

interface ProjectProps {
  project: { no: string; tag: string; title: string; tagline: string; repo: string; live: string; stats: readonly { value: string; unit: string; label: string }[] }
  cases: readonly { no: number; title: string; problem: string; approach: string; result: string; bridge: string }[]
  kicker: string; bg: string; t: Theme
  shots?: { src: string; label: string }[]
  gui?: { title: string; body: string }
}

function ProjectSlide({ project, cases, kicker, shots, gui, bg, t, subProgress }: ProjectProps & { subProgress: number }) {
  const stackPanels: { node: React.ReactNode; slideOut?: boolean }[] = [
    { node: <IntroPanel project={project} kicker={kicker} shots={shots} t={t} />, slideOut: true },
    ...cases.map((c, i) => ({ node: <CasePanel key={`c${i}`} item={c} no={i + 1} kicker={`${kicker} · CASE`} t={t} /> })),
  ]
  const stackEnd = stackPanels.length - 1
  const stackProgress = gui ? Math.min(subProgress, stackEnd) : subProgress
  const panX = gui ? -Math.max(0, Math.min(1, subProgress - stackEnd)) * 50 : 0
  return (
    <div style={{ position: 'absolute', inset: 0, background: bg, overflow: 'hidden' }}>
      <SectionBg t={t} />
      <div style={{ position: 'absolute', inset: 0, width: gui ? '200%' : '100%', transform: `translateX(${panX}%)`, transition: 'transform 220ms cubic-bezier(0.33,1,0.68,1)', zIndex: 1 }}>
        <div style={{ position: 'absolute', left: 0, top: 0, width: gui ? '50%' : '100%', height: '100%' }}>
          {stackPanels.map((p, i) => (
            <HStackCard key={i} index={i} progress={stackProgress} slideOut={p.slideOut}>{p.node}</HStackCard>
          ))}
        </div>
        {gui && (
          <div style={{ position: 'absolute', left: '50%', top: 0, width: '50%', height: '100%' }}>
            <GuiPanel gui={gui} t={t} />
          </div>
        )}
      </div>
      <StackDots total={stackPanels.length + (gui ? 1 : 0)} progress={subProgress} t={t} />
    </div>
  )
}

function ClosingFooterSlide({ t }: { t: Theme }) {
  return (
    <div style={{ background: t.secAlt }}>
      <section style={{ minHeight: '100vh', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 'clamp(48px, 6vw, 96px)' }}>
        <SectionBg t={t} />
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
          <Kicker label="CLOSING" />
          <div style={{ fontFamily: FONT, fontSize: 'clamp(28px, 4.6vw, 58px)', fontWeight: 800, lineHeight: 1.24, letterSpacing: '-0.035em', color: t.ink, wordBreak: 'keep-all' }}>
            <BlurText text={MANIFESTO.closing} delay={55} animateBy="words" direction="bottom" className="!m-0" />
          </div>
          <p style={{ fontFamily: FONT, fontSize: 'clamp(15px, 1.7vw, 20px)', fontWeight: 500, lineHeight: 1.65, color: t.sub, margin: 'clamp(24px, 3.6vh, 44px) 0 0', maxWidth: 720, wordBreak: 'keep-all' }}>{MANIFESTO.closingSub}</p>
          <div style={{ marginTop: 'clamp(32px, 5vh, 56px)', display: 'flex', alignItems: 'center', gap: 10, color: t.muted, fontFamily: FONT, fontSize: 12.5, fontWeight: 600 }}>
            <span>아래로 스크롤</span>
            <motion.span animate={{ y: [0, 5, 0] }} transition={{ duration: 1.5, repeat: Infinity }}>↓</motion.span>
          </div>
        </div>
      </section>
      <KokoneFooter />
    </div>
  )
}

// ─────────────────────────────────────────────
// 페이지
// ─────────────────────────────────────────────

export default function PageKokone() {
  const [isDark, setIsDark] = useState(true)
  const t = makeTheme(isDark)

  useEffect(() => {
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    window.scrollTo(0, 0)
    return () => { document.body.style.overflow = prevOverflow }
  }, [])

  const debiCases = CASES.filter((c) => c.tag === 'debi-marlene')
  const kasaCases = CASES.filter((c) => c.tag === 'kasaterm')

  const debiShots = [
    { src: shotAiChat, label: 'AI 챗 — Gemma4 LoRA 캐릭터 대화' },
    { src: shotTts, label: 'TTS 설정 — CosyVoice3 음성 합성' },
    { src: shotDashboard, label: '서버 대시보드 — React 19 · Tailwind 4' },
    { src: shotWebpanel, label: '웹패널 — PWA' },
  ]
  const slides: Slide[] = [
    { node: <Hero t={t} /> },
    { node: <Statement kicker="MANIFESTO" text={MANIFESTO.intro} sub={MANIFESTO.introSub} bg={t.secAlt} t={t} /> },
    { node: <AboutStackSlide t={t} /> },
    { render: (sub) => <ProjectSlide project={PROJECT_DEBI} cases={debiCases} kicker="PROJECT 01" bg={t.sec} t={t} shots={debiShots} subProgress={sub} />, substeps: debiCases.length },
    { render: (sub) => <ProjectSlide project={PROJECT_KASA} cases={kasaCases} kicker="PROJECT 02" bg={t.secAlt} t={t} gui={PROJECT_KASA.gui} subProgress={sub} />, substeps: kasaCases.length + 1 },
    { node: <BuildsSlide t={t} /> },
    { node: <ClosingFooterSlide t={t} />, scroll: true },
  ]

  return (
    <div style={{ fontFamily: FONT, color: t.ink, letterSpacing: '-0.01em', background: t.pageBg, minHeight: '100vh', overflowX: 'clip' }}>
      <ThemeToggle isDark={isDark} toggle={() => setIsDark((v) => !v)} />
      <KokoneChatbot />
      <SlideDeck slides={slides} accent={ACCENT} />
    </div>
  )
}
