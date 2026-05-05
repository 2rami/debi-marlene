import React, { forwardRef, useEffect, useRef, useState } from 'react'
import { AnimatedBeam } from '../../../components/magicui/animated-beam'
import SectionShell from './SectionShell'
import { C, FONT_BODY, FONT_MONO, FONT_DISPLAY } from './colors'

type NodeProps = {
  label: string
  sub?: string
  stack?: string
  variant?: 'primary' | 'branch' | 'terminal'
  active?: boolean
}

const NodeBox = forwardRef<HTMLDivElement, NodeProps>(function NodeBox(
  { label, sub, stack, variant = 'primary', active = false },
  ref,
) {
  const isTerminal = variant === 'terminal'
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
    <div
      ref={ref}
      style={{
        position: 'relative',
        zIndex: 2,
        background: isTerminal ? C.nexonBlue : C.bgWhite,
        border: `1px solid ${active ? C.nexonBlue : isTerminal ? C.nexonBlue : C.cardBorder}`,
        borderRadius: 14,
        padding: '14px 18px',
        minWidth: 140,
        maxWidth: 180,
        textAlign: 'center',
        whiteSpace: 'nowrap',
        boxShadow: active
          ? `0 6px 22px rgba(0, 86, 214, 0.22)`
          : '0 4px 14px rgba(10, 18, 36, 0.05)',
        transform: active ? 'translateY(-2px)' : 'translateY(0)',
        transition: 'transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease',
      }}
    >
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 800,
          color: isTerminal ? C.bgWhite : C.nexonBlue,
          letterSpacing: '0.14em',
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
            color: isTerminal ? 'rgba(255,255,255,0.85)' : C.inkMuted,
            fontFamily: FONT_BODY,
            fontWeight: 500,
            letterSpacing: '-0.005em',
          }}
        >
          {sub}
        </div>
      )}
    </div>
    {stack && (
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 10,
          letterSpacing: '0.08em',
          color: active ? C.nexonBlue : C.inkMuted,
          fontWeight: 700,
          textTransform: 'uppercase',
          textAlign: 'center',
          maxWidth: 200,
          lineHeight: 1.4,
          whiteSpace: 'normal',
          transition: 'color 180ms ease',
        }}
      >
        {stack}
      </div>
    )}
    </div>
  )
})

type Step = {
  n: number
  label: string
  desc: string
  cost: string
}

interface Props {
  steps: readonly Step[]
  title: string
}

type Evidence =
  | { kind: 'image'; src: string; alt: string; caption?: string }
  | { kind: 'code'; lang: string; body: string; caption?: string }

const EVIDENCE: Evidence[] = [
  {
    kind: 'code',
    lang: 'python',
    body: `# run/llm/classify_intent.py
PATCH_KEYWORDS = re.compile(
    r"(패치|너프|버프|변경|밸런스|상향|하향|OP)"
)
intent = "patch" if PATCH_KEYWORDS.search(text) else "general"`,
    caption: '정규식 한 번으로 patch / general 분기 — LLM 호출 0회',
  },
  {
    kind: 'image',
    src: '/portfolio/architecture/patchnote.png',
    alt: 'ER 패치노트 응답 임베드',
    caption: '데비&마를렌이 ER 공식 패치노트에서 캐릭터 별칭을 매핑해 응답',
  },
  {
    kind: 'code',
    lang: 'python',
    body: `# run/llm/session_store.py
async def get_or_create_session(guild_id, user_id):
    row = await db.fetch_one(
        "SELECT session_id, turn, last_at FROM sessions "
        "WHERE guild_id=? AND user_id=?",
        (guild_id, user_id),
    )
    if row and row.turn < 50 and not idle_over(row.last_at, hours=6):
        return row.session_id
    return await rotate(guild_id, user_id)  # 요약→archive→새 세션`,
    caption: '(guild_id, user_id) → session_id 영속. turn 50 / 6h idle 자동 회전',
  },
  {
    kind: 'image',
    src: '/portfolio/architecture/llm-response.png',
    alt: 'Discord LLM 응답 말풍선',
    caption: 'few-shot 5쌍 + 4가지 방어 규칙으로 캐릭터 톤 유지',
  },
  {
    kind: 'image',
    src: '/portfolio/architecture/stats-card.png',
    alt: 'StatsLayoutView 네이티브 카드',
    caption: 'Claude가 search_player_stats 자율 호출 → LayoutView v2로 직접 post',
  },
]

