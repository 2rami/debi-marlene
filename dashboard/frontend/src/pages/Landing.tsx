import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useEffect, useState } from 'react'
import Header from '../components/common/Header'
import { api } from '../services/api'

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
      highlights: ['커스텀 TTS 음성', '채널별 설정', '프리미엄 기능'],
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      ),
    },
    {
      title: '이터널리턴 전적',
      description: '이터널리턴 플레이어의 전적, 캐릭터별 통계, 티어별 추천 캐릭터를 검색할 수 있습니다.',
      highlights: ['전적 검색', '캐릭터 통계', '추천 캐릭터'],
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      title: '유튜브 알림',
      description: '특정 유튜브 채널의 새 영상 업로드를 서버 채널이나 DM으로 알려줍니다.',
      highlights: ['서버 알림', 'DM 알림', '자동 알림'],
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      ),
    },
    {
      title: '음악 재생',
      description: '유튜브에서 음악을 검색하고 음성 채널에서 재생합니다. 대기열 관리를 지원합니다.',
      highlights: ['YouTube 검색', '대기열 관리', '스킵/정지'],
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      ),
    },
  ]

  const pricingPlans = [
    {
      name: '무료',
      price: '0',
      period: '',
      description: '기본 서버 관리 기능',
      features: ['이터널리턴 전적 검색', '유튜브 알림', '음악 재생', '피드백 보내기'],
      cta: '무료로 시작하기',
      highlighted: false,
    },
    {
      name: '프리미엄',
      price: '9,900',
      period: '/월',
      description: 'TTS 기능 포함',
      features: ['무료 기능 전부', 'TTS (음성 읽기)', '우선 지원', '프리미엄 배지'],
      cta: '프리미엄 시작하기',
      highlighted: true,
    },
    {
      name: '연간 프리미엄',
      price: '99,000',
      period: '/년',
      description: '2개월 할인',
      features: ['프리미엄 기능 전부', '연간 결제 할인', '16% 할인 적용'],
      cta: '연간 구독하기',
      highlighted: false,
    },
  ]

  return (
    <div className="min-h-screen">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-discord-darkest via-discord-darker to-discord-darkest" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-debi-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-marlene-primary/10 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-6 py-20 md:py-28">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="gradient-text">Debi & Marlene</span>
            </h1>
            <p className="text-lg md:text-xl text-discord-muted max-w-2xl mx-auto mb-10">
              이터널리턴 전적 검색, 유튜브 알림, 음악 재생, TTS까지
              <br />
              다양한 기능을 제공하는 디스코드 봇
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <a
                href={getInviteUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-gradient inline-flex items-center gap-3 px-8 py-4 rounded-xl text-white font-semibold text-lg"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                봇 초대하기
              </a>
              <button
                onClick={handleDashboard}
                className="inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-discord-light/20 hover:bg-discord-light/30 text-discord-text font-semibold text-lg transition-colors"
              >
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                </svg>
                대시보드
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 max-w-lg mx-auto">
              <div className="text-center">
                <p className="text-3xl md:text-4xl font-bold text-discord-text">{stats.users.toLocaleString()}</p>
                <p className="text-discord-muted text-sm">Users</p>
              </div>
              <div className="text-center">
                <p className="text-3xl md:text-4xl font-bold text-discord-text">{stats.servers.toLocaleString()}</p>
                <p className="text-discord-muted text-sm">Servers</p>
              </div>
              <div className="text-center">
                <p className="text-3xl md:text-4xl font-bold text-discord-text">{stats.commands}</p>
                <p className="text-discord-muted text-sm">Commands</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-discord-darker">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            <span className="gradient-text">주요 기능</span>
          </h2>
          <p className="text-discord-muted text-center mb-12 max-w-2xl mx-auto">
            다양한 기능으로 디스코드 서버를 더 즐겁게
          </p>

          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="card-glow bg-discord-dark rounded-xl p-6 border border-discord-light/20"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-debi-primary/20 to-marlene-primary/20 flex items-center justify-center flex-shrink-0 text-debi-primary">
                    {feature.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-discord-text mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-discord-muted text-sm mb-4">
                      {feature.description}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {feature.highlights.map((highlight, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 text-xs rounded bg-discord-light/20 text-discord-muted"
                        >
                          {highlight}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-8">
            <Link
              to="/commands"
              className="inline-flex items-center gap-2 text-debi-primary hover:text-debi-light transition-colors"
            >
              모든 커맨드 보기
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-discord-darkest">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            <span className="gradient-text">요금제</span>
          </h2>
          <p className="text-discord-muted text-center mb-12 max-w-2xl mx-auto">
            TTS 기능을 사용하려면 프리미엄 구독이 필요합니다
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <div
                key={index}
                className={`relative rounded-2xl p-8 ${
                  plan.highlighted
                    ? 'bg-gradient-to-br from-debi-primary/20 to-marlene-primary/20 border-2 border-debi-primary/50'
                    : 'bg-discord-dark border border-discord-light/20'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-debi-primary to-marlene-primary rounded-full text-sm font-semibold">
                    인기
                  </div>
                )}

                <h3 className="text-xl font-semibold text-discord-text mb-2">
                  {plan.name}
                </h3>
                <p className="text-discord-muted text-sm mb-4">
                  {plan.description}
                </p>

                <div className="mb-6">
                  <span className="text-4xl font-bold text-discord-text">
                    {plan.price}
                  </span>
                  <span className="text-discord-muted">원{plan.period}</span>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-sm">
                      <svg className="w-5 h-5 text-discord-green flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-discord-text">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={handleDashboard}
                  className={`w-full py-3 rounded-lg font-semibold transition-all ${
                    plan.highlighted
                      ? 'btn-gradient text-white'
                      : 'bg-discord-light text-discord-text hover:bg-discord-muted/20'
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-discord-darker border-t border-discord-light/10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center">
                  <span className="text-white font-bold text-lg">D</span>
                </div>
                <span className="font-bold text-lg text-discord-text">Debi & Marlene</span>
              </div>
              <p className="text-discord-muted text-sm">
                이터널리턴 전적 검색, 유튜브 알림, 음악 재생, TTS를 제공하는 디스코드 봇
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-discord-text mb-4">Links</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/commands" className="text-discord-muted hover:text-discord-text transition-colors">Commands</Link></li>
                <li><Link to="/docs" className="text-discord-muted hover:text-discord-text transition-colors">Documentation</Link></li>
                <li><a href={getInviteUrl()} target="_blank" rel="noopener noreferrer" className="text-discord-muted hover:text-discord-text transition-colors">Invite Bot</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-discord-text mb-4">Community</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="https://discord.gg/your-server" className="text-discord-muted hover:text-discord-text transition-colors">Support Server</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-discord-text mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/terms" className="text-discord-muted hover:text-discord-text transition-colors">Terms of Service</Link></li>
                <li><Link to="/privacy" className="text-discord-muted hover:text-discord-text transition-colors">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-discord-light/10 text-center text-discord-muted text-sm">
            <p>Debi & Marlene - Made with love</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
