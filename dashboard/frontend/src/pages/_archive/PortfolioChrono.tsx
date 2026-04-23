import { useRef, useEffect, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import Lenis from 'lenis'
import ScrollFloat from '../components/common/ScrollFloat'
import Galaxy from '../components/common/Galaxy'

import CHRONO_LOGO from '../assets/images/event/chrono_studio_logo.jpeg'
import STATUSLINE_PREVIEW from '../assets/images/event/statusline_preview.png'

/* ── Colors ── */
const GOLD = '#C4A265'
const GOLD_LIGHT = '#D4B878'
const GOLD_DIM = '#8B7335'
const BG = '#0A0A0A'
const BG_CARD = 'rgba(196,162,101,0.03)'
const BORDER = 'rgba(196,162,101,0.15)'
const TEXT = '#E8E0D0'
const TEXT_DIM = '#9A9080'

/* ── SVG Icons ── */
const IconGitHub = ({ size = 18 }: { size?: number }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" width={size} height={size}>
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
  </svg>
)
const IconGlobe = ({ size = 18 }: { size?: number }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} width={size} height={size}>
    <circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
  </svg>
)
const IconMail = ({ size = 18 }: { size?: number }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} width={size} height={size}>
    <rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/>
  </svg>
)
const IconExternal = ({ size = 14 }: { size?: number }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} width={size} height={size}>
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
  </svg>
)

/* ── FadeIn ── */
function FadeIn({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

/* ── Section Title with ScrollFloat ── */
function SectionTitle({ children, sub }: { children: string; sub?: string }) {
  return (
    <div className="mb-16">
      <ScrollFloat
        containerClassName="tracking-tight leading-tight [font-family:'Allura',cursive]"
        textClassName="text-4xl md:text-6xl"
        scrollStart="center bottom+=30%"
        scrollEnd="bottom bottom-=20%"
      >
        {children}
      </ScrollFloat>
      {sub && (
        <FadeIn delay={0.1}>
          <p className="mt-3 text-base" style={{ color: TEXT_DIM }}>{sub}</p>
        </FadeIn>
      )}
      <FadeIn delay={0.15}>
        <div className="mt-4 h-px w-24" style={{ background: `linear-gradient(to right, ${GOLD}, transparent)` }} />
      </FadeIn>
    </div>
  )
}

/* ── Card ── */
function Card({ children, className = '', delay = 0 }: {
  children: React.ReactNode; className?: string; delay?: number
}) {
  return (
    <FadeIn delay={delay}>
      <div
        className={`border p-6 transition-colors duration-300 hover:border-[rgba(196,162,101,0.3)] ${className}`}
        style={{ background: BG_CARD, borderColor: BORDER }}
      >
        {children}
      </div>
    </FadeIn>
  )
}

/* ── Tag ── */
function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="px-2.5 py-1 text-xs font-medium border"
      style={{ color: GOLD_LIGHT, borderColor: BORDER, background: 'rgba(196,162,101,0.06)' }}
    >
      {children}
    </span>
  )
}

/* ── Link Button ── */
function LinkButton({ href, children, icon }: { href: string; children: React.ReactNode; icon?: React.ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer"
      className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium border transition-colors hover:bg-[rgba(196,162,101,0.08)]"
      style={{ color: GOLD, borderColor: BORDER }}>
      {icon}
      {children}
    </a>
  )
}

/* ── Side Nav ── */
const NAV_ITEMS = [
  { id: 'hero', label: 'Intro' },
  { id: 'harness', label: 'Harness Engineering' },
  { id: 'finetune', label: 'AI Fine-tuning' },
  { id: 'automation', label: 'Automation' },
  { id: 'journey', label: 'Journey' },
  { id: 'techstack', label: 'Tech Stack' },
  { id: 'match', label: 'JD Match' },
]

function SideNav({ active }: { active: string }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > window.innerHeight * 0.8)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <AnimatePresence>
      {visible && (
        <motion.nav
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="fixed left-6 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-3"
        >
          {NAV_ITEMS.map(item => (
            <a key={item.id} href={`#${item.id}`} className="group flex items-center gap-3 transition-opacity duration-200"
              style={{ opacity: active === item.id ? 1 : 0.4 }}>
              <div className="w-2 h-2 transition-all duration-200" style={{
                background: active === item.id ? GOLD : 'transparent',
                border: `1px solid ${active === item.id ? GOLD : TEXT_DIM}`,
              }} />
              <span className="text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: TEXT_DIM }}>
                {item.label}
              </span>
            </a>
          ))}
        </motion.nav>
      )}
    </AnimatePresence>
  )
}

