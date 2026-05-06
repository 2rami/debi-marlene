import { useEffect, useRef, useState, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { gsap } from 'gsap'
import { useAuth } from '../../contexts/AuthContext'
import { creditsApi, MyCreditsResponse, GachaResponse } from '../../lib/credits'
import { trackEvent } from '../../lib/analytics'
import CreditIcon from './CreditIcon'
import CreditDonateModal from './CreditDonateModal'

/**
 * 크레딧 지갑 — 구름 톤 알약 + 풍선 드롭다운.
 *
 * - BubbleMenu 의 `url(#bubble-cloud)` 필터 재사용 (구름 질감)
 * - 알약/패널/베팅 버튼 모두 흰 구름 베이스 + 크레딧 녹색(#326D1B/#E5FC8A) 액센트
 * - GSAP back.out 진입 애니메이션
 * - position:fixed 래퍼 → 패널은 portal 로 document.body 부착 (filter trap 회피)
 * - 비-로그인 시: 알약 안에 자물쇠 SVG, 드롭다운엔 로그인 안내만
 */
export default function CreditWalletDropdown() {
  const { user, login } = useAuth()
  const [data, setData] = useState<MyCreditsResponse | null>(null)
  const [open, setOpen] = useState(false)
  const [donateOpen, setDonateOpen] = useState(false)
  const [busyCheckIn, setBusyCheckIn] = useState(false)
  const [busyBet, setBusyBet] = useState(false)
  const [lastBet, setLastBet] = useState<GachaResponse | null>(null)
  const [flash, setFlash] = useState<string | null>(null)
  const btnRef = useRef<HTMLButtonElement | null>(null)
  const panelRef = useRef<HTMLDivElement | null>(null)
  const [anchor, setAnchor] = useState<{ top: number; right: number } | null>(null)

  const refresh = useCallback(async () => {
    if (!user) { setData(null); return }
    try {
      setData(await creditsApi.me())
    } catch {
      // 백엔드 미배포여도 부드럽게.
    }
  }, [user])

  useEffect(() => { void refresh() }, [refresh])

  // 외부 클릭 / Esc → 닫기
  useEffect(() => {
    if (!open) return
    const onDoc = (e: MouseEvent) => {
      const target = e.target as Node
      if (btnRef.current && btnRef.current.contains(target)) return
      const panel = document.getElementById('credit-dropdown-panel')
      if (panel && panel.contains(target)) return
      setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', onDoc)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDoc)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  // GSAP 진입 애니메이션
  useEffect(() => {
    if (!open) return
    const el = panelRef.current
    if (!el) return
    gsap.fromTo(
      el,
      { scale: 0.7, opacity: 0, y: -10, transformOrigin: 'top right' },
      { scale: 1, opacity: 1, y: 0, duration: 0.5, ease: 'back.out(1.6)' },
    )
  }, [open])

  const toggle = () => {
    if (!btnRef.current) return
    const rect = btnRef.current.getBoundingClientRect()
    setAnchor({ top: rect.bottom + 10, right: window.innerWidth - rect.right })
    setOpen(v => !v)
    if (!open) void refresh()
  }

  const handleCheckIn = async () => {
    if (busyCheckIn) return
    setBusyCheckIn(true)
    try {
      const r = await creditsApi.checkIn()
      if (r.ok && !r.already && r.gained > 0) {
        trackEvent('credit_check_in', { gained: r.gained, streak: r.streak })
        setFlash(`+${r.gained} · 연속 ${r.streak}일`)
        setTimeout(() => setFlash(null), 2400)
      }
      await refresh()
    } catch {
      // 무음
    } finally {
      setBusyCheckIn(false)
    }
  }

  const handleBet = async (bet: number) => {
    if (busyBet || bet <= 0) return
    setBusyBet(true)
    try {
      const r = await creditsApi.gacha(bet)
      setLastBet(r)
      if (r.ok) {
        trackEvent('credit_gacha', { bet, multiplier: r.multiplier ?? 0 })
      }
      await refresh()
    } catch {
      // 무음 — last bet 갱신 실패 무시
    } finally {
      setBusyBet(false)
    }
  }

  const isLoggedIn = !!user
  const balance = data?.balance ?? 0
  const streak = data?.streak_days ?? 0
  const checkedToday = data?.checked_in_today ?? false
  const dailyBet = data?.daily_bet ?? 0
  const dailyCap = data?.daily_bet_cap ?? 50
  const remainingCap = Math.max(0, dailyCap - dailyBet)

  // ── 구름 톤 베이스 ──
  // 트리거 알약: 흰 구름 + 녹색 텍스트
  // 패널: 흰 구름 + 녹색 액센트 + 미세한 그림자
  const CLOUD_BG = 'rgba(255,255,255,0.92)'
  const CLOUD_FILTER = 'url(#bubble-cloud)'

  return (
    <>
      <button
        ref={btnRef}
        onClick={toggle}
        className="relative h-12 md:h-14 rounded-full cursor-pointer flex items-center group"
        aria-label={isLoggedIn ? `크레딧 잔고 ${balance.toLocaleString()}` : '크레딧 (로그인 필요)'}
      >
        {/* 구름 베이스 — bubble-cloud filter 로 가장자리 흐트러짐 */}
        <span
          className="absolute inset-0 rounded-full shadow-[0_4px_16px_rgba(0,0,0,0.12)] transition-transform duration-200 group-hover:scale-105"
          style={{ background: CLOUD_BG, filter: CLOUD_FILTER }}
          aria-hidden
        />
        <span className="relative z-10 flex items-center gap-1.5 px-3 md:px-4">
          {isLoggedIn ? (
            <>
              <CreditIcon size={20} />
              <span className="hidden sm:inline text-sm font-bold text-[#326D1B] tabular-nums">
                {balance.toLocaleString()}
              </span>
              {!checkedToday && (
                <span
                  className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#E5FC8A] ring-2 ring-[#326D1B]"
                  aria-hidden
                />
              )}
            </>
          ) : (
            <>
              {/* 자물쇠 SVG — 로그인 필요 표시 */}
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                   stroke="#326D1B" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"
                   aria-hidden>
                <rect x="3" y="11" width="18" height="11" rx="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
              <span className="hidden sm:inline text-sm font-bold text-[#326D1B]">로그인</span>
            </>
          )}
        </span>
      </button>

      {open && anchor && createPortal(
        <div
          ref={panelRef}
          id="credit-dropdown-panel"
          className="fixed z-[1003] w-72"
          style={{ top: anchor.top, right: anchor.right }}
          role="dialog"
        >
          {/* 패널 구름 베이스 */}
          <div className="relative">
            <span
              className="absolute inset-0 rounded-3xl shadow-[0_12px_32px_rgba(0,0,0,0.18)]"
              style={{ background: CLOUD_BG, filter: CLOUD_FILTER }}
              aria-hidden
            />

            {/* 작은 꼬리 (트리거 향함) */}
            <span
              className="absolute -top-2 right-8 w-5 h-5 rounded-full"
              style={{ background: CLOUD_BG, filter: CLOUD_FILTER }}
              aria-hidden
            />

            <div className="relative z-10 p-4">
              {!isLoggedIn ? (
                <LoginGate onLogin={() => { setOpen(false); login() }} />
              ) : (
                <LoggedInPanel
                  balance={balance}
                  streak={streak}
                  checkedToday={checkedToday}
                  busyCheckIn={busyCheckIn}
                  flash={flash}
                  dailyBet={dailyBet}
                  dailyCap={dailyCap}
                  remainingCap={remainingCap}
                  busyBet={busyBet}
                  lastBet={lastBet}
                  onBet={handleBet}
                  onCheckIn={handleCheckIn}
                  onDonate={() => { setOpen(false); setDonateOpen(true) }}
                />
              )}
            </div>
          </div>
        </div>,
        document.body,
      )}

      <CreditDonateModal
        isOpen={donateOpen}
        onClose={() => setDonateOpen(false)}
        onDone={refresh}
      />
    </>
  )
}

// ─────────────────────────────────────────────────────────────────────────────

interface BetCloudButtonProps {
  label: string
  disabled?: boolean
  onClick: () => void
  danger?: boolean
}

function BetCloudButton({ label, disabled, onClick, danger }: BetCloudButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="relative h-9 rounded-full text-xs font-bold transition-transform active:scale-95 disabled:cursor-not-allowed"
    >
      <span
        className={`absolute inset-0 rounded-full transition-all
          ${disabled
            ? 'opacity-40'
            : 'shadow-[0_2px_6px_rgba(0,0,0,0.08)] hover:scale-105'}`}
        style={{
          background: danger ? 'rgba(229,252,138,0.85)' : 'rgba(255,255,255,0.92)',
          filter: 'url(#bubble-cloud)',
        }}
        aria-hidden
      />
      <span className={`relative z-10 px-1 ${danger ? 'text-[#244D11]' : 'text-[#326D1B]'}`}>
        {label}
      </span>
    </button>
  )
}

function LoginGate({ onLogin }: { onLogin: () => void }) {
  return (
    <div className="text-[#326D1B]">
      <div className="flex items-center gap-2 mb-2">
        <CreditIcon size={22} />
        <div className="text-base font-bold">크레딧 시스템</div>
      </div>
      <p className="text-sm text-[#326D1B]/80 leading-relaxed mb-4">
        로그인하면 출석체크 +10, 베팅, 서버 기부 등<br />
        크레딧 시스템을 사용할 수 있어요.
      </p>
      <button
        onClick={onLogin}
        className="w-full py-2.5 rounded-2xl text-sm font-bold bg-[#326D1B] text-[#E5FC8A] hover:bg-[#244D11] transition-colors"
      >
        디스코드로 로그인
      </button>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────

interface LoggedInProps {
  balance: number
  streak: number
  checkedToday: boolean
  busyCheckIn: boolean
  flash: string | null
  dailyBet: number
  dailyCap: number
  remainingCap: number
  busyBet: boolean
  lastBet: GachaResponse | null
  onBet: (bet: number) => void
  onCheckIn: () => void
  onDonate: () => void
}

function formatLastBet(r: GachaResponse | null): string | null {
  if (!r) return null
  if (!r.ok) {
    if (r.reason === 'daily_cap') return `오늘 베팅 한도 도달 (남은 ${r.remaining ?? 0})`
    if (r.reason === 'insufficient') return `잔고 부족 (필요 ${r.needed})`
    return r.reason || '베팅 실패'
  }
  const mult = r.multiplier ?? 0
  const tag = mult === 0 ? '꽝' : mult === 10 ? 'JACKPOT 10x' : `${mult}x`
  const sign = (r.net ?? 0) >= 0 ? '+' : ''
  return `[${tag}] ${r.bet} → ${r.payout} (${sign}${r.net})`
}

function LoggedInPanel({
  balance, streak, checkedToday, busyCheckIn, flash,
  dailyBet, dailyCap, remainingCap, busyBet, lastBet,
  onBet, onCheckIn, onDonate,
}: LoggedInProps) {
  const presets = [5, 10, 50]
  const allInAmount = Math.min(balance, remainingCap)
  const lastLine = formatLastBet(lastBet)
  const lastIsWin = !!(lastBet?.ok && (lastBet.net ?? 0) > 0)
  return (
    <div className="text-[#326D1B]">
      {/* 헤더 */}
      <div className="flex items-center gap-2 mb-3">
        <CreditIcon size={24} />
        <div className="leading-tight">
          <div className="text-[10px] uppercase tracking-wider text-[#326D1B]/55">
            크레딧 잔고
          </div>
          <div className="text-2xl font-extrabold tabular-nums leading-none">
            {balance.toLocaleString()}
          </div>
        </div>
      </div>

      {/* 미니 통계 */}
      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div
          className="rounded-2xl px-3 py-2 border border-[#326D1B]/15"
          style={{ background: 'rgba(229,252,138,0.35)' }}
        >
          <div className="text-[#326D1B]/60">연속 출석</div>
          <div className="font-bold">{streak}일</div>
        </div>
        <div
          className="rounded-2xl px-3 py-2 border border-[#326D1B]/15"
          style={{ background: 'rgba(229,252,138,0.35)' }}
        >
          <div className="text-[#326D1B]/60">오늘 출석</div>
          <div className={`font-bold ${checkedToday ? 'text-[#326D1B]' : 'text-[#7a4a08]'}`}>
            {checkedToday ? '완료' : '미완료'}
          </div>
        </div>
      </div>

      {/* 액션 버튼 */}
      <button
        onClick={onCheckIn}
        disabled={checkedToday || busyCheckIn}
        className={`w-full py-2.5 rounded-2xl text-sm font-bold mb-3 transition-colors flex items-center justify-center gap-2
          ${checkedToday
            ? 'bg-[#326D1B]/10 text-[#326D1B]/40 cursor-not-allowed'
            : 'bg-[#326D1B] text-[#E5FC8A] hover:bg-[#244D11]'}`}
      >
        <CreditIcon size={14} />
        {checkedToday ? '오늘 출석 완료' : '출석체크 +10'}
      </button>

      {/* 베팅 섹션 — 구름 모양 작은 버튼 4개 */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-[10px] text-[#326D1B]/60 mb-1.5">
          <span>베팅 (70% 0배 / 20% 2배 / 8% 3배 / 2% 10배)</span>
          <span className="tabular-nums">{dailyBet}/{dailyCap}</span>
        </div>
        <div className="grid grid-cols-4 gap-1.5">
          {presets.map(amt => {
            const disabled = busyBet || amt > balance || amt > remainingCap
            return (
              <BetCloudButton
                key={amt}
                label={String(amt)}
                disabled={disabled}
                onClick={() => onBet(amt)}
              />
            )
          })}
          <BetCloudButton
            label={allInAmount > 0 ? `ALL ${allInAmount}` : 'ALL'}
            disabled={busyBet || allInAmount <= 0}
            onClick={() => onBet(allInAmount)}
            danger
          />
        </div>
        {lastLine && (
          <div
            className={`mt-2 rounded-2xl px-3 py-1.5 text-[11px] font-semibold tabular-nums border
              ${lastIsWin
                ? 'border-[#326D1B]/30 text-[#326D1B]'
                : 'border-[#7a4a08]/25 text-[#7a4a08]'}`}
            style={{
              background: lastIsWin
                ? 'rgba(229,252,138,0.55)'
                : 'rgba(255,255,255,0.6)',
            }}
          >
            {lastLine}
          </div>
        )}
      </div>

      <button
        onClick={onDonate}
        className="w-full py-2.5 rounded-2xl text-sm font-medium bg-white/0 hover:bg-[#326D1B]/10 border border-[#326D1B]/25 text-[#326D1B] transition-colors"
      >
        서버에 기부
      </button>

      {flash && (
        <div className="mt-3 rounded-2xl border border-[#326D1B]/30 px-3 py-2 text-[#326D1B] text-xs font-semibold"
             style={{ background: 'rgba(229,252,138,0.6)' }}>
          {flash}
        </div>
      )}
    </div>
  )
}
