import { forwardRef } from 'react'

/**
 * SVG 텍스처 필터 정의 — 페이지당 한 번만 렌더링하면 됨
 * GlassButton이 자동으로 마운트 여부를 추적해서 중복 방지
 */
let filterMounted = false

function GlassFilter() {
  if (filterMounted) return null
  filterMounted = true

  return (
    <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden="true">
      <defs>
        {/* 오목렌즈 왜곡 + 종이 질감 통합 필터 (backdrop-filter용) */}
        <filter id="glass-lens" x="0%" y="0%" width="100%" height="100%">
          {/* 1단계: 오목렌즈 굴절 — 중앙→가장자리 그라데이션 맵으로 픽셀을 끌어당김 */}
          <feImage
            href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cdefs%3E%3CradialGradient id='rg' cx='50%25' cy='50%25' r='50%25'%3E%3Cstop offset='0%25' stop-color='%23808080'/%3E%3Cstop offset='70%25' stop-color='%23606060'/%3E%3Cstop offset='100%25' stop-color='%23404040'/%3E%3C/radialGradient%3E%3C/defs%3E%3Crect width='100' height='100' fill='url(%23rg)'/%3E%3C/svg%3E"
            result="lensMap"
            preserveAspectRatio="none"
            x="0" y="0" width="100%" height="100%"
          />
          <feDisplacementMap
            in="SourceGraphic" in2="lensMap"
            scale="25"
            xChannelSelector="R" yChannelSelector="G"
            result="displaced"
          />
          {/* 2단계: 아주 살짝 블러 (피그마 흐릿함=6 대응) */}
          <feGaussianBlur in="displaced" stdDeviation="0.8" result="lensed" />
          {/* 3단계: 종이/유리 표면 텍스처 */}
          <feTurbulence
            type="fractalNoise" baseFrequency="0.5"
            numOctaves="3" seed="5730"
            result="noise"
          />
          <feDisplacementMap
            in="lensed" in2="noise"
            scale="2"
            xChannelSelector="R" yChannelSelector="G"
          />
        </filter>
        {/* 표면 텍스처 전용 (filter 속성용) */}
        <filter id="glass-texture" x="0%" y="0%" width="100%" height="100%">
          <feTurbulence
            type="fractalNoise" baseFrequency="0.5"
            numOctaves="3" seed="5730"
            result="noise"
          />
          <feDisplacementMap
            in="SourceGraphic" in2="noise"
            scale="2"
            xChannelSelector="R" yChannelSelector="G"
          />
        </filter>
      </defs>
    </svg>
  )
}

interface GlassButtonProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  as?: 'a' | 'button'
  size?: 'sm' | 'md' | 'lg'
}

const GlassButton = forwardRef<HTMLAnchorElement | HTMLButtonElement, GlassButtonProps>(
  ({ as = 'a', size = 'md', children, className = '', style, ...props }, ref) => {
    const sizeClass = {
      sm: 'w-[160px] h-[48px] text-[20px]',
      md: 'w-[199px] h-[56px] text-[24px]',
      lg: 'w-[240px] h-[64px] text-[28px]',
    }[size]

    const Tag = as as any

    return (
      <>
        <GlassFilter />
        <Tag
          ref={ref}
          className={`group relative flex items-center justify-center hover:-translate-y-1 transition-transform duration-300 ${sizeClass} ${className}`}
          style={style}
          {...props}
        >
          {/* 유리판: backdrop-blur로 뒤 배경을 뿌옇게 + SVG 텍스처로 표면 질감 */}
          <div
            className="absolute inset-0 rounded-[15px] pointer-events-none"
            style={{
              background: 'rgba(255, 255, 255, 0.08)',
              backdropFilter: 'url(#glass-lens)',
              WebkitBackdropFilter: 'url(#glass-lens)',
              filter: 'url(#glass-texture)',
              boxShadow: '0px 4px 4px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.6)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            }}
          />
          <span className="relative z-10 font-title text-black pb-1">{children}</span>
        </Tag>
      </>
    )
  }
)

GlassButton.displayName = 'GlassButton'

export default GlassButton