/* ══════════════════════════════════════════════════════════════════
   MAIN COMPONENT
   ══════════════════════════════════════════════════════════════════ */
export default function PortfolioChrono() {
  const [activeSection, setActiveSection] = useState('hero')

  /* Lenis smooth scroll */
  useEffect(() => {
    const lenis = new Lenis({ duration: 1.4, easing: (t: number) => 1 - Math.pow(1 - t, 4) })
    ;(window as any).__lenis = lenis
    function raf(time: number) { lenis.raf(time); requestAnimationFrame(raf) }
    requestAnimationFrame(raf)
    return () => { lenis.destroy(); delete (window as any).__lenis }
  }, [])

  /* Intersection observer for nav */
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        for (const entry of entries) {
          if (entry.isIntersecting) setActiveSection(entry.target.id)
        }
      },
      { rootMargin: '-40% 0px -40% 0px' }
    )
    NAV_ITEMS.forEach(item => {
      const el = document.getElementById(item.id)
      if (el) observer.observe(el)
    })
    return () => observer.disconnect()
  }, [])

  /* ScrollFloat color override + Space Grotesk font (this page only) */
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = `
      .chrono-scroll-title .word { color: ${GOLD} !important; }
      @font-face { font-family: 'Allura'; src: local('Allura'), url('/fonts/Allura-Regular.ttf') format('truetype'); font-weight: 400; font-display: swap; }
    `
    document.head.appendChild(style)
    return () => { document.head.removeChild(style) }
  }, [])

  return (
    <div className="min-h-screen" style={{ background: BG, color: TEXT, fontFamily: "'Paperlogy', 'Pretendard', system-ui, sans-serif" }}>
      <SideNav active={activeSection} />

      {/* ══ HERO (fixed behind — content slides over like a blanket) ══ */}
      <section id="hero" className="fixed top-0 left-0 right-0 h-screen flex flex-col justify-center items-center px-6 overflow-hidden" style={{ zIndex: 0 }}>
        <div className="absolute inset-0">
          <Galaxy hueShift={40} speed={0.3} density={1.2} glowIntensity={0.2} saturation={0.3}
            rotationSpeed={0.02} twinkleIntensity={0.4} mouseRepulsion={true} mouseInteraction={true} />
        </div>

        <div className="relative z-10 flex flex-col items-center text-center max-w-3xl">
          <motion.img src={CHRONO_LOGO} alt="Chrono Studio"
            className="w-64 md:w-80 h-auto mb-8 opacity-90" draggable={false}
            initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 0.9, scale: 1 }}
            transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }} />

          <motion.div className="w-16 h-px mb-8" style={{ background: GOLD_DIM }}
            initial={{ scaleX: 0 }} animate={{ scaleX: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }} />

          <motion.h1 className="text-2xl md:text-4xl font-bold tracking-tight mb-3" style={{ color: TEXT }}
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}>
            개발 자동화 엔지니어
          </motion.h1>
          <motion.p className="text-sm md:text-base mb-2" style={{ color: GOLD }}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}>
            AI Harness Engineering / TA Team
          </motion.p>
          <motion.p className="text-sm mt-6 max-w-lg leading-relaxed" style={{ color: TEXT_DIM }}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}>
            AI 에이전트의 하네스를 직접 설계하고 구축합니다.
            커스텀 도구 제작, 모델 파인튜닝, 서버리스 GPU 배포까지
            AI 개발 파이프라인 전체를 1인으로 운영하고 있습니다.
          </motion.p>

          <motion.div className="grid grid-cols-2 md:grid-cols-4 gap-px mt-14 border" style={{ borderColor: BORDER }}
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}>
            {[
              { num: '2 Models', label: 'AI 파인튜닝' },
              { num: '60+', label: '자동화 커맨드' },
              { num: '100+', label: '서버 운영중' },
              { num: 'Open Source', label: 'AI Tooling 공개' },
            ].map((s, i) => (
              <div key={i} className="px-6 py-5 text-center" style={{ background: BG_CARD }}>
                <div className="text-lg font-bold" style={{ color: GOLD }}>{s.num}</div>
                <div className="text-xs mt-1" style={{ color: TEXT_DIM }}>{s.label}</div>
              </div>
            ))}
          </motion.div>

          <motion.div className="flex flex-wrap gap-4 mt-10"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.9 }}>
            <LinkButton href="https://github.com/2rami/debi-marlene" icon={<IconGitHub />}>GitHub</LinkButton>
            <LinkButton href="https://debimarlene.com" icon={<IconGlobe />}>Live Service</LinkButton>
          </motion.div>
        </div>

        <motion.div className="absolute bottom-10"
          animate={{ y: [0, 8, 0] }} transition={{ duration: 2, repeat: Infinity }}>
          <div className="w-px h-12" style={{ background: `linear-gradient(to bottom, transparent, ${GOLD_DIM})` }} />
        </motion.div>
      </section>

      {/* Spacer for hero height */}
      <div className="h-screen" />

      {/* ── Content wrapper (slides over hero like a blanket) ── */}
      <div className="relative z-10" style={{ background: BG }}>
        {/* Top edge: thin gold line + shadow for blanket edge */}
        <div className="h-px" style={{ background: `linear-gradient(to right, transparent, ${GOLD_DIM}, transparent)` }} />
        <div className="h-16 -mt-px" style={{
          background: `linear-gradient(to bottom, rgba(196,162,101,0.05), transparent)`
        }} />

      {/* ══ HARNESS ENGINEERING ══ */}
      <section id="harness" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="chrono-scroll-title">
            <SectionTitle sub="AI 에이전트를 감싸는 인프라를 설계하고 구축합니다">
              Harness Engineering
            </SectionTitle>
          </div>

          {/* Definition */}
          <FadeIn>
            <div className="border-l-2 pl-6 mb-14" style={{ borderColor: GOLD_DIM }}>
              <p className="text-sm leading-relaxed" style={{ color: TEXT_DIM }}>
                <span style={{ color: GOLD }}>Harness Engineering</span>은 AI 에이전트 자체가 아닌,
                에이전트가 안정적으로 작동하도록 감싸는 <strong style={{ color: TEXT }}>도구 접근 권한, 가드레일,
                피드백 루프, 관찰 가능성 계층</strong>을 설계하는 엔지니어링 분야입니다.
                말의 고삐(harness)에서 유래한 용어로, 강력하지만 예측 불가능한 AI를 올바른 방향으로 이끄는 시스템을 만듭니다.
              </p>
            </div>
          </FadeIn>

          {/* Harness components grid */}
          <div className="grid md:grid-cols-2 gap-px border" style={{ borderColor: BORDER }}>
            {[
              {
                title: 'MCP Server Integration',
                desc: 'Claude Code에 MCP 서버를 연동하여 AI 에이전트의 도구 접근 범위를 확장. GitHub, Notion, Figma, Chrome DevTools, Memory Graph 등 외부 시스템과의 양방향 통신 구축.',
                tags: ['MCP Protocol', 'Tool-use', 'Claude Code'],
              },
              {
                title: 'Hooks & Guardrails',
                desc: 'Claude Code hooks 시스템으로 에이전트의 행동에 가드레일 설정. 도구 호출 전/후 자동 검증, 컨텍스트 주입, 세션 시작 시 프로젝트 상태 자동 로드.',
                tags: ['Hooks', 'Guardrails', 'Automation'],
              },
              {
                title: 'Custom Skills & Agents',
                desc: 'gws CLI, NotebookLM CLI 등 커스텀 스킬을 제작하여 에이전트의 능력을 확장. Google Workspace 전체를 CLI로 제어하고, 조사/정리 작업을 자동화하는 스킬 시스템 구축.',
                tags: ['Skills', 'CLI Tooling', 'Agent Extension'],
              },
              {
                title: 'Context & Memory System',
                desc: 'CLAUDE.md로 프로젝트 컨텍스트를 관리하고, 파일 기반 auto memory 시스템으로 대화 간 연속성 유지. Google Drive 동기화로 여러 기기에서 메모리 공유.',
                tags: ['CLAUDE.md', 'Auto Memory', 'Observability'],
              },
            ].map((item, i) => (
              <div key={i} className="p-6 transition-colors hover:bg-[rgba(196,162,101,0.04)]" style={{ background: BG_CARD }}>
                <h3 className="text-base font-bold mb-3" style={{ color: TEXT }}>{item.title}</h3>
                <p className="text-sm leading-relaxed mb-4" style={{ color: TEXT_DIM }}>{item.desc}</p>
                <div className="flex flex-wrap gap-2">
                  {item.tags.map(t => <Tag key={t}>{t}</Tag>)}
                </div>
              </div>
            ))}
          </div>

          {/* Statusline */}
          <FadeIn delay={0.1} className="mt-6">
            <div className="border p-6" style={{ borderColor: BORDER, background: BG_CARD }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider" style={{ color: GOLD }}>
                  Custom Statusline (Open Source)
                </h3>
                <a href="https://github.com/2rami/claude-code-simple-statusline" target="_blank" rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs transition-colors hover:opacity-80" style={{ color: GOLD_LIGHT }}>
                  <IconGitHub size={14} />
                  2rami/claude-code-simple-statusline
                  <IconExternal size={12} />
                </a>
              </div>
              <p className="text-sm mb-4" style={{ color: TEXT_DIM }}>
                직접 만든 오픈소스 statusline. Nerd Font 아이콘 + Tokyo Night 컬러로
                모델명, git 브랜치, 컨텍스트 사용률, 현재 프롬프트를 실시간 표시.
              </p>
              {/* Statusline preview (screenshot) */}
              <img src={STATUSLINE_PREVIEW} alt="Statusline preview" className="w-full h-auto border" draggable={false}
                style={{ borderColor: 'rgba(196,162,101,0.1)', borderRadius: 4 }} />
            </div>
          </FadeIn>

          {/* AI Pair Programming tools */}
          <FadeIn delay={0.15} className="mt-px">
            <div className="border p-6" style={{ borderColor: BORDER, background: BG_CARD }}>
              <h3 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: GOLD }}>
                AI Pair Programming 환경
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { name: 'Claude Code', role: '주력 에이전트', active: true },
                  { name: 'Cursor AI', role: 'IDE 통합', active: false },
                  { name: 'OpenAI Codex', role: '에이전트 비교', active: false },
                  { name: 'Antigravity', role: '에이전트 비교', active: false },
                ].map(tool => (
                  <div key={tool.name} className="border p-3" style={{
                    borderColor: tool.active ? GOLD_DIM : BORDER,
                    background: tool.active ? 'rgba(196,162,101,0.06)' : 'transparent',
                  }}>
                    <div className="text-sm font-medium" style={{ color: tool.active ? GOLD : TEXT }}>{tool.name}</div>
                    <div className="text-xs mt-1" style={{ color: TEXT_DIM }}>{tool.role}</div>
                  </div>
                ))}
              </div>
            </div>
          </FadeIn>

          {/* MCP Servers */}
          <FadeIn delay={0.2} className="mt-px">
            <div className="border p-6" style={{ borderColor: BORDER, background: BG_CARD }}>
              <h3 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: GOLD }}>
                MCP 서버 (Model Context Protocol)
              </h3>
              <p className="text-sm mb-4" style={{ color: TEXT_DIM }}>
                Claude Code에 외부 도구를 연결하는 MCP 서버를 활용하여 브라우저 제어, 디자인 시스템 연동, 최신 문서 조회 등을 AI가 직접 수행.
              </p>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                {[
                  { name: 'Context7', desc: '라이브러리/프레임워크 최신 문서 실시간 조회', color: '#43b581' },
                  { name: 'Figma MCP', desc: '디자인 → 코드 변환, 디자인 토큰 추출', color: '#a259ff' },
                  { name: 'Chrome DevTools', desc: '브라우저 제어, 디버깅, Lighthouse 감사', color: '#4285f4' },
                  { name: 'GitHub', desc: 'PR/이슈 관리, 코드 검색, 저장소 관리', color: '#e6edf3' },
                  { name: 'Notion', desc: '페이지 검색/생성, 데이터베이스 관리', color: '#ffffff' },
                  { name: 'Memory Graph', desc: '엔티티/관계 기반 지식 그래프 저장', color: '#e58fb6' },
                ].map((mcp) => (
                  <div key={mcp.name} className="border px-4 py-3" style={{ borderColor: BORDER, background: 'rgba(196,162,101,0.02)' }}>
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-1.5 h-1.5" style={{ backgroundColor: mcp.color }} />
                      <span className="text-sm font-bold" style={{ color: TEXT }}>{mcp.name}</span>
                    </div>
                    <p className="text-xs" style={{ color: TEXT_DIM }}>{mcp.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ AI FINE-TUNING & DEPLOYMENT ══ */}
      <section id="finetune" className="py-24 px-6" style={{ background: 'rgba(196,162,101,0.02)' }}>
        <div className="max-w-5xl mx-auto">
          <div className="chrono-scroll-title">
            <SectionTitle sub="HuggingFace 모델 파인튜닝부터 서버리스 GPU 배포까지">
              AI Fine-tuning
            </SectionTitle>
          </div>

          <div className="space-y-px">
            <Card>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold" style={{ color: TEXT }}>CosyVoice3 TTS Fine-tuning</h3>
                  <p className="text-xs mt-1" style={{ color: GOLD }}>FunAudioLLM/Fun-CosyVoice3-0.5B-2512</p>
                </div>
                <span className="text-xs px-2 py-1 border" style={{ color: GOLD, borderColor: BORDER }}>Production</span>
              </div>
              <p className="text-sm leading-relaxed mb-4" style={{ color: TEXT_DIM }}>
                6종의 TTS 엔진(Coqui, XTTS, MeloTTS, Fish-Speech, GPT-SoVITS, CosyVoice3)을
                직접 테스트/비교 후 CosyVoice3 채택. Colab A100/T4 환경에서 LLM SFT 파인튜닝.
                bfloat16 호환성 패치, Qwen2 attention 이슈 해결 등 저수준 트러블슈팅 경험.
              </p>
              <div className="flex flex-wrap gap-2">
                {['CosyVoice3', 'HuggingFace', 'PyTorch', 'Colab A100/T4', 'Modal T4 GPU', 'bfloat16'].map(t => <Tag key={t}>{t}</Tag>)}
              </div>
            </Card>

            <Card delay={0.05}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold" style={{ color: TEXT }}>Gemma 4 Fine-tuning</h3>
                  <p className="text-xs mt-1" style={{ color: GOLD }}>Text Chat (LoRA) + Audio Understanding (Omni)</p>
                </div>
                <span className="text-xs px-2 py-1 border" style={{ color: GOLD_LIGHT, borderColor: BORDER }}>Recent</span>
              </div>
              <p className="text-sm leading-relaxed mb-4" style={{ color: TEXT_DIM }}>
                Gemma 4 E4B 모델로 캐릭터 텍스트 채팅(LoRA 파인튜닝)과 오디오 이해(Omni) 구현.
                quantize 불가 이슈 해결 (bfloat16 + CPU offload), Modal A10G 배포, STT 0.7~2.5초 달성.
              </p>
              <div className="flex flex-wrap gap-2">
                {['Gemma 4', 'LoRA', 'Omni Audio', 'Modal A10G', 'bfloat16+CPU offload'].map(t => <Tag key={t}>{t}</Tag>)}
              </div>
            </Card>

            <Card delay={0.1}>
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-bold" style={{ color: TEXT }}>HuggingFace Model Management</h3>
              </div>
              <p className="text-sm leading-relaxed mb-4" style={{ color: TEXT_DIM }}>
                캐릭터별 브랜치 전략으로 HuggingFace 모델 관리. Modal Volume 캐싱으로 cold start 최적화.
                Google Drive 체크포인트 백업, Colab-HF-Modal 파이프라인 구축.
              </p>
              <div className="flex flex-wrap gap-2">
                {['HuggingFace Hub', 'Model Versioning', 'Modal Volume', 'Colab Pipeline'].map(t => <Tag key={t}>{t}</Tag>)}
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* ══ AUTOMATION ══ */}
      <section id="automation" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="chrono-scroll-title">
            <SectionTitle sub="반복 작업 자동화 및 생산성 향상 시스템">
              Automation
            </SectionTitle>
          </div>

          <div className="grid md:grid-cols-3 gap-px border" style={{ borderColor: BORDER }}>
            {[
              {
                title: 'Build & Deploy',
                items: [
                  'Makefile 60+ 커맨드',
                  'Docker 멀티스테이지 빌드',
                  'GCP Artifact Registry',
                  'VM 원격 배포/롤백',
                  'Cloudflare 캐시 퍼지',
                ],
              },
              {
                title: 'Infrastructure',
                items: [
                  'GCP Compute Engine VM',
                  'nginx 리버스 프록시',
                  'Gunicorn + supervisor',
                  'Google Cloud Storage',
                  'Modal Serverless GPU',
                ],
              },
              {
                title: 'Development',
                items: [
                  'Claude Code + MCP 연동',
                  'Auto Memory (Google Drive)',
                  'CLAUDE.md 컨텍스트 관리',
                  'Custom CLI Skills',
                  'Hook 기반 자동 검증',
                ],
              },
            ].map((col, i) => (
              <FadeIn key={i} delay={i * 0.05}>
                <div className="p-6 h-full" style={{ background: BG_CARD }}>
                  <h3 className="text-sm font-semibold uppercase tracking-wider mb-5" style={{ color: GOLD }}>{col.title}</h3>
                  <ul className="space-y-3">
                    {col.items.map(item => (
                      <li key={item} className="flex items-start gap-2 text-sm" style={{ color: TEXT_DIM }}>
                        <span className="mt-1.5 w-1.5 h-1.5 shrink-0" style={{ background: GOLD_DIM }} />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ══ JOURNEY ══ */}
      <section id="journey" className="py-24 px-6" style={{ background: 'rgba(196,162,101,0.02)' }}>
        <div className="max-w-5xl mx-auto">
          <div className="chrono-scroll-title">
            <SectionTitle sub="GPT 복붙부터 AI 에이전트 하네스 엔지니어링까지">
              Journey
            </SectionTitle>
          </div>

          <div className="relative">
            <div className="absolute left-[7px] top-0 bottom-0 w-px" style={{ background: BORDER }} />
            <div className="space-y-8">
              {[
                { date: '2025.02', title: 'GPT 복붙 시대', desc: 'ChatGPT로 코드 생성 -> 복붙. 위치 오류와 컨텍스트 부재로 비효율적.', accent: false },
                { date: '2025.04', title: 'VS Code AI 시대', desc: 'ChatGPT "Work with Apps" (VS Code 연동). 파일 하나만 접근 가능, 제한적.', accent: false },
                { date: '2025.06', title: 'Claude Code 도입', desc: '출시 즉시 도입. 파일 시스템 전체 접근, 에이전트 기반 개발의 시작.', accent: true },
                { date: '2025.10', title: 'Discord 봇 풀스택 개발 시작', desc: 'AI 에이전트와 함께 봇+대시보드+웹패널+인프라를 1인 개발. GCP 배포.', accent: false },
                { date: '2026.01', title: 'TTS 파인튜닝 + Modal 배포', desc: 'Qwen3-TTS -> CosyVoice3 파인튜닝. HuggingFace 모델 관리, Modal T4 GPU 배포.', accent: true },
                { date: '2026.03', title: 'Harness Engineering 본격화', desc: 'MCP 서버 10+개 연동, hooks/skills 시스템, auto memory, CLAUDE.md 컨텍스트 관리. AI 에이전트의 하네스를 직접 설계하고 운영.', accent: true },
                { date: '2026.04', title: 'Gemma 4 파인튜닝 + 음성 AI', desc: 'Gemma4 LoRA 파인튜닝, Omni 오디오 이해, 실시간 음성 대화 시스템 개발 중.', accent: true },
              ].map((item, i) => (
                <FadeIn key={i} delay={i * 0.05} className="relative pl-8">
                  <div className="absolute left-0 top-[6px] w-[15px] h-[15px] border-2" style={{
                    background: item.accent ? `${GOLD}33` : BG,
                    borderColor: item.accent ? GOLD : TEXT_DIM,
                  }} />
                  <div className="text-xs mb-1" style={{ color: GOLD_DIM }}>{item.date}</div>
                  <h4 className="font-bold mb-1" style={{ color: item.accent ? GOLD : TEXT }}>{item.title}</h4>
                  <p className="text-sm leading-relaxed" style={{ color: TEXT_DIM }}>{item.desc}</p>
                </FadeIn>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ══ TECH STACK ══ */}
      <section id="techstack" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="chrono-scroll-title">
            <SectionTitle sub="프로젝트에서 실제 사용 중인 기술">
              Tech Stack
            </SectionTitle>
          </div>

          <div className="grid md:grid-cols-2 gap-px border" style={{ borderColor: BORDER }}>
            {[
              {
                category: 'AI / ML', color: GOLD,
                items: [
                  { name: 'Anthropic Claude API', detail: '봇 AI 대화, 캐릭터 페르소나' },
                  { name: 'CosyVoice3', detail: 'TTS 파인튜닝 (LLM SFT)' },
                  { name: 'Gemma 4', detail: 'LoRA 텍스트 + Omni 오디오' },
                  { name: 'Modal Serverless', detail: 'GPU 추론 서버 (T4/A10G)' },
                  { name: 'HuggingFace', detail: '모델 호스팅/버전 관리' },
                ],
              },
              {
                category: 'Backend', color: '#7BA7BC',
                items: [
                  { name: 'Python', detail: '봇, 백엔드, ML 파이프라인' },
                  { name: 'discord.py', detail: 'Discord 봇 프레임워크' },
                  { name: 'Flask', detail: 'API 서버 (대시보드, 웹패널)' },
                  { name: 'aiohttp', detail: '비동기 HTTP 클라이언트' },
                ],
              },
              {
                category: 'Frontend', color: '#BC7B7B',
                items: [
                  { name: 'React 19', detail: 'UI 프레임워크' },
                  { name: 'TypeScript', detail: '타입 안전성' },
                  { name: 'Vite', detail: '빌드 도구' },
                  { name: 'Tailwind CSS 4', detail: '스타일링' },
                  { name: 'Framer Motion', detail: '애니메이션' },
                ],
              },
              {
                category: 'Infrastructure', color: '#7BBC8F',
                items: [
                  { name: 'GCP Compute Engine', detail: 'VM 호스팅' },
                  { name: 'Docker', detail: '컨테이너화, 멀티스테이지 빌드' },
                  { name: 'nginx', detail: '리버스 프록시, SPA 라우팅' },
                  { name: 'Cloudflare', detail: 'CDN, DNS, DDoS 방어' },
                  { name: 'Google Cloud Storage', detail: '설정/데이터 저장' },
                ],
              },
            ].map((cat, i) => (
              <FadeIn key={i} delay={i * 0.03}>
                <div className="p-6 h-full" style={{ background: BG_CARD }}>
                  <h3 className="text-sm font-semibold uppercase tracking-wider mb-5" style={{ color: cat.color }}>{cat.category}</h3>
                  <div className="space-y-3">
                    {cat.items.map(item => (
                      <div key={item.name} className="flex items-baseline gap-3">
                        <span className="text-sm font-medium shrink-0" style={{ color: TEXT }}>{item.name}</span>
                        <span className="text-xs" style={{ color: TEXT_DIM }}>{item.detail}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </FadeIn>
            ))}
          </div>

          {/* AI Harness Tooling */}
          <FadeIn delay={0.1} className="mt-px">
            <div className="border p-6" style={{ borderColor: BORDER, background: BG_CARD }}>
              <h3 className="text-sm font-semibold uppercase tracking-wider mb-5" style={{ color: GOLD }}>AI Harness Tooling</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {[
                  { name: 'Claude Code', detail: '주력 AI 에이전트' },
                  { name: 'MCP Servers', detail: '10+ 서버 연동' },
                  { name: 'Claude Hooks', detail: '에이전트 가드레일' },
                  { name: 'Custom Skills', detail: 'gws, nlm 등' },
                  { name: 'Auto Memory', detail: 'Drive 동기화' },
                  { name: 'CLAUDE.md', detail: '컨텍스트 관리' },
                ].map(item => (
                  <div key={item.name} className="flex items-baseline gap-3">
                    <span className="text-sm font-medium" style={{ color: GOLD_LIGHT }}>{item.name}</span>
                    <span className="text-xs" style={{ color: TEXT_DIM }}>{item.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ JD MATCH ══ */}
      <section id="match" className="py-24 px-6" style={{ background: 'rgba(196,162,101,0.02)' }}>
        <div className="max-w-5xl mx-auto">
          <div className="chrono-scroll-title">
            <SectionTitle sub="크로노스튜디오 개발 자동화 엔지니어 공고와의 매칭">
              JD Match
            </SectionTitle>
          </div>

          {/* 담당업무 */}
          <FadeIn className="mb-10">
            <h3 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: GOLD }}>담당업무</h3>
            <div className="border" style={{ borderColor: BORDER }}>
              {[
                { req: 'AI 도구 설계 및 개발', match: 'Claude Code에 MCP 서버 10+개 연동, hooks/skills 커스텀 제작, auto memory 시스템 구축' },
                { req: '반복 작업 자동화 및 생산성 향상', match: 'Makefile 60+ 커맨드 배포 자동화, Docker 파이프라인, GCP VM 원격 배포/롤백' },
                { req: 'AI Agent 워크플로우 최적화', match: 'CLAUDE.md 컨텍스트 관리, 파일 메모리로 대화 간 연속성 유지, 병렬 에이전트 활용' },
                { req: 'AI Pair Programming 환경 구축', match: 'Claude Code 중심 개발 환경 구축, MCP/hooks/skills 하네스 설계, 프로젝트 전체를 AI와 협업으로 개발' },
                { req: 'AI Tooling 제작', match: 'gws CLI (Google Workspace), NotebookLM CLI, 커스텀 Statusline 등 생산성 도구 직접 제작 및 오픈소스 공개' },
              ].map((item, i) => (
                <div key={i} className="flex flex-col md:flex-row gap-2 md:gap-6 p-5 border-b last:border-0" style={{ borderColor: BORDER }}>
                  <div className="md:w-1/3 text-sm font-medium" style={{ color: TEXT }}>{item.req}</div>
                  <div className="md:w-2/3 text-sm" style={{ color: TEXT_DIM }}>{item.match}</div>
                </div>
              ))}
            </div>
          </FadeIn>

          {/* 자격요건 */}
          <FadeIn delay={0.05} className="mb-10">
            <h3 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: GOLD }}>자격요건</h3>
            <div className="border" style={{ borderColor: BORDER }}>
              {[
                { req: 'AI를 활용한 개발 경험', match: 'Claude Code로 풀스택 프로젝트 전체 개발 (봇+대시보드+웹패널+인프라), Anthropic API 직접 통합' },
                { req: 'Vibe Coding 환경 이해', match: 'GPT 복붙 -> VS Code AI -> Claude Code -> 하네스 엔지니어링까지 AI 코딩 발전 과정을 직접 경험' },
                { req: 'AI 기술 빠른 학습/적용', match: 'TTS 엔진 6종 비교, Gemma4 출시 즉시 파인튜닝 적용, 새 도구 출시 당일 테스트/적용' },
                { req: 'Python / TypeScript', match: 'Python (봇, ML 파이프라인, Flask), TypeScript (React 대시보드, Vite)' },
              ].map((item, i) => (
                <div key={i} className="flex flex-col md:flex-row gap-2 md:gap-6 p-5 border-b last:border-0" style={{ borderColor: BORDER }}>
                  <div className="md:w-1/3 text-sm font-medium" style={{ color: TEXT }}>{item.req}</div>
                  <div className="md:w-2/3 text-sm" style={{ color: TEXT_DIM }}>{item.match}</div>
                </div>
              ))}
            </div>
          </FadeIn>

          {/* 우대사항 */}
          <FadeIn delay={0.1}>
            <h3 className="text-sm font-semibold uppercase tracking-wider mb-4" style={{ color: GOLD }}>우대사항</h3>
            <div className="grid md:grid-cols-2 gap-px border" style={{ borderColor: BORDER }}>
              {[
                { title: 'Claude Code / Cursor / OpenCode', desc: 'Claude Code 주력, Cursor/Codex/Antigravity 비교 사용' },
                { title: 'AI 워크플로우 구축', desc: 'MCP 서버 연동, hooks 가드레일, skills 시스템, auto memory 파이프라인' },
                { title: 'HuggingFace 파인튜닝/추론', desc: 'CosyVoice3, Gemma4 파인튜닝 + HF 모델 관리 + Modal GPU 배포' },
                { title: 'AI API 기반 서비스', desc: 'Anthropic Claude API 통합 Discord 봇, Modal 서버리스 TTS API' },
                { title: '게임 개발 환경 이해', desc: '이터널 리턴 전적봇 운영, dak.gg API 리버스 엔지니어링, 게임 커뮤니티' },
                { title: 'Agent / MCP / Tool-use', desc: 'MCP 프로토콜 10+ 서버 운용, Tool-use 기반 에이전트 확장, 커스텀 스킬' },
                { title: '자동화 실행력', desc: 'Makefile 배포, Docker CI/CD, GCP VM 관리, Cloudflare 캐시 퍼지 자동화' },
                { title: 'AI 트렌드 + 효율화', desc: 'TTS 엔진 6종 비교, 최신 모델 출시 즉시 테스트, AI 코딩 도구 변천사 체험' },
              ].map((item, i) => (
                <div key={i} className="p-5 transition-colors hover:bg-[rgba(196,162,101,0.04)]" style={{ background: BG_CARD }}>
                  <div className="text-sm font-bold mb-1" style={{ color: TEXT }}>{item.title}</div>
                  <div className="text-xs" style={{ color: TEXT_DIM }}>{item.desc}</div>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ══ FOOTER ══ */}
      <footer className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <FadeIn>
            <div className="w-16 h-px mx-auto mb-8" style={{ background: GOLD_DIM }} />
            <h2 className="text-2xl md:text-3xl font-bold mb-3" style={{ color: TEXT }}>
              코드와 커밋 히스토리에서 확인할 수 있습니다
            </h2>
            <p className="text-sm mb-8" style={{ color: TEXT_DIM }}>
              이 포트폴리오의 모든 내용은 실제 프로젝트에 기반합니다.
            </p>
            <div className="flex justify-center gap-4">
              <LinkButton href="https://github.com/2rami/debi-marlene" icon={<IconGitHub />}>GitHub</LinkButton>
              <LinkButton href="mailto:goenho0613@gmail.com" icon={<IconMail />}>goenho0613@gmail.com</LinkButton>
            </div>
          </FadeIn>
        </div>
        <div className="text-center mt-12 text-xs" style={{ color: TEXT_DIM }}>
          Yang Gunho -- Built with Claude Code
        </div>
      </footer>

      </div>{/* end content wrapper */}
    </div>
  )
}
