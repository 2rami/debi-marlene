import { useEffect, useState } from 'react'
import { creditsApi, GuildBalance } from '../../lib/credits'
import { trackEvent } from '../../lib/analytics'
import { api } from '../../services/api'
import CreditIcon from './CreditIcon'

interface ServerLite { id: string; name: string; icon: string | null; hasBot: boolean }

interface Props {
  isOpen: boolean
  onClose: () => void
  onDone?: () => void   // 잔고 갱신 콜백 (CreditWallet refresh 등)
}

/**
 * 크레딧 → 서버 공동 지갑 이체 모달.
 * 일반 후원(현금)은 별도 DonationModal.tsx (Toss/Kakao). 헷갈리지 않게 CreditDonateModal.
 */
export default function CreditDonateModal({ isOpen, onClose, onDone }: Props) {
  const [guilds, setGuilds] = useState<GuildBalance[]>([])
  const [serverNames, setServerNames] = useState<Record<string, string>>({})
  const [selected, setSelected] = useState<string>('')
  const [amount, setAmount] = useState<number>(10)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<{ donated: number; guild_balance: number } | null>(null)
  const [myBalance, setMyBalance] = useState<number>(0)

  useEffect(() => {
    if (!isOpen) return
    setError(null)
    setSuccess(null)
    void Promise.all([
      creditsApi.guilds().then(r => {
        setGuilds(r.guilds)
        if (r.guilds[0]) setSelected(r.guilds[0].guild_id)
      }).catch(() => setGuilds([])),
      creditsApi.me().then(r => setMyBalance(r.balance)).catch(() => setMyBalance(0)),
      api.get<{ servers: ServerLite[] }>('/servers')
        .then(r => {
          const map: Record<string, string> = {}
          r.data.servers.forEach(s => { map[s.id] = s.name })
          setServerNames(map)
        })
        .catch(() => setServerNames({})),
    ])
  }, [isOpen])

  const submit = async () => {
    if (!selected || amount <= 0 || busy) return
    setBusy(true)
    setError(null)
    try {
      const r = await creditsApi.donate(selected, amount)
      if (r.ok) {
        // 서버 200 + ok=true 인 경우에만 GA 발사
        trackEvent('credit_donate', { amount, guild_id: selected })
        setSuccess({ donated: r.donated ?? amount, guild_balance: r.guild_balance ?? 0 })
        setMyBalance(r.personal_balance ?? Math.max(0, myBalance - amount))
        onDone?.()
      } else {
        if (r.reason === 'insufficient') {
          setError(`잔고 부족 (필요 ${r.needed} · 보유 ${r.balance})`)
        } else {
          setError(r.reason || '실패')
        }
      }
    } catch (e: unknown) {
      setError((e as Error).message ?? '네트워크 오류')
    } finally {
      setBusy(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-[#1a1b1e] rounded-3xl border border-white/10 shadow-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <CreditIcon size={20} />
            서버에 크레딧 기부
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl leading-none">×</button>
        </div>

        {success ? (
          <div className="space-y-3">
            <div className="rounded-xl bg-emerald-500/15 border border-emerald-400/30 px-4 py-3 text-emerald-200 text-sm">
              {success.donated} 크레딧 기부 완료. 서버 공동 지갑 잔고: {success.guild_balance.toLocaleString()}
            </div>
            <button onClick={onClose} className="w-full py-2.5 rounded-xl bg-white text-black font-bold">
              닫기
            </button>
          </div>
        ) : (
          <>
            <div className="mb-3 text-sm text-gray-400">
              내 잔고: <span className="text-white font-semibold">{myBalance.toLocaleString()}</span>
            </div>

            <label className="block text-xs text-gray-400 mb-1">기부할 서버</label>
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className="w-full mb-4 px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-sm"
            >
              {guilds.length === 0 && <option value="">관리 가능한 서버 없음</option>}
              {guilds.map(g => (
                <option key={g.guild_id} value={g.guild_id}>
                  {serverNames[g.guild_id] || g.guild_id} (현재 {g.balance.toLocaleString()})
                </option>
              ))}
            </select>

            <label className="block text-xs text-gray-400 mb-1">금액</label>
            <div className="flex gap-2 mb-3">
              {[10, 50, 100, 500].map(v => (
                <button
                  key={v}
                  onClick={() => setAmount(v)}
                  className={`flex-1 py-2 rounded-xl text-sm font-medium border transition
                    ${amount === v
                      ? 'bg-white text-black border-white'
                      : 'bg-white/5 text-gray-300 border-white/10 hover:bg-white/10'}`}
                >
                  {v}
                </button>
              ))}
            </div>
            <input
              type="number"
              min={1}
              value={amount}
              onChange={(e) => setAmount(Math.max(1, parseInt(e.target.value || '0', 10)))}
              className="w-full mb-4 px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-sm tabular-nums"
            />

            {error && (
              <div className="mb-3 px-3 py-2 rounded-xl bg-red-500/15 border border-red-400/30 text-red-300 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={submit}
              disabled={busy || !selected || amount <= 0 || amount > myBalance}
              className="w-full py-3 rounded-xl bg-amber-400 text-black font-bold disabled:bg-white/5 disabled:text-white/30"
            >
              {busy ? '처리 중…' : `${amount.toLocaleString()} 크레딧 기부`}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
