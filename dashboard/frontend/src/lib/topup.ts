/**
 * 크레딧 충전 API 클라이언트 + 타입.
 * dashboard 백엔드 /api/credits/topup/* 호출.
 *
 * 결제 금액은 서버가 패키지 정의로 결정한다. 클라이언트는 package_id 만 보내고
 * confirm 시에도 amount 를 보내지 않는다 (서버가 orderId 로 금액 판단).
 */
import { api } from '../services/api'

export interface TopupPackage {
  id: string
  krw: number
  credits: number
  label: string
  bonus: number
}

export interface CheckoutResponse {
  orderId: string
  amount: number
  orderName: string
  customerKey: string
}

export interface ConfirmResponse {
  success: boolean
  already?: boolean
  credits?: number
  balance?: number
}

export interface RefundResponse {
  ok: boolean
  reason?: string
  refunded_credits?: number
  balance?: number
  topup_credits?: number
}

export const topupApi = {
  packages: () =>
    api.get<{ packages: TopupPackage[] }>('/credits/topup/packages').then(r => r.data.packages),
  checkout: (packageId: string) =>
    api.post<CheckoutResponse>('/credits/topup/checkout', { package_id: packageId }).then(r => r.data),
  confirm: (paymentKey: string, orderId: string) =>
    api.post<ConfirmResponse>('/credits/topup/confirm', { paymentKey, orderId }).then(r => r.data),
  refund: (orderId: string) =>
    api.post<RefundResponse>('/credits/topup/refund', { orderId }).then(r => r.data),
}