export default function ArchitectureDiagram({ steps, title }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const userRef = useRef<HTMLDivElement>(null)
  const classifyRef = useRef<HTMLDivElement>(null)
  const patchnoteRef = useRef<HTMLDivElement>(null)
  const memoryRef = useRef<HTMLDivElement>(null)
  const llmRef = useRef<HTMLDivElement>(null)
  const toolRef = useRef<HTMLDivElement>(null)

  const [activeIdx, setActiveIdx] = useState<number | null>(null)
  const hoverProps = (i: number) => ({
    onClick: () => setActiveIdx((cur) => (cur === i ? null : i)),
    role: 'button' as const,
    tabIndex: 0,
    onKeyDown: (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        setActiveIdx((cur) => (cur === i ? null : i))
      }
    },
  })

  const NODE_NAMES = ['classify_intent', 'fetch_patchnote', 'fetch_memory', 'call_llm', 'custom_tool']
  const active = activeIdx != null ? steps[activeIdx] : null
  const evidence = activeIdx != null ? EVIDENCE[activeIdx] : null

  // "debi-marlene 시스템 — 입력 한 번에 일어나는 일" 같은 한 줄 string을 두 줄 강세 구조로 분해
  const titleParts = splitTitle(title)

  return (
    <SectionShell
      id="architecture"
      ch="CH 2"
      no="02"
      kicker="ARCHITECTURE · 입력 한 번에 일어나는 일"
      title={
        <span style={{ display: 'block' }}>
          <span style={{ display: 'block' }}>{titleParts.head}</span>
          {titleParts.tail && (
            <span
              style={{
                display: 'block',
                fontSize: '0.62em',
                fontWeight: 500,
                color: C.inkSoft,
                letterSpacing: '-0.005em',
                marginTop: 10,
              }}
            >
              {titleParts.tail}
            </span>
          )}
        </span>
      }
      variant="aside"
      background={C.bgLight}
    >
      {/* Diagram canvas — 라이트, 단일 nexonBlue 빔 */}
      <div
        ref={containerRef}
        style={{
          position: 'relative',
          width: '100%',
          height: 440,
          marginBottom: 56,
          borderTop: `1px solid ${C.cardBorder}`,
          borderBottom: `1px solid ${C.cardBorder}`,
          paddingTop: 24,
          paddingBottom: 24,
        }}
      >
        {/* USER */}
        <div style={{ position: 'absolute', left: '8%', top: '58%', transform: 'translate(-50%, -50%)' }}>
          <NodeBox ref={userRef} label="USER" sub="Discord 입력" stack="discord.py" variant="terminal" />
        </div>

        {/* CLASSIFY */}
        <div {...hoverProps(0)} style={{ position: 'absolute', left: '28%', top: '58%', transform: 'translate(-50%, -50%)', cursor: 'pointer' }}>
          <NodeBox ref={classifyRef} label={NODE_NAMES[0]} sub="regex 0.1ms" stack="LangGraph · python re" active={activeIdx === 0} />
        </div>

        {/* PATCHNOTE (branch up) */}
        <div {...hoverProps(1)} style={{ position: 'absolute', left: '50%', top: '12%', transform: 'translate(-50%, 0)', cursor: 'pointer' }}>
          <NodeBox ref={patchnoteRef} label={NODE_NAMES[1]} sub="patch intent only" stack="httpx · 1h TTL cache" variant="branch" active={activeIdx === 1} />
        </div>

        {/* MEMORY */}
        <div {...hoverProps(2)} style={{ position: 'absolute', left: '50%', top: '58%', transform: 'translate(-50%, -50%)', cursor: 'pointer' }}>
          <NodeBox ref={memoryRef} label={NODE_NAMES[2]} sub="SQLite 영속" stack="aiosqlite · 50 turns / 6h" active={activeIdx === 2} />
        </div>

        {/* LLM */}
        <div {...hoverProps(3)} style={{ position: 'absolute', left: '72%', top: '58%', transform: 'translate(-50%, -50%)', cursor: 'pointer' }}>
          <NodeBox ref={llmRef} label={NODE_NAMES[3]} sub="claude-haiku-4-5" stack="Anthropic Managed Agents" active={activeIdx === 3} />
        </div>

        {/* TOOL */}
        <div {...hoverProps(4)} style={{ position: 'absolute', left: '92%', top: '58%', transform: 'translate(-50%, -50%)', cursor: 'pointer' }}>
          <NodeBox ref={toolRef} label={NODE_NAMES[4]} sub="StatsLayoutView" stack="Discord LayoutView v2" variant="terminal" active={activeIdx === 4} />
        </div>

        {/* Beams — 단일 nexonBlue 라이트 톤 */}
        <AnimatedBeam
          containerRef={containerRef}
          fromRef={userRef}
          toRef={classifyRef}
          duration={4}
          pathColor={C.cardBorder}
          pathOpacity={1}
          gradientStartColor={C.nexonLightBlue}
          gradientStopColor={C.nexonBlue}
        />
        <AnimatedBeam
          containerRef={containerRef}
          fromRef={classifyRef}
          toRef={patchnoteRef}
          duration={4}
          curvature={-50}
          pathColor={C.cardBorder}
          pathOpacity={1}
          gradientStartColor={C.nexonLightBlue}
          gradientStopColor={C.nexonBlue}
        />
        <AnimatedBeam
          containerRef={containerRef}
          fromRef={classifyRef}
          toRef={memoryRef}
          duration={4}
          pathColor={C.cardBorder}
          pathOpacity={1}
          gradientStartColor={C.nexonLightBlue}
          gradientStopColor={C.nexonBlue}
        />
        <AnimatedBeam
          containerRef={containerRef}
          fromRef={patchnoteRef}
          toRef={memoryRef}
          duration={4}
          curvature={50}
          pathColor={C.cardBorder}
          pathOpacity={1}
          gradientStartColor={C.nexonLightBlue}
          gradientStopColor={C.nexonBlue}
        />
        <AnimatedBeam
          containerRef={containerRef}
          fromRef={memoryRef}
          toRef={llmRef}
          duration={4}
          pathColor={C.cardBorder}
          pathOpacity={1}
          gradientStartColor={C.nexonLightBlue}
          gradientStopColor={C.nexonBlue}
        />
        <AnimatedBeam
          containerRef={containerRef}
          fromRef={llmRef}
          toRef={toolRef}
          duration={4}
          pathColor={C.cardBorder}
          pathOpacity={1}
          gradientStartColor={C.nexonLightBlue}
          gradientStopColor={C.nexonBlue}
        />
      </div>

      {/* 노드 클릭 시 표시되는 캡션 + evidence (2칼럼) */}
      <div
        style={{
          minHeight: 220,
          paddingTop: 24,
          paddingBottom: 20,
          borderTop: `1px solid ${C.cardBorder}`,
          transition: 'opacity 180ms ease',
        }}
      >
        {active ? (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(0, 1.05fr) minmax(0, 1fr)',
              columnGap: 'clamp(24px, 4vw, 56px)',
              rowGap: 24,
              alignItems: 'start',
            }}
          >
            {/* LEFT — 캡션 (번호 + 라벨 + desc + cost) */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(56px, 72px) minmax(0, 1fr)',
                columnGap: 24,
                alignItems: 'baseline',
              }}
            >
              <span
                style={{
                  fontFamily: FONT_DISPLAY,
                  fontSize: 'clamp(28px, 3.4vw, 40px)',
                  fontWeight: 800,
                  lineHeight: 1,
                  color: C.nexonBlue,
                  letterSpacing: '-0.04em',
                }}
              >
                {String(active.n).padStart(2, '0')}
              </span>
              <div>
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 12,
                    fontWeight: 800,
                    letterSpacing: '0.06em',
                    color: C.ink,
                    marginBottom: 8,
                    wordBreak: 'keep-all',
                  }}
                >
                  {active.label}
                </div>
                <p
                  style={{
                    fontFamily: FONT_BODY,
                    fontSize: 14.5,
                    lineHeight: 1.7,
                    color: C.inkSoft,
                    margin: '0 0 14px',
                    fontWeight: 500,
                    wordBreak: 'keep-all',
                  }}
                >
                  {active.desc}
                </p>
                <span
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: '0.12em',
                    color: C.nexonBlue,
                    textTransform: 'uppercase',
                  }}
                >
                  {active.cost}
                </span>
              </div>
            </div>

            {/* RIGHT — evidence (스샷 또는 코드) */}
            {evidence && <EvidencePane evidence={evidence} />}
          </div>
        ) : (
          <div
            style={{
              fontFamily: FONT_MONO,
              fontSize: 12,
              fontWeight: 600,
              letterSpacing: '0.14em',
              color: C.inkMuted,
              textTransform: 'uppercase',
            }}
          >
            노드를 클릭하면 단계 설명과 실제 운영 화면이 표시됩니다
          </div>
        )}
      </div>

      <InitTrigger />
    </SectionShell>
  )
}

