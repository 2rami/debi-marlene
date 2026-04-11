import { useRef, useEffect, useState } from 'react'
import { motion, useInView, useScroll, useTransform, AnimatePresence } from 'framer-motion'
import Lenis from 'lenis'
import Header from '../components/common/Header'
import GlassButton from '../components/common/GlassButton'
import GradientText from '../components/common/GradientText'
import ScrollFloat from '../components/common/ScrollFloat'
import { useTheme } from '../contexts/ThemeContext'

/* ── Assets ── */
import CHAR_HERO_LIGHT from '../assets/images/event/imgi_30_ch01_v2.png'
import CHAR_HERO_DARK from '../assets/images/event/char_twins_dark.png'

/* Screenshots */
import SS_STATS from '../assets/images/event/screenshot_stats.png'
import SS_RECORD from '../assets/images/event/screenshot_record.png'
import SS_DASHBOARD from '../assets/images/event/screenshot_dashboard.png'
import SS_TTS_SETTINGS from '../assets/images/event/screenshot_tts_settings.png'
import SS_WEBPANEL from '../assets/images/event/screenshot_webpanel.png'
import SS_STATUSLINE from '../assets/images/event/statusline_preview.png'

const ACCENT = '#0B5ED7'
const ACCENT2 = '#6DC8E8'

/* ── FadeIn ── */
function FadeIn({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

/* ── SVG Title Text ── */
function SVGTitle({ lines, className = '' }: { lines: string[]; className?: string }) {
  const { isDark } = useTheme()
  return (
    <div className={className} style={{ filter: 'url(#text-texture)' }}>
      {lines.map((line, i) => {
        const charCount = line.length
        const vw = charCount <= 2 ? 350 * charCount : 280 * charCount
        const gradId = `title-grad-${i}`
        return (
          <div key={i}>
            <svg viewBox={`0 0 ${vw} 250`} className="w-[300px] md:w-[550px] lg:w-[700px] h-auto overflow-visible block">
              {isDark && (
                <defs>
                  <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor={ACCENT} />
                    <stop offset="100%" stopColor={ACCENT2} />
                  </linearGradient>
                </defs>
              )}
              {isDark ? (
                <>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="none" stroke={`url(#${gradId})`} strokeWidth="12" paintOrder="stroke">{line}</text>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="#d1d5db" stroke={`url(#${gradId})`} strokeWidth="5" paintOrder="stroke" style={{ filter: `drop-shadow(0px 4px 8px rgba(11, 94, 215, 0.3))` }}>{line}</text>
                </>
              ) : (
                <>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="none" stroke={ACCENT2} strokeWidth="12" paintOrder="stroke">{line}</text>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill={ACCENT} stroke={ACCENT2} strokeWidth="5" paintOrder="stroke" style={{ filter: `drop-shadow(0px 4px 6px rgba(11, 94, 215, 0.4))` }}>{line}</text>
                </>
              )}
            </svg>
          </div>
        )
      })}
    </div>
  )
}

/* ── Screenshot with glow ── */
function Screenshot({ src, alt, delay = 0 }: { src: string; alt: string; delay?: number }) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className="relative group">
      <div className={`absolute -inset-3 rounded-3xl blur-xl transition-opacity group-hover:opacity-100 ${
        isDark ? 'bg-[#0B5ED7]/10 opacity-50' : 'bg-gradient-to-br from-[#0B5ED7]/15 to-[#6DC8E8]/15 opacity-60'
      }`} />
      <img
        src={src}
        alt={alt}
        className={`relative w-full h-auto max-h-[400px] object-contain object-top rounded-2xl shadow-2xl border ${isDark ? 'border-white/10' : 'border-white/40'}`}
        draggable={false}
      />
    </FadeIn>
  )
}

/* ── JD Match Card ── */
function MatchCard({ requirement, evidence, techs, delay = 0 }: {
  requirement: string; evidence: string; techs: string[]; delay?: number
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className={`p-5 rounded-2xl border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/80 border-gray-200/50'}`}>
      <div className="flex items-start gap-3 mb-3">
        <div className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" style={{ backgroundColor: `${ACCENT}20`, color: ACCENT }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>
        </div>
        <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>{requirement}</div>
      </div>
      <p className={`text-sm leading-relaxed ml-9 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{evidence}</p>
      <div className="flex flex-wrap gap-1.5 mt-3 ml-9">
        {techs.map(t => (
          <span key={t} className={`px-2 py-0.5 rounded-full text-xs border ${isDark ? 'bg-white/[0.05] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
        ))}
      </div>
    </FadeIn>
  )
}

/* ── Troubleshoot Card ── */
function TroubleshootCard({ title, problem, cause, solution, color, delay = 0 }: {
  title: string; problem: string; cause: string; solution: string; color: string; delay?: number
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay}>
      <div className={`rounded-2xl border overflow-hidden ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/80 border-gray-200/50'}`}>
        <div className="flex items-stretch">
          <div className="w-1 shrink-0" style={{ backgroundColor: color }} />
          <div className="flex-1 p-5">
            <div className={`font-bold text-sm mb-3 ${isDark ? 'text-white' : 'text-gray-800'}`}>{title}</div>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#ed4245' }}>Problem</div>
                <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{problem}</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#faa61a' }}>Root Cause</div>
                <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{cause}</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#43b581' }}>Solution</div>
                <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{solution}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </FadeIn>
  )
}

