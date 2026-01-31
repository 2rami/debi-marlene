import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useEffect } from 'react'

export default function Landing() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading && user) {
      navigate('/dashboard')
    }
  }, [user, loading, navigate])

  const features = [
    {
      title: '서버 관리',
      description: '공지 채널, 환영 메시지, 자동응답 등 서버 설정을 웹에서 간편하게 관리하세요.',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
    },
    {
      title: '채팅 필터',
      description: '욕설, 스팸 등 원치 않는 메시지를 자동으로 필터링하고 관리하세요.',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
    },
    {
      title: '제재 관리',
      description: '경고, 뮤트, 킥, 밴 등 제재 기록을 체계적으로 관리하세요.',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
    },
    {
      title: '티켓 시스템',
      description: '사용자 문의를 티켓으로 관리하고 효율적으로 응대하세요.',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
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
      features: ['서버 설정 관리', '환영 메시지', '자동응답', '채팅 필터', '제재 관리', '티켓 시스템'],
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
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-discord-darkest via-discord-darker to-discord-darkest" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-debi-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-marlene-primary/10 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-6 py-24 md:py-32">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="gradient-text">Debi & Marlene</span>
              <br />
              <span className="text-discord-text">Dashboard</span>
            </h1>
            <p className="text-lg md:text-xl text-discord-muted max-w-2xl mx-auto mb-10">
              디스코드 서버를 웹에서 쉽게 관리하세요.
              <br />
              공지, 환영 메시지, 자동응답, 채팅 필터, 제재까지 한 곳에서.
            </p>

            <button
              onClick={login}
              className="btn-gradient inline-flex items-center gap-3 px-8 py-4 rounded-xl text-white font-semibold text-lg"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
              </svg>
              Discord로 로그인
            </button>
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
            무료로 제공되는 강력한 서버 관리 기능들
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="card-glow bg-discord-dark rounded-xl p-6 border border-discord-light/20"
              >
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-debi-primary/20 to-marlene-primary/20 flex items-center justify-center mb-4 text-debi-primary">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-discord-text mb-2">
                  {feature.title}
                </h3>
                <p className="text-discord-muted text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
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
                  onClick={login}
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
      <footer className="py-8 bg-discord-darker border-t border-discord-light/10">
        <div className="max-w-7xl mx-auto px-6 text-center text-discord-muted text-sm">
          <p>Debi & Marlene Dashboard</p>
        </div>
      </footer>
    </div>
  )
}
