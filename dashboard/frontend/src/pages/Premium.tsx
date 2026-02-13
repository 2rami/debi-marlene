import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import Sidebar from '../components/common/Sidebar'

export default function Premium() {
  const { user } = useAuth()
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'yearly' | null>(null)
  const [loading, setLoading] = useState(false)

  const plans = [
    {
      id: 'monthly' as const,
      name: '월간 후원',
      price: 9900,
      period: '월',
      description: '매월 자동 후원',
      features: ['TTS (음성 읽기) 기능', '우선 지원', '후원자 배지'],
    },
    {
      id: 'yearly' as const,
      name: '연간 후원',
      price: 99000,
      period: '년',
      description: '16% 할인 적용',
      features: ['TTS (음성 읽기) 기능', '우선 지원', '후원자 배지', '2개월 무료'],
      badge: '인기',
    },
  ]

  const handleSubscribe = async (planId: 'monthly' | 'yearly') => {
    setSelectedPlan(planId)
    setLoading(true)

    try {
      // TODO: Implement Toss Payments checkout
      console.log('Starting payment for plan:', planId)
    } catch (error) {
      console.error('Payment error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold mb-4">
              <span className="gradient-text">프리미엄 후원</span>으로 업그레이드
            </h1>
            <p className="text-discord-muted">
              TTS 기능으로 채팅을 음성으로 들어보세요
            </p>
          </div>

          {/* Current Status */}
          {user?.premium.isActive && (
            <div className="mb-8 p-6 rounded-xl bg-gradient-to-r from-debi-primary/20 to-marlene-primary/20 border border-debi-primary/30">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-discord-text">
                    프리미엄 활성화됨
                  </h2>
                  <p className="text-discord-muted">
                    {user.premium.plan === 'monthly' ? '월간' : '연간'} 후원 중
                    {user.premium.expiresAt && (
                      <> · 만료: {new Date(user.premium.expiresAt).toLocaleDateString('ko-KR')}</>
                    )}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Pricing Cards */}
          {!user?.premium.isActive && (
            <div className="grid md:grid-cols-2 gap-6">
              {plans.map(plan => (
                <div
                  key={plan.id}
                  className={`relative rounded-2xl p-8 transition-all ${plan.badge
                      ? 'bg-gradient-to-br from-debi-primary/20 to-marlene-primary/20 border-2 border-debi-primary/50'
                      : 'bg-discord-dark border border-discord-light/20 hover:border-discord-light/40'
                    }`}
                >
                  {plan.badge && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-debi-primary to-marlene-primary rounded-full text-xs font-semibold text-white">
                      {plan.badge}
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
                      {plan.price.toLocaleString()}
                    </span>
                    <span className="text-discord-muted">원/{plan.period}</span>
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
                    onClick={() => handleSubscribe(plan.id)}
                    disabled={loading && selectedPlan === plan.id}
                    className={`w-full py-3 rounded-lg font-semibold transition-all disabled:opacity-50 ${plan.badge
                        ? 'btn-gradient text-white'
                        : 'bg-discord-light text-discord-text hover:bg-discord-muted/20'
                      }`}
                  >
                    {loading && selectedPlan === plan.id ? '처리 중...' : '후원하기'}
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Features Comparison */}
          <div className="mt-12">
            <h2 className="text-xl font-semibold text-discord-text mb-6 text-center">
              기능 비교
            </h2>

            <div className="bg-discord-dark rounded-xl border border-discord-light/20 overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-discord-light/20">
                    <th className="text-left p-4 text-discord-muted font-normal">기능</th>
                    <th className="text-center p-4 text-discord-muted font-normal">무료</th>
                    <th className="text-center p-4 text-discord-muted font-normal">프리미엄</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { feature: '서버 설정 관리', free: true, premium: true },
                    { feature: '환영 메시지', free: true, premium: true },
                    { feature: '자동응답', free: true, premium: true },
                    { feature: '채팅 필터', free: true, premium: true },
                    { feature: '제재 관리', free: true, premium: true },
                    { feature: '티켓 시스템', free: true, premium: true },
                    { feature: 'TTS (음성 읽기)', free: false, premium: true },
                    { feature: '우선 지원', free: false, premium: true },
                  ].map((row, idx) => (
                    <tr key={idx} className="border-b border-discord-light/10 last:border-0">
                      <td className="p-4 text-discord-text">{row.feature}</td>
                      <td className="p-4 text-center">
                        {row.free ? (
                          <svg className="w-5 h-5 text-discord-green mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-discord-muted mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                      </td>
                      <td className="p-4 text-center">
                        {row.premium ? (
                          <svg className="w-5 h-5 text-discord-green mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-discord-muted mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
