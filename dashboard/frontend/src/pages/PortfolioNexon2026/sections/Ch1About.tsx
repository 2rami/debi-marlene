import { CSSProperties, useEffect, useRef } from 'react'
import { motion, MotionValue, useScroll, useTransform } from 'framer-motion'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { C, FONT_BODY, FONT_DISPLAY, FONT_MONO } from '../shared/colors'
import { STATS } from '../content/llm'
import { useRevealOff } from '../shared/useRevealOff'

gsap.registerPlugin(ScrollTrigger)

/**
 * CH 1 — WHO (01 ABOUT + 02 DETAILS 통합 핀 슬라이드)
 *
 * 좌: CH 라벨 · 타이틀 · lede · STATS (sticky 동안 고정)
 * 우: 6개 포인트 카드 stack — 현재 카드 + 다음 카드 미리보기 (스크롤 진행이 카드 전환 구동)
 * 후속: pull quote (직무 연결, 자연 스크롤)
 */

const POINTS = [
  { k: 'SCALE',  t: '158 Discord 서버',     d: '9개월간 라이브 운영' },
  { k: 'AGENT',  t: '2-tier StateGraph',    d: 'LangGraph + Anthropic Managed Agents (claude-haiku-4-5)' },
  { k: 'TOOLS',  t: 'Custom tool 자율 판단', d: '네이티브 UI post · 패치노트 RAG' },
  { k: 'VOICE',  t: '음성 실시간 파이프라인',  d: 'DAVE → VAD → Qwen3.5-Omni → CosyVoice3' },
  { k: 'METRIC', t: '매일 정량/정성 검증',   d: '톤 일관성 · 환각률 · 비용' },
  { k: 'OPS',    t: '모델·프롬프트 회전',    d: 'few-shot · 세션 정책 변경 추적' },
] as const

export default function Ch1About() {
  const revealOff = useRevealOff()
  const containerRef = useRef<HTMLDivElement>(null)

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  })

  // 슬라이드용 progress — INTRO_FRAC 이후를 [0, 1] 로 remap.
  const slideProgress = useTransform(scrollYProgress, [INTRO_FRAC, 1], [0, 1])

  if (revealOff) return <Ch1Static />

  const N = POINTS.length
  const M = N + 1 // 카드 N장 + 마지막 pull quote 1장

  return (
    <section id="about" style={{ background: C.bgWhite, position: 'relative' }}>
      {/* 핀 슬라이드 영역 — outer 가 스크롤 길이를 만들고, inner 가 sticky */}
      <div
        ref={containerRef}
        style={{
          height: `${M * 450}vh`,
          position: 'relative',
        }}
      >
        <div
          style={{
            position: 'sticky',
            top: 0,
            height: '100vh',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: 1320,
              margin: '0 auto',
              padding: '0 clamp(40px, 6vw, 120px)',
              display: 'grid',
              gridTemplateColumns: 'minmax(0, 0.95fr) minmax(0, 1.05fr)',
              gap: 'clamp(40px, 5vw, 88px)',
              alignItems: 'center',
            }}
          >
            <LeftIntro triggerRef={containerRef} />
            <CardStack triggerRef={containerRef} slideProgress={slideProgress} />
          </div>

          <ProgressBar
            scrollYProgress={scrollYProgress}
            slideProgress={slideProgress}
            count={M}
            containerRef={containerRef}
          />
        </div>
      </div>
    </section>
  )
}

