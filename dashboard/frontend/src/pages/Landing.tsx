import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useEffect, useState } from 'react'
import Header from '../components/common/Header'
import { api } from '../services/api'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Users, Server, Terminal } from 'lucide-react'
import AnimatedSection from '../components/common/AnimatedSection'
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

export default function Landing() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState<BotStats>({ users: 0, servers: 0, commands: 17 })
  const [botClientId, setBotClientId] = useState<string | null>(null)
  const [isDonationModalOpen, setIsDonationModalOpen] = useState(false)

  const { scrollY } = useScroll()
  const heroBgY = useTransform(scrollY, [0, 800], [0, 200])
  const heroCharY = useTransform(scrollY, [0, 600], [0, -50])

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

  return (
    <div className="min-h-screen overflow-x-hidden font-body bg-white selection:bg-debi-primary/30">
      <Header />
      <DonationModal isOpen={isDonationModalOpen} onClose={() => setIsDonationModalOpen(false)} />

      {/* ═══════════════════════════════════════════
          HERO — Figma: 0~1258px (bike + sky bg)
          ═══════════════════════════════════════════ */}
      <section className="relative min-h-screen overflow-hidden">
        {/* BG: Bike scene (full bleed, behind everything) */}
        <motion.div style={{ y: heroBgY }} className="absolute inset-0 -top-20 z-0">
          <img src={BG_BIKE} alt="" className="w-[120%] h-[130%] object-cover opacity-60" />
        </motion.div>

        {/* BG: Sky overlay */}
        <div className="absolute inset-0 z-[1]">
          <img src={BG_SKY} alt="" className="w-full h-full object-cover" />
          <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-black/20 to-transparent" />
          <div className="absolute bottom-0 inset-x-0 h-48 bg-gradient-to-t from-white to-transparent" />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-[1440px] mx-auto px-8 pt-28 pb-16 min-h-screen flex items-center">
          <div className="grid xl:grid-cols-[1fr_1fr] gap-6 items-center w-full">
            {/* Left: Text Content */}
            <motion.div
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="relative z-10"
            >
              {/* NEW badge */}
              <img src={NEW_BADGE} alt="NEW" className="h-10 mb-4 drop-shadow-md" />

              {/* Gradient Title — MemomentKkukkukk */}
              <p className="font-title gradient-text-title text-[clamp(28px,3.5vw,43px)] mb-1 drop-shadow-sm">
                데비&마를렌 봇
              </p>

              {/* Display Title — YPairingFont */}
              <h1 className="font-display font-bold text-[clamp(60px,8vw,119px)] text-[#8ea9c9] leading-[1] mb-6 [text-shadow:6px_4px_4px_#e58fb6]">
                대시보드
              </h1>

              {/* After School text image */}
              <img
                src={TXT_AFTERSCHOOL}
                alt="Debi & Marlene After School"
                className="h-[clamp(80px,12vw,160px)] mb-8 drop-shadow-lg"
              />

              {/* Subtitle — Paperlogy */}
              <p className="text-lg md:text-xl text-gray-600 mb-10 leading-relaxed max-w-md font-medium">
                이터널리턴 전적부터 고품질 TTS,<br />
                완벽한 음악 재생 기능까지.
              </p>

              {/* CTA Buttons — MemomentKkukkukk */}
              <div className="flex flex-wrap items-center gap-4">
                <a
                  href={getInviteUrl()}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group relative inline-block hover:scale-105 hover:-rotate-1 active:scale-95 transition-transform"
                >
                  <img src={BTN_START} alt="" className="h-[70px] w-auto drop-shadow-xl opacity-90 group-hover:opacity-100" />
                  <span className="absolute inset-0 flex items-center justify-center font-title text-xl text-white drop-shadow-[0_2px_3px_rgba(0,0,0,0.6)] pl-2">
                    봇 초대하기
                  </span>
                </a>
                <button
                  onClick={handleDashboard}
                  className="group relative inline-block hover:scale-105 hover:rotate-1 active:scale-95 transition-transform"
                >
                  <img src={BTN_GAME01} alt="" className="h-[65px] w-auto drop-shadow-lg opacity-90 group-hover:opacity-100" />
                  <span className="absolute inset-0 flex items-center justify-center font-title text-lg text-white drop-shadow-[0_2px_3px_rgba(0,0,0,0.6)]">
                    대시보드
                  </span>
                </button>
              </div>
            </motion.div>

            {/* Right: Hero Character — animate */}
            <motion.div
              style={{ y: heroCharY }}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.3, type: 'spring', stiffness: 60 }}
              className="hidden xl:block relative h-[700px]"
            >
              {/* Figma: ch01 at (427,366) 950x892 — ~66% width, right side */}
              <img
                src={CHAR_HERO}
                alt="Debi & Marlene"
                className="absolute bottom-0 right-0 h-[110%] w-auto object-contain drop-shadow-[0_20px_50px_rgba(0,0,0,0.2)] animate-float-slow"
              />
              {/* ch07 top-right decoration — Figma: (1127,1293) but relative to hero */}
              <img src={CHAR_07} alt="" className="absolute -top-4 right-10 w-28 drop-shadow-lg animate-float-medium opacity-80" />
            </motion.div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          FEATURES + MID VISUAL — Figma: 1258~4084px
          구름 배경(bg03)이 카드~앉은 캐릭터까지 하나로 이어짐
          ═══════════════════════════════════════════ */}
      <section className="relative overflow-hidden">
        {/* BG: Cloud sky — Figma: imgi_29_bg03, 1439x2772 전체 커버 */}
        <div className="absolute inset-0 z-0">
          <img src={BG_CLOUD} alt="" className="w-full h-full object-cover object-center" />
          {/* 카드 영역만 살짝 밝게, 아래는 하늘 원본 그대로 */}
          <div className="absolute top-0 inset-x-0 h-[35%] bg-gradient-to-b from-white/40 to-transparent" />
        </div>

        {/* ── Feature Cards ── */}
        <div className="relative z-10 max-w-[1440px] mx-auto px-8 pt-24 pb-12">
          <AnimatedSection className="text-center mb-16">
            <p className="font-title gradient-text-title text-2xl mb-3">주요 기능</p>
            <h2 className="font-title text-3xl md:text-4xl text-gray-700">
              하나의 봇으로 모든 기능을
            </h2>
          </AnimatedSection>

          <div className="flex flex-col md:flex-row justify-center items-center gap-6 md:gap-8 mb-16">
            <AnimatedSection delay={0} className="relative w-[260px] h-[355px] shrink-0">
              <img src={CARD_CYAN} alt="" className="absolute inset-0 w-full h-full object-contain drop-shadow-lg" />
              <div className="relative z-10 flex flex-col items-center justify-center h-full px-6 pt-12 pb-8 text-center">
                <p className="font-title text-xl text-[#3cabc9] mb-3">고품질 TTS</p>
                <p className="text-sm text-gray-600 leading-relaxed">
                  데비와 마를렌의 목소리로<br />채팅을 읽어줍니다
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={0.1} className="relative w-[260px] h-[355px] shrink-0">
              <img src={CARD_CYAN} alt="" className="absolute inset-0 w-full h-full object-contain drop-shadow-lg" />
              <div className="relative z-10 flex flex-col items-center justify-center h-full px-6 pt-12 pb-8 text-center">
                <p className="font-title text-xl text-[#3cabc9] mb-3">전적 검색</p>
                <p className="text-sm text-gray-600 leading-relaxed">
                  이터널리턴 전적과<br />캐릭터 통계를 한눈에
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={0.2} className="relative w-[260px] h-[355px] shrink-0">
              <img src={CARD_PINK} alt="" className="absolute inset-0 w-full h-full object-contain drop-shadow-lg" />
              <div className="relative z-10 flex flex-col items-center justify-center h-full px-6 pt-12 pb-8 text-center">
                <p className="font-title text-xl text-[#e58fb6] mb-3">음악 재생</p>
                <p className="text-sm text-gray-600 leading-relaxed">
                  유튜브 검색 기반<br />음악과 대기열 관리
                </p>
              </div>
            </AnimatedSection>
          </div>

          <AnimatedSection delay={0.3} className="text-center">
            <Link
              to="/commands"
              className="group relative inline-block hover:scale-105 active:scale-95 transition-transform"
            >
              <img src={BTN_GAME02} alt="" className="h-[55px] drop-shadow-lg opacity-90 group-hover:opacity-100" />
              <span className="absolute inset-0 flex items-center justify-center font-title text-base text-white drop-shadow-[0_2px_3px_rgba(0,0,0,0.6)]">
                명령어 확인
              </span>
            </Link>
          </AnimatedSection>
        </div>

        {/* Decorative chars around cards */}
        <img src={CHAR_03} alt="" className="absolute left-[12%] top-[35%] w-28 opacity-60 animate-float-gentle pointer-events-none z-10" />
        <img
          src={CHAR_05}
          alt=""
          className="absolute right-[8%] top-[30%] w-24 opacity-50 animate-float-medium pointer-events-none z-10"
          style={{ transform: 'rotate(39deg)' }}
        />
        <img src={CHAR_07} alt="" className="absolute right-[15%] top-[8%] w-24 opacity-50 animate-float-slow pointer-events-none z-10" />

        {/* ── Sitting Characters — 레퍼런스: 넓은 파란 하늘 + 하단에 캐릭터 ── */}
        <div className="relative z-10 pt-20 min-h-[60vh] flex flex-col justify-end items-center">
          {/* 넓은 하늘 공간 확보 후 캐릭터는 하단에 */}
          <motion.img
            src={CHAR_SITTING}
            alt="Debi & Marlene"
            className="w-[55%] max-w-[814px] h-auto drop-shadow-[0_8px_30px_rgba(0,0,0,0.3)]"
            initial={{ opacity: 0, y: 60, scale: 0.95 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
          />
        </div>

        {/* Decorations around sitting chars */}
        <img src={CURSOR} alt="" className="absolute left-[25%] bottom-[18%] w-20 opacity-50 animate-float-medium pointer-events-none z-10" />
        <img src={CHAR_02} alt="" className="absolute right-[12%] bottom-[10%] w-20 opacity-50 animate-float-gentle pointer-events-none z-10" />
        <img
          src={CHAR_06}
          alt=""
          className="absolute left-[5%] bottom-[15%] w-28 opacity-40 animate-float-slow pointer-events-none z-10"
          style={{ transform: 'rotate(33deg)' }}
        />
      </section>

      {/* ═══════════════════════════════════════════
          BOARD — Figma: 4084~5424px (notebook + grid + game buttons)
          ═══════════════════════════════════════════ */}
      <section className="relative py-20 overflow-hidden">
        {/* BG: Notebook texture — Figma: imgi_86_bg_box02, full width */}
        <img src={BG_NOTEBOOK} alt="" className="absolute inset-0 w-full h-full object-cover z-0" />

        <div className="relative z-10 max-w-[1440px] mx-auto px-8">
          {/* Section heading */}
          <AnimatedSection className="text-center mb-12">
            <p className="font-title gradient-text-title text-2xl mb-3">인사말 카드</p>
            <h2 className="font-title text-3xl md:text-4xl text-gray-700">
              새 멤버를 환영하세요
            </h2>
          </AnimatedSection>

          {/* Grid + Greeting Preview — Figma: teal grid bg */}
          <AnimatedSection delay={0.2} className="relative max-w-[1100px] mx-auto">
            {/* Teal grid background */}
            <img src={BG_GRID} alt="" className="w-full rounded-xl drop-shadow-lg" />

            {/* Greeting Preview overlaid on grid */}
            <div className="absolute inset-0 flex items-center justify-center p-4 md:p-10">
              <div className="w-full max-w-3xl bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/60 p-4">
                <GreetingPreview />
              </div>
            </div>
          </AnimatedSection>

          {/* Pink bar with stats — Figma: imgi_89_bg_box04 */}
          <AnimatedSection delay={0.3} className="relative max-w-[1100px] mx-auto mt-8">
            <img src={BG_PINKBAR} alt="" className="w-full rounded-xl drop-shadow-md" />
            <div className="absolute inset-0 flex items-center justify-center gap-8 md:gap-20">
              {[
                { label: '누적 유저', value: stats.users, icon: Users },
                { label: '서버', value: stats.servers, icon: Server },
                { label: '명령어', value: stats.commands, icon: Terminal },
              ].map((stat, idx) => (
                <div key={idx} className="flex flex-col items-center">
                  <stat.icon className="w-5 h-5 md:w-6 md:h-6 text-white/80 mb-1" />
                  <motion.span
                    className="font-display font-bold text-2xl md:text-4xl text-white drop-shadow-md"
                    initial={{ opacity: 0, scale: 0.5 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ type: 'spring', stiffness: 100, delay: idx * 0.1 }}
                  >
                    {stat.value.toLocaleString()}
                  </motion.span>
                  <span className="text-[10px] md:text-xs text-white/70 font-semibold tracking-wider uppercase mt-0.5">
                    {stat.label}
                  </span>
                </div>
              ))}
            </div>
          </AnimatedSection>
        </div>

        {/* Scattered game buttons — Figma: various positions + rotations */}
        <img src={BTN_GAME05} alt="" className="absolute left-[8%] top-[60%] w-36 md:w-44 opacity-70 animate-float-gentle pointer-events-none z-20 drop-shadow-lg" />
        <img
          src={BTN_GAME04}
          alt=""
          className="absolute left-[28%] bottom-[5%] w-28 md:w-36 opacity-60 animate-float-medium pointer-events-none z-20 drop-shadow-lg"
          style={{ transform: 'rotate(19deg)' }}
        />
        <img src={BTN_GAME03} alt="" className="absolute right-[10%] bottom-[10%] w-24 opacity-60 animate-float-slow pointer-events-none z-20 drop-shadow-lg" />
        <img
          src={BTN_GAME01}
          alt=""
          className="absolute right-[5%] top-[55%] w-36 md:w-40 opacity-65 pointer-events-none z-20 drop-shadow-lg animate-float-gentle"
          style={{ transform: 'scaleX(-1)' }}
        />
      </section>

      {/* ═══════════════════════════════════════════
          SHOWCASE + CTA — Figma: 5424~6186px (game front + sec bg)
          ═══════════════════════════════════════════ */}
      <section className="relative py-24 overflow-hidden">
        {/* BG: Section background */}
        <img src={BG_SEC} alt="" className="absolute inset-0 w-full h-full object-cover z-0 opacity-90" />
        <div className="absolute inset-0 bg-gradient-to-b from-white via-transparent to-black/40 z-[1]" />

        <div className="relative z-10 max-w-[1440px] mx-auto px-8">
          {/* Game front showcase */}
          <AnimatedSection className="flex justify-center mb-16">
            <img
              src={GAME_FRONT}
              alt="Game Preview"
              className="max-w-full md:max-w-[700px] w-full rounded-2xl drop-shadow-2xl"
            />
          </AnimatedSection>

          {/* Donation CTA */}
          <AnimatedSection delay={0.2}>
            <div className="max-w-3xl mx-auto bg-white/90 backdrop-blur-md rounded-3xl p-8 md:p-12 shadow-2xl border border-white/60 relative overflow-hidden">
              <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex-1 text-center md:text-left">
                  <h3 className="font-title text-2xl md:text-3xl text-gray-800 mb-3">
                    봇이 마음에 드셨나요?
                  </h3>
                  <p className="text-gray-500 text-base leading-relaxed">
                    서버 유지비와 새로운 기능 추가를 위해<br className="hidden md:block" />
                    커피 한 잔의 정성이라도 큰 힘이 됩니다.
                  </p>
                </div>
                <button
                  onClick={() => setIsDonationModalOpen(true)}
                  className="group relative shrink-0 inline-block hover:scale-105 active:scale-95 transition-transform"
                >
                  <img src={BTN_GAME03} alt="" className="h-[65px] drop-shadow-lg opacity-90 group-hover:opacity-100" />
                  <span className="absolute inset-0 flex items-center justify-center font-title text-lg text-white drop-shadow-[0_2px_3px_rgba(0,0,0,0.6)]">
                    후원하기
                  </span>
                </button>
              </div>

              {/* Decorative character */}
              <img src={CHAR_06} alt="" className="absolute -bottom-4 -right-4 w-28 opacity-20 animate-float-gentle pointer-events-none" />
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          FOOTER
          ═══════════════════════════════════════════ */}
      <footer className="py-10 bg-[#1a1a2e] border-t border-white/10">
        <div className="max-w-[1440px] mx-auto px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <img src={LOGO} alt="Logo" className="h-8 opacity-70" />
              <span className="font-title text-lg text-white/80">Debi & Marlene</span>
            </div>
            <div className="flex gap-8 text-sm font-medium">
              <Link to="/commands" className="text-gray-400 hover:text-white transition-colors">명령어</Link>
              <Link to="/bot-guide" className="text-gray-400 hover:text-white transition-colors">인텐트 가이드</Link>
              <a href="https://discord.gg/aDemda3qC9" className="text-gray-400 hover:text-white transition-colors">지원 서버</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
