import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useEffect, useState } from 'react'
import Header from '../components/common/Header'
import { api } from '../services/api'
import { motion, useScroll, useTransform } from 'framer-motion'
import { 
  Mic,
  Search,
  Youtube,
  Music,
  MessageSquare,
  Users,
  Server,
  Terminal
} from 'lucide-react'
import AnimatedSection from '../components/common/AnimatedSection'
import GreetingPreview from '../components/landing/GreetingPreview'
import DonationModal from '../components/common/DonationModal'

// Event Assets for Redesign
import HERO_SKY from '../assets/images/event/imgi_28_bg01.png'
import HERO_MAIN from '../assets/images/event/imgi_30_ch01.png'
import HERO_BIKE from '../assets/images/event/imgi_31_bg02.png'
import FEATURE_BG from '../assets/images/event/imgi_29_bg03.png'
import LOGO_WHITE from '../assets/images/event/imgi_2_logo_white.png'

// Image Buttons
import BTN_START from '../assets/images/event/imgi_105_btn_start.png'
import BTN_GAME01 from '../assets/images/event/imgi_92_btn_game01.png'
import BTN_GAME02 from '../assets/images/event/imgi_93_btn_game02.png'
import BTN_GAME03 from '../assets/images/event/imgi_95_btn_game03.png'

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
  const y1 = useTransform(scrollY, [0, 1000], [0, 300])
  const y2 = useTransform(scrollY, [0, 800], [0, -100])
  const opacityHeroBg = useTransform(scrollY, [0, 600], [1, 0.2])

  const handleDashboard = () => {
    if (user) {
      navigate('/dashboard')
    } else {
      login()
    }
  }

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get<{ stats: BotStats, botClientId: string }>('/bot/stats')
        setStats(response.data.stats)
        setBotClientId(response.data.botClientId)
      } catch {
        // 실패해도 기본값 사용
      }
    }
    fetchStats()
  }, [])

  const getInviteUrl = () => {
    if (!botClientId) return 'https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands'
    return `https://discord.com/api/oauth2/authorize?client_id=${botClientId}&permissions=8&scope=bot%20applications.commands`
  }

  const features = [
    {
      title: '고품질 음성 TTS',
      description: '채팅 메시지를 음성으로 더욱 생생하게! 데비와 마를렌의 음성을 지원합니다.',
      highlights: ['커스텀 음성', '채널 설정', '생동감 최고'],
      icon: Mic,
      color: "from-[#FF9A9E] to-[#FECFEF]",
      textColor: "text-pink-400"
    },
    {
      title: '이터널리턴 전적',
      description: '전적 검색 및 통계, 추천 캐릭터까지 디스코드에서 바로 확인 가능합니다.',
      highlights: ['빠른 검색', '캐릭터 통계', '편리함'],
      icon: Search,
      color: "from-[#a18cd1] to-[#fbc2eb]",
      textColor: "text-purple-400"
    },
    {
      title: '유튜브 알림',
      description: '구독 채널의 새 영상을 놓치지 않도록 채널과 DM으로 알려드립니다.',
      highlights: ['실시간 알림', 'DM 송출'],
      icon: Youtube,
      color: "from-[#ff9a44] to-[#fc6076]",
      textColor: "text-orange-400"
    },
    {
      title: '완벽한 음악 재생',
      description: '유튜브 검색 기반 음악 재생과 편리한 대기열 관리 UI를 제공합니다.',
      highlights: ['YouTube 검색', 'UI 대기열 조작'],
      icon: Music,
      color: "from-[#4facfe] to-[#00f2fe]",
      textColor: "text-blue-400"
    },
  ]

  return (
    <div className="min-h-screen bg-discord-darkest overflow-x-hidden selection:bg-debi-primary/30 selection:text-white font-sans">
      <Header />

      <DonationModal
        isOpen={isDonationModalOpen}
        onClose={() => setIsDonationModalOpen(false)}
      />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-20 overflow-hidden bg-discord-darkest flex-col justify-center">
        {/* Parallax Background */}
        <motion.div
          style={{ y: y1, opacity: opacityHeroBg }}
          className="absolute inset-0 z-0 pointer-events-none"
        >
          <div className="absolute inset-0 bg-gradient-to-b from-discord-darkest/40 via-transparent to-discord-darkest/95 z-20 mix-blend-multiply" />
          <div className="absolute inset-0 bg-black/50 z-20 mix-blend-overlay" />
          <img src={HERO_SKY} alt="Hero Background" className="w-full h-full object-cover object-top opacity-70" />
        </motion.div>

        {/* Content Container */}
        <div className="relative z-30 w-full max-w-7xl mx-auto px-6 grid xl:grid-cols-[1.2fr_1fr] gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="text-left"
          >
            <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 mb-8 shadow-2xl">
               <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_10px_#4ade80]" />
               <span className="text-base font-bold text-white tracking-wide">누적 {stats.servers.toLocaleString()}개 서버에서 활약 중 🚀</span>
            </div>

            {/* Custom Text Title */}
            <h1 className="text-6xl md:text-8xl font-black mb-6 leading-[1.1] text-white tracking-tight">
              <span className="inline-block px-4 py-2 bg-clip-text text-transparent bg-gradient-to-br from-[#FF6B6B] to-[#FFE66D] drop-shadow-[0_0_20px_rgba(255,107,107,0.5)] transform -rotate-2">
                데비 & 마를렌 봇
              </span><br />
              <span className="text-4xl md:text-6xl text-white/90 drop-shadow-xl mt-4 block font-extrabold pb-2">
                최고의 디스코드 파트너.
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-200 mb-12 leading-relaxed max-w-2xl drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] font-medium">
              이터널리턴 전적부터 고품질 TTS, 완벽한 음악 재생 기능까지.<br />
              여러분의 커뮤니티 서버를 한 단계 더 업그레이드 하세요!
            </p>

            {/* Image Buttons with Text Overlay */}
            <div className="flex flex-col sm:flex-row items-center gap-6">
              <a
                href={getInviteUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="group relative transition-transform hover:scale-105 hover:-rotate-1 active:scale-95 inline-block"
              >
                <img src={BTN_START} alt="초대하기 바탕" className="h-[80px] w-auto drop-shadow-2xl opacity-90 group-hover:opacity-100 group-hover:drop-shadow-[0_0_30px_rgba(255,255,255,0.4)]" />
                <div className="absolute inset-0 flex items-center justify-center font-black text-xl text-white drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] tracking-wide pl-2">
                  봇 초대하기
                </div>
              </a>

              <button
                onClick={handleDashboard}
                className="group relative transition-transform hover:scale-105 hover:rotate-1 active:scale-95 inline-block"
              >
                <img src={BTN_GAME01} alt="대시보드 바탕" className="h-[75px] w-auto drop-shadow-lg opacity-90 group-hover:opacity-100" />
                <div className="absolute inset-0 flex items-center justify-center font-black text-lg text-white drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] tracking-wide">
                  대시보드 quản lý
                </div>
              </button>
            </div>
          </motion.div>

          {/* Hero Character */}
          <motion.div
            style={{ y: y2 }}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1.2, delay: 0.3, type: "spring", stiffness: 50 }}
            className="hidden xl:flex relative justify-center items-center h-[700px]"
          >
            <img
              src={HERO_MAIN}
              alt="Character"
              className="w-auto h-[120%] max-h-[900px] object-contain drop-shadow-[0_40px_80px_rgba(0,0,0,0.8)] animate-float z-10 absolute bottom-[-100px]"
            />
          </motion.div>
        </div>

        {/* 바닥 장식 */}
        <div className="absolute bottom-0 w-full h-32 bg-gradient-to-t from-discord-darker to-transparent z-40" />
      </section>

      {/* Features Section */}
      <section className="py-32 bg-discord-darker relative">
        <div className="max-w-7xl mx-auto px-6">
          <AnimatedSection className="mb-24 flex flex-col md:flex-row items-center justify-between gap-8 text-center md:text-left">
            <div>
              <div className="inline-block px-4 py-1.5 bg-debi-primary/15 border border-debi-primary/30 rounded-full text-debi-primary font-bold text-sm mb-6">
                ✨ 최고급 퀄리티
              </div>
              <h2 className="text-4xl md:text-5xl font-black text-white leading-tight">
                단 하나의 봇으로<br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#4ECDC4] to-[#fbc2eb]">모든 기능</span>을 한 번에!
              </h2>
            </div>
            
            <Link
              to="/commands"
              className="group relative transition-transform hover:scale-110 active:scale-95 inline-block"
            >
              <img src={BTN_GAME02} alt="커맨드 바탕" className="h-[60px] drop-shadow-xl relative z-10 opacity-90 group-hover:opacity-100" />
              <div className="absolute inset-0 z-20 flex items-center justify-center font-bold text-base text-white drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] tracking-wide">
                 커맨드 확인
              </div>
            </Link>
          </AnimatedSection>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <AnimatedSection key={index} delay={index * 0.1} className="h-full">
                <div className="h-full bg-gradient-to-b from-white/[0.04] to-black/20 rounded-[2.5rem] p-8 border border-white/[0.05] hover:border-white/20 hover:bg-white/[0.08] transition-all duration-300 relative overflow-hidden group">
                  
                  {/* Clean Icon */}
                  <div className={`w-16 h-16 rounded-2xl mb-8 flex items-center justify-center bg-gradient-to-br ${feature.color} bg-opacity-20 shadow-lg`}>
                    <feature.icon className="w-8 h-8 text-white drop-shadow-md" />
                  </div>

                  <h3 className="text-2xl font-bold text-white mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-discord-muted text-base leading-relaxed mb-8 flex-grow">
                    {feature.description}
                  </p>
                  
                  <div className="flex flex-wrap gap-2">
                    {feature.highlights.map((highlight, idx) => (
                      <span key={idx} className={`text-xs font-bold px-3 py-1.5 rounded-full bg-gradient-to-r ${feature.color} bg-opacity-10 border border-white/10 text-white shadow-sm`}>
                        {highlight}
                      </span>
                    ))}
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Greeting Preview Section */}
      <section className="py-32 relative overflow-hidden bg-discord-darkest">
        <div className="absolute inset-0 z-0">
          <img src={FEATURE_BG} alt="Feature Background" className="w-full h-full object-cover opacity-10 mix-blend-color-dodge grayscale" />
          <div className="absolute inset-0 bg-gradient-to-b from-discord-darker via-discord-darkest/90 to-discord-darker" />
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6">
          <AnimatedSection className="text-center mb-16 relative">
            <MessageSquare className="absolute -top-10 left-[10%] w-16 h-16 text-white/10 rotate-12" />
            <h2 className="text-4xl md:text-5xl font-black mb-6 text-white drop-shadow-lg z-10 relative">
              커스텀 <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF6B6B] to-[#FFE66D]">인사말 카드</span>
            </h2>
            <p className="text-discord-muted text-xl max-w-2xl mx-auto z-10 relative">
              새 멤버가 환영받는 특별한 순간을 만들어보세요.
            </p>
          </AnimatedSection>

          <AnimatedSection delay={0.2} className="relative max-w-4xl mx-auto">
            <div className="absolute -inset-10 bg-gradient-to-r from-pink-500/20 via-purple-500/20 to-blue-500/20 blur-[100px] rounded-full opacity-60 pointer-events-none" />
            <div className="relative bg-black/40 backdrop-blur-2xl border border-white/10 rounded-[3rem] p-8 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
              <GreetingPreview />
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-32 relative overflow-hidden bg-[#0a0a0c]">
        {/* 통계창 배경은 은은한 게임 배경으로 적용 */}
        <div className="absolute inset-0 z-0 flex items-center justify-center opacity-30 overflow-hidden">
           <img src={HERO_BIKE} className="w-full h-[150%] object-cover blur-[5px] mix-blend-luminosity" alt="Background Effect" />
           <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0c] via-transparent to-[#0a0a0c]" />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-16 text-center">
            {[
              { label: '누적 사용 유저', value: stats.users, icon: Users },
              { label: '활성화 서버', value: stats.servers, icon: Server },
              { label: '명령어 종류', value: stats.commands, icon: Terminal },
            ].map((stat, idx) => (
              <AnimatedSection key={idx} delay={idx * 0.2}>
                <div className="flex flex-col items-center group">
                  <div className="mb-6 w-20 h-20 rounded-full flex items-center justify-center bg-white/5 border border-white/10 group-hover:bg-white/10 transition-colors">
                    <stat.icon className="w-10 h-10 text-white opacity-80 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <motion.span
                    className="text-5xl md:text-7xl font-black text-white mb-4 block drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]"
                    initial={{ opacity: 0, scale: 0.5 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ type: "spring", stiffness: 100, delay: idx * 0.1 }}
                  >
                    {stat.value.toLocaleString()}
                  </motion.span>
                  <span className="text-xl text-gray-400 font-bold tracking-widest uppercase">
                    {stat.label}
                  </span>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Donation Section with Image Buttons */}
      <section className="py-32 bg-discord-darkest relative overflow-hidden border-t border-white/5">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-pink-500/10 blur-[150px] rounded-full pointer-events-none" />

        <div className="max-w-5xl mx-auto px-6 relative z-10">
          <AnimatedSection delay={0.2}>
            <div className="bg-gradient-to-br from-[#1a1c23] to-[#121318] rounded-[3rem] p-10 md:p-16 border border-white/[0.08] shadow-[0_30px_60px_rgba(0,0,0,0.6)] relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-r from-pink-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />

              <div className="flex flex-col md:flex-row items-center justify-between gap-12 relative z-10">
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-3xl md:text-5xl font-black text-white mb-6 leading-tight">
                    봇이 마음에 드셨나요?<br />
                    <span className="text-pink-400 font-extrabold">힘을 보태주세요!</span>
                  </h3>
                  <p className="text-gray-300 text-lg leading-relaxed mb-8 font-medium">
                    서버 유지비와 새로운 기능 추가를 위해 후원을 받습니다.<br className="hidden md:block"/>
                    ☕ 커피 한 잔의 정성이라도 매우 큰 힘이 됩니다.
                  </p>
                </div>

                <div className="flex flex-col items-center gap-6">
                  <button
                    onClick={() => setIsDonationModalOpen(true)}
                    className="group relative transition-transform hover:scale-110 active:scale-95 inline-block"
                  >
                    <img src={BTN_GAME03} alt="후원 바탕" className="h-[75px] drop-shadow-[0_10px_20px_rgba(255,105,180,0.4)] relative z-10 opacity-90 group-hover:opacity-100" />
                    <div className="absolute inset-0 z-20 flex items-center justify-center font-black text-xl text-white drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] tracking-wide pr-2">
                       후원하기
                    </div>
                  </button>
                  <p className="text-sm font-bold text-discord-muted bg-black/40 px-4 py-2 rounded-full border border-white/5">
                    * 자율 후원 시스템
                  </p>
                </div>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Footer (간단하게 유지) */}
      <footer className="pt-20 pb-12 bg-black border-t border-white/10 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
               <img src={LOGO_WHITE} alt="Logo" className="h-10 opacity-80" />
               <span className="font-black text-xl text-white">Debi & Marlene</span>
            </div>
            
            <div className="flex gap-8 font-medium text-sm">
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