function LeftIntro({ triggerRef }: { triggerRef: React.RefObject<HTMLDivElement | null> }) {
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const root = rootRef.current
    const trigger = triggerRef.current
    if (!root || !trigger) return

    const ctx = gsap.context(() => {
      const labelChars = root.querySelectorAll<HTMLElement>('[data-anim="label"] .ch')
      const titleWords = root.querySelectorAll<HTMLElement>('[data-anim="title"] .word')
      const ledeWords = root.querySelectorAll<HTMLElement>('[data-anim="lede"] .word')
      const statBars = root.querySelectorAll<HTMLElement>('[data-anim="stat-bar"]')
      const statValues = root.querySelectorAll<HTMLElement>('[data-anim="stat-value"]')
      const statMeta = root.querySelectorAll<HTMLElement>('[data-anim="stat-meta"]')

      // 초기 상태
      gsap.set(labelChars, { opacity: 0, y: -10 })
      gsap.set(titleWords, { opacity: 0, y: 48, clipPath: 'inset(0 0 100% 0)' })
      gsap.set(ledeWords, { opacity: 0, filter: 'blur(8px)', y: 14 })
      gsap.set(statBars, { scaleX: 0, transformOrigin: 'left center' })
      gsap.set(statMeta, { opacity: 0, y: 12 })

      // scrub timeline — 핀 outer container 를 trigger 로.
      // start: 'top 70%' (섹션이 viewport 70% 지점 도달 — 등장 시작)
      // end: start 시점부터 1.5 viewport 더 스크롤 — 카드 2번 보일 즈음 완료.
      // (핀 engage 후에도 container 의 top 은 위로 계속 올라가므로 scrub 가능)
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger,
          start: 'top 70%',
          end: () => '+=' + window.innerHeight * 1.5,
          scrub: 0.8,
          invalidateOnRefresh: true,
        },
        defaults: { ease: 'power2.out' },
      })

      tl.to(labelChars, { opacity: 1, y: 0, stagger: 0.04, duration: 0.4 }, 0)
        .to(
          titleWords,
          { opacity: 1, y: 0, clipPath: 'inset(0 0 0% 0)', duration: 1, stagger: 0.12 },
          0.1,
        )
        .to(
          ledeWords,
          { opacity: 1, filter: 'blur(0px)', y: 0, duration: 0.7, stagger: 0.025 },
          0.5,
        )
        .to(statBars, { scaleX: 1, duration: 0.6, stagger: 0.1, ease: 'power2.inOut' }, 0.7)
        .to(statMeta, { opacity: 1, y: 0, duration: 0.5, stagger: 0.1 }, 0.78)

      // count-up — scrub 가능하도록 timeline child tween. 0 → target 값.
      statValues.forEach((el) => {
        const target = parseFloat(el.dataset.value || '0')
        const decimals = (el.dataset.value || '').includes('.') ? 1 : 0
        const proxy = { v: 0 }
        tl.to(
          proxy,
          {
            v: target,
            duration: 1.4,
            ease: 'power2.out',
            onUpdate: () => {
              el.textContent = proxy.v.toFixed(decimals)
            },
          },
          0.65,
        )
      })
    }, root)

    // Lenis/폰트 로드 race 회피 — 마운트 직후 한 번 + 100ms 후 한 번 더 refresh
    ScrollTrigger.refresh()
    const refreshId = window.setTimeout(() => ScrollTrigger.refresh(), 100)

    return () => {
      window.clearTimeout(refreshId)
      ctx.revert()
    }
  }, [])

  return (
    <div ref={rootRef} style={{ display: 'flex', flexDirection: 'column', gap: 24, minWidth: 0 }}>
      <AnimatedLabel ch="CH 1" no="01—02" kicker="WHO · ABOUT" />

      <h2
        data-anim="title"
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 'clamp(30px, 3.6vw, 48px)',
          fontWeight: 800,
          lineHeight: 1.12,
          letterSpacing: '-0.028em',
          color: C.ink,
          margin: 0,
          wordBreak: 'keep-all',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.25em',
        }}
      >
        {'저는 이런 사람입니다'.split(' ').map((w, i) => (
          <span key={i} className="word" style={{ display: 'inline-block', willChange: 'transform, opacity, clip-path' }}>
            {w}
          </span>
        ))}
      </h2>

      <p
        data-anim="lede"
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 'clamp(15px, 1.4vw, 19px)',
          lineHeight: 1.55,
          fontWeight: 600,
          color: C.inkSoft,
          margin: 0,
          letterSpacing: '-0.018em',
          maxWidth: 480,
          wordBreak: 'keep-all',
        }}
      >
        <LedeText />
      </p>

      <StatStripe />
    </div>
  )
}

