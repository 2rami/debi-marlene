import React, { forwardRef, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { AnimatedBeam } from '../../../components/magicui/animated-beam'
import ScrollFloat from '../../../components/reactbits/ScrollFloat'
import TextType from '../../../components/reactbits/TextType'
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
    body: `# run/services/chat/chat_agent_graph.py
PATCH_KEYWORDS = re.compile(
    r"(패치|너프|버프|변경|밸런스|조정|상향|하향|OP"
    r"|약해졌|강해졌|업데이트|노트"
    r"|추가|신규|새로|등장|개편|새.{0,3}스킬)"
)
intent = "patch" if PATCH_KEYWORDS.search(text) else "general"`,
    caption: '정규식 한 번으로 patch / general 분기 — LLM 호출 0회. 자연어 누수 발견 시 키워드 보강',
  },
  {
    kind: 'image',
    src: '/portfolio/architecture/patchnote.png',
    alt: '데비&마를렌 패치노트 응답 + V2 Container 카드',
    caption: '"새로운 전술 스킬 추가" 같은 자연어 → fetch_patchnote → 11.0 핫픽스 + Part.1 메인 두 패치 합쳐서 카드 송출. 페르소나 톤 + 출처 표기 동시',
  },
  {
    kind: 'code',
    lang: 'python',
    body: `# run/services/chat/managed_agents_client.py
session_id, summary = await session_store.get_or_rotate_session(
    guild_id, user_id,
    create_fn=self._create_session,
    archive_fn=self._archive_session,
    summarize_fn=self._summarize_session,
)
# turn 50 / 6h idle 도달 시 요약 → archive → 새 세션`,
    caption: '(guild_id, user_id) → session_id SQLite 영속 매핑. Anthropic Sessions가 history 자동 유지',
  },
  {
    kind: 'image',
    src: '/portfolio/architecture/character-stats.png',
    alt: 'get_character_stats 응답 + CharacterStatsView 카드',
    caption: '"지금 통계 봐바" → claude-haiku-4-5가 get_character_stats 자율 호출 → 다이아+ 7일 티어 카드 + 페르소나가 결과 paraphrase',
  },
  {
    kind: 'image',
    src: '/portfolio/architecture/stats-card.png',
    alt: 'StatsLayoutView 네이티브 v2 카드',
    caption: '"데비야 모모모 전적 검색해줘" → search_player_stats(nickname) → StatsLayoutView v2 Container를 채널에 직접 post',
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
          <ScrollFloat
            animationDuration={0.9}
            ease="back.out(1.6)"
            stagger={0.025}
            scrollStart="top bottom-=10%"
            scrollEnd="bottom center+=20%"
            textStyle={{
              display: 'block',
              fontFamily: 'inherit',
              fontSize: 'inherit',
              fontWeight: 'inherit',
              lineHeight: 'inherit',
              letterSpacing: 'inherit',
              color: 'inherit',
            }}
          >
            {titleParts.head}
          </ScrollFloat>
          {titleParts.tail && (
            <ScrollFloat
              animationDuration={0.9}
              ease="back.out(1.6)"
              stagger={0.018}
              scrollStart="top bottom-=20%"
              scrollEnd="bottom center+=10%"
              textStyle={{
                display: 'block',
                fontFamily: 'inherit',
                fontSize: '0.62em',
                fontWeight: 500,
                color: C.inkSoft,
                letterSpacing: '-0.005em',
                lineHeight: 1.3,
                marginTop: 10,
              }}
            >
              {titleParts.tail}
            </ScrollFloat>
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
          height: 320,
          marginBottom: 24,
          borderTop: `1px solid ${C.cardBorder}`,
          borderBottom: `1px solid ${C.cardBorder}`,
          paddingTop: 16,
          paddingBottom: 16,
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
  const [hover, setHover] = useState(false)

  return (
    <div
      onMouseEnter={() => !errored && setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        position: 'relative',
        background: C.bgWhite,
        border: `1px solid ${hover ? C.nexonBlue : C.cardBorder}`,
        borderRadius: 12,
        // overflow는 thumb 박스에서만 — popover는 viewport에 떠야 해서 outer에선 visible
        overflow: 'visible',
        aspectRatio: '16 / 10',
        cursor: errored ? 'default' : 'zoom-in',
        transition: 'border-color 180ms ease',
      }}
    >
      {!errored ? (
        <>
          {/* thumb 자체는 overflow hidden + radius 처리 */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              borderRadius: 12,
              overflow: 'hidden',
            }}
          >
            <img
              src={src}
              alt={alt}
              onError={() => setErrored(true)}
              style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
            />
          </div>
          {/* zoom 안내 배지 */}
          <div
            style={{
              position: 'absolute',
              top: 8,
              right: 8,
              padding: '4px 8px',
              borderRadius: 999,
              background: 'rgba(10, 18, 36, 0.72)',
              color: '#fff',
              fontFamily: FONT_MONO,
              fontSize: 10,
              fontWeight: 700,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              opacity: hover ? 0 : 0.85,
              transition: 'opacity 180ms ease',
              pointerEvents: 'none',
              zIndex: 2,
            }}
          >
            HOVER
          </div>
          <AnimatePresence>
            {hover && <ImagePreviewPopover src={src} alt={alt} />}
          </AnimatePresence>
        </>
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
            borderRadius: 12,
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

function ImagePreviewPopover({ src, alt }: { src: string; alt: string }) {
  // body 포털로 렌더링 — 상위 transform/will-change 영향 우회, viewport 정중앙 보장
  if (typeof document === 'undefined') return null
  return createPortal(
    <motion.div
      initial={{ opacity: 0, scale: 0.94 }}
      animate={{
        opacity: 1,
        scale: 1,
        transition: { type: 'spring', stiffness: 240, damping: 22 },
      }}
      exit={{ opacity: 0, scale: 0.96, transition: { duration: 0.15 } }}
      style={{
        position: 'fixed',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        pointerEvents: 'none',
      }}
    >
      <img
        src={src}
        alt={alt}
        style={{
          display: 'block',
          width: 'auto',
          height: 'auto',
          maxWidth: 'min(820px, 92vw)',
          maxHeight: '86vh',
          objectFit: 'contain',
          borderRadius: 12,
          boxShadow:
            '0 28px 80px -12px rgba(10, 18, 36, 0.45), 0 0 0 1px rgba(10, 18, 36, 0.08)',
        }}
      />
    </motion.div>,
    document.body,
  )
}

function CodeEvidence({ body, lang }: { body: string; lang: string }) {
  // 첫 줄이 `# path/to/file.py` 형태면 터미널 title로 분리
  const lines = body.split('\n')
  const isPathComment = (lines[0] || '').trim().startsWith('#')
  const title = isPathComment
    ? lines[0].replace(/^#\s*/, '').trim()
    : lang.toUpperCase()
  const codeBody = (isPathComment ? lines.slice(1).join('\n').replace(/^\n+/, '') : body)

  return (
    <div
      style={{
        margin: 0,
        background: '#0d1117',
        borderRadius: 12,
        overflow: 'hidden',
        boxShadow: '0 12px 40px -12px rgba(10, 18, 36, 0.32), 0 0 0 1px rgba(255,255,255,0.05)',
      }}
    >
      {/* macOS 터미널 title bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '10px 14px',
          background: '#161b22',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <div style={{ display: 'flex', gap: 6 }}>
          <TerminalDot color="#ff5f57" />
          <TerminalDot color="#febc2e" />
          <TerminalDot color="#28c840" />
        </div>
        <div
          style={{
            flex: 1,
            textAlign: 'center',
            fontFamily: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace',
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: '0.04em',
            color: 'rgba(230, 237, 243, 0.55)',
            paddingRight: 36, // dot 영역 보정
          }}
        >
          {title}
        </div>
      </div>

      {/* 코드 본문 — 타이핑 효과 */}
      <pre
        style={{
          margin: 0,
          padding: '18px 20px',
          fontFamily: '"JetBrains Mono", "SF Mono", Menlo, Consolas, monospace',
          fontSize: 12.5,
          lineHeight: 1.65,
          color: '#e6edf3',
          whiteSpace: 'pre',
          overflowX: 'auto',
        }}
      >
        <TextType
          as="code"
          text={codeBody}
          typingSpeed={14}
          loop={false}
          startOnVisible
          showCursor
          cursorCharacter="▍"
          cursorClassName="terminal-cursor"
        />
      </pre>
    </div>
  )
}

function TerminalDot({ color }: { color: string }) {
  return (
    <span
      style={{
        width: 12,
        height: 12,
        borderRadius: '50%',
        background: color,
        display: 'inline-block',
      }}
    />
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