function EvidencePane({ evidence }: { evidence: Evidence }) {
  return (
    <figure style={{ margin: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
      {evidence.kind === 'image' ? (
        <ImageEvidence src={evidence.src} alt={evidence.alt} />
      ) : (
        <CodeEvidence body={evidence.body} lang={evidence.lang} />
      )}
      {evidence.caption && (
        <figcaption
          style={{
            fontFamily: FONT_BODY,
            fontSize: 12.5,
            lineHeight: 1.55,
            color: C.inkMuted,
            fontWeight: 500,
            wordBreak: 'keep-all',
          }}
        >
          {evidence.caption}
        </figcaption>
      )}
    </figure>
  )
}

function ImageEvidence({ src, alt }: { src: string; alt: string }) {
  const [errored, setErrored] = useState(false)
  return (
    <div
      style={{
        position: 'relative',
        background: C.bgWhite,
        border: `1px solid ${C.cardBorder}`,
        borderRadius: 12,
        overflow: 'hidden',
        aspectRatio: '16 / 10',
      }}
    >
      {!errored ? (
        <img
          src={src}
          alt={alt}
          onError={() => setErrored(true)}
          style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
        />
      ) : (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            background: C.bgLight,
            color: C.inkMuted,
            fontFamily: FONT_MONO,
            fontSize: 11,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            padding: 20,
            textAlign: 'center',
          }}
        >
          <span style={{ fontWeight: 800, color: C.nexonBlue }}>SCREENSHOT</span>
          <span style={{ wordBreak: 'break-all' }}>{src}</span>
          <span style={{ fontFamily: FONT_BODY, fontSize: 10.5, letterSpacing: 0, textTransform: 'none', color: C.inkMuted }}>
            public 폴더에 이미지 추가하면 자동 표시
          </span>
        </div>
      )}
    </div>
  )
}

