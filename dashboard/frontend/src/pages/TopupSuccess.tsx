import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { topupApi } from '../lib/topup'
import CreditIcon from '../components/credits/CreditIcon'

/**
 * 크레딧 충전 결제 성공 콜백 (/payment/topup/success).
 *
 * Toss 결제창 → successUrl 리디렉션. searchParams 의 paymentKey/orderId 만 확인하고
 * 서버 confirm 을 호출한다. 금액은 서버가 orderId 로 결정하므로 amount 는 보내지 않는다.
 */
export default function TopupSuccess() {
  const [searchParams] = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [credits, setCredits] = useState<number | null>(null)
  const [balance, setBalance] = useState<number | null>(null)

  useEffect(() => {
    const run = async () => {
      const paymentKey = searchParams.get('paymentKey')
      const orderId = searchParams.get('orderId')
      if (!paymentKey || !orderId) {
        setError('결제 정보가 올바르지 않습니다.')
        setLoading(false)
        return
      }
      try {
        const r = await topupApi.confirm(paymentKey, orderId)
        if (r.success) {
          setCredits(r.credits ?? null)
          setBalance(r.balance ?? null)
        } else {
          setError('결제 확인에 실패했습니다.')
        }
      } catch {
        setError('결제 확인에 실패했습니다. 잠시 후 잔고를 확인해 주세요.')
      } finally {
        setLoading(false)
      }
    }
    void run()
  }, [searchParams])

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
            to="/"
            className="inline-block px-6 py-3 bg-discord-light rounded-lg text-discord-text hover:bg-discord-muted/20 transition-colors"
          >
            홈으로
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-discord-darkest flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-discord-dark rounded-2xl p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-discord-green/20 flex items-center justify-center">
          <CreditIcon size={32} />
        </div>
        <h1 className="text-2xl font-bold text-discord-text mb-2">충전 완료!</h1>
        <p className="text-discord-muted mb-6">
          {credits != null ? (
            <>
              <span className="text-discord-text font-bold tabular-nums">{credits.toLocaleString()}</span> 크레딧이 충전되었습니다.
              {balance != null && (
                <>
                  <br />현재 잔고 <span className="text-discord-text font-bold tabular-nums">{balance.toLocaleString()}</span>
                </>
              )}
            </>
          ) : (
            '크레딧이 충전되었습니다.'
          )}
        </p>
        <Link
          to="/"
          className="inline-block btn-gradient px-6 py-3 rounded-lg text-white font-semibold"
        >
          홈으로
        </Link>
      </div>
    </div>
  )
}
