import { Link, useSearchParams } from 'react-router-dom'

export default function PaymentFail() {
  const [searchParams] = useSearchParams()
  const errorCode = searchParams.get('code')
  const errorMessage = searchParams.get('message')

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
          {errorMessage || '결제 처리 중 오류가 발생했습니다.'}
        </p>
        {errorCode && (
          <p className="text-discord-muted text-sm mb-6">
            오류 코드: {errorCode}
          </p>
        )}
        <div className="flex gap-3 justify-center">
          <Link
            to="/premium"
            className="px-6 py-3 btn-gradient rounded-lg text-white font-semibold"
          >
            다시 시도하기
          </Link>
          <Link
            to="/dashboard"
            className="px-6 py-3 bg-discord-light rounded-lg text-discord-text hover:bg-discord-muted/20 transition-colors"
          >
            대시보드로
          </Link>
        </div>
      </div>
    </div>
  )
}
