import { C, FONT_BODY } from './colors'
import Button from './Button'

/**
 * 풀블리드 페이지 전체에 떠있는 두 코너 라벨.
 * freesentation.blog 패턴: TL 정체성 / TR 액션.
 */
export default function CornerLabels({
  ctaLabel = 'GO TO PROJECT',
  ctaHref = 'https://github.com/2rami/debi-marlene',
}: {
  ctaLabel?: string
  ctaHref?: string
}) {
  return (
    <>
      {/* 좌상단 — 정체성 */}
      <div
        style={{
          position: 'fixed',
          top: 'clamp(20px, 3vh, 36px)',
          left: 'clamp(20px, 3vw, 100px)',
          zIndex: 110,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          mixBlendMode: 'difference',
          color: '#FFFFFF',
        }}
      >
        <span
          style={{
            fontFamily: FONT_BODY,
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
          }}
        >
          NEXON · LLM EVAL
        </span>
      </div>

      {/* 우상단 — 통일된 outlined Button */}
      <div
        style={{
          position: 'fixed',
          top: 'clamp(20px, 3vh, 36px)',
          right: 'clamp(20px, 3vw, 100px)',
          zIndex: 110,
        }}
      >
        <Button
          href={ctaHref}
          label={ctaLabel}
          variant="outline"
          size="sm"
          style={{
            backdropFilter: 'blur(8px)',
            background: 'rgba(255, 255, 255, 0.7)',
            color: C.nexonBlue,
          }}
        />
      </div>
    </>
  )
}
