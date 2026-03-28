import Header from '../components/common/Header'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

/* ── Animation Wrapper ── */
function FadeIn({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-60px' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 32 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

/* ── Section Title ── */
function SectionTitle({ label, title, description }: { label: string; title: string; description?: string }) {
  return (
    <FadeIn className="mb-12">
      <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold tracking-wider uppercase bg-debi-primary/10 text-debi-primary border border-debi-primary/20 mb-4">
        {label}
      </span>
      <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">{title}</h2>
      {description && <p className="text-discord-muted text-lg max-w-2xl">{description}</p>}
    </FadeIn>
  )
}

/* ── Stat Card ── */
function StatCard({ value, label, delay }: { value: string; label: string; delay: number }) {
  return (
    <FadeIn delay={delay} className="text-center px-6 py-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
      <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-debi-primary to-marlene-primary bg-clip-text text-transparent">
        {value}
      </div>
      <div className="text-sm text-discord-muted mt-1">{label}</div>
    </FadeIn>
  )
}

/* ── Feature Card ── */
function FeatureCard({ title, description, tags, delay }: { title: string; description: string; tags: string[]; delay: number }) {
  return (
    <FadeIn delay={delay} className="group p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-debi-primary/30 transition-all duration-300">
      <h3 className="text-lg font-bold text-white mb-2 group-hover:text-debi-primary transition-colors">{title}</h3>
      <p className="text-discord-muted text-sm leading-relaxed mb-4">{description}</p>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span key={tag} className="px-2.5 py-1 rounded-full text-xs bg-white/[0.05] text-gray-400 border border-white/[0.06]">
            {tag}
          </span>
        ))}
      </div>
    </FadeIn>
  )
}

/* ── Tech Badge ── */
function TechBadge({ name, category, delay }: { name: string; category: 'ai' | 'backend' | 'frontend' | 'infra'; delay: number }) {
  const colors = {
    ai: 'from-violet-500/20 to-purple-500/20 border-violet-500/30 text-violet-300',
    backend: 'from-emerald-500/20 to-green-500/20 border-emerald-500/30 text-emerald-300',
    frontend: 'from-debi-primary/20 to-cyan-500/20 border-debi-primary/30 text-debi-300',
    infra: 'from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-300',
  }
  return (
    <FadeIn delay={delay}>
      <span className={`inline-flex px-4 py-2 rounded-xl text-sm font-medium bg-gradient-to-r border ${colors[category]}`}>
        {name}
      </span>
    </FadeIn>
  )
}

/* ── Architecture Node ── */
function ArchNode({ label, sub, accent = false }: { label: string; sub: string; accent?: boolean }) {
  return (
    <div className={`px-5 py-4 rounded-xl border text-center ${accent ? 'bg-debi-primary/10 border-debi-primary/30' : 'bg-white/[0.03] border-white/[0.06]'}`}>
      <div className={`text-sm font-bold ${accent ? 'text-debi-primary' : 'text-white'}`}>{label}</div>
      <div className="text-xs text-discord-muted mt-0.5">{sub}</div>
    </div>
  )
}

function ArchArrow() {
  return (
    <div className="flex items-center justify-center text-discord-muted">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 5v14M19 12l-7 7-7-7" />
      </svg>
    </div>
  )
}

/* ── Screenshot Placeholder ── */
function ScreenshotPlaceholder({ label }: { label: string }) {
  return (
    <div className="aspect-video rounded-xl border border-dashed border-white/10 bg-white/[0.02] flex items-center justify-center">
      <span className="text-sm text-discord-muted">{label}</span>
    </div>
  )
}

/* ══════════════════════════════════════════════
   Portfolio Page
   ══════════════════════════════════════════════ */