function LedeText() {
  // 단어 단위 split — 색상 강조 단어("LLM 평가 어시스턴트")는 별도 묶음
  const parts: Array<{ text: string; accent?: boolean }> = [
    { text: '게임 사용자의 도메인 깊이와 LLM 운영자의 평가 감각이 결합된 지점, 그것이' },
    { text: 'LLM 평가 어시스턴트', accent: true },
    { text: '직무의 본질입니다.' },
  ]

  let key = 0
  return (
    <>
      {parts.map((p, idx) =>
        p.accent ? (
          <span key={idx}>
            {' '}
            <span
              className="word"
              style={{
                display: 'inline-block',
                color: C.nexonBlue,
                fontWeight: 700,
                willChange: 'transform, opacity, filter',
              }}
            >
              {p.text}
            </span>{' '}
          </span>
        ) : (
          <span key={idx}>
            {p.text.split(' ').map((w) => (
              <span
                key={key++}
                className="word"
                style={{ display: 'inline-block', marginRight: '0.25em', willChange: 'transform, opacity, filter' }}
              >
                {w}
              </span>
            ))}
          </span>
        ),
      )}
    </>
  )
}

function AnimatedLabel({ ch, no, kicker }: { ch: string; no: string; kicker: string }) {
  const labelStyle: CSSProperties = {
    fontFamily: FONT_BODY,
    fontSize: 11,
    fontWeight: 800,
    letterSpacing: '0.22em',
    textTransform: 'uppercase',
  }
  const line = `${ch} · ${no}`
  return (
    <div data-anim="label">
      <div style={{ ...labelStyle, color: C.nexonBlue, marginBottom: 4 }}>
        {line.split('').map((c, i) => (
          <span key={i} className="ch" style={{ display: 'inline-block', willChange: 'transform, opacity' }}>
            {c === ' ' ? ' ' : c}
          </span>
        ))}
      </div>
      <div style={{ ...labelStyle, color: C.inkMuted }}>
        {kicker.split('').map((c, i) => (
          <span key={i} className="ch" style={{ display: 'inline-block', willChange: 'transform, opacity' }}>
            {c === ' ' ? ' ' : c}
          </span>
        ))}
      </div>
    </div>
  )
}

