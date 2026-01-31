import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import { useAuth } from '../contexts/AuthContext'

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams()
  const { refreshUser } = useAuth()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const confirmPayment = async () => {
      const paymentKey = searchParams.get('paymentKey')
      const orderId = searchParams.get('orderId')
      const amount = searchParams.get('amount')

      if (!paymentKey || !orderId || !amount) {
        setError('결제 정보가 올바르지 않습니다.')
        setLoading(false)
        return
      }

      try {
        await api.post('/premium/confirm', {
          paymentKey,
          orderId,
          amount: parseInt(amount),
        })
        await refreshUser()
      } catch (err) {
        setError('결제 확인에 실패했습니다.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    confirmPayment()
  }, [searchParams, refreshUser])

  if (loading) {
    return (
      <div className="min-h-screen bg-discord-darkest flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 rounded-full border-4 border-discord-dark" />
            <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-debi-primary animate-spin" />
          </div>
          <p className="text-discord-muted">결제를 확인하고 있습니다...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-discord-darkest flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-discord-dark rounded-2xl p-8 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-discord-red/20 flex items-center justify-center">
            <svg className="w-8 h-8 text-discord-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-discord-text mb-2">결제 오류</h1>
          <p className="text-discord-muted mb-6">{error}</p>
          <Link
            to="/premium"
            className="inline-block px-6 py-3 bg-discord-light rounded-lg text-discord-text hover:bg-discord-muted/20 transition-colors"
          >
            다시 시도하기
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-discord-darkest flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-discord-dark rounded-2xl p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-discord-green/20 flex items-center justify-center">
          <svg className="w-8 h-8 text-discord-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-discord-text mb-2">결제 완료!</h1>
        <p className="text-discord-muted mb-6">
          프리미엄 구독이 활성화되었습니다.
          <br />
          이제 TTS 기능을 사용할 수 있습니다.
        </p>
        <Link
          to="/dashboard"
          className="inline-block btn-gradient px-6 py-3 rounded-lg text-white font-semibold"
        >
          대시보드로 이동
        </Link>
      </div>
    </div>
  )
}
