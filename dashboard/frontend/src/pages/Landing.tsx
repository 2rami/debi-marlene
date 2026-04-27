import { useRef, useEffect, useState } from 'react'
import { motion, useInView, useScroll, useTransform, useMotionValue, useSpring } from 'framer-motion'
import Lenis from 'lenis'
import Header from '../components/common/Header'
import FlowingMenu from '../components/common/FlowingMenu'
import GlassButton from '../components/common/GlassButton'
import GradientText from '../components/common/GradientText'
import DonationModal from '../components/common/DonationModal'
import ScrollFloat from '../components/common/ScrollFloat'
import DecryptedText from '../components/common/DecryptedText'
import { api } from '../services/api'

/* ── Assets ── */
import BG_SKY from '../assets/images/event/imgi_28_bg01.png'
import BG_CLOUD from '../assets/images/event/imgi_31_bg02.png'
import CHAR_HERO from '../assets/images/event/imgi_30_ch01_v2.png'
// import CHAR_SITTING from '../assets/images/event/imgi_62_ch04.png'
import CHAR_02 from '../assets/images/event/imgi_47_ch02.png'
import CHAR_03 from '../assets/images/event/imgi_48_ch03.png'
import CHAR_05 from '../assets/images/event/imgi_49_ch05.png'
import CHAR_06 from '../assets/images/event/imgi_50_ch06.png'
import CHAR_07 from '../assets/images/event/imgi_51_ch07.png'
import NEW_BADGE from '../assets/images/event/imgi_77_new.png'
import BG_FOOTER from '../assets/images/event/footer_bg.png'
import FOOTER_PLATFORM from '../assets/images/event/footer_platform.png'
import FOOTER_CHAR from '../assets/images/event/footer_char.png'
// import TWINS_APPROVE from '../assets/images/event/236_twins_approve.png'
import HIGHFIVE_GIF from '../assets/images/event/highfive.gif'
import CHAR_CLASSROOM from '../assets/images/event/char_classroom.png'
import CHAR_SUMMER from '../assets/images/event/char_summer.png'
import CHAR_BATTLE from '../assets/images/event/char_battle.png'
import CHAR_BATTLE2 from '../assets/images/event/char_battle2.png'
import CURSOR from '../assets/images/event/imgi_45_cursor01.png'
// import SS_STATS from '../assets/images/event/screenshot_stats.png'
import SS_RECORD from '../assets/images/event/screenshot_record.png'
import SS_MUSIC from '../assets/images/event/screenshot_music.png'
import TWINS_CIRCLE from '../assets/images/event/twins_approve_circle.png'
import EMOTICON_UNIFORM from '../assets/images/event/emoticon_uniform.png'
import CircularText from '../components/common/CircularText'
import { useAuth } from '../contexts/AuthContext'

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
    <div ref={ref} className="relative z-[3]">
      <motion.div style={{ y }}>
        {children}
      </motion.div>
    </div>
  )
}