function StatStripe() {
  return (
    <div
      style={{
        marginTop: 8,
        display: 'grid',
        gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
        gap: 14,
      }}
    >
      {STATS.map((s, i) => {
        const isNumeric = /^\d+(\.\d+)?$/.test(s.value)
        return (
          <div
            key={s.label}
            style={{
              position: 'relative',
              paddingTop: 12,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            {/* 상단 border — scaleX 0 → 1 등장 */}
            <div
              data-anim="stat-bar"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: 2,
                background: i === 0 ? C.nexonBlue : C.ink,
                opacity: i === 0 ? 1 : 0.85,
              }}
            />
            <div
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 'clamp(20px, 2.2vw, 28px)',
                fontWeight: 800,
                lineHeight: 1,
                color: C.ink,
                fontVariantNumeric: 'tabular-nums',
                letterSpacing: '-0.025em',
              }}
            >
              {isNumeric ? (
                <span data-anim="stat-value" data-value={s.value}>
                  0
                </span>
              ) : (
                s.value
              )}
              {s.unit && (
                <span style={{ fontSize: '0.5em', fontWeight: 700, marginLeft: 3, color: C.inkMuted }}>
                  {s.unit}
                </span>
              )}
            </div>
            <div
              data-anim="stat-meta"
              style={{ fontSize: 12, fontWeight: 700, color: C.ink, letterSpacing: '-0.005em' }}
            >
              {s.label}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// 좌측 인트로 완료 + 카드 fade-in 까지 끝난 뒤에야 slideshow 시작.
// fade-in: scrollYProgress ≈ 0.115 ~ 0.169 (top-=0.85vh ~ 1.25vh, 컨테이너 = 7.4 viewport).
// INTRO_FRAC 이후 구간에서 카드 transitions 진행.
const INTRO_FRAC = 0.17

// 카드/인디케이터 공통 timing — 인접 transition 안 겹치게 2*HOLD + TRANS = 1.0 (slot 단위)
const HOLD_HALF_FRAC = 0.35
const TRANS_FRAC = 0.3

function CardStack({
  triggerRef,
  slideProgress,
}: {
  triggerRef: React.RefObject<HTMLDivElement | null>
  slideProgress: MotionValue<number>
}) {
  const N = POINTS.length
  const M = N + 1 // 카드 + quote
  const stackRef = useRef<HTMLDivElement>(null)

  // 좌측 인트로 (top 70% → +1.5vh) 끝난 직후 fade-in.
  // GSAP scrub 으로 LeftIntro 와 같은 trigger 사용.
  useEffect(() => {
    if (typeof window === 'undefined') return
    const stack = stackRef.current
    const trigger = triggerRef.current
    if (!stack || !trigger) return

    const ctx = gsap.context(() => {
      gsap.set(stack, { opacity: 0, y: 40 })
      gsap.to(stack, {
        opacity: 1,
        y: 0,
        ease: 'power2.out',
        scrollTrigger: {
          trigger,
          // intro 완료 시점부터 시작 → 0.4 viewport 동안 fade-in
          start: () => 'top top-=' + window.innerHeight * 0.85,
          end: () => 'top top-=' + window.innerHeight * 1.25,
          scrub: 0.6,
          invalidateOnRefresh: true,
        },
      })
    })

    const refreshId = window.setTimeout(() => ScrollTrigger.refresh(), 100)
    return () => {
      window.clearTimeout(refreshId)
      ctx.revert()
    }
  }, [triggerRef])

  return (
    <div
      ref={stackRef}
      style={{
        position: 'relative',
        width: '100%',
        height: 'clamp(380px, 56vh, 460px)',
        willChange: 'transform, opacity',
      }}
    >
      {POINTS.map((p, i) => (
        <PointCard
          key={p.k}
          i={i}
          m={M}
          point={p}
          scrollYProgress={slideProgress}
        />
      ))}

      {/* 마지막 슬라이드 — 카드들 다 빠진 자리에 pull quote */}
      <QuoteSlide i={N} m={M} scrollYProgress={slideProgress} />
    </div>
  )
}

function PointCard({
  i,
  m,
  point,
  scrollYProgress,
}: {
  i: number
  m: number
  point: { k: string; t: string; d: string }
  scrollYProgress: MotionValue<number>
}) {
  // hold 구간 포함 piecewise t — 카드가 화면에 "혼자" 머무르는 시간 확보.
  // rel: scroll progress 와 카드 center 의 차.
  //   < -HOLD_HALF-TRANS : invisible (t=-1, opacity 0)
  //   ∈ [-HOLD_HALF-TRANS, -HOLD_HALF] : enter (t: -1 → 0)
  //   ∈ [-HOLD_HALF, +HOLD_HALF] : hold (t=0, full opacity)
  //   ∈ [+HOLD_HALF, +HOLD_HALF+TRANS] : exit (t: 0 → 1)
  //   > +HOLD_HALF+TRANS : gone (t=1, opacity 0)
  const t = useTransform(scrollYProgress, (p) => {
    // 슬롯을 1/m 로 정의 — 마지막 quote 가 슬롯 끝에 도달한 뒤에도 추가 스크롤 동안
    // 화면에 머물 수 있도록 한 슬롯 분량의 tail buffer 확보 (slideProgress=1 까지 hold).
    const slot = 1 / m
    const center = i * slot
    // 인접 카드 transition 이 겹치지 않도록 2*HOLD_HALF + TRANS = slot 로 셋업.
    // → 카드 i hold 동안 카드 i+1 은 완전 invisible. 진짜 "머무름" 구간 생김.
    const HOLD_HALF = HOLD_HALF_FRAC * slot
    const TRANS = TRANS_FRAC * slot
    const rel = p - center
    if (rel < -HOLD_HALF - TRANS) return -1
    if (rel < -HOLD_HALF) return (rel + HOLD_HALF) / TRANS
    if (rel <= HOLD_HALF) return 0
    if (rel <= HOLD_HALF + TRANS) return (rel - HOLD_HALF) / TRANS
    return 1
  })

  // preview 가 미리 보이지 않도록 t=-1 일 때 opacity 0 (이전 design 의 0.45 제거)
  const opacity = useTransform(t, [-1.01, -1, 0, 1, 1.01], [0, 0, 1, 0, 0])
  const x = useTransform(t, [-1, 0, 1], [90, 0, 0])
  const y = useTransform(t, [-1, 0, 1], [80, 0, -120])
  const scale = useTransform(t, [-1, 0, 1], [0.78, 1, 0.88])
  const zIndex = useTransform(t, (v) => Math.round(100 - Math.abs(v) * 20))
  const filter = useTransform(t, [-1, 0], ['blur(4px)', 'blur(0px)'])
  const indexLabel = String(i + 1).padStart(2, '0')

  return (
    <motion.article
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        x,
        y,
        scale,
        zIndex,
        filter,
        background: C.bgWhite,
        borderRadius: 28,
        border: `1px solid ${C.cardBorder}`,
        boxShadow: '0 24px 60px rgba(10, 18, 36, 0.10)',
        padding: 'clamp(28px, 3vw, 44px)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        gap: 24,
        willChange: 'transform, opacity',
        transformOrigin: 'center bottom',
      }}
    >
      {/* 상단 — 큰 인덱스 + 키워드 */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            letterSpacing: '0.24em',
            color: C.nexonBlue,
            fontWeight: 800,
          }}
        >
          POINT · {point.k}
        </div>
        <div
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(56px, 7vw, 88px)',
            fontWeight: 900,
            lineHeight: 0.85,
            color: C.nexonBlue,
            letterSpacing: '-0.04em',
            fontVariantNumeric: 'tabular-nums',
            opacity: 0.18,
            marginTop: -6,
          }}
        >
          {indexLabel}
        </div>
      </header>

      {/* 본문 — 큰 헤드라인 + 보조 설명 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <h3
          style={{
            margin: 0,
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(28px, 3.2vw, 42px)',
            fontWeight: 800,
            lineHeight: 1.18,
            letterSpacing: '-0.025em',
            color: C.ink,
            wordBreak: 'keep-all',
          }}
        >
          {point.t}
        </h3>
        <p
          style={{
            margin: 0,
            fontFamily: FONT_BODY,
            fontSize: 'clamp(15px, 1.3vw, 18px)',
            lineHeight: 1.55,
            color: C.inkSoft,
            fontWeight: 500,
            wordBreak: 'keep-all',
            maxWidth: 540,
          }}
        >
          {point.d}
        </p>
      </div>

    </motion.article>
  )
}

function QuoteSlide({
  i,
  m,
  scrollYProgress,
}: {
  i: number
  m: number
  scrollYProgress: MotionValue<number>
}) {
  // PointCard 와 같은 piecewise t — preview 미노출 + hold 구간 확보. exit 없음.
  const t = useTransform(scrollYProgress, (p) => {
    // 슬롯을 1/m 로 정의 — 마지막 quote 가 슬롯 끝에 도달한 뒤에도 추가 스크롤 동안
    // 화면에 머물 수 있도록 한 슬롯 분량의 tail buffer 확보 (slideProgress=1 까지 hold).
    const slot = 1 / m
    const center = i * slot
    // 인접 카드 transition 이 겹치지 않도록 2*HOLD_HALF + TRANS = slot 로 셋업.
    // → 카드 i hold 동안 카드 i+1 은 완전 invisible. 진짜 "머무름" 구간 생김.
    const HOLD_HALF = HOLD_HALF_FRAC * slot
    const TRANS = TRANS_FRAC * slot
    const rel = p - center
    if (rel < -HOLD_HALF - TRANS) return -1
    if (rel < -HOLD_HALF) return (rel + HOLD_HALF) / TRANS
    return 0
  })
  const opacity = useTransform(t, [-1.01, -1, 0], [0, 0, 1])
  const y = useTransform(t, [-1, 0], [120, 0])
  const scale = useTransform(t, [-1, 0], [0.85, 1])
  const zIndex = useTransform(t, (v) => Math.round(100 - Math.abs(v) * 20))

  return (
    <motion.div
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        y,
        scale,
        zIndex,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: 'clamp(28px, 3vw, 44px) clamp(12px, 1.5vw, 24px)',
        willChange: 'transform, opacity',
      }}
    >
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          letterSpacing: '0.24em',
          color: C.nexonBlue,
          fontWeight: 800,
          marginBottom: 24,
        }}
      >
        SO — 결론
      </div>

      <blockquote
        style={{
          margin: 0,
          paddingTop: 28,
          borderTop: `2px solid ${C.ink}`,
        }}
      >
        <p
          style={{
            margin: 0,
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(26px, 3vw, 38px)',
            lineHeight: 1.32,
            fontWeight: 800,
            letterSpacing: '-0.025em',
            color: C.ink,
            wordBreak: 'keep-all',
          }}
        >
          이 라이브 검증 경험을 게임 도메인의{' '}
          <span style={{ color: C.nexonBlue }}>LLM 평가 직무</span>로
          <br />
          그대로 이어 가고 싶습니다.
        </p>
      </blockquote>
    </motion.div>
  )
}


function ProgressBar({
  scrollYProgress,
  slideProgress,
  count,
  containerRef,
}: {
  scrollYProgress: MotionValue<number>
  slideProgress: MotionValue<number>
  count: number
  containerRef: React.RefObject<HTMLDivElement | null>
}) {
  const goTo = (i: number) => {
    if (typeof window === 'undefined') return
    const container = containerRef.current
    if (!container) return
    // 카드 i center = i / count (slot = 1/count, center at i*slot).
    // scrollYProgress 로 변환: INTRO_FRAC + slideTarget * (1 - INTRO_FRAC)
    const slideTarget = i / count
    const sypTarget = INTRO_FRAC + slideTarget * (1 - INTRO_FRAC)
    const targetY = container.offsetTop + sypTarget * (container.offsetHeight - window.innerHeight)
    const lenis = (window as { __lenis?: { scrollTo: (y: number, opts?: object) => void } }).__lenis
    if (lenis?.scrollTo) {
      lenis.scrollTo(targetY, { duration: 1.4 })
    } else {
      window.scrollTo({ top: targetY, behavior: 'smooth' })
    }
  }

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 'clamp(32px, 5vh, 56px)',
        left: 'clamp(40px, 6vw, 120px)',
        right: 'clamp(40px, 6vw, 120px)',
      }}
    >
      {/* 연속 progress bar — 첫 스크롤부터 즉각 반응 */}
      <div
        style={{
          position: 'relative',
          height: 4,
          background: 'rgba(10,18,36,0.08)',
          borderRadius: 2,
          overflow: 'visible',
        }}
      >
        {/* fill — 핀 engage 즉시 0 부터 채워짐 (scrollYProgress 기준) */}
        <motion.div
          style={{
            position: 'absolute',
            inset: 0,
            background: C.nexonBlue,
            borderRadius: 2,
            transformOrigin: 'left center',
            scaleX: scrollYProgress,
          }}
        />

        {/* 클릭 가능한 tick — 각 카드 center 위치(scrollYProgress 좌표)에 배치 */}
        {Array.from({ length: count }).map((_, i) => (
          <IndicatorTick
            key={i}
            index={i}
            count={count}
            slideProgress={slideProgress}
            onClick={() => goTo(i)}
          />
        ))}
      </div>
    </div>
  )
}

