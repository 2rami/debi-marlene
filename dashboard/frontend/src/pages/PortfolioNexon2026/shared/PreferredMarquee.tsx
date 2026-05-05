import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { C, FONT_BODY, FONT_DISPLAY, FONT_MONO } from './colors'

interface Game {
  readonly title: string
  readonly period: string
  readonly detail: string
}

interface Props {
  games: readonly Game[]
}

/**
 * CH 3·06 PREFERRED — dual marquee.
 *
 * 위/아래 두 가로 띠가 서로 반대 방향으로 끝없이 흐름.
 * 스크롤 velocity 가 클수록 흐르는 속도 ↑ (Lenis 의 __lenis.velocity 사용)
 * idle 상태에서도 천천히 흐르고, 사용자가 빠르게 스크롤하면 부스트.
 */
export default function PreferredMarquee({ games }: Props) {
  const topInnerRef = useRef<HTMLDivElement>(null)
  const bottomInnerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const topEl = topInnerRef.current
    const botEl = bottomInnerRef.current
    if (!topEl || !botEl) return

    // 무한 스크롤 — 자식이 2배 복제돼있어 -50% 까지만 가면 다시 0% 로 잘못 점프 없이 loop
    const topAnim = gsap.to(topEl, {
      xPercent: -50,
      duration: 50, // 기본 속도 (느린 idle)
      ease: 'none',
      repeat: -1,
    })
    const botAnim = gsap.to(botEl, {
      xPercent: 50,
      duration: 50,
      ease: 'none',
      repeat: -1,
    })
    // bottom 은 -50% → 0 시작 (반대 방향)
    botAnim.totalTime(botAnim.duration() / 2)

    // Lenis velocity 따라 timescale 변동
    let raf = 0
    const tick = () => {
      const lenis = (window as { __lenis?: { velocity?: number } }).__lenis
      const v = Math.abs(lenis?.velocity ?? 0)
      // velocity 값이 보통 0~80 범위. 정상 idle 1, 빠르면 5~6 까지
      const boost = 1 + Math.min(6, v / 14)
      topAnim.timeScale(boost)
      botAnim.timeScale(boost)
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)

    return () => {
      cancelAnimationFrame(raf)
      topAnim.kill()
      botAnim.kill()
    }
  }, [])

  return (
    <section
      id="preferred"
      style={{
        position: 'relative',
        background: C.bgWhite,
        padding: 'clamp(80px, 10vh, 120px) 0',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          padding: '0 clamp(40px, 6vw, 120px)',
          maxWidth: 1280,
          margin: '0 auto 56px',
          display: 'flex',
          alignItems: 'baseline',
          gap: 16,
          flexWrap: 'wrap',
        }}
      >
        <span
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            fontWeight: 800,
            color: C.nexonBlue,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
          }}
        >
          CH 3 · 06
        </span>
        <span
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            fontWeight: 800,
            color: C.inkMuted,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
          }}
        >
          Preferred · 우대 사항
        </span>
        <span style={{ flex: 1, height: 1, background: C.cardBorder, minWidth: 60 }} />
        <h3
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(22px, 2.6vw, 32px)',
            fontWeight: 800,
            color: C.ink,
            margin: 0,
            letterSpacing: '-0.025em',
            wordBreak: 'keep-all',
            flexBasis: '100%',
          }}
        >
          MMORPG · FPS · 어드벤처 · 슈팅 · 수집형 — 5종 5장르
        </h3>
      </div>

      <MarqueeRow innerRef={topInnerRef} games={games} variant="title" />
      <div style={{ height: 24 }} />
      <MarqueeRow innerRef={bottomInnerRef} games={games} variant="detail" reverse />
    </section>
  )
}

// ─────────────────────────────────────────────

function MarqueeRow({
  innerRef,
  games,
  variant,
  reverse = false,
}: {
  innerRef: React.RefObject<HTMLDivElement | null>
  games: readonly Game[]
  variant: 'title' | 'detail'
  reverse?: boolean
}) {
  // 같은 리스트를 두 번 이어붙여 무한 loop 가능하게
  const items = [...games, ...games]
  return (
    <div style={{ overflow: 'hidden', width: '100%' }}>
      <div
        ref={innerRef}
        style={{
          display: 'flex',
          width: 'max-content',
          gap: variant === 'title' ? 'clamp(48px, 6vw, 96px)' : 'clamp(32px, 4vw, 64px)',
          // reverse row 는 처음부터 -50% 위치 — totalTime 으로 처리
          willChange: 'transform',
        }}
      >
        {items.map((g, i) => (
          <MarqueeItem key={`${g.title}-${i}`} game={g} variant={variant} reverse={reverse} />
        ))}
      </div>
    </div>
  )
}

function MarqueeItem({
  game,
  variant,
  reverse,
}: {
  game: Game
  variant: 'title' | 'detail'
  reverse: boolean
}) {
  void reverse
  if (variant === 'title') {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 24, whiteSpace: 'nowrap', flex: '0 0 auto' }}>
        <span
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(48px, 6.5vw, 84px)',
            fontWeight: 800,
            lineHeight: 1,
            color: C.ink,
            letterSpacing: '-0.04em',
          }}
        >
          {game.title}
        </span>
        <span
          aria-hidden
          style={{
            display: 'inline-block',
            width: 14,
            height: 14,
            borderRadius: '50%',
            background: C.nexonBlue,
          }}
        />
      </div>
    )
  }
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
        whiteSpace: 'nowrap',
        flex: '0 0 auto',
        paddingRight: 24,
        borderRight: `1px solid ${C.cardBorder}`,
      }}
    >
      <span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          letterSpacing: '0.22em',
          color: C.nexonBlue,
          fontWeight: 800,
          textTransform: 'uppercase',
        }}
      >
        {game.period}
      </span>
      <span
        style={{
          fontFamily: FONT_BODY,
          fontSize: 'clamp(14px, 1.15vw, 17px)',
          color: C.inkSoft,
          fontWeight: 500,
          letterSpacing: '-0.005em',
        }}
      >
        {game.detail}
      </span>
    </div>
  )
}