/* ── Audio Player ── */
function AudioPlayer({ label, src }: { label: string; src: string }) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)

  const toggle = () => {
    if (!audioRef.current) return
    if (playing) { audioRef.current.pause() }
    else { audioRef.current.play() }
    setPlaying(!playing)
  }

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    const onTime = () => setProgress(audio.duration ? (audio.currentTime / audio.duration) * 100 : 0)
    const onEnd = () => { setPlaying(false); setProgress(0) }
    audio.addEventListener('timeupdate', onTime)
    audio.addEventListener('ended', onEnd)
    return () => { audio.removeEventListener('timeupdate', onTime); audio.removeEventListener('ended', onEnd) }
  }, [])

  return (
    <div
      className="flex items-center gap-4 bg-white/60 backdrop-blur-md rounded-2xl px-5 py-4 shadow-lg cursor-pointer group"
      onClick={toggle}
    >
      <audio ref={audioRef} src={src} preload="metadata" />
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#3cabc9] to-[#e58fb6] flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
        {playing ? (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="white"><rect x="3" y="2" width="4" height="12" rx="1" /><rect x="9" y="2" width="4" height="12" rx="1" /></svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="white"><path d="M4 2l10 6-10 6V2z" /></svg>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-title text-sm text-gray-700 truncate">{label}</div>
        <div className="h-1.5 bg-gray-200 rounded-full mt-1.5 overflow-hidden">
          <div className="h-full bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] rounded-full transition-all duration-200" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  )
}

/* ── Parallax Feature Section ── */
function ParallaxFeature({
  image, titleLines, description, keywords, align = 'left',
  titleColor, shadowColor: _sc, screenshot, audioFiles, children,
}: {
  image: string
  titleLines: string[]
  description: string
  keywords: string[]
  align?: 'left' | 'right'
  titleColor: string
  shadowColor: string
  screenshot?: string
  audioFiles?: { label: string; src: string }[]
  children?: React.ReactNode
}) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })

  // 캐릭터: 느리게 (스크롤 대비 적게 움직임)
  const charY = useTransform(scrollYProgress, [0, 1], [80, -80])
  // 키워드 장식: 빠르게
  const decoY = useTransform(scrollYProgress, [0, 1], [150, -250])

  const isLeft = align === 'left'

  return (
    <div ref={ref} className="relative overflow-hidden py-60 md:py-80">
      {/* 캐릭터: absolute, 느린 패럴랙스, 텍스트 반대쪽에 배치 */}
      <motion.div
        className={`absolute inset-y-0 z-[3] pointer-events-none flex items-center ${isLeft ? 'right-[-15%] justify-end' : 'left-[-15%] justify-start'}`}
        style={{ y: charY, width: '65%' }}
      >
        <img
          src={image} alt="" className="w-full h-auto object-contain" draggable={false}
          style={{ animation: 'electricOutline 3s ease-in-out infinite' }}
        />
      </motion.div>

      {/* 키워드 장식: 빠른 패럴랙스 */}
      <motion.div
        className={`absolute ${isLeft ? 'right-[5%] md:right-[10%]' : 'left-[5%] md:left-[10%]'} top-0 h-full flex flex-col justify-center gap-4 opacity-[0.6] pointer-events-none z-[2]`}
        style={{ y: decoY }}
      >
        {keywords.map((kw, i) => (
          <span key={i} className={`font-title text-[80px] md:text-[140px] lg:text-[200px] leading-none ${titleColor} whitespace-nowrap`}>
            {kw}
          </span>
        ))}
      </motion.div>

      {/* 콘텐츠: 일반 스크롤 속도 */}
      <div className={`relative z-[5] px-6 lg:px-16 ${isLeft ? '' : 'text-right'}`}>
        {titleLines.map((line, i) => {
          const charCount = line.length
          const vw = charCount <= 2 ? 350 * charCount : 280 * charCount
          return (
            <div key={i} className={`${isLeft ? '' : 'flex justify-end'}`} style={{ filter: 'url(#text-texture)' }}>
              <svg viewBox={`0 0 ${vw} 250`} className="w-[350px] md:w-[650px] lg:w-[850px] h-auto overflow-visible block">
                <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="none" stroke="#FFA6D7" strokeWidth="12" paintOrder="stroke">{line}</text>
                <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="#7DE8ED" stroke="#FFA6D7" strokeWidth="5" paintOrder="stroke" style={{ filter: 'drop-shadow(0px 4px 6px rgba(212, 103, 158, 0.4))' }}>{line}</text>
              </svg>
            </div>
          )
        })}
        <p className={`font-bold text-gray-800 text-2xl md:text-3xl leading-relaxed max-w-xl mt-12 ${isLeft ? '' : 'ml-auto'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
          {description}
        </p>

        {/* 스크린샷 */}
        {screenshot && (
          <FadeIn className={`mt-16 ${isLeft ? '' : 'flex justify-end'}`}>
            <div className="relative max-w-xs md:max-w-sm">
              <div className="absolute -inset-4 bg-gradient-to-br from-[#3cabc9]/20 to-[#e58fb6]/20 rounded-3xl blur-xl" />
              <img
                src={screenshot}
                alt="Bot screenshot"
                className="relative w-full h-auto rounded-2xl shadow-2xl border border-white/30"
                draggable={false}
              />
            </div>
          </FadeIn>
        )}

        {/* 오디오 플레이어 */}
        {audioFiles && (
          <FadeIn className={`mt-16 ${isLeft ? '' : 'flex justify-end'}`}>
            <div className="flex flex-col gap-4 max-w-sm">
              {audioFiles.map((af, i) => (
                <AudioPlayer key={i} label={af.label} src={af.src} />
              ))}
            </div>
          </FadeIn>
        )}

        {children}
      </div>
    </div>
  )
}

/* ── Floating Split Button (우측하단) ── */
function FloatingSplitButton() {
  const { user, logout } = useAuth()
  const [hovered, setHovered] = useState(false)

  return (
    <div
      className="fixed bottom-8 right-8 z-[50] w-[140px] h-[140px] md:w-[160px] md:h-[160px]"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* 유리구름 배경 */}
      <div
        className="absolute inset-0 rounded-full shadow-[0_4px_24px_rgba(0,0,0,0.1)] transition-all duration-300"
        style={{
          background: 'rgba(255,255,255,0.85)',
          filter: 'url(#float-cloud)',
          transform: hovered ? 'scale(1.05)' : 'scale(1)',
        }}
      />

      {/* 기본 상태: CircularText + 이미지 */}
      <div className={`absolute inset-0 transition-all duration-300 ${hovered ? 'opacity-0 scale-90' : 'opacity-100 scale-100'}`}>
        <CircularText
          text="DASHBOARD * DEBI & MARLENE * "
          spinDuration={15}
          onHover="speedUp"
          className="w-[140px] h-[140px] md:w-[160px] md:h-[160px] text-gray-500"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <img src={TWINS_CIRCLE} alt="" className="w-16 h-16 md:w-20 md:h-20 rounded-full object-cover" draggable={false} />
        </div>
      </div>

      {/* 호버 상태: 스플릿 */}
      <div className={`absolute inset-0 transition-all duration-300 ${hovered ? 'opacity-100 scale-100' : 'opacity-0 scale-110'}`}>
        {/* 위쪽 — 대시보드 */}
        <a
          href="/dashboard"
          className="absolute top-0 left-0 right-0 h-1/2 flex flex-col items-center justify-center rounded-t-full overflow-hidden group/top hover:bg-[#3cabc9]/10 transition-colors"
        >
          <img src={TWINS_CIRCLE} alt="" className="w-10 h-10 md:w-12 md:h-12 rounded-full object-cover group-hover/top:scale-110 transition-transform" draggable={false} />
          <span className="font-title text-[10px] md:text-xs text-[#3cabc9] mt-1">Dashboard</span>
        </a>
        {/* 구분선 */}
        <div className="absolute top-1/2 left-[15%] right-[15%] h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent" />
        {/* 아래쪽 — 로그아웃 (로그인 시) / 로그인 (비로그인 시) */}
        {user ? (
          <button
            onClick={(e) => { e.stopPropagation(); logout() }}
            className="absolute bottom-0 left-0 right-0 h-1/2 flex flex-col items-center justify-center rounded-b-full overflow-hidden group/bot hover:bg-[#e58fb6]/10 transition-colors"
          >
            <img src={EMOTICON_UNIFORM} alt="" className="w-10 h-10 md:w-12 md:h-12 rounded-full object-cover group-hover/bot:scale-110 transition-transform" draggable={false} />
            <span className="font-title text-[10px] md:text-xs text-[#e58fb6] mt-1">Logout</span>
          </button>
        ) : (
          <a
            href="/dashboard"
            className="absolute bottom-0 left-0 right-0 h-1/2 flex flex-col items-center justify-center rounded-b-full overflow-hidden group/bot hover:bg-[#e58fb6]/10 transition-colors"
          >
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#e58fb6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" /><polyline points="10 17 15 12 10 7" /><line x1="15" y1="12" x2="3" y2="12" />
            </svg>
            <span className="font-title text-[10px] md:text-xs text-[#e58fb6] mt-1">Login</span>
          </a>
        )}
      </div>
    </div>
  )
}

/* ── Global Fast-moving Particles ── */
const ICONS = [CHAR_02, CHAR_03, CHAR_05, CHAR_06, CHAR_07, CURSOR];

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
    <div className="fixed inset-0 pointer-events-none z-[2] overflow-hidden">
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

/* ── Feature card (unused, kept for reference) ── */

/* ══════════════════════════════════════════════
   Landing Page
   ══════════════════════════════════════════════ */
export default function Landing() {
  const heroRef = useRef(null)
  const [isDonationOpen, setIsDonationOpen] = useState(false)
  const [stats, setStats] = useState<{ users: number; servers: number; commands: number } | null>(null)
  // auth는 FloatingSplitButton에서 사용

  // Lenis 스무스 스크롤
  useEffect(() => {
    api.get<{ stats: { users: number; servers: number; commands: number } }>('/bot/stats')
      .then(r => setStats(r.data.stats))
      .catch(() => {})
  }, [])

  // Lenis 스무스 스크롤
  useEffect(() => {
    const lenis = new Lenis({ duration: 5, wheelMultiplier: 0.5, easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
    (window as any).__lenis = lenis
    function raf(time: number) { lenis.raf(time); requestAnimationFrame(raf) }
    requestAnimationFrame(raf)
    return () => { lenis.destroy(); (window as any).__lenis = null }
  }, [])

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

  // 띠 색상 (여기만 바꾸면 전체 반영)
  const STRIP_CYAN = { bg: '#50d9ff', hover: '#61ddff', text: '#ffffff', hoverText: '#ffffff' }
  const STRIP_PINK = { bg: '#E58FB6', hover: '#ffa2cc', text: '#ffffff', hoverText: '#ffffff' }

  return (
    <div className="min-h-screen bg-[#f8fcfd] font-body selection:bg-[#3cabc9]/20 relative z-0" style={{ overflowX: 'clip' }}>
      {/* 텍스처 SVG 필터 — 텍스트용 (피그마 원본 값) */}
      <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden="true">
        <defs>
          <filter id="text-texture" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.339" numOctaves="3" seed="5044" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="4" xChannelSelector="R" yChannelSelector="G" />
          </filter>
          <filter id="glass-cloud" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.3" numOctaves="4" seed="5730" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>
      </svg>
      <GlobalParticles />
      <Header />

      {/* ══ HERO ══ */}
      <section
        ref={heroRef}
        onMouseMove={handleMouseMove}
        className="relative h-screen min-h-[700px]"
      >
        {/* z-[0]: Sky background (상단바 영역까지 화면 전체를 덮도록 top 0 근처로 확장) */}
        <motion.div
          className="absolute z-[0] top-0 left-[-5%] w-[110%]"
          style={{ y: skyY, x: layer1X, translateY: layer1Y }}
        >
          <img src={BG_SKY} alt="" className="w-full h-auto" draggable={false} />
        </motion.div>

        {/* z-[3]: Cloud/leaf overlay */}
        <motion.div
          className="absolute z-[6] top-[20%] left-[-15%] w-[130%] h-[90%] pointer-events-none"
          style={{ y: cloudY, x: layer2X, translateY: layer2Y }}
        >
          <img src={BG_CLOUD} alt="" className="w-full h-full object-cover mix-blend-multiply" draggable={false} />
        </motion.div>

        {/* z-[5]: Main character — 데스크톱: 왼쪽 32%, 모바일: 상단 중앙 */}
        <motion.div
          className="absolute z-[7] pointer-events-none
            bottom-[5%] left-[32%] w-[64%] max-w-[950px] h-[85%]
            max-md:bottom-auto max-md:top-[8%] max-md:left-[10%] max-md:w-[80%] max-md:h-[50%]"
          style={{ y: charY, x: charMoveX, translateY: charMoveY }}
        >
          <img src={CHAR_HERO} alt="Debi & Marlene" className="w-full h-full object-contain object-bottom" draggable={false} />
        </motion.div>

        {/* z-[3]: Hero text content — 데스크톱: 상단 38vh, 모바일: 하단 배치 */}
        <motion.div
          className="relative z-[5] pl-[6%] pr-6 h-full flex flex-col pointer-events-none
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

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <GradientText
              colors={['#3cabc9', '#e58fb6', '#7DE8ED', '#FFA6D7', '#3cabc9']}
              animationSpeed={5}
              className="!mx-0 font-title text-[28px] md:text-[43.08px] leading-normal whitespace-nowrap"
              pauseOnHover
            >
              데비&마를렌 봇
            </GradientText>
          </motion.div>

          <motion.div
            className="mt-1"
            style={{ filter: 'url(#text-texture)' }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
          >
            <svg viewBox="0 0 700 190" className="w-[320px] md:w-[650px] lg:w-[700px] h-auto overflow-visible">
              <text x="0" y="150" fontSize="167" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="none" stroke="#FFA6D7" strokeWidth="12" paintOrder="stroke">대시보드</text>
              <text x="0" y="150" fontSize="167" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="#7DE8ED" stroke="#FFA6D7" strokeWidth="5" paintOrder="stroke" style={{ filter: 'drop-shadow(0px 4px 6px rgba(212, 103, 158, 0.4))' }}>대시보드</text>
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

        {/* Bottom gradient fade — 제거됨 */}

        {/* ══ FLOWING MENU STRIP (Hero 중간 아래) ══ */}
        <div className="absolute left-0 right-0 top-[25%] z-[2]">
          <ParallaxStrip speed={-150}>
            <FlowingMenu
              items={[{ text: 'TTS  >  Stats  >  Music  >  Quiz  >  Welcome  >' }]}
              speed={8}
              textColor={STRIP_CYAN.text} bgColor={STRIP_CYAN.bg} hoverBgColor={STRIP_CYAN.hover} hoverTextColor={STRIP_CYAN.hoverText}
              borderColor="transparent" fontSize="text-4xl md:text-5xl" padding="py-8 md:py-12" glassEffect
            />
          </ParallaxStrip>
        </div>
      </section>

      {/* ══ FEATURES (세로 4개 기능 소개) ══ */}
      <div className="relative z-[5]">
        {/* 섹션 타이틀 */}
        <div className="text-center py-24 px-6">
          <ScrollFloat
            containerClassName="font-title bg-gradient-to-r from-[#e58fb6] to-[#3cabc9] bg-clip-text text-transparent leading-tight"
            textClassName="text-5xl md:text-[74px]"
          >
            주요 기능
          </ScrollFloat>
          <ScrollFloat
            containerClassName="font-title text-gray-700 mt-4"
            textClassName="text-xl md:text-3xl"
            stagger={0.02}
          >
            하나의 봇으로 모든 기능을
          </ScrollFloat>
        </div>

        {/* 기능 1: TTS + 띠 (캐릭터 뒤, 상단) */}
        <div className="relative">
          <div className="absolute top-[15%] left-0 right-0 z-[2] -rotate-2">
            <ParallaxStrip speed={-120}>
              <FlowingMenu
                items={[{ text: 'TTS  >  Voice  >  AI  >  Character  >  Speech  >' }]}
                speed={8} textColor={STRIP_CYAN.text} bgColor={STRIP_CYAN.bg} hoverBgColor={STRIP_CYAN.hover} hoverTextColor={STRIP_CYAN.hoverText} borderColor="transparent"
                fontSize="text-3xl md:text-5xl" padding="py-6 md:py-10" glassEffect
              />
            </ParallaxStrip>
          </div>
          <ParallaxFeature
            image={CHAR_CLASSROOM}
            titleLines={['고품질', 'TTS']}
            description="데비와 마를렌의 목소리로 채팅을 읽어줍니다. AI 파인튜닝 모델 기반의 자연스러운 캐릭터 음성."
            keywords={['VOICE', 'AI', 'SPEECH']}
            align="left"
            titleColor="text-[#3cabc9]"
            shadowColor="rgba(60,171,201,0.4)"
            audioFiles={[
              { label: 'Debi Voice Demo', src: '/audio/demo_debi_desc.wav' },
              { label: 'Marlene Voice Demo', src: '/audio/demo_marlene_desc.wav' },
            ]}
          />
        </div>

        {/* 섹션 사이 띠 */}
        <div className="my-16">
          <ParallaxStrip speed={-200}>
            <FlowingMenu
              items={[{ text: 'Stats  >  MMR  >  Rank  >  Analysis  >  Stats  >' }]}
              speed={10} textColor={STRIP_PINK.text} bgColor={STRIP_PINK.bg} hoverBgColor={STRIP_PINK.hover} hoverTextColor={STRIP_PINK.hoverText} borderColor="transparent"
              fontSize="text-4xl md:text-6xl" padding="py-8 md:py-12" glassEffect
            />
          </ParallaxStrip>
        </div>

        {/* 기능 2: 전적 검색 + 띠 (캐릭터 뒤, 하단) */}
        <div className="relative">
          <div className="absolute bottom-[10%] left-0 right-0 z-[2] rotate-1">
            <ParallaxStrip speed={-150}>
              <FlowingMenu
                items={[{ text: 'Eternal Return  >  Record  >  Search  >  Stats  >' }]}
                speed={6} textColor={STRIP_CYAN.text} bgColor={STRIP_CYAN.bg} hoverBgColor={STRIP_CYAN.hover} hoverTextColor={STRIP_CYAN.hoverText} borderColor="transparent"
                fontSize="text-3xl md:text-5xl" padding="py-6 md:py-10" glassEffect
              />
            </ParallaxStrip>
          </div>
          <ParallaxFeature
            image={CHAR_SUMMER}
            titleLines={['전적', '검색']}
            description="이터널리턴 전적과 캐릭터 통계를 한눈에. MMR 그래프, 팀원 분석까지 Discord 안에서 바로 확인."
            keywords={['STATS', 'MMR', 'RANK']}
            align="right"
            titleColor="text-[#3cabc9]"
            shadowColor="rgba(60,171,201,0.4)"
            screenshot={SS_RECORD}
          />
        </div>

        {/* 섹션 사이 띠 */}
        <div className="my-16">
          <ParallaxStrip speed={-180}>
            <FlowingMenu
              items={[{ text: 'Music  >  Queue  >  Quiz  >  YouTube  >  Play  >' }]}
              speed={12} textColor={STRIP_PINK.text} bgColor={STRIP_PINK.bg} hoverBgColor={STRIP_PINK.hover} hoverTextColor={STRIP_PINK.hoverText} borderColor="transparent"
              fontSize="text-4xl md:text-6xl" padding="py-8 md:py-12" glassEffect
            />
          </ParallaxStrip>
        </div>

        {/* 기능 3: 음악 재생 + 띠 (캐릭터 위, 중앙) */}
        <div className="relative">
          <div className="absolute top-[40%] left-0 right-0 z-[2] -rotate-1">
            <ParallaxStrip speed={-170}>
              <FlowingMenu
                items={[{ text: 'Now Playing  >  Skip  >  Pause  >  Queue  >' }]}
                speed={9} textColor={STRIP_CYAN.text} bgColor={STRIP_CYAN.bg} hoverBgColor={STRIP_CYAN.hover} hoverTextColor={STRIP_CYAN.hoverText} borderColor="transparent"
                fontSize="text-3xl md:text-5xl" padding="py-6 md:py-10" glassEffect
              />
            </ParallaxStrip>
          </div>
          <ParallaxFeature
            image={CHAR_BATTLE}
            titleLines={['음악', '재생']}
            description="유튜브 검색 기반 음악과 대기열 관리. 노래 퀴즈까지 음성 채널에서 함께 즐기세요."
            keywords={['MUSIC', 'QUEUE', 'PLAY']}
            align="left"
            titleColor="text-[#e58fb6]"
            shadowColor="rgba(229,143,182,0.4)"
            screenshot={SS_MUSIC}
          />
        </div>

        {/* 섹션 사이 띠 */}
        <div className="my-16">
          <ParallaxStrip speed={-140}>
            <FlowingMenu
              items={[{ text: 'Welcome  >  Dashboard  >  Settings  >  Premium  >' }]}
              speed={10} textColor={STRIP_CYAN.text} bgColor={STRIP_CYAN.bg} hoverBgColor={STRIP_CYAN.hover} hoverTextColor={STRIP_CYAN.hoverText} borderColor="transparent"
              fontSize="text-4xl md:text-6xl" padding="py-8 md:py-12" glassEffect
            />
          </ParallaxStrip>
        </div>

        {/* 기능 4: 환영 메시지 + 띠 (캐릭터 뒤, 상단) */}
        <div className="relative">
          <div className="absolute top-[20%] left-0 right-0 z-[2] rotate-2">
            <ParallaxStrip speed={-190}>
              <FlowingMenu
                items={[{ text: 'Greet  >  Welcome  >  Join  >  Hello  >' }]}
                speed={7} textColor={STRIP_PINK.text} bgColor={STRIP_PINK.bg} hoverBgColor={STRIP_PINK.hover} hoverTextColor={STRIP_PINK.hoverText} borderColor="transparent"
                fontSize="text-3xl md:text-5xl" padding="py-6 md:py-10" glassEffect
              />
            </ParallaxStrip>
          </div>
          <ParallaxFeature
            image={CHAR_BATTLE2}
            titleLines={['환영', '메시지']}
            description="새로운 멤버가 들어오면 자동으로 환영 메시지를 보내줍니다. 커스텀 메시지와 채널 설정까지."
            keywords={['WELCOME', 'GREET', 'JOIN']}
            align="right"
            titleColor="text-[#e58fb6]"
            shadowColor="rgba(229,143,182,0.4)"
          />
        </div>
      </div>

      {/* ══ STATS ══ */}
      <div className="py-28 relative z-[5]">
        <div className="text-center mb-16">
          <ScrollFloat
            containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent"
            textClassName="text-5xl md:text-[80px]"
          >
            Numbers
          </ScrollFloat>
        </div>
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-3 gap-6 md:gap-10">
            <FadeIn delay={0.1}>
              <div className="p-8 md:p-10 text-center">
                {stats ? (
                  <DecryptedText
                    text={stats.users.toLocaleString('en-US')}
                    className="font-title text-5xl md:text-7xl lg:text-8xl font-bold bg-gradient-to-b from-[#3cabc9] to-[#3cabc9]/60 bg-clip-text text-transparent"
                    encryptedClassName="font-title text-5xl md:text-7xl lg:text-8xl font-bold text-[#3cabc9]/30"
                    animateOn="inViewHover"
                    speed={40}
                    maxIterations={15}
                    sequential
                    characters="0123456789,."
                  />
                ) : (
                  <div className="h-[3rem] md:h-[4.5rem] lg:h-[6rem] w-40 md:w-56 lg:w-64 mx-auto bg-[#3cabc9]/10 rounded-lg animate-pulse" aria-label="loading" />
                )}
                <div className="font-body text-sm md:text-lg mt-3 text-gray-500 tracking-wider uppercase">Users</div>
              </div>
            </FadeIn>
            <FadeIn delay={0.2}>
              <div className="p-8 md:p-10 text-center">
                {stats ? (
                  <DecryptedText
                    text={String(stats.servers)}
                    className="font-title text-5xl md:text-7xl lg:text-8xl font-bold bg-gradient-to-b from-[#e58fb6] to-[#e58fb6]/60 bg-clip-text text-transparent"
                    encryptedClassName="font-title text-5xl md:text-7xl lg:text-8xl font-bold text-[#e58fb6]/30"
                    animateOn="inViewHover"
                    speed={40}
                    maxIterations={15}
                    sequential
                    characters="0123456789"
                  />
                ) : (
                  <div className="h-[3rem] md:h-[4.5rem] lg:h-[6rem] w-24 md:w-32 lg:w-40 mx-auto bg-[#e58fb6]/10 rounded-lg animate-pulse" aria-label="loading" />
                )}
                <div className="font-body text-sm md:text-lg mt-3 text-gray-500 tracking-wider uppercase">Servers</div>
              </div>
            </FadeIn>
            <FadeIn delay={0.3}>
              <div className="p-8 md:p-10 text-center">
                {stats ? (
                  <DecryptedText
                    text={String(stats.commands)}
                    className="font-title text-5xl md:text-7xl lg:text-8xl font-bold bg-gradient-to-b from-[#7DE8ED] to-[#7DE8ED]/60 bg-clip-text text-transparent"
                    encryptedClassName="font-title text-5xl md:text-7xl lg:text-8xl font-bold text-[#7DE8ED]/30"
                    animateOn="inViewHover"
                    speed={40}
                    maxIterations={15}
                    sequential
                    characters="0123456789"
                  />
                ) : (
                  <div className="h-[3rem] md:h-[4.5rem] lg:h-[6rem] w-20 md:w-28 lg:w-32 mx-auto bg-[#7DE8ED]/10 rounded-lg animate-pulse" aria-label="loading" />
                )}
                <div className="font-body text-sm md:text-lg mt-3 text-gray-500 tracking-wider uppercase">Commands</div>
              </div>
            </FadeIn>
          </div>
        </div>
      </div>

      {/* ══ DONATION ══ */}
      <DonationModal isOpen={isDonationOpen} onClose={() => setIsDonationOpen(false)} />

      {/* ══ 우측하단 스플릿 플로팅 버튼 ══ */}
      <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden="true">
        <defs>
          <filter id="float-cloud" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.3" numOctaves="4" seed="4242" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>
      </svg>
      <FloatingSplitButton />

      {/* ══ FOOTER (CTA + 후원 + 캐릭터 + 카피라이트) ══ */}
      <footer className="relative z-[5] overflow-hidden">
        {/* 하늘 배경 — 푸터 전체를 덮음 */}
        <img
          src={BG_FOOTER}
          alt=""
          className="absolute inset-0 w-full h-full object-cover object-bottom"
          draggable={false}
        />
        <div className="absolute inset-x-0 top-0 h-64 bg-gradient-to-b from-[#f8fcfd] via-[#f8fcfd]/80 to-transparent z-[1]" />

        {/* CTA + 후원 통합 카드 */}
        <div className="relative z-[2] flex justify-center pt-20 px-6">
          <FadeIn className="w-full max-w-3xl">
            <div className="bg-white/60 rounded-3xl border border-white/40 p-8 md:p-12">
              {/* CTA 영역 */}
              <div className="text-center mb-8">
                <ScrollFloat
                  containerClassName="font-title text-gray-800 mb-4"
                  textClassName="text-3xl md:text-4xl"
                >
                  봇이 마음에 드셨나요?
                </ScrollFloat>
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
                  <img src={HIGHFIVE_GIF} alt="" className="w-32 md:w-40 h-auto object-contain" draggable={false} />
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