function IndicatorTick({
  index,
  count,
  slideProgress,
  onClick,
}: {
  index: number
  count: number
  slideProgress: MotionValue<number>
  onClick: () => void
}) {
  // 카드 i 가 가까울수록(=현재 active) tick 강조
  const distance = useTransform(slideProgress, (p) => Math.abs(p * count - index))
  const dotScale = useTransform(distance, [0, 0.5, 1.2], [1.6, 1.0, 0.8])
  const dotOpacity = useTransform(distance, [0, 0.5, 1.2], [1, 0.7, 0.45])
  // tick 가로 위치 — scrollYProgress 좌표계 (bar 와 일치).
  // 카드 i center 의 scrollYProgress = INTRO_FRAC + (i/count) * (1 - INTRO_FRAC)
  const leftPercent = (INTRO_FRAC + (index / count) * (1 - INTRO_FRAC)) * 100

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Slide ${index + 1} 으로 이동`}
      style={{
        position: 'absolute',
        top: '50%',
        left: `${leftPercent}%`,
        transform: 'translate(-50%, -50%)',
        width: 18,
        height: 18,
        background: 'transparent',
        border: 'none',
        padding: 0,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <motion.div
        style={{
          width: 10,
          height: 10,
          borderRadius: '50%',
          background: C.bgWhite,
          border: `2px solid ${C.nexonBlue}`,
          scale: dotScale,
          opacity: dotOpacity,
        }}
      />
    </button>
  )
}

function StickyLabel({ ch, no, kicker }: { ch: string; no: string; kicker: string }) {
  const labelStyle: CSSProperties = {
    fontFamily: FONT_BODY,
    fontSize: 11,
    fontWeight: 800,
    letterSpacing: '0.22em',
    textTransform: 'uppercase',
  }
  return (
    <div>
      <div style={{ ...labelStyle, color: C.nexonBlue, marginBottom: 4 }}>
        {ch} · {no}
      </div>
      <div style={{ ...labelStyle, color: C.inkMuted }}>{kicker}</div>
    </div>
  )
}

/** ?reveal=off — 정적 캡처용 fallback. 슬라이드 비활성, 모든 카드 그리드로 표시 */
function Ch1Static() {
  return (
    <section id="about" style={{ background: C.bgWhite, padding: '110px clamp(40px, 6vw, 120px)' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 48 }}>
        <StickyLabel ch="CH 1" no="01—02" kicker="WHO · ABOUT" />
        <h2 style={{ fontFamily: FONT_DISPLAY, fontSize: 44, fontWeight: 800, margin: 0 }}>저는 이런 사람입니다</h2>
        <StatStripe />
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: 24,
          }}
        >
          {POINTS.map((p) => (
            <div
              key={p.k}
              style={{
                padding: 24,
                border: `1px solid ${C.cardBorder}`,
                borderRadius: 18,
                background: C.bgWhite,
              }}
            >
              <div style={{ fontSize: 11, letterSpacing: '0.22em', color: C.nexonBlue, fontWeight: 800 }}>
                {p.k}
              </div>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: 20, fontWeight: 700, marginTop: 8 }}>
                {p.t}
              </div>
              <div style={{ fontSize: 14, color: C.inkSoft, marginTop: 6 }}>{p.d}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
