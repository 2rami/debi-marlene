import { useRef, useEffect, useState } from 'react'
import { motion, useInView, useScroll, useTransform, useMotionValue, useSpring } from 'framer-motion'
import Header from '../components/common/Header'
import FlowingMenu from '../components/common/FlowingMenu'
import GlassButton from '../components/common/GlassButton'
import DonationModal from '../components/common/DonationModal'

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
import BG_FOOTER from '../assets/images/event/footer_bg.png'
import FOOTER_PLATFORM from '../assets/images/event/footer_platform.png'
import FOOTER_CHAR from '../assets/images/event/footer_char.png'
import TWINS_APPROVE from '../assets/images/event/236_twins_approve.png'
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

/* ── Wipe-in effect (GSAP ScrollTrigger) ── */
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
              duration: 2.5,
              ease: 'power2.inOut',
              scrollTrigger: {
                trigger: ref.current,
                start: 'top 85%',
                once: true,
              },
            }
          )
        })
      })
    )
    return () => ctx?.revert()
  }, [])

  return (
    <div ref={ref} className={className} style={{ clipPath: 'inset(0 100% 0 0)' }}>
      {children}
    </div>
  )
}

/* ── Parallax Strip (스크롤보다 빠르게 올라감) ── */
function ParallaxStrip({ children, speed = -150 }: { children: React.ReactNode; speed?: number }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })
  const y = useTransform(scrollYProgress, [0, 1], [0, speed])
  return (
    <div ref={ref} className="relative z-20">
      <motion.div style={{ y }}>
        {children}
      </motion.div>
    </div>
  )
}

/* ── Global Fast-moving Particles ── */
const ICONS = [CHAR_02, CHAR_03, CHAR_05, CHAR_06, CHAR_07, CURSOR, NEW_BADGE];

