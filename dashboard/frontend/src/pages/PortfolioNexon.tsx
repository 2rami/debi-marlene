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
import TWINS_APPROVE from '../assets/images/event/236_twins_approve.png'
import BG_FOOTER from '../assets/images/event/footer_bg.png'
import FOOTER_PLATFORM from '../assets/images/event/footer_platform.png'
import FOOTER_CHAR from '../assets/images/event/footer_char.png'

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
            <svg viewBox={`0 0 ${vw} 250`} className="w-[220px] md:w-[380px] lg:w-[480px] h-auto overflow-visible block">
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
/* ── Section Navigator ── */
const SECTIONS = [
  { id: 'hero', label: 'Hero' },
  { id: 'match', label: 'JD Match' },
  { id: 'pipeline', label: 'AI Pipeline' },
  { id: 'troubleshoot', label: 'Troubleshooting' },
  { id: 'features', label: 'Features' },
  { id: 'architecture', label: 'Architecture' },
  { id: 'techstack', label: 'Tech Stack' },
]

function SectionNav() {
  const { isDark, toggle } = useTheme()
  const [active, setActive] = useState('hero')
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight
      setProgress(max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0)

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
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <motion.nav
      initial={{ opacity: 0, x: 40 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.9, delay: 1.0, ease: [0.22, 1, 0.36, 1] }}
      className="group fixed right-3 top-1/2 -translate-y-1/2 z-40 max-md:hidden opacity-30 hover:opacity-100 transition-opacity duration-300"
    >
      <div className={`relative py-3 pr-3 pl-3 group-hover:py-5 group-hover:pr-5 group-hover:pl-5 rounded-2xl border backdrop-blur-md transition-all duration-300 ${
        isDark
          ? 'bg-white/[0.02] border-white/[0.05] group-hover:bg-white/[0.04] group-hover:border-white/[0.08] shadow-[0_8px_24px_rgba(0,0,0,0.25)]'
          : 'bg-white/40 border-[#0B5ED7]/10 group-hover:bg-white/70 group-hover:border-[#0B5ED7]/15 shadow-[0_8px_24px_rgba(11,94,215,0.08)]'
      }`}>
        {/* Top corner glow */}
        <div className={`absolute -top-2 -right-2 w-16 h-16 rounded-full blur-2xl pointer-events-none ${
          isDark ? 'bg-[#6DC8E8]/10' : 'bg-[#0B5ED7]/15'
        }`} />

        <ul className="relative flex flex-col gap-4 group-hover:gap-5 transition-all duration-300">
          {/* Vertical progress rail — aligned to dot column center */}
          <div className={`absolute left-[7px] group-hover:left-[33px] top-2 bottom-2 w-[2px] rounded-full overflow-hidden pointer-events-none transition-all duration-300 ${
            isDark ? 'bg-white/[0.08]' : 'bg-[#0B5ED7]/10'
          }`}>
            <div
              className="w-full bg-gradient-to-b from-[#0B5ED7] to-[#6DC8E8] origin-top transition-transform duration-300 ease-out"
              style={{ height: '100%', transform: `scaleY(${progress})` }}
            />
          </div>

          {SECTIONS.map((s, i) => {
            const isActive = active === s.id
            const number = String(i + 1).padStart(2, '0')
            return (
              <li key={s.id} className="relative">
                <button
                  onClick={() => document.getElementById(s.id)?.scrollIntoView({ behavior: 'smooth' })}
                  className="flex items-center gap-3 w-full cursor-pointer text-left"
                >
                  {/* Section number — hidden by default, appears on nav hover */}
                  <span className={`text-[10px] font-mono font-bold tabular-nums tracking-wider transition-all duration-300 max-w-0 opacity-0 group-hover:max-w-[14px] group-hover:opacity-100 overflow-hidden ${
                    isActive
                      ? 'text-[#0B5ED7]'
                      : isDark
                        ? 'text-white/60'
                        : 'text-gray-500'
                  }`}>
                    {number}
                  </span>

                  {/* Dot with halo + pulse — sits on top of the rail */}
                  <div className="relative flex items-center justify-center w-4 h-4 shrink-0 z-10">
                    {isActive && (
                      <>
                        <motion.div
                          layoutId="nav-halo-nexon"
                          className="absolute inset-[-7px] rounded-full bg-gradient-to-br from-[#0B5ED7]/50 to-[#6DC8E8]/50 blur-[6px]"
                          transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                        />
                        <motion.div
                          className="absolute inset-[-3px] rounded-full border-2 border-[#0B5ED7]/50"
                          animate={{ scale: [1, 1.4, 1], opacity: [0.8, 0, 0.8] }}
                          transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
                        />
                      </>
                    )}
                    <div className={`rounded-full transition-all duration-300 relative z-10 ${
                      isActive
                        ? 'w-[13px] h-[13px] bg-gradient-to-br from-[#0B5ED7] to-[#6DC8E8] shadow-[0_0_14px_rgba(11,94,215,0.7)]'
                        : isDark
                          ? 'w-[9px] h-[9px] bg-white/30 group-hover:bg-white/60 group-hover:scale-110'
                          : 'w-[9px] h-[9px] bg-gray-300 group-hover:bg-[#0B5ED7]/60 group-hover:scale-110'
                    }`} />
                  </div>

                  {/* Label — collapsed by default, expands on nav hover */}
                  <span className={`text-[13px] font-semibold tracking-wide whitespace-nowrap transition-all duration-300 max-w-0 opacity-0 overflow-hidden group-hover:max-w-[120px] group-hover:opacity-100 ${
                    isActive
                      ? 'text-[#0B5ED7]'
                      : isDark
                        ? 'text-white/80'
                        : 'text-gray-700'
                  }`}>
                    {s.label}
                  </span>
                </button>
              </li>
            )
          })}
        </ul>

        {/* Bottom "scroll %" indicator — collapsed by default */}
        <div className={`mt-0 pt-0 border-t-0 max-h-0 opacity-0 overflow-hidden group-hover:mt-5 group-hover:pt-4 group-hover:border-t group-hover:max-h-[60px] group-hover:opacity-100 transition-all duration-300 ${isDark ? 'border-white/[0.06]' : 'border-[#0B5ED7]/10'} flex items-center justify-between`}>
          <span className={`text-[9px] font-mono font-bold tracking-widest uppercase ${
            isDark ? 'text-white/30' : 'text-gray-400'
          }`}>
            Scroll
          </span>
          <span className="text-[11px] font-mono font-bold tabular-nums bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent">
            {Math.round(progress * 100)}%
          </span>
        </div>

        {/* Theme toggle — collapsed by default, expands on nav hover */}
        <button
          onClick={toggle}
          aria-label="Toggle theme"
          className={`mt-0 w-full flex items-center justify-between gap-2 px-3 py-0 rounded-xl border-0 max-h-0 opacity-0 overflow-hidden cursor-pointer transition-all duration-300 group-hover:mt-3 group-hover:py-2.5 group-hover:border group-hover:max-h-[60px] group-hover:opacity-100 ${
            isDark
              ? 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.05] hover:border-white/[0.12]'
              : 'bg-white/50 border-[#0B5ED7]/10 hover:bg-[#0B5ED7]/[0.04] hover:border-[#0B5ED7]/20'
          }`}
        >
          <span className={`text-[10px] font-mono font-bold tracking-widest uppercase ${
            isDark ? 'text-white/40' : 'text-gray-500'
          }`}>
            {isDark ? 'Light' : 'Dark'}
          </span>
          <motion.div
            key={isDark ? 'dark' : 'light'}
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            className={isDark ? 'text-[#6DC8E8]' : 'text-[#0B5ED7]'}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
              {isDark ? (
                <><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></>
              ) : (
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              )}
            </svg>
          </motion.div>
        </button>
      </div>
    </motion.nav>
  )
}


