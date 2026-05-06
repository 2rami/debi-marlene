import { useEffect, useState, useCallback } from 'react'
import { creditsApi, MyCreditsResponse } from '../../lib/credits'
import CreditIcon from './CreditIcon'
import CheckInButton from './CheckInButton'
import { useAuth } from '../../contexts/AuthContext'

interface Props {
  compact?: boolean   // 헤더용 (잔고 + 출석 버튼만)
  className?: string
}

/**
 * 크레딧 지갑 — 헤더/사이드바 잔고 + streak + 출석 버튼.
 * 로그인 상태에서만 fetch. 로그아웃이면 null.
 */
export default function CreditWallet({ compact = true, className = '' }: Props) {
  const { user } = useAuth()
  const [data, setData] = useState<MyCreditsResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    if (!user) return
    setLoading(true)
    try {
      const r = await creditsApi.me()
      setData(r)
    } catch {
      // 백엔드 없거나 미배포여도 컴포넌트는 깨지지 않게.
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    void refresh()
  }, [refresh])

  if (!user) return null

  const balance = data?.balance ?? 0
  const streak = data?.streak_days ?? 0
  const checked = data?.checked_in_today ?? false

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-white"
        title={loading ? '불러오는 중' : `잔고 ${balance} · 연속 ${streak}일`}
      >
        <CreditIcon size={16} />
        <span className="text-sm font-semibold tabular-nums">{balance.toLocaleString()}</span>
        {!compact && streak > 0 && (
          <span className="ml-1 text-xs text-amber-300/90">{streak}일 연속</span>
        )}
      </div>
      <CheckInButton
        disabled={checked}
        onSuccess={refresh}
      />
    </div>
  )
}
