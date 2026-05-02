import { CSSProperties, MouseEvent, ReactNode } from 'react'
import { C, FONT_BODY } from './colors'

type Variant = 'primary' | 'outline' | 'ghost'
type Size = 'sm' | 'md'

interface Props {
  href: string
  label: ReactNode
  variant?: Variant
  size?: Size
  external?: boolean
  arrow?: boolean
  style?: CSSProperties
  inverse?: boolean // 다크 bg 위에서 inverse 색상
}

export default function Button({
  href,
  label,
  variant = 'outline',
  size = 'md',
  external,
  arrow = true,
  style,
  inverse = false,
}: Props) {
  const isExternal = external ?? href.startsWith('http')

  const baseColor = inverse ? '#FFFFFF' : C.nexonBlue
  const hoverFill = inverse ? '#FFFFFF' : C.nexonBlue
  const hoverText = inverse ? C.nexonBlue : '#FFFFFF'

  const sizing =
    size === 'sm'
      ? { padding: '7px 14px', fontSize: 11 }
      : { padding: '12px 22px', fontSize: 13 }

  const variants: Record<Variant, CSSProperties> = {
    primary: {
      background: baseColor,
      color: inverse ? C.nexonBlue : '#FFFFFF',
      border: `1px solid ${baseColor}`,
    },
    outline: {
      background: 'transparent',
      color: baseColor,
      border: `1px solid ${baseColor}`,
    },
    ghost: {
      background: 'transparent',
      color: baseColor,
      border: '1px solid transparent',
      padding: size === 'sm' ? '6px 4px' : '10px 4px',
    },
  }

  function onEnter(e: MouseEvent<HTMLAnchorElement>) {
    if (variant === 'ghost') {
      e.currentTarget.style.opacity = '0.6'
      return
    }
    if (variant === 'outline') {
      e.currentTarget.style.background = hoverFill
      e.currentTarget.style.color = hoverText
    } else {
      e.currentTarget.style.opacity = '0.85'
    }
  }
  function onLeave(e: MouseEvent<HTMLAnchorElement>) {
    if (variant === 'ghost') {
      e.currentTarget.style.opacity = '1'
      return
    }
    if (variant === 'outline') {
      e.currentTarget.style.background = 'transparent'
      e.currentTarget.style.color = baseColor
    } else {
      e.currentTarget.style.opacity = '1'
    }
  }

  return (
    <a
      href={href}
      target={isExternal ? '_blank' : undefined}
      rel={isExternal ? 'noopener noreferrer' : undefined}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        borderRadius: 999,
        fontFamily: FONT_BODY,
        fontWeight: 700,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        textDecoration: 'none',
        whiteSpace: 'nowrap',
        transition: 'background 200ms ease, color 200ms ease, opacity 200ms ease',
        ...sizing,
        ...variants[variant],
        ...style,
      }}
    >
      {label}
      {arrow && <span style={{ fontSize: '0.95em', opacity: 0.8 }}>↗</span>}
    </a>
  )
}
