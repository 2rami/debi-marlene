import { useState, useEffect } from 'react'
import { ExternalLink, Loader2 } from 'lucide-react'
import { api } from '../../services/api'

interface OGKeyStatus {
  connected: boolean
  key_tail?: string | null
  created_at?: string | null
  last_used?: string | null
  calls?: number
  est_usd?: number
  est_krw?: number
}

// 게이트웨이 요금은 달러로 청구된다. 원화는 "얼마쯤 드나" 를 가늠하게 하는 안내용이라
// 환율을 실시간으로 끌어오지 않고 어림수로 둔다.
const USD_TO_KRW = 1400
const COST_PER_IMAGE_USD = 0.05
// ⚠️값은 원화로만 말한다. 봇에 이미 "크레딧" 재화가 있어서(대화·TTS) 이미지 값을
// 크레딧으로 환산해 보여줬더니 같은 이름의 다른 것 두 개가 되어 헷갈렸다(2026-08-25).
// 이미지는 봇 크레딧을 쓰지 않는다 — 사용자 본인 OG 잔액에서 나간다.

export default function OGKeySettings() {
  const [status, setStatus] = useState<OGKeyStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [keyInput, setKeyInput] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    let cancelled = false
    api.get<OGKeyStatus>('/og-key')
      .then(r => { if (!cancelled) setStatus(r.data) })
      .catch(e => { if (!cancelled) setError(e instanceof Error ? e.message : '상태를 불러오지 못했어요.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  const connect = async () => {
    const key = keyInput.trim()
    if (!key || submitting) return
    setSubmitting(true)
    setError(null)
    try {
      const r = await api.post<OGKeyStatus>('/og-key', { key })
      setStatus(r.data)
      setKeyInput('')
    } catch (e) {
      setError(e instanceof Error ? e.message : '연결하지 못했어요.')
    } finally {
      setSubmitting(false)
    }
  }

  const disconnect = async () => {
    setDeleting(true)
    setError(null)
    try {
      await api.delete('/og-key')
      setStatus({ connected: false })
      setConfirmingDelete(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : '해제하지 못했어요.')
    } finally {
      setDeleting(false)
    }
  }

  const perImageKrw = Math.round(COST_PER_IMAGE_USD * USD_TO_KRW / 10) * 10

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">이미지 생성</h2>
        <p className="text-discord-muted text-sm">
          디스코드에서 <span className="text-white/80 font-medium">/그림</span> 을 쓰려면 OpenGateway 키가 필요합니다.
        </p>
      </div>

      {loading ? (
        <div className="p-4 bg-discord-dark rounded-lg text-discord-muted text-sm flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin" />
          상태를 불러오는 중...
        </div>
      ) : status?.connected ? (
        <div className="p-4 bg-discord-dark rounded-lg space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.6)]" />
                <span className="text-sm font-medium text-emerald-400">연결됨</span>
              </div>
              <p className="font-mono text-sm text-white/70 truncate">
                sk-{'‥‥'}{status.key_tail}
              </p>
            </div>
            {confirmingDelete ? (
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={disconnect}
                  disabled={deleting}
                  className="px-3 py-1.5 rounded-lg bg-discord-red/20 border border-discord-red/40 text-discord-red text-sm font-medium hover:bg-discord-red/30 transition-colors disabled:opacity-50"
                >
                  {deleting ? '해제 중...' : '정말 해제'}
                </button>
                <button
                  onClick={() => setConfirmingDelete(false)}
                  disabled={deleting}
                  className="px-3 py-1.5 rounded-lg border border-discord-light/20 text-discord-muted text-sm hover:text-white transition-colors"
                >
                  취소
                </button>
              </div>
            ) : (
              <button
                onClick={() => setConfirmingDelete(true)}
                className="px-3 py-1.5 rounded-lg border border-discord-light/20 text-discord-muted text-sm hover:text-white hover:border-discord-light/40 transition-colors flex-shrink-0"
              >
                연결 해제
              </button>
            )}
          </div>

          <div className="pt-3 border-t border-discord-light/10">
            <p className="text-sm text-discord-muted">
              지금까지 <span className="text-white font-medium tabular-nums">{status.calls ?? 0}</span>장
              {' · '}
              약 <span className="text-white font-medium tabular-nums">
                {(status.est_krw ?? Math.round((status.calls ?? 0) * perImageKrw)).toLocaleString()}
              </span>원
              <span className="text-discord-muted/70">
                {' '}(${(status.est_usd ?? 0).toFixed(2)} · 본인 OG 계정에서 청구)
              </span>
            </p>
          </div>
        </div>
      ) : (
        <div className="p-4 bg-discord-dark rounded-lg space-y-5">
          <p className="text-sm text-discord-muted">
            요금은 본인 계정에서 나갑니다 — 한 장에 약 {perImageKrw}원, 5달러면 100장쯤입니다.
          </p>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-5 h-5 rounded bg-discord-light/20 text-white text-xs font-semibold flex items-center justify-center flex-shrink-0">1</span>
              <span className="font-medium text-white text-sm">OpenGateway 에서 키 받기</span>
            </div>
            {/* 새 탭 — 같은 창에서 넘어가면 키를 들고 돌아왔을 때 이 화면이 사라진다 */}
            <a
              href="https://opengateway.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-discord-darkest border border-discord-light/20 text-white text-sm hover:border-discord-light/40 transition-colors"
            >
              opengateway.ai 열기
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-5 h-5 rounded bg-discord-light/20 text-white text-xs font-semibold flex items-center justify-center flex-shrink-0">2</span>
              <span className="font-medium text-white text-sm">받은 키 붙여넣기</span>
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={keyInput}
                onChange={(e) => { setKeyInput(e.target.value); setError(null) }}
                onKeyDown={(e) => { if (e.key === 'Enter') connect() }}
                placeholder="sk-..."
                autoComplete="off"
                spellCheck={false}
                disabled={submitting}
                className="flex-1 min-w-0 p-2.5 bg-discord-darkest border border-discord-light/20 rounded-lg text-white text-sm font-mono placeholder-discord-muted focus:border-debi-primary focus:outline-none disabled:opacity-50"
              />
              <button
                onClick={connect}
                disabled={submitting || !keyInput.trim()}
                className="px-4 py-2.5 rounded-lg bg-debi-primary text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 flex-shrink-0"
              >
                {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                {submitting ? '확인 중...' : '연결하기'}
              </button>
            </div>
            <p className="text-xs text-discord-muted mt-2">
              키는 잠가서 보관하고, 등록 후에는 다시 보여주지 않습니다.
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-discord-red/10 border border-discord-red/30 text-discord-red text-sm">
          {error}
        </div>
      )}
    </div>
  )
}