/* ── Pipeline Step ── */
function PipelineStep({ step, title, desc, techs, isLast = false, delay = 0 }: {
  step: number; title: string; desc: string; techs: string[]; isLast?: boolean; delay?: number
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className="relative pl-10 pb-8">
      {!isLast && <div className={`absolute left-[15px] top-10 bottom-0 w-px ${isDark ? 'bg-white/[0.06]' : 'bg-gray-200'}`} />}
      <div className="absolute left-0 top-0 w-[32px] h-[32px] rounded-full flex items-center justify-center text-xs font-bold" style={{ backgroundColor: `${ACCENT}20`, color: ACCENT }}>
        {step}
      </div>
      <h4 className={`font-bold mb-1 ${isDark ? 'text-white' : 'text-gray-800'}`}>{title}</h4>
      <p className={`text-sm leading-relaxed mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{desc}</p>
      <div className="flex flex-wrap gap-1.5">
        {techs.map(t => (
          <span key={t} className={`px-2 py-0.5 rounded-full text-xs border ${isDark ? 'bg-white/[0.05] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
        ))}
      </div>
    </FadeIn>
  )
}

/* ── Theme Toggle Button ── */
function ThemeToggle() {
  const { isDark, toggle } = useTheme()
  return (
    <motion.button
      onClick={toggle}
      className={`fixed bottom-6 right-6 z-50 cursor-pointer rounded-full w-12 h-12 flex items-center justify-center ${
        isDark
          ? 'bg-gradient-to-b from-[#1a1a2e] to-[#16213e] border border-white/15 text-white'
          : 'bg-gradient-to-b from-white to-gray-50 border border-gray-200 text-gray-700'
      }`}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25, delay: 0.5 }}
      whileHover={{ scale: 1.1 }}
      style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.12)' }}
      aria-label="Toggle theme"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
        {isDark ? (
          <><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></>
        ) : (
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        )}
      </svg>
    </motion.button>
  )
}

/* ── Section Navigator ── */
const SECTIONS = [
  { id: 'hero', label: 'Hero' },
  { id: 'match', label: 'JD Match' },
  { id: 'pipeline', label: 'AI Pipeline' },
  { id: 'troubleshoot', label: 'Troubleshooting' },
  { id: 'features', label: 'Features' },
  { id: 'architecture', label: 'Architecture' },
  { id: 'techstack', label: 'Tech Stack' },
  { id: 'cost', label: 'Cost Analysis' },
]

function SectionNav() {
  const { isDark } = useTheme()
  const [active, setActive] = useState('hero')
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.scrollY > window.innerHeight * 0.5)
      for (let i = SECTIONS.length - 1; i >= 0; i--) {
        const el = document.getElementById(SECTIONS[i].id)
        if (el) {
          const rect = el.getBoundingClientRect()
          if (rect.top <= window.innerHeight * 0.4) {
            setActive(SECTIONS[i].id)
            break
          }
        }
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <AnimatePresence>
      {visible && (
        <motion.nav
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.3 }}
          className="fixed right-5 top-1/2 -translate-y-1/2 z-40 flex flex-col items-end gap-3 max-md:hidden"
        >
          {SECTIONS.map(s => {
            const isActive = active === s.id
            return (
              <button
                key={s.id}
                onClick={() => document.getElementById(s.id)?.scrollIntoView({ behavior: 'smooth' })}
                className="group flex items-center gap-2.5 cursor-pointer"
              >
                <span className={`text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'text-[#0B5ED7] opacity-100'
                    : isDark ? 'text-white/0 group-hover:text-white/70' : 'text-gray-800/0 group-hover:text-gray-500'
                }`}>
                  {s.label}
                </span>
                <div className="relative flex items-center justify-center w-3 h-3">
                  {isActive && (
                    <motion.div
                      layoutId="nav-active-nexon"
                      className="absolute inset-[-3px] rounded-full bg-[#0B5ED7]/20"
                      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                    />
                  )}
                  <div className={`w-2.5 h-2.5 rounded-full transition-all duration-200 ${
                    isActive
                      ? 'bg-[#0B5ED7] scale-100'
                      : isDark ? 'bg-white/20 group-hover:bg-white/50 scale-75' : 'bg-gray-300 group-hover:bg-gray-400 scale-75'
                  }`} />
                </div>
              </button>
            )
          })}
        </motion.nav>
      )}
    </AnimatePresence>
  )
}


/* ══════════════════════════════════════════════
   PortfolioNexon Page
   ══════════════════════════════════════════════ */