/* ══════════════════════════════════════════════
   JD Variant Content (공고별 콘텐츠 분기)
   ══════════════════════════════════════════════ */
type JDVariant = 'company' | 'ax'

type MatchData = {
  requirement: string
  evidence: string
  techs: string[]
  className: string
}

type TechCat = {
  title: string
  color: string
  hex: string
  items: { name: string; desc: string }[]
}

const TECH_CATS = {
  ai: {
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
  backend: {
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
  frontend: {
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
  infra: {
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
  devops: {
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
  tools: {
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
} as const satisfies Record<string, TechCat>

type TechCatKey = keyof typeof TECH_CATS

const JD_CONTENT: Record<JDVariant, {
  tabLabel: string
  badge: string
  titleLine1: string
  titleLine2: string
  terminalCmd: string
  terminalLoading: string
  terminalOkLines: [string, string, string]
  matchSubtitleTop: string
  matchSubtitleBottom: string
  requirements: MatchData[]
  preferred: MatchData[]
  techStackOrder: TechCatKey[]
}> = {
  company: {
    tabLabel: '컴퍼니솔루션실',
    badge: 'NEXON 컴퍼니솔루션실 지원',
    titleLine1: 'Enterprise LLM',
    titleLine2: 'Solution Engineer',
    terminalCmd: '~$ ./init_solution.sh',
    terminalLoading: 'Loading enterprise stack...',
    terminalOkLines: [
      'LLM Business Automation',
      'Full-Stack Web (React + Flask)',
      'GCP Production Ops',
    ],
    matchSubtitleTop: '넥슨 컴퍼니솔루션실 웹 애플리케이션 엔지니어 공고 주요 업무·우대사항과',
    matchSubtitleBottom: '이 프로젝트에서 실제로 구현한 내용의 매칭.',
    requirements: [
      {
        requirement: '지능형 사내 솔루션 설계 및 개발',
        evidence: 'Debi Marlene은 커뮤니티 운영을 위한 멀티 컴포넌트 사내 자동화 솔루션. Discord 봇 엔진, 대시보드 웹, 웹패널, 영속 저장소, LLM 추론 서버까지 1인으로 설계·개발·운영 중인 LLM 기반 업무 혁신의 실제 프로덕션 사례.',
        techs: ['LLM Pipeline', 'Multi-component', '1인 풀스택'],
        className: 'md:col-span-2 lg:col-span-2',
      },
      {
        requirement: '엔터프라이즈 웹 애플리케이션 구축',
        evidence: 'Flask REST API 2종(Dashboard, Webpanel)을 Gunicorn + Nginx 리버스 프록시로 VM 프로덕션 운영. Discord OAuth2 인증, 세션 관리, CORS/SSL 포함.',
        techs: ['Flask', 'Gunicorn', 'OAuth2', 'Nginx'],
        className: 'md:col-span-1 lg:col-span-1',
      },
      {
        requirement: 'LLM / 외부 AI API 활용 업무 자동화',
        evidence: 'Anthropic Claude API 프로덕션 연동, Gemma4 LoRA 파인튜닝 + Modal A10G 서빙, Qwen3.5-Omni DashScope 연동. 모델 선택·파인튜닝·서빙·비용 최적화 전 구간을 1인으로 책임.',
        techs: ['Claude API', 'Gemma4 LoRA', 'Modal', 'DashScope'],
        className: 'md:col-span-1 lg:col-span-1',
      },
      {
        requirement: '시스템 통합 및 RESTful API 고도화',
        evidence: 'Discord Bot ↔ Dashboard API ↔ Webpanel API ↔ Modal Serverless ↔ GCS 간 RESTful 통합. 인증 토큰 전파, 상태 동기화, 멀티 서비스 오케스트레이션을 직접 설계·운영.',
        techs: ['REST API', 'System Integration', 'Multi-service'],
        className: 'md:col-span-2 lg:col-span-2',
      },
      {
        requirement: '성능 최적화를 위한 시스템 운영 / 유지보수',
        evidence: 'LangGraph 의도 분류로 불필요한 RAG 호출 제거(응답 100~300ms 절감). 음성 파이프라인은 0.5초 프리버퍼 VAD + 하이브리드 웨이크워드로 지연 최소화. GCS 메모리 조건부 fetch로 I/O 비용 절감.',
        techs: ['Latency Opt', 'Cost Reduction', 'Conditional Fetch'],
        className: 'md:col-span-2 lg:col-span-2',
      },
      {
        requirement: '대규모 상태 · 바이너리 데이터 관리',
        evidence: 'GCS 기반 멀티턴 대화 메모리, HuggingFace 모델 버전 관리, Docker 이미지 Artifact Registry 체계로 대용량 상태·바이너리를 효율적으로 운영.',
        techs: ['GCS', 'HF Registry', 'Artifact Registry'],
        className: 'md:col-span-1 lg:col-span-1',
      },
    ],
    preferred: [
      {
        requirement: 'LLM API 서비스 개발 / RAG 시스템 구축',
        evidence: 'Claude API 프로덕션 운영, 패치노트 RAG 키워드 검색으로 LLM 시스템 프롬프트에 실시간 주입. LangGraph StateGraph 조건부 엣지로 잡담/정보 요청 분기.',
        techs: ['Claude API', 'Patchnote RAG', 'LangGraph'],
        className: 'md:col-span-1',
      },
      {
        requirement: 'React / 모던 프론트엔드 풀스택',
        evidence: 'React 19 + TypeScript + Vite + Tailwind 4 기반 대시보드·웹패널 2종 구축. Framer Motion, 상태 동기화, OAuth2 플로우까지 직접 구현.',
        techs: ['React 19', 'TypeScript', 'Vite', 'Tailwind 4'],
        className: 'md:col-span-1',
      },
      {
        requirement: 'AWS / GCP 클라우드 + CI/CD 자동화',
        evidence: 'GCP Compute Engine VM에 Docker 컨테이너로 배포. Artifact Registry + Makefile 파이프라인으로 빌드·푸시·VM 재시작·롤백 자동화. Cloudflare CDN/DNS 연동.',
        techs: ['GCP', 'Docker', 'Makefile CI/CD', 'Cloudflare'],
        className: 'md:col-span-1',
      },
      {
        requirement: '요구사항 구조화 + 문서화 / 협업',
        evidence: 'CLAUDE.md 프로젝트 가이드, Mermaid 아키텍처 다이어그램, 포트폴리오 웹페이지까지 코드 기반 문서화. 분산 시스템 구조를 신규 기여자가 즉시 이해할 수 있는 수준으로 정리.',
        techs: ['Docs-as-code', 'Mermaid', 'CLAUDE.md'],
        className: 'md:col-span-1',
      },
    ],
    techStackOrder: ['backend', 'frontend', 'infra', 'devops', 'ai', 'tools'],
  },
  ax: {
    tabLabel: 'AX 채널',
    badge: 'NEXON AX-Tech Portfolio',
    titleLine1: 'AI Agent',
    titleLine2: 'Full-Stack Engineer',
    terminalCmd: '~$ ./init_competency.sh',
    terminalLoading: 'Loading core architecture...',
    terminalOkLines: [
      'Advanced RAG Systems',
      'Real-time Voice Chat',
      'Scalable Infra (GCP)',
    ],
    matchSubtitleTop: '넥슨 AX-Tech실 공고 요구사항과',
    matchSubtitleBottom: '이 프로젝트에서 실제로 구현한 내용의 매칭.',
    requirements: [
      {
        requirement: 'Python, TypeScript 능숙한 개발',
        evidence: '봇 백엔드(Python, discord.py, Flask), 대시보드 프론트엔드(TypeScript, React 19), 웹패널(Flask + React). 두 언어로 전체 서비스를 1인 개발 및 운영 중.',
        techs: ['Python', 'TypeScript', 'discord.py', 'React 19', 'Flask'],
        className: 'md:col-span-2 lg:col-span-2',
      },
      {
        requirement: '외부 AI 서비스 활용 개발',
        evidence: 'Gemma4 LoRA 파인튜닝 후 Modal A10G에 배포, Qwen3.5-Omni는 DashScope API 연동. 텍스트 채팅과 음성 대화 두 채널에서 실시간 서비스 운영.',
        techs: ['Gemma4 LoRA', 'Qwen3.5-Omni', 'Modal A10G', 'DashScope'],
        className: 'md:col-span-1 lg:col-span-1',
      },
      {
        requirement: '대화형 AI Agent 설계',
        evidence: '캐릭터 인격을 가진 대화 AI. 키워드 호출 트리거, 패치노트 RAG 컨텍스트 주입, GCS 기반 멀티턴 메모리를 LangGraph StateGraph로 오케스트레이션.',
        techs: ['LangGraph', 'Patchnote RAG', 'Multi-turn Memory'],
        className: 'md:col-span-1 lg:col-span-1',
      },
      {
        requirement: '업무 자동화 및 생산성 향상',
        evidence: '유저가 웹사이트를 직접 방문해야 했던 전적 조회와 패치노트 확인을 Discord 안에서 즉시 해결. LangGraph 의도 분류로 잡담에는 RAG를 건너뛰도록 최적화하여 응답 지연과 불필요한 네트워크 호출을 제거.',
        techs: ['LangGraph', 'Intent Classification', 'Context Reduction'],
        className: 'md:col-span-2 lg:col-span-2',
      },
      {
        requirement: '풀스택 역량 (프론트/백/인프라)',
        evidence: 'React 19, Tailwind 4 (프론트) / Flask, Gunicorn (백엔드) / Docker, Nginx, GCP (인프라). 전 과정 1인 풀스택 개발.',
        techs: ['React 19', 'Flask', 'Docker', 'GCP', 'Nginx'],
        className: 'md:col-span-2 lg:col-span-2',
      },
      {
        requirement: '프롬프트/데이터 구조화 설계',
        evidence: "프롬프트 튜닝으로 '음성 봇이 들린 말을 그대로 반복하는 문제'와 '단일 캐릭터 호출 시 양쪽 캐릭터가 답변하는 문제'를 해결. 화자 태그 기반 응답 파서로 멀티 캐릭터 음성 라우팅 구현.",
        techs: ['Prompt Engineering', 'Speaker Parsing'],
        className: 'md:col-span-1 lg:col-span-1',
      },
    ],
    preferred: [
      {
        requirement: 'LLM 챗봇, RAG 구축/운영',
        evidence: '최신 게임 패치노트를 벡터 없이 키워드로 컴팩트하게 검색해 LLM 시스템 프롬프트에 주입(Patchnote RAG).',
        techs: ['Patchnote RAG', 'Context Window'],
        className: 'md:col-span-1',
      },
      {
        requirement: 'AI 개발 도구 활용 경험',
        evidence: 'Claude Code CLI를 주 개발 환경으로 사용. Figma/Context7/NotebookLM MCP 서버 연동으로 디자인 조회, 라이브러리 문서 검색, 장문 URL 요약을 개발 워크플로우에 통합.',
        techs: ['Claude Code', 'MCP Protocol', 'Figma MCP', 'Context7'],
        className: 'md:col-span-1',
      },
      {
        requirement: 'AX(AI Transformation) 사례 구축',
        evidence: "웹사이트를 직접 방문해야 했던 전적 검색과 패치노트 확인을 Discord 안으로 이관. 키워드 호출('데비야')만으로 패치노트 RAG가 캐릭터 말투로 답변하고, 슬래시 커맨드로 전적 조회. 유저가 컨텍스트 스위칭 없이 게임 대화 중에 즉시 정보 획득.",
        techs: ['Keyword Trigger', 'Patchnote RAG', 'Slash Commands', 'Context Reduction'],
        className: 'md:col-span-1',
      },
      {
        requirement: 'AWS/클라우드 운영 기반',
        evidence: 'GCP Compute Engine VM 프로덕션 환경에서 Discord 봇, Dashboard API, Webpanel API를 Docker 컨테이너로 운영. Nginx 리버스 프록시 + SSL, Cloudflare CDN, Makefile 기반 빌드·배포·롤백 자동화.',
        techs: ['GCP', 'Docker', 'Nginx', 'Makefile', 'Cloudflare'],
        className: 'md:col-span-1',
      },
    ],
    techStackOrder: ['ai', 'backend', 'frontend', 'infra', 'devops', 'tools'],
  },
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
  const [jdVariant, setJdVariant] = useState<JDVariant>('company')
  const jd = JD_CONTENT[jdVariant]

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

      // 동적 컨텐츠 변화 대응: TroubleshootCard 아코디언, Mermaid async 렌더링 등으로
      // document 높이가 변하면 ScrollTrigger 캐시가 stale해져서 Features pin 위치가 어긋남.
      // ResizeObserver + 디바운스로 body 크기 변화를 감지해 refresh 호출.
      let refreshTimer: number | null = null
      const scheduleRefresh = () => {
        if (refreshTimer !== null) window.clearTimeout(refreshTimer)
        refreshTimer = window.setTimeout(() => {
          ScrollTrigger.refresh()
          refreshTimer = null
        }, 150)
      }
      const resizeObserver = new ResizeObserver(scheduleRefresh)
      resizeObserver.observe(document.body)

      // 완전 로드 후 한번 더 refresh (폰트/이미지/Mermaid SVG 렌더 반영)
      const onLoad = () => ScrollTrigger.refresh()
      if (document.readyState === 'complete') {
        window.setTimeout(onLoad, 100)
      } else {
        window.addEventListener('load', onLoad, { once: true })
      }

      cleanup = () => {
        if (refreshTimer !== null) window.clearTimeout(refreshTimer)
        resizeObserver.disconnect()
        window.removeEventListener('load', onLoad)
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
            
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold tracking-wider uppercase mb-5 border w-max ${
              isDark ? 'bg-[#0B5ED7]/10 text-[#6DC8E8] border-[#0B5ED7]/30' : 'bg-[#0B5ED7]/5 text-[#0B5ED7] border-[#0B5ED7]/20 bg-blend-multiply'
            }`}>
              <div className="w-2 h-2 rounded-full bg-[#0B5ED7] animate-pulse" />
              {jd.badge}
            </div>

            {/* JD variant tab switcher — inline inside Hero card */}
            <div className={`inline-flex p-1 rounded-xl mb-7 border w-max ${isDark ? 'bg-black/40 border-white/[0.08]' : 'bg-white/70 border-[#0B5ED7]/15 shadow-[0_4px_16px_rgba(11,94,215,0.06)]'}`}>
              {(Object.keys(JD_CONTENT) as JDVariant[]).map((key) => {
                const isActive = jdVariant === key
                return (
                  <button
                    key={key}
                    onClick={() => setJdVariant(key)}
                    className={`px-4 md:px-5 py-2 rounded-lg text-xs md:text-sm font-bold transition-all duration-300 ${
                      isActive
                        ? (isDark
                            ? 'bg-[#0B5ED7]/30 text-white border border-[#0B5ED7]/40'
                            : 'bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] text-white shadow-[0_2px_10px_rgba(11,94,215,0.3)]')
                        : (isDark
                            ? 'text-gray-500 hover:text-gray-200'
                            : 'text-gray-500 hover:text-[#0B5ED7]')
                    }`}
                  >
                    <span className="flex items-center gap-1.5">
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${isActive ? 'animate-pulse' : ''}`}
                        style={{ backgroundColor: isActive ? '#ffffff' : (isDark ? '#6DC8E8' : '#0B5ED7') }}
                      />
                      {JD_CONTENT[key].tabLabel}
                    </span>
                  </button>
                )
              })}
            </div>

            <GradientText
              colors={[ACCENT, ACCENT2, '#4A9BE8', ACCENT2, ACCENT]}
              animationSpeed={5}
              className="!mx-0 font-title text-[32px] md:text-[48px] lg:text-[56px] leading-[1.1] tracking-tight mb-6"
            >
              {jd.titleLine1}<br/>{jd.titleLine2}
            </GradientText>

            <p className={`text-lg md:text-xl leading-relaxed max-w-2xl font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
              {jdVariant === 'company' ? (
                <>
                  LLM 기반 사내 자동화 솔루션을 멀티 컴포넌트 웹 시스템으로<br className="hidden md:block"/>
                  직접 설계·배포·운영해온 1인 풀스택 엔지니어 <span className={`font-bold py-1 px-2 rounded-lg ${isDark ? 'text-white bg-white/10' : 'text-gray-800 bg-gray-200/60'}`}>양건호</span>입니다.
                </>
              ) : (
                <>
                  LLM 파인튜닝, 음성 AI Agent, RAG 대화 시스템을<br className="hidden md:block"/>
                  직접 기획하고 배포까지 운영한 1인 풀스택 엔지니어 <span className={`font-bold py-1 px-2 rounded-lg ${isDark ? 'text-white bg-white/10' : 'text-gray-800 bg-gray-200/60'}`}>양건호</span>입니다.
                </>
              )}
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
                  v: 'AI-First', l: 'Claude Code 개발', sub: 'Built with Claude Code',
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
              <div className="text-[#6DC8E8] font-bold">{jd.terminalCmd}</div>
              <div className="text-gray-400 mt-2 mb-1">{jd.terminalLoading}</div>
              {jd.terminalOkLines.map((line) => (
                <div key={line}><span className="text-[#0B5ED7] font-bold">[OK]</span> {line}</div>
              ))}
              <div className="mt-3 text-emerald-400 flex items-center gap-1">Status: Ready <div className="w-2 h-4 bg-emerald-400 animate-pulse" /></div>
            </div>
            </GlassCard>
          </FadeIn>

          {/* Action Block - Span 3 */}
          <FadeIn delay={0.25} className="md:col-span-6 lg:col-span-3 h-full">
            <GlassCard className="h-full rounded-[32px]">
              <div className="flex flex-col justify-center h-full w-full p-8">
                {/* Header with icon — clearly a label, not a button */}
                <div className={`flex items-center gap-2 mb-6 ${isDark ? 'text-[#6DC8E8]' : 'text-[#0B5ED7]'}`}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="15 3 21 3 21 9" />
                    <polyline points="9 21 3 21 3 15" />
                    <line x1="21" y1="3" x2="14" y2="10" />
                    <line x1="3" y1="21" x2="10" y2="14" />
                  </svg>
                  <span className="text-[11px] font-bold uppercase tracking-[0.2em]">Explore Project</span>
                </div>

                <div className="flex flex-col gap-3">
                  <GlassButton href="/landing" size="sm" className="!w-full !h-12 !text-sm">
                    <span className="flex items-center justify-center gap-2">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polygon points="5 3 19 12 5 21 5 3" />
                      </svg>
                      Live Site Demo
                    </span>
                  </GlassButton>
                  <GlassButton href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer" size="sm" className="!w-full !h-12 !text-sm">
                    <span className="flex items-center justify-center gap-2">
                      <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                      GitHub Repo
                    </span>
                  </GlassButton>
                </div>
              </div>
            </GlassCard>
          </FadeIn>

        </motion.div>
      </section>

      {/* ══ JD MATCH ══ */}
      <section id="match" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-16">
            <ScrollFloat
              containerClassName="font-title bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent leading-tight"
              textClassName="text-4xl md:text-[64px]"
            >
              JD Match
            </ScrollFloat>
            <FadeIn delay={0.1}>
              <p className={`text-lg max-w-2xl mx-auto mt-4 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                {jd.matchSubtitleTop}<br />
                {jd.matchSubtitleBottom}
              </p>
            </FadeIn>
          </div>

          {/* 지원 자격 */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-6`} style={{ color: ACCENT }}>
              Requirements
            </h3>
          </FadeIn>
          <div key={`${jdVariant}-req`} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
            {jd.requirements.map((card, i) => (
              <MatchCard
                key={`${jdVariant}-req-${i}`}
                delay={i * 0.05}
                requirement={card.requirement}
                evidence={card.evidence}
                techs={card.techs}
                className={card.className}
              />
            ))}
          </div>

          {/* 우대사항 */}
          <FadeIn>
            <h3 className={`text-sm font-bold uppercase tracking-wider mb-6`} style={{ color: ACCENT2 }}>
              Preferred
            </h3>
          </FadeIn>
          <div key={`${jdVariant}-pref`} className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {jd.preferred.map((card, i) => (
              <MatchCard
                key={`${jdVariant}-pref-${i}`}
                delay={i * 0.05}
                requirement={card.requirement}
                evidence={card.evidence}
                techs={card.techs}
                className={card.className}
              />
            ))}
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

          {/* Sticky range wrapper — Pipeline nodes + LangGraph까지만 탭 고정, Model Selection Journey부턴 해제 */}
          <div className="relative">
          <div className="sticky top-4 z-30 mb-12 flex justify-center py-2 pointer-events-none">
            <FadeIn>
              <div className={`pointer-events-auto inline-flex p-1.5 rounded-2xl backdrop-blur-xl ${isDark ? 'bg-[#0a0e14]/75 border border-white/[0.1] shadow-[0_8px_24px_rgba(0,0,0,0.4)]' : 'bg-white/85 border border-gray-200 shadow-[0_8px_24px_rgba(0,0,0,0.08)]'}`}>
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
                  <PipelineNode step={4} title="LLM + 응답 전송" desc="call_llm 노드 → Modal A10G Gemma4 LoRA. Components V2 UI로 Discord 전송." techs={['Gemma4 LoRA', 'Modal A10G', 'Components V2']} delay={0.15} isLast />
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
                  <PipelineNode step={4} title="Omni + TTS" desc="Qwen3.5-Omni로 상황 파악. 화자별 대사 분리 후 CosyVoice3로 재생." techs={['Qwen3.5-Omni', 'CosyVoice3']} delay={0.15} isLast />
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
          </div>
          {/* ── sticky range 끝 ── */}

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
          <div className="font-title bg-gradient-to-r from-[#0B5ED7] to-[#6DC8E8] bg-clip-text text-transparent text-2xl md:text-4xl">
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
                  <p className={`font-bold text-base md:text-lg leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-800'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                    캐릭터 인격 기반 대화형 AI Agent.
                  </p>
                  <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
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
                  <p className={`font-bold text-base md:text-lg leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-800'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                    실시간 음성 이해와 TTS 응답.
                  </p>
                  <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Discord DAVE E2EE 음성 스트림 수신,
                    WebRTC VAD 발화 감지, Qwen3.5-Omni 오디오 이해.
                    화자별 CosyVoice3 파인튜닝으로 캐릭터 음성 생성.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {['Qwen3.5-Omni', 'CosyVoice3', 'WebRTC VAD'].map(t => (
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
                  <p className={`font-bold text-base md:text-lg leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-800'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                    Discord OAuth2 관리 웹앱.
                  </p>
                  <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
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
                  <p className={`font-bold text-base md:text-lg leading-relaxed ${isDark ? 'text-gray-200' : 'text-gray-800'}`} style={{ fontFamily: "'Paperlogy', sans-serif" }}>
                    전적 검색 + 관리자 모니터링.
                  </p>
                  <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
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

          <div key={`${jdVariant}-tech`} className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jd.techStackOrder.map((catKey, i) => {
              const cat = TECH_CATS[catKey]
              return (
                <FadeIn key={`${jdVariant}-${catKey}`} delay={i * 0.05} className="h-full">
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
              )
            })}
          </div>
        </div>
      </section>

      {/* ══ COST ANALYSIS ══ */}
      {/* ══ FOOTER ══ */}
      <footer className="relative z-[5] overflow-hidden">
        {isDark ? (
          /* Dark footer */
          <div className="py-20">
            <div className="max-w-5xl mx-auto px-6 text-center">
              <FadeIn>
                <img src={TWINS_APPROVE} alt="" className="w-48 h-auto mx-auto mb-8" draggable={false} />
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-3 font-title">
                  더 자세한 내용이 궁금하시면
                </h2>
                <p className="text-discord-muted mb-8">
                  코드와 커밋 히스토리에서 개발 과정을 확인할 수 있습니다.
                </p>
                <div className="flex justify-center gap-4 flex-wrap">
                  <GlassButton href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer" size="sm">
                    <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>GitHub</span>
                  </GlassButton>
                  <GlassButton href="mailto:goenho0613@gmail.com" size="sm">
                    <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" className="w-5 h-5"><path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6z" fill="none" stroke="currentColor" strokeWidth="2"/><polyline points="22,6 12,13 2,6" fill="none" stroke="currentColor" strokeWidth="2"/></svg>Contact</span>
                  </GlassButton>
                  <GlassButton href="/portfolio" size="sm">All Portfolios</GlassButton>
                </div>
              </FadeIn>
            </div>
          </div>
        ) : (
          /* Light footer with sky background */
          <>
            <img src={BG_FOOTER} alt="" className="absolute inset-0 w-full h-full object-cover object-bottom" draggable={false} />
            <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#f8fcfd] to-transparent z-[1]" />

            <div className="relative z-[2] flex justify-center pt-20 px-6">
              <FadeIn className="w-full max-w-3xl">
                <div className="bg-white/60 rounded-3xl border border-white/40 p-8 md:p-12 text-center backdrop-blur-sm">
                  <ScrollFloat
                    containerClassName="font-title text-gray-800 mb-4"
                    textClassName="text-3xl md:text-4xl"
                  >
                    더 자세한 내용이 궁금하시면
                  </ScrollFloat>
                  <p className="text-gray-500 mb-8 leading-relaxed">
                    코드와 커밋 히스토리에서 개발 과정을 확인할 수 있습니다.
                  </p>
                  <div className="flex justify-center gap-4 flex-wrap">
                    <GlassButton href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer" size="sm">
                      <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>GitHub</span>
                    </GlassButton>
                    <GlassButton href="mailto:goenho0613@gmail.com" size="sm">
                      <span className="flex items-center gap-2"><svg viewBox="0 0 24 24" className="w-5 h-5"><path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6z" fill="none" stroke="currentColor" strokeWidth="2"/><polyline points="22,6 12,13 2,6" fill="none" stroke="currentColor" strokeWidth="2"/></svg>Contact</span>
                    </GlassButton>
                    <GlassButton href="/portfolio" size="sm">All Portfolios</GlassButton>
                  </div>
                </div>
              </FadeIn>
            </div>

            {/* Footer character + platform */}
            <div className="relative z-[2] mt-6">
              <img src={FOOTER_PLATFORM} alt="" className="w-full h-auto" draggable={false} />
              <div className="absolute inset-0 z-[1]">
                <img src={FOOTER_CHAR} alt="" className="w-full h-full object-contain" draggable={false} />
              </div>
            </div>
          </>
        )}

        {/* Copyright */}
        <div className={`relative z-[3] text-center py-6 text-xs ${isDark ? 'text-discord-muted' : 'text-gray-400'}`}>
          Yang Gunho -- NEXON AI Agent Full-Stack Engineer -- Built with Claude Code
        </div>
      </footer>
    </div>
  )
}
