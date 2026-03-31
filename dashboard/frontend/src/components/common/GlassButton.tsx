import { forwardRef } from 'react'

function GlassFilter() {
  if (typeof document !== 'undefined' && document.getElementById('glass-lens')) return null

  return (
    <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden="true">
      <defs>
        {/* 종이/유리 표면 텍스처 필터 (backdrop-filter용) */}
        <filter id="glass-lens" x="0%" y="0%" width="100%" height="100%">
          {/* 살짝 블러 (유리 느낌) */}
          <feGaussianBlur in="SourceGraphic" stdDeviation="0.6" result="blurred" />
          {/* 종이/유리 표면 텍스처 */}
          <feTurbulence
            type="fractalNoise" baseFrequency="0.5"
            numOctaves="3" seed="5730"
            result="noise"
          />
          <feDisplacementMap
            in="blurred" in2="noise"
            scale="3"
            xChannelSelector="R" yChannelSelector="G"
          />
        </filter>
        {/* 종이/유리 질감 텍스처 (filter 속성용, Chrome 호환) */}
        <filter id="glass-texture" x="-5%" y="-5%" width="110%" height="110%">
          {/* 살짝 블러 (유리 느낌) */}
          <feGaussianBlur in="SourceGraphic" stdDeviation="0.5" result="blurred" />
          {/* 종이 질감 텍스처 */}
          <feTurbulence
            type="fractalNoise" baseFrequency="0.45"
            numOctaves="3" seed="5730"
            result="noise"
          />
          <feDisplacementMap
            in="blurred" in2="noise"
            scale="4"
            xChannelSelector="R" yChannelSelector="G"
          />
        </filter>
      </defs>
    </svg>
  )
}

type GlassButtonProps = {
  as?: 'a' | 'button'
  size?: 'sm' | 'md' | 'lg'
} & (
  | (React.AnchorHTMLAttributes<HTMLAnchorElement> & { as?: 'a' })
  | (React.ButtonHTMLAttributes<HTMLButtonElement> & { as: 'button' })
)

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
          {/* 유리판: backdrop-blur + SVG 텍스처로 종이 질감 테두리 */}
          <div
            className="absolute inset-0 rounded-[15px] pointer-events-none transition-all duration-300 group-hover:shadow-[0_0_15px_rgba(255,255,255,0.6),0_0_30px_rgba(255,255,255,0.3)] group-hover:border-white/80"
            style={{
              background: 'rgba(255, 255, 255, 0.35)',
              filter: 'url(#glass-texture)',
              boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
              border: '1.5px solid rgba(255, 255, 255, 0.3)',
            }}
          />
          <span className="relative z-10 font-title text-black">{children}</span>
        </Tag>
      </>
    )
  }
)

GlassButton.displayName = 'GlassButton'

export default GlassButton
