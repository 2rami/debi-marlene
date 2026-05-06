/**
 * GA4 통합.
 *
 * - 측정 ID는 환경변수 VITE_GA_MEASUREMENT_ID 로 주입. 하드코딩 금지.
 * - production 빌드(import.meta.env.PROD)에서만 활성. dev 노이즈 차단.
 * - 쿠키 동의 (localStorage `ga_consent` = 'granted' | 'denied') 가 'granted' 일 때만 gtag.js 로드.
 *   거부 시 script tag 자체를 주입하지 않음.
 *
 * 노출 함수:
 *   initGA()            루트에서 1회 호출. 동의·prod 게이트 통과 시 gtag.js 로드.
 *   trackPageView(path) SPA 라우트 변경 시 발사.
 *   trackEvent(name, p) 커스텀 이벤트.
 *   grantConsent()      배너에서 동의 클릭 시 호출 → 즉시 init 재시도.
 *   denyConsent()       배너에서 거부 시 호출 → 향후 init 차단.
 *   getConsentStatus()
 */

type ConsentStatus = 'granted' | 'denied' | 'unknown'

const CONSENT_KEY = 'ga_consent'

declare global {
  interface Window {
    dataLayer: unknown[]
    gtag: (...args: unknown[]) => void
  }
}

let initialized = false

function getMeasurementId(): string | undefined {
  return import.meta.env.VITE_GA_MEASUREMENT_ID as string | undefined
}

export function getConsentStatus(): ConsentStatus {
  if (typeof window === 'undefined') return 'unknown'
  const v = window.localStorage.getItem(CONSENT_KEY)
  if (v === 'granted' || v === 'denied') return v
  return 'unknown'
}

function shouldEnable(): boolean {
  if (!import.meta.env.PROD) return false
  if (typeof window === 'undefined') return false
  if (!getMeasurementId()) return false
  if (getConsentStatus() !== 'granted') return false
  return true
}

function loadGtagScript(measurementId: string) {
  // gtag dataLayer + 함수 시그니처
  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag() {
    // eslint-disable-next-line prefer-rest-params
    window.dataLayer.push(arguments)
  }
  window.gtag('js', new Date())
  // SPA 페이지뷰는 수동으로 발사하므로 자동 발사 끔
  window.gtag('config', measurementId, { send_page_view: false })

  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`
  document.head.appendChild(script)
}

export function initGA(): void {
  if (initialized) return
  if (!shouldEnable()) return
  const id = getMeasurementId()
  if (!id) return
  loadGtagScript(id)
  initialized = true
  // 첫 페이지뷰는 GAPageTracker 의 useEffect 가 마운트 시 발사함 — 여기서는 안 쏨 (중복 방지)
}

export function trackPageView(path: string): void {
  if (!initialized) return
  const id = getMeasurementId()
  if (!id || !window.gtag) return
  window.gtag('event', 'page_view', {
    page_path: path,
    page_location: window.location.href,
    page_title: document.title,
  })
}

export function trackEvent(name: string, params: Record<string, unknown> = {}): void {
  if (!initialized) return
  if (!window.gtag) return
  window.gtag('event', name, params)
}

export function grantConsent(): void {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(CONSENT_KEY, 'granted')
  // GABootstrap 시점에 막혔다면 여기서 init 재시도 + 첫 page_view 직접 발사
  // (라우트 변경이 없으면 GAPageTracker 가 안 쏘기 때문)
  if (!initialized) {
    initGA()
    if (initialized) {
      trackPageView(window.location.pathname + window.location.search)
    }
  }
}

export function denyConsent(): void {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(CONSENT_KEY, 'denied')
  // 이미 로드된 경우는 다음 새로고침 때 적용 (스크립트 언로드는 깔끔하지 않음)
}
