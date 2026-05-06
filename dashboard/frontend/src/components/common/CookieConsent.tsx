/**
 * 쿠키 동의 배너 — 한국 개보법 + GDPR 대응.
 *
 * 동작:
 *   - localStorage `ga_consent` 미설정 시에만 노출.
 *   - 동의/거부 클릭 시 analytics.ts 의 grant/deny 호출 + 배너 닫기.
 *   - dev 빌드에서는 표시하지 않음 (PROD 게이트).
 */

import { useEffect, useState } from 'react'
import { denyConsent, getConsentStatus, grantConsent } from '../../lib/analytics'

export default function CookieConsent() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!import.meta.env.PROD) return
    if (getConsentStatus() === 'unknown') setVisible(true)
  }, [])

  if (!visible) return null

  const accept = () => {
    grantConsent()
    setVisible(false)
  }
  const reject = () => {
    denyConsent()
    setVisible(false)
  }

  // 뎁마봇 Landing 톤: 화이트 글래스 + 트윈스 그라데이션 (#3cabc9 디비 / #e58fb6 마를렌)
  return (
    <div
      role="dialog"
      aria-label="쿠키 사용 동의"
      className="fixed left-4 right-4 bottom-4 md:left-1/2 md:right-auto md:bottom-6 md:-translate-x-1/2 z-[9999] md:max-w-[640px] md:w-[calc(100%-2rem)]"
    >
      {/* 트윈스 그라데이션 글로우 — 카드 뒤에 부드러운 후광 */}
      <div
        aria-hidden
        className="absolute -inset-3 rounded-[28px] bg-gradient-to-br from-[#3cabc9]/25 to-[#e58fb6]/25 blur-2xl pointer-events-none"
      />

      <div
        className="relative rounded-2xl border border-white/40 bg-white/85 backdrop-blur-md shadow-[0_12px_40px_rgba(60,171,201,0.18)] px-5 py-4 md:px-6 md:py-5 flex flex-col md:flex-row md:items-center gap-4"
      >
        <div
          className="flex-1 text-gray-700 text-[13.5px] leading-relaxed"
          style={{ fontFamily: "'Paperlogy', sans-serif" }}
        >
          <div
            className="font-title text-[15px] mb-1 bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent"
          >
            쿠키 사용 안내
          </div>
          이 사이트는 방문 통계를 위해 Google Analytics 쿠키를 사용합니다. 동의하시면 익명화된
          사용 데이터가 수집됩니다.
        </div>

        <div className="flex gap-2 shrink-0 self-stretch md:self-auto">
          <button
            type="button"
            onClick={reject}
            className="flex-1 md:flex-none px-4 py-2 rounded-xl text-sm font-semibold text-gray-600 border border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300 transition-colors cursor-pointer"
          >
            거부
          </button>
          <button
            type="button"
            onClick={accept}
            className="flex-1 md:flex-none px-5 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] hover:brightness-110 active:brightness-95 transition-all shadow-md shadow-[#e58fb6]/30 cursor-pointer"
          >
            동의
          </button>
        </div>
      </div>
    </div>
  )
}
