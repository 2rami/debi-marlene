import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { useEffect, useState, useRef, useCallback } from 'react'
import Header from '../components/common/Header'
import { api } from '../services/api'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import { Users, Server, Terminal, ChevronDown } from 'lucide-react'
import GreetingPreview from '../components/landing/GreetingPreview'
import DonationModal from '../components/common/DonationModal'

// ── Backgrounds ──
import BG_BIKE from '../assets/images/event/imgi_31_bg02.png'
import BG_SKY from '../assets/images/event/imgi_28_bg01.png'
import BG_CLOUD from '../assets/images/event/imgi_29_bg03.png'
import BG_NOTEBOOK from '../assets/images/event/imgi_86_bg_box02.png'
import BG_GRID from '../assets/images/event/imgi_87_bg_box03.png'
import BG_PINKBAR from '../assets/images/event/imgi_89_bg_box04.png'
import BG_SEC from '../assets/images/event/imgi_81_bg_sec01.png'

// ── Characters ──
import CHAR_HERO from '../assets/images/event/imgi_30_ch01.png'
import CHAR_SITTING from '../assets/images/event/imgi_62_ch04.png'
import CHAR_02 from '../assets/images/event/imgi_47_ch02.png'
import CHAR_03 from '../assets/images/event/imgi_48_ch03.png'
import CHAR_05 from '../assets/images/event/imgi_49_ch05.png'
import CHAR_06 from '../assets/images/event/imgi_50_ch06.png'
import CHAR_07 from '../assets/images/event/imgi_51_ch07.png'

// ── UI Elements ──
import TXT_AFTERSCHOOL from '../assets/images/event/imgi_32_txt01.png'
import NEW_BADGE from '../assets/images/event/imgi_77_new.png'
import CURSOR from '../assets/images/event/imgi_45_cursor01.png'
import GAME_FRONT from '../assets/images/event/imgi_46_game_front01.png'
import LOGO from '../assets/images/event/imgi_2_logo_white.png'
import BTN_START from '../assets/images/event/imgi_105_btn_start.png'

// ── Card Frames ──
import CARD_CYAN from '../assets/images/event/imgi_100_bg_rw01.png'
import CARD_PINK from '../assets/images/event/imgi_102_bg_rw02.png'

// ── Game Buttons ──
import BTN_GAME01 from '../assets/images/event/imgi_92_btn_game01.png'
import BTN_GAME02 from '../assets/images/event/imgi_93_btn_game02.png'
import BTN_GAME03 from '../assets/images/event/imgi_95_btn_game03.png'
import BTN_GAME04 from '../assets/images/event/imgi_96_btn_game04.png'
import BTN_GAME05 from '../assets/images/event/imgi_97_btn_game05.png'

interface BotStats {
  users: number
  servers: number
  commands: number
}

/* ─── Animated Counter ─── */
function useCountUp(target: number, isInView: boolean, duration = 1600) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    if (!isInView || target === 0) return
    let start = 0
    const startTime = performance.now()
    const step = (now: number) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
      const current = Math.round(eased * target)
      if (current !== start) {
        start = current
        setCount(current)
      }
      if (progress < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [target, isInView, duration])
  return count
}

/* ─── 3D Tilt Card ─── */
function TiltCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const [transform, setTransform] = useState('')

  const handleMove = useCallback((e: React.MouseEvent) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width - 0.5
    const y = (e.clientY - rect.top) / rect.height - 0.5
    setTransform(`perspective(600px) rotateY(${x * 12}deg) rotateX(${y * -12}deg) scale3d(1.03,1.03,1.03)`)
  }, [])

  const handleLeave = useCallback(() => {
    setTransform('perspective(600px) rotateY(0deg) rotateX(0deg) scale3d(1,1,1)')
  }, [])

  return (
    <div
      ref={ref}
      onMouseMove={handleMove}
      onMouseLeave={handleLeave}
      className={className}
      style={{ transform, transition: 'transform 0.35s cubic-bezier(.03,.98,.52,.99)', willChange: 'transform' }}
    >
      {children}
    </div>
  )
}