function GlobalParticles() {
  const [particles, setParticles] = useState<any[]>([]);

  useEffect(() => {
    const w = window.innerWidth || 1200;
    const h = window.innerHeight || 800;

    const items = Array.from({ length: 70 }).map((_, i) => {
      const sizeBase = Math.random() > 0.8 ? 70 : 35;
      return {
        id: i,
        src: ICONS[i % ICONS.length],
        size: sizeBase + Math.random() * 35,
        startY: Math.random() * h,
        startX: w + 100 + Math.random() * 400,
        endX: -200 - Math.random() * 200,
        animDuration: 5 + Math.random() * 10,
        delay: -Math.random() * 20,
        rotationSpeed: (Math.random() > 0.5 ? 1 : -1) * (90 + Math.random() * 270)
      };
    });
    setParticles(items);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
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
  const [isDonationOpen, setIsDonationOpen] = useState(false)

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
    { text: '\u2192  TTS  \u00B7  Stats  \u00B7  Music  \u00B7  Quiz  \u2192' },
  ]

  return (
    <div className="min-h-screen bg-[#e0f7fa] font-body overflow-x-hidden selection:bg-[#3cabc9]/20 relative z-0">
      {/* 텍스처 SVG 필터 — 텍스트용 (피그마 원본 값) */}
      <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden="true">
        <defs>
          <filter id="text-texture" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.339" numOctaves="3" seed="5044" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="4" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>
      </svg>
      <GlobalParticles />
      <Header />

      {/* ══ HERO ══ */}
      <section
        ref={heroRef}
        onMouseMove={handleMouseMove}
        className="relative h-[150vh] min-h-[900px] overflow-hidden"
      >
        {/* z-[0]: Sky background (상단바 영역까지 화면 전체를 덮도록 top 0 근처로 확장) */}
        <motion.div
          className="absolute z-[0] top-0 left-[-5%] w-[110%]"
          style={{ y: skyY, x: layer1X, translateY: layer1Y }}
        >
          <img src={BG_SKY} alt="" className="w-full h-auto opacity-90" draggable={false} />
        </motion.div>

        {/* z-2: Cloud/leaf overlay — Figma: 1763x886, 122% wide, starts at y=392/1258 = 31% */}
        <motion.div
          className="absolute z-[2] top-[20%] left-[-15%] w-[130%] h-[90%]"
          style={{ y: cloudY, x: layer2X, translateY: layer2Y }}
        >
          <img src={BG_CLOUD} alt="" className="w-full h-full object-cover mix-blend-multiply" draggable={false} />
        </motion.div>

        {/* z-[5]: Main character — 데스크톱: 왼쪽 32%, 모바일: 상단 중앙 */}
        <motion.div
          className="absolute z-[5] filter drop-shadow-2xl
            bottom-[5%] left-[32%] w-[64%] max-w-[950px] h-[85%]
            max-md:bottom-auto max-md:top-[8%] max-md:left-[10%] max-md:w-[80%] max-md:h-[50%]"
          style={{ y: charY, x: charMoveX, translateY: charMoveY }}
        >
          <img src={CHAR_HERO} alt="Debi & Marlene" className="w-full h-full object-contain object-bottom" draggable={false} />
        </motion.div>

        {/* z-[3]: Hero text content — 데스크톱: 상단 38vh, 모바일: 하단 배치 */}
        <motion.div
          className="relative z-[3] pl-[6%] pr-6 h-full flex flex-col pointer-events-none
            justify-start pt-[38vh]
            max-md:justify-end max-md:pb-[12vh] max-md:pt-0 max-md:items-center"
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

          <motion.div
            className="mt-1"
            style={{ filter: 'url(#text-texture)' }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            <svg viewBox="0 0 700 190" className="w-[320px] md:w-[650px] lg:w-[700px] h-auto overflow-visible">
              {/* 핑크 아웃라인 (아래 레이어) */}
              <text
                x="0" y="150"
                fontSize="167"
                fontWeight="bold"
                fontFamily="'YPairingFont', system-ui, sans-serif"
                fill="none"
                stroke="#FFA6D7"
                strokeWidth="12"
                paintOrder="stroke"
              >
                대시보드
              </text>
              {/* 시안 채움 (위 레이어) */}
              <text
                x="0" y="150"
                fontSize="167"
                fontWeight="bold"
                fontFamily="'YPairingFont', system-ui, sans-serif"
                fill="#7DE8ED"
                stroke="#FFA6D7"
                strokeWidth="5"
                paintOrder="stroke"
                style={{ filter: 'drop-shadow(0px 4px 6px rgba(212, 103, 158, 0.4))' }}
              >
                대시보드
              </text>
            </svg>
          </motion.div>

          <motion.div
            className="flex gap-4 mt-10 pointer-events-auto max-md:mt-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <GlassButton
              href="https://discord.com/oauth2/authorize?client_id=1393529860793831489&permissions=8&scope=bot%20applications.commands"
              target="_blank"
              rel="noopener noreferrer"
            >
              봇 초대하기
            </GlassButton>
            <GlassButton href="/dashboard">
              대시보드
            </GlassButton>
          </motion.div>
        </motion.div>

        {/* Bottom gradient fade */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-white to-transparent z-[4]" />

        {/* ══ FLOWING MENU STRIP (Hero 중간 아래, 캐릭터/텍스트 뒤) ══ */}
        <div className="absolute left-0 right-0 bottom-[30%] z-[2]">
          <ParallaxStrip speed={-150}>
            <FlowingMenu
              items={menuItems}
              speed={8}
              textColor="#fff8e1"
              bgColor="rgba(255, 214, 100, 0.85)"
              hoverBgColor="rgba(255, 193, 50, 0.95)"
              hoverTextColor="#ffffff"
              borderColor="transparent"
            />
          </ParallaxStrip>
        </div>
      </section>

      {/* ══ FEATURES ══ */}
      <section className="py-24 px-6 lg:px-12 relative z-10 bg-white/50">
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
      <ParallaxStrip speed={-0.3}>
        <FlowingMenu
          items={[
            { text: '\u2192  Welcome  \u00B7  Dashboard  \u00B7  Settings  \u00B7  Premium  \u2192' },
          ]}
          speed={10}
          textColor="#ffffff"
          bgColor="#e58fb6"
          hoverBgColor="#c97a9e"
          hoverTextColor="#ffffff"
          borderColor="transparent"
        />
      </ParallaxStrip>

      {/* ══ STATS ══ */}
      <section className="py-20 bg-gradient-to-r from-[#f472b6] to-[#ec4899] relative z-10">
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

      {/* ══ DONATION ══ */}
      <DonationModal isOpen={isDonationOpen} onClose={() => setIsDonationOpen(false)} />

      {/* ══ FOOTER (CTA + 후원 + 캐릭터 + 카피라이트) ══ */}
      <footer className="relative z-10 overflow-hidden">
        {/* 하늘 배경 — 푸터 전체를 덮음 */}
        <img
          src={BG_FOOTER}
          alt=""
          className="absolute inset-0 w-full h-full object-cover object-bottom"
          draggable={false}
        />
        <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#e0f7fa] to-transparent z-[1]" />

        {/* CTA + 후원 통합 카드 */}
        <div className="relative z-[2] flex justify-center pt-20 px-6">
          <FadeIn className="w-full max-w-3xl">
            <div className="bg-white/60 rounded-3xl border border-white/40 p-8 md:p-12">
              {/* CTA 영역 */}
              <div className="text-center mb-8">
                <p className="font-title text-3xl md:text-4xl text-gray-800 mb-4">
                  봇이 마음에 드셨나요?
                </p>
                <p className="text-gray-500 mb-8 leading-relaxed">
                  지금 바로 서버에 초대해서 데비와 마를렌을 만나보세요.
                </p>
                <div className="flex justify-center gap-4">
                  <GlassButton
                    href="https://discord.com/oauth2/authorize?client_id=1393529860793831489&permissions=8&scope=bot%20applications.commands"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    봇 초대하기
                  </GlassButton>
                  <GlassButton href="/dashboard">
                    대시보드
                  </GlassButton>
                </div>
              </div>

              {/* 구분선 */}
              <div className="border-t border-gray-200/50 my-8" />

              {/* 후원 영역 */}
              <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="flex-1 text-center md:text-left">
                  <p className="font-title text-2xl md:text-3xl bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent mb-4">
                    <ElectricText>개발자 응원하기</ElectricText>
                  </p>
                  <p className="font-body text-gray-600 text-sm leading-relaxed mb-6">
                    여러분의 소중한 후원은 서버 운영과 새로운 기능 개발에 큰 힘이 됩니다.<br className="hidden md:block" />
                    <span className="text-gray-800 font-semibold">특별한 후원자 배지</span>와 <span className="text-gray-800 font-semibold">우선 지원 혜택</span>을 드립니다.
                  </p>
                  <GlassButton
                    as="button"
                    onClick={() => setIsDonationOpen(true)}
                  >
                    후원하기
                  </GlassButton>
                </div>
                <div className="w-36 h-36 md:w-44 md:h-44 rounded-full bg-white/40 flex items-center justify-center shrink-0">
                  <img src={TWINS_APPROVE} alt="" className="w-28 md:w-36 h-auto object-contain" draggable={false} />
                </div>
              </div>
            </div>
          </FadeIn>
        </div>

        {/* 발판 + 캐릭터 + 카피라이트 (3레이어) */}
        <div className="relative z-[2] mt-2">
          {/* 레이어1: 발판 (항상 보임) */}
          <img
            src={FOOTER_PLATFORM}
            alt=""
            className="w-full h-auto block"
            draggable={false}
          />
          {/* 레이어2: 캐릭터 (wipe 효과) */}
          <WipeIn className="absolute inset-0 z-[1]">
            <img
              src={FOOTER_CHAR}
              alt="Debi & Marlene"
              className="w-full h-full object-contain"
              draggable={false}
            />
          </WipeIn>
          {/* 레이어3: 카피라이트 — 발판 위에 겹침 */}
          <div className="absolute z-[3] inset-x-0 bottom-2 text-center">
            <p className="font-title text-lg text-white/80 drop-shadow-md">
              Debi & Marlene<span className="text-[#7DE8ED]">.</span>
            </p>
            <p className="text-xs text-white/60 mt-1 drop-shadow-md">
              Eternal Return and all related content are trademarks of Nimble Neuron.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
