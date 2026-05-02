/**
 * PortfolioNexon2026 디자인 토큰
 * 넥슨 브랜드 아이덴티티 (CI: 청록 + 라임 + 다크 네이비)
 *
 * 톤 일관성 원칙:
 * - 라이트 섹션 베이스 = bgWhite | bgLight (둘만 사용)
 * - 다크 섹션은 ARCHITECTURE 와 CTA 두 곳뿐
 * - 액센트 컬러는 nexonBlue + lime + ink 3색 한정
 * - coral/yellow/lavender 는 사용 금지 (제거)
 */

export const C = {
  // BG (라이트)
  bgWhite: '#FFFFFF',
  bgLight: '#F7F9FC',
  bgSoft: '#EEF3F8', // 살짝 더 차분하게

  // BG (다크 — ARCHITECTURE / CTA 전용)
  bgDark: '#070B14',
  bgDarkSoft: '#0F1729',

  // Brand (Nexon CI)
  nexonBlue: '#0091CC', // CI 청록
  nexonBlueAlt: '#0062DF', // 인터랙션용 보조 블루
  nexonLightBlue: '#5BC0E5', // 톤 다운된 라이트 블루 (악센트용)
  nexonNavy: '#0A1F3C', // CI 다크 네이비
  lime: '#C4F000', // CI 라임 (그대로)

  // Legacy aliases — Nexon CI 톤으로 통일 (개별 컬러 대신 nexonBlue 계열 + lime 만 사용)
  coral: '#0091CC', // 기존 코랄 → 블루로 통일
  yellow: '#C4F000', // 기존 옐로우 → 라임으로 통일
  lavender: '#0A1F3C', // 기존 라벤더 → 네이비로 통일

  // Text
  ink: '#0A1224',
  inkSoft: '#3F4A5F',
  inkMuted: '#8A95A6',
  inverse: '#FFFFFF',

  // Card / Surface
  cardBg: '#FFFFFF',
  cardBorder: 'rgba(10, 18, 36, 0.08)',
  cardShadow: '0 8px 28px rgba(10, 18, 36, 0.06)',
  cardShadowHover: '0 16px 44px rgba(0, 145, 204, 0.14)',

  // Radius (통일)
  radiusSm: 12,
  radiusMd: 18,
  radiusLg: 24,
} as const

// 본문 (Paperlogy — Footer 톤과 통일)
export const FONT_BODY =
  "'Paperlogy', 'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif"

// 디스플레이 (큰 헤드라인 — NEXON Lv2 Gothic)
export const FONT_DISPLAY =
  "'NEXON Lv2 Gothic', 'Paperlogy', 'Pretendard', sans-serif"

// 부제/세련된 sans
export const FONT_SANS =
  "'NEXON Lv2 Gothic', 'Paperlogy', 'Pretendard', sans-serif"

// 게임/메이플 액센트 (캐릭터 카드 등 한정)
export const FONT_GAME =
  "'NEXON Maplestory', 'NEXON Lv2 Gothic', sans-serif"

// 모노 (코드/태그/숫자)
export const FONT_MONO =
  "'JetBrains Mono', 'D2Coding', 'SF Mono', Menlo, Consolas, monospace"
