import { useRef } from 'react'
import { motion, useInView, useScroll, useTransform } from 'framer-motion'
import Header from '../components/common/Header'
import FlowingMenu from '../components/common/FlowingMenu'

/* ── Assets ── */
import BG_SKY from '../assets/images/event/imgi_28_bg01.png'
import BG_CLOUD from '../assets/images/event/imgi_31_bg02.png'
import CHAR_HERO from '../assets/images/event/imgi_30_ch01.png'
import CHAR_SITTING from '../assets/images/event/imgi_62_ch04.png'
import CHAR_02 from '../assets/images/event/imgi_47_ch02.png'
import CHAR_03 from '../assets/images/event/imgi_48_ch03.png'
import CHAR_05 from '../assets/images/event/imgi_49_ch05.png'
import CHAR_06 from '../assets/images/event/imgi_50_ch06.png'
import CHAR_07 from '../assets/images/event/imgi_51_ch07.png'
import NEW_BADGE from '../assets/images/event/imgi_77_new.png'
import CURSOR from '../assets/images/event/imgi_45_cursor01.png'

/* ── Fade-in wrapper ── */
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

/* ── Floating character icon with drift ── */
function FloatingIcon({ src, alt, className, delay = 0, drift = -120 }: { src: string; alt: string; className: string; delay?: number; drift?: number }) {
  const dur = 8 + Math.random() * 6
  const yDrift = -20 + Math.random() * 40
  return (
    <motion.img
      src={src}
      alt={alt}
      draggable={false}
      className={`absolute pointer-events-none select-none ${className}`}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{
        opacity: [0, 1, 1, 0.7],
        scale: 1,
        x: [0, drift * 0.3, drift * 0.7, drift],
        y: [0, yDrift * 0.5, yDrift, yDrift * 0.8],
        rotate: [0, Math.random() * 20 - 10, Math.random() * 30 - 15],
      }}
      transition={{
        opacity: { duration: dur, delay, repeat: Infinity, repeatType: 'loop' },
        scale: { duration: 0.8, delay, ease: 'backOut' },
        x: { duration: dur, delay, repeat: Infinity, repeatType: 'loop', ease: 'linear' },
        y: { duration: dur * 0.7, delay, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' },
        rotate: { duration: dur * 0.5, delay, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' },
      }}
    />
  )
}

/* ── Electric underline effect ── */
function ElectricText({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`relative inline-block group ${className}`}>
      {children}
      <span className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-[#3cabc9] via-[#ff9af2] to-[#3cabc9] bg-[length:200%_100%] animate-[electric_1.5s_ease-in-out_infinite]" />
      <span className="absolute bottom-[-1px] left-0 w-full h-[4px] bg-gradient-to-r from-transparent via-[#3cabc9] to-transparent opacity-40 blur-[2px] animate-[electric_1.5s_ease-in-out_infinite_0.1s]" />
    </span>
  )
}

/* ── Feature card ── */
function FeatureCard({ title, description, color, delay }: { title: string; description: string; color: 'cyan' | 'pink'; delay: number }) {
  const borderColor = color === 'cyan' ? 'border-[#3cabc9]/30 hover:border-[#3cabc9]' : 'border-[#e58fb6]/30 hover:border-[#e58fb6]'
  const titleColor = color === 'cyan' ? 'text-[#3cabc9]' : 'text-[#e58fb6]'
  return (
    <FadeIn delay={delay} className="flex-1 min-w-[260px]">
      <div className={`p-8 rounded-2xl bg-white/80 backdrop-blur-sm border-2 ${borderColor} transition-all duration-300 hover:shadow-lg hover:-translate-y-1 h-full`}>
        <h3 className={`font-title text-2xl mb-3 ${titleColor}`}>{title}</h3>
        <p className="font-body text-gray-500 text-sm leading-relaxed">{description}</p>
      </div>
    </FadeIn>
  )
}

/* ══════════════════════════════════════════════
   Landing Page
   ══════════════════════════════════════════════ */
export default function Landing() {
  const heroRef = useRef(null)
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const skyY = useTransform(scrollYProgress, [0, 1], ['0%', '20%'])
  const cloudY = useTransform(scrollYProgress, [0, 1], ['0%', '30%'])
  const charY = useTransform(scrollYProgress, [0, 1], ['0%', '10%'])

  const menuItems = [
    { text: 'TTS' },
    { text: 'Stats' },
    { text: 'Music' },
    { text: 'Quiz' },
  ]

  return (
    <div className="min-h-screen bg-white font-body overflow-x-hidden selection:bg-[#3cabc9]/20">
      <Header />

      {/* ══ HERO ══ */}
      <section ref={heroRef} className="relative h-screen min-h-[700px] overflow-hidden">
        {/* White top area */}
        <div className="absolute z-0 top-0 left-0 w-full h-[35%] bg-white" />

        {/* z-1: Sky background — Figma: 1440x831, starts at y=427/1258 = 34% */}
        <motion.div className="absolute z-[1] top-[34%] left-0 w-full h-[66%]" style={{ y: skyY }}>
          <img src={BG_SKY} alt="" className="w-full h-full object-cover object-top" draggable={false} />
        </motion.div>

        {/* z-2: Cloud/leaf overlay — Figma: 1763x886, 122% wide, starts at y=392/1258 = 31% */}
        <motion.div className="absolute z-[2] top-[31%] left-[-11%] w-[122%] h-[70%]" style={{ y: cloudY }}>
          <img src={BG_CLOUD} alt="" className="w-full h-full object-cover" draggable={false} />
        </motion.div>

        {/* z-3: Main character — Figma: x=455/1440=31.6% from left, 922x866 */}
        <motion.div
          className="absolute z-[3] bottom-0 right-0 md:right-[3%] w-[80%] md:w-[64%] max-w-[922px] h-[69%]"
          style={{ y: charY }}
        >
          <img src={CHAR_HERO} alt="Debi & Marlene" className="w-full h-full object-contain object-bottom" draggable={false} />
        </motion.div>

        {/* z-4: Floating character icons - drifting left */}
        <div className="absolute inset-0 z-[4] hidden md:block overflow-hidden">
          <FloatingIcon src={CHAR_03} alt="" className="w-16 h-16 object-contain top-[30%] left-[15%]" delay={0} drift={-150} />
          <FloatingIcon src={CURSOR} alt="" className="w-12 h-12 object-contain top-[22%] left-[28%]" delay={1.5} drift={-200} />
          <FloatingIcon src={CHAR_05} alt="" className="w-14 h-14 object-contain top-[20%] left-[70%]" delay={0.8} drift={-180} />
          <FloatingIcon src={CHAR_02} alt="" className="w-11 h-11 object-contain top-[55%] left-[20%]" delay={2} drift={-100} />
          <FloatingIcon src={CHAR_06} alt="" className="w-12 h-12 object-contain top-[48%] left-[12%]" delay={3} drift={-130} />
          <FloatingIcon src={CHAR_07} alt="" className="w-24 h-24 object-contain top-[65%] left-[75%]" delay={0.5} drift={-160} />
        </div>

        {/* z-10: Hero text content — above all layers */}
        <div className="relative z-[10] max-w-7xl mx-auto px-6 lg:px-12 h-full flex flex-col justify-center pt-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <img src={NEW_BADGE} alt="NEW" className="w-24 h-auto mb-2" draggable={false} />
          </motion.div>

          <motion.p
            className="font-title text-[28px] md:text-[43.08px] leading-normal bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent whitespace-nowrap"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            {`데비&마를렌 봇`}
          </motion.p>

          <motion.h1
            className="font-display text-[72px] md:text-[120px] lg:text-[167px] leading-none font-bold mt-1 whitespace-nowrap"
            style={{
              WebkitTextStroke: '0px transparent',
              color: 'rgba(97, 239, 255, 0.67)',
              textShadow: '0px 5.613px 0px #ff9af2, 0px 4px 4px rgba(0,0,0,0.25)',
              paintOrder: 'stroke fill',
            }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            대시보드
          </motion.h1>

          <motion.div
            className="flex gap-4 mt-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <a
              href="https://discord.com/oauth2/authorize?client_id=1393529860793831489&permissions=8&scope=bot%20applications.commands"
              target="_blank"
              rel="noopener noreferrer"
              className="group relative px-10 py-3.5 w-[199px] h-[56px] flex items-center justify-center rounded-[15px] font-title text-[24px] text-black shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)] backdrop-blur-xl bg-white/30 hover:bg-white/50 hover:-translate-y-0.5 transition-all duration-300 overflow-hidden"
            >
              <div className="absolute inset-0 opacity-[0.08] grain-overlay pointer-events-none" />
              봇 초대하기
            </a>
            <a
              href="/dashboard"
              className="group relative px-8 py-3.5 w-[133px] h-[56px] flex items-center justify-center rounded-[15px] font-title text-[24px] text-black shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)] backdrop-blur-xl bg-white/30 hover:bg-white/50 hover:-translate-y-0.5 transition-all duration-300 overflow-hidden"
            >
              <div className="absolute inset-0 opacity-[0.08] grain-overlay pointer-events-none" />
              대시보드
            </a>
          </motion.div>
        </div>

        {/* Bottom gradient fade */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-white to-transparent" />
      </section>

      {/* ══ FLOWING MENU STRIP ══ */}
      <FlowingMenu
        items={menuItems}
        speed={10}
        textColor="#374151"
        bgColor="#fafafa"
        hoverBgColor="#3cabc9"
        hoverTextColor="#ffffff"
        borderColor="#e5e7eb"
      />

      {/* ══ FEATURES ══ */}
      <section className="py-24 px-6 lg:px-12 bg-white">
        <div className="max-w-6xl mx-auto">
          <FadeIn className="text-center mb-16">
            <p className="font-title text-5xl md:text-[74px] bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight">
              <ElectricText>주요 기능</ElectricText>
            </p>
            <p className="font-title text-xl md:text-3xl text-gray-700 mt-4">
              하나의 봇으로 모든 기능을
            </p>
          </FadeIn>

          <div className="flex flex-wrap gap-6 justify-center">
            <FeatureCard
              title="고품질 TTS"
              description="데비와 마를렌의 목소리로 채팅을 읽어줍니다. AI 파인튜닝 모델 기반의 자연스러운 캐릭터 음성."
              color="cyan"
              delay={0.1}
            />
            <FeatureCard
              title="전적 검색"
              description="이터널리턴 전적과 캐릭터 통계를 한눈에. MMR 그래프, 팀원 분석까지 Discord 안에서 바로 확인."
              color="cyan"
              delay={0.2}
            />
            <FeatureCard
              title="음악 재생"
              description="유튜브 검색 기반 음악과 대기열 관리. 노래 퀴즈까지 음성 채널에서 함께 즐기세요."
              color="pink"
              delay={0.3}
            />
          </div>
        </div>
      </section>

      {/* ══ CHARACTER ILLUSTRATION ══ */}
      <section className="relative py-12 overflow-hidden bg-gradient-to-b from-white via-[#f0f9ff] to-white">
        <FadeIn className="max-w-4xl mx-auto px-6">
          <img
            src={CHAR_SITTING}
            alt="Debi & Marlene"
            className="w-full max-w-[700px] mx-auto h-auto object-contain"
            draggable={false}
          />
        </FadeIn>
      </section>

      {/* ══ FLOWING MENU STRIP 2 ══ */}
      <FlowingMenu
        items={[
          { text: 'Welcome' },
          { text: 'Dashboard' },
          { text: 'Settings' },
          { text: 'Premium' },
        ]}
        speed={14}
        textColor="#374151"
        bgColor="#fafafa"
        hoverBgColor="#e58fb6"
        hoverTextColor="#ffffff"
        borderColor="#e5e7eb"
      />

      {/* ══ STATS ══ */}
      <section className="py-20 bg-gradient-to-r from-[#f472b6] to-[#ec4899]">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-3 gap-8 text-center text-white">
            <FadeIn delay={0.1}>
              <div className="font-display text-5xl md:text-7xl font-bold">11,799</div>
              <div className="font-body text-sm md:text-base mt-2 opacity-80">누적 유저</div>
            </FadeIn>
            <FadeIn delay={0.2}>
              <div className="font-display text-5xl md:text-7xl font-bold">100</div>
              <div className="font-body text-sm md:text-base mt-2 opacity-80">서버</div>
            </FadeIn>
            <FadeIn delay={0.3}>
              <div className="font-display text-5xl md:text-7xl font-bold">17</div>
              <div className="font-body text-sm md:text-base mt-2 opacity-80">명령어</div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ══ CTA ══ */}
      <section className="py-24 bg-white">
        <FadeIn className="max-w-3xl mx-auto px-6 text-center">
          <p className="font-title text-3xl md:text-4xl text-gray-800 mb-4">
            봇이 마음에 드셨나요?
          </p>
          <p className="text-gray-500 mb-10 leading-relaxed">
            지금 바로 서버에 초대해서 데비와 마를렌을 만나보세요.
          </p>
          <div className="flex justify-center gap-4">
            <a
              href="https://discord.com/oauth2/authorize?client_id=1393529860793831489&permissions=8&scope=bot%20applications.commands"
              target="_blank"
              rel="noopener noreferrer"
              className="px-10 py-4 rounded-2xl font-title text-lg text-white bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
            >
              봇 초대하기
            </a>
            <a
              href="/dashboard"
              className="px-10 py-4 rounded-2xl font-title text-lg text-gray-600 bg-gray-50 border border-gray-200 hover:bg-white hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300"
            >
              대시보드
            </a>
          </div>
        </FadeIn>
      </section>

      {/* ══ FOOTER ══ */}
      <footer className="py-8 border-t border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="font-title text-lg text-gray-400">
            Debi & Marlene<span className="text-[#3cabc9]">.</span>
          </p>
          <p className="text-xs text-gray-400">
            Eternal Return and all related content are trademarks of Nimble Neuron.
          </p>
        </div>
      </footer>
    </div>
  )
}
