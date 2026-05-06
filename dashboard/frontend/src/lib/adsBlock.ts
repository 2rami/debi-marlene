/**
 * AdSense Auto Ads 차단 유틸.
 *
 * /portfolio/* 라우트는 NEXON 면접관이 보는 페이지라 광고 노출 금지.
 *
 * 차단 메커니즘:
 *   - `window.adsbygoogle.pauseAdRequests = 1` — Google 공식 Auto Ads 일시정지 플래그
 *     (https://support.google.com/adsense/answer/9261805)
 *   - 이미 주입된 광고 슬롯(ins.adsbygoogle / aswift / google_ads_iframe) DOM 제거
 *   - 비동기로 슬롯이 늦게 들어올 수 있어 짧은 폴링으로 추가 청소
 *
 * 첫 페이지 로드 시점은 `index.html` 의 inline 가드가 처리 (pathname 보고 즉시 pause).
 * 이 모듈은 SPA 라우트 변경 / 동적 슬롯 주입 대응용.
 */

interface AdsByGoogle extends Array<unknown> {
  pauseAdRequests?: 0 | 1
}

declare global {
  interface Window {
    adsbygoogle?: AdsByGoogle
  }
}

export function removeAdSlots(): void {
  if (typeof document === 'undefined') return
  document
    .querySelectorAll(
      'ins.adsbygoogle, iframe[id^="aswift_"], iframe[id^="google_ads_iframe"], div[id^="google_ads_iframe"]',
    )
    .forEach((el) => el.remove())
}

export function pauseAds(): void {
  if (typeof window === 'undefined') return
  const w = window as Window
  w.adsbygoogle = w.adsbygoogle || ([] as AdsByGoogle)
  ;(w.adsbygoogle as AdsByGoogle).pauseAdRequests = 1
  removeAdSlots()
}

export function resumeAds(): void {
  if (typeof window === 'undefined') return
  const ab = (window as Window).adsbygoogle
  if (ab) ab.pauseAdRequests = 0
}
