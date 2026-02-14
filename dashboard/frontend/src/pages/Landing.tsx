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

  const pricingPlans = [
    {
      name: '무료',
      price: '0',
      period: '',
      description: '모든 기본 기능 무료',
      features: ['이터널리턴 전적 검색', '유튜브 알림', '음악 재생', '서버 관리'],
      cta: '무료로 시작하기',
      highlighted: false,
    },
    {
      name: '후원',
      price: '자유',
      period: '',
      description: '개발자 응원하기',
      features: ['원하는 금액으로 후원', '서버 운영비 지원', '기능 개발 응원'],
      cta: '후원하기',
      highlighted: true,
    },
  ]

  return (
    <div className="min-h-screen bg-discord-darkest overflow-x-hidden selection:bg-debi-primary/30 selection:text-white">
      <Header />

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

      {/* Pricing Section (Renamed to Donation) */}
      <section className="py-32 bg-discord-darkest">
        <div className="max-w-7xl mx-auto px-6">
          <AnimatedSection className="text-center mb-20">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              <span className="gradient-text">개발자 후원</span>
            </h2>
            <p className="text-discord-muted text-lg">
              데비&마를렌의 지속적인 개발을 위해 후원해주세요
            </p>
          </AnimatedSection>

          <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto px-4">
            {pricingPlans.map((plan, index) => (
              <AnimatedSection key={index} delay={index * 0.1}>
                <div
                  className={`relative rounded-3xl p-8 h-full flex flex-col ${plan.highlighted
                    ? 'bg-gradient-to-b from-discord-dark to-discord-darker border-2 border-debi-primary/50 shadow-[0_0_50px_rgba(var(--debi-primary),0.1)]'
                    : 'bg-discord-dark border border-discord-light/10 hover:border-discord-light/30 transition-colors'
                    }`}
                >
                  {plan.highlighted && (
                    <div className="absolute -top-5 left-1/2 -translate-x-1/2 px-6 py-2 bg-gradient-to-r from-debi-primary to-marlene-primary rounded-full text-sm font-bold text-white shadow-lg">
                      BEST CHOICE
                    </div>
                  )}

                  <h3 className="text-2xl font-bold text-white mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-discord-muted text-sm mb-6 pb-6 border-b border-white/5">
                    {plan.description}
                  </p>

                  <div className="mb-8">
                    <span className="text-5xl font-black text-white">
                      {plan.price}
                    </span>
                    {plan.price !== '자유' && (
                      <span className="text-discord-muted text-lg font-medium ml-1">원{plan.period}</span>
                    )}
                  </div>

                  <ul className="space-y-4 mb-10 flex-1">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-3 text-sm group">
                        <div className={`p-1 rounded-full ${plan.highlighted ? 'bg-debi-primary/20 text-debi-primary' : 'bg-gray-800 text-gray-400'} mt-0.5`}>
                          <Check className="w-3 h-3" />
                        </div>
                        <span className="text-gray-300 group-hover:text-white transition-colors">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    onClick={handleDashboard}
                    className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${plan.highlighted
                      ? 'btn-gradient text-white hover:opacity-90 shadow-lg hover:shadow-debi-primary/25'
                      : 'bg-white/5 text-white hover:bg-white/10'
                      }`}
                  >
                    {plan.cta}
                  </button>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-black/20 border-t border-white/5 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center text-white font-bold">
                  DM
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
                <li><Link to="/terms" className="text-discord-muted hover:text-debi-primary transition-colors">이용약관</Link></li>
                <li><Link to="/privacy" className="text-discord-muted hover:text-debi-primary transition-colors">개인정보처리방침</Link></li>
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
