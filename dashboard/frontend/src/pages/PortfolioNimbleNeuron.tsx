import { useRef, useEffect, useState, useCallback } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import Lenis from 'lenis'
import Header from '../components/common/Header'
import GradientText from '../components/common/GradientText'
import ScrollFloat from '../components/common/ScrollFloat'
import { useTheme } from '../contexts/ThemeContext'
import ProfileCard from '../components/common/ProfileCard'

/* ── Assets ── */
import CHAR_HERO_LIGHT from '../assets/images/event/imgi_30_ch01_v2.png'
import CHAR_HERO_DARK from '../assets/images/event/char_twins_dark.png'
import TWINS_APPROVE from '../assets/images/event/236_twins_approve.png'
import BG_FOOTER from '../assets/images/event/footer_bg.png'
import FOOTER_PLATFORM from '../assets/images/event/footer_platform.png'
import FOOTER_CHAR from '../assets/images/event/footer_char.png'

/* ── dak.gg CDN ── */
const CDN = 'https://cdn.dak.gg/assets/er'
const GAME_ASSETS = `${CDN}/game-assets/10.6.0`
const TIER_IMG = (id: number) => `${CDN}/images/rank/full/${id}.png`
const CHAR_PROFILE = (key: string) => `${GAME_ASSETS}/CharProfile_${key}_S000.png`

const TIER_METEORITE = TIER_IMG(63)
const TIER_MITHRIL = TIER_IMG(66)
const ALEX_PROFILE = CHAR_PROFILE('Alex')
const ALEX_FULL = `${GAME_ASSETS}/CharResult_Alex_S000.png`

const POPULAR_CHARS = [
  { key: 'Alex', name: '알렉스' }, { key: 'Aya', name: '아야' },
  { key: 'Hyunwoo', name: '현우' }, { key: 'Fiora', name: '피오라' },
  { key: 'Cathy', name: '캐시' }, { key: 'Nadine', name: '나딘' },
  { key: 'Sua', name: '수아' }, { key: 'Eleven', name: '일레븐' },
  { key: 'Lenox', name: '레녹스' }, { key: 'Jackie', name: '재키' },
  { key: 'Hart', name: '하트' }, { key: 'Yuki', name: '유키' },
]

const ALL_TIERS = [
  { id: 1, name: '아이언' }, { id: 2, name: '브론즈' }, { id: 3, name: '실버' },
  { id: 4, name: '골드' }, { id: 5, name: '플래티넘' }, { id: 6, name: '다이아몬드' },
  { id: 66, name: '미스릴' }, { id: 63, name: '메테오라이트' },
  { id: 7, name: '데미갓' }, { id: 8, name: '이터니티' },
]

/* ── SVG Icons ── */
const IconGitHub = ({ size = 18 }: { size?: number }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" width={size} height={size}>
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
  </svg>
)
const IconGlobe = ({ size = 18 }: { size?: number }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} width={size} height={size}>
    <circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
  </svg>
)
const IconExternal = ({ size = 14 }: { size?: number }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} width={size} height={size}>
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
  </svg>
)