/* ─── Stagger Text ─── */
function StaggerText({ text, className = '', delay = 0 }: { text: string; className?: string; delay?: number }) {
  return (
    <span className={className} aria-label={text}>
      {text.split('').map((char, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, y: 30, filter: 'blur(6px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          transition={{ duration: 0.5, delay: delay + i * 0.04, ease: [0.22, 1, 0.36, 1] }}
          className="inline-block"
          style={{ whiteSpace: char === ' ' ? 'pre' : undefined }}
        >
          {char}
        </motion.span>
      ))}
    </span>
  )
}

/* ═══════════════════════════════════════════════════
   LANDING PAGE
   ═══════════════════════════════════════════════════ */
export default function Landing() {
  const { user, login } = useAuth()
  const { isDark } = useTheme()
  const navigate = useNavigate()
  const [stats, setStats] = useState<BotStats>({ users: 0, servers: 0, commands: 17 })
  const [botClientId, setBotClientId] = useState<string | null>(null)
  const [isDonationModalOpen, setIsDonationModalOpen] = useState(false)

  // Scroll parallax
  const { scrollY } = useScroll()
  const heroBgY = useTransform(scrollY, [0, 1000], [0, 300])
  const heroMidY = useTransform(scrollY, [0, 800], [0, 150])
  const heroCharY = useTransform(scrollY, [0, 600], [0, -80])
  const heroCharScale = useTransform(scrollY, [0, 400], [1, 1.08])
  const heroOverlayOpacity = useTransform(scrollY, [200, 600], [0, 0.6])

  // Stats animated counters
  const statsRef = useRef(null)
  const statsInView = useInView(statsRef, { once: true, margin: '-60px' })
  const userCount = useCountUp(stats.users, statsInView)
  const serverCount = useCountUp(stats.servers, statsInView)
  const commandCount = useCountUp(stats.commands, statsInView, 800)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get<{ stats: BotStats; botClientId: string }>('/bot/stats')
        setStats(res.data.stats)
        setBotClientId(res.data.botClientId)
      } catch { /* 기본값 사용 */ }
    }
    fetchStats()
  }, [])

  const handleDashboard = () => {
    if (user) navigate('/dashboard')
    else login()
  }

  const getInviteUrl = () => {
    if (!botClientId) return 'https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands'
    return `https://discord.com/api/oauth2/authorize?client_id=${botClientId}&permissions=8&scope=bot%20applications.commands`
  }

  // Dynamic theme colors for section backgrounds
  const pageBg = isDark ? '#0f1219' : '#ffffff'
  const blendColor = isDark ? '#0f1219' : '#ffffff'
  const midBlend = isDark ? '#151a24' : '#fdf6ee'

  return (
    <div
      className="min-h-screen overflow-x-hidden font-body selection:bg-debi-primary/30 transition-colors duration-500"
      style={{ backgroundColor: pageBg, color: isDark ? '#e2e8f0' : undefined }}
    >
      <Header />
      <DonationModal isOpen={isDonationModalOpen} onClose={() => setIsDonationModalOpen(false)} />

      {/* Grain overlay */}
      <div className="fixed inset-0 z-[60] pointer-events-none opacity-[0.035] mix-blend-overlay grain-overlay" />

      {/* ═══════════════════════════════════════════
          HERO
          ═══════════════════════════════════════════ */}
      <section className="relative h-screen min-h-[700px] overflow-hidden">
        {/* Layer 0: Bike scene — BIGGER, more prominent */}
        <motion.div style={{ y: heroBgY }} className="absolute inset-0 -top-32 z-0">
          <img
            src={BG_BIKE}
            alt=""
            className="w-full h-[160%] object-cover object-center"
            style={{ opacity: isDark ? 0.35 : 0.55 }}
          />
        </motion.div>

        {/* Layer 1: Sky overlay */}
        <motion.div style={{ y: heroMidY }} className="absolute inset-0 -top-16 z-[1]">
          <img
            src={BG_SKY}
            alt=""
            className="w-full h-[120%] object-cover"
            style={{ opacity: isDark ? 0.7 : 1 }}
          />
        </motion.div>

        {/* Dark overlay for dark mode */}
        {isDark && (
          <div className="absolute inset-0 z-[1] bg-[#0f1219]/40" />
        )}

        {/* Vignette */}
        <div className="absolute inset-0 z-[2]">
          <div
            className="absolute top-0 inset-x-0 h-40"
            style={{ background: `linear-gradient(to bottom, ${isDark ? 'rgba(15,18,25,0.5)' : 'rgba(0,0,0,0.2)'}, transparent)` }}
          />
          <motion.div
            style={{ opacity: heroOverlayOpacity }}
            className="absolute inset-0"
            key={`overlay-${isDark}`}
          >
            <div className="w-full h-full" style={{ backgroundColor: blendColor }} />
          </motion.div>
        </div>

        {/* Bottom blend */}
        <div
          className="absolute bottom-0 inset-x-0 h-64 z-[3]"
          style={{ background: `linear-gradient(to top, ${blendColor}, ${blendColor}b3, transparent)` }}
        />

        {/* Content */}
        <div className="relative z-10 max-w-[1440px] mx-auto px-6 lg:px-12 h-full flex items-center">
          <div className="grid xl:grid-cols-[1.1fr_0.9fr] gap-8 items-center w-full">
            {/* Left: Text */}
            <div className="relative z-10 pt-20 xl:pt-0">
              <motion.img
                src={NEW_BADGE}
                alt="NEW"
                className="h-9 mb-5 drop-shadow-md"
                initial={{ opacity: 0, scale: 0.5, rotate: -12 }}
                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
              />

              <div className="mb-2">
                <StaggerText
                  text="데비&마를렌 봇"
                  className="font-title gradient-text-title text-[clamp(26px,3.2vw,40px)]"
                  delay={0.2}
                />
              </div>

              <motion.h1
                className="font-display font-bold text-[clamp(56px,7.5vw,110px)] leading-[0.95] mb-5 hero-title-shadow"
                style={{ color: isDark ? '#a3bfdb' : '#8ea9c9' }}
                initial={{ opacity: 0, y: 60, scale: 0.9 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 1, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
              >
                대시보드
              </motion.h1>

              <motion.img
                src={TXT_AFTERSCHOOL}
                alt="Debi & Marlene After School"
                className="h-[clamp(70px,11vw,145px)] mb-7 drop-shadow-lg"
                style={{ filter: isDark ? 'brightness(1.1)' : undefined }}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.8 }}
              />

              <motion.p
                className="text-lg md:text-xl mb-10 leading-relaxed max-w-md font-medium"
                style={{ color: isDark ? '#94a3b8' : '#4b5563' }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 1 }}
              >
                이터널리턴 전적부터 고품질 TTS,<br />
                완벽한 음악 재생 기능까지.
              </motion.p>

              {/* CTA Buttons — no text shadows */}
              <motion.div
                className="flex flex-wrap items-center gap-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.2 }}
              >
                <a
                  href={getInviteUrl()}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group relative inline-block hover:scale-105 hover:-rotate-1 active:scale-95 transition-transform duration-200"
                >
                  <img src={BTN_START} alt="" className="h-[68px] w-auto drop-shadow-xl opacity-90 group-hover:opacity-100 group-hover:drop-shadow-[0_8px_24px_rgba(229,143,182,0.4)] transition-all" />
                  <span className="absolute inset-0 flex items-center justify-center font-title text-xl text-white pl-2">
                    봇 초대하기
                  </span>
                </a>
                <button
                  onClick={handleDashboard}
                  className="group relative inline-block hover:scale-105 hover:rotate-1 active:scale-95 transition-transform duration-200"
                >
                  <img src={BTN_GAME01} alt="" className="h-[63px] w-auto drop-shadow-lg opacity-90 group-hover:opacity-100 group-hover:drop-shadow-[0_8px_24px_rgba(60,171,201,0.4)] transition-all" />
                  <span className="absolute inset-0 flex items-center justify-center font-title text-lg text-white">
                    대시보드
                  </span>
                </button>
              </motion.div>
            </div>

            {/* Right: Hero Character */}
            <motion.div
              style={{ y: heroCharY, scale: heroCharScale }}
              className="hidden xl:block relative h-[700px]"
            >
              <motion.img
                src={CHAR_HERO}
                alt="Debi & Marlene"
                className="absolute bottom-0 right-0 h-[110%] w-auto object-contain drop-shadow-[0_20px_60px_rgba(0,0,0,0.25)]"
                initial={{ opacity: 0, x: 80, scale: 0.85 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                transition={{ duration: 1.2, delay: 0.4, type: 'spring', stiffness: 50 }}
              />
              <motion.img
                src={CHAR_07}
                alt=""
                className="absolute -top-4 right-8 w-28 drop-shadow-lg opacity-75"
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut' }}
              />
            </motion.div>
          </div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-1"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
        >
          <span className="text-xs font-medium tracking-widest uppercase" style={{ color: isDark ? '#64748b' : '#9ca3af' }}>
            Scroll
          </span>
          <motion.div animate={{ y: [0, 8, 0] }} transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}>
            <ChevronDown className="w-5 h-5" style={{ color: isDark ? '#64748b' : '#9ca3af' }} />
          </motion.div>
        </motion.div>
      </section>

      {/* ═══════════════════════════════════════════
          FEATURES
          ═══════════════════════════════════════════ */}
      <section className="relative overflow-hidden">
        {/* BG: Cloud sky */}
        <div className="absolute inset-0 z-0">
          <img
            src={BG_CLOUD}
            alt=""
            className="w-full h-full object-cover object-top"
            style={{ opacity: isDark ? 0.3 : 1 }}
          />
          {isDark && <div className="absolute inset-0 bg-[#0f1219]/50" />}
          <div
            className="absolute top-0 inset-x-0 h-[25%]"
            style={{ background: `linear-gradient(to bottom, ${blendColor}, transparent)` }}
          />
        </div>

        {/* Cards */}
        <div className="relative z-10 max-w-[1440px] mx-auto px-6 lg:px-12 pt-12 pb-12">
          <motion.div
            className="text-center mb-14"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 0.7 }}
          >
            <p className="font-title gradient-text-title text-2xl mb-2">주요 기능</p>
            <h2 className="font-title text-3xl md:text-4xl" style={{ color: isDark ? '#cbd5e1' : '#374151' }}>
              하나의 봇으로 모든 기능을
            </h2>
          </motion.div>

          <div className="flex flex-col md:flex-row justify-center items-center gap-6 md:gap-10 mb-14">
            {([
              { frame: CARD_CYAN, color: '#3cabc9', title: '고품질 TTS', desc: '데비와 마를렌의 목소리로\n채팅을 읽어줍니다', delay: 0, from: -60 },
              { frame: CARD_CYAN, color: '#3cabc9', title: '전적 검색', desc: '이터널리턴 전적과\n캐릭터 통계를 한눈에', delay: 0.12, from: 0 },
              { frame: CARD_PINK, color: '#e58fb6', title: '음악 재생', desc: '유튜브 검색 기반\n음악과 대기열 관리', delay: 0.24, from: 60 },
            ] as const).map((card, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: card.from, y: 30 }}
                whileInView={{ opacity: 1, x: 0, y: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.7, delay: card.delay, ease: [0.22, 1, 0.36, 1] }}
              >
                <TiltCard className="relative w-[250px] h-[345px] shrink-0 cursor-default">
                  <img src={card.frame} alt="" className="absolute inset-0 w-full h-full object-contain drop-shadow-lg" />
                  <div className="relative z-10 flex flex-col items-center justify-center h-full px-6 pt-12 pb-8 text-center">
                    <p className="font-title text-xl mb-3" style={{ color: card.color }}>{card.title}</p>
                    <p className="text-sm leading-relaxed whitespace-pre-line" style={{ color: isDark ? '#94a3b8' : '#4b5563' }}>
                      {card.desc}
                    </p>
                  </div>
                </TiltCard>
              </motion.div>
            ))}
          </div>

          {/* Commands button — no text shadow */}
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Link
              to="/commands"
              className="group relative inline-block hover:scale-105 active:scale-95 transition-transform duration-200"
            >
              <img src={BTN_GAME02} alt="" className="h-[55px] drop-shadow-lg opacity-90 group-hover:opacity-100 group-hover:drop-shadow-[0_6px_20px_rgba(60,171,201,0.35)] transition-all" />
              <span className="absolute inset-0 flex items-center justify-center font-title text-base text-white">
                명령어 확인
              </span>
            </Link>
          </motion.div>
        </div>

        {/* Decorative characters */}
        <motion.img
          src={CHAR_03}
          alt=""
          className="absolute left-[10%] top-[38%] w-28 pointer-events-none z-10"
          style={{ opacity: isDark ? 0.3 : 0.5 }}
          animate={{ y: [0, -12, 0], rotate: [0, -3, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.img
          src={CHAR_05}
          alt=""
          className="absolute right-[7%] top-[32%] w-24 pointer-events-none z-10"
          style={{ opacity: isDark ? 0.25 : 0.4 }}
          animate={{ y: [0, -8, 0], rotate: [39, 42, 39] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        />
        <motion.img
          src={CHAR_07}
          alt=""
          className="absolute right-[14%] top-[8%] w-24 pointer-events-none z-10"
          style={{ opacity: isDark ? 0.25 : 0.4 }}
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
        />

        {/* Sitting Characters */}
        <div className="relative z-10 pt-16 min-h-[55vh] flex flex-col justify-end items-center">
          <motion.img
            src={CHAR_SITTING}
            alt="Debi & Marlene"
            className="w-[50%] max-w-[780px] h-auto drop-shadow-[0_12px_40px_rgba(0,0,0,0.25)]"
            initial={{ opacity: 0, y: 80, scale: 0.92 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 1.4, ease: [0.22, 1, 0.36, 1] }}
          />
        </div>

        <motion.img src={CURSOR} alt="" className="absolute left-[24%] bottom-[16%] w-20 pointer-events-none z-10"
          style={{ opacity: isDark ? 0.25 : 0.4 }}
          animate={{ y: [0, -6, 0], x: [0, 4, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.img src={CHAR_02} alt="" className="absolute right-[11%] bottom-[9%] w-20 pointer-events-none z-10"
          style={{ opacity: isDark ? 0.25 : 0.4 }}
          animate={{ y: [0, -8, 0], rotate: [0, 5, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 0.8 }}
        />
        <motion.img src={CHAR_06} alt="" className="absolute left-[4%] bottom-[14%] w-28 pointer-events-none z-10"
          style={{ opacity: isDark ? 0.2 : 0.3 }}
          animate={{ y: [0, -6, 0], rotate: [33, 36, 33] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1.5 }}
        />

        {/* Bottom blend */}
        <div
          className="absolute bottom-0 inset-x-0 h-32 z-[5]"
          style={{ background: `linear-gradient(to top, ${midBlend}, transparent)` }}
        />
      </section>

      {/* ═══════════════════════════════════════════
          BOARD — Greeting + Stats
          ═══════════════════════════════════════════ */}
      <section className="relative py-20 overflow-hidden">
        <img
          src={BG_NOTEBOOK}
          alt=""
          className="absolute inset-0 w-full h-full object-cover z-0"
          style={{ opacity: isDark ? 0.25 : 1, filter: isDark ? 'brightness(0.5)' : undefined }}
        />
        {isDark && <div className="absolute inset-0 bg-[#151a24]/70 z-0" />}

        <div className="relative z-10 max-w-[1440px] mx-auto px-6 lg:px-12">
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.7 }}
          >
            <p className="font-title gradient-text-title text-2xl mb-2">인사말 카드</p>
            <h2 className="font-title text-3xl md:text-4xl" style={{ color: isDark ? '#cbd5e1' : '#374151' }}>
              새 멤버를 환영하세요
            </h2>
          </motion.div>

          <motion.div
            className="relative max-w-[1100px] mx-auto"
            initial={{ opacity: 0, y: 40, scale: 0.97 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          >
            <img src={BG_GRID} alt="" className="w-full rounded-xl drop-shadow-lg" style={{ opacity: isDark ? 0.7 : 1 }} />
            <div className="absolute inset-0 flex items-center justify-center p-4 md:p-10">
              <div
                className="w-full max-w-3xl backdrop-blur-sm rounded-2xl shadow-2xl border p-4"
                style={{
                  backgroundColor: isDark ? 'rgba(30,35,50,0.85)' : 'rgba(255,255,255,0.85)',
                  borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.6)',
                }}
              >
                <GreetingPreview />
              </div>
            </div>
          </motion.div>

          {/* Stats bar */}
          <motion.div
            ref={statsRef}
            className="relative max-w-[1100px] mx-auto mt-8"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            <img src={BG_PINKBAR} alt="" className="w-full rounded-xl drop-shadow-md" />
            <div className="absolute inset-0 flex items-center justify-center gap-8 md:gap-20">
              {[
                { label: '누적 유저', value: userCount, icon: Users },
                { label: '서버', value: serverCount, icon: Server },
                { label: '명령어', value: commandCount, icon: Terminal },
              ].map((stat, idx) => (
                <div key={idx} className="flex flex-col items-center">
                  <stat.icon className="w-5 h-5 md:w-6 md:h-6 text-white/80 mb-1" />
                  <span className="font-display font-bold text-2xl md:text-4xl text-white drop-shadow-md tabular-nums">
                    {stat.value.toLocaleString()}
                  </span>
                  <span className="text-[10px] md:text-xs text-white/70 font-semibold tracking-wider uppercase mt-0.5">
                    {stat.label}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Floating game buttons */}
        <motion.img src={BTN_GAME05} alt="" className="absolute left-[7%] top-[58%] w-36 md:w-44 pointer-events-none z-20 drop-shadow-lg"
          style={{ opacity: isDark ? 0.4 : 0.6 }}
          animate={{ y: [0, -10, 0], rotate: [0, -3, 0] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.img src={BTN_GAME04} alt="" className="absolute left-[27%] bottom-[4%] w-28 md:w-36 pointer-events-none z-20 drop-shadow-lg"
          style={{ opacity: isDark ? 0.35 : 0.5 }}
          animate={{ y: [0, -8, 0], rotate: [19, 22, 19] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut', delay: 0.7 }}
        />
        <motion.img src={BTN_GAME03} alt="" className="absolute right-[9%] bottom-[9%] w-24 pointer-events-none z-20 drop-shadow-lg"
          style={{ opacity: isDark ? 0.35 : 0.5 }}
          animate={{ y: [0, -7, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 1.3 }}
        />
        <motion.img src={BTN_GAME01} alt="" className="absolute right-[4%] top-[53%] w-36 md:w-40 pointer-events-none z-20 drop-shadow-lg"
          style={{ opacity: isDark ? 0.4 : 0.55, scaleX: -1 }}
          animate={{ y: [0, -9, 0] }}
          transition={{ duration: 5.5, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
        />

        {/* Section blends */}
        <div className="absolute top-0 inset-x-0 h-20 z-[5]" style={{ background: `linear-gradient(to bottom, ${midBlend}, transparent)` }} />
        <div className="absolute bottom-0 inset-x-0 h-24 z-[5]" style={{ background: `linear-gradient(to top, ${isDark ? 'rgba(15,18,25,0.8)' : 'rgba(255,255,255,0.6)'}, transparent)` }} />
      </section>

      {/* ═══════════════════════════════════════════
          SHOWCASE + CTA
          ═══════════════════════════════════════════ */}
      <section className="relative py-24 overflow-hidden">
        <img
          src={BG_SEC}
          alt=""
          className="absolute inset-0 w-full h-full object-cover z-0"
          style={{ opacity: isDark ? 0.6 : 0.9 }}
        />
        <div
          className="absolute inset-0 z-[1]"
          style={{
            background: isDark
              ? 'linear-gradient(to bottom, rgba(15,18,25,0.7), transparent, rgba(15,18,25,0.8))'
              : 'linear-gradient(to bottom, rgba(255,255,255,1), transparent, rgba(0,0,0,0.4))',
          }}
        />

        <div className="relative z-10 max-w-[1440px] mx-auto px-6 lg:px-12">
          <motion.div
            className="flex justify-center mb-16"
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
          >
            <img
              src={GAME_FRONT}
              alt="Game Preview"
              className="max-w-full md:max-w-[680px] w-full rounded-2xl drop-shadow-[0_25px_60px_rgba(0,0,0,0.35)]"
            />
          </motion.div>

          {/* Donation CTA */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.8, delay: 0.15 }}
          >
            <div
              className="max-w-3xl mx-auto backdrop-blur-md rounded-3xl p-8 md:p-12 border relative overflow-hidden group"
              style={{
                backgroundColor: isDark ? 'rgba(30,35,50,0.9)' : 'rgba(255,255,255,0.92)',
                borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.6)',
                boxShadow: isDark
                  ? '0 20px 60px rgba(0,0,0,0.4)'
                  : '0 20px 60px rgba(0,0,0,0.15)',
              }}
            >
              <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 gradient-border-animated pointer-events-none" />

              <div className="flex flex-col md:flex-row items-center justify-between gap-8 relative z-10">
                <div className="flex-1 text-center md:text-left">
                  <h3 className="font-title text-2xl md:text-3xl mb-3" style={{ color: isDark ? '#e2e8f0' : '#1f2937' }}>
                    봇이 마음에 드셨나요?
                  </h3>
                  <p className="text-base leading-relaxed" style={{ color: isDark ? '#94a3b8' : '#6b7280' }}>
                    서버 유지비와 새로운 기능 추가를 위해<br className="hidden md:block" />
                    커피 한 잔의 정성이라도 큰 힘이 됩니다.
                  </p>
                </div>
                <button
                  onClick={() => setIsDonationModalOpen(true)}
                  className="group/btn relative shrink-0 inline-block hover:scale-105 active:scale-95 transition-transform duration-200"
                >
                  <img src={BTN_GAME03} alt="" className="h-[65px] drop-shadow-lg opacity-90 group-hover/btn:opacity-100 group-hover/btn:drop-shadow-[0_8px_24px_rgba(229,143,182,0.4)] transition-all" />
                  <span className="absolute inset-0 flex items-center justify-center font-title text-lg text-white">
                    후원하기
                  </span>
                </button>
              </div>

              <img src={CHAR_06} alt="" className="absolute -bottom-4 -right-4 w-28 opacity-15 pointer-events-none animate-float-gentle" />
            </div>
          </motion.div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          FOOTER
          ═══════════════════════════════════════════ */}
      <footer
        className="py-12 border-t"
        style={{
          backgroundColor: isDark ? '#0a0d14' : '#1a1a2e',
          borderColor: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.05)',
        }}
      >
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <img src={LOGO} alt="Logo" className="h-8 opacity-60" />
              <span className="font-title text-lg text-white/70">Debi & Marlene</span>
            </div>
            <div className="flex gap-8 text-sm font-medium">
              <Link to="/commands" className="text-gray-500 hover:text-white transition-colors duration-200">명령어</Link>
              <Link to="/bot-guide" className="text-gray-500 hover:text-white transition-colors duration-200">인텐트 가이드</Link>
              <Link to="/premium" className="text-gray-500 hover:text-white transition-colors duration-200">후원</Link>
              <a href="https://discord.gg/aDemda3qC9" className="text-gray-500 hover:text-white transition-colors duration-200">지원 서버</a>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-white/5 text-center">
            <p className="text-xs text-gray-600">Debi & Marlene Bot. Not affiliated with Nimble Neuron.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
