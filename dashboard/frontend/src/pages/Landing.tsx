import { useRef, useEffect, useState } from 'react'
import { motion, useInView, useScroll, useTransform, useMotionValue, useSpring } from 'framer-motion'
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

/* ── Global Fast-moving Particles ── */
const ICONS = [CHAR_02, CHAR_03, CHAR_05, CHAR_06, CHAR_07, CURSOR, NEW_BADGE];

function GlobalParticles() {
  const [particles, setParticles] = useState<any[]>([]);

  useEffect(() => {
    const w = window.innerWidth || 1200;
    const h = window.innerHeight || 800;
    
    // 45여 개의 파티클을 매우 부드럽고 꾸준하게 가로로 흐르도록 수정
    const items = Array.from({ length: 45 }).map((_, i) => {
      const sizeBase = Math.random() > 0.8 ? 70 : 35; 
      return {
        id: i,
        src: ICONS[i % ICONS.length],
        size: sizeBase + Math.random() * 35,
        startY: Math.random() * h, 
        startX: w + 100 + Math.random() * 400, // 확실하게 화면 우측 밖
        endX: -200 - Math.random() * 200,      // 확실하게 화면 좌측 밖
        animDuration: 10 + Math.random() * 20, // 자연스럽고 약간 빠르게
        delay: -Math.random() * 40,
        rotationSpeed: (Math.random() > 0.5 ? 1 : -1) * (90 + Math.random() * 270) 
      };
    });
    setParticles(items);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-[1] overflow-hidden">
      {particles.map((item: any) => (
        <motion.img
          key={item.id}
          src={item.src}
          className="absolute"
          style={{ width: item.size, height: 'auto', opacity: 0.55 }}
          initial={{ x: item.startX, y: item.startY, rotate: 0 }}
          animate={{
            x: [item.startX, item.endX],
            rotate: [0, item.rotationSpeed],
          }}
          transition={{
            x: { duration: item.animDuration, repeat: Infinity, ease: 'linear', delay: item.delay },
            rotate: { duration: item.animDuration * 1.5, repeat: Infinity, ease: 'linear', delay: item.delay }
          }}
        />
      ))}
    </div>
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
  
  // 스크롤 패럴랙스 (수직 이동)
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const skyY = useTransform(scrollYProgress, [0, 1], ['0%', '15%'])
  const cloudY = useTransform(scrollYProgress, [0, 1], ['0%', '30%'])
  const charY = useTransform(scrollYProgress, [0, 1], ['0%', '10%'])
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '25%'])

  // 마우스 패럴랙스 (x, y 이동)
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { damping: 25, stiffness: 120 };
  const smoothMouseX = useSpring(mouseX, springConfig);
  const smoothMouseY = useSpring(mouseY, springConfig);

  const handleMouseMove = (e: React.MouseEvent<HTMLElement>) => {
    const { clientX, clientY } = e;
    const { innerWidth, innerHeight } = window;
    // -1 ~ 1 사이의 값으로 정규화
    const x = (clientX / innerWidth) * 2 - 1;
    const y = (clientY / innerHeight) * 2 - 1;
    mouseX.set(x);
    mouseY.set(y);
  };

  // 각 레이어별 미세한 마우스 이동값
  const layer1X = useTransform(smoothMouseX, [-1, 1], [-15, 15]);
  const layer1Y = useTransform(smoothMouseY, [-1, 1], [-15, 15]);
  
  const layer2X = useTransform(smoothMouseX, [-1, 1], [-30, 30]);
  const layer2Y = useTransform(smoothMouseY, [-1, 1], [-30, 30]);

  const charMoveX = useTransform(smoothMouseX, [-1, 1], [-10, 10]);
  const charMoveY = useTransform(smoothMouseY, [-1, 1], [-5, 5]);

  const menuItems = [
    { text: 'TTS' },
    { text: 'Stats' },
    { text: 'Music' },
    { text: 'Quiz' },
  ]

  return (
    <div className="min-h-screen bg-[#e0f7fa] font-body overflow-x-hidden selection:bg-[#3cabc9]/20 relative z-0">
      {/* 찐 유리 왜곡(Liquid Glass) 효과를 위한 SVG 필터 정의 */}
      <svg style={{ display: 'none' }}>
        <defs>
          <filter id="liquid-glass" x="0%" y="0%" width="100%" height="100%">
            {/* 울렁거리는 랜덤 노이즈(Turbulence) 삭제! 오목렌즈의 굴곡을 정확히 계산하는 X/Y 그라데이션 정밀 맵 주입 */}
            <feImage href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cdefs%3E%3ClinearGradient id='gx' x1='0%25' y1='0%25' x2='100%25' y2='0%25'%3E%3Cstop offset='0%25' stop-color='%23000000'/%3E%3Cstop offset='50%25' stop-color='%23800000'/%3E%3Cstop offset='100%25' stop-color='%23ff0000'/%3E%3C/linearGradient%3E%3ClinearGradient id='gy' x1='0%25' y1='0%25' x2='0%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%23000000'/%3E%3Cstop offset='50%25' stop-color='%23008000'/%3E%3Cstop offset='100%25' stop-color='%2300ff00'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='100' height='100' fill='url(%23gx)'/%3E%3Crect width='100' height='100' fill='url(%23gy)' style='mix-blend-mode:screen'/%3E%3C/svg%3E" result="lensMap" preserveAspectRatio="none" x="0" y="0" width="100%" height="100%" />
            {/* 중앙으로 픽셀을 블랙홀처럼 강하게 끌어당기는 힘! scale을 40에서 120으로 무려 3배 펌핑 */}
            <feDisplacementMap in="SourceGraphic" in2="lensMap" scale="120" xChannelSelector="R" yChannelSelector="G" result="displaced" />
            {/* 요청하신 대로 블러값을 2에서 1로 훨씬 더 줄였습니다 */}
            <feGaussianBlur in="displaced" stdDeviation="1" result="blur" />
            
            {/* 피그마의 원본 텍스처 질감(feTurbulence) 부활 후 은은하게 오버레이 코팅 */}
            <feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves="3" result="noiseTexture" />
            <feColorMatrix in="noiseTexture" type="saturate" values="0" result="grayNoise" />
            <feComponentTransfer in="grayNoise" result="fadedNoise">
              <feFuncA type="linear" slope="0.15" />
            </feComponentTransfer>
            <feBlend mode="overlay" in="fadedNoise" in2="blur" />
          </filter>
        </defs>
      </svg>
      <GlobalParticles />
      <Header />

      {/* ══ HERO ══ */}
      <section 
        ref={heroRef} 
        onMouseMove={handleMouseMove}
        className="relative h-screen min-h-[700px] overflow-hidden"
      >
        {/* z-[0]: Sky background (상단바 영역까지 화면 전체를 덮도록 top 0 근처로 확장) */}
        <motion.div 
          className="absolute z-[0] top-[-5%] left-[-5%] w-[110%] h-[110%]" 
          style={{ y: skyY, x: layer1X, translateY: layer1Y }}
        >
          <img src={BG_SKY} alt="" className="w-full h-full object-cover object-top opacity-90" draggable={false} />
        </motion.div>

        {/* z-2: Cloud/leaf overlay — Figma: 1763x886, 122% wide, starts at y=392/1258 = 31% */}
        <motion.div 
          className="absolute z-[2] top-[20%] left-[-15%] w-[130%] h-[90%]" 
          style={{ y: cloudY, x: layer2X, translateY: layer2Y }}
        >
          <img src={BG_CLOUD} alt="" className="w-full h-full object-cover mix-blend-multiply" draggable={false} />
        </motion.div>

        {/* z-[5]: Main character */}
        <motion.div
          className="absolute z-[5] bottom-0 right-0 md:right-[3%] w-[90%] md:w-[68%] max-w-[950px] h-[75%] filter drop-shadow-2xl"
          style={{ y: charY, x: charMoveX, translateY: charMoveY }}
        >
          <img src={CHAR_HERO} alt="Debi & Marlene" className="w-full h-full object-contain object-bottom" draggable={false} />
        </motion.div>

        {/* z-[3]: Hero text content — BEHIND the character */}
        <motion.div 
          className="relative z-[3] max-w-7xl mx-auto px-6 lg:px-12 h-full flex flex-col justify-center pt-20 pointer-events-none"
          style={{ y: textY }}
        >
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
              background: 'rgba(97, 239, 255, 0.67)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              WebkitTextStroke: '2.95px #ff9af2',
              textShadow: '0px 5.613px 1.4px #ff9af2, 0px 4px 4px rgba(0,0,0,0.25)',
              paintOrder: 'stroke fill',
            }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            대시보드
          </motion.h1>

          <motion.div
            className="flex gap-4 mt-10 pointer-events-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <a
              href="https://discord.com/oauth2/authorize?client_id=1393529860793831489&permissions=8&scope=bot%20applications.commands"
              target="_blank"
              rel="noopener noreferrer"
              className="group relative w-[199px] h-[56px] flex items-center justify-center hover:-translate-y-1 transition-transform duration-300"
            >
              {/* 유리의 기본 판 (SVG 필터 연동으로 뒤쪽 화면 굴절) */}
              <div 
                className="absolute inset-0 bg-white/10 rounded-[15px] shadow-[0px_4px_4px_rgba(0,0,0,0.25)] pointer-events-none"
                style={{
                  backdropFilter: 'url(#liquid-glass)',
                  WebkitBackdropFilter: 'url(#liquid-glass)'
                }}
              />
              <span className="relative z-10 font-title text-[24px] text-black pb-1">봇 초대하기</span>
            </a>
            <a
              href="/dashboard"
              className="group relative w-[199px] h-[56px] flex items-center justify-center hover:-translate-y-1 transition-transform duration-300"
            >
              {/* 유리의 기본 판 (SVG 필터 연동으로 뒤쪽 화면 굴절) */}
              <div 
                className="absolute inset-0 bg-white/10 rounded-[15px] shadow-[0px_4px_4px_rgba(0,0,0,0.25)] pointer-events-none"
                style={{
                  backdropFilter: 'url(#liquid-glass)',
                  WebkitBackdropFilter: 'url(#liquid-glass)'
                }}
              />
              <span className="relative z-10 font-title text-[24px] text-black pb-1">대시보드</span>
            </a>
          </motion.div>
        </motion.div>

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
      <section className="py-24 px-6 lg:px-12 relative z-10 bg-white/50 backdrop-blur-sm">
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
      <section className="relative py-12 overflow-hidden z-10 bg-white/40">
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
      <section className="py-24 relative z-10 bg-white/60 backdrop-blur-md">
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
      <footer className="py-8 border-t border-gray-100 relative z-10 bg-white/80">
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
