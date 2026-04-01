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
import CHAR_CLASSROOM from '../assets/images/event/char_classroom.png'
import CHAR_SUMMER from '../assets/images/event/char_summer.png'
import CHAR_BATTLE from '../assets/images/event/char_battle.png'
import CHAR_BATTLE2 from '../assets/images/event/char_battle2.png'
import TWINS_APPROVE from '../assets/images/event/236_twins_approve.png'
import BG_FOOTER from '../assets/images/event/footer_bg.png'
import FOOTER_PLATFORM from '../assets/images/event/footer_platform.png'
import FOOTER_CHAR from '../assets/images/event/footer_char.png'

/* Screenshots */
import SS_STATS from '../assets/images/event/screenshot_stats.png'
import SS_RECORD from '../assets/images/event/screenshot_record.png'
import SS_RECORD2 from '../assets/images/event/screenshot_record2.png'
import SS_MUSIC from '../assets/images/event/screenshot_music.png'
import SS_SEASON from '../assets/images/event/screenshot_season.png'

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

/* ── Theme Toggle Button ── */
function ThemeToggle() {
  const { isDark, toggle } = useTheme()
  return (
    <button
      onClick={toggle}
      className={`fixed bottom-6 right-6 z-50 w-12 h-12 rounded-full flex items-center justify-center transition-all shadow-lg hover:scale-110 ${
        isDark ? 'bg-white/10 border border-white/20 text-white' : 'bg-white border border-gray-200 text-gray-700'
      }`}
      aria-label="Toggle theme"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 theme-toggle-icon">
        {isDark ? (
          <>{/* Sun */}<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></>
        ) : (
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        )}
      </svg>
    </button>
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
            </div>
          </div>
        </div>

        {/* Feature 2: TTS + 음악 */}
        <div className="max-w-6xl mx-auto px-6 mt-32 mb-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1 space-y-4">
              <Screenshot src={SS_STATS} alt="캐릭터 통계" delay={0.1} />
              <Screenshot src={SS_MUSIC} alt="음악 재생" delay={0.15} />
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
            </FadeIn>
          </div>
        </div>

        {/* Feature 3: 대시보드 + 시즌 */}
        <div className="max-w-6xl mx-auto px-6 mt-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <FadeIn>
              <SVGTitle lines={['웹', '대시보드']} />
              <p className={`font-bold text-xl md:text-2xl leading-relaxed mt-8 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                Discord OAuth2 기반 웹 관리 시스템.
              </p>
              <p className={`text-base leading-relaxed mt-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                서버별 봇 설정, 환영 메시지, TTS 설정, 퀴즈 곡 관리 등을 웹에서 통합 제공.
                관리자 전용 웹패널로 봇 로그, 서버 현황, 유저 니즈를 분석.
              </p>
              <div className="flex flex-wrap gap-2 mt-6">
                {['React 19', 'Flask', 'OAuth2', 'Tailwind 4', 'Cloudflare'].map(t => (
                  <span key={t} className={`px-3 py-1 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.03] text-gray-400 border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{t}</span>
                ))}
              </div>
            </FadeIn>
            <div>
              <Screenshot src={SS_SEASON} alt="시즌 정보" delay={0.1} />
            </div>
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
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              아키텍처
            </ScrollFloat>
          </div>

          <FadeIn className={`p-6 md:p-8 rounded-3xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 backdrop-blur-sm border-gray-200/80'}`}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Client */}
              <div>
                <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>Client</h4>
                <div className="space-y-2">
                  <div className="px-4 py-3 rounded-xl bg-discord-blurple/10 border border-discord-blurple/20">
                    <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>Discord Users</div>
                    <div className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Slash Commands / Voice Channel</div>
                  </div>
                  {[
                    { name: 'Web Dashboard', desc: 'debimarlene.com (React)' },
                    { name: 'Admin Panel', desc: 'panel.debimarlene.com' },
                  ].map(c => (
                    <div key={c.name} className={`px-4 py-3 rounded-xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-gray-50/80 border-gray-200/50'}`}>
                      <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>{c.name}</div>
                      <div className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{c.desc}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Service */}
              <div>
                <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>Service</h4>
                <div className="space-y-2">
                  <div className="px-4 py-3 rounded-xl bg-[#3cabc9]/10 border border-[#3cabc9]/20">
                    <div className="text-sm font-bold text-[#3cabc9]">Discord Bot</div>
                    <div className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Python / discord.py / Cogs</div>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-[#3cabc9]/10 border border-[#3cabc9]/20">
                    <div className="text-sm font-bold text-[#3cabc9]">Flask API</div>
                    <div className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Gunicorn + nginx</div>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-violet-500/10 border border-violet-500/20">
                    <div className="text-sm font-bold text-violet-400">AI TTS (Modal)</div>
                    <div className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>CosyVoice3 / T4 GPU</div>
                  </div>
                </div>
              </div>

              {/* Infra */}
              <div>
                <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>Infrastructure</h4>
                <div className="space-y-2">
                  <div className="px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
                    <div className="text-sm font-bold text-amber-400">GCP VM</div>
                    <div className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>Docker + Seoul Region</div>
                  </div>
                  {[
                    { name: 'GCS / Artifact Registry', desc: '설정 저장 / 이미지 레지스트리' },
                    { name: 'Cloudflare', desc: 'CDN / 도메인 / SSL' },
                  ].map(c => (
                    <div key={c.name} className={`px-4 py-3 rounded-xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-gray-50/80 border-gray-200/50'}`}>
                      <div className={`text-sm font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>{c.name}</div>
                      <div className={`text-xs ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{c.desc}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* External APIs */}
            <div className={`mt-6 pt-5 border-t ${isDark ? 'border-white/[0.06]' : 'border-gray-200/50'}`}>
              <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>External APIs</h4>
              <div className="flex flex-wrap gap-2">
                {['dak.gg API', 'Eternal Return API', 'YouTube Data API', 'Discord OAuth2', 'Anthropic Claude API', 'HuggingFace'].map(api => (
                  <span key={api} className={`px-3 py-1.5 rounded-lg text-xs border ${isDark ? 'bg-white/[0.03] text-discord-muted border-white/[0.06]' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>{api}</span>
                ))}
              </div>
            </div>
          </FadeIn>
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

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                num: '01', title: 'AI Native 개발', color: '#3cabc9',
                desc: 'Claude Code를 핵심 개발 도구로 활용. 아키텍처 설계, 코드 작성, 디버깅까지 AI 에이전트와의 협업으로 빠르게 반복. 이 포트폴리오 페이지도 Claude Code로 제작.',
              },
              {
                num: '02', title: '컨테이너 배포', color: '#e58fb6',
                desc: 'Docker 이미지 빌드 후 GCP Artifact Registry에 Push. Makefile 기반 자동화로 빌드/배포/롤백을 단일 커맨드로 처리.',
              },
              {
                num: '03', title: '유저 피드백 반영', color: '#7DE8ED',
                desc: '웹패널로 봇 사용 현황과 유저 니즈를 파악. TTS 속도 피드백 → 6종 엔진 비교 후 교체. 저작권 이슈 → 유료화를 후원으로 전환.',
              },
            ].map((item, i) => (
              <FadeIn key={item.num} delay={i * 0.1} className={`p-6 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 backdrop-blur-sm border-gray-200/80'}`}>
                <div className="text-3xl font-bold font-title mb-2" style={{ color: item.color }}>{item.num}</div>
                <h3 className={`font-bold mb-3 text-lg ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.title}</h3>
                <p className={`text-sm leading-relaxed ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{item.desc}</p>
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
