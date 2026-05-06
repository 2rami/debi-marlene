import { useState } from 'react'
import { creditsApi } from '../../lib/credits'
import { trackEvent } from '../../lib/analytics'
import CreditIcon from './CreditIcon'

interface Props {
  disabled?: boolean
  onSuccess?: () => void
}

/**
 * 일일 출석체크 버튼. 성공 시 +N 토스트 + GA 이벤트 발사.
 * GA 이벤트는 200 응답 후에만 (낙관적 발사 X — 통계 오염 방지).
 */
export default function CheckInButton({ disabled = false, onSuccess }: Props) {
  const [busy, setBusy] = useState(false)
  const [flash, setFlash] = useState<{ gained: number; streak: number } | null>(null)

  const handleClick = async () => {
    if (disabled || busy) return
    setBusy(true)
    try {
      const r = await creditsApi.checkIn()
      if (r.ok && !r.already && r.gained > 0) {
        trackEvent('credit_check_in', { gained: r.gained, streak: r.streak })
        setFlash({ gained: r.gained, streak: r.streak })
        setTimeout(() => setFlash(null), 2500)
      }
      onSuccess?.()
    } catch {
      // 무음 실패 — 사용자에게 거슬리지 않게.
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="relative">
      <button
        onClick={handleClick}
        disabled={disabled || busy}
        className={`px-3 py-1.5 rounded-full text-xs font-bold border transition-colors flex items-center gap-1.5
          ${disabled
            ? 'bg-white/3 text-white/30 border-white/5 cursor-not-allowed'
            : 'bg-amber-400 text-black border-amber-300 hover:bg-amber-300'}`}
        title={disabled ? '오늘 출석 완료' : '오늘 출석체크 +10'}
      >
        <CreditIcon size={14} />
        {disabled ? '출석 완료' : '출석체크'}
      </button>

      {flash && (
        <div className="absolute right-0 top-[calc(100%+6px)] z-30 px-3 py-2 rounded-xl bg-black/90 border border-amber-300/40 text-amber-200 text-xs whitespace-nowrap shadow-lg animate-in fade-in slide-in-from-top-1">
          +{flash.gained} 크레딧 · 연속 {flash.streak}일
        </div>
      )}
    </div>
  )
}