/* ── FadeIn ─ */
function FadeIn({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  return (
    <motion.div ref={ref}
      initial={{ opacity: 0, y: 24 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >{children}</motion.div>
  )
}

/* ── SpotlightCard (ReactBits) ── */
function SpotlightCard({ children, className = '', spotlightColor = 'rgba(60, 171, 201, 0.15)' }: {
  children: React.ReactNode; className?: string; spotlightColor?: string
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [pos, setPos] = useState({ x: 0, y: 0 })
  const [opacity, setOpacity] = useState(0)

  return (
    <div ref={ref}
      onMouseMove={e => { if (!ref.current) return; const r = ref.current.getBoundingClientRect(); setPos({ x: e.clientX - r.left, y: e.clientY - r.top }) }}
      onMouseEnter={() => setOpacity(0.6)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative overflow-hidden ${className}`}
    >
      <div className="pointer-events-none absolute inset-0 transition-opacity duration-500"
        style={{ opacity, background: `radial-gradient(circle at ${pos.x}px ${pos.y}px, ${spotlightColor}, transparent 80%)` }} />
      {children}
    </div>
  )
}

/* ── Stat Card ── */
function StatCard({ value, label, image }: { value: string; label: string; image?: string }) {
  const { isDark } = useTheme()
  const isLong = value.length > 3
  return (
    <div className={`text-center px-3 py-5 rounded-2xl border ${
      isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/60 backdrop-blur-sm border-white/40'
    }`}>
      {image ? <img src={image} alt={label} className="w-10 h-10 mx-auto mb-2 object-contain" draggable={false} /> : <div className="w-10 h-10 mb-2" />}
      <div className={`font-bold bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight ${
        isLong ? 'text-sm md:text-base' : 'text-xl md:text-2xl'
      }`}>{value}</div>
      <div className={`text-xs mt-1.5 ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{label}</div>
    </div>
  )
}

/* ── Bullet List ── */
function BulletList({ items, color = '#3cabc9' }: { items: string[]; color?: string }) {
  const { isDark } = useTheme()
  return (
    <ul className="space-y-2.5">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-3">
          <span className="w-1.5 h-1.5 rounded-full mt-2 shrink-0" style={{ backgroundColor: color }} />
          <span className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{item}</span>
        </li>
      ))}
    </ul>
  )
}

/* ── Section Heading ── */
function SectionHeading({ number }: { number: string }) {
  const { isDark } = useTheme()
  return (
    <FadeIn>
      <div className="flex items-center gap-3 mb-2">
        <span className="text-xs font-bold tracking-widest text-[#3cabc9]">{number}</span>
        <div className={`flex-1 h-px ${isDark ? 'bg-white/[0.06]' : 'bg-gray-200'}`} />
      </div>
    </FadeIn>
  )
}

/* ── Tech Tag ── */
function TechTag({ name, color = '#3cabc9' }: { name: string; color?: string }) {
  const { isDark } = useTheme()
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs border ${
      isDark ? 'bg-white/[0.05] border-white/[0.06]' : 'bg-gray-50 border-gray-200'
    }`} style={{ color }}>{name}</span>
  )
}

/* ── Link Button ── */
function LinkButton({ href, children, icon }: { href: string; children: React.ReactNode; icon?: React.ReactNode }) {
  const { isDark } = useTheme()
  return (
    <a href={href} target="_blank" rel="noopener noreferrer"
      className={`inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium rounded-xl border transition-colors ${
        isDark ? 'border-white/[0.08] text-white hover:bg-white/[0.05]' : 'border-gray-200 text-gray-700 hover:bg-gray-50'
      }`}>
      {icon}{children}<IconExternal size={12} />
    </a>
  )
}

/* ── Theme Toggle (StarBorder intro -> shrink) ── */
function ThemeToggle() {
  const { isDark, toggle } = useTheme()
  const [expanded, setExpanded] = useState(true)
  const hasInteracted = useRef(false)

  useEffect(() => {
    const timer = setTimeout(() => { if (!hasInteracted.current) setExpanded(false) }, 4500)
    return () => clearTimeout(timer)
  }, [])

  const handleClick = useCallback(() => {
    toggle()
    if (expanded) { hasInteracted.current = true; setExpanded(false) }
  }, [toggle, expanded])

  const starColor = isDark ? '#7DE8ED' : '#3cabc9'

  return (
    <motion.button onClick={handleClick} layout
      className={`fixed bottom-6 right-6 z-50 cursor-pointer overflow-hidden ${expanded ? 'rounded-2xl' : 'rounded-full'}`}
      initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25, delay: 0.5 }}
      whileHover={{ scale: expanded ? 1.03 : 1.1 }}
      aria-label="Toggle theme" style={{ padding: expanded ? '2px 0' : '0' }}>
      <AnimatePresence>
        {expanded && (<>
          <motion.div className="absolute w-[300%] h-[50%] opacity-70 rounded-full animate-star-bottom z-0"
            style={{ bottom: '-11px', right: '-250%', background: `radial-gradient(circle, ${starColor}, transparent 10%)` }}
            initial={{ opacity: 0 }} animate={{ opacity: 0.7 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }} />
          <motion.div className="absolute w-[300%] h-[50%] opacity-70 rounded-full animate-star-top z-0"
            style={{ top: '-10px', left: '-250%', background: `radial-gradient(circle, ${starColor}, transparent 10%)` }}
            initial={{ opacity: 0 }} animate={{ opacity: 0.7 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }} />
        </>)}
      </AnimatePresence>
      <motion.div layout className={`relative z-[1] flex items-center justify-center overflow-hidden ${
        expanded ? 'gap-3 rounded-2xl px-6 py-4' : 'rounded-full w-12 h-12'
      } ${isDark ? 'bg-gradient-to-b from-[#1a1a2e] to-[#16213e] border border-white/15 text-white' : 'bg-gradient-to-b from-white to-gray-50 border border-gray-200 text-gray-700'}`}
        style={{ boxShadow: expanded ? `0 0 24px ${isDark ? 'rgba(125,232,237,0.25)' : 'rgba(60,171,201,0.2)'}, 0 8px 32px rgba(0,0,0,0.15)` : '0 4px 16px rgba(0,0,0,0.12)' }}>
        <motion.svg layout xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"
          className={`shrink-0 theme-toggle-icon ${expanded ? 'w-6 h-6' : 'w-5 h-5'}`}>
          {isDark ? (
            <><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></>
          ) : (<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>)}
        </motion.svg>
        <AnimatePresence>
          {expanded && (
            <motion.div initial={{ opacity: 0, width: 0 }} animate={{ opacity: 1, width: 'auto' }} exit={{ opacity: 0, width: 0 }}
              transition={{ duration: 0.3 }} className="flex flex-col items-start whitespace-nowrap overflow-hidden">
              <span className="text-sm font-semibold leading-tight">{isDark ? 'Light Mode' : 'Dark Mode'}</span>
              <span className={`text-[11px] leading-tight ${isDark ? 'text-white/50' : 'text-gray-400'}`}>Click to switch</span>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.button>
  )
}

/* ── Side Nav ── */
const NAV_ITEMS = [
  { id: 'hero', label: 'Intro' },
  { id: 'match', label: '공고 매칭' },
  { id: 'data', label: '데이터 분석' },
  { id: 'troubleshoot', label: '트러블슈팅' },
  { id: 'play', label: '플레이 경험' },
  { id: 'dev', label: '개발 역량' },
]

function SideNav() {
  const { isDark } = useTheme()
  const [active, setActive] = useState('hero')
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.scrollY > window.innerHeight * 0.8)
      for (let i = NAV_ITEMS.length - 1; i >= 0; i--) {
        const el = document.getElementById(NAV_ITEMS[i].id)
        if (el && el.getBoundingClientRect().top <= window.innerHeight * 0.4) {
          setActive(NAV_ITEMS[i].id)
          break
        }
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <AnimatePresence>
      {visible && (
        <motion.nav initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
          className="fixed right-5 top-1/2 -translate-y-1/2 z-40 flex flex-col items-end gap-3 max-md:hidden">
          {NAV_ITEMS.map(s => (
            <button key={s.id} onClick={() => document.getElementById(s.id)?.scrollIntoView({ behavior: 'smooth' })}
              className="group flex items-center gap-2.5 cursor-pointer">
              <span className={`text-xs font-medium transition-all duration-200 ${
                active === s.id ? 'text-[#3cabc9] opacity-100' : isDark ? 'text-white/0 group-hover:text-white/70' : 'text-gray-800/0 group-hover:text-gray-500'
              }`}>{s.label}</span>
              <div className="relative flex items-center justify-center w-3 h-3">
                {active === s.id && (
                  <motion.div layoutId="nav-nn" className="absolute inset-[-3px] rounded-full bg-[#3cabc9]/20"
                    transition={{ type: 'spring', stiffness: 300, damping: 25 }} />
                )}
                <div className={`w-2.5 h-2.5 rounded-full transition-all duration-200 ${
                  active === s.id ? 'bg-[#3cabc9] scale-100' : isDark ? 'bg-white/20 group-hover:bg-white/50 scale-75' : 'bg-gray-300 group-hover:bg-gray-400 scale-75'
                }`} />
              </div>
            </button>
          ))}
        </motion.nav>
      )}
    </AnimatePresence>
  )
}

/* ══════════════════════════════════════════════
   NimbleNeuron QA Portfolio
   ══════════════════════════════════════════════ */
export default function PortfolioNimbleNeuron() {
  const { isDark } = useTheme()

  useEffect(() => {
    const lenis = new Lenis({ duration: 0.25, wheelMultiplier: 0.5, easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) })
    ;(window as any).__lenis = lenis
    lenis.scrollTo(0, { immediate: true })
    function raf(time: number) { lenis.raf(time); requestAnimationFrame(raf) }
    requestAnimationFrame(raf)
    return () => { lenis.destroy(); (window as any).__lenis = null }
  }, [])

  return (
    <div className={`min-h-screen font-body selection:bg-[#3cabc9]/20 relative z-0 transition-colors duration-500 ${
      isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'
    }`} style={{ overflowX: 'clip' }}>
      <Header />
      <ThemeToggle />
      <SideNav />

      {/* ══ HERO ══ */}
      <section id="hero" className="relative min-h-screen flex items-center overflow-hidden">
        <div className={`absolute top-20 left-[10%] w-[600px] h-[600px] rounded-full blur-[150px] pointer-events-none ${isDark ? 'bg-[#3cabc9]/[0.07]' : 'bg-[#3cabc9]/[0.12]'}`} />
        <div className={`absolute top-40 right-[10%] w-[500px] h-[500px] rounded-full blur-[150px] pointer-events-none ${isDark ? 'bg-[#e58fb6]/[0.05]' : 'bg-[#e58fb6]/[0.08]'}`} />

        <div className="absolute right-[2%] top-[8%] w-[45%] max-w-[600px] h-[70%] overflow-hidden pointer-events-none z-[2] max-md:hidden">
          <img src={isDark ? CHAR_HERO_DARK : CHAR_HERO_LIGHT} alt=""
            className="w-full h-auto object-cover object-top transition-opacity duration-500" draggable={false} />
        </div>

        <div className="relative z-[5] max-w-6xl mx-auto px-6 lg:px-16">
          <FadeIn>
            <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-6 ${
              isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'
            }`}>Nimble Neuron -- Character QA</span>
          </FadeIn>

          <FadeIn delay={0.1}>
            <GradientText colors={['#3cabc9', '#e58fb6', '#7DE8ED', '#FFA6D7', '#3cabc9']}
              animationSpeed={5} className="!mx-0 font-title text-[24px] md:text-[36px] leading-normal whitespace-nowrap mb-2" pauseOnHover>
              양건호
            </GradientText>
          </FadeIn>

          <FadeIn delay={0.15}>
            <h1 className={`font-title text-4xl md:text-6xl font-bold leading-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
              이터널 리턴<br />
              <span className="bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent">캐릭터 QA</span>
            </h1>
          </FadeIn>

          <FadeIn delay={0.25}>
            <p className={`text-lg md:text-xl leading-relaxed max-w-xl mt-8 font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}
              style={{ fontFamily: "'Paperlogy', sans-serif" }}>
              1,100시간의 코어 플레이 경험과<br />
              게임 데이터 분석 역량을 갖춘 QA 지원자.
            </p>
          </FadeIn>

          <FadeIn delay={0.3}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-14 max-w-2xl">
              <StatCard value="메테오라이트" label="현재 티어" image={TIER_METEORITE} />
              <StatCard value="1,100+" label="플레이 시간" />
              <StatCard value="미스릴+" label="시즌7~" image={TIER_MITHRIL} />
              <StatCard value="알렉스" label="주 캐릭터" image={ALEX_PROFILE} />
            </div>
          </FadeIn>

          <FadeIn delay={0.35}>
            <div className="flex flex-wrap gap-4 mt-10">
              <LinkButton href="https://github.com/2rami/debi-marlene" icon={<IconGitHub />}>GitHub</LinkButton>
              <LinkButton href="https://debimarlene.com" icon={<IconGlobe />}>Live Service</LinkButton>
            </div>
          </FadeIn>
        </div>

        <motion.div className="absolute bottom-10 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 8, 0] }} transition={{ duration: 2, repeat: Infinity }}>
          <div className={`w-px h-12 ${isDark ? 'bg-gradient-to-b from-transparent to-white/20' : 'bg-gradient-to-b from-transparent to-gray-300'}`} />
        </motion.div>
      </section>

      {/* ══ 공고 매칭 ══ */}
        <section id="match" className="py-24 relative">
          <div className={`absolute inset-0 ${isDark ? 'bg-white/[0.01]' : 'bg-gray-50/50'}`} />
          <div className="relative max-w-5xl mx-auto px-6">
            <div className="text-center mb-16">
              <ScrollFloat containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight"
                textClassName="text-4xl md:text-[64px]">공고 매칭</ScrollFloat>
              <FadeIn delay={0.1}>
                <p className={`text-xl md:text-2xl font-semibold max-w-2xl mx-auto mt-6 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  필수/우대 요건에 대한 경험 매칭
                </p>
              </FadeIn>
            </div>

            <SectionHeading number="REQUIRED" />
            <div className="grid md:grid-cols-3 gap-5 mb-12">
              {[
                { icon: '1', title: '전투 시스템 이해', req: 'MOBA, PvP 전투 시스템에 대한 높은 이해도', match: '메테오라이트 티어, 1,100시간+ 플레이. 스킬 구조, 빌드 경로, 전투 타이밍, 메타 변화에 대한 깊은 이해.' },
                { icon: '2', title: '전투 메커니즘 분석', req: '스킬 구조, 상성을 분석하고 논리적으로 설명', match: 'dak.gg API로 50+ 캐릭터 승률/픽률/티어 통계 시스템을 직접 설계. 밸런스 변동을 정량적으로 분석.' },
                { icon: '3', title: '커뮤니케이션', req: '이슈 원인 파악 + 유관 부서 소통 능력', match: '디스코드 커뮤니티 운영, dak.gg API 리버스 엔지니어링으로 이슈 원인 추적. 개발 경험 기반 기술적 소통.' },
              ].map((item, i) => (
                <FadeIn key={i} delay={i * 0.08}>
                  <SpotlightCard className={`p-5 rounded-2xl border h-full ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/80'}`}>
                    <div className="w-8 h-8 rounded-full bg-[#3cabc9]/10 border border-[#3cabc9]/20 flex items-center justify-center mb-3">
                      <span className="text-sm font-bold text-[#3cabc9]">{item.icon}</span>
                    </div>
                    <h4 className={`font-bold text-sm mb-1 ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.title}</h4>
                    <p className={`text-xs mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>{item.req}</p>
                    <div className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{item.match}</div>
                  </SpotlightCard>
                </FadeIn>
              ))}
            </div>

            <SectionHeading number="PREFERRED" />
            <div className="grid md:grid-cols-3 gap-5">
              {[
                { icon: '1', title: '협업 툴', req: 'Jira, Confluence, Slack 등', match: 'Git/GitHub 버전 관리 및 이슈 트래킹. Discord 커뮤니티 운영. Docker/Makefile 배포 자동화.' },
                { icon: '2', title: '코어 플레이어', req: '코어 레벨 수준의 게임 플레이 경험', match: '메테오라이트 티어 (상위). 4시즌 연속 플레이로 메타 변화 전체를 체감.' },
                { icon: '3', title: 'QA 포트폴리오', req: '게임 분석서 혹은 QA 관련 포트폴리오', match: '이터널 리턴 전적/통계 분석 봇을 직접 개발하여 운영 중. 데이터 수집/시각화 시스템이 곧 포트폴리오.' },
              ].map((item, i) => (
                <FadeIn key={i} delay={i * 0.08}>
                  <SpotlightCard className={`p-5 rounded-2xl border h-full ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/80'}`}
                    spotlightColor="rgba(229, 143, 182, 0.15)">
                    <div className="w-8 h-8 rounded-full bg-[#e58fb6]/10 border border-[#e58fb6]/20 flex items-center justify-center mb-3">
                      <span className="text-sm font-bold text-[#e58fb6]">{item.icon}</span>
                    </div>
                    <h4 className={`font-bold text-sm mb-1 ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.title}</h4>
                    <p className={`text-xs mb-3 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>{item.req}</p>
                    <div className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{item.match}</div>
                  </SpotlightCard>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ══ 게임 데이터 분석 ══ */}
        <section id="data" className="py-24 relative">
          <div className="max-w-5xl mx-auto px-6">
            <div className="text-center mb-16">
              <ScrollFloat containerClassName="font-title bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight"
                textClassName="text-4xl md:text-[64px]">게임 데이터 분석</ScrollFloat>
              <FadeIn delay={0.1}>
                <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  Debi & Marlene Discord Bot -- 이터널 리턴 전적/통계 분석 시스템
                </p>
              </FadeIn>
            </div>

            <SectionHeading number="01" />
            <FadeIn><h3 className={`font-bold text-lg mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>데이터 수집 및 구조화</h3></FadeIn>
            <FadeIn delay={0.05}>
              <BulletList items={[
                'dak.gg 웹사이트의 Network 탭을 분석하여 비공개 API 엔드포인트를 전수 수집하고 문서화 (프로젝트에서 가장 도전적인 작업)',
                '50개 이상의 캐릭터, 무기, 특성, 전술스킬, 아이템, 날씨 데이터를 캐시 시스템(GameDataCache)으로 중앙 관리',
                '캐릭터-무기-특성 조합별 승률/픽률 데이터 정규화 및 분석',
                'Eternal Return API + dak.gg API 이중 연동으로 데이터 신뢰성 확보',
              ]} />
            </FadeIn>

            {/* 봇이 관리하는 실험체 데이터 미리보기 */}
            <FadeIn delay={0.1}>
              <div className={`mt-8 p-5 rounded-2xl border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
                <div className={`text-xs font-semibold uppercase tracking-wider mb-4 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
                  봇이 관리하는 실험체 데이터 (dak.gg CDN)
                </div>
                <div className="flex flex-wrap gap-3 items-center">
                  {POPULAR_CHARS.map((c, i) => (
                    <motion.div key={c.key}
                      initial={{ opacity: 0, scale: 0.8 }} whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }} transition={{ delay: i * 0.04, duration: 0.3 }}
                      className="flex flex-col items-center gap-1">
                      <div className={`w-14 h-14 rounded-xl overflow-hidden border-2 ${
                        c.key === 'Alex' ? 'border-[#3cabc9] shadow-lg shadow-[#3cabc9]/20' : isDark ? 'border-white/[0.08]' : 'border-gray-200'
                      }`}>
                        <img src={CHAR_PROFILE(c.key)} alt={c.name} className="w-full h-full object-cover" draggable={false} />
                      </div>
                      <span className={`text-[10px] ${c.key === 'Alex' ? 'text-[#3cabc9] font-bold' : isDark ? 'text-discord-muted' : 'text-gray-400'}`}>{c.name}</span>
                    </motion.div>
                  ))}
                  <div className={`w-14 h-14 rounded-xl border-2 border-dashed flex items-center justify-center ${isDark ? 'border-white/[0.08]' : 'border-gray-200'}`}>
                    <span className={`text-lg ${isDark ? 'text-white/20' : 'text-gray-300'}`}>+75</span>
                  </div>
                </div>
              </div>
            </FadeIn>

            <div className="h-12" />

            <SectionHeading number="02" />
            <FadeIn><h3 className={`font-bold text-lg mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>시각화 및 UI</h3></FadeIn>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <FadeIn delay={0.05}>
                <SpotlightCard className={`p-5 rounded-2xl border h-full ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/80'}`}>
                  <h4 className="text-sm font-semibold uppercase tracking-wider mb-3 text-[#3cabc9]">주요 명령어</h4>
                  {[
                    { cmd: '/전적', desc: '닉네임 검색 -> 시즌별 전적/랭크/MMR/최빈 캐릭터' },
                    { cmd: '/통계', desc: '캐릭터별 승률/픽률/티어 통계, 다중 정렬' },
                    { cmd: '/시즌', desc: '현재 시즌 정보 (시작일, 경과일)' },
                    { cmd: '/동접', desc: 'Steam API 실시간 동접자 수' },
                  ].map((f, i) => (
                    <div key={i} className={`flex items-start gap-3 py-2.5 border-b last:border-0 ${isDark ? 'border-white/[0.04]' : 'border-gray-100'}`}>
                      <span className={`shrink-0 px-2.5 py-0.5 rounded-lg text-xs font-medium border ${isDark ? 'bg-white/[0.02]' : 'bg-gray-50'} text-[#3cabc9] border-[#3cabc9]/20`}>{f.cmd}</span>
                      <span className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{f.desc}</span>
                    </div>
                  ))}
                </SpotlightCard>
              </FadeIn>
              <FadeIn delay={0.1}>
                <SpotlightCard className={`p-5 rounded-2xl border h-full ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/80'}`}
                  spotlightColor="rgba(229, 143, 182, 0.15)">
                  <h4 className="text-sm font-semibold uppercase tracking-wider mb-3 text-[#e58fb6]">시각화 기능</h4>
                  <BulletList color="#e58fb6" items={[
                    'matplotlib 기반 MMR 추이 그래프 (Discord 다크테마 최적화)',
                    'Components V2 (LayoutView) 기반 모던 UI',
                    '티어별/기간별 필터링 (다이아+, 3일/7일)',
                    '승률순/픽률순/티어순 정렬 + 페이지네이션',
                  ]} />
                </SpotlightCard>
              </FadeIn>
            </div>

            {/* 티어 시스템 */}
            <FadeIn delay={0.15}>
              <div className={`p-5 rounded-2xl border mb-8 ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
                <div className={`text-xs font-semibold uppercase tracking-wider mb-4 ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>티어별 데이터 필터링 시스템</div>
                <div className="flex items-center gap-2 overflow-x-auto pb-2">
                  {ALL_TIERS.map((t, i) => {
                    const hl = t.id === 63
                    return (
                      <motion.div key={t.id} initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }} transition={{ delay: i * 0.05 }}
                        className={`flex flex-col items-center gap-1 px-2 py-2 rounded-xl shrink-0 ${
                          hl ? isDark ? 'bg-[#3cabc9]/10 ring-1 ring-[#3cabc9]/30' : 'bg-[#3cabc9]/[0.06] ring-1 ring-[#3cabc9]/20' : ''
                        }`}>
                        <img src={TIER_IMG(t.id)} alt={t.name} className="w-10 h-10 object-contain" draggable={false} />
                        <span className={`text-[10px] whitespace-nowrap ${hl ? 'text-[#3cabc9] font-bold' : isDark ? 'text-discord-muted' : 'text-gray-400'}`}>{t.name}</span>
                      </motion.div>
                    )
                  })}
                </div>
              </div>
            </FadeIn>

            <SectionHeading number="03" />
            <FadeIn><h3 className={`font-bold text-lg mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>QA 관점에서의 가치</h3></FadeIn>
            <FadeIn delay={0.05}>
              <div className={`p-6 rounded-2xl border ${isDark ? 'bg-[#3cabc9]/[0.03] border-[#3cabc9]/10' : 'bg-[#3cabc9]/[0.04] border-[#3cabc9]/15'}`}>
                <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  이 시스템을 운영하면서 패치 전후 캐릭터 수치 변동, 비정상적인 승률 급등/급락,
                  API 응답 구조 변경 등을 실시간으로 감지하고 대응한 경험이 있습니다.
                  이는 캐릭터 QA에서 밸런스 이상이나 스킬 버그를 데이터 기반으로 탐지하는 역량과 직결됩니다.
                </p>
              </div>
            </FadeIn>
          </div>
        </section>

        {/* ══ 트러블슈팅 (Krafton 패턴) ══ */}
        <section id="troubleshoot" className="py-24 relative">
          <div className={`absolute inset-0 ${isDark ? 'bg-white/[0.01]' : 'bg-gray-50/50'}`} />
          <div className="relative max-w-5xl mx-auto px-6">
            <div className="text-center mb-16">
              <ScrollFloat containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight"
                textClassName="text-4xl md:text-[64px]">트러블슈팅</ScrollFloat>
              <FadeIn delay={0.1}>
                <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  봇 개발/운영 중 만난 실제 문제들과 해결 과정
                </p>
              </FadeIn>
            </div>

            {/* API */}
            <FadeIn>
              <h3 className={`text-sm font-bold uppercase tracking-wider mb-4 text-[#3cabc9]`}>API & Data</h3>
            </FadeIn>
            <div className="space-y-4 mb-12">
              {[
                {
                  title: 'dak.gg API 리버스 엔지니어링',
                  problem: '공식 API 문서가 존재하지 않아 봇에 필요한 캐릭터/전적/통계 데이터를 확보할 수 없었음.',
                  cause: 'dak.gg는 내부 API만 사용하며 외부 개발자용 문서를 제공하지 않음. 엔드포인트 구조, 파라미터, 응답 형식이 모두 비공개.',
                  solution: 'Chrome DevTools Network 탭에서 API 호출 패턴을 체계적으로 분석. 요청/응답 구조를 문서화하고, 파라미터 조합 테스트로 숨겨진 기능까지 발견. 프로젝트 내 참조 문서로 관리.',
                  color: '#3cabc9',
                },
                {
                  title: 'API 응답 구조 예고 없는 변경',
                  problem: 'dak.gg API 응답 필드가 예고 없이 변경되어 봇의 전적/통계 명령어가 일괄 오류 발생..',
                  cause: '비공개 API 특성상 변경 공지가 없음. 응답 JSON의 필드명이나 중첩 구조가 변경되면 파서가 즉시 깨짐.',
                  solution: '에러 로그 모니터링 + 유저 리포트로 즉시 감지. 변경된 필드 구조를 분석하여 파서를 업데이트하고, 방어적 코딩(옵셔널 체이닝, 폴백값)을 추가.',
                  color: '#3cabc9',
                },
              ].map((item, i) => (
                <FadeIn key={i} delay={i * 0.05}>
                  <SpotlightCard className={`rounded-2xl border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/80 border-gray-200/50'}`}>
                    <div className="flex items-stretch">
                      <div className="w-1 shrink-0" style={{ backgroundColor: item.color }} />
                      <div className="flex-1 p-5">
                        <div className={`font-bold text-sm mb-3 ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.title}</div>
                        <div className="grid md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#ed4245' }}>Problem</div>
                            <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{item.problem}</div>
                          </div>
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#faa61a' }}>Root Cause</div>
                            <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{item.cause}</div>
                          </div>
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#43b581' }}>Solution</div>
                            <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{item.solution}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </SpotlightCard>
                </FadeIn>
              ))}
            </div>

            {/* Voice / TTS */}
            <FadeIn>
              <h3 className={`text-sm font-bold uppercase tracking-wider mb-4 text-[#e58fb6]`}>Voice & TTS</h3>
            </FadeIn>
            <div className="space-y-4">
              {[
                {
                  title: '음성 채널 TTS/음악 동시접속 충돌',
                  problem: 'TTS와 음악 재생이 동시에 같은 음성 클라이언트를 사용하면서 오디오가 끊기거나 겹침.',
                  cause: 'discord.py의 VoiceClient는 단일 AudioSource만 지원. TTS와 음악이 서로 AudioSource를 덮어쓰는 구조.',
                  solution: 'VoiceManager를 설계하여 음성 클라이언트를 중앙 관리. TTS/음악 우선순위 큐를 구현하여 충돌 없이 순차 재생.',
                  color: '#e58fb6',
                },
                {
                  title: 'CosyVoice3 TTS 비트박스 현상',
                  problem: 'T4 GPU에서 파인튜닝된 CosyVoice3 모델로 추론하면 음성 대신 비트박스 소리가 출력.',
                  cause: 'pretrained checkpoint가 bfloat16으로 저장되어 있는데, T4는 bfloat16 하드웨어 미지원. float16으로 변환해도 모델 로드 시 weight가 다시 bfloat16으로 덮어씌워짐.',
                  solution: 'T4에서도 bfloat16을 소프트웨어 에뮬레이션으로 사용하도록 강제. transformers 4.51.3 버전 고정으로 attention 구현체 충돌 방지.',
                  color: '#e58fb6',
                },
              ].map((item, i) => (
                <FadeIn key={i} delay={i * 0.05}>
                  <SpotlightCard className={`rounded-2xl border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/80 border-gray-200/50'}`}
                    spotlightColor="rgba(229, 143, 182, 0.15)">
                    <div className="flex items-stretch">
                      <div className="w-1 shrink-0" style={{ backgroundColor: item.color }} />
                      <div className="flex-1 p-5">
                        <div className={`font-bold text-sm mb-3 ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.title}</div>
                        <div className="grid md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#ed4245' }}>Problem</div>
                            <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{item.problem}</div>
                          </div>
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#faa61a' }}>Root Cause</div>
                            <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{item.cause}</div>
                          </div>
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: '#43b581' }}>Solution</div>
                            <div className={isDark ? 'text-gray-400' : 'text-gray-500'}>{item.solution}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </SpotlightCard>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ══ 플레이 경험 ══ */}
        <section id="play" className="py-24 relative">
          <div className="max-w-5xl mx-auto px-6">
            <div className="text-center mb-16">
              <ScrollFloat containerClassName="font-title bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight"
                textClassName="text-4xl md:text-[64px]">플레이 경험</ScrollFloat>
            </div>

            {/* Player Card (ReactBits ProfileCard) */}
            <FadeIn>
              <div className="flex justify-center mb-12">
                <ProfileCard
                  avatarUrl={ALEX_FULL}
                  miniAvatarUrl={ALEX_PROFILE}
                  name="양건호"
                  title="Character QA"
                  handle="2rami"
                  status="Meteorite / 1,100h+"
                  contactText="GitHub"
                  showUserInfo={true}
                  onContactClick={() => window.open('https://github.com/2rami/debi-marlene', '_blank')}
                  innerGradient="linear-gradient(145deg, rgba(60,171,201,0.3) 0%, rgba(229,143,182,0.2) 100%)"
                  behindGlowColor="rgba(60, 171, 201, 0.5)"
                  className="w-full max-w-[320px]"
                />
              </div>
            </FadeIn>

            <div className="grid md:grid-cols-2 gap-12">
              <div>
                <FadeIn><h3 className={`font-bold mb-6 text-lg ${isDark ? 'text-white' : 'text-gray-800'}`}>게임 이해도</h3></FadeIn>
                <FadeIn delay={0.05}>
                  <BulletList items={[
                    '캐릭터별 스킬 구조, 쿨다운, 계수, 상호작용 메커니즘 숙지',
                    '캐릭터 상성 관계 및 매치업별 전략 이해',
                    '패치 노트 분석을 통한 메타 변화 예측 및 적응',
                    '빌드 경로(무기/방어구/특성/전술스킬) 최적화 경험',
                    '고티어 환경에서의 엣지 케이스 및 비정상 상호작용 인지',
                  ]} />
                </FadeIn>
              </div>
              <div>
                <FadeIn delay={0.1}><h3 className={`font-bold mb-6 text-lg ${isDark ? 'text-white' : 'text-gray-800'}`}>커뮤니티 활동</h3></FadeIn>
                <FadeIn delay={0.15}>
                  <p className={`text-sm leading-relaxed mb-6 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    디스코드 서버를 운영하며 유저들의 피드백을 수집하고,
                    게임 내 이슈나 밸런스에 대한 토론을 주도한 경험이 있습니다.
                    유저 관점에서의 불편함과 개발자 관점에서의 기술적 제약을
                    동시에 이해하며 소통할 수 있습니다.
                  </p>
                </FadeIn>
                <FadeIn delay={0.2}><h3 className={`font-bold mb-4 text-lg ${isDark ? 'text-white' : 'text-gray-800'}`}>부가 기능</h3></FadeIn>
                <FadeIn delay={0.25}>
                  <BulletList color="#e58fb6" items={[
                    'AI 대화 -- Claude API 기반 캐릭터 페르소나 대화',
                    'TTS -- CosyVoice3 파인튜닝 모델로 캐릭터 음성 합성',
                    '음악 -- YouTube 기반 음악 재생 + 노래 퀴즈',
                  ]} />
                </FadeIn>
              </div>
            </div>
          </div>
        </section>

        {/* ══ 개발 역량 (보조) ══ */}
        <section id="dev" className="py-24 relative">
          <div className={`absolute inset-0 ${isDark ? 'bg-white/[0.01]' : 'bg-gray-50/50'}`} />
          <div className="relative max-w-5xl mx-auto px-6">
            <div className="text-center mb-16">
              <ScrollFloat containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight"
                textClassName="text-4xl md:text-[64px]">개발 역량</ScrollFloat>
              <FadeIn delay={0.1}>
                <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  버그 리포트 품질과 유관 부서 소통에 도움이 되는 기술적 배경
                </p>
              </FadeIn>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-12">
              {[
                { title: 'Backend', color: '#3cabc9', techs: ['Python', 'discord.py', 'Flask', 'Gunicorn'] },
                { title: 'Frontend', color: '#e58fb6', techs: ['React 19', 'TypeScript', 'Vite', 'Tailwind 4'] },
                { title: 'Infra', color: '#7DE8ED', techs: ['GCP VM', 'GCS', 'Docker', 'nginx', 'Makefile'] },
              ].map((group, i) => (
                <FadeIn key={i} delay={i * 0.05}>
                  <SpotlightCard className={`p-5 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/80'}`}>
                    <h4 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: group.color }}>{group.title}</h4>
                    <div className="flex flex-wrap gap-2">
                      {group.techs.map(t => <TechTag key={t} name={t} color={group.color} />)}
                    </div>
                  </SpotlightCard>
                </FadeIn>
              ))}
            </div>

            {/* QA 연결 카드 */}
            <div className="grid md:grid-cols-3 gap-4">
              {[
                { title: '테스트 케이스 설계', desc: '블랙박스 상태의 시스템에서 동작을 분석하고 문서화하는 능력', icon: '1' },
                { title: '버그 재현 및 원인 분석', desc: '예상과 다른 응답을 발견했을 때 근본 원인을 추적하는 습관', icon: '2' },
                { title: '리스크 평가', desc: '변경사항이 전체 시스템에 미치는 영향을 파악하는 시각', icon: '3' },
              ].map((item, i) => (
                <FadeIn key={i} delay={i * 0.05}>
                  <SpotlightCard className={`p-5 rounded-2xl border h-full ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/80'}`}>
                    <div className="w-8 h-8 rounded-full bg-[#3cabc9]/10 border border-[#3cabc9]/20 flex items-center justify-center mb-3">
                      <span className="text-sm font-bold text-[#3cabc9]">{item.icon}</span>
                    </div>
                    <h4 className={`font-bold text-sm mb-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>{item.title}</h4>
                    <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>{item.desc}</p>
                  </SpotlightCard>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ══ FOOTER ══ */}
        <footer className="relative z-[5] overflow-hidden">
          {isDark ? (
            <div className="py-20">
              <div className="max-w-5xl mx-auto px-6 text-center">
                <FadeIn>
                  <img src={TWINS_APPROVE} alt="" className="w-48 h-auto mx-auto mb-8" draggable={false} />
                  <h2 className="text-2xl md:text-3xl font-bold text-white mb-3 font-title">
                    이터널 리턴을 가장 많이 플레이한 QA가 되겠습니다.
                  </h2>
                  <p className="text-discord-muted mb-8">
                    1,100시간의 코어 플레이 경험과 데이터 분석 역량으로,<br />
                    게임의 품질을 유저 눈높이에서 지키겠습니다.
                  </p>
                  <div className="flex justify-center gap-4">
                    <LinkButton href="https://github.com/2rami/debi-marlene" icon={<IconGitHub />}>GitHub</LinkButton>
                    <LinkButton href="https://debimarlene.com/portfolio/nimble-neuron" icon={<IconGlobe />}>Web Portfolio</LinkButton>
                  </div>
                </FadeIn>
              </div>
            </div>
          ) : (
            <>
              <img src={BG_FOOTER} alt="" className="absolute inset-0 w-full h-full object-cover object-bottom" draggable={false} />
              <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#f8fcfd] to-transparent z-[1]" />
              <div className="relative z-[2] flex justify-center pt-20 px-6">
                <FadeIn className="w-full max-w-3xl">
                  <div className="bg-white/60 rounded-3xl border border-white/40 p-8 md:p-12 text-center backdrop-blur-sm">
                    <h2 className="font-title text-3xl md:text-4xl font-bold text-gray-800 mb-4">
                      이터널 리턴을 가장 많이<br />플레이한 QA가 되겠습니다.
                    </h2>
                    <p className="text-gray-500 mb-8 leading-relaxed">
                      1,100시간의 코어 플레이 경험과 데이터 분석 역량으로,<br />
                      게임의 품질을 유저 눈높이에서 지키겠습니다.
                    </p>
                    <div className="flex justify-center gap-4">
                      <LinkButton href="https://github.com/2rami/debi-marlene" icon={<IconGitHub />}>GitHub</LinkButton>
                      <LinkButton href="https://debimarlene.com/portfolio/nimble-neuron" icon={<IconGlobe />}>Web Portfolio</LinkButton>
                    </div>
                  </div>
                </FadeIn>
              </div>
              <div className="relative z-[2] mt-6">
                <img src={FOOTER_PLATFORM} alt="" className="w-full h-auto" draggable={false} />
                <div className="absolute inset-0 z-[1]">
                  <img src={FOOTER_CHAR} alt="" className="w-full h-full object-contain" draggable={false} />
                </div>
              </div>
            </>
          )}
          <div className={`relative z-[3] text-center py-6 text-xs ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
            Yang Gunho -- Built with Claude Code
          </div>
        </footer>

      {/* Print styles */}
      <style>{`
        @media print {
          * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
          body { background: ${isDark ? '#1e1f2e' : '#f8fcfd'} !important; }
          nav, header, .fixed { display: none !important; }
          section { page-break-inside: avoid; padding-top: 2rem !important; padding-bottom: 2rem !important; }
          .min-h-screen { min-height: auto !important; }
          .blur-\\[150px\\] { display: none !important; }
        }
      `}</style>
    </div>
  )
}
