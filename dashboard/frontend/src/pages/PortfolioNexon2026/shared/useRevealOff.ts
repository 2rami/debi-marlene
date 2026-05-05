/**
 * URL 파라미터 ?reveal=off 감지.
 * Figma html-to-design / 정적 캡처 시 reveal/fade 애니메이션 무력화 용도.
 *
 * SSR 안전: window 없으면 false.
 */
export function useRevealOff(): boolean {
  if (typeof window === 'undefined') return false
  try {
    return new URLSearchParams(window.location.search).get('reveal') === 'off'
  } catch {
    return false
  }
}
