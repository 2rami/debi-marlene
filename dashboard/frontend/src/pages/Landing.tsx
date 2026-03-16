import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useEffect, useState } from 'react'
import Header from '../components/common/Header'
import { api } from '../services/api'
import { motion, useScroll, useTransform } from 'framer-motion'
import {
  Bot,
  Gamepad2,
  Bell,
  Music,
  ChevronRight,
  Star,
  Check,
  ArrowRight
} from 'lucide-react'
import AnimatedSection from '../components/common/AnimatedSection'
import GreetingPreview from '../components/landing/GreetingPreview'
import DonationModal from '../components/common/DonationModal'

// Images
import HERO_SKY from '../assets/images/hero-sky.jpg'
import HERO_MAIN from '../assets/images/hero-main.png'
import HERO_BIKE from '../assets/images/hero-bike.jpg'
import FEATURE_BG from '../assets/images/feature-bg.jpg'

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
  const y1 = useTransform(scrollY, [0, 500], [0, 150])
  const y2 = useTransform(scrollY, [0, 500], [0, -50])

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
      title: 'TTS (음성 읽기)',
      description: '텍스트 채널의 메시지를 음성 채널에서 읽어줍니다. 데비와 마를렌 두 가지 음성을 지원합니다.',
      highlights: ['커스텀 TTS 음성', '채널별 설정', '후원 전용 기능'],
      icon: <Bot className="w-8 h-8" />,
      color: "from-blue-500/20 to-cyan-500/20 text-cyan-400"
    },
    {
      title: '이터널리턴 전적',
      description: '이터널리턴 플레이어의 전적, 캐릭터별 통계, 티어별 추천 캐릭터를 검색할 수 있습니다.',
      highlights: ['전적 검색', '캐릭터 통계', '추천 캐릭터'],
      icon: <Gamepad2 className="w-8 h-8" />,
      color: "from-purple-500/20 to-pink-500/20 text-pink-400"
    },
    {
      title: '유튜브 알림',
      description: '특정 유튜브 채널의 새 영상 업로드를 서버 채널이나 DM으로 알려줍니다.',
      highlights: ['서버 알림', 'DM 알림', '자동 알림'],
      icon: <Bell className="w-8 h-8" />,
      color: "from-red-500/20 to-orange-500/20 text-orange-400"
    },
    {
      title: '음악 재생',
      description: '유튜브에서 음악을 검색하고 음성 채널에서 재생합니다. 대기열 관리를 지원합니다.',
      highlights: ['YouTube 검색', '대기열 관리', '스킵/정지'],
      icon: <Music className="w-8 h-8" />,
      color: "from-emerald-500/20 to-green-500/20 text-emerald-400"
    },
  ]

  return (
    <div className="min-h-screen bg-discord-darkest overflow-x-hidden selection:bg-debi-primary/30 selection:text-white">
      <Header />

      <DonationModal
        isOpen={isDonationModalOpen}
        onClose={() => setIsDonationModalOpen(false)}
      />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-20 overflow-hidden">
        {/* Parallax Background */}
        <motion.div
          style={{ y: y1 }}
          className="absolute inset-0 z-0"
        >
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-discord-darkest/60 to-discord-darkest z-10" />
          <img src={HERO_SKY} alt="Sky Background" className="w-full h-full object-cover object-top" />
        </motion.div>

        {/* Content Container */}
        <div className="relative z-10 w-full max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="text-left"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur border border-white/20 mb-6">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-sm font-medium text-white/90">현재 {stats.servers.toLocaleString()}개 서버에서 활동 중</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-black mb-6 leading-tight text-white drop-shadow-2xl">
              함께하는 즐거움<br />
              <span className="gradient-text drop-shadow-none">Debi & Marlene</span>
            </h1>

            <p className="text-lg md:text-xl text-gray-200 mb-10 leading-relaxed max-w-lg shadow-black drop-shadow-md">
              이터널리턴 전적부터 고품질 TTS, 음악 재생까지.<br />
              여러분의 디스코드 서버를 더욱 활기차게 만들어보세요.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-4">
              <a
                href={getInviteUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="group relative px-8 py-4 rounded-xl bg-white text-discord-darkest font-bold text-lg shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:shadow-[0_0_30px_rgba(255,255,255,0.5)] transition-all overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-2">
                  <Bot className="w-6 h-6" />
                  봇 초대하기
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-debi-primary to-marlene-primary opacity-0 group-hover:opacity-10 transition-opacity" />
              </a>

              <button
                onClick={handleDashboard}
                className="px-8 py-4 rounded-xl bg-black/40 hover:bg-black/60 backdrop-blur border border-white/10 text-white font-semibold text-lg transition-all flex items-center gap-2 group"
              >
                대시보드
                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </motion.div>

          <motion.div
            style={{ y: y2 }}
            initial={{ opacity: 0, scale: 0.8, rotate: -5 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
            className="hidden lg:block relative"
          >
            <img
              src={HERO_MAIN}
              alt="Debi & Marlene"
              className="w-full h-auto drop-shadow-[0_20px_50px_rgba(0,0,0,0.5)] animate-float"
            />
          </motion.div>
        </div>
      </section>

      {/* Greeting Preview Section */}
      <section className="py-24 relative overflow-hidden bg-discord-dark">
        <div className="absolute inset-0 bg-cover bg-center opacity-5" style={{ backgroundImage: `url(${FEATURE_BG})` }} />
        <div className="relative max-w-7xl mx-auto px-6">
          <AnimatedSection className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              <span className="gradient-text">나만의 인사말 카드</span>
            </h2>
            <p className="text-discord-muted text-lg max-w-2xl mx-auto">
              서버에 새로운 멤버가 들어왔을 때, 데비와 마를렌이 특별한 인사말로 환영해줍니다.
              지금 바로 미리 만들어보세요!
            </p>
          </AnimatedSection>

          <AnimatedSection delay={0.2}>
            <GreetingPreview />
          </AnimatedSection>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 bg-discord-darker relative">
        <div className="max-w-7xl mx-auto px-6">
          <AnimatedSection className="mb-20">
            <h2 className="text-3xl md:text-5xl font-bold text-center mb-6 text-white">
              더 강력해진 <span className="text-debi-primary">주요 기능</span>
            </h2>
          </AnimatedSection>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <AnimatedSection key={index} delay={index * 0.1} className="h-full">
                <div className="h-full bg-discord-dark rounded-2xl p-8 border border-discord-light/10 hover:border-discord-light/30 transition-colors group hover:-translate-y-2 duration-300">
                  <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-discord-muted text-sm leading-relaxed mb-4">
                    {feature.description}
                  </p>
                  <div className="flex flex-wrap gap-2 mt-auto">
                    {feature.highlights.map((highlight, idx) => (
                      <span key={idx} className="text-xs font-medium px-2 py-1 rounded bg-discord-light/10 text-discord-muted">
                        {highlight}
                      </span>
                    ))}
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>

          <div className="mt-20 text-center">
            <Link
              to="/commands"
              className="inline-flex items-center gap-2 text-white/80 hover:text-white hover:gap-4 transition-all"
            >
              모든 커맨드 기능 살펴보기
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section with Image */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0">
          <img src={HERO_BIKE} alt="Bike Background" className="w-full h-full object-cover opacity-20" />
          <div className="absolute inset-0 bg-gradient-to-t from-discord-darkest via-discord-darkest/80 to-transparent" />
        </div>

        <div className="relative max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
            {[
              { label: 'Total Users', value: stats.users, icon: <Star className="w-6 h-6" /> },
              { label: 'Active Servers', value: stats.servers, icon: <Bot className="w-6 h-6" /> },
              { label: 'Commands Used', value: stats.commands, icon: <Gamepad2 className="w-6 h-6" /> },
            ].map((stat, idx) => (
              <AnimatedSection key={idx} delay={idx * 0.2}>
                <div className="flex flex-col items-center">
                  <div className="mb-4 p-3 rounded-full bg-white/5 backdrop-blur border border-white/10 text-debi-primary">
                    {stat.icon}
                  </div>
                  <motion.span
                    className="text-5xl md:text-6xl font-black text-white mb-2 block"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                  >
                    {stat.value.toLocaleString()}
                  </motion.span>
                  <span className="text-lg text-discord-muted uppercase tracking-wider font-medium">
                    {stat.label}
                  </span>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* New Donation Section */}
      <section className="py-32 bg-discord-darkest relative overflow-hidden">
        {/* Background Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-debi-primary/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-4xl mx-auto px-6 relative z-10">
          <AnimatedSection className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              <span className="gradient-text">함께 만들어가는 데비&마를렌</span>
            </h2>
            <p className="text-discord-muted text-lg max-w-2xl mx-auto">
              여러분의 소중한 후원은 안정적인 서버 운영과 더 나은 기능을 개발하는 데 큰 힘이 됩니다.
              작은 정성이라도 감사히 받겠습니다! 🙇‍♂️
            </p>
          </AnimatedSection>

          <AnimatedSection delay={0.2}>
            <div className="bg-gradient-to-br from-discord-dark to-discord-darker rounded-[40px] p-8 md:p-12 border border-white/5 shadow-2xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-r from-debi-primary/5 to-marlene-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              <div className="flex flex-col md:flex-row items-center justify-between gap-10 relative z-10">
                <div className="flex-1 text-center md:text-left">
                  <div className="inline-block px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-debi-primary text-sm font-semibold mb-6">
                    ☕ 개발자에게 커피 한 잔
                  </div>
                  <h3 className="text-3xl font-bold text-white mb-4">
                    따뜻한 마음을 전해주세요
                  </h3>
                  <p className="text-gray-400 leading-relaxed mb-8">
                    후원해주신 금액은 서버 운영비와 개발에 소중하게 사용됩니다.<br className="hidden md:block" />
                    여러분의 응원이 큰 힘이 돼요!
                  </p>

                  <div className="flex flex-wrap gap-4 justify-center md:justify-start">
                    {['서버 운영 비용', '새로운 기능 개발', '쾌적한 서비스 유지'].map((tag, idx) => (
                      <span key={idx} className="flex items-center gap-2 text-sm text-gray-500 bg-black/20 px-3 py-2 rounded-lg">
                        <Check className="w-3 h-3 text-debi-primary" />
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="w-full md:w-auto flex flex-col items-center gap-4">
                  <button
                    onClick={() => setIsDonationModalOpen(true)}
                    className="w-full md:w-auto px-12 py-5 rounded-2xl bg-gradient-to-r from-debi-primary to-marlene-primary text-white text-xl font-bold shadow-lg shadow-debi-primary/25 hover:shadow-debi-primary/40 hover:scale-105 active:scale-95 transition-all duration-300"
                  >
                    후원하기
                  </button>
                  <p className="text-xs text-discord-muted">
                    * 언제든지 취소할 수 있는 자율 후원입니다
                  </p>
                </div>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-black/20 border-t border-white/5 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl overflow-hidden shadow-lg object-cover">
                  <img src={FEATURE_BG} alt="Debi & Marlene Logo" className="w-full h-full object-cover" />
                </div>
                <span className="font-bold text-xl text-white">Debi & Marlene</span>
              </div>
              <p className="text-discord-muted text-sm leading-relaxed max-w-sm">
                이터널리턴 전적 검색, 고품질 TTS, 음악 재생까지.<br />
                디스코드 서버 운영을 위한 최고의 파트너입니다.
              </p>
            </div>

            <div>
              <h4 className="font-bold text-white mb-6">바로가기</h4>
              <ul className="space-y-3 text-sm">
                <li><Link to="/commands" className="text-discord-muted hover:text-debi-primary transition-colors">전체 명령어</Link></li>
                <li><Link to="/docs" className="text-discord-muted hover:text-debi-primary transition-colors">사용 가이드</Link></li>
                <li><a href={getInviteUrl()} target="_blank" rel="noopener noreferrer" className="text-discord-muted hover:text-debi-primary transition-colors">봇 초대하기</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-6">지원 및 법적고지</h4>
              <ul className="space-y-3 text-sm">
                <li><a href="https://discord.gg/aDemda3qC9" className="text-discord-muted hover:text-debi-primary transition-colors">공식 서포트 서버</a></li>
                <li><Link to="/terms" className="text-discord-muted hover:text-debi-primary transition-colors">이용약관 / 개인정보처리방침</Link></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-white/5 text-center text-discord-muted text-sm font-medium">
            <p>&copy; {new Date().getFullYear()} Debi & Marlene. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
