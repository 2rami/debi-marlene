import { useRef, useEffect, useState } from 'react'
import { motion, useInView, useScroll, useTransform, AnimatePresence } from 'framer-motion'
import Lenis from 'lenis'
import Header from '../components/common/Header'
import GlassButton from '../components/common/GlassButton'
import GradientText from '../components/common/GradientText'
import ScrollFloat from '../components/common/ScrollFloat'
import MermaidDiagram from '../components/common/MermaidDiagram'
import { useTheme } from '../contexts/ThemeContext'
import { CalendarDays, Layers, BrainCircuit, Bot } from 'lucide-react'
/* ── Assets ── */
import CHAR_HERO_LIGHT from '../assets/images/event/imgi_30_ch01_v2.png'
import CHAR_HERO_DARK from '../assets/images/event/char_twins_dark.png'

/* Screenshots */
import SS_STATS from '../assets/images/event/screenshot_stats.png'
import SS_DASHBOARD from '../assets/images/event/screenshot_dashboard.png'
import SS_TTS_SETTINGS from '../assets/images/event/screenshot_tts_settings.png'
import SS_WEBPANEL from '../assets/images/event/screenshot_webpanel.png'
import SS_STATUSLINE from '../assets/images/event/statusline_preview.png'
import SS_AI_CHAT from '../assets/images/event/screenshot_ai_chat.png'

const ACCENT = '#0B5ED7'
const ACCENT2 = '#6DC8E8'

const ARCHITECTURE_MERMAID = `flowchart LR
  U1([Discord User])
  U2([Web User])

  subgraph CLIENT[Client Layer]
    direction TB
    D[Discord App]
    DB[Dashboard Web]
    AP[Admin Panel]
  end

  subgraph VM[GCP Compute Engine - Seoul]
    direction TB
    NGX{{Nginx Proxy + SSL}}
    BOT[Discord Bot<br/>discord.py]
    API1[Dashboard API<br/>Flask + OAuth2]
    API2[Webpanel API<br/>Flask + SSE]
    NGX --> API1
    NGX --> API2
  end

  subgraph AI[AI Services]
    direction TB
    M1[[Modal A10G<br/>Gemma4 LoRA]]
    M2[[Modal T4<br/>CosyVoice3 TTS]]
    DS[[DashScope<br/>Qwen3.5-Omni]]
  end

  subgraph STOR[Storage & CDN]
    direction TB
    GCS[(GCS<br/>Memory + Assets)]
    HF[(HuggingFace<br/>Model Registry)]
    CF{{Cloudflare<br/>CDN / DNS}}
  end

  U1 --> D
  U2 --> DB
  U2 --> AP
  D -.Voice/Text.-> BOT
  DB --> CF
  AP --> CF
  CF --> NGX

  BOT -->|Chat RAG| M1
  BOT -->|TTS Synth| M2
  BOT -->|Audio Understanding| DS
  BOT -->|Memory| GCS
  M1 -.Fine-tuned Weights.-> HF
  M2 -.Fine-tuned Weights.-> HF

  classDef userNode fill:#818cf8,stroke:#6366f1,color:#fff,stroke-width:2px
  classDef clientNode fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,stroke-width:2px
  classDef serverNode fill:#0B5ED7,stroke:#1e3a8a,color:#fff,stroke-width:2px
  classDef infraNode fill:#64748b,stroke:#475569,color:#fff,stroke-width:2px
  classDef aiNode fill:#a855f7,stroke:#7c3aed,color:#fff,stroke-width:2px
  classDef storeNode fill:#f59e0b,stroke:#d97706,color:#fff,stroke-width:2px

  class U1,U2 userNode
  class D,DB,AP clientNode
  class BOT,API1,API2 serverNode
  class NGX infraNode
  class M1,M2,DS aiNode
  class GCS,HF storeNode
  class CF infraNode
`

// 실제 LangGraph StateGraph의 draw_mermaid() 출력 그대로.
// 생성 커맨드: graph.get_graph().draw_mermaid()
// 점선(-.->)이 conditional edge, 실선(-->)이 일반 edge
const CHAT_AGENT_MERMAID = `---
config:
  flowchart:
    curve: linear
---
graph TD;
    __start__([START]):::first
    classify_intent(classify_intent)
    fetch_patchnote(fetch_patchnote)
    skip_patchnote(skip_patchnote)
    fetch_memory(fetch_memory)
    call_llm(call_llm)
    __end__([END]):::last
    __start__ --> classify_intent;
    classify_intent -. "intent = patch" .-> fetch_patchnote;
    classify_intent -. "intent = general" .-> skip_patchnote;
    fetch_memory --> call_llm;
    fetch_patchnote --> fetch_memory;
    skip_patchnote --> fetch_memory;
    call_llm --> __end__;
    classDef default fill:#e8f4ff,stroke:#0B5ED7,stroke-width:2px,color:#0f172a,line-height:1.2
    classDef first fill:#0B5ED7,color:#fff,stroke:#1e3a8a
    classDef last fill:#6DC8E8,color:#0f172a,stroke:#0B5ED7
`

/* ── FadeIn ── */
function FadeIn({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

/* ── Glass Card (Cloud Texture wrapper) ── */
function GlassCard({ children, className = '' }: { children?: React.ReactNode, className?: string }) {
  const { isDark } = useTheme()
  return (
    <div className={`relative rounded-[inherit] overflow-hidden ${className}`}>
      <div
        className="absolute inset-0 pointer-events-none transition-all duration-300"
        style={{
          zIndex: 0,
          background: isDark ? 'rgba(255, 255, 255, 0.04)' : 'rgba(255, 255, 255, 0.72)',
          filter: 'url(#glass-texture)',
          boxShadow: isDark
            ? '0px 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255, 255, 255, 0.15), inset 0 0 20px rgba(255,255,255,0.05)'
            : '0px 12px 32px rgba(11, 94, 215, 0.10), 0px 2px 8px rgba(15, 23, 42, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.9)',
          border: isDark
            ? '1.5px solid rgba(255, 255, 255, 0.25)'
            : '1.5px solid rgba(11, 94, 215, 0.18)',
          backdropFilter: 'blur(20px)'
        }}
      />
      <div className="relative z-10 w-full h-full">{children}</div>
    </div>
  )
}

/* ── SVG Title Text ── */
function SVGTitle({ lines, className = '' }: { lines: string[]; className?: string }) {
  const { isDark } = useTheme()
  return (
    <div className={className} style={{ filter: 'url(#text-texture)' }}>
      {lines.map((line, i) => {
        const charCount = line.length
        const vw = charCount <= 2 ? 350 * charCount : 280 * charCount
        const gradId = `title-grad-${i}`
        return (
          <div key={i}>
            <svg viewBox={`0 0 ${vw} 250`} className="w-[300px] md:w-[550px] lg:w-[700px] h-auto overflow-visible block">
              {isDark && (
                <defs>
                  <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor={ACCENT} />
                    <stop offset="100%" stopColor={ACCENT2} />
                  </linearGradient>
                </defs>
              )}
              {isDark ? (
                <>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="none" stroke={`url(#${gradId})`} strokeWidth="12" paintOrder="stroke">{line}</text>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="#d1d5db" stroke={`url(#${gradId})`} strokeWidth="5" paintOrder="stroke" style={{ filter: `drop-shadow(0px 4px 8px rgba(11, 94, 215, 0.3))` }}>{line}</text>
                </>
              ) : (
                <>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill="none" stroke={ACCENT2} strokeWidth="12" paintOrder="stroke">{line}</text>
                  <text x="0" y="200" fontSize="220" fontWeight="bold" fontFamily="'YPairingFont', system-ui, sans-serif" fill={ACCENT} stroke={ACCENT2} strokeWidth="5" paintOrder="stroke" style={{ filter: `drop-shadow(0px 4px 6px rgba(11, 94, 215, 0.4))` }}>{line}</text>
                </>
              )}
            </svg>
          </div>
        )
      })}
    </div>
  )
}

/* ── JD Match Card (Hover Bento) ── */
function MatchCard({ requirement, evidence, techs, delay = 0, className = "" }: {
  requirement: string; evidence: string; techs: string[]; delay?: number; className?: string;
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className={`group h-full ${className}`}>
      <GlassCard className="relative p-6 rounded-3xl h-full transition-all duration-500 hover:-translate-y-1">
      {/* Background Glow */}
      <div className={`absolute top-0 right-0 w-32 h-32 blur-[50px] transition-opacity duration-500 opacity-0 group-hover:opacity-100 ${isDark ? 'bg-[#0B5ED7]/20' : 'bg-[#0B5ED7]/10'}`} />
      
      <div className="relative z-10 flex flex-col h-full">
        <div className="flex items-start gap-4 mb-4">
          <div className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shadow-sm transition-transform duration-300 group-hover:scale-110" style={{ backgroundColor: isDark ? `${ACCENT}25` : `${ACCENT}15`, color: ACCENT }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
          </div>
          <div className={`text-base font-bold leading-tight pt-1 w-full pr-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>{requirement}</div>
        </div>
        
        {/* Tech tags - always visible at bottom, pushing space */}
        <div className="mt-auto pt-4 flex flex-wrap gap-2">
          {techs.map(t => (
            <span key={t} className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${isDark ? 'bg-white/[0.05] text-gray-300 border-white/[0.06] group-hover:border-white/[0.15]' : 'bg-gray-50 text-gray-600 border-gray-200 group-hover:border-blue-200'}`}>{t}</span>
          ))}
        </div>

        {/* Hover Overlay for Evidence */}
        <div className={`absolute inset-0 p-6 flex flex-col justify-center backdrop-blur-md transition-all duration-500 ease-out opacity-0 translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 ${isDark ? 'bg-[#1a1a2e]/90' : 'bg-white/95'}`}>
          <div className="flex items-center gap-2 mb-3 text-xs font-bold uppercase tracking-wider text-[#0B5ED7]">
             <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg> Implementation
          </div>
          <p className={`text-sm leading-relaxed font-medium ${isDark ? 'text-gray-200' : 'text-gray-700'}`}>{evidence}</p>
        </div>
      </div>
      </GlassCard>
    </FadeIn>
  )
}

