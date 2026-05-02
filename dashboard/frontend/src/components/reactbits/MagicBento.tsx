import React, { useRef, useEffect, useState, useCallback } from 'react'
import { gsap } from 'gsap'

export interface BentoItem {
  label: string
  title: string
  description: string
  color?: string
  span?: { col?: number; row?: number }
}

interface MagicBentoProps {
  items: BentoItem[]
  glowColor?: string
  spotlightRadius?: number
  enableSpotlight?: boolean
  enableBorderGlow?: boolean
  enableMagnetism?: boolean
}

const DEFAULT_GLOW = '0, 145, 204'
const MOBILE = 768

const updateGlow = (card: HTMLElement, mouseX: number, mouseY: number, intensity: number, radius: number) => {
  const rect = card.getBoundingClientRect()
  const x = ((mouseX - rect.left) / rect.width) * 100
  const y = ((mouseY - rect.top) / rect.height) * 100
  card.style.setProperty('--glow-x', `${x}%`)
  card.style.setProperty('--glow-y', `${y}%`)
  card.style.setProperty('--glow-intensity', String(intensity))
  card.style.setProperty('--glow-radius', `${radius}px`)
}

const GlobalSpotlight: React.FC<{
  gridRef: React.RefObject<HTMLDivElement | null>
  enabled: boolean
  spotlightRadius: number
  glowColor: string
}> = ({ gridRef, enabled, spotlightRadius, glowColor }) => {
  const spotlightRef = useRef<HTMLDivElement | null>(null)
  useEffect(() => {
    if (!enabled || !gridRef.current) return
    const spot = document.createElement('div')
    spot.className = 'magic-bento-spotlight'
    spot.style.cssText = `
      position: fixed;
      width: 700px;
      height: 700px;
      border-radius: 50%;
      pointer-events: none;
      background: radial-gradient(circle, rgba(${glowColor}, 0.18) 0%, rgba(${glowColor}, 0.08) 25%, rgba(${glowColor}, 0.03) 50%, transparent 70%);
      z-index: 200;
      opacity: 0;
      transform: translate(-50%, -50%);
      mix-blend-mode: screen;
    `
    document.body.appendChild(spot)
    spotlightRef.current = spot

    const proximity = spotlightRadius * 0.5
    const fadeDistance = spotlightRadius * 0.75

    const onMove = (e: MouseEvent) => {
      const grid = gridRef.current
      if (!grid || !spotlightRef.current) return
      const gridRect = grid.getBoundingClientRect()
      const inside =
        e.clientX >= gridRect.left &&
        e.clientX <= gridRect.right &&
        e.clientY >= gridRect.top &&
        e.clientY <= gridRect.bottom
      const cards = grid.querySelectorAll<HTMLElement>('.bento-card')
      if (!inside) {
        gsap.to(spotlightRef.current, { opacity: 0, duration: 0.3 })
        cards.forEach((c) => c.style.setProperty('--glow-intensity', '0'))
        return
      }
      let minDistance = Infinity
      cards.forEach((c) => {
        const r = c.getBoundingClientRect()
        const cx = r.left + r.width / 2
        const cy = r.top + r.height / 2
        const d = Math.hypot(e.clientX - cx, e.clientY - cy) - Math.max(r.width, r.height) / 2
        const eff = Math.max(0, d)
        minDistance = Math.min(minDistance, eff)
        let glow = 0
        if (eff <= proximity) glow = 1
        else if (eff <= fadeDistance) glow = (fadeDistance - eff) / (fadeDistance - proximity)
        updateGlow(c, e.clientX, e.clientY, glow, spotlightRadius)
      })
      gsap.to(spotlightRef.current, { left: e.clientX, top: e.clientY, duration: 0.1, ease: 'power2.out' })
      const targetOpacity =
        minDistance <= proximity
          ? 0.8
          : minDistance <= fadeDistance
            ? ((fadeDistance - minDistance) / (fadeDistance - proximity)) * 0.8
            : 0
      gsap.to(spotlightRef.current, { opacity: targetOpacity, duration: 0.2 })
    }
    document.addEventListener('mousemove', onMove)
    return () => {
      document.removeEventListener('mousemove', onMove)
      spotlightRef.current?.parentNode?.removeChild(spotlightRef.current)
    }
  }, [enabled, gridRef, spotlightRadius, glowColor])
  return null
}