export default function Portfolio() {
  return (
    <div className="min-h-screen bg-discord-darkest font-body selection:bg-debi-primary/30">
      <Header />

      {/* ── Hero ── */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Gradient orbs */}
        <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-debi-primary/[0.07] rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-40 right-1/4 w-[400px] h-[400px] bg-marlene-primary/[0.05] rounded-full blur-[120px] pointer-events-none" />

        <div className="relative z-10 max-w-5xl mx-auto px-6">
          <FadeIn>
            <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold tracking-wider uppercase bg-white/[0.05] text-discord-muted border border-white/[0.08] mb-6">
              Portfolio
            </span>
          </FadeIn>

          <FadeIn delay={0.1}>
            <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight mb-4">
              Debi & Marlene
              <span className="text-debi-primary">.</span>
            </h1>
          </FadeIn>

          <FadeIn delay={0.2}>
            <p className="text-xl md:text-2xl text-gray-400 max-w-3xl leading-relaxed mb-4">
              AI 기반 Discord 커뮤니티 봇 + 풀스택 대시보드
            </p>
            <p className="text-base text-discord-muted max-w-2xl leading-relaxed">
              이터널 리턴 게임 커뮤니티를 위한 다기능 Discord 봇.
              AI TTS, 전적 검색, 음악 재생, 노래 퀴즈 등을 제공하며,
              웹 대시보드에서 서버별 설정을 관리할 수 있습니다.
            </p>
          </FadeIn>

          <FadeIn delay={0.3}>
            <div className="flex flex-wrap gap-3 mt-8">
              <a
                href="https://github.com/kasaOT"
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-white/[0.06] border border-white/[0.1] hover:bg-white/[0.1] transition-all"
              >
                GitHub
              </a>
              <a
                href="https://debimarlene.com/landing"
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-debi-primary to-debi-600 hover:brightness-110 transition-all"
              >
                Live Site
              </a>
            </div>
          </FadeIn>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-14">
            <StatCard value="7+" label="핵심 서비스" delay={0.15} />
            <StatCard value="Full-Stack" label="1인 개발 / 운영" delay={0.25} />
            <StatCard value="GCP" label="프로덕션 배포" delay={0.35} />
            <StatCard value="AI Native" label="Claude Code 개발" delay={0.45} />
          </div>
        </div>
      </section>

      {/* ── Overview ── */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="Overview"
            title="프로젝트 개요"
            description="문제 정의부터 설계, 구현, 배포, 운영까지 전 과정을 1인으로 수행한 프로젝트입니다."
          />

          <div className="grid md:grid-cols-2 gap-6">
            <FadeIn delay={0.1} className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <h3 className="text-white font-bold mb-3">해결한 문제</h3>
              <ul className="space-y-2 text-sm text-discord-muted leading-relaxed">
                <li className="flex gap-2"><span className="text-debi-primary mt-0.5">--</span>이터널 리턴 커뮤니티에 맞춤형 봇 부재</li>
                <li className="flex gap-2"><span className="text-debi-primary mt-0.5">--</span>Discord 서버 관리 설정이 흩어져 있음</li>
                <li className="flex gap-2"><span className="text-debi-primary mt-0.5">--</span>기존 TTS 봇의 단조로운 음성 품질</li>
                <li className="flex gap-2"><span className="text-debi-primary mt-0.5">--</span>게임 전적 확인을 위해 외부 사이트 이동 필요</li>
              </ul>
            </FadeIn>

            <FadeIn delay={0.2} className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <h3 className="text-white font-bold mb-3">솔루션</h3>
              <ul className="space-y-2 text-sm text-discord-muted leading-relaxed">
                <li className="flex gap-2"><span className="text-marlene-primary mt-0.5">--</span>AI 캐릭터 음성 TTS (파인튜닝 모델)</li>
                <li className="flex gap-2"><span className="text-marlene-primary mt-0.5">--</span>웹 대시보드에서 서버별 설정 통합 관리</li>
                <li className="flex gap-2"><span className="text-marlene-primary mt-0.5">--</span>Discord 내에서 바로 전적/통계 조회</li>
                <li className="flex gap-2"><span className="text-marlene-primary mt-0.5">--</span>노래 퀴즈, 환영 메시지 등 커뮤니티 기능</li>
              </ul>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ── Architecture ── */}
      <section className="py-20 bg-white/[0.01]">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="Architecture"
            title="시스템 아키텍처"
            description="GCP 기반 컨테이너 인프라에서 봇, 대시보드, TTS 서비스가 유기적으로 동작합니다."
          />

          <FadeIn className="p-8 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
            {/* Users */}
            <div className="flex justify-center mb-4">
              <ArchNode label="Discord Users" sub="슬래시 커맨드 / 음성 채널" />
            </div>
            <ArchArrow />

            {/* Bot layer */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-4">
              <ArchNode label="Discord Bot" sub="Python / discord.py" accent />
              <ArchNode label="Dashboard" sub="React + Flask" accent />
              <ArchNode label="Webpanel" sub="React + Flask" />
            </div>
            <ArchArrow />

            {/* Service layer */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 my-4">
              <ArchNode label="Eternal Return API" sub="dak.gg / ER API" />
              <ArchNode label="AI TTS" sub="Modal Serverless" accent />
              <ArchNode label="Claude API" sub="Anthropic" accent />
              <ArchNode label="GCS Storage" sub="설정 / 데이터" />
            </div>
            <ArchArrow />

            {/* Infra layer */}
            <div className="flex justify-center mt-4">
              <ArchNode label="GCP Compute Engine" sub="Docker + nginx / asia-northeast3 (Seoul)" />
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── AI Integration ── */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="AI Integration"
            title="AI / LLM 활용"
            description="프로젝트의 핵심 차별점. LLM API 활용부터 모델 파인튜닝, Serverless 배포까지."
          />

          <div className="grid md:grid-cols-3 gap-6">
            <FadeIn delay={0.1} className="p-6 rounded-2xl bg-gradient-to-b from-violet-500/[0.06] to-transparent border border-violet-500/20">
              <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-4">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-violet-400">
                  <path d="M12 2a4 4 0 0 1 4 4c0 1.95-1.4 3.58-3.25 3.93L12 22" strokeLinecap="round" />
                  <path d="M8 6a4 4 0 0 1 8 0" />
                  <path d="M6 12a6 6 0 0 0 12 0" />
                </svg>
              </div>
              <h3 className="text-white font-bold mb-2">Claude API 통합</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                Anthropic Claude API를 봇에 직접 통합.
                사용자 대화 맥락을 이해하고 자연스러운 응답 생성.
                프롬프트 엔지니어링으로 캐릭터 페르소나 유지.
              </p>
            </FadeIn>

            <FadeIn delay={0.2} className="p-6 rounded-2xl bg-gradient-to-b from-debi-primary/[0.06] to-transparent border border-debi-primary/20">
              <div className="w-10 h-10 rounded-xl bg-debi-primary/10 border border-debi-primary/20 flex items-center justify-center mb-4">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-debi-400">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                  <line x1="12" y1="19" x2="12" y2="23" />
                </svg>
              </div>
              <h3 className="text-white font-bold mb-2">AI TTS 파인튜닝</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                Qwen3-TTS 모델을 캐릭터 음성 데이터로 파인튜닝.
                0.6B(경량) / 1.7B(고품질) 두 가지 모델 운영.
                CosyVoice3 기반 학습 파이프라인 직접 구축.
              </p>
            </FadeIn>

            <FadeIn delay={0.3} className="p-6 rounded-2xl bg-gradient-to-b from-amber-500/[0.06] to-transparent border border-amber-500/20">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-4">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-amber-400">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                </svg>
              </div>
              <h3 className="text-white font-bold mb-2">Modal Serverless 배포</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                파인튜닝된 TTS 모델을 Modal에 Serverless 배포.
                T4 GPU에서 실시간 음성 합성.
                콜드 스타트 최적화로 Discord 음성 채널 즉시 응답.
              </p>
            </FadeIn>
          </div>

          {/* AI Native 개발 */}
          <FadeIn delay={0.15} className="mt-8 p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
            <h3 className="text-white font-bold mb-3">AI Native 개발 프로세스</h3>
            <p className="text-sm text-discord-muted leading-relaxed">
              이 프로젝트는 <span className="text-white font-medium">Claude Code</span>를 핵심 개발 도구로 활용하여 구축했습니다.
              기획 단계의 아키텍처 설계부터 코드 작성, 디버깅, 배포 자동화까지 전 과정에서 AI 코딩 에이전트와 협업했으며,
              이를 통해 1인 개발자로서 풀스택 서비스의 빠른 프로토타이핑과 반복 개선이 가능했습니다.
              포트폴리오 페이지 자체도 Claude Code로 제작되었습니다.
            </p>
          </FadeIn>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-20 bg-white/[0.01]">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="Features"
            title="주요 기능"
          />

          <div className="grid md:grid-cols-2 gap-6">
            <FeatureCard
              delay={0.1}
              title="이터널 리턴 전적 검색"
              description="dak.gg API 연동으로 Discord 내에서 바로 전적, MMR 그래프, 캐릭터 통계, 팀원 정보를 조회. Discord Components V2(LayoutView)로 시각적 UI 구현."
              tags={['dak.gg API', 'LayoutView', 'MMR Graph', 'Pillow']}
            />
            <FeatureCard
              delay={0.15}
              title="AI 캐릭터 TTS"
              description="파인튜닝된 AI 모델로 캐릭터 음성을 합성하여 Discord 음성 채널에서 재생. 서버별로 음성/속도/언어 커스터마이징 가능."
              tags={['Qwen3-TTS', 'Modal GPU', 'Fine-tuning', 'Voice Channel']}
            />
            <FeatureCard
              delay={0.2}
              title="웹 대시보드"
              description="Discord OAuth2 인증 기반. 서버별 봇 설정 관리, 환영 메시지 편집, TTS 설정, 임베드 빌더, 퀴즈 관리 등을 웹에서 통합 제공."
              tags={['React', 'Flask', 'OAuth2', 'Tailwind']}
            />
            <FeatureCard
              delay={0.25}
              title="노래 퀴즈"
              description="YouTube 음원 기반 노래 맞추기 게임. 아티스트/제목 별도 정답 처리, GCS에서 글로벌 곡 목록 관리, 서버별 커스텀 곡 추가."
              tags={['YouTube', 'GCS', 'Real-time', 'FFmpeg']}
            />
            <FeatureCard
              delay={0.3}
              title="음악 재생"
              description="YouTube 검색/재생, 대기열 관리, 볼륨 조절. Discord 음성 채널에서 바로 음악 감상."
              tags={['yt-dlp', 'FFmpeg', 'Voice Channel', 'Queue']}
            />
            <FeatureCard
              delay={0.35}
              title="환영 시스템"
              description="서버 참여 시 커스텀 환영 메시지 자동 발송. 대시보드에서 메시지 내용, 임베드 스타일, 대상 채널 설정."
              tags={['Webhook', 'Embed Builder', 'Dashboard']}
            />
          </div>

          {/* Screenshot placeholders */}
          <div className="grid md:grid-cols-2 gap-6 mt-8">
            <FadeIn delay={0.1}>
              <ScreenshotPlaceholder label="Discord Bot UI (추후 추가)" />
            </FadeIn>
            <FadeIn delay={0.2}>
              <ScreenshotPlaceholder label="Dashboard (추후 추가)" />
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ── Tech Stack ── */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="Tech Stack"
            title="기술 스택"
          />

          <div className="space-y-8">
            {/* AI / ML */}
            <div>
              <h3 className="text-sm font-semibold text-violet-400 uppercase tracking-wider mb-3">AI / ML</h3>
              <div className="flex flex-wrap gap-3">
                {['Anthropic Claude API', 'Qwen3-TTS (Fine-tuned)', 'CosyVoice3', 'Modal Serverless', 'Prompt Engineering'].map((t, i) => (
                  <TechBadge key={t} name={t} category="ai" delay={i * 0.05} />
                ))}
              </div>
            </div>

            {/* Backend */}
            <div>
              <h3 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-3">Backend</h3>
              <div className="flex flex-wrap gap-3">
                {['Python', 'discord.py', 'Flask', 'FFmpeg', 'Pillow', 'yt-dlp'].map((t, i) => (
                  <TechBadge key={t} name={t} category="backend" delay={i * 0.05} />
                ))}
              </div>
            </div>

            {/* Frontend */}
            <div>
              <h3 className="text-sm font-semibold text-debi-400 uppercase tracking-wider mb-3">Frontend</h3>
              <div className="flex flex-wrap gap-3">
                {['React 19', 'TypeScript', 'Vite', 'Tailwind CSS 4', 'Framer Motion', 'Recharts'].map((t, i) => (
                  <TechBadge key={t} name={t} category="frontend" delay={i * 0.05} />
                ))}
              </div>
            </div>

            {/* Infrastructure */}
            <div>
              <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider mb-3">Infrastructure</h3>
              <div className="flex flex-wrap gap-3">
                {['GCP Compute Engine', 'Docker', 'nginx', 'Artifact Registry', 'Google Cloud Storage', 'Discord OAuth2'].map((t, i) => (
                  <TechBadge key={t} name={t} category="infra" delay={i * 0.05} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Dev Process ── */}
      <section className="py-20 bg-white/[0.01]">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="Process"
            title="개발 / 운영 프로세스"
          />

          <div className="grid md:grid-cols-3 gap-6">
            <FadeIn delay={0.1} className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <div className="text-2xl font-bold text-debi-primary mb-1">01</div>
              <h3 className="text-white font-bold mb-2">AI Native 개발</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                Claude Code를 핵심 개발 도구로 활용.
                아키텍처 설계, 코드 작성, 디버깅, 문서화까지
                AI 에이전트와의 협업으로 빠르게 반복.
              </p>
            </FadeIn>

            <FadeIn delay={0.2} className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <div className="text-2xl font-bold text-debi-primary mb-1">02</div>
              <h3 className="text-white font-bold mb-2">컨테이너 배포</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                Docker 이미지 빌드 후 GCP Artifact Registry에 Push.
                Makefile 기반 자동화로 빌드/배포/롤백을
                단일 커맨드로 처리.
              </p>
            </FadeIn>

            <FadeIn delay={0.3} className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <div className="text-2xl font-bold text-debi-primary mb-1">03</div>
              <h3 className="text-white font-bold mb-2">프로덕션 운영</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                GCP VM에서 Docker + nginx로 서비스 운영.
                Quick Deploy로 코드 변경 시 무중단 반영.
                GCS로 봇 설정/데이터 영속화.
              </p>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ── Footer CTA ── */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <FadeIn>
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-4">
              더 자세한 내용이 궁금하시면
            </h2>
            <p className="text-discord-muted mb-8">
              코드와 커밋 히스토리에서 개발 과정을 확인할 수 있습니다.
            </p>
            <div className="flex justify-center gap-4">
              <a
                href="https://github.com/kasaOT"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 rounded-xl text-sm font-semibold text-white bg-white/[0.06] border border-white/[0.1] hover:bg-white/[0.1] transition-all"
              >
                GitHub
              </a>
              <a
                href="mailto:contact@debimarlene.com"
                className="px-6 py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-debi-primary to-marlene-primary hover:brightness-110 transition-all"
              >
                Contact
              </a>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Bottom spacing */}
      <div className="h-20" />
    </div>
  )
}
