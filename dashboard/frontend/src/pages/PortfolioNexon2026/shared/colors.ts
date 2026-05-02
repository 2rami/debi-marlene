/**
 * PortfolioNexon2026 디자인 토큰
 *
 * 톤 일관성 (freesentation 원칙):
 * - 폰트 2종: Paperlogy(본문/UI) + NEXON Lv2 Gothic(헤드라인)
 * - 액센트 1색: nexonBlue (#0091CC)
 * - 라임/네이비는 NexonGate(CH 0) 컴포넌트에서만 raw hex로 사용
 * - 다크 섹션은 ARCHITECTURE / HIGHLIGHTS / CTA 한정
 */

const BLUE = '#0091CC'

export const C = {
  bgWhite: '#FFFFFF',
  bgLight: '#F7F9FC',
  bgSoft: '#EEF3F8',

  bgDark: '#070B14',
  bgDarkSoft: '#0F1729',

  nexonBlue: BLUE,
  nexonBlueAlt: '#0062DF',
  nexonLightBlue: '#5BC0E5',

  // 모든 비-블루 액센트는 BLUE 로 리다이렉트.
  // GATE(CH 0) 외 어디서도 라임/네이비가 등장하지 않도록 별칭 통일.
  nexonNavy: BLUE,
  lime: BLUE,
  coral: BLUE,
  yellow: BLUE,
  lavender: BLUE,

  ink: '#0A1224',
  inkSoft: '#3F4A5F',
  inkMuted: '#8A95A6',
  inverse: '#FFFFFF',

  cardBg: '#FFFFFF',
  cardBorder: 'rgba(10, 18, 36, 0.08)',
  cardShadow: '0 8px 28px rgba(10, 18, 36, 0.06)',
  cardShadowHover: '0 16px 44px rgba(0, 145, 204, 0.14)',

  radiusSm: 12,
  radiusMd: 18,
  radiusLg: 24,
} as const

// CH 0 GATE 전용 — Hero NEXON 로고 분해 모션에서만 사용
export const GATE_COLORS = {
  blue: '#0098D8',
  navy: '#00365C',
  lime: '#CAD400',
  black: '#1C1C1B',
} as const

// 본문 + 키커 + 모노 자리 — Paperlogy 통일
export const FONT_BODY =
  "'Paperlogy', 'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif"

// 헤드라인 — NEXON Lv2 Gothic
export const FONT_DISPLAY =
  "'NEXON Lv2 Gothic', 'Paperlogy', 'Pretendard', sans-serif"

// 별칭 — 기존 코드에서 FONT_SANS / FONT_GAME / FONT_MONO 참조하던 곳을 모두 Paperlogy/디스플레이로 흡수
export const FONT_SANS = FONT_DISPLAY
export const FONT_GAME = FONT_DISPLAY
export const FONT_MONO = FONT_BODY