/* ── Troubleshoot Accordion ── */
function TroubleshootCard({ title, problem, cause, solution, color, delay = 0 }: {
  title: string; problem: string; cause: string; solution: string; color: string; delay?: number
}) {
  const { isDark } = useTheme()
  const [isOpen, setIsOpen] = useState(false)
  
  return (
    <FadeIn delay={delay}>
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className={`group cursor-pointer rounded-2xl border overflow-hidden transition-all duration-300 select-none ${isDark ? 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04]' : 'bg-white border-gray-200/50 hover:bg-gray-50'} ${isOpen ? isDark ? 'ring-1 ring-white/10' : 'shadow-md ring-1 ring-gray-200' : ''}`}
      >
        <div className="flex items-stretch">
          <div className="w-1.5 shrink-0 transition-colors" style={{ backgroundColor: isOpen ? color : `${color}80` }} />
          <div className="flex-1 p-5">
            <div className={`flex items-center justify-between font-bold text-base ${isDark ? 'text-white' : 'text-gray-800'}`}>
              <div className="flex items-center gap-3">
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs transition-transform duration-300 ${isOpen ? 'rotate-90' : ''}`} style={{ backgroundColor: `${color}20`, color: color }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M9 18l6-6-6-6"/></svg>
                </span>
                {title}
              </div>
            </div>
            
            <AnimatePresence initial={false}>
              {isOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3, ease: [0.04, 0.62, 0.23, 0.98] }}
                  className="overflow-hidden"
                >
                  <div className="grid md:grid-cols-3 gap-6 pt-5 mt-4 border-t border-dashed border-gray-200 dark:border-white/10 text-sm">
                    <div>
                      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider mb-2" style={{ color: '#ed4245' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                        Problem
                      </div>
                      <div className={`leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{problem}</div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider mb-2" style={{ color: '#faa61a' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polygon points="12 2 2 22 22 22"/><line x1="12" y1="8" x2="12" y2="14"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
                        Root Cause
                      </div>
                      <div className={`leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{cause}</div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider mb-2" style={{ color: '#43b581' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                        Solution
                      </div>
                      <div className={`leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{solution}</div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </FadeIn>
  )
}

/* ── Pipeline Node (Horizontal) ── */
function PipelineNode({ step, title, desc, techs, isLast = false, delay = 0 }: {
  step: number; title: string; desc: string; techs: string[]; isLast?: boolean; delay?: number
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className="relative flex-1 min-w-[240px]">
      {!isLast && (
        <div className="hidden md:block absolute top-[24px] left-[60px] right-[-20px] h-px z-0">
          <div className="w-full h-full border-t-2 border-dashed border-gray-300 dark:border-white/20" />
          <svg className="absolute right-0 top-1/2 -translate-y-1/2 text-gray-300 dark:text-white/20" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M9 18l6-6-6-6"/></svg>
        </div>
      )}
      <div className="relative z-10 bg-inherit pr-6 pb-6 md:pb-0">
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-base font-bold shadow-sm mb-4 transition-transform hover:scale-110`} style={{ backgroundColor: isDark ? `${ACCENT}20` : `${ACCENT}15`, color: ACCENT }}>
          {step}
        </div>
        <h4 className={`font-bold text-base mb-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>{title}</h4>
        <p className={`text-sm leading-relaxed mb-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{desc}</p>
        <div className="flex flex-wrap gap-1.5">
          {techs.map(t => (
            <span key={t} className={`px-2 py-0.5 rounded-full text-[11px] font-medium border ${isDark ? 'bg-white/[0.05] text-gray-300 border-white/[0.06]' : 'bg-gray-50 text-gray-600 border-gray-200'}`}>{t}</span>
          ))}
        </div>
      </div>
    </FadeIn>
  )
}

/* ── Theme Toggle Button ── */
function ThemeToggle() {
  const { isDark, toggle } = useTheme()
  return (
    <motion.button
      onClick={toggle}
      className={`fixed bottom-6 right-6 z-50 cursor-pointer rounded-full w-12 h-12 flex items-center justify-center ${
        isDark
          ? 'bg-gradient-to-b from-[#1a1a2e] to-[#16213e] border border-white/15 text-white'
          : 'bg-gradient-to-b from-white to-gray-50 border border-gray-200 text-gray-700'
      }`}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25, delay: 0.5 }}
      whileHover={{ scale: 1.1 }}
      style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.12)' }}
      aria-label="Toggle theme"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
        {isDark ? (
          <><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></>
        ) : (
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        )}
      </svg>
    </motion.button>
  )
}

/* ── Section Navigator ── */
const SECTIONS = [
  { id: 'hero', label: 'Hero' },
  { id: 'match', label: 'JD Match' },
  { id: 'pipeline', label: 'AI Pipeline' },
  { id: 'troubleshoot', label: 'Troubleshooting' },
  { id: 'features', label: 'Features' },
  { id: 'architecture', label: 'Architecture' },
  { id: 'techstack', label: 'Tech Stack' },
  { id: 'cost', label: 'Cost Analysis' },
]

function SectionNav() {
  const { isDark } = useTheme()
  const [active, setActive] = useState('hero')
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.scrollY > window.innerHeight * 0.5)
      for (let i = SECTIONS.length - 1; i >= 0; i--) {
        const el = document.getElementById(SECTIONS[i].id)
        if (el) {
          const rect = el.getBoundingClientRect()
          if (rect.top <= window.innerHeight * 0.4) {
            setActive(SECTIONS[i].id)
            break
          }
        }
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <AnimatePresence>
      {visible && (
        <motion.nav
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.3 }}
          className="fixed right-5 top-1/2 -translate-y-1/2 z-40 flex flex-col items-end gap-3 max-md:hidden"
        >
          {SECTIONS.map(s => {
            const isActive = active === s.id
            return (
              <button
                key={s.id}
                onClick={() => document.getElementById(s.id)?.scrollIntoView({ behavior: 'smooth' })}
                className="group flex items-center gap-2.5 cursor-pointer"
              >
                <span className={`text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'text-[#0B5ED7] opacity-100'
                    : isDark ? 'text-white/0 group-hover:text-white/70' : 'text-gray-800/0 group-hover:text-gray-500'
                }`}>
                  {s.label}
                </span>
                <div className="relative flex items-center justify-center w-3 h-3">
                  {isActive && (
                    <motion.div
                      layoutId="nav-active-nexon"
                      className="absolute inset-[-3px] rounded-full bg-[#0B5ED7]/20"
                      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                    />
                  )}
                  <div className={`w-2.5 h-2.5 rounded-full transition-all duration-200 ${
                    isActive
                      ? 'bg-[#0B5ED7] scale-100'
                      : isDark ? 'bg-white/20 group-hover:bg-white/50 scale-75' : 'bg-gray-300 group-hover:bg-gray-400 scale-75'
                  }`} />
                </div>
              </button>
            )
          })}
        </motion.nav>
      )}
    </AnimatePresence>
  )
}


/* ══════════════════════════════════════════════
   PortfolioNexon Page
   ══════════════════════════════════════════════ */
export default function PortfolioNexon() {
  const { isDark } = useTheme()
  const heroRef = useRef(null)
  const featuresContainerRef = useRef<HTMLDivElement>(null)
  const featuresTrackRef = useRef<HTMLDivElement>(null)
  const [pipelineTab, setPipelineTab] = useState<'text' | 'voice'>('text')

  // Lenis + GSAP ScrollTrigger 통합 초기화
  useEffect(() => {
    let lenis: Lenis | null = null
    let ctx: ReturnType<typeof import('gsap').default.context> | undefined
    let cleanup = () => {}

    ;(async () => {
      const [{ default: gsap }, { ScrollTrigger }] = await Promise.all([
        import('gsap'),
        import('gsap/ScrollTrigger'),
      ])
      gsap.registerPlugin(ScrollTrigger)

      lenis = new Lenis({
        duration: 0.25,
        wheelMultiplier: 0.5,
        easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      })
      ;(window as any).__lenis = lenis
      lenis.scrollTo(0, { immediate: true })

      // Lenis scroll 이벤트마다 ScrollTrigger 갱신
      lenis.on('scroll', ScrollTrigger.update)
      // GSAP ticker가 Lenis raf 루프를 구동 (requestAnimationFrame 중복 방지)
      const tickerFn = (time: number) => { lenis?.raf(time * 1000) }
      gsap.ticker.add(tickerFn)
      gsap.ticker.lagSmoothing(0)

      // Features 핀 가로 스크롤
      ctx = gsap.context(() => {
        const track = featuresTrackRef.current
        const container = featuresContainerRef.current
        if (!track || !container) return

        const cards = gsap.utils.toArray<HTMLElement>('.feature-card', track)
        if (cards.length === 0) return

        gsap.to(cards, {
          xPercent: -100 * (cards.length - 1),
          ease: 'none',
          scrollTrigger: {
            trigger: container,
            pin: true,
            pinSpacing: true,
            anticipatePin: 1,
            start: 'top top',
            end: () => '+=' + (container.offsetWidth * (cards.length - 1)),
            scrub: 0.5,
            fastScrollEnd: true,
            snap: {
              snapTo: 1 / (cards.length - 1),
              duration: { min: 0.15, max: 0.4 },
              delay: 0,
              ease: 'power2.out',
              directional: false,
            },
            invalidateOnRefresh: true,
          },
        })
      }, featuresContainerRef)

      cleanup = () => {
        gsap.ticker.remove(tickerFn)
        ctx?.revert()
        lenis?.destroy()
        ;(window as any).__lenis = null
        ScrollTrigger.getAll().forEach(t => t.kill())
      }
    })()

    return () => cleanup()
  }, [])

  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '30%'])

  return (
    <div className={`min-h-screen font-body selection:bg-[#0B5ED7]/20 relative z-0 transition-colors duration-500 ${
      isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'
    }`} style={{ overflowX: 'clip' }}>
      <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden="true">
        <defs>
          <filter id="text-texture" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.339" numOctaves="3" seed="5044" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="4" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>
      </svg>

      <Header />
      <ThemeToggle />
      <SectionNav />

      {/* ══ HERO (BENTO REDESIGN) ══ */}
      <section id="hero" ref={heroRef} className="relative min-h-screen pt-32 pb-24 flex items-center justify-center overflow-hidden">
        <div className={`absolute top-0 right-0 w-full h-[500px] bg-gradient-to-b from-[#0B5ED7]/10 to-transparent pointer-events-none`} />
        <div className={`absolute top-[20%] left-[10%] w-[500px] h-[500px] rounded-full blur-[120px] pointer-events-none ${isDark ? 'bg-[#6DC8E8]/[0.08]' : 'bg-[#6DC8E8]/[0.15]'}`} />
        
        <motion.div className="relative z-10 w-full max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-12 gap-6" style={{ y: textY }}>
          
          {/* Main Title Block - Span 8 */}
          <FadeIn className="md:col-span-12 lg:col-span-8 h-full">
            <GlassCard className="h-full p-10 md:p-14 rounded-[32px] flex flex-col justify-center">
            <div className={`absolute top-0 right-0 w-[400px] h-[400px] rounded-full blur-[100px] opacity-30 pointer-events-none translate-x-1/3 -translate-y-1/3 ${isDark ? 'bg-[#0B5ED7]' : 'bg-[#0B5ED7]'}`} />
            
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold tracking-wider uppercase mb-8 border w-max ${
              isDark ? 'bg-[#0B5ED7]/10 text-[#6DC8E8] border-[#0B5ED7]/30' : 'bg-[#0B5ED7]/5 text-[#0B5ED7] border-[#0B5ED7]/20 bg-blend-multiply'
            }`}>
              <div className="w-2 h-2 rounded-full bg-[#0B5ED7] animate-pulse" />
              NEXON Application Portfolio
            </div>

            <GradientText
              colors={[ACCENT, ACCENT2, '#4A9BE8', ACCENT2, ACCENT]}
              animationSpeed={5}
              className="!mx-0 font-title text-[32px] md:text-[48px] lg:text-[56px] leading-[1.1] tracking-tight mb-6"
            >
              AI Agent<br/>Full-Stack Engineer
            </GradientText>
            
            <p className={`text-lg md:text-xl leading-relaxed max-w-2xl font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
              LLM 파인튜닝, 음성 AI Agent, RAG 대화 시스템을<br className="hidden md:block"/>
              직접 기획하고 배포까지 운영한 1인 풀스택 엔지니어 <span className={`font-bold py-1 px-2 rounded-lg ${isDark ? 'text-white bg-white/10' : 'text-gray-800 bg-gray-200/60'}`}>양건호</span>입니다.
            </p>
            </GlassCard>
          </FadeIn>

          {/* Visual Block - Span 4 */}
          <FadeIn delay={0.1} className="md:col-span-6 lg:col-span-4 h-full">
            <GlassCard className="h-full rounded-[32px] group">
            <div className={`absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent z-10 transition-opacity duration-500 opacity-100 lg:opacity-100 ${isDark ? 'opacity-100' : ''}`} />
            <img
              src={isDark ? CHAR_HERO_DARK : CHAR_HERO_LIGHT}
              alt="Character Hero"
              className="w-full h-full object-cover object-top min-h-[300px] transition-transform duration-700 group-hover:scale-105"
              draggable={false}
            />
            <div className={`absolute bottom-6 left-6 z-20 ${isDark ? '' : 'lg:text-white text-gray-800 drop-shadow-md'}`}>
              <div className="font-bold tracking-widest text-sm flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> SYSTEM ONLINE
              </div>
            </div>
            </GlassCard>
          </FadeIn>

          {/* Stats Block - Span 5 */}
          <FadeIn delay={0.15} className="md:col-span-6 lg:col-span-5 h-full">
            <GlassCard className="h-full p-8 rounded-[32px] flex flex-col justify-center">
            <div className="grid grid-cols-2 gap-y-10 gap-x-6 w-full">
              {[
                { 
                  v: '6+', l: '개발 기간', sub: 'Months Dev Time',
                  icon: <CalendarDays strokeWidth={1.5} className="w-6 h-6" />
                },
                { 
                  v: 'Full', l: '1인 개발', sub: 'End-to-End Stack',
                  icon: <Layers strokeWidth={1.5} className="w-6 h-6" />
                },
                { 
                  v: '6개', l: 'LLM & TTS', sub: 'Models Integrated',
                  icon: <BrainCircuit strokeWidth={1.5} className="w-6 h-6" />
                },
                { 
                  v: 'Native', l: 'AI 주도로 구축', sub: 'Built with AI',
                  icon: <Bot strokeWidth={1.5} className="w-6 h-6" />
                },
              ].map((s, i) => (
                <div key={i} className="flex flex-col gap-3 group">
                  <div className={`p-3 w-max rounded-[14px] transition-colors ${isDark ? 'bg-white/[0.04] text-[#6DC8E8] group-hover:bg-[#0B5ED7]/20 group-hover:text-white' : 'bg-[#0B5ED7]/5 text-[#0B5ED7] group-hover:bg-[#0B5ED7]/10'}`}>
                    {s.icon}
                  </div>
                  <div>
                    <div className="text-[19px] md:text-[22px] font-bold bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent mb-1 -tracking-wider font-[Paperlogy]">
                      {s.v}
                    </div>
                    <div className={`text-[13px] font-bold mb-0.5 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>{s.l}</div>
                    <div className={`text-[10px] md:text-[11px] font-medium tracking-widest uppercase ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{s.sub}</div>
                  </div>
                </div>
              ))}
            </div>
            </GlassCard>
          </FadeIn>

          {/* Code/Terminal Block - Span 4 */}
          <FadeIn delay={0.2} className="md:col-span-6 lg:col-span-4 h-full">
            <GlassCard className="h-full p-8 rounded-[32px] flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
            </div>
            <div className="font-mono text-[13px] sm:text-sm leading-relaxed text-gray-300">
              <div className="text-[#6DC8E8] font-bold">~$ ./init_competency.sh</div>
              <div className="text-gray-400 mt-2 mb-1">Loading core architecture...</div>
              <div><span className="text-[#0B5ED7] font-bold">[OK]</span> Advanced RAG Systems</div>
              <div><span className="text-[#0B5ED7] font-bold">[OK]</span> Real-time Voice Chat</div>
              <div><span className="text-[#0B5ED7] font-bold">[OK]</span> Scalable Infra (GCP)</div>
              <div className="mt-3 text-emerald-400 flex items-center gap-1">Status: Ready <div className="w-2 h-4 bg-emerald-400 animate-pulse" /></div>
            </div>
            </GlassCard>
          </FadeIn>

          {/* Action Block - Span 3 */}
          <FadeIn delay={0.25} className="md:col-span-6 lg:col-span-3 h-full">
            <GlassCard className="h-full p-8 rounded-[32px] flex flex-col justify-center gap-4">
            <div className={`text-xs font-bold uppercase tracking-widest mb-1 text-center ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Explore Project</div>
            <GlassButton href="/landing" size="sm" className="!w-full !h-14 !text-base shadow-md">
              Live Site Demo
            </GlassButton>
            <GlassButton href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer" size="sm" className="!w-full !h-14 !text-base shadow-md">
               <span className="flex items-center gap-2">
                 <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg> 
                 GitHub Repo
               </span>
            </GlassButton>
            </GlassCard>
          </FadeIn>

        </motion.div>
      </section>

      {/* ══ JD MATCH ══ */}
      <section id="match" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName={`font-title bg-gradient-to-r from-[${ACCENT}] to-[${ACCENT2}] bg-clip-text text-transparent leading-tight`}
              textClassName="text-4xl md:text-[64px]"
            >
              JD Match
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                넥슨 AX-Tech실 공고 요구사항과<br />
                이 프로젝트에서 실제로 구현한 내용의 매칭.
              </p>
            </FadeIn>
          </div>

          {/* 지원 자격 */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-6`} style={{ color: ACCENT }}>
              Requirements
            </h3>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
            <MatchCard
              delay={0}
              requirement="Python, TypeScript 능숙한 개발"
              evidence="봇 백엔드(Python, discord.py, Flask), 대시보드 프론트엔드(TypeScript, React 19), 웹패널(Flask + React). 두 언어로 전체 서비스를 1인 개발 및 운영 중."
              techs={['Python', 'TypeScript', 'discord.py', 'React 19', 'Flask']}
              className="md:col-span-2 lg:col-span-2"
            />
            <MatchCard
              delay={0.05}
              requirement="외부 AI 서비스 활용 개발"
              evidence="Gemma4 LoRA 파인튜닝(Modal API), Qwen3.5-Omni API(DashScope). 텍스트 채팅 + 음성 대화 두 채널에서 실시간 서비스 운영."
              techs={['Gemma4 LoRA', 'Qwen-Omni', 'API Integration']}
              className="md:col-span-1 lg:col-span-1"
            />
            <MatchCard
              delay={0.1}
              requirement="대화형 AI Agent 설계"
              evidence="캐릭터별 인격을 가진 AI. 발화 트리거 + 패치노트 RAG 맥락 주입 + GCS 메모리로 멀티턴 대화 구현."
              techs={['Prompt Eng', 'RAG Context', 'GCS Multi-turn']}
              className="md:col-span-1 lg:col-span-1"
            />
            <MatchCard
              delay={0.15}
              requirement="업무 자동화 및 생산성 향상"
              evidence="Claude Code CLI 파이프라인. Figma/Context7 MCP 연동으로 프론트엔드 구현부터 배포까지 AI 기반 자동 생성 도입."
              techs={['Claude Code', 'MCP Server', 'AI Dev']}
              className="md:col-span-2 lg:col-span-2"
            />
            <MatchCard
              delay={0.2}
              requirement="풀스택 역량 (프론트/백/인프라)"
              evidence="React 19, Tailwind 4 (프론트) / Flask, Gunicorn (백엔드) / Docker, Nginx, GCP (인프라). 전 과정 1인 풀스택 개발."
              techs={['React 19', 'Flask', 'Docker', 'GCP', 'Nginx']}
              className="md:col-span-2 lg:col-span-2"
            />
            <MatchCard
              delay={0.25}
              requirement="프롬프트/데이터 구조화 설계"
              evidence="프롬프트 튜닝으로 '음성 봇이 들린 말을 그대로 대답하는 문제' 파훼. 대사 분리 파서(Speaker Parsing) 구현."
              techs={['System Prompt', 'LLM Parsing']}
              className="md:col-span-1 lg:col-span-1"
            />
          </div>

          {/* 우대사항 */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-6`} style={{ color: ACCENT2 }}>
              Preferred
            </h3>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <MatchCard
              delay={0}
              requirement="LLM 챗봇, RAG 구축/운영"
              evidence="최신 게임 패치노트를 벡터 없이 키워드로 컴팩트하게 검색해 LLM 시스템 프롬프트에 주입(Patchnote RAG)."
              techs={['Patchnote RAG', 'Context Window']}
              className="md:col-span-1"
            />
            <MatchCard
              delay={0.05}
              requirement="AI 도구 활용 및 리팩토링"
              evidence="전체 사이트를 Claude Code와 MCP(Figma, 문서 도구) 기반으로 자동화 설계 및 최적화하여 10배 생산성 확보."
              techs={['Claude Code', 'AI-first', 'Systematic Gen']}
              className="md:col-span-1"
            />
            <MatchCard
              delay={0.1}
              requirement="AX(AI Transformation) 사례 구축"
              evidence="웹사이트를 직접 방문해야 했던 전적 검색과 패치노트 확인을 Discord 안으로 이관. 키워드 호출('데비야')만으로 패치노트 RAG가 캐릭터 말투로 답변하고, 슬래시 커맨드로 전적 조회. 유저가 컨텍스트 스위칭 없이 게임 대화 중에 즉시 정보 획득."
              techs={['Keyword Trigger', 'Patchnote RAG', 'Slash Commands', 'Context Reduction']}
              className="md:col-span-1"
            />
            <MatchCard
              delay={0.15}
              requirement="AWS/클라우드 운영 기반"
              evidence="GCP Compute Engine 프로덕션 환경 + Docker/nginx. CI/CD를 Makefile 기반으로 파이프라인 관리."
              techs={['GCP', 'Docker/Nginx', 'Makefile CICD']}
              className="md:col-span-1"
            />
          </div>
        </div>
      </section>

      {/* ══ AI PIPELINE ══ */}
      <section id="pipeline" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#6DC8E8] to-[#0B5ED7] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              AI Pipeline
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                텍스트 채팅과 음성 대화, 두 채널의 AI 파이프라인.
              </p>
            </FadeIn>
          </div>

          <div className="mb-12 flex justify-center">
            <FadeIn>
              <div className={`inline-flex p-1.5 rounded-2xl ${isDark ? 'bg-[#000000]/30 border border-white/[0.06]' : 'bg-gray-100/50 border border-gray-200'}`}>
                <button 
                  onClick={() => setPipelineTab('text')}
                  className={`px-8 py-3 rounded-xl text-sm font-bold transition-all duration-300 ${pipelineTab === 'text' ? (isDark ? 'bg-[#0B5ED7]/20 text-white shadow-lg border border-[#0B5ED7]/30' : 'bg-white text-[#0B5ED7] shadow-sm border border-gray-200/50') : (isDark ? 'text-gray-500 hover:text-gray-300 border border-transparent' : 'text-gray-500 hover:text-gray-700 border border-transparent')}`}
                >
                  <span className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${pipelineTab === 'text' ? 'animate-pulse' : ''}`} style={{ backgroundColor: ACCENT }} />
                    Text Chat
                  </span>
                </button>
                <button 
                  onClick={() => setPipelineTab('voice')}
                  className={`px-8 py-3 rounded-xl text-sm font-bold transition-all duration-300 ${pipelineTab === 'voice' ? (isDark ? 'bg-[#6DC8E8]/20 text-white shadow-lg border border-[#6DC8E8]/30' : 'bg-white text-[#0B5ED7] shadow-sm border border-gray-200/50') : (isDark ? 'text-gray-500 hover:text-gray-300 border border-transparent' : 'text-gray-500 hover:text-gray-700 border border-transparent')}`}
                >
                  <span className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${pipelineTab === 'voice' ? 'animate-pulse' : ''}`} style={{ backgroundColor: ACCENT2 }} />
                    Voice Chat
                  </span>
                </button>
              </div>
            </FadeIn>
          </div>

          <div className="relative min-h-[300px]">
             {pipelineTab === 'text' && (
                <motion.div
                  key="text"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.4, ease: [0.04, 0.62, 0.23, 0.98] }}
                  className="flex flex-col md:flex-row gap-8 md:gap-0 mt-8"
                >
                  <PipelineNode step={1} title="키워드 트리거" desc="'데비야', '마를렌아' 호출 감지. LangGraph StateGraph로 진입." techs={['discord.py', 'LangGraph']} delay={0} />
                  <PipelineNode step={2} title="의도 분류 (분기)" desc="regex 기반 classify_intent 노드. patch 키워드 있으면 RAG, 없으면 skip." techs={['Conditional Edge']} delay={0.05} />
                  <PipelineNode step={3} title="컨텍스트 수집" desc="fetch_patchnote (조건부) → fetch_memory (GCS corrections). 필요할 때만 실행." techs={['RAG', 'GCS', 'TypedDict State']} delay={0.1} />
                  <PipelineNode step={4} title="LLM + 응답 전송" desc="call_llm 노드 → Modal A10G Gemma4 LoRA. Components V2 UI로 Discord 전송." techs={['Gemma4 LoRA', 'Modal', 'Components V2']} delay={0.15} isLast />
                </motion.div>
              )}
              
              {pipelineTab === 'voice' && (
                <motion.div
                  key="voice"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.4, ease: [0.04, 0.62, 0.23, 0.98] }}
                  className="flex flex-col md:flex-row gap-8 md:gap-0 mt-8"
                >
                  <PipelineNode step={1} title="음성 수신 / 복호화" desc="음성 패킷 수신. Transport 및 DAVE E2EE 2차 복호화 수행." techs={['voice_recv', 'DAVE E2EE']} delay={0} />
                  <PipelineNode step={2} title="VAD 발화 감지" desc="16kHz 다운샘플 -> WebRTC VAD. 0.5초 프리버퍼로 시작 영역 보존." techs={['VAD', 'Opus Decoder']} delay={0.05} />
                  <PipelineNode step={3} title="하이브리드 웨이크워드" desc="짧은 발화: 게임 음성 재생 후 듣기. 긴 발화: 즉시 Omni 모델 추론." techs={['Hybrid Wakeword']} delay={0.1} />
                  <PipelineNode step={4} title="Omni + TTS" desc="Qwen3.5-Omni로 상황 파악. 화자별 대사 분리 후 CosyVoice3로 재생." techs={['Qwen-Omni', 'CosyTTS']} delay={0.15} isLast />
                </motion.div>
              )}
          </div>

          {/* LangGraph StateGraph -- Actual draw_mermaid() output */}
          {pipelineTab === 'text' && (
            <FadeIn delay={0.1} className="mt-20">
              <div className="text-center mb-6">
                <h3 className={`text-sm font-bold uppercase tracking-wider ${isDark ? 'text-[#6DC8E8]' : 'text-[#0B5ED7]'}`}>
                  LangGraph StateGraph
                </h3>
                <p className={`text-xs mt-2 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  아래 다이어그램은 <code className={`px-1.5 py-0.5 rounded ${isDark ? 'bg-white/[0.05] text-[#6DC8E8]' : 'bg-gray-100 text-[#0B5ED7]'}`}>graph.get_graph().draw_mermaid()</code> 실행 결과를 그대로 렌더링한 것.
                </p>
              </div>
              <GlassCard className="p-6 md:p-10 rounded-3xl">
                <MermaidDiagram chart={CHAT_AGENT_MERMAID} className="[&_svg]:w-full [&_svg]:h-auto [&_svg]:max-w-2xl [&_svg]:mx-auto" />
              </GlassCard>
              <div className="grid md:grid-cols-2 gap-4 mt-6">
                <GlassCard className="p-5 rounded-2xl">
                  <div className={`text-[11px] font-bold uppercase tracking-wider mb-2 ${isDark ? 'text-red-400' : 'text-red-500'}`}>Before -- 선형 if-else</div>
                  <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    모든 메시지에 패치노트 RAG 호출 (평균 100~300ms). '데비야 안녕' 같은 잡담도 네트워크 hop 발생.
                  </p>
                </GlassCard>
                <GlassCard className="p-5 rounded-2xl">
                  <div className={`text-[11px] font-bold uppercase tracking-wider mb-2 ${isDark ? 'text-emerald-400' : 'text-emerald-500'}`}>After -- StateGraph + Conditional Edge</div>
                  <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    classify_intent가 regex로 patch 키워드를 0.1ms에 판별. 잡담은 skip_patchnote로 우회, RAG 비용 0.
                  </p>
                </GlassCard>
              </div>
            </FadeIn>
          )}

          {/* Model Selection Journey */}
          <FadeIn delay={0.2} className="mt-16">
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-6 text-center ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              Model Selection Journey -- 6 Attempts
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {[
                { name: 'Qwen2.5-Omni-7B', result: 'FAIL', reason: '파인튜닝 과적합 (loss 0.15)' },
                { name: 'Qwen3.5-9B', result: 'FAIL', reason: 'linear_attention Windows 미지원' },
                { name: 'Gemma4 E4B', result: 'TEXT', reason: 'Unsloth LoRA 텍스트 채팅 성공' },
                { name: 'Gemma4 Omni', result: 'REPLACED', reason: '오디오 이해 동작, 품질 낮음' },
                { name: 'Qwen3-Omni-30B', result: 'FAIL', reason: 'vLLM A100-40GB에서도 OOM' },
                { name: 'Qwen3.5-Omni+', result: 'ADOPTED', reason: 'DashScope API, 품질/비용 최적' },
              ].map((m, i) => (
                <FadeIn key={i} delay={0.05 * i}>
                  <div className={`px-3 py-3 rounded-xl border text-center ${
                    m.result === 'ADOPTED'
                      ? isDark ? 'bg-[#0B5ED7]/10 border-[#0B5ED7]/30' : 'bg-[#0B5ED7]/[0.06] border-[#0B5ED7]/20'
                      : m.result === 'TEXT'
                        ? isDark ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-emerald-50 border-emerald-200/50'
                        : isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/80 border-gray-200'
                  }`}>
                    <div className={`text-xs font-bold mb-1 ${
                      m.result === 'ADOPTED' ? 'text-[#0B5ED7]'
                        : m.result === 'TEXT' ? 'text-emerald-400'
                          : isDark ? 'text-white' : 'text-gray-800'
                    }`}>{m.name}</div>
                    <div className={`text-xs px-2 py-0.5 rounded-full inline-block mb-1 ${
                      m.result === 'ADOPTED' ? 'bg-[#0B5ED7]/20 text-[#0B5ED7]'
                        : m.result === 'TEXT' ? 'bg-emerald-500/20 text-emerald-400'
                          : m.result === 'REPLACED' ? 'bg-amber-500/20 text-amber-400'
                            : isDark ? 'bg-white/[0.05] text-gray-500' : 'bg-gray-100 text-gray-500'
                    }`}>{m.result}</div>
                    <div className={`text-[10px] leading-tight ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{m.reason}</div>
                  </div>
                </FadeIn>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ TROUBLESHOOTING ══ */}
      <section id="troubleshoot" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              Troubleshooting
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                AI 서비스 구축 과정에서 만난 실제 문제들과 해결 과정.
              </p>
            </FadeIn>
          </div>

          {/* AI/LLM */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-4`} style={{ color: ACCENT }}>
              AI / LLM
            </h3>
          </FadeIn>
          <div className="space-y-4 mb-12">
            <TroubleshootCard
              title="Qwen3-Omni 셀프호스팅 실패 (MoE 아키텍처)"
              problem="Qwen3-Omni-30B-A3B를 A100 40GB에서 셀프호스팅 시도했으나 transformers는 응답 없고, vLLM은 CUDA OOM."
              cause="MoE 모델은 활성 파라미터가 3B지만 전체 30B 가중치를 메모리에 로드해야 함. transformers는 MoE 추론이 극도로 느리고, vLLM은 engine v1 미지원."
              solution="셀프호스팅을 포기하고 DashScope API로 전환. OpenAI SDK 호환(base_url만 변경)으로 코드 변경 최소화. 비용도 월 $46 -> $0.27로 170배 절감."
              color={ACCENT}
              delay={0}
            />
            <TroubleshootCard
              title="DAVE E2EE 2차 암호화 (Discord 음성)"
              problem="Discord 음성채널에서 수신한 오디오가 전부 노이즈. transport 복호화만으로는 원본 오디오를 얻을 수 없음."
              cause="Discord가 2024년부터 DAVE(Discord Audio & Video End-to-End Encryption)를 강제 적용. voice_recv 라이브러리는 transport 암호화만 풀어줌."
              solution="davey 라이브러리로 DAVE 2차 복호화를 직접 구현. DaveSession.decrypt(user_id, MediaType.audio, data) 호출 추가."
              color={ACCENT}
              delay={0.05}
            />
            <TroubleshootCard
              title="TTS가 화자 태그까지 읽어버림"
              problem="'데비: 안녕!' 이라는 응답을 TTS가 '데비 콜론 안녕'으로 읽음."
              cause="LLM 응답에 포함된 화자 태그(데비:, 마를렌:)를 제거하지 않고 TTS에 전달."
              solution="parse_character_lines() 함수로 응답을 화자별로 분리, 태그 제거 후 각각 다른 CosyVoice3 음성 모델로 TTS 재생."
              color={ACCENT2}
              delay={0.1}
            />
            <TroubleshootCard
              title="VAD 발화 끝 감지 안 됨"
              problem="말을 멈춰도 발화 종료가 감지되지 않아 feed #500까지 speaking=True 상태 지속."
              cause="배경 소음으로 WebRTC VAD의 silence_count가 계속 리셋. 1.5초 무음 조건을 충족하지 못함."
              solution="SILENCE_FRAMES를 1.5초에서 0.7초로, MAX_SPEECH_SEC를 25초에서 8초로 조정. 환경 소음에 대한 허용 범위 확대."
              color={ACCENT2}
              delay={0.15}
            />
          </div>

          {/* Infrastructure */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-4`} style={{ color: '#43b581' }}>
              Infrastructure
            </h3>
          </FadeIn>
          <div className="space-y-4">
            <TroubleshootCard
              title="CosyVoice3 bfloat16 비트박스 현상"
              problem="T4 GPU에서 파인튜닝된 모델로 추론하면 음성 대신 비트박스 소리가 출력."
              cause="pretrained checkpoint가 bfloat16으로 저장되어 있어 float16으로 변환해도 모델 로드 시 덮어써짐. T4는 bfloat16 하드웨어 미지원."
              solution="T4에서도 bfloat16을 소프트웨어 에뮬레이션으로 사용하도록 강제. pretrained 구조를 건드리지 않고 런타임에서 해결."
              color="#43b581"
              delay={0}
            />
            <TroubleshootCard
              title="Modal Cold Start 58초 -> 워밍업 전략"
              problem="Modal Serverless에 배포한 TTS 서버의 콜드 스타트가 58초. 첫 요청 시 유저가 1분 대기."
              cause="매 콜드 스타트마다 HuggingFace에서 600MB+ 모델 다운로드 + GPU 로드."
              solution="/tts 명령으로 음성채널 입장 시 서버 미리 워밍업. Volume 캐싱으로 warm RTF 1.5~2.2x 달성. 워밍업 상태를 Discord UI에 시각적으로 표시."
              color="#43b581"
              delay={0.05}
            />
          </div>
        </div>
      </section>

      {/* ══ FEATURES ══ */}
      <section id="features" ref={featuresContainerRef} className="relative overflow-hidden h-screen">
        {/* Fixed section title while pinned */}
        <div className="absolute top-8 left-0 right-0 z-20 text-center pointer-events-none">
          <div className="font-title bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent text-3xl md:text-5xl">
            Features
          </div>
          <div className={`text-xs tracking-[0.3em] uppercase mt-2 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
            Scroll down to pan
          </div>
        </div>

        <div ref={featuresTrackRef} className="flex h-full will-change-transform">
          {/* Feature 1: AI 대화 */}
          <div className="feature-card shrink-0 w-screen h-full flex items-center justify-center px-6 md:px-16">
            <GlassCard className="w-full max-w-6xl p-8 md:p-12 rounded-[32px]">
              <div className="grid md:grid-cols-2 gap-12 items-center w-full">
                <div className="space-y-6">
                  <SVGTitle lines={['AI', '대화']} />
                  <p className={`font-bold text-xl md:text-2xl leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-800'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                    캐릭터 인격 기반 대화형 AI Agent.
                  </p>
                  <p className={`text-base leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Gemma4 LoRA 파인튜닝 모델로 캐릭터 말투와 성격을 학습.
                    패치노트 RAG로 최신 게임 정보를 반영하고,
                    GCS 기반 대화 메모리로 세션 간 맥락을 유지하는 멀티턴 대화.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {['Gemma4 LoRA', 'Modal A10G', 'Patchnote RAG', 'GCS Memory'].map(t => (
                      <span key={t} className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${isDark ? 'bg-white/[0.05] text-[#6DC8E8] border-white/[0.08]' : 'bg-[#0B5ED7]/5 text-[#0B5ED7] border-[#0B5ED7]/20'}`}>{t}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <img src={SS_AI_CHAT} alt="AI 대화 - 키워드 트리거 + 패치노트 RAG" className="w-full h-auto max-h-[55vh] object-contain rounded-2xl shadow-2xl" draggable={false} />
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Feature 2: 음성 Agent */}
          <div className="feature-card shrink-0 w-screen h-full flex items-center justify-center px-6 md:px-16">
            <GlassCard className="w-full max-w-6xl p-8 md:p-12 rounded-[32px]">
              <div className="grid md:grid-cols-2 gap-12 items-center w-full">
                <div className="order-2 md:order-1">
                  <img src={SS_TTS_SETTINGS} alt="TTS 설정" className="w-full h-auto max-h-[55vh] object-contain rounded-2xl shadow-2xl" draggable={false} />
                </div>
                <div className="order-1 md:order-2 space-y-6">
                  <SVGTitle lines={['음성', 'Agent']} />
                  <p className={`font-bold text-xl md:text-2xl leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-800'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                    실시간 음성 이해와 TTS 응답.
                  </p>
                  <p className={`text-base leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Discord DAVE E2EE 음성 스트림 수신,
                    WebRTC VAD 발화 감지, Qwen3.5-Omni 오디오 이해.
                    화자별 CosyVoice3 파인튜닝으로 캐릭터 음성 생성.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {['Qwen3.5', 'CosyVoice3', 'WebRTC VAD'].map(t => (
                      <span key={t} className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${isDark ? 'bg-white/[0.05] text-[#6DC8E8] border-white/[0.08]' : 'bg-[#0B5ED7]/5 text-[#0B5ED7] border-[#0B5ED7]/20'}`}>{t}</span>
                    ))}
                  </div>
                  <div className="space-y-2 mt-2">
                    {[ { label: 'Debi', src: '/audio/demo_debi_desc.wav' }, { label: 'Marlene', src: '/audio/demo_marlene_desc.wav' } ].map(s => (
                      <div key={s.label} className={`flex items-center gap-3 px-4 py-2.5 rounded-[16px] border ${isDark ? 'bg-black/40 border-white/10' : 'bg-white border-gray-200 shadow-sm'}`}>
                        <span className="shrink-0 text-xs font-bold w-12" style={{ color: ACCENT }}>{s.label}</span>
                        <audio controls preload="none" className="w-full h-8 [&::-webkit-media-controls-panel]:bg-transparent"><source src={s.src} type="audio/wav" /></audio>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Feature 3: 웹 대시보드 */}
          <div className="feature-card shrink-0 w-screen h-full flex items-center justify-center px-6 md:px-16">
            <GlassCard className="w-full max-w-6xl p-8 md:p-12 rounded-[32px]">
              <div className="grid md:grid-cols-2 gap-12 items-center w-full">
                <div className="space-y-6">
                  <SVGTitle lines={['웹', '대시보드']} />
                  <p className={`font-bold text-xl md:text-2xl leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-800'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                    Discord OAuth2 관리 웹앱.
                  </p>
                  <p className={`text-base leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    서버별 봇 설정, TTS 속도 등 통합 커스터마이징. Toss Payments SDK 연동으로 후원 시스템 구축.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {['React 19', 'Flask', 'Toss Payments'].map(t => (
                      <span key={t} className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${isDark ? 'bg-white/[0.05] text-[#6DC8E8] border-white/[0.08]' : 'bg-[#0B5ED7]/5 text-[#0B5ED7] border-[#0B5ED7]/20'}`}>{t}</span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-1 gap-3">
                  <img src={SS_DASHBOARD} alt="대시보드" className="w-full h-auto max-h-[26vh] object-contain rounded-2xl shadow-2xl" draggable={false} />
                  <img src={SS_STATUSLINE} alt="Statusline Preview" className="w-full h-auto max-h-[26vh] object-contain rounded-2xl shadow-2xl" draggable={false} />
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Feature 4: 운영 도구 */}
          <div className="feature-card shrink-0 w-screen h-full flex items-center justify-center px-6 md:px-16">
            <GlassCard className="w-full max-w-6xl p-8 md:p-12 rounded-[32px]">
              <div className="grid md:grid-cols-2 gap-12 items-center w-full">
                <div className="order-2 md:order-1 grid grid-cols-1 gap-3">
                  <img src={SS_STATS} alt="전적 통계" className="w-full h-auto max-h-[26vh] object-contain rounded-2xl shadow-2xl" draggable={false} />
                  <img src={SS_WEBPANEL} alt="웹패널" className="w-full h-auto max-h-[26vh] object-contain rounded-2xl shadow-2xl" draggable={false} />
                </div>
                <div className="order-1 md:order-2 space-y-6">
                  <SVGTitle lines={['운영', '도구']} />
                  <p className={`font-bold text-xl md:text-2xl leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-800'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                    전적 검색 + 관리자 모니터링.
                  </p>
                  <p className={`text-base leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    dak.gg API를 리버스 엔지니어링하여 수집. 관리자 웹패널(SSE)로 봇 사용량 및 지연 시간 실시간 스트리밍 모니터링.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {['dak.gg API', 'Flask SSE', 'Nginx', 'Components V2'].map(t => (
                      <span key={t} className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${isDark ? 'bg-white/[0.05] text-[#6DC8E8] border-white/[0.08]' : 'bg-[#0B5ED7]/5 text-[#0B5ED7] border-[#0B5ED7]/20'}`}>{t}</span>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>

        {/* Scroll hint while pinned */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-2 z-20 pointer-events-none">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`animate-pulse ${isDark ? 'text-gray-500' : 'text-gray-400'}`}><path d="M12 5v14M5 12l7 7 7-7"/></svg>
          <span className={`text-[11px] font-bold tracking-[0.25em] uppercase ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Scroll</span>
        </div>
      </section>

      {/* ══ ARCHITECTURE ══ */}
      <section id="architecture" className="py-24 relative">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#6DC8E8] to-[#0B5ED7] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              Architecture
            </ScrollFloat>
          </div>

          <FadeIn>
            <GlassCard className="p-6 md:p-10 rounded-3xl">
              <div className="relative">
                <div className={`absolute -top-[100px] left-[50%] -translate-x-[50%] w-[500px] h-[300px] blur-[120px] pointer-events-none ${isDark ? 'bg-[#0B5ED7]/15' : 'bg-[#0B5ED7]/[0.08]'}`} />
                <MermaidDiagram chart={ARCHITECTURE_MERMAID} className="relative z-10 [&_svg]:w-full [&_svg]:h-auto [&_svg]:max-w-full" />
                <p className={`relative z-10 text-center text-xs mt-6 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  * 이 다이어그램은 Mermaid.js로 데이터 기반 렌더링. 서비스 추가 시 하드코딩 없이 텍스트만 수정.
                </p>
              </div>
            </GlassCard>
          </FadeIn>
        </div>
      </section>

      {/* ══ TECH STACK ══ */}
      <section id="techstack" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              Tech Stack
            </ScrollFloat>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: 'AI / ML',
                color: 'text-indigo-400',
                hex: '#818cf8',
                items: [
                  { name: 'Gemma4 E4B', desc: 'LoRA 파인튜닝, Unsloth, bfloat16' },
                  { name: 'Qwen3.5-Omni', desc: 'DashScope API, 오디오 이해' },
                  { name: 'CosyVoice3', desc: 'TTS 파인튜닝, Modal T4 배포' },
                  { name: 'WebRTC VAD', desc: '실시간 음성 활동 감지' },
                ],
              },
              {
                title: 'Backend',
                color: 'text-emerald-400',
                hex: '#34d399',
                items: [
                  { name: 'Python', desc: 'discord.py 2.6, asyncio' },
                  { name: 'Flask', desc: 'REST API x2, Gunicorn' },
                  { name: 'Modal', desc: 'Serverless GPU (A10G, T4)' },
                  { name: 'GCS', desc: '설정, 대화 메모리 저장소' },
                ],
              },
              {
                title: 'Frontend',
                color: 'text-pink-400',
                hex: '#f472b6',
                items: [
                  { name: 'React 19', desc: 'TypeScript, Vite' },
                  { name: 'Tailwind 4', desc: 'Utility-first CSS' },
                  { name: 'Framer Motion', desc: '애니메이션, 트랜지션' },
                  { name: 'OAuth2', desc: 'Discord 로그인 연동' },
                ],
              },
              {
                title: 'Infrastructure',
                color: 'text-amber-400',
                hex: '#fbbf24',
                items: [
                  { name: 'GCP VM', desc: 'Compute Engine, Seoul' },
                  { name: 'Docker', desc: '컨테이너 빌드/배포' },
                  { name: 'nginx', desc: 'Reverse proxy, SSL' },
                  { name: 'Cloudflare', desc: 'CDN, DNS, 캐시 퍼지' },
                ],
              },
              {
                title: 'DevOps',
                color: 'text-violet-400',
                hex: '#a78bfa',
                items: [
                  { name: 'Makefile', desc: '빌드/배포/롤백 자동화' },
                  { name: 'Artifact Registry', desc: 'Docker 이미지 관리' },
                  { name: 'HuggingFace', desc: '모델 버전 관리' },
                  { name: 'Colab', desc: 'A100/T4 파인튜닝' },
                ],
              },
              {
                title: 'AI Dev Tools',
                color: 'text-sky-400',
                hex: '#38bdf8',
                items: [
                  { name: 'Claude Code', desc: '주 개발 도구, CLI' },
                  { name: 'MCP Server', desc: 'Figma, Context7, NLM' },
                  { name: 'Exa', desc: '시맨틱 웹 검색' },
                  { name: 'Obsidian', desc: '지식 관리, TODO' },
                ],
              },
            ].map((cat, i) => (
              <FadeIn key={cat.title} delay={i * 0.05} className="h-full">
                <GlassCard className={`group relative p-8 rounded-[32px] transition-all duration-300 h-full ${isDark ? 'hover:bg-white/[0.04]' : 'hover:-translate-y-1'}`}>
                {/* Dynamic Glow via style property to inject valid hex colors */}
                <div className={`absolute top-0 right-[-20px] w-32 h-32 blur-[50px] transition-opacity duration-500 opacity-20 group-hover:opacity-100 z-0 pointer-events-none`} style={{ backgroundColor: cat.hex }} />
                
                <h3 className={`text-sm font-bold uppercase tracking-widest mb-6 relative z-10 ${cat.color}`}>{cat.title}</h3>
                <div className="space-y-5 relative z-10">
                  {cat.items.map(item => (
                    <div key={item.name} className="flex flex-col gap-1.5">
                      <span className={`text-[15px] font-bold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                        {item.name}
                      </span>
                      <span className={`text-sm leading-relaxed ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{item.desc}</span>
                    </div>
                  ))}
                </div>
                </GlassCard>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ══ COST ANALYSIS ══ */}
      <section id="cost" className="py-24 relative">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#6DC8E8] to-[#0B5ED7] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              Cost Analysis
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                셀프호스팅 vs API, 비용 최적화 의사결정 과정.
              </p>
            </FadeIn>
          </div>

          <FadeIn>
            <div className="grid md:grid-cols-2 gap-6 relative">
              <div className="absolute top-[40%] left-1/2 -translate-x-[50%] -translate-y-1/2 z-10 hidden md:flex items-center justify-center w-12 h-12 rounded-full border shadow-[0_8px_30px_rgb(0,0,0,0.12)] transition-transform hover:rotate-180 hover:scale-110 duration-500 cursor-pointer text-gray-500 dark:text-gray-400 bg-white dark:bg-[#1a1a2e] border-gray-100 dark:border-white/10">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </div>

              {/* Before */}
              <GlassCard className="p-8 rounded-[32px] transition-opacity duration-300 opacity-70 hover:opacity-100 h-full">
                <div className="text-xs font-bold uppercase tracking-widest text-[#ed4245] flex items-center gap-2 mb-6">
                   <div className="w-1.5 h-1.5 rounded-full bg-[#ed4245]" />
                   Before: Self-Hosted Model
                </div>
                <div className="space-y-4">
                  <div>
                    <div className={`text-sm font-medium mb-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Voice AI (Modal A10G)</div>
                    <div className={`text-3xl lg:text-4xl font-bold font-mono ${isDark ? 'text-white' : 'text-gray-800'}`}>~$46<span className="text-base font-normal text-gray-500">/mo</span></div>
                    <div className="text-sm font-bold text-[#ed4245] mt-2">Cold Start: 60s+</div>
                  </div>
                </div>
              </GlassCard>

              {/* After */}
              <GlassCard className="group p-8 rounded-[32px] h-full transition-all duration-500">
                <div className="absolute -top-12 -right-12 w-48 h-48 bg-[#0B5ED7]/20 blur-[60px] rounded-full group-hover:scale-150 transition-transform duration-700 pointer-events-none" />
                <div className="text-xs font-bold uppercase tracking-widest text-[#0B5ED7] flex items-center gap-2 mb-6">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#0B5ED7] animate-pulse" />
                  After: API Transition
                </div>
                <div className="space-y-4 relative z-10">
                  <div>
                    <div className={`text-sm font-medium mb-1 ${isDark ? 'text-blue-300/80' : 'text-blue-600/80'}`}>Voice AI (DashScope API)</div>
                    <div className={`text-4xl lg:text-5xl font-bold font-mono text-[#0B5ED7]`}>~$0.27<span className="text-lg font-normal opacity-50">/mo</span></div>
                    <div className="text-sm text-[#0B5ED7] font-bold mt-2">Cold Start: 0s</div>
                  </div>
                </div>
                
                <div className="mt-8 pt-6 border-t border-[#0B5ED7]/20 relative z-10">
                  <div className={`text-sm leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                    OpenAI SDK 기반 프록시 전환으로 코드는 유지하며 <span className="font-bold text-[#0B5ED7] bg-[#0B5ED7]/10 px-1 rounded">170배의 비용을 절감</span>했습니다.
                  </div>
                </div>
              </GlassCard>
            </div>
            
            {/* Additional Costs Summary */}
            <GlassCard className="mt-6 p-6 rounded-[32px]">
              <div className="grid grid-cols-3 gap-4 text-center divide-x divide-gray-200 dark:divide-white/10">
                {[
                  { name: 'Text Chat AI', val: '~$46', sub: 'Modal A10G (Gemma4 LoRA)' },
                  { name: 'Voice TTS', val: '~$15', sub: 'Modal T4 (CosyVoice3)' },
                  { name: 'Infrastructure', val: '~$7', sub: 'GCP e2-micro VM' },
                ].map(s => (
                  <div key={s.name} className="px-4">
                     <div className={`text-xs font-bold uppercase tracking-wider mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{s.name}</div>
                     <div className={`text-xl font-bold font-mono ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>{s.val}</div>
                     <div className={`text-[10px] sm:text-xs mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{s.sub}</div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </FadeIn>
        </div>
      </section>

      {/* ══ FOOTER ══ */}
      <footer className={`py-16 border-t ${isDark ? 'border-white/[0.06]' : 'border-gray-200'}`}>
        <div className="max-w-4xl mx-auto px-6 text-center">
          <FadeIn>
            <GradientText
              colors={[ACCENT, ACCENT2, '#4A9BE8', ACCENT2, ACCENT]}
              animationSpeed={5}
              className="font-title text-2xl md:text-4xl mb-4"
              pauseOnHover
            >
              Yang Gunho
            </GradientText>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
              NEXON -- AI Agent Full-Stack Engineer
            </p>
            <div className="flex justify-center gap-4 mt-6">
              <GlassButton href="https://github.com/2rami" target="_blank" rel="noopener noreferrer" size="sm">GitHub</GlassButton>
              <GlassButton href="/portfolio" size="sm">All Portfolios</GlassButton>
            </div>
          </FadeIn>
        </div>
      </footer>
    </div>
  )
}
