import { C, FONT_BODY } from './colors'
import Button from './Button'
import useIsMobile from './useIsMobile'

/**
 * 풀블리드 페이지 전체에 떠있는 두 코너 라벨.
 * freesentation.blog 패턴: TL 정체성 / TR 액션.
 * 모바일에선 정체성 라벨만 작게, CTA(GO TO BOT)는 본문 우선이라 숨김.
 */
export default function CornerLabels({
  ctaLabel = 'GO TO PROJECT',
  ctaHref = 'https://github.com/2rami/debi-marlene',
}: {
  ctaLabel?: string
  ctaHref?: string
}) {
  const isMobile = useIsMobile()
  return (
    <>
      {/* 좌상단 — 정체성 */}
      <div
        style={{
          position: 'fixed',
          top: 'clamp(14px, 2.5vh, 36px)',
          left: 'clamp(14px, 3vw, 100px)',
          zIndex: 110,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          mixBlendMode: 'difference',
          color: '#FFFFFF',
          pointerEvents: 'none',
        }}
      >
        <span
          style={{
            fontFamily: FONT_BODY,
            fontSize: isMobile ? 9.5 : 11,
            fontWeight: 700,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
          }}
        >
          NEXON · LLM EVAL
        </span>
      </div>

      {/* 우상단 — 외부 이탈 CTA. 면접관 시점에선 우선순위 낮음 → ghost 톤 + 모바일 숨김 */}
      {!isMobile && (
        <div
          style={{
            position: 'fixed',
            top: 'clamp(20px, 3vh, 36px)',
            right: 'clamp(20px, 3vw, 100px)',
            zIndex: 110,
            opacity: 0.7,
          }}
        >
          <Button
            href={ctaHref}
            label={ctaLabel}
            variant="ghost"
            size="sm"
            arrow={false}
            style={{
              color: C.inkMuted,
              fontWeight: 600,
              letterSpacing: '0.16em',
            }}
          />
        </div>
      )}
    </>
  )
}
