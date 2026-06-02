import { useEffect, useState } from 'react'
import { loadTossPayments } from '@tosspayments/tosspayments-sdk'
import { useAuth } from '../../contexts/AuthContext'
import { topupApi, TopupPackage } from '../../lib/topup'
import { trackEvent } from '../../lib/analytics'
import CreditIcon from './CreditIcon'

const CLIENT_KEY = import.meta.env.VITE_TOSS_CLIENT_KEY || ''

interface Props {
  isOpen: boolean
  onClose: () => void
}

/**
 * 크레딧 충전 모달 — Toss 결제창(SDK v2) 방식.
 *
 * 흐름: 패키지 선택 → checkout(orderId 발급, 서버가 금액 결정) → Toss 결제창 requestPayment
 *      → /payment/topup/success 리디렉션 → TopupSuccess 가 confirm.
 *
 * 결제위젯이 아닌 결제창 방식 — API 개별 연동 키(test_ck)로 동작하며 한국 표준 방식.
 * 금액은 서버가 결정하므로 결제창엔 표시용 value 만 전달한다.
 */
export default function CreditTopupModal({ isOpen, onClose }: Props) {
  const { user } = useAuth()
  const [packages, setPackages] = useState<TopupPackage[]>([])
  const [selected, setSelected] = useState<TopupPackage | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isOpen) return
    setError(null)
    setSelected(null)
    topupApi.packages().then(setPackages).catch(() => setPackages([]))
  }, [isOpen])

  const handlePay = async () => {
    if (!selected || busy || !user) return
    if (!CLIENT_KEY) {
      setError('결제 설정이 누락되었습니다. (VITE_TOSS_CLIENT_KEY)')
      return
    }
    setBusy(true)
    setError(null)
    try {
      // 서버가 orderId·금액을 결정 (클라이언트 금액 신뢰 안 함).
      const order = await topupApi.checkout(selected.id)
      trackEvent('credit_topup_checkout', { pkg: selected.id, krw: selected.krw })

      const tossPayments = await loadTossPayments(CLIENT_KEY)
      const payment = tossPayments.payment({ customerKey: `ckey_${user.id}` })
      await payment.requestPayment({
        method: 'CARD', // 카드 + 간편결제(카카오/네이버/토스페이)
        amount: { currency: 'KRW', value: order.amount },
        orderId: order.orderId,
        orderName: order.orderName,
        successUrl: window.location.origin + '/payment/topup/success',
        failUrl: window.location.origin + '/payment/topup/fail',
      })
      // requestPayment 는 결제창으로 이동 — 정상 흐름에선 이 아래로 안 옴
    } catch (e: unknown) {
      setError((e as Error)?.message ?? '결제 요청에 실패했습니다.')
      setBusy(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[1100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-[#1a1b1e] rounded-3xl border border-white/10 shadow-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <CreditIcon size={20} />
            크레딧 충전
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl leading-none">×</button>
        </div>

        {/* 패키지 선택 */}
        <div className="grid grid-cols-2 gap-2 mb-4">
          {packages.map(p => {
            const active = selected?.id === p.id
            return (
              <button
                key={p.id}
                onClick={() => setSelected(p)}
                className={`rounded-2xl px-3 py-3 text-left border transition
                  ${active
                    ? 'bg-[#326D1B] border-[#326D1B] text-[#E5FC8A]'
                    : 'bg-white/5 border-white/10 text-gray-200 hover:bg-white/10'}`}
              >
                <div className="flex items-center gap-1.5 text-base font-extrabold tabular-nums">
                  <CreditIcon size={16} />
                  {p.credits.toLocaleString()}
                  {p.bonus > 0 && (
                    <span className={`text-[10px] font-bold ${active ? 'text-[#E5FC8A]' : 'text-emerald-400'}`}>
                      +{p.bonus}%
                    </span>
                  )}
                </div>
                <div className={`text-xs mt-0.5 ${active ? 'text-[#E5FC8A]/80' : 'text-gray-400'}`}>
                  {p.krw.toLocaleString()}원
                </div>
              </button>
            )
          })}
        </div>

        {error && (
          <div className="mb-3 px-3 py-2 rounded-xl bg-red-500/15 border border-red-400/30 text-red-300 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handlePay}
          disabled={busy || !selected}
          className="w-full py-3 rounded-xl bg-[#326D1B] text-[#E5FC8A] font-bold disabled:bg-white/5 disabled:text-white/30"
        >
          {busy ? '결제창 여는 중…' : selected ? `${selected.krw.toLocaleString()}원 결제` : '패키지를 선택하세요'}
        </button>

        <p className="mt-3 text-[11px] text-gray-500 text-center leading-relaxed">
          카드 · 카카오페이 · 네이버페이 · 토스페이로 결제할 수 있어요.
        </p>
      </div>
    </div>
  )
}