export default function PortfolioNexon() {
  const { isDark } = useTheme()
  const heroRef = useRef(null)

  useEffect(() => {
    const lenis = new Lenis({ duration: 0.25, wheelMultiplier: 0.5, easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) })
    ;(window as any).__lenis = lenis
    lenis.scrollTo(0, { immediate: true })
    function raf(time: number) { lenis.raf(time); requestAnimationFrame(raf) }
    requestAnimationFrame(raf)
    return () => { lenis.destroy(); (window as any).__lenis = null }
  }, [])

  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const charY = useTransform(scrollYProgress, [0, 1], ['0%', '20%'])
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '30%'])

  return (
    <div className={`min-h-screen font-body selection:bg-[#0B5ED7]/20 relative z-0 transition-colors duration-500 ${
      isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'
    }`} style={{ overflowX: 'clip' }}>
      <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden="true">
        <defs>
          <filter id="text-texture" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.339" numOctaves="3" seed="5044" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="4" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>
      </svg>

      <Header />
      <ThemeToggle />
      <SectionNav />

      {/* ══ HERO ══ */}
      <section id="hero" ref={heroRef} className="relative min-h-screen flex items-center overflow-hidden">
        <div className={`absolute top-20 left-[10%] w-[600px] h-[600px] rounded-full blur-[150px] pointer-events-none ${isDark ? 'bg-[#0B5ED7]/[0.07]' : 'bg-[#0B5ED7]/[0.12]'}`} />
        <div className={`absolute top-40 right-[10%] w-[500px] h-[500px] rounded-full blur-[150px] pointer-events-none ${isDark ? 'bg-[#6DC8E8]/[0.05]' : 'bg-[#6DC8E8]/[0.08]'}`} />

        <motion.div
          className="absolute right-[2%] top-[8%] w-[45%] max-w-[600px] h-[70%] overflow-hidden pointer-events-none z-[2] max-md:hidden"
          style={{ y: charY }}
        >
          <img
            src={isDark ? CHAR_HERO_DARK : CHAR_HERO_LIGHT}
            alt=""
            className="w-full h-auto object-cover object-top transition-opacity duration-500"
            draggable={false}
          />
        </motion.div>

        <motion.div className="relative z-[5] max-w-6xl mx-auto px-6 lg:px-16 py-32" style={{ y: textY }}>
          <FadeIn>
            <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-6 ${
              isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'
            }`}>
              Portfolio -- Yang Gunho
            </span>
          </FadeIn>

          <FadeIn delay={0.1}>
            <GradientText
              colors={[ACCENT, ACCENT2, '#4A9BE8', ACCENT2, ACCENT]}
              animationSpeed={5}
              className="!mx-0 font-title text-[24px] md:text-[36px] leading-normal whitespace-nowrap mb-2"
              pauseOnHover
            >
              NEXON -- AI Agent Full-Stack Engineer
            </GradientText>
          </FadeIn>

          <FadeIn delay={0.15}>
            <SVGTitle lines={['포트폴리오']} />
          </FadeIn>

          <FadeIn delay={0.25}>
            <p className={`text-lg md:text-xl leading-relaxed max-w-xl mt-8 font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
              LLM 파인튜닝, 음성 AI Agent, RAG 대화 시스템을<br />
              직접 설계하고 운영한 1인 풀스택 프로젝트.
            </p>
          </FadeIn>

          <FadeIn delay={0.3}>
            <div className="flex flex-wrap gap-4 mt-10">
              <GlassButton href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer" size="sm">
                <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>GitHub</span>
              </GlassButton>
              <GlassButton href="/landing" size="sm">
                Live Site
              </GlassButton>
            </div>
          </FadeIn>

          <FadeIn delay={0.35}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-14 max-w-2xl">
              {[
                { v: '6+ months', l: '개발 기간' },
                { v: 'Full-Stack', l: '1인 개발/운영' },
                { v: '6 Models', l: 'LLM/TTS 모델 비교' },
                { v: 'AI Native', l: 'Claude Code 개발' },
              ].map((s, i) => (
                <div key={i} className={`text-center px-4 py-4 rounded-2xl border ${
                  isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/60 backdrop-blur-sm border-white/40'
                }`}>
                  <div className="text-xl md:text-2xl font-bold bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent">{s.v}</div>
                  <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{s.l}</div>
                </div>
              ))}
            </div>
          </FadeIn>
        </motion.div>
      </section>

      {/* ══ JD MATCH ══ */}
      <section id="match" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName={`font-title bg-gradient-to-r from-[${ACCENT}] to-[${ACCENT2}] bg-clip-text text-transparent leading-tight`}
              textClassName="text-4xl md:text-[64px]"
            >
              JD Match
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                넥슨 AX-Tech실 공고 요구사항과<br />
                이 프로젝트에서 실제로 구현한 내용의 매칭.
              </p>
            </FadeIn>
          </div>

          {/* 지원 자격 */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-6`} style={{ color: ACCENT }}>
              Requirements
            </h3>
          </FadeIn>
          <div className="space-y-4 mb-12">
            <MatchCard
              delay={0}
              requirement="Python, TypeScript 능숙한 개발"
              evidence="봇 백엔드(Python, discord.py, Flask), 대시보드 프론트엔드(TypeScript, React 19), 웹패널(Flask + React). 두 언어로 전체 서비스를 1인 개발 및 운영 중."
              techs={['Python', 'TypeScript', 'discord.py', 'React 19', 'Flask']}
            />
            <MatchCard
              delay={0.05}
              requirement="LLM 등 외부 AI 서비스를 활용한 웹 애플리케이션 개발"
              evidence="Gemma4 LoRA 파인튜닝(Modal A10G), Qwen3.5-Omni API(DashScope), Claude API 연동. 텍스트 채팅 + 음성 대화 두 채널에서 AI를 활용한 실시간 서비스 운영."
              techs={['Gemma4 LoRA', 'Qwen3.5-Omni API', 'Claude API', 'Modal Serverless']}
            />
            <MatchCard
              delay={0.1}
              requirement="대화형 AI, Agent 설계/개발"
              evidence="캐릭터 인격을 가진 대화형 AI Agent. 키워드 트리거 + 패치노트 검색(RAG) + 대화 메모리(GCS)로 맥락을 유지하는 멀티턴 대화 시스템 구현."
              techs={['Prompt Engineering', 'RAG', 'GCS Memory', 'Multi-turn']}
            />
            <MatchCard
              delay={0.15}
              requirement="업무 자동화 및 생산성 향상을 위한 AI 활용"
              evidence="Claude Code CLI로 전체 프로젝트 개발. MCP 서버 연동(Figma, Context7, NotebookLM). AI 기반 개발 도구로 6개월간 1인 풀스택 프로젝트 완성."
              techs={['Claude Code', 'MCP Server', 'Figma MCP', 'AI-assisted Dev']}
            />
            <MatchCard
              delay={0.2}
              requirement="풀스택 역량 -- 프론트엔드부터 백엔드까지"
              evidence="React 19 + Tailwind 4 + Vite(프론트) / Flask + Gunicorn(백엔드) / Docker + nginx(인프라) / GCP VM + Cloudflare CDN(배포). 기획-개발-배포-운영 전 과정을 단독 수행."
              techs={['React', 'Flask', 'Docker', 'GCP', 'Cloudflare', 'nginx']}
            />
            <MatchCard
              delay={0.25}
              requirement="프롬프트 설계, 입력 데이터 구조화로 LLM 활용 품질 개선"
              evidence="캐릭터별 인격 프롬프트 + 패치노트 컨텍스트 주입 + 대화 히스토리 관리. 음성 대화에서는 '들린 말 반복 금지', '캐릭터별 응답 분리' 등 프롬프트 튜닝으로 품질 개선."
              techs={['System Prompt', 'Context Injection', 'Response Parsing']}
            />
          </div>

          {/* 우대사항 */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-6`} style={{ color: ACCENT2 }}>
              Preferred
            </h3>
          </FadeIn>
          <div className="space-y-4">
            <MatchCard
              delay={0}
              requirement="LLM 챗봇, RAG 설계/개발/운영 경험"
              evidence="패치노트 RAG: 최신 패치 데이터를 파싱하여 벡터 없이 키워드 기반으로 검색, LLM 컨텍스트에 주입. 대화 메모리를 GCS에 저장하여 세션 간 맥락 유지."
              techs={['Patchnote RAG', 'GCS', 'Keyword Search', 'Context Window']}
            />
            <MatchCard
              delay={0.05}
              requirement="AI 기반 개발 도구를 능숙하게 활용하여 생산성 향상"
              evidence="Claude Code CLI를 주 개발 도구로 사용. MCP 서버(Figma, Context7, NotebookLM, Exa)로 외부 도구 연동. 이 포트폴리오 페이지 자체도 Claude Code로 작성."
              techs={['Claude Code', 'MCP Protocol', 'AI-first Development']}
            />
            <MatchCard
              delay={0.1}
              requirement="AX(AI Transformation) 프로젝트 경험"
              evidence="게임 커뮤니티의 반복 업무(전적 검색, 패치 요약, 음성 안내)를 AI로 자동화. 수동으로 웹사이트를 방문해야 했던 작업을 Discord 안에서 AI가 처리."
              techs={['Automation', 'Discord Bot', 'AI Integration']}
            />
            <MatchCard
              delay={0.15}
              requirement="AWS 또는 클라우드 환경 서비스 운영 경험"
              evidence="GCP Compute Engine VM에서 프로덕션 서비스 운영. Docker 컨테이너 + nginx reverse proxy + Cloudflare CDN. Makefile로 빌드/배포/롤백 자동화."
              techs={['GCP', 'Docker', 'nginx', 'Cloudflare', 'Makefile']}
            />
          </div>
        </div>
      </section>

      {/* ══ AI PIPELINE ══ */}
      <section id="pipeline" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#6DC8E8] to-[#0B5ED7] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              AI Pipeline
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                텍스트 채팅과 음성 대화, 두 채널의 AI 파이프라인.
              </p>
            </FadeIn>
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            {/* Text Chat Pipeline */}
            <div>
              <FadeIn>
                <h3 className={`font-bold mb-6 text-lg flex items-center gap-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: ACCENT }} />
                  Text Chat -- Gemma4 LoRA
                </h3>
              </FadeIn>
              <PipelineStep step={1} title="키워드 트리거" desc="'데비야', '마를렌아' 등 캐릭터 호출 키워드 감지. 슬래시 커맨드(/대화)로도 트리거 가능." techs={['discord.py', 'Regex']} delay={0} />
              <PipelineStep step={2} title="컨텍스트 구성" desc="최신 패치노트 검색(RAG) + 대화 히스토리(GCS) + 캐릭터 시스템 프롬프트 조합." techs={['Patchnote RAG', 'GCS Memory']} delay={0.05} />
              <PipelineStep step={3} title="LLM 추론" desc="Modal A10G에서 Gemma4 E4B + LoRA 어댑터로 캐릭터 인격 기반 응답 생성." techs={['Gemma4', 'LoRA', 'Unsloth', 'Modal']} delay={0.1} />
              <PipelineStep step={4} title="응답 전송" desc="Discord Components V2(Container, Section, TextDisplay)로 시각적 UI 구성하여 전송." techs={['Components V2', 'LayoutView']} delay={0.15} isLast />
            </div>

            {/* Voice Pipeline */}
            <div>
              <FadeIn delay={0.1}>
                <h3 className={`font-bold mb-6 text-lg flex items-center gap-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: ACCENT2 }} />
                  Voice Chat -- Qwen3.5-Omni
                </h3>
              </FadeIn>
              <PipelineStep step={1} title="음성 수신 + DAVE 복호화" desc="Discord Voice Gateway에서 음성 패킷 수신. Transport 복호화 후 DAVE E2EE 2차 복호화 (Discord 강제 암호화)." techs={['voice_recv', 'DAVE E2EE', 'davey']} delay={0} />
              <PipelineStep step={2} title="VAD 발화 감지" desc="Opus -> PCM -> 16kHz 다운샘플 -> WebRTC VAD. 0.5초 pre-buffer로 발화 시작 부분 보존." techs={['WebRTC VAD', 'Opus Decoder']} delay={0.05} />
              <PipelineStep step={3} title="하이브리드 웨이크워드" desc="짧은 발화(<2초): 게임 음성 즉시 재생 + 듣기 모드 진입. 긴 발화(>=2초): 키워드 체크 + 응답을 한번에." techs={['Hybrid Wakeword', 'Local ACK']} delay={0.1} />
              <PipelineStep step={4} title="Omni 모델 + TTS" desc="Qwen3.5-Omni API로 오디오 이해 + 응답 생성. 화자별 대사 분리 후 CosyVoice3 파인튜닝 TTS로 음성 재생." techs={['DashScope API', 'CosyVoice3', 'Speaker Parsing']} delay={0.15} isLast />
            </div>
          </div>

          {/* Model Selection Journey */}
          <FadeIn delay={0.2} className="mt-16">
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-6 text-center ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              Model Selection Journey -- 6 Attempts
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {[
                { name: 'Qwen2.5-Omni-7B', result: 'FAIL', reason: '파인튜닝 과적합 (loss 0.15)' },
                { name: 'Qwen3.5-9B', result: 'FAIL', reason: 'linear_attention Windows 미지원' },
                { name: 'Gemma4 E4B', result: 'TEXT', reason: 'Unsloth LoRA 텍스트 채팅 성공' },
                { name: 'Gemma4 Omni', result: 'REPLACED', reason: '오디오 이해 동작, 품질 낮음' },
                { name: 'Qwen3-Omni-30B', result: 'FAIL', reason: 'vLLM A100-40GB에서도 OOM' },
                { name: 'Qwen3.5-Omni+', result: 'ADOPTED', reason: 'DashScope API, 품질/비용 최적' },
              ].map((m, i) => (
                <FadeIn key={i} delay={0.05 * i}>
                  <div className={`px-3 py-3 rounded-xl border text-center ${
                    m.result === 'ADOPTED'
                      ? isDark ? 'bg-[#0B5ED7]/10 border-[#0B5ED7]/30' : 'bg-[#0B5ED7]/[0.06] border-[#0B5ED7]/20'
                      : m.result === 'TEXT'
                        ? isDark ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-emerald-50 border-emerald-200/50'
                        : isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/80 border-gray-200'
                  }`}>
                    <div className={`text-xs font-bold mb-1 ${
                      m.result === 'ADOPTED' ? 'text-[#0B5ED7]'
                        : m.result === 'TEXT' ? 'text-emerald-400'
                          : isDark ? 'text-white' : 'text-gray-800'
                    }`}>{m.name}</div>
                    <div className={`text-xs px-2 py-0.5 rounded-full inline-block mb-1 ${
                      m.result === 'ADOPTED' ? 'bg-[#0B5ED7]/20 text-[#0B5ED7]'
                        : m.result === 'TEXT' ? 'bg-emerald-500/20 text-emerald-400'
                          : m.result === 'REPLACED' ? 'bg-amber-500/20 text-amber-400'
                            : isDark ? 'bg-white/[0.05] text-gray-500' : 'bg-gray-100 text-gray-500'
                    }`}>{m.result}</div>
                    <div className={`text-[10px] leading-tight ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{m.reason}</div>
                  </div>
                </FadeIn>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ TROUBLESHOOTING ══ */}
      <section id="troubleshoot" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              Troubleshooting
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                AI 서비스 구축 과정에서 만난 실제 문제들과 해결 과정.
              </p>
            </FadeIn>
          </div>

          {/* AI/LLM */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-4`} style={{ color: ACCENT }}>
              AI / LLM
            </h3>
          </FadeIn>
          <div className="space-y-4 mb-12">
            <TroubleshootCard
              title="Qwen3-Omni 셀프호스팅 실패 (MoE 아키텍처)"
              problem="Qwen3-Omni-30B-A3B를 A100 40GB에서 셀프호스팅 시도했으나 transformers는 응답 없고, vLLM은 CUDA OOM."
              cause="MoE 모델은 활성 파라미터가 3B지만 전체 30B 가중치를 메모리에 로드해야 함. transformers는 MoE 추론이 극도로 느리고, vLLM은 engine v1 미지원."
              solution="셀프호스팅을 포기하고 DashScope API로 전환. OpenAI SDK 호환(base_url만 변경)으로 코드 변경 최소화. 비용도 월 $46 -> $0.27로 170배 절감."
              color={ACCENT}
              delay={0}
            />
            <TroubleshootCard
              title="DAVE E2EE 2차 암호화 (Discord 음성)"
              problem="Discord 음성채널에서 수신한 오디오가 전부 노이즈. transport 복호화만으로는 원본 오디오를 얻을 수 없음."
              cause="Discord가 2024년부터 DAVE(Discord Audio & Video End-to-End Encryption)를 강제 적용. voice_recv 라이브러리는 transport 암호화만 풀어줌."
              solution="davey 라이브러리로 DAVE 2차 복호화를 직접 구현. DaveSession.decrypt(user_id, MediaType.audio, data) 호출 추가."
              color={ACCENT}
              delay={0.05}
            />
            <TroubleshootCard
              title="TTS가 화자 태그까지 읽어버림"
              problem="'데비: 안녕!' 이라는 응답을 TTS가 '데비 콜론 안녕'으로 읽음."
              cause="LLM 응답에 포함된 화자 태그(데비:, 마를렌:)를 제거하지 않고 TTS에 전달."
              solution="parse_character_lines() 함수로 응답을 화자별로 분리, 태그 제거 후 각각 다른 CosyVoice3 음성 모델로 TTS 재생."
              color={ACCENT2}
              delay={0.1}
            />
            <TroubleshootCard
              title="VAD 발화 끝 감지 안 됨"
              problem="말을 멈춰도 발화 종료가 감지되지 않아 feed #500까지 speaking=True 상태 지속."
              cause="배경 소음으로 WebRTC VAD의 silence_count가 계속 리셋. 1.5초 무음 조건을 충족하지 못함."
              solution="SILENCE_FRAMES를 1.5초에서 0.7초로, MAX_SPEECH_SEC를 25초에서 8초로 조정. 환경 소음에 대한 허용 범위 확대."
              color={ACCENT2}
              delay={0.15}
            />
          </div>

          {/* Infrastructure */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-4`} style={{ color: '#43b581' }}>
              Infrastructure
            </h3>
          </FadeIn>
          <div className="space-y-4">
            <TroubleshootCard
              title="CosyVoice3 bfloat16 비트박스 현상"
              problem="T4 GPU에서 파인튜닝된 모델로 추론하면 음성 대신 비트박스 소리가 출력."
              cause="pretrained checkpoint가 bfloat16으로 저장되어 있어 float16으로 변환해도 모델 로드 시 덮어써짐. T4는 bfloat16 하드웨어 미지원."
              solution="T4에서도 bfloat16을 소프트웨어 에뮬레이션으로 사용하도록 강제. pretrained 구조를 건드리지 않고 런타임에서 해결."
              color="#43b581"
              delay={0}
            />
            <TroubleshootCard
              title="Modal Cold Start 58초 -> 워밍업 전략"
              problem="Modal Serverless에 배포한 TTS 서버의 콜드 스타트가 58초. 첫 요청 시 유저가 1분 대기."
              cause="매 콜드 스타트마다 HuggingFace에서 600MB+ 모델 다운로드 + GPU 로드."
              solution="/tts 명령으로 음성채널 입장 시 서버 미리 워밍업. Volume 캐싱으로 warm RTF 1.5~2.2x 달성. 워밍업 상태를 Discord UI에 시각적으로 표시."
              color="#43b581"
              delay={0.05}
            />
          </div>
        </div>
      </section>

      {/* ══ FEATURES ══ */}
      <section id="features" className="py-24 relative">
        <div className="text-center mb-16 px-6">
          <ScrollFloat
            containerClassName="font-title bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent leading-tight"
            textClassName="text-4xl md:text-[64px]"
          >
            Features
          </ScrollFloat>
        </div>

        {/* AI 대화 */}
        <div className="max-w-6xl mx-auto px-6 mb-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <FadeIn>
              <SVGTitle lines={['AI', '대화']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                캐릭터 인격 기반 대화형 AI Agent.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                Gemma4 LoRA 파인튜닝 모델로 캐릭터 말투와 성격을 학습.
                패치노트 RAG로 최신 게임 정보를 반영하고,
                GCS 기반 대화 메모리로 세션 간 맥락을 유지하는 멀티턴 대화.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['Gemma4 LoRA', 'Modal A10G', 'Patchnote RAG', 'GCS Memory'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
            </FadeIn>
            <div className="space-y-4">
              <Screenshot src={SS_RECORD} alt="AI 대화" delay={0.1} />
            </div>
          </div>
        </div>

        {/* 음성 대화 */}
        <div className="max-w-6xl mx-auto px-6 mb-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1 space-y-4">
              <Screenshot src={SS_TTS_SETTINGS} alt="TTS 설정" delay={0.1} />
            </div>
            <FadeIn className="order-1 md:order-2">
              <SVGTitle lines={['음성', 'Agent']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                음성 입력, AI 이해, TTS 응답.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                Discord 음성채널에서 실시간 음성 수신, DAVE E2EE 복호화,
                WebRTC VAD로 발화 감지 후 Qwen3.5-Omni로 오디오 이해.
                화자별 CosyVoice3 파인튜닝 TTS로 캐릭터 음성 응답.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['Qwen3.5-Omni', 'CosyVoice3', 'WebRTC VAD', 'DAVE E2EE'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
              {/* TTS 음성 샘플 */}
              <div className="mt-6 space-y-3">
                <div className={`text-xs font-semibold uppercase tracking-wider ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>CosyVoice3 Fine-tuned Voice Sample</div>
                {[
                  { label: 'Debi', src: '/audio/demo_debi_desc.wav' },
                  { label: 'Marlene', src: '/audio/demo_marlene_desc.wav' },
                ].map(s => (
                  <div key={s.label} className={`flex items-center gap-3 px-4 py-3 rounded-xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-gray-50 border-gray-200'}`}>
                    <span className={`shrink-0 text-sm font-bold w-16`} style={{ color: ACCENT }}>{s.label}</span>
                    <audio controls preload="none" className="w-full h-8 [&::-webkit-media-controls-panel]:bg-transparent">
                      <source src={s.src} type="audio/wav" />
                    </audio>
                  </div>
                ))}
              </div>
            </FadeIn>
          </div>
        </div>

        {/* 웹 대시보드 */}
        <div className="max-w-6xl mx-auto px-6 mb-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <FadeIn>
              <SVGTitle lines={['웹', '대시보드']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                Discord OAuth2 기반 서버 관리 웹앱.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                서버별 봇 설정, TTS 음성/속도 커스터마이징,
                환영/퇴장 메시지 관리, 퀴즈 곡 관리 등을 웹에서 통합 제공.
                Toss Payments SDK 연동으로 후원 결제 기능 구현.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['React 19', 'TypeScript', 'Flask', 'OAuth2', 'Tailwind 4', 'Toss Payments'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
            </FadeIn>
            <div className="space-y-4">
              <Screenshot src={SS_DASHBOARD} alt="대시보드" delay={0.1} />
              <Screenshot src={SS_STATUSLINE} alt="Statusline Preview" delay={0.15} />
            </div>
          </div>
        </div>

        {/* 전적 검색 + 관리자 패널 */}
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1 space-y-4">
              <Screenshot src={SS_STATS} alt="전적 통계" delay={0.1} />
              <Screenshot src={SS_WEBPANEL} alt="웹패널" delay={0.15} />
            </div>
            <FadeIn className="order-1 md:order-2">
              <SVGTitle lines={['운영', '도구']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                전적 검색 + 관리자 모니터링.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                dak.gg API 리버스 엔지니어링으로 전적/통계 데이터 수집.
                관리자 전용 웹패널로 봇 사용 로그, 서버 현황, 유저 니즈 분석.
                SSE 기반 실시간 로그 스트리밍.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['dak.gg API', 'Components V2', 'Flask SSE', 'nginx'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ══ ARCHITECTURE ══ */}
      <section id="architecture" className="py-24 relative">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#6DC8E8] to-[#0B5ED7] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              Architecture
            </ScrollFloat>
          </div>

          <div className="space-y-6">
            {/* Clients */}
            <FadeIn>
              <div className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>Clients</div>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { name: 'Discord', desc: 'Text / Voice / Slash Commands', color: 'discord-blurple' },
                  { name: 'Dashboard', desc: 'debimarlene.com', color: ACCENT },
                  { name: 'Admin Panel', desc: 'panel.debimarlene.com', color: ACCENT2 },
                ].map(c => (
                  <div key={c.name} className={`px-4 py-4 rounded-2xl text-center border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/50'}`}>
                    <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>{c.name}</div>
                    <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{c.desc}</div>
                  </div>
                ))}
              </div>
            </FadeIn>

            <div className="flex justify-center">
              <svg width="24" height="32" viewBox="0 0 24 32" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                <path d="M12 0 L12 24 M6 18 L12 24 L18 18" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>

            {/* GCP VM */}
            <FadeIn delay={0.1}>
              <div className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>GCP Compute Engine VM (Seoul)</div>
              <div className={`p-5 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-[#0B5ED7]/20' : 'bg-blue-50/50 border-blue-200/50'}`}>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { name: 'Discord Bot', desc: 'Python / discord.py' },
                    { name: 'Flask API x2', desc: 'Dashboard + Panel' },
                    { name: 'nginx', desc: 'Reverse Proxy + SSL' },
                    { name: 'Docker', desc: 'Containerized' },
                  ].map(s => (
                    <div key={s.name} className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-[#0B5ED7]/10 border-[#0B5ED7]/20' : 'bg-white border-blue-200/50'}`}>
                      <div className="text-sm font-bold" style={{ color: ACCENT }}>{s.name}</div>
                      <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{s.desc}</div>
                    </div>
                  ))}
                </div>
              </div>
            </FadeIn>

            <div className="flex justify-center gap-16">
              <svg width="24" height="32" viewBox="0 0 24 32" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                <path d="M12 0 L12 24 M6 18 L12 24 L18 18" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
              <svg width="24" height="32" viewBox="0 0 24 32" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                <path d="M12 0 L12 24 M6 18 L12 24 L18 18" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>

            {/* External Services */}
            <FadeIn delay={0.2}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>AI Services</div>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { name: 'Modal A10G', desc: 'Gemma4 Chat' },
                      { name: 'Modal T4', desc: 'CosyVoice3 TTS' },
                      { name: 'DashScope', desc: 'Qwen3.5-Omni' },
                      { name: 'HuggingFace', desc: 'Model Registry' },
                    ].map(s => (
                      <div key={s.name} className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-violet-500/10 border-violet-500/20' : 'bg-violet-50 border-violet-200/50'}`}>
                        <div className="text-sm font-bold text-violet-400">{s.name}</div>
                        <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{s.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <div className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>Storage & CDN</div>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { name: 'GCS', desc: 'Settings / Memory' },
                      { name: 'Artifact Registry', desc: 'Docker Images' },
                      { name: 'Cloudflare', desc: 'CDN / DNS / SSL' },
                      { name: 'Colab', desc: 'Fine-tuning (A100/T4)' },
                    ].map(s => (
                      <div key={s.name} className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-amber-500/10 border-amber-500/20' : 'bg-amber-50 border-amber-200/50'}`}>
                        <div className="text-sm font-bold text-amber-400">{s.name}</div>
                        <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{s.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ══ TECH STACK ══ */}
      <section id="techstack" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              Tech Stack
            </ScrollFloat>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: 'AI / ML',
                color: `text-[${ACCENT}]`,
                items: [
                  { name: 'Gemma4 E4B', desc: 'LoRA 파인튜닝, Unsloth, bfloat16' },
                  { name: 'Qwen3.5-Omni', desc: 'DashScope API, 오디오 이해' },
                  { name: 'CosyVoice3', desc: 'TTS 파인튜닝, Modal T4 배포' },
                  { name: 'WebRTC VAD', desc: '실시간 음성 활동 감지' },
                ],
              },
              {
                title: 'Backend',
                color: 'text-emerald-400',
                items: [
                  { name: 'Python', desc: 'discord.py 2.6, asyncio' },
                  { name: 'Flask', desc: 'REST API x2, Gunicorn' },
                  { name: 'Modal', desc: 'Serverless GPU (A10G, T4)' },
                  { name: 'GCS', desc: '설정, 대화 메모리 저장소' },
                ],
              },
              {
                title: 'Frontend',
                color: 'text-pink-400',
                items: [
                  { name: 'React 19', desc: 'TypeScript, Vite' },
                  { name: 'Tailwind 4', desc: 'Utility-first CSS' },
                  { name: 'Framer Motion', desc: '애니메이션, 트랜지션' },
                  { name: 'OAuth2', desc: 'Discord 로그인 연동' },
                ],
              },
              {
                title: 'Infrastructure',
                color: 'text-amber-400',
                items: [
                  { name: 'GCP VM', desc: 'Compute Engine, Seoul' },
                  { name: 'Docker', desc: '컨테이너 빌드/배포' },
                  { name: 'nginx', desc: 'Reverse proxy, SSL' },
                  { name: 'Cloudflare', desc: 'CDN, DNS, 캐시 퍼지' },
                ],
              },
              {
                title: 'DevOps',
                color: 'text-violet-400',
                items: [
                  { name: 'Makefile', desc: '빌드/배포/롤백 자동화' },
                  { name: 'Artifact Registry', desc: 'Docker 이미지 관리' },
                  { name: 'HuggingFace', desc: '모델 버전 관리' },
                  { name: 'Colab', desc: 'A100/T4 파인튜닝' },
                ],
              },
              {
                title: 'AI Dev Tools',
                color: `text-[${ACCENT2}]`,
                items: [
                  { name: 'Claude Code', desc: '주 개발 도구, CLI' },
                  { name: 'MCP Server', desc: 'Figma, Context7, NLM' },
                  { name: 'Exa', desc: '시맨틱 웹 검색' },
                  { name: 'Obsidian', desc: '지식 관리, TODO' },
                ],
              },
            ].map((cat, i) => (
              <FadeIn key={cat.title} delay={i * 0.05} className={`p-5 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 backdrop-blur-sm border-gray-200/80'}`}>
                <h3 className={`text-sm font-semibold uppercase tracking-wider mb-4 ${cat.color}`}>{cat.title}</h3>
                {cat.items.map(item => (
                  <div key={item.name} className={`flex items-start gap-3 py-3 border-b last:border-0 ${isDark ? 'border-white/[0.04]' : 'border-gray-100'}`}>
                    <span className={`shrink-0 px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.02]' : 'bg-gray-50'} ${cat.color} border-current/20`}>
                      {item.name}
                    </span>
                    <span className={`text-sm leading-relaxed ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{item.desc}</span>
                  </div>
                ))}
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ══ COST ANALYSIS ══ */}
      <section id="cost" className="py-24 relative">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#6DC8E8] to-[#0B5ED7] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              Cost Analysis
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                셀프호스팅 vs API, 비용 최적화 의사결정 과정.
              </p>
            </FadeIn>
          </div>

          <FadeIn>
            <div className={`rounded-2xl border overflow-hidden ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/80 border-gray-200/50'}`}>
              <table className="w-full text-sm">
                <thead>
                  <tr className={isDark ? 'bg-white/[0.03]' : 'bg-gray-50'}>
                    <th className={`px-5 py-3 text-left font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>Service</th>
                    <th className={`px-5 py-3 text-left font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>Method</th>
                    <th className={`px-5 py-3 text-right font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>Cost/mo</th>
                    <th className={`px-5 py-3 text-right font-semibold ${isDark ? 'text-white' : 'text-gray-800'}`}>Cold Start</th>
                  </tr>
                </thead>
                <tbody className={`divide-y ${isDark ? 'divide-white/[0.04]' : 'divide-gray-100'}`}>
                  {[
                    { service: 'Voice AI (before)', method: 'Gemma4Audio (Modal A10G)', cost: '~$46', cold: '60s+', highlight: false },
                    { service: 'Voice AI (after)', method: 'Qwen3.5-Omni (DashScope API)', cost: '~$0.27', cold: '0s', highlight: true },
                    { service: 'Text Chat', method: 'Gemma4 LoRA (Modal A10G)', cost: '~$46', cold: '~30s', highlight: false },
                    { service: 'TTS', method: 'CosyVoice3 (Modal T4)', cost: '~$15', cold: '~58s', highlight: false },
                    { service: 'Infra', method: 'GCP VM (e2-micro)', cost: '~$7', cold: '-', highlight: false },
                  ].map((row, i) => (
                    <tr key={i} className={row.highlight ? isDark ? 'bg-[#0B5ED7]/[0.06]' : 'bg-blue-50/50' : ''}>
                      <td className={`px-5 py-3 ${row.highlight ? 'font-bold' : ''} ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{row.service}</td>
                      <td className={`px-5 py-3 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{row.method}</td>
                      <td className={`px-5 py-3 text-right font-mono ${row.highlight ? 'text-[#0B5ED7] font-bold' : isDark ? 'text-gray-400' : 'text-gray-500'}`}>{row.cost}</td>
                      <td className={`px-5 py-3 text-right ${row.highlight ? 'text-[#0B5ED7] font-bold' : isDark ? 'text-gray-400' : 'text-gray-500'}`}>{row.cold}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </FadeIn>

          <FadeIn delay={0.1} className={`mt-6 p-5 rounded-2xl border ${isDark ? 'bg-[#0B5ED7]/[0.06] border-[#0B5ED7]/20' : 'bg-blue-50/50 border-blue-200/50'}`}>
            <div className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
              <span className="font-bold" style={{ color: ACCENT }}>170x</span> cost reduction by switching from self-hosted Gemma4Audio to Qwen3.5-Omni API.
              OpenAI SDK compatible -- only <code className={`px-1.5 py-0.5 rounded text-xs ${isDark ? 'bg-white/[0.05]' : 'bg-white'}`}>base_url</code> change needed.
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ FOOTER ══ */}
      <footer className={`py-16 border-t ${isDark ? 'border-white/[0.06]' : 'border-gray-200'}`}>
        <div className="max-w-4xl mx-auto px-6 text-center">
          <FadeIn>
            <GradientText
              colors={[ACCENT, ACCENT2, '#4A9BE8', ACCENT2, ACCENT]}
              animationSpeed={5}
              className="font-title text-2xl md:text-4xl mb-4"
              pauseOnHover
            >
              Yang Gunho
            </GradientText>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
              NEXON -- AI Agent Full-Stack Engineer
            </p>
            <div className="flex justify-center gap-4 mt-6">
              <GlassButton href="https://github.com/2rami" target="_blank" rel="noopener noreferrer" size="sm">GitHub</GlassButton>
              <GlassButton href="/portfolio" size="sm">All Portfolios</GlassButton>
            </div>
          </FadeIn>
        </div>
      </footer>
    </div>
  )
}
