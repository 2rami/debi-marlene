import { Link, useSearchParams } from 'react-router-dom'

/**
 * 크레딧 충전 결제 실패 콜백 (/payment/topup/fail).
 * Toss 결제 실패/취소 시 failUrl 로 리디렉션. code/message 쿼리로 사유 표시.
 */
export default function TopupFail() {
  const [searchParams] = useSearchParams()
  const code = searchParams.get('code')
  const message = searchParams.get('message')

  return (
    <div className="min-h-screen bg-discord-darkest flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-discord-dark rounded-2xl p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-discord-red/20 flex items-center justify-center">
          <svg className="w-8 h-8 text-discord-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-discord-text mb-2">결제 실패</h1>
        <p className="text-discord-muted mb-2">
          {message || '결제가 완료되지 않았습니다.'}
        </p>
        {code && <p className="text-discord-muted/60 text-xs mb-6">오류 코드: {code}</p>}
        <div className="flex gap-2 justify-center">
          <Link
            to="/"
            className="inline-block px-6 py-3 bg-discord-light rounded-lg text-discord-text hover:bg-discord-muted/20 transition-colors"
          >
            홈으로
          </Link>
          <Link
            to="/dashboard"
            className="inline-block btn-gradient px-6 py-3 rounded-lg text-white font-semibold"
          >
            대시보드
          </Link>
        </div>
      </div>
    </div>
  )
}
