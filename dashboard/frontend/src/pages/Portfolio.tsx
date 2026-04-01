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
// import CHAR_CLASSROOM from '../assets/images/event/char_classroom.png'
// import CHAR_SUMMER from '../assets/images/event/char_summer.png'
// import CHAR_BATTLE from '../assets/images/event/char_battle.png'
// import CHAR_BATTLE2 from '../assets/images/event/char_battle2.png'
import TWINS_APPROVE from '../assets/images/event/236_twins_approve.png'
import BG_FOOTER from '../assets/images/event/footer_bg.png'
import FOOTER_PLATFORM from '../assets/images/event/footer_platform.png'
import FOOTER_CHAR from '../assets/images/event/footer_char.png'

/* Screenshots */
import SS_STATS from '../assets/images/event/screenshot_stats.png'
import SS_RECORD from '../assets/images/event/screenshot_record.png'
import SS_RECORD2 from '../assets/images/event/screenshot_record2.png'
import SS_MUSIC from '../assets/images/event/screenshot_music.png'
import SS_DASHBOARD from '../assets/images/event/screenshot_dashboard.png'
import SS_TTS_SETTINGS from '../assets/images/event/screenshot_tts_settings.png'
import SS_WEBPANEL from '../assets/images/event/screenshot_webpanel.png'

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

/* ── WipeIn (GSAP ScrollTrigger) ── */
// @ts-ignore: reserved for future use
function WipeIn({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    let ctx: ReturnType<typeof import('gsap').default.context> | undefined
    import('gsap').then(({ default: gsap }) =>
      import('gsap/ScrollTrigger').then(({ ScrollTrigger }) => {
        gsap.registerPlugin(ScrollTrigger)
        if (!ref.current) return
        ctx = gsap.context(() => {
          gsap.fromTo(ref.current,
            { clipPath: 'inset(0 100% 0 0)' },
            {
              clipPath: 'inset(0 0% 0 0)',
              duration: 2,
              ease: 'power2.inOut',
              scrollTrigger: { trigger: ref.current, start: 'top 85%', once: true },
            }
          )
        })
      })
    )
    return () => ctx?.revert()
  }, [])
  return <div ref={ref} className={className} style={{ clipPath: 'inset(0 100% 0 0)' }}>{children}</div>
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
                    <stop offset="0%" stopColor="#3cabc9" />
                    <stop offset="100%" stopColor="#e58fb6" />
                  </linearGradient>
                </defs>
              )}
              {isDark ? (
                <>
                  {/* Dark: gray-300 fill + 시안→핑크 그라데이션 stroke */}
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="none" stroke={`url(#${gradId})`} strokeWidth="12" paintOrder="stroke">{line}</text>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="#d1d5db" stroke={`url(#${gradId})`} strokeWidth="5" paintOrder="stroke" style={{ filter: 'drop-shadow(0px 4px 8px rgba(60, 171, 201, 0.3))' }}>{line}</text>
                </>
              ) : (
                <>
                  {/* Light: 시안 fill + 핑크 stroke */}
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="none" stroke="#FFA6D7" strokeWidth="12" paintOrder="stroke">{line}</text>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="#7DE8ED" stroke="#FFA6D7" strokeWidth="5" paintOrder="stroke" style={{ filter: 'drop-shadow(0px 4px 6px rgba(212, 103, 158, 0.4))' }}>{line}</text>
                </>
              )}
            </svg>
          </div>
        )
      })}
    </div>
  )
}