const useMobile = () => {
  const [m, set] = useState(false)
  useEffect(() => {
    const c = () => set(window.innerWidth <= MOBILE)
    c()
    window.addEventListener('resize', c)
    return () => window.removeEventListener('resize', c)
  }, [])
  return m
}

const MagicBento: React.FC<MagicBentoProps> = ({
  items,
  glowColor = DEFAULT_GLOW,
  spotlightRadius = 300,
  enableSpotlight = true,
  enableBorderGlow = true,
  enableMagnetism = true,
}) => {
  const gridRef = useRef<HTMLDivElement>(null)
  const isMobile = useMobile()

  const handleMouseMove = useCallback(
    (el: HTMLDivElement, e: React.MouseEvent) => {
      if (isMobile || !enableMagnetism) return
      const r = el.getBoundingClientRect()
      const x = e.clientX - r.left - r.width / 2
      const y = e.clientY - r.top - r.height / 2
      gsap.to(el, { x: x * 0.04, y: y * 0.04, duration: 0.3, ease: 'power2.out' })
    },
    [isMobile, enableMagnetism],
  )

  const handleMouseLeave = useCallback((el: HTMLDivElement) => {
    if (isMobile) return
    gsap.to(el, { x: 0, y: 0, duration: 0.4, ease: 'power2.out' })
  }, [isMobile])

  return (
    <>
      <style>{`
        .bento-grid {
          --glow-color: ${glowColor};
        }
        .bento-card {
          --glow-x: 50%;
          --glow-y: 50%;
          --glow-intensity: 0;
          --glow-radius: 200px;
          position: relative;
          overflow: hidden;
        }
        .bento-card.with-border-glow::after {
          content: '';
          position: absolute;
          inset: 0;
          padding: 2px;
          background: radial-gradient(var(--glow-radius) circle at var(--glow-x) var(--glow-y),
              rgba(${glowColor}, calc(var(--glow-intensity) * 0.9)) 0%,
              rgba(${glowColor}, calc(var(--glow-intensity) * 0.4)) 30%,
              transparent 60%);
          border-radius: inherit;
          -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          mask-composite: exclude;
          pointer-events: none;
          transition: opacity 0.3s ease;
          z-index: 1;
        }
      `}</style>
      {enableSpotlight && !isMobile && (
        <GlobalSpotlight
          gridRef={gridRef}
          enabled={enableSpotlight}
          spotlightRadius={spotlightRadius}
          glowColor={glowColor}
        />
      )}
      <div ref={gridRef} className="bento-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gridAutoRows: 'minmax(180px, auto)', gap: 16 }}>
        {items.map((item, i) => (
          <div
            key={i}
            className={`bento-card ${enableBorderGlow ? 'with-border-glow' : ''}`}
            onMouseMove={(e) => handleMouseMove(e.currentTarget, e)}
            onMouseLeave={(e) => handleMouseLeave(e.currentTarget)}
            style={{
              backgroundColor: item.color || '#0F1729',
              color: '#FFFFFF',
              borderRadius: 20,
              border: '1px solid rgba(255,255,255,0.08)',
              padding: '24px 28px',
              gridColumn: item.span?.col ? `span ${item.span.col}` : 'span 1',
              gridRow: item.span?.row ? `span ${item.span.row}` : 'span 1',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              minHeight: 180,
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
            }}
          >
            <div style={{ position: 'relative', zIndex: 2 }}>
              <span style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 11,
                letterSpacing: '0.18em',
                color: `rgba(${glowColor}, 1)`,
                fontWeight: 700,
                textTransform: 'uppercase',
              }}>
                {item.label}
              </span>
            </div>
            <div style={{ position: 'relative', zIndex: 2 }}>
              <h3 style={{
                fontSize: 'clamp(20px, 2vw, 28px)',
                fontWeight: 800,
                lineHeight: 1.25,
                margin: '0 0 8px',
                letterSpacing: '-0.015em',
              }}>
                {item.title}
              </h3>
              <p style={{
                fontSize: 13.5,
                lineHeight: 1.55,
                margin: 0,
                color: 'rgba(255,255,255,0.7)',
                fontWeight: 500,
              }}>
                {item.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </>
  )
}

export default MagicBento
