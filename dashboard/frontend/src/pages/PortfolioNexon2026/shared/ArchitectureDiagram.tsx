import { forwardRef, useRef, useState, useEffect } from 'react'
import { motion, useScroll, useTransform, useMotionValueEvent } from 'framer-motion'
import { AnimatedBeam } from '../../../components/magicui/animated-beam'
import { C, FONT_BODY, FONT_MONO, FONT_DISPLAY } from './colors'

type NodeProps = {
  label: string
  sub?: string
  active: boolean
  done: boolean
  variant?: 'primary' | 'branch' | 'terminal'
}

const NodeBox = forwardRef<HTMLDivElement, NodeProps>(function NodeBox(
  { label, sub, active, done, variant = 'primary' },
  ref,
) {
  const accent =
    variant === 'branch'
      ? '#FFD400'
      : variant === 'terminal'
        ? '#C4F000'
        : '#338AFA'

  return (
    <motion.div
      ref={ref}
      animate={{
        scale: active ? 1.06 : 1,
        boxShadow: active
          ? `0 0 0 1px ${accent}, 0 0 40px ${accent}66, 0 16px 48px rgba(0,0,0,0.4)`
          : done
            ? `0 0 0 1px ${accent}55, 0 8px 32px rgba(0,0,0,0.35)`
            : '0 0 0 1px rgba(255,255,255,0.08), 0 8px 24px rgba(0,0,0,0.3)',
      }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      style={{
        position: 'relative',
        zIndex: 2,
        background: active || done ? 'rgba(20, 28, 48, 0.92)' : 'rgba(20, 28, 48, 0.6)',
        backdropFilter: 'blur(8px)',
        border: '1px solid transparent',
        borderRadius: 14,
        padding: '14px 18px',
        minWidth: 140,
        maxWidth: 180,
        textAlign: 'center',
        whiteSpace: 'nowrap',
        opacity: active ? 1 : done ? 0.85 : 0.45,
      }}
    >
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 700,
          color: active ? accent : 'rgba(255,255,255,0.55)',
          letterSpacing: '0.12em',
          marginBottom: 4,
          textTransform: 'uppercase',
        }}
      >
        {label}
      </div>
      {sub && (
        <div
          style={{
            fontSize: 11,
            color: 'rgba(255,255,255,0.65)',
            fontFamily: FONT_BODY,
          }}
        >
          {sub}
        </div>
      )}
    </motion.div>
  )
})

type Step = {
  n: number
  label: string
  desc: string
  cost: string
}