/* ── Timeline Dot ── */
function TimelineDot({ date, title, desc, techs, accent = false, delay = 0 }: {
  date: string; title: string; desc: string; techs: string[]; accent?: boolean; delay?: number
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className="relative pl-8 pb-8 last:pb-0">
      <div className={`absolute left-[7px] top-3 bottom-0 w-px ${isDark ? 'bg-white/[0.06]' : 'bg-gray-200'}`} />
      <div className={`absolute left-0 top-[6px] w-[15px] h-[15px] rounded-full border-2 ${
        accent
          ? 'bg-[#3cabc9]/20 border-[#3cabc9]'
          : isDark ? 'bg-discord-darker border-white/20' : 'bg-white border-gray-300'
      }`} />
      <div className={`text-xs mb-1 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>{date}</div>
      <h4 className={`font-bold mb-1 ${isDark ? 'text-white' : 'text-gray-800'}`}>{title}</h4>
      <p className={`text-sm leading-relaxed mb-2 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{desc}</p>
      <div className="flex flex-wrap gap-1.5">
        {techs.map(t => (
          <span key={t} className={`px-2 py-0.5 rounded-full text-xs border ${
            isDark ? 'bg-white/[0.05] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'
          }`}>{t}</span>
        ))}
      </div>
    </FadeIn>
  )
}

/* ── TTS Card ── */
function TTSCard({ name, result, reason, isFinal = false }: { name: string; result: string; reason: string; isFinal?: boolean }) {
  const { isDark } = useTheme()
  return (
    <div className={`px-4 py-3 rounded-xl border transition-all ${
      isFinal
        ? isDark ? 'bg-[#3cabc9]/10 border-[#3cabc9]/30' : 'bg-[#3cabc9]/[0.06] border-[#3cabc9]/20'
        : isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/80 border-gray-200'
    }`}>
      <div className="flex items-center justify-between mb-1">
        <span className={`text-sm font-bold ${isFinal ? 'text-[#3cabc9]' : isDark ? 'text-white' : 'text-gray-800'}`}>{name}</span>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          result === 'ADOPTED'
            ? 'bg-[#3cabc9]/20 text-[#3cabc9]'
            : isDark ? 'bg-white/[0.05] text-discord-muted' : 'bg-gray-100 text-gray-500'
        }`}>{result}</span>
      </div>
      <p className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{reason}</p>
    </div>
  )
}

/* ── Tech Category Card ── */
function TechCard({ title, color, items, delay = 0 }: {
  title: string; color: string; items: { name: string; reason: string }[]; delay?: number
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className={`p-5 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 backdrop-blur-sm border-gray-200/80'}`}>
      <h3 className={`text-sm font-semibold uppercase tracking-wider mb-4 ${color}`}>{title}</h3>
      {items.map(item => (
        <div key={item.name} className={`flex items-start gap-3 py-3 border-b last:border-0 ${isDark ? 'border-white/[0.04]' : 'border-gray-100'}`}>
          <span className={`shrink-0 px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.02]' : 'bg-gray-50'} ${color} border-current/20`}>
            {item.name}
          </span>
          <span className={`text-sm leading-relaxed ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{item.reason}</span>
        </div>
      ))}
    </FadeIn>
  )
}

/* ── Screenshot with glow ── */
function Screenshot({ src, alt, delay = 0 }: { src: string; alt: string; delay?: number }) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className="relative group">
      <div className={`absolute -inset-3 rounded-3xl blur-xl transition-opacity group-hover:opacity-100 ${
        isDark ? 'bg-[#3cabc9]/10 opacity-50' : 'bg-gradient-to-br from-[#3cabc9]/15 to-[#e58fb6]/15 opacity-60'
      }`} />
      <img
        src={src}
        alt={alt}
        className={`relative w-full h-auto rounded-2xl shadow-2xl border ${isDark ? 'border-white/10' : 'border-white/40'}`}
        draggable={false}
      />
    </FadeIn>
  )
}

/* ── Theme Toggle Button (with intro animation) ── */
function ThemeToggle() {
  const { isDark, toggle } = useTheme()
  const [expanded, setExpanded] = useState(true)
  const hasInteracted = useRef(false)

  // 3초 후 자동 축소 (클릭 안 했으면)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!hasInteracted.current) setExpanded(false)
    }, 3500)
    return () => clearTimeout(timer)
  }, [])

  const handleClick = () => {
    toggle()
    if (expanded) {
      hasInteracted.current = true
      setExpanded(false)
    }
  }

  return (
    <motion.button
      onClick={handleClick}
      layout
      className={`fixed bottom-6 right-6 z-50 flex items-center justify-center gap-2.5 shadow-lg cursor-pointer ${
        expanded ? 'rounded-2xl px-5 py-3' : 'rounded-full w-12 h-12'
      } ${
        isDark ? 'bg-white/10 border border-white/20 text-white' : 'bg-white border border-gray-200 text-gray-700'
      }`}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25, delay: 0.8 }}
      whileHover={{ scale: expanded ? 1.02 : 1.1 }}
      aria-label="Toggle theme"
    >
      <motion.svg layout xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 shrink-0 theme-toggle-icon">
        {isDark ? (
          <>{/* Sun */}<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></>
        ) : (
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        )}
      </motion.svg>
      <AnimatePresence>
        {expanded && (
          <motion.span
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: 'auto' }}
            exit={{ opacity: 0, width: 0 }}
            transition={{ duration: 0.3 }}
            className="text-sm font-medium whitespace-nowrap overflow-hidden"
          >
            {isDark ? '라이트 모드로 전환' : '다크 모드로 전환'}
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  )
}

/* ── Section Navigator ── */
const SECTIONS = [
  { id: 'hero', label: 'Hero' },
  { id: 'journey', label: '개발 여정' },
  { id: 'features', label: '주요 기능' },
  { id: 'tts', label: 'TTS 엔진' },
  { id: 'architecture', label: '아키텍처' },
  { id: 'techstack', label: '기술 스택' },
  { id: 'code', label: '코드' },
  { id: 'deploy', label: '배포 환경' },
  { id: 'process', label: '프로세스' },
  { id: 'match', label: '공고 매칭' },
]

function SectionNav() {
  const { isDark } = useTheme()
  const [active, setActive] = useState('hero')
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const onScroll = () => {
      // Hero 지나면 보이기
      setVisible(window.scrollY > window.innerHeight * 0.5)

      // 현재 섹션 감지
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

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

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
                onClick={() => scrollTo(s.id)}
                className="group flex items-center gap-2.5 cursor-pointer"
              >
                {/* Label — appears on hover or active */}
                <span className={`text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? isDark ? 'text-[#3cabc9] opacity-100' : 'text-[#3cabc9] opacity-100'
                    : isDark ? 'text-white/0 group-hover:text-white/70' : 'text-gray-800/0 group-hover:text-gray-500'
                }`}>
                  {s.label}
                </span>
                {/* Dot */}
                <div className="relative flex items-center justify-center w-3 h-3">
                  {isActive && (
                    <motion.div
                      layoutId="nav-active"
                      className="absolute inset-[-3px] rounded-full bg-[#3cabc9]/20"
                      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                    />
                  )}
                  <div className={`w-2.5 h-2.5 rounded-full transition-all duration-200 ${
                    isActive
                      ? 'bg-[#3cabc9] scale-100'
                      : isDark
                        ? 'bg-white/20 group-hover:bg-white/50 scale-75'
                        : 'bg-gray-300 group-hover:bg-gray-400 scale-75'
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
   Portfolio Page
   ══════════════════════════════════════════════ */
export default function Portfolio() {
  const { isDark } = useTheme()
  const heroRef = useRef(null)

  // Lenis smooth scroll
  useEffect(() => {
    const lenis = new Lenis({ duration: 0.25, wheelMultiplier: 0.5, easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) })
    function raf(time: number) { lenis.raf(time); requestAnimationFrame(raf) }
    requestAnimationFrame(raf)
    return () => lenis.destroy()
  }, [])

  // Hero parallax
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const charY = useTransform(scrollYProgress, [0, 1], ['0%', '20%'])
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '30%'])

  return (
    <div className={`min-h-screen font-body selection:bg-[#3cabc9]/20 relative z-0 transition-colors duration-500 ${
      isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'
    }`} style={{ overflowX: 'clip' }}>
      {/* SVG texture filter */}
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
        {/* Background gradient blobs */}
        <div className={`absolute top-20 left-[10%] w-[600px] h-[600px] rounded-full blur-[150px] pointer-events-none ${isDark ? 'bg-[#3cabc9]/[0.07]' : 'bg-[#3cabc9]/[0.12]'}`} />
        <div className={`absolute top-40 right-[10%] w-[500px] h-[500px] rounded-full blur-[150px] pointer-events-none ${isDark ? 'bg-[#e58fb6]/[0.05]' : 'bg-[#e58fb6]/[0.08]'}`} />

        {/* Character image — upper body crop, swaps on theme */}
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

        {/* Text content */}
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
              colors={['#3cabc9', '#e58fb6', '#7DE8ED', '#FFA6D7', '#3cabc9']}
              animationSpeed={5}
              className="!mx-0 font-title text-[24px] md:text-[36px] leading-normal whitespace-nowrap mb-2"
              pauseOnHover
            >
              데비&마를렌 봇
            </GradientText>
          </FadeIn>

          <FadeIn delay={0.15}>
            <SVGTitle lines={['포트폴리오']} />
          </FadeIn>

          <FadeIn delay={0.25}>
            <p className={`text-lg md:text-xl leading-relaxed max-w-xl mt-8 font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
              AI 캐릭터 TTS + 게임 전적 검색 Discord Bot.<br />
              기획부터 개발, 배포, 운영까지 1인 풀스택 프로젝트.
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

          {/* Quick Stats */}
          <FadeIn delay={0.35}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-14 max-w-2xl">
              {[
                { v: '6+ months', l: '개발 기간' },
                { v: 'Full-Stack', l: '1인 개발/운영' },
                { v: 'GCP', l: '프로덕션 인프라' },
                { v: 'AI Native', l: 'Claude Code 개발' },
              ].map((s, i) => (
                <div key={i} className={`text-center px-4 py-4 rounded-2xl border ${
                  isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/60 backdrop-blur-sm border-white/40'
                }`}>
                  <div className="text-xl md:text-2xl font-bold bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent">{s.v}</div>
                  <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{s.l}</div>
                </div>
              ))}
            </div>
          </FadeIn>
        </motion.div>
      </section>

      {/* ══ AI TOOL JOURNEY ══ */}
      <section id="journey" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              개발 여정
            </ScrollFloat>
            <ScrollFloat
              containerClassName={`font-title mt-4 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}
              textClassName="text-lg md:text-2xl"
              stagger={0.02}
            >
              AI 도구의 발전과 함께 성장한 과정
            </ScrollFloat>
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            {/* AI 도구 발전 */}
            <div>
              <FadeIn>
                <h3 className={`font-bold mb-6 text-lg ${isDark ? 'text-white' : 'text-gray-800'}`}>AI 코딩 도구 발전</h3>
              </FadeIn>
              <TimelineDot delay={0} date="2025.02" title="ChatGPT (복붙 시대)"
                desc="맥북 구매 후 개발 첫 시도. 코드를 복사-붙여넣기하면 위치 오류가 반복되고, AI가 파일 구조를 이해하지 못하는 한계."
                techs={['ChatGPT', 'Copy-Paste']} />
              <TimelineDot delay={0.05} date="2025.04" title="ChatGPT Work with Apps"
                desc="VS Code 연동을 시도했으나 파일 하나만 접근 가능. 그래도 중간고사 웹디자인 과제에서 HTML 사이트 + Vercel 배포 완료."
                techs={['VS Code', 'HTML', 'Vercel']} />
              <TimelineDot delay={0.1} date="2025.06" title="Claude Code CLI" accent
                desc="출시 즉시 도입. 파일시스템 전체 접근이 가능해지면서 기말과제 React + Router 완성. '다른 것도 만들 수 있겠다'는 전환점."
                techs={['Claude Code', 'React', 'React Router']} />
              <TimelineDot delay={0.15} date="2025 방학" title="Discord 봇 개발 시작" accent
                desc="이터널 리턴에 전적 검색봇이 없었음. '내가 만들어야겠다'고 결심."
                techs={['Python', 'discord.py']} />
            </div>

            {/* 인프라 발전 */}
            <div>
              <FadeIn delay={0.1}>
                <h3 className={`font-bold mb-6 text-lg ${isDark ? 'text-white' : 'text-gray-800'}`}>인프라 전환 과정</h3>
              </FadeIn>
              <TimelineDot delay={0} date="2025.08~10" title="AWS 시도"
                desc="첫 클라우드 배포. 예상치 못한 6만원 청구, 복잡한 콘솔."
                techs={['AWS', 'EC2']} />
              <TimelineDot delay={0.05} date="2025.10" title="GCP 전환"
                desc="Google 생태계(GCS, OAuth 등)와의 자연스러운 연동. 비용 예측 가능."
                techs={['GCP']} />
              <TimelineDot delay={0.1} date="2026.01" title="Cloud Run → VM 확정" accent
                desc="Cloud Run은 24시간 상시 실행 불가. Discord 봇은 항상 온라인이어야 하므로 Compute Engine VM 최종 결정."
                techs={['Cloud Run', 'Compute Engine']} />
              <TimelineDot delay={0.15} date="2026.02" title="프로덕션 인프라 완성" accent
                desc="Docker + nginx + Gunicorn + supervisor. Makefile로 빌드/배포/롤백을 단일 커맨드로 자동화."
                techs={['Docker', 'nginx', 'Gunicorn', 'Makefile']} />
            </div>
          </div>
        </div>
      </section>

      {/* ══ FEATURES WITH SCREENSHOTS ══ */}
      <section id="features" className="py-24 relative">
        <div className="text-center mb-16 px-6">
          <ScrollFloat
            containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight"
            textClassName="text-4xl md:text-[64px]"
          >
            주요 기능
          </ScrollFloat>
        </div>

        {/* Feature 1: 전적 검색 */}
        <div className="max-w-6xl mx-auto px-6 mb-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <FadeIn>
              <SVGTitle lines={['전적', '검색']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                이터널리턴 전적과 통계를 Discord 안에서 바로 확인.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                dak.gg 사이트의 Network 탭에서 모든 API endpoint를 수집하고 문서화하여 구축.
                공식 API에 없는 데이터는 hash 기반으로 보완.
                Discord Components V2(LayoutView)로 시각적 UI 구현.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['dak.gg API', 'Eternal Return API', 'Components V2', 'Pillow'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
            </FadeIn>
            <div className="space-y-4">
              <Screenshot src={SS_RECORD} alt="전적 검색" delay={0.1} />
              <Screenshot src={SS_RECORD2} alt="전적 상세" delay={0.15} />
              <Screenshot src={SS_STATS} alt="캐릭터 통계" delay={0.2} />
            </div>
          </div>
        </div>

        {/* Feature 2: TTS + 음악 */}
        <div className="max-w-6xl mx-auto px-6 mt-32 mb-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1 space-y-4">
              <Screenshot src={SS_MUSIC} alt="음악 재생" delay={0.1} />
            </div>
            <FadeIn className="order-1 md:order-2">
              <SVGTitle lines={['TTS &', '음악']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                AI 파인튜닝 캐릭터 음성 + 음악 재생.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                CosyVoice3 모델을 캐릭터 음성 데이터로 파인튜닝. Colab A100/T4에서 학습 후 HuggingFace에 업로드,
                Modal Serverless T4 GPU에서 실시간 합성. YouTube 기반 음악 재생 + 노래 퀴즈 기능.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['CosyVoice3', 'Modal T4', 'HuggingFace', 'yt-dlp', 'FFmpeg'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
              {/* TTS 음성 샘플 */}
              <div className="mt-6 space-y-3">
                <div className={`text-xs font-semibold uppercase tracking-wider ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>CosyVoice3 파인튜닝 음성 샘플</div>
                {[
                  { label: '데비', src: '/audio/demo_debi_desc.wav' },
                  { label: '마를렌', src: '/audio/demo_marlene_desc.wav' },
                ].map(s => (
                  <div key={s.label} className={`flex items-center gap-3 px-4 py-3 rounded-xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-gray-50 border-gray-200'}`}>
                    <span className={`shrink-0 text-sm font-bold w-16 ${isDark ? 'text-[#3cabc9]' : 'text-[#3cabc9]'}`}>{s.label}</span>
                    <audio controls preload="none" className="w-full h-8 [&::-webkit-media-controls-panel]:bg-transparent">
                      <source src={s.src} type="audio/wav" />
                    </audio>
                  </div>
                ))}
                <p className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
                  * 다른 TTS 엔진(GPT-SoVITS, Qwen3-TTS 등) 비교 샘플은 추후 추가 예정
                </p>
              </div>
            </FadeIn>
          </div>
        </div>

        {/* Feature 3: 웹 대시보드 (유저용) */}
        <div className="max-w-6xl mx-auto px-6 mt-32 mb-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <FadeIn>
              <SVGTitle lines={['웹', '대시보드']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                Discord OAuth2 기반 서버 관리.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                서버별 봇 설정, 환영/퇴장 메시지, TTS 음성/속도 커스터마이징,
                임베드 빌더, 퀴즈 곡 관리 등을 웹에서 통합 제공.
                Toss Payments 연동으로 후원 기능도 구현.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['React 19', 'Flask', 'OAuth2', 'Tailwind 4', 'Toss Payments'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
            </FadeIn>
            <div className="space-y-4">
              <Screenshot src={SS_DASHBOARD} alt="서버 대시보드" delay={0.1} />
              <Screenshot src={SS_TTS_SETTINGS} alt="TTS 설정" delay={0.15} />
            </div>
          </div>
        </div>

        {/* Feature 4: 웹패널 (관리자용) */}
        <div className="max-w-6xl mx-auto px-6 mt-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1">
              <Screenshot src={SS_WEBPANEL} alt="웹패널 봇 로그" delay={0.1} />
            </div>
            <FadeIn className="order-1 md:order-2">
              <SVGTitle lines={['웹패널']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                관리자 전용 모니터링 & 운영 도구.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                봇 사용 로그, 서버별 사용 현황, 유저 니즈 분석을 위한 관리자 패널.
                GCS 기반 YouTube 채널 알림, 공지 전송, 서버 상태 모니터링 기능 제공.
                초기 Electron 데스크톱 앱으로도 배포했으나 업데이트 빈도 문제로 웹 전환.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['Flask', 'React', 'GCS', 'YouTube API', 'Cloudflare', 'Electron (레거시)'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
              {/* 웹패널 주요 기능 목록 */}
              <div className={`mt-6 grid grid-cols-2 gap-2`}>
                {[
                  { icon: '>', label: 'YouTube 알림' },
                  { icon: '>', label: '봇 로그 모니터링' },
                  { icon: '>', label: '공지 전송' },
                  { icon: '>', label: '서버 사용 현황' },
                  { icon: '>', label: 'Components V2 렌더링' },
                  { icon: '>', label: '음성채널 상태 표시' },
                ].map(f => (
                  <div key={f.label} className={`flex items-center gap-2 text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    <span className="text-[#3cabc9] font-bold">{f.icon}</span>
                    {f.label}
                  </div>
                ))}
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ══ TTS ENGINE WAR ══ */}
      <section id="tts" className="py-24 relative">
        <div className={`absolute inset-0 ${isDark ? 'bg-white/[0.01]' : 'bg-gray-50/50'}`} />
        <div className="relative max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              TTS 엔진 전쟁
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                봇 사용자 대부분이 원하는 기능: 특정 캐릭터 음성으로 말하기.<br />
                6종의 TTS 엔진을 비교하며 최적의 솔루션을 찾아간 과정.
              </p>
            </FadeIn>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            <FadeIn delay={0.05}><TTSCard name="GPT-SoVITS" result="DROPPED" reason="로컬에서 친구들과 재밌게 사용. Modal 배포 후 반응 좋았지만 속도가 너무 느림" /></FadeIn>
            <FadeIn delay={0.1}><TTSCard name="Coqui TTS" result="DROPPED" reason="한국어 지원 부족" /></FadeIn>
            <FadeIn delay={0.15}><TTSCard name="XTTS" result="DROPPED" reason="속도가 여전히 느림" /></FadeIn>
            <FadeIn delay={0.2}><TTSCard name="MeloTTS" result="DROPPED" reason="CPU 기반이라 가장 빨랐지만 억양 부자연스럽고 기계적" /></FadeIn>
            <FadeIn delay={0.25}><TTSCard name="Qwen3-TTS" result="DROPPED" reason="성능 최고, 최신 모델. 하지만 속도가 여전히 느림" /></FadeIn>
            <FadeIn delay={0.3}><TTSCard name="CosyVoice3" result="ADOPTED" reason="비자기회귀 모델 중 가장 빠르고 음질 우수. Modal T4 GPU에 서버리스 배포" isFinal /></FadeIn>
          </div>

          <FadeIn delay={0.2} className={`mt-6 p-5 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200'}`}>
            <h4 className={`font-bold mb-2 text-sm ${isDark ? 'text-white' : 'text-gray-800'}`}>추가로 시도한 접근</h4>
            <div className={`grid md:grid-cols-2 gap-4 text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              <div>
                <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-800'}`}>Edge TTS + RVC v2 하이브리드</span>
                <p className="mt-1">무료 Edge TTS 출력을 실시간 음성 변환(RVC)으로 캐릭터 음색 적용. 파인튜닝 없이도 가능하지만 품질 한계.</p>
              </div>
              <div>
                <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-800'}`}>현재 한계 & 향후 계획</span>
                <p className="mt-1">Modal에서 스트리밍 불가, GCP VM GPU는 비용 과다. 향후 옴니모델 기반 음성 대화 기능 계획 중.</p>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ ARCHITECTURE ══ */}
      <section id="architecture" className="py-24 relative">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              아키텍처
            </ScrollFloat>
          </div>

          {/* Flow Diagram */}
          <div className="space-y-6">
            {/* Row 1: Clients */}
            <FadeIn>
              <div className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>Clients</div>
              <div className="grid grid-cols-3 gap-3">
                <div className={`px-4 py-4 rounded-2xl text-center border ${isDark ? 'bg-discord-blurple/10 border-discord-blurple/20' : 'bg-indigo-50 border-indigo-200/50'}`}>
                  <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>Discord</div>
                  <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Slash Commands / Voice</div>
                </div>
                <div className={`px-4 py-4 rounded-2xl text-center border ${isDark ? 'bg-[#3cabc9]/10 border-[#3cabc9]/20' : 'bg-cyan-50 border-cyan-200/50'}`}>
                  <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>Dashboard</div>
                  <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>debimarlene.com</div>
                </div>
                <div className={`px-4 py-4 rounded-2xl text-center border ${isDark ? 'bg-[#e58fb6]/10 border-[#e58fb6]/20' : 'bg-pink-50 border-pink-200/50'}`}>
                  <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>Admin Panel</div>
                  <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>panel.debimarlene.com</div>
                </div>
              </div>
            </FadeIn>

            {/* Arrow */}
            <div className="flex justify-center">
              <svg width="24" height="32" viewBox="0 0 24 32" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                <path d="M12 0 L12 24 M6 18 L12 24 L18 18" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>

            {/* Row 2: GCP VM */}
            <FadeIn delay={0.1}>
              <div className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>GCP Compute Engine VM (Seoul)</div>
              <div className={`p-5 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-amber-500/20' : 'bg-amber-50/50 border-amber-200/50'}`}>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-[#3cabc9]/10 border-[#3cabc9]/20' : 'bg-white border-cyan-200/50'}`}>
                    <div className="text-sm font-bold text-[#3cabc9]">Discord Bot</div>
                    <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Python / discord.py</div>
                  </div>
                  <div className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-[#3cabc9]/10 border-[#3cabc9]/20' : 'bg-white border-cyan-200/50'}`}>
                    <div className="text-sm font-bold text-[#3cabc9]">Flask API x2</div>
                    <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Dashboard + Panel</div>
                  </div>
                  <div className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-amber-500/10 border-amber-500/20' : 'bg-white border-amber-200/50'}`}>
                    <div className="text-sm font-bold text-amber-400">nginx</div>
                    <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Reverse Proxy + SSL</div>
                  </div>
                  <div className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-amber-500/10 border-amber-500/20' : 'bg-white border-amber-200/50'}`}>
                    <div className="text-sm font-bold text-amber-400">Docker</div>
                    <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Containerized</div>
                  </div>
                </div>
              </div>
            </FadeIn>

            {/* Arrows to external */}
            <div className="flex justify-center gap-16">
              <svg width="24" height="32" viewBox="0 0 24 32" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                <path d="M12 0 L12 24 M6 18 L12 24 L18 18" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
              <svg width="24" height="32" viewBox="0 0 24 32" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                <path d="M12 0 L12 24 M6 18 L12 24 L18 18" fill="none" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>

            {/* Row 3: External Services */}
            <FadeIn delay={0.2}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* AI / Storage */}
                <div>
                  <div className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>AI & Storage</div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-violet-500/10 border-violet-500/20' : 'bg-violet-50 border-violet-200/50'}`}>
                      <div className="text-sm font-bold text-violet-400">Modal TTS</div>
                      <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>CosyVoice3 / T4</div>
                    </div>
                    <div className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-violet-500/10 border-violet-500/20' : 'bg-violet-50 border-violet-200/50'}`}>
                      <div className="text-sm font-bold text-violet-400">HuggingFace</div>
                      <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Model Registry</div>
                    </div>
                    <div className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-amber-500/10 border-amber-500/20' : 'bg-amber-50 border-amber-200/50'}`}>
                      <div className="text-sm font-bold text-amber-400">GCS</div>
                      <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Settings / Data</div>
                    </div>
                    <div className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-amber-500/10 border-amber-500/20' : 'bg-amber-50 border-amber-200/50'}`}>
                      <div className="text-sm font-bold text-amber-400">Artifact Registry</div>
                      <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Docker Images</div>
                    </div>
                  </div>
                </div>

                {/* External APIs */}
                <div>
                  <div className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>External APIs</div>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { name: 'dak.gg', desc: '전적 데이터', color: 'rose' },
                      { name: 'ER API', desc: '게임 데이터', color: 'rose' },
                      { name: 'YouTube', desc: '음악 / 알림', color: 'rose' },
                      { name: 'Claude API', desc: 'AI 대화', color: 'rose' },
                    ].map(api => (
                      <div key={api.name} className={`px-3 py-3 rounded-xl text-center border ${isDark ? 'bg-rose-500/10 border-rose-500/20' : 'bg-rose-50 border-rose-200/50'}`}>
                        <div className={`text-sm font-bold ${isDark ? 'text-rose-300' : 'text-rose-500'}`}>{api.name}</div>
                        <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{api.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </FadeIn>

            {/* Bottom: CDN */}
            <FadeIn delay={0.25} className={`px-4 py-3 rounded-xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-gray-50 border-gray-200/50'}`}>
              <span className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-700'}`}>Cloudflare</span>
              <span className={`text-xs ml-3 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>CDN / DNS / SSL -- debimarlene.com, panel.debimarlene.com</span>
            </FadeIn>
          </div>

          {/* Architecture Features */}
          <div className="grid md:grid-cols-2 gap-4 mt-10">
            {[
              { title: '다계층 구조 (Layered Architecture)', desc: 'Commands - Views - Services - Core 계층 분리로 관심사 분리 및 유지보수성 확보. Cog 단위로 기능을 독립적으로 관리.' },
              { title: '비동기 처리 (Async-First)', desc: 'asyncio + aiohttp 기반 모든 API 호출 동시 처리. 9개 게임 데이터 API를 asyncio.gather()로 병렬 호출.' },
              { title: '하이브리드 스토리지', desc: 'GCS 우선 + 로컬 백업 폴백 전략. 5초 캐시로 API 부하 최소화. 서버별 설정/퀴즈 목록 등 관리.' },
              { title: '화자별 TTS 파이프라인', desc: 'CosyVoice3 파인튜닝으로 데비/마를렌 캐릭터 음성 분리. HuggingFace에서 모델 Pull → Modal T4 GPU에서 실시간 합성.' },
            ].map((f, i) => (
              <FadeIn key={f.title} delay={0.3 + i * 0.05} className={`p-4 rounded-xl border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
                <h4 className={`text-sm font-bold mb-1 ${isDark ? 'text-white' : 'text-gray-800'}`}>{f.title}</h4>
                <p className={`text-xs leading-relaxed ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{f.desc}</p>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ══ TECH STACK ══ */}
      <section id="techstack" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              기술 스택
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                각 기술을 선택한 구체적인 이유
              </p>
            </FadeIn>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <TechCard title="AI / ML" color="text-violet-400" delay={0} items={[
              { name: 'Claude API', reason: '캐릭터 대화 기능 + NYPC 코드배틀. 향후 옴니모델 음성대화 계획 중' },
              { name: 'CosyVoice3', reason: '6종 TTS 비교 후 채택. 비자기회귀 모델 중 가장 빠르고 음질 우수' },
              { name: 'Modal', reason: '서버리스 GPU. 요청 시에만 T4 GPU 과금' },
              { name: 'Colab', reason: '로컬 4070 Ti는 학습 중 다른 작업 불가. 셀 단위 실행이 직관적' },
            ]} />
            <TechCard title="Backend" color="text-emerald-400" delay={0.05} items={[
              { name: 'Python', reason: '넥슨게임즈 ML팀 친누나 추천. AI/ML 라이브러리 연동 용이' },
              { name: 'discord.py', reason: 'Python 선택의 자연스러운 귀결' },
              { name: 'Flask', reason: '경량 웹 프레임워크. 대시보드/웹패널 API 서버' },
              { name: 'Gunicorn', reason: 'Flask 내장 서버는 동시 요청 처리 불가 → 멀티 워커 프로덕션 서버' },
            ]} />
            <TechCard title="Frontend" color="text-[#3cabc9]" delay={0.1} items={[
              { name: 'React 19', reason: '기말과제에서 성공적으로 사용. Next.js는 당시 문제 있었음' },
              { name: 'TypeScript', reason: '오류를 더 명확하게 잡을 수 있어서' },
              { name: 'Tailwind 4', reason: 'CSS 파일 왔다갔다 하는 게 귀찮아서' },
              { name: 'Framer Motion', reason: '다른 애니메이션 라이브러리보다 가볍고 모션이 다양함' },
            ]} />
            <TechCard title="Infrastructure" color="text-amber-400" delay={0.15} items={[
              { name: 'GCP VM', reason: 'AWS 비용 폭탄 + Cloud Run 상시실행 불가 → 24시간 운영 VM' },
              { name: 'Docker', reason: '로컬과 VM 환경 일관성 보장' },
              { name: 'Cloudflare', reason: '도메인 + CDN + SSL' },
              { name: 'Makefile', reason: '에이전트에게 배포시키면 토큰 낭비. 터미널에서 한 줄로 빌드/배포' },
            ]} />
          </div>
        </div>
      </section>

      {/* ══ CODE HIGHLIGHTS ══ */}
      <section id="code" className="py-24 relative">
        <div className={`absolute inset-0 ${isDark ? 'bg-white/[0.01]' : 'bg-gray-50/50'}`} />
        <div className="relative max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              코드 하이라이트
            </ScrollFloat>
          </div>

          <div className="space-y-8">
            {/* Code 1: GCS 하이브리드 스토리지 */}
            <FadeIn className={`rounded-2xl border overflow-hidden ${isDark ? 'border-white/[0.06]' : 'border-gray-200'}`}>
              <div className={`px-5 py-3 flex items-center justify-between ${isDark ? 'bg-white/[0.04]' : 'bg-gray-100'}`}>
                <span className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>GCS 하이브리드 스토리지 시스템</span>
                <span className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>run/core/config.py</span>
              </div>
              <div className={`px-5 py-3 border-b ${isDark ? 'border-white/[0.04] bg-white/[0.02]' : 'border-gray-100 bg-gray-50/50'}`}>
                <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  <span className={`font-bold ${isDark ? 'text-white' : 'text-gray-700'}`}>문제:</span> Cloud Run의 일시적 스토리지 한계로 상태 유지 불가
                </p>
                <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  <span className={`font-bold ${isDark ? 'text-white' : 'text-gray-700'}`}>해결:</span> GCS를 주 저장소로, 로컬을 백업으로 사용하는 하이브리드 전략. 5초 캐시로 성능 최적화
                </p>
              </div>
              <pre className={`px-5 py-4 text-xs leading-relaxed overflow-x-auto ${isDark ? 'bg-[#0d1117] text-gray-300' : 'bg-[#1e1e2e] text-gray-300'}`} style={{ fontFamily: "'JetBrains Mono', monospace" }}>{`def load_settings():
    """GCS 또는 로컬 백업에서 설정 파일을 로드합니다."""
    global settings_cache, cache_timestamp
    current_time = time.time()

    # 캐시된 설정이 있고 아직 유효하면 사용
    if settings_cache and (current_time - cache_timestamp) < CACHE_DURATION:
        return settings_cache.copy()

    # 1순위: GCS에서 로드
    client = get_gcs_client()
    if client:
        try:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_KEY)
            settings = json.loads(blob.download_as_text())
            settings_cache = settings.copy()
            cache_timestamp = current_time
            return settings
        except Exception as e:
            print(f"[경고] GCS 로드 실패: {e}")

    # 2순위: 로컬 백업 (GCS 실패 시 폴백)
    if os.path.exists(backup_file):
        with open(backup_file, 'r') as f:
            return json.load(f)

    return {"guilds": {}, "users": {}, "global": {}}`}</pre>
            </FadeIn>

            {/* Code 2: 비동기 병렬 API */}
            <FadeIn delay={0.1} className={`rounded-2xl border overflow-hidden ${isDark ? 'border-white/[0.06]' : 'border-gray-200'}`}>
              <div className={`px-5 py-3 flex items-center justify-between ${isDark ? 'bg-white/[0.04]' : 'bg-gray-100'}`}>
                <span className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>비동기 병렬 API 호출 (9개 동시)</span>
                <span className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>run/services/eternal_return/api_client.py</span>
              </div>
              <div className={`px-5 py-3 border-b ${isDark ? 'border-white/[0.04] bg-white/[0.02]' : 'border-gray-100 bg-gray-50/50'}`}>
                <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  <span className={`font-bold ${isDark ? 'text-white' : 'text-gray-700'}`}>특징:</span> 9개의 서로 다른 API를 asyncio.gather()로 동시 호출하여 초기화 시간 단축
                </p>
              </div>
              <pre className={`px-5 py-4 text-xs leading-relaxed overflow-x-auto ${isDark ? 'bg-[#0d1117] text-gray-300' : 'bg-[#1e1e2e] text-gray-300'}`} style={{ fontFamily: "'JetBrains Mono', monospace" }}>{`async def initialize_game_data():
    """게임 데이터 초기화 - 9개 API 병렬 호출"""
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(
        headers=API_HEADERS, timeout=timeout
    ) as session:
        tasks = {
            'current_season': session.get(".../current-season"),
            'seasons': session.get(f"{BASE}/data/seasons?hl=ko"),
            'characters': session.get(f"{BASE}/data/characters?hl=ko"),
            'tiers': session.get(f"{BASE}/data/tiers?hl=ko"),
            'items': session.get(f"{BASE}/data/items?hl=ko"),
            'masteries': session.get(f"{BASE}/data/masteries?hl=ko"),
            'trait_skills': session.get(f"{BASE}/data/trait-skills?hl=ko"),
            'tactical_skills': session.get(f"{BASE}/data/tactical-skills?hl=ko"),
            'weathers': session.get(f"{BASE}/data/weathers?hl=ko"),
        }

        # 모든 응답을 동시에 대기
        responses = await asyncio.gather(
            *tasks.values(), return_exceptions=True
        )`}</pre>
            </FadeIn>

            {/* Code 3: CosyVoice3 Modal TTS */}
            <FadeIn delay={0.15} className={`rounded-2xl border overflow-hidden ${isDark ? 'border-white/[0.06]' : 'border-gray-200'}`}>
              <div className={`px-5 py-3 flex items-center justify-between ${isDark ? 'bg-white/[0.04]' : 'bg-gray-100'}`}>
                <span className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>CosyVoice3 Modal 서버리스 GPU 배포</span>
                <span className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>run/services/tts/cosyvoice3_modal_server.py</span>
              </div>
              <div className={`px-5 py-3 border-b ${isDark ? 'border-white/[0.04] bg-white/[0.02]' : 'border-gray-100 bg-gray-50/50'}`}>
                <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  <span className={`font-bold ${isDark ? 'text-white' : 'text-gray-700'}`}>AI:</span> CosyVoice3 파인튜닝 모델로 캐릭터별 음성 합성. HuggingFace에서 모델 Pull → T4 GPU 실시간 추론
                </p>
              </div>
              <pre className={`px-5 py-4 text-xs leading-relaxed overflow-x-auto ${isDark ? 'bg-[#0d1117] text-gray-300' : 'bg-[#1e1e2e] text-gray-300'}`} style={{ fontFamily: "'JetBrains Mono', monospace" }}>{`import modal

app = modal.App("cosyvoice3-tts")

@app.cls(gpu="T4", image=tts_image, secrets=[hf_secret])
class CosyVoice3Service:
    @modal.enter()
    def load_model(self):
        """컨테이너 시작 시 모델 로드 (cold start ~58초)"""
        from cosyvoice.cli.cosyvoice import CosyVoice3
        self.model = CosyVoice3("CosyVoice3-0.5B-2512")
        # 파인튜닝된 체크포인트 로드
        self.model.load_finetuned("2R4mi/cosyvoice3-eternal-return")

    @modal.method()
    def synthesize(self, text: str, character: str) -> bytes:
        """텍스트를 캐릭터 음성으로 변환"""
        output = self.model.inference_instruct2(
            text, character,
            stream=False
        )
        # PCM -> WAV 변환 후 반환
        return audio_to_wav_bytes(output['tts_speech'])`}</pre>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ══ DEPLOYMENT ══ */}
      <section id="deploy" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              배포 환경
            </ScrollFloat>
          </div>

          {/* 배포 목록 */}
          <FadeIn>
            <div className="grid md:grid-cols-2 gap-4">
              {[
                { label: '봇 서버', value: 'GCP Compute Engine VM + Docker', color: '#3cabc9' },
                { label: 'TTS API', value: 'Modal Serverless GPU (T4)', color: '#9c27b0' },
                { label: '웹 서버', value: 'nginx + Gunicorn + supervisor', color: '#3cabc9' },
                { label: '스토리지', value: 'Google Cloud Storage (설정/데이터)', color: '#fbbc04' },
                { label: '이미지 저장소', value: 'GCP Artifact Registry (Docker)', color: '#fbbc04' },
                { label: '리전', value: 'asia-northeast3 (서울)', color: '#34a853' },
                { label: 'CDN / 도메인', value: 'Cloudflare (debimarlene.com)', color: '#f48120' },
                { label: '배포 자동화', value: 'Makefile (60+ 커맨드)', color: '#e58fb6' },
                { label: '모델 저장소', value: 'HuggingFace (캐릭터별 브랜치)', color: '#9c27b0' },
                { label: '파인튜닝', value: 'Google Colab (A100 / T4)', color: '#9c27b0' },
              ].map((item) => (
                <div key={item.label} className={`flex items-center gap-4 px-4 py-3 rounded-xl border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
                  <div className="w-1 h-8 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                  <div>
                    <div className={`text-xs font-semibold uppercase tracking-wider ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>{item.label}</div>
                    <div className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.value}</div>
                  </div>
                </div>
              ))}
            </div>
          </FadeIn>

          {/* 요청 흐름도 */}
          <FadeIn delay={0.1} className="mt-10">
            <h3 className={`text-lg font-bold mb-6 ${isDark ? 'text-white' : 'text-gray-800'}`}>
              도메인 → 서버 요청 흐름
            </h3>
            <div className="space-y-3">
              {/* Step 1: User */}
              <div className={`px-5 py-4 rounded-2xl border text-center ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/50'}`}>
                <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>유저가 debimarlene.com 접속</div>
              </div>

              <div className="flex justify-center">
                <svg width="24" height="24" viewBox="0 0 24 24" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                  <path d="M12 2 L12 18 M7 13 L12 18 L17 13" fill="none" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>

              {/* Step 2: Cloudflare */}
              <div className="px-5 py-4 rounded-2xl border bg-[#f48120]/10 border-[#f48120]/20">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold text-[#f48120]">Cloudflare</div>
                    <div className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>DNS + SSL + CDN + DDoS 방어</div>
                  </div>
                  <div className={`text-xs max-w-xs text-right ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
                    도메인 구매 후 네임서버를 Cloudflare로 변경. HTTPS 암호화 자동 처리. 배포 시 API로 캐시 퍼지.
                  </div>
                </div>
              </div>

              <div className="flex justify-center">
                <svg width="24" height="24" viewBox="0 0 24 24" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                  <path d="M12 2 L12 18 M7 13 L12 18 L17 13" fill="none" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>

              {/* Step 3: nginx-proxy */}
              <div className="px-5 py-4 rounded-2xl border bg-amber-500/10 border-amber-500/20">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold text-amber-400">nginx-proxy (리버스 프록시)</div>
                    <div className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>VM 포트 80/443에서 도메인별 라우팅</div>
                  </div>
                  <div className={`text-xs max-w-xs text-right ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
                    VIRTUAL_HOST 환경변수로 도메인 → 컨테이너 매핑. 하나의 VM에서 여러 서비스 운영 가능.
                  </div>
                </div>
              </div>

              {/* Split into two branches */}
              <div className="grid md:grid-cols-2 gap-4">
                {/* Branch A: Dashboard */}
                <div className="space-y-3">
                  <div className="flex justify-center">
                    <svg width="24" height="24" viewBox="0 0 24 24" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                      <path d="M12 2 L12 18 M7 13 L12 18 L17 13" fill="none" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                  </div>
                  <div className="px-4 py-4 rounded-2xl border bg-[#3cabc9]/10 border-[#3cabc9]/20">
                    <div className="text-sm font-bold text-[#3cabc9] mb-2">debimarlene.com</div>
                    <div className="space-y-1.5">
                      <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-700'}`}>nginx</span> -- React 정적 파일 서빙 + SPA 라우팅
                      </div>
                      <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-700'}`}>/api/*</span> -- Gunicorn (Flask) 프록시
                      </div>
                      <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-700'}`}>supervisord</span> -- nginx + gunicorn 프로세스 관리
                      </div>
                    </div>
                  </div>
                </div>

                {/* Branch B: Webpanel */}
                <div className="space-y-3">
                  <div className="flex justify-center">
                    <svg width="24" height="24" viewBox="0 0 24 24" className={isDark ? 'text-white/20' : 'text-gray-300'}>
                      <path d="M12 2 L12 18 M7 13 L12 18 L17 13" fill="none" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                  </div>
                  <div className="px-4 py-4 rounded-2xl border bg-[#e58fb6]/10 border-[#e58fb6]/20">
                    <div className="text-sm font-bold text-[#e58fb6] mb-2">panel.debimarlene.com</div>
                    <div className="space-y-1.5">
                      <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-700'}`}>nginx-proxy</span> -- 정적 파일 직접 서빙 (/home/kasa/)
                      </div>
                      <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-700'}`}>/api/*</span> -- Flask 백엔드 (포트 8080)
                      </div>
                      <div className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                        <span className={`font-medium ${isDark ? 'text-white' : 'text-gray-700'}`}>SSE 스트리밍</span> -- 실시간 로그 (proxy_buffering off)
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ DEVELOPMENT PROCESS ══ */}
      <section id="process" className="py-24 relative">
        <div className={`absolute inset-0 ${isDark ? 'bg-white/[0.01]' : 'bg-gray-50/50'}`} />
        <div className="relative max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              개발 프로세스
            </ScrollFloat>
          </div>

          {/* 2x3 grid */}
          <div className="grid md:grid-cols-2 gap-5">
            {[
              {
                num: '01', title: 'AI Native 개발', color: '#3cabc9',
                desc: 'Claude Code를 핵심 개발 도구로 활용. GPT 복붙 → VS Code AI → Claude Code로 발전하며 AI 에이전트와의 협업 방식을 체득. 이 포트폴리오 페이지 자체도 Claude Code로 제작.',
                detail: 'CLAUDE.md로 프로젝트 컨텍스트를 관리하고, 파일 메모리 시스템으로 대화 간 연속성을 유지.',
              },
              {
                num: '02', title: '문제 발견 → 직접 해결', color: '#e58fb6',
                desc: '이터널 리턴에 전적 검색봇이 없다는 문제를 발견하고 직접 개발. dak.gg Network 탭에서 API endpoint를 전부 수집하고 문서화하는 것부터 시작.',
                detail: '공식 API에 없는 데이터는 해시 기반으로 보완. 프로젝트 초기 가장 어려웠던 작업.',
              },
              {
                num: '03', title: '반복적 기술 검증', color: '#7DE8ED',
                desc: 'TTS 엔진 6종을 직접 테스트하고 비교. 속도/음질/비용을 기준으로 평가하여 CosyVoice3를 최종 채택.',
                detail: 'GPT-SoVITS → Coqui → XTTS → MeloTTS → Edge+RVC → Qwen3-TTS → CosyVoice3. 각각의 한계를 경험하고 다음 대안을 찾는 과정.',
              },
              {
                num: '04', title: '인프라 시행착오', color: '#3cabc9',
                desc: 'AWS 비용 폭탄 경험 후 GCP로 전환. Cloud Run의 상시 실행 불가 문제를 발견하고 VM으로 최종 결정.',
                detail: 'Docker + nginx + Gunicorn + supervisor 스택을 직접 구성. Makefile 60+ 커맨드로 빌드/배포/롤백 자동화.',
              },
              {
                num: '05', title: '유저 피드백 기반 의사결정', color: '#e58fb6',
                desc: '웹패널로 실제 사용 데이터를 수집하고 유저 니즈를 분석. TTS 속도 불만 → 엔진 교체, 저작권 이슈 → 유료화를 후원으로 전환.',
                detail: 'Electron 데스크톱 앱 → 업데이트 빈도 문제 → PWA로 전환 시도. 실사용 기반 의사결정.',
              },
              {
                num: '06', title: '지속적 UI/UX 개선', color: '#7DE8ED',
                desc: 'Discord Embed → Components V2(LayoutView) 전환으로 봇 UI를 대폭 개선. 웹 대시보드도 Tailwind 4 + Framer Motion으로 리뉴얼.',
                detail: '다크/라이트 테마, 커스텀 폰트, 패럴랙스 효과, 캐릭터 에셋 활용 등 브랜딩에 투자.',
              },
            ].map((item, i) => (
              <FadeIn key={item.num} delay={i * 0.05} className={`p-6 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 backdrop-blur-sm border-gray-200/80'}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className="text-2xl font-bold font-title" style={{ color: item.color }}>{item.num}</div>
                  <h3 className={`font-bold text-lg ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.title}</h3>
                </div>
                <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>{item.desc}</p>
                <p className={`text-xs leading-relaxed mt-2 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>{item.detail}</p>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ══ KRAFTON MATCH (공고 매칭) ══ */}
      <section id="match" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              공고 매칭
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                크래프톤 AI FDE 공고 요건과 프로젝트 경험의 매칭
              </p>
            </FadeIn>
          </div>

          {/* 필수 요건 */}
          <FadeIn className="mb-8">
            <h3 className={`text-sm font-semibold uppercase tracking-wider mb-4 ${isDark ? 'text-[#3cabc9]' : 'text-[#3cabc9]'}`}>필수 요건</h3>
            <div className={`rounded-2xl border overflow-hidden ${isDark ? 'border-white/[0.06]' : 'border-gray-200'}`}>
              {[
                { req: 'Claude Code 등 코딩 에이전트 활용', match: 'Claude Code로 프로젝트 전체 개발 (GPT → VS Code AI → Claude Code 발전 과정)' },
                { req: 'LLM/AI API 활용', match: 'Anthropic Claude API 직접 통합, TTS 모델 파인튜닝' },
                { req: 'PO 관점 문제정의~구현 독립 수행', match: '풀스택 1인 개발/운영 (봇+대시보드+웹패널+인프라)' },
                { req: 'AI 트렌드 학습 의지', match: 'TTS 엔진 6종 비교, Discord V2, 최신 기술 적극 도입' },
              ].map((item, i) => (
                <div key={i} className={`flex flex-col md:flex-row gap-2 md:gap-6 p-4 ${
                  i !== 3 ? isDark ? 'border-b border-white/[0.04]' : 'border-b border-gray-100' : ''
                } ${isDark ? 'bg-white/[0.02]' : i % 2 === 0 ? 'bg-gray-50/50' : 'bg-white'}`}>
                  <div className={`md:w-1/3 text-sm font-medium ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.req}</div>
                  <div className={`md:w-2/3 text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{item.match}</div>
                </div>
              ))}
            </div>
          </FadeIn>

          {/* 우대 사항 */}
          <FadeIn delay={0.1}>
            <h3 className={`text-sm font-semibold uppercase tracking-wider mb-4 ${isDark ? 'text-[#e58fb6]' : 'text-[#e58fb6]'}`}>우대 사항 (4/4 충족)</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {[
                { title: 'AI 에이전트/워크플로우 자동화', desc: 'Claude AI 봇, TTS 파이프라인, Makefile 60+ 커맨드 자동화' },
                { title: '게임/엔터테인먼트 도메인', desc: '이터널 리턴 전적봇, dak.gg API, 게임 커뮤니티 운영' },
                { title: '클라우드(GCP)', desc: 'Compute Engine, Artifact Registry, GCS 직접 구축' },
                { title: '프롬프트 엔지니어링/RAG', desc: 'Claude API 프롬프트 설계, 캐릭터 페르소나' },
              ].map((item, i) => (
                <div key={i} className={`px-4 py-3 rounded-xl border ${isDark ? 'bg-[#e58fb6]/[0.04] border-[#e58fb6]/20' : 'bg-[#e58fb6]/[0.03] border-[#e58fb6]/15'}`}>
                  <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.title}</div>
                  <div className={`text-xs mt-1 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{item.desc}</div>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ FOOTER ══ */}
      <footer className="relative z-[5] overflow-hidden">
        {isDark ? (
          /* Dark footer */
          <div className="py-20">
            <div className="max-w-5xl mx-auto px-6 text-center">
              <FadeIn>
                <img src={TWINS_APPROVE} alt="" className="w-48 h-auto mx-auto mb-8" draggable={false} />
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-3 font-title">
                  더 자세한 내용이 궁금하시면
                </h2>
                <p className="text-discord-muted mb-8">
                  코드와 커밋 히스토리에서 개발 과정을 확인할 수 있습니다.
                </p>
                <div className="flex justify-center gap-4">
                  <GlassButton href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer" size="sm">
                    <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>GitHub</span>
                  </GlassButton>
                  <GlassButton href="mailto:goenho0613@gmail.com" size="sm">
                    <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" className="w-5 h-5"><path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6z" fill="none" stroke="currentColor" strokeWidth="2"/><polyline points="22,6 12,13 2,6" fill="none" stroke="currentColor" strokeWidth="2"/></svg>Contact</span>
                  </GlassButton>
                </div>
              </FadeIn>
            </div>
          </div>
        ) : (
          /* Light footer with sky background */
          <>
            <img src={BG_FOOTER} alt="" className="absolute inset-0 w-full h-full object-cover object-bottom" draggable={false} />
            <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#f8fcfd] to-transparent z-[1]" />

            <div className="relative z-[2] flex justify-center pt-20 px-6">
              <FadeIn className="w-full max-w-3xl">
                <div className="bg-white/60 rounded-3xl border border-white/40 p-8 md:p-12 text-center">
                  <ScrollFloat
                    containerClassName="font-title text-gray-800 mb-4"
                    textClassName="text-3xl md:text-4xl"
                  >
                    더 자세한 내용이 궁금하시면
                  </ScrollFloat>
                  <p className="text-gray-500 mb-8 leading-relaxed">
                    코드와 커밋 히스토리에서 개발 과정을 확인할 수 있습니다.
                  </p>
                  <div className="flex justify-center gap-4">
                    <GlassButton href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer" size="sm">
                      <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>GitHub</span>
                    </GlassButton>
                    <GlassButton href="mailto:goenho0613@gmail.com" size="sm">
                      <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" className="w-5 h-5"><path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6z" fill="none" stroke="currentColor" strokeWidth="2"/><polyline points="22,6 12,13 2,6" fill="none" stroke="currentColor" strokeWidth="2"/></svg>Contact</span>
                    </GlassButton>
                  </div>
                </div>
              </FadeIn>
            </div>

            {/* Footer character + platform */}
            <div className="relative z-[2] mt-6">
              <img src={FOOTER_PLATFORM} alt="" className="w-full h-auto" draggable={false} />
              <div className="absolute inset-0 z-[1]">
                <img src={FOOTER_CHAR} alt="" className="w-full h-full object-contain" draggable={false} />
              </div>
            </div>
          </>
        )}

        {/* Copyright */}
        <div className={`relative z-[3] text-center py-6 text-xs ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
          Yang Gunho -- Built with Claude Code
        </div>
      </footer>
    </div>
  )
}
