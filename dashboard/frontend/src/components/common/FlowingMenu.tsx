import { useRef, useEffect, useState } from 'react'
import { gsap } from 'gsap'

interface FlowingMenuItem {
  text: string
  image?: string
}

interface FlowingMenuProps {
  items: FlowingMenuItem[]
  speed?: number
  textColor?: string
  bgColor?: string
  hoverBgColor?: string
  hoverTextColor?: string
  borderColor?: string
  className?: string
  fontSize?: string
  padding?: string
  glassEffect?: boolean
}

export default function FlowingMenu({
  items,
  speed = 12,
  textColor = '#374151',
  bgColor = 'transparent',
  hoverBgColor: _hbg = '#3cabc9',
  hoverTextColor: _htc = '#fff',
  borderColor = '#e5e7eb',
  className = '',
  fontSize,
  padding,
  glassEffect = false,
}: FlowingMenuProps) {
  return (
    <div className={`w-full overflow-hidden relative ${className}`}>
      {/* 배경: 유리구름 텍스쳐는 여기만 적용 */}
      <div
        className="absolute inset-0"
        style={{ backgroundColor: bgColor, filter: glassEffect ? 'url(#glass-cloud)' : undefined }}
      />
      <nav className="relative z-[1] flex flex-col m-0 p-0">
        {items.map((item, idx) => (
          <FlowingRow
            key={idx}
            {...item}
            speed={speed}
            textColor={textColor}
            borderColor={borderColor}
            isFirst={idx === 0}
            fontSize={fontSize}
            padding={padding}
          />
        ))}
      </nav>
    </div>
  )
}

function FlowingRow({
  text,
  image,
  speed,
  textColor,
  borderColor,
  isFirst,
  fontSize,
  padding,
}: FlowingMenuItem & {
  speed: number
  textColor: string
  borderColor: string
  isFirst: boolean
  fontSize?: string
  padding?: string
}) {
  const itemRef = useRef<HTMLDivElement>(null)
  const defaultInnerRef = useRef<HTMLDivElement>(null)
  const defaultAnimRef = useRef<gsap.core.Tween | null>(null)
  const [reps, setReps] = useState(8)

  useEffect(() => {
    const calc = () => {
      const el = defaultInnerRef.current
      if (!el) return
      const part = el.querySelector('.marquee-part') as HTMLElement
      if (!part) return
      setReps(Math.max(8, Math.ceil(window.innerWidth / part.offsetWidth) + 3))
    }
    calc()
    window.addEventListener('resize', calc)
    return () => window.removeEventListener('resize', calc)
  }, [text])

  useEffect(() => {
    const setup = () => {
      if (!defaultInnerRef.current) return
      const part = defaultInnerRef.current.querySelector('.marquee-part') as HTMLElement
      if (!part || part.offsetWidth === 0) return
      defaultAnimRef.current?.kill()
      defaultAnimRef.current = gsap.to(defaultInnerRef.current, {
        x: -part.offsetWidth,
        duration: speed,
        ease: 'none',
        repeat: -1,
      })
    }
    const t = setTimeout(setup, 50)
    return () => { clearTimeout(t); defaultAnimRef.current?.kill() }
  }, [text, reps, speed])

  const CircleArrow = () => (
    <svg className="inline-block mx-4 shrink-0" width="0.8em" height="0.8em" viewBox="0 0 48 48" fill="none">
      <circle cx="24" cy="24" r="22" stroke="currentColor" strokeWidth="3" />
      <path d="M20 16l10 8-10 8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )

  const renderStyledText = (t: string) => {
    const parts = t.split(/\s*>\s*/).filter(Boolean)
    return parts.map((word, j) => (
      <span key={j} className="inline-flex items-center group/word">
        <span className={`${j % 2 === 0 ? 'font-normal' : 'font-black'} relative after:absolute after:bottom-0 after:left-0 after:w-0 after:h-[3px] after:bg-current after:transition-all after:duration-300 group-hover/word:after:w-full`}>{word}</span>
        <CircleArrow />
      </span>
    ))
  }

  const marqueeParts = [...Array(reps)].map((_, i) => (
    <div className="marquee-part flex items-center shrink-0" key={i}>
      <span className={`whitespace-nowrap font-title ${fontSize || 'text-xl md:text-2xl'} px-[2vw] tracking-wider`} style={{ transform: 'scaleY(1.3)', transformOrigin: 'center' }}>{renderStyledText(text)}</span>
      {image && (
        <div className="w-[120px] h-[40px] mx-[1vw] rounded-full bg-cover bg-center" style={{ backgroundImage: `url(${image})` }} />
      )}
    </div>
  ))

  return (
    <div
      ref={itemRef}
      className="relative overflow-hidden"
      style={{ borderTop: isFirst ? 'none' : `1px solid ${borderColor}`, borderBottom: `1px solid ${borderColor}` }}
    >
      {/* 자동 스크롤 텍스트 */}
      <div className={`${padding || 'py-4 md:py-5'} overflow-hidden`}>
        <div className="w-fit flex" ref={defaultInnerRef} style={{ color: textColor }}>
          {marqueeParts}
        </div>
      </div>
    </div>
  )
}