function CodeEvidence({ body, lang }: { body: string; lang: string }) {
  return (
    <pre
      style={{
        margin: 0,
        background: C.ink,
        color: '#e6edf3',
        border: `1px solid ${C.ink}`,
        borderRadius: 12,
        padding: '16px 18px',
        fontFamily: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace',
        fontSize: 12.5,
        lineHeight: 1.6,
        overflow: 'auto',
        maxHeight: 240,
      }}
    >
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 10,
          fontWeight: 800,
          letterSpacing: '0.18em',
          color: C.nexonLightBlue,
          textTransform: 'uppercase',
          marginBottom: 10,
        }}
      >
        {lang}
      </div>
      <code style={{ fontFamily: 'inherit' }}>{body}</code>
    </pre>
  )
}

function splitTitle(raw: string): { head: string; tail: string | null } {
  const m = raw.match(/^(.+?)\s*[—–-]\s*(.+)$/)
  if (!m) return { head: raw, tail: null }
  return { head: m[1].trim(), tail: m[2].trim() }
}

function InitTrigger() {
  useEffect(() => {
    // beam path 정확히 잡으려고 mount 후 resize 한 번 dispatch
    const t = setTimeout(() => window.dispatchEvent(new Event('resize')), 100)
    return () => clearTimeout(t)
  }, [])
  return null
}