export default function ArchitectureDiagram({
  steps,
  title,
}: {
  steps: readonly Step[]
  title: string
}) {
  const sectionRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const userRef = useRef<HTMLDivElement>(null)
  const classifyRef = useRef<HTMLDivElement>(null)
  const patchnoteRef = useRef<HTMLDivElement>(null)
  const memoryRef = useRef<HTMLDivElement>(null)
  const llmRef = useRef<HTMLDivElement>(null)
  const toolRef = useRef<HTMLDivElement>(null)

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start start', 'end end'],
  })

  // 0~5: USER → step1 → step2 → step3 → step4 → step5
  const activeFloat = useTransform(scrollYProgress, [0, 1], [0, 5])
  const [active, setActive] = useState(0)

  useMotionValueEvent(activeFloat, 'change', (v) => {
    const next = Math.min(5, Math.max(0, Math.round(v)))
    setActive(next)
  })

  // For caption: when active >= 1, show step (active - 1)
  const currentStep = active >= 1 ? steps[active - 1] : null

  // 노드 박스용 짧은 라벨 (step.label은 caption 용으로 길게 사용)
  const NODE_NAMES = ['classify_intent', 'fetch_patchnote', 'fetch_memory', 'call_llm', 'custom_tool']
  const shortName = (i: number) => NODE_NAMES[i] ?? steps[i].label

  // Visibility: this node is active or already passed
  const isActive = (i: number) => active === i
  const isDone = (i: number) => active > i

  return (
    <section
      ref={sectionRef}
      style={{
        position: 'relative',
        height: '220vh',
        background: C.bgLight,
        padding: '0 clamp(24px, 5vw, 80px)',
      }}
    >
      {/* dark inset card — 라이트 배경 위에 떠있는 다크 카드 */}
      <div
        aria-hidden
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: 'clamp(24px, 5vw, 80px)',
          right: 'clamp(24px, 5vw, 80px)',
          background: '#070B14',
          borderRadius: 32,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(60% 50% at 30% 30%, rgba(0, 98, 223, 0.18), transparent), radial-gradient(50% 40% at 80% 70%, rgba(138, 95, 255, 0.14), transparent)',
            pointerEvents: 'none',
          }}
        />
      </div>

      <div
        style={{
          position: 'sticky',
          top: 0,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          padding: '64px 48px 48px',
        }}
      >
        {/* Header */}
        <div style={{ maxWidth: 1280, margin: '0 auto', width: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 18 }}>
            <span
              style={{
                fontFamily: FONT_MONO,
                fontSize: 11,
                fontWeight: 700,
                color: C.nexonLightBlue,
                letterSpacing: '0.18em',
              }}
            >
              02
            </span>
            <span
              style={{
                fontFamily: FONT_MONO,
                fontSize: 11,
                fontWeight: 800,
                color: 'rgba(245, 250, 249, 0.65)',
                letterSpacing: '0.18em',
              }}
            >
              ARCHITECTURE · 입력 한 번에 일어나는 일
            </span>
            <span style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.18)' }} />
            <span
              style={{
                fontFamily: FONT_MONO,
                fontSize: 11,
                color: 'rgba(255,255,255,0.55)',
                letterSpacing: '0.08em',
              }}
            >
              {String(active).padStart(2, '0')} / 05
            </span>
          </div>
          <h2
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(28px, 3.6vw, 44px)',
              fontWeight: 700,
              lineHeight: 1.15,
              letterSpacing: '-0.025em',
              color: '#FFFFFF',
              margin: 0,
            }}
          >
            {title}
          </h2>
        </div>

        {/* Diagram canvas */}
        <div
          ref={containerRef}
          style={{
            position: 'relative',
            flex: 1,
            maxWidth: 1280,
            margin: '40px auto 0',
            width: '100%',
            minHeight: 280,
          }}
        >
          {/* USER */}
          <div
            style={{
              position: 'absolute',
              left: '8%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <NodeBox
              ref={userRef}
              label="USER"
              sub="Discord 입력"
              active={isActive(0)}
              done={isDone(0)}
              variant="terminal"
            />
          </div>

          {/* CLASSIFY */}
          <div
            style={{
              position: 'absolute',
              left: '28%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <NodeBox
              ref={classifyRef}
              label={shortName(0)}
              sub="regex 0.1ms"
              active={isActive(1)}
              done={isDone(1)}
            />
          </div>

          {/* PATCHNOTE (branch up) */}
          <div
            style={{
              position: 'absolute',
              left: '50%',
              top: '14%',
              transform: 'translate(-50%, 0)',
            }}
          >
            <NodeBox
              ref={patchnoteRef}
              label={shortName(1)}
              sub="patch intent only"
              active={isActive(2)}
              done={isDone(2)}
              variant="branch"
            />
          </div>

          {/* MEMORY */}
          <div
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <NodeBox
              ref={memoryRef}
              label={shortName(2)}
              sub="SQLite 영속"
              active={isActive(3)}
              done={isDone(3)}
            />
          </div>

          {/* LLM */}
          <div
            style={{
              position: 'absolute',
              left: '72%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <NodeBox
              ref={llmRef}
              label={shortName(3)}
              sub="claude-haiku-4-5"
              active={isActive(4)}
              done={isDone(4)}
            />
          </div>

          {/* TOOL */}
          <div
            style={{
              position: 'absolute',
              left: '92%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <NodeBox
              ref={toolRef}
              label={shortName(4)}
              sub="StatsLayoutView"
              active={isActive(5)}
              done={isDone(5)}
              variant="terminal"
            />
          </div>

          {/* Beams */}
          <AnimatedBeam
            containerRef={containerRef}
            fromRef={userRef}
            toRef={classifyRef}
            duration={3.5}
            gradientStartColor="#338AFA"
            gradientStopColor="#8A5FFF"
          />
          <AnimatedBeam
            containerRef={containerRef}
            fromRef={classifyRef}
            toRef={patchnoteRef}
            duration={3.5}
            curvature={-50}
            gradientStartColor="#FFD400"
            gradientStopColor="#FF9900"
          />
          <AnimatedBeam
            containerRef={containerRef}
            fromRef={classifyRef}
            toRef={memoryRef}
            duration={3.5}
            gradientStartColor="#338AFA"
            gradientStopColor="#8A5FFF"
          />
          <AnimatedBeam
            containerRef={containerRef}
            fromRef={patchnoteRef}
            toRef={memoryRef}
            duration={3.5}
            curvature={50}
            gradientStartColor="#FFD400"
            gradientStopColor="#338AFA"
          />
          <AnimatedBeam
            containerRef={containerRef}
            fromRef={memoryRef}
            toRef={llmRef}
            duration={3.5}
            gradientStartColor="#338AFA"
            gradientStopColor="#8A5FFF"
          />
          <AnimatedBeam
            containerRef={containerRef}
            fromRef={llmRef}
            toRef={toolRef}
            duration={3.5}
            gradientStartColor="#8A5FFF"
            gradientStopColor="#C4F000"
          />
        </div>

        {/* Caption — current step details */}
        <div
          style={{
            maxWidth: 920,
            margin: '0 auto',
            width: '100%',
            minHeight: 140,
            paddingTop: 28,
          }}
        >
          {currentStep ? (
            <motion.div
              key={currentStep.n}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              style={{
                display: 'grid',
                gridTemplateColumns: 'auto 1fr auto',
                gap: 28,
                alignItems: 'center',
              }}
            >
              <span
                style={{
                  fontFamily: FONT_MONO,
                  fontSize: 56,
                  fontWeight: 800,
                  lineHeight: 1,
                  color: 'rgba(255,255,255,0.12)',
                  letterSpacing: '-0.03em',
                }}
              >
                {String(currentStep.n).padStart(2, '0')}
              </span>
              <div>
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 12,
                    color: '#338AFA',
                    fontWeight: 700,
                    letterSpacing: '0.12em',
                    marginBottom: 8,
                  }}
                >
                  {currentStep.label}
                </div>
                <p
                  style={{
                    fontSize: 16,
                    lineHeight: 1.6,
                    color: 'rgba(255,255,255,0.85)',
                    margin: 0,
                  }}
                >
                  {currentStep.desc}
                </p>
              </div>
              <div
                style={{
                  fontFamily: FONT_MONO,
                  fontSize: 12,
                  color: '#C4F000',
                  fontWeight: 800,
                  textAlign: 'right',
                  whiteSpace: 'nowrap',
                  paddingLeft: 16,
                  borderLeft: '1px solid rgba(255,255,255,0.15)',
                  paddingTop: 4,
                  paddingBottom: 4,
                }}
              >
                {currentStep.cost}
              </div>
            </motion.div>
          ) : (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{
                fontSize: 14,
                color: 'rgba(255,255,255,0.5)',
                fontFamily: FONT_MONO,
                letterSpacing: '0.04em',
                margin: 0,
                textAlign: 'center',
              }}
            >
              ▼ 스크롤하면 입력이 5단계 파이프라인을 따라 흐릅니다
            </motion.p>
          )}
        </div>
      </div>

      {/* Hidden init to allow ResizeObserver to settle */}
      <InitTrigger />
    </section>
  )
}

function InitTrigger() {
  useEffect(() => {
    // Force layout recalc after mount so beam paths are accurate
    const t = setTimeout(() => window.dispatchEvent(new Event('resize')), 100)
    return () => clearTimeout(t)
  }, [])
  return null
}
