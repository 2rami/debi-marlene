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
}

export default function FlowingMenu({
  items,
  speed = 12,
  textColor = '#374151',
  bgColor = 'transparent',
  hoverBgColor = '#3cabc9',
  hoverTextColor = '#fff',
  borderColor = '#e5e7eb',
  className = '',
}: FlowingMenuProps) {
  return (
    <div className={`w-full overflow-hidden ${className}`} style={{ backgroundColor: bgColor }}>
      <nav className="flex flex-col m-0 p-0">
        {items.map((item, idx) => (
          <FlowingRow
            key={idx}
            {...item}
            speed={speed}
            textColor={textColor}
            hoverBgColor={hoverBgColor}
            hoverTextColor={hoverTextColor}
            borderColor={borderColor}
            isFirst={idx === 0}
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
  hoverBgColor,
  hoverTextColor,
  borderColor,
  isFirst,
}: FlowingMenuItem & {
  speed: number
  textColor: string
  hoverBgColor: string
  hoverTextColor: string
  borderColor: string
  isFirst: boolean
}) {
  const itemRef = useRef<HTMLDivElement>(null)
  const marqueeRef = useRef<HTMLDivElement>(null)
  const marqueeInnerRef = useRef<HTMLDivElement>(null)
  const animationRef = useRef<gsap.core.Tween | null>(null)
  const [reps, setReps] = useState(6)

  const ease = { duration: 0.5, ease: 'expo' }

  const closestEdge = (mx: number, my: number, w: number, h: number) => {
    const top = mx * mx + my * my
    const bot = mx * mx + (my - h) * (my - h)
    return top < bot ? 'top' : 'bottom'
  }

  useEffect(() => {
    const calc = () => {
      if (!marqueeInnerRef.current) return
      const part = marqueeInnerRef.current.querySelector('.marquee-part') as HTMLElement
      if (!part) return
      setReps(Math.max(6, Math.ceil(window.innerWidth / part.offsetWidth) + 2))
    }
    calc()
    window.addEventListener('resize', calc)
    return () => window.removeEventListener('resize', calc)
  }, [text])

  useEffect(() => {
    const setup = () => {
      if (!marqueeInnerRef.current) return
      const part = marqueeInnerRef.current.querySelector('.marquee-part') as HTMLElement
      if (!part || part.offsetWidth === 0) return
      animationRef.current?.kill()
      animationRef.current = gsap.to(marqueeInnerRef.current, {
        x: -part.offsetWidth,
        duration: speed,
        ease: 'none',
        repeat: -1,
      })
    }
    const t = setTimeout(setup, 50)
    return () => { clearTimeout(t); animationRef.current?.kill() }
  }, [text, reps, speed])

  const onEnter = (ev: React.MouseEvent<HTMLDivElement>) => {
    if (!itemRef.current || !marqueeRef.current || !marqueeInnerRef.current) return
    const r = itemRef.current.getBoundingClientRect()
    const edge = closestEdge(ev.clientX - r.left - r.width / 2, ev.clientY - r.top, r.width, r.height)
    gsap.timeline({ defaults: ease })
      .set(marqueeRef.current, { y: edge === 'top' ? '-101%' : '101%' }, 0)
      .set(marqueeInnerRef.current, { y: edge === 'top' ? '101%' : '-101%' }, 0)
      .to([marqueeRef.current, marqueeInnerRef.current], { y: '0%' }, 0)
  }

  const onLeave = (ev: React.MouseEvent<HTMLDivElement>) => {
    if (!itemRef.current || !marqueeRef.current || !marqueeInnerRef.current) return
    const r = itemRef.current.getBoundingClientRect()
    const edge = closestEdge(ev.clientX - r.left - r.width / 2, ev.clientY - r.top, r.width, r.height)
    gsap.timeline({ defaults: ease })
      .to(marqueeRef.current, { y: edge === 'top' ? '-101%' : '101%' }, 0)
      .to(marqueeInnerRef.current, { y: edge === 'top' ? '101%' : '-101%' }, 0)
  }

  return (
    <div
      ref={itemRef}
      className="relative overflow-hidden"
      style={{ borderTop: isFirst ? 'none' : `1px solid ${borderColor}`, borderBottom: `1px solid ${borderColor}` }}
    >
      <div
        className="flex items-center justify-center py-4 md:py-5 cursor-pointer font-title text-xl md:text-2xl uppercase tracking-wider"
        onMouseEnter={onEnter}
        onMouseLeave={onLeave}
        style={{ color: textColor }}
      >
        {text}
      </div>

      <div
        ref={marqueeRef}
        className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none translate-y-[101%]"
        style={{ backgroundColor: hoverBgColor }}
      >
        <div className="h-full w-fit flex" ref={marqueeInnerRef}>
          {[...Array(reps)].map((_, i) => (
            <div className="marquee-part flex items-center shrink-0" key={i} style={{ color: hoverTextColor }}>
              <span className="whitespace-nowrap font-title text-xl md:text-2xl px-[2vw] tracking-wider">{text}</span>
              {image && (
                <div
                  className="w-[120px] h-[40px] mx-[1vw] rounded-full bg-cover bg-center"
                  style={{ backgroundImage: `url(${image})` }}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
