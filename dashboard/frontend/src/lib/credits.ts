/**
 * 크레딧 API 클라이언트.
 * dashboard 백엔드 /api/credits/* 호출 + 타입 정의.
 */
import { api } from '../services/api'

export interface LedgerEntry {
  user_id: string
  guild_id?: string
  type: 'check_in' | 'debit' | 'credit' | 'donate' | 'gacha'
  amount: number
  reason: string
  ts: string
}

export interface MyCreditsResponse {
  balance: number
  streak_days: number
  last_check_in: string | null
  checked_in_today: boolean
  daily_bet: number
  daily_bet_cap: number
  recent_ledger: LedgerEntry[]
}

export interface CheckInResponse {
  ok: boolean
  already?: boolean
  gained: number
  bonus?: number
  balance: number
  streak: number
}

export interface GachaResponse {
  ok: boolean
  reason?: string
  multiplier?: number
  bet?: number
  payout?: number
  net?: number
  balance?: number
  daily_bet?: number
  daily_cap?: number
  // insufficient 시
  needed?: number
  // daily_cap 시
  cap?: number
  used_today?: number
  remaining?: number
}

export interface DonateResponse {
  ok: boolean
  reason?: string
  personal_balance?: number
  guild_balance?: number
  donated?: number
  needed?: number
  balance?: number
}

export interface GuildBalance {
  guild_id: string
  balance: number
}

export const creditsApi = {
  me: () => api.get<MyCreditsResponse>('/credits/me').then(r => r.data),
  checkIn: () => api.post<CheckInResponse>('/credits/check-in').then(r => r.data),
  donate: (guild_id: string, amount: number) =>
    api.post<DonateResponse>('/credits/donate', { guild_id, amount }).then(r => r.data),
  gacha: (bet: number) =>
    api.post<GachaResponse>('/credits/gacha', { bet }).then(r => r.data),
  guilds: () =>
    api.get<{ guilds: GuildBalance[] }>('/credits/guilds').then(r => r.data),
}
