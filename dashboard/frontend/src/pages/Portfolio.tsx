import Header from '../components/common/Header'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

/* ── Animation Wrapper ── */
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

/* ── Section Title ── */
function SectionTitle({ label, title, description }: { label: string; title: string; description?: string }) {
  return (
    <FadeIn className="mb-10">
      <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold tracking-wider uppercase bg-debi-primary/10 text-debi-primary border border-debi-primary/20 mb-3">
        {label}
      </span>
      <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">{title}</h2>
      {description && <p className="text-discord-muted text-lg max-w-2xl">{description}</p>}
    </FadeIn>
  )
}

/* ── Timeline Item ── */
function TimelineItem({ date, title, description, techs, delay, accent = false }: {
  date: string; title: string; description: string; techs: string[]; delay: number; accent?: boolean
}) {
  return (
    <FadeIn delay={delay} className="relative pl-8 pb-8 last:pb-0">
      {/* Line */}
      <div className="absolute left-[7px] top-3 bottom-0 w-px bg-white/[0.06]" />
      {/* Dot */}
      <div className={`absolute left-0 top-[6px] w-[15px] h-[15px] rounded-full border-2 ${accent ? 'bg-debi-primary/20 border-debi-primary' : 'bg-discord-darker border-white/20'}`} />
      <div className="text-xs text-discord-muted mb-1">{date}</div>
      <h4 className="text-white font-bold mb-1">{title}</h4>
      <p className="text-sm text-discord-muted leading-relaxed mb-2">{description}</p>
      <div className="flex flex-wrap gap-1.5">
        {techs.map(t => (
          <span key={t} className="px-2 py-0.5 rounded-full text-xs bg-white/[0.05] text-gray-400 border border-white/[0.06]">{t}</span>
        ))}
      </div>
    </FadeIn>
  )
}

/* ── Tech Row ── */
function TechRow({ name, reason, category }: { name: string; reason: string; category: 'ai' | 'backend' | 'frontend' | 'infra' | 'data' | 'api' }) {
  const colors = {
    ai: 'border-violet-500/20 text-violet-300',
    backend: 'border-emerald-500/20 text-emerald-300',
    frontend: 'border-debi-primary/20 text-debi-300',
    infra: 'border-amber-500/20 text-amber-300',
    data: 'border-blue-500/20 text-blue-300',
    api: 'border-rose-500/20 text-rose-300',
  }
  return (
    <div className="flex items-start gap-3 py-3 border-b border-white/[0.04] last:border-0">
      <span className={`shrink-0 px-3 py-1 rounded-lg text-xs font-medium border bg-white/[0.02] ${colors[category]}`}>
        {name}
      </span>
      <span className="text-sm text-discord-muted leading-relaxed">{reason}</span>
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

/* ── TTS Engine Card ── */
function TTSCard({ name, result, reason, isFinal = false }: { name: string; result: string; reason: string; isFinal?: boolean }) {
  return (
    <div className={`px-4 py-3 rounded-xl border ${isFinal ? 'bg-debi-primary/[0.06] border-debi-primary/20' : 'bg-white/[0.02] border-white/[0.06]'}`}>
      <div className="flex items-center justify-between mb-1">
        <span className={`text-sm font-bold ${isFinal ? 'text-debi-primary' : 'text-white'}`}>{name}</span>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          result === 'ADOPTED' ? 'bg-debi-primary/20 text-debi-primary' : 'bg-white/[0.05] text-discord-muted'
        }`}>{result}</span>
      </div>
      <p className="text-xs text-discord-muted">{reason}</p>
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
      <section className="relative pt-32 pb-16 overflow-hidden">
        <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-debi-primary/[0.07] rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-40 right-1/4 w-[400px] h-[400px] bg-marlene-primary/[0.05] rounded-full blur-[120px] pointer-events-none" />

        <div className="relative z-10 max-w-5xl mx-auto px-6">
          <FadeIn>
            <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold tracking-wider uppercase bg-white/[0.05] text-discord-muted border border-white/[0.08] mb-6">
              Portfolio -- Yang Gunho
            </span>
          </FadeIn>

          <FadeIn delay={0.1}>
            <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight mb-4">
              Debi & Marlene
              <span className="text-debi-primary">.</span>
            </h1>
          </FadeIn>

          <FadeIn delay={0.2}>
            <p className="text-xl md:text-2xl text-gray-400 max-w-3xl leading-relaxed mb-3">
              AI 캐릭터 TTS + 게임 전적 검색 Discord Bot
            </p>
            <p className="text-base text-discord-muted max-w-2xl leading-relaxed">
              이터널 리턴 게임 커뮤니티를 위한 풀스택 Discord 서비스.
              AI 파인튜닝 TTS, 전적/통계 검색, 음악 재생, 노래 퀴즈 등을 제공하며,
              웹 대시보드에서 서버별 설정을 관리합니다.
              기획부터 개발, 배포, 운영까지 1인 풀스택으로 진행한 프로젝트입니다.
            </p>
          </FadeIn>

          <FadeIn delay={0.3}>
            <div className="flex flex-wrap gap-3 mt-8">
              <a href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-white/[0.06] border border-white/[0.1] hover:bg-white/[0.1] transition-all">
                GitHub
              </a>
              <a href="https://debimarlene.com/landing" target="_blank" rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-debi-primary to-debi-600 hover:brightness-110 transition-all">
                Live Site
              </a>
            </div>
          </FadeIn>

          {/* Quick Stats */}
          <FadeIn delay={0.35}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12">
              {[
                { v: '6+ months', l: '개발 기간' },
                { v: 'Full-Stack', l: '1인 개발/운영' },
                { v: 'GCP', l: '프로덕션 인프라' },
                { v: 'AI Native', l: 'Claude Code 개발' },
              ].map((s, i) => (
                <div key={i} className="text-center px-4 py-4 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
                  <div className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-debi-primary to-marlene-primary bg-clip-text text-transparent">{s.v}</div>
                  <div className="text-xs text-discord-muted mt-1">{s.l}</div>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── Development Journey ── */}
      <section className="py-16">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="Journey"
            title="개발 여정"
            description="AI 도구의 발전과 함께 성장한 기술적 과정"
          />

          <div className="grid md:grid-cols-2 gap-12">
            {/* AI 도구 발전 */}
            <FadeIn>
              <h3 className="text-white font-bold mb-6 text-lg">AI 코딩 도구 발전</h3>
              <TimelineItem delay={0} date="2025.02" title="ChatGPT (복붙 시대)"
                description="맥북 구매 후 개발 첫 시도. 코드를 복사-붙여넣기하면 위치 오류가 반복되고, AI가 파일 구조를 이해하지 못하는 한계."
                techs={['ChatGPT', 'Copy-Paste']} />
              <TimelineItem delay={0.05} date="2025.04" title="ChatGPT Work with Apps"
                description="VS Code 연동을 시도했으나 파일 하나만 접근 가능하고 성능이 제한적. 그래도 중간고사 웹디자인 과제에서 HTML 사이트를 제작하고 Vercel로 배포까지 완료."
                techs={['VS Code', 'HTML', 'Vercel']} />
              <TimelineItem delay={0.1} date="2025.06" title="Claude Code CLI" accent
                description="출시 즉시 도입. 파일시스템 전체 접근이 가능해지면서 기말과제에서 React + React Router 프로젝트를 완성. '다른 것도 만들 수 있겠다'는 자신감이 생긴 전환점."
                techs={['Claude Code', 'React', 'React Router']} />
              <TimelineItem delay={0.15} date="2025 방학" title="Discord 봇 개발 시작" accent
                description="이터널 리턴을 하고 있었는데 전적 검색봇이 없었음. '내가 만들어야겠다'고 결심하고 개발 시작."
                techs={['Python', 'discord.py']} />
            </FadeIn>

            {/* 인프라 발전 */}
            <FadeIn delay={0.1}>
              <h3 className="text-white font-bold mb-6 text-lg">인프라 전환 과정</h3>
              <TimelineItem delay={0} date="2025.08~10" title="AWS 시도"
                description="첫 클라우드 배포. 예상치 못한 6만원 청구, 복잡한 콘솔. 전적+통계 기능만 있던 초기 버전."
                techs={['AWS', 'EC2']} />
              <TimelineItem delay={0.05} date="2025.10" title="GCP 전환"
                description="Google 생태계(GCS, OAuth 등)와의 자연스러운 연동. 비용 예측 가능."
                techs={['GCP']} />
              <TimelineItem delay={0.1} date="2026.01" title="Cloud Run 시도{' -> '}VM 확정"
                description="Cloud Run은 24시간 상시 실행이 불가능. Discord 봇은 항상 온라인이어야 하므로 Compute Engine VM으로 최종 결정."
                techs={['Cloud Run', 'Compute Engine']} accent />
              <TimelineItem delay={0.15} date="2026.02" title="프로덕션 인프라 완성"
                description="Docker 컨테이너 + nginx 리버스 프록시 + Gunicorn WSGI + supervisor 프로세스 관리. Makefile로 배포 자동화."
                techs={['Docker', 'nginx', 'Gunicorn', 'Makefile']} accent />
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ── TTS Engine War ── */}
      <section className="py-16 bg-white/[0.01]">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="TTS"
            title="TTS 엔진 선택 과정"
            description="봇 사용자 대부분이 원하는 기능: 특정 캐릭터 음성으로 말하기. 6종의 TTS 엔진을 비교하며 최적의 솔루션을 찾아간 과정."
          />

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            <FadeIn delay={0.05}><TTSCard name="GPT-SoVITS" result="DROPPED" reason="로컬에서 친구들과 재밌게 사용. Modal 배포 후 반응 좋았지만 속도가 너무 느려 상용화 어렵다는 피드백" /></FadeIn>
            <FadeIn delay={0.1}><TTSCard name="Coqui TTS" result="DROPPED" reason="한국어 지원 부족" /></FadeIn>
            <FadeIn delay={0.15}><TTSCard name="XTTS" result="DROPPED" reason="속도가 여전히 느림" /></FadeIn>
            <FadeIn delay={0.2}><TTSCard name="MeloTTS" result="DROPPED" reason="CPU 기반이라 가장 빨랐지만 억양이 부자연스럽고 기계적. 발음 교정이 필요해서 복잡" /></FadeIn>
            <FadeIn delay={0.25}><TTSCard name="Qwen3-TTS" result="DROPPED" reason="성능 최고, 최신 모델. 하지만 속도가 여전히 느림" /></FadeIn>
            <FadeIn delay={0.3}><TTSCard name="CosyVoice3" result="ADOPTED" reason="비자기회귀 모델 중 가장 빠르고 음질 우수. Modal T4 GPU에 서버리스 배포" isFinal /></FadeIn>
          </div>

          <FadeIn delay={0.2} className="mt-6 p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
            <h4 className="text-white font-bold mb-2 text-sm">추가로 시도한 접근</h4>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-discord-muted">
              <div>
                <span className="text-white font-medium">Edge TTS + RVC v2 하이브리드</span>
                <p className="mt-1">무료 Edge TTS 출력을 실시간 음성 변환(RVC)으로 캐릭터 음색 적용. 파인튜닝 없이도 가능하지만 품질 한계.</p>
              </div>
              <div>
                <span className="text-white font-medium">현재 한계 & 향후 계획</span>
                <p className="mt-1">Modal에서 스트리밍 불가, GCP VM GPU는 비용 과다. 향후 옴니모델 기반 음성 대화 기능 계획 중.</p>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-16">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle label="Features" title="주요 기능" />

          <div className="grid md:grid-cols-2 gap-5">
            {([
              { title: '이터널 리턴 전적 검색', desc: 'dak.gg 사이트의 Network 탭에서 모든 API endpoint를 수집하고 문서화하여 구축. 공식 API에 없는 데이터는 hash 기반으로 보완. Discord Components V2(LayoutView)로 시각적 UI 구현.', tags: ['dak.gg API', 'ER API', 'LayoutView', 'Pillow'], note: '프로젝트 초기 가장 어려웠던 작업' },
              { title: 'AI 캐릭터 TTS', desc: 'CosyVoice3 모델을 캐릭터 음성 데이터로 파인튜닝. Colab A100/T4에서 학습 후 HuggingFace에 업로드, Modal Serverless T4 GPU에서 실시간 합성. 서버별 음성/속도 커스터마이징.', tags: ['CosyVoice3', 'Modal', 'Colab', 'HuggingFace'] },
              { title: '웹 대시보드 (유저용)', desc: 'Discord OAuth2 인증 기반. 서버별 봇 설정, 환영 메시지, TTS 설정, 임베드 빌더, 퀴즈 곡 관리 등을 웹에서 통합 제공.', tags: ['React', 'Flask', 'OAuth2', 'Tailwind'] },
              { title: '웹패널 (관리자용)', desc: '봇 로그 모니터링, 서버 사용 현황 파악, 유저 니즈 분석을 위한 관리자 전용 패널. 초기 Electron 데스크톱 앱으로도 배포했으나 업데이트 빈도 문제로 웹 전환.', tags: ['Flask', 'React', 'Cloudflare'] },
              { title: '노래 퀴즈', desc: 'YouTube 음원 기반 노래 맞추기 게임. 아티스트/제목 별도 정답 처리, GCS에서 글로벌 곡 목록 관리, 서버별 커스텀 곡 추가 가능.', tags: ['yt-dlp', 'FFmpeg', 'GCS'] },
              { title: '음악 재생 + YouTube 알림', desc: 'YouTube 검색/재생, 대기열 관리. 이터널 리턴 공식 채널 업로드 시 Discord 알림 발송으로 게임 홍보 효과.', tags: ['yt-dlp', 'YouTube API', 'FFmpeg'] },
            ] as const).map((f, i) => (
              <FadeIn key={f.title} delay={i * 0.05} className="group p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-debi-primary/30 transition-all">
                <h3 className="text-base font-bold text-white mb-2 group-hover:text-debi-primary transition-colors">{f.title}</h3>
                <p className="text-sm text-discord-muted leading-relaxed mb-3">{f.desc}</p>
                {'note' in f && f.note && <p className="text-xs text-debi-primary/70 mb-3">* {f.note}</p>}
                <div className="flex flex-wrap gap-1.5">
                  {f.tags.map(t => <span key={t} className="px-2 py-0.5 rounded-full text-xs bg-white/[0.05] text-gray-400 border border-white/[0.06]">{t}</span>)}
                </div>
              </FadeIn>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-5 mt-6">
            <FadeIn delay={0.1}><ScreenshotPlaceholder label="Discord Bot UI (추후 추가)" /></FadeIn>
            <FadeIn delay={0.15}><ScreenshotPlaceholder label="Dashboard (추후 추가)" /></FadeIn>
          </div>
        </div>
      </section>

      {/* ── Architecture ── */}
      <section className="py-16 bg-white/[0.01]">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle label="Architecture" title="시스템 아키텍처" />

          <FadeIn className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Client Layer */}
              <div>
                <h4 className="text-xs font-semibold text-discord-muted uppercase tracking-wider mb-3">Client</h4>
                <div className="space-y-2">
                  <div className="px-4 py-3 rounded-xl bg-discord-blurple/10 border border-discord-blurple/20">
                    <div className="text-sm font-bold text-white">Discord Users</div>
                    <div className="text-xs text-discord-muted">Slash Commands / Voice Channel</div>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                    <div className="text-sm font-bold text-white">Web Dashboard</div>
                    <div className="text-xs text-discord-muted">debimarlene.com (React)</div>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                    <div className="text-sm font-bold text-white">Admin Panel</div>
                    <div className="text-xs text-discord-muted">panel.debimarlene.com</div>
                  </div>
                </div>
              </div>

              {/* Service Layer */}
              <div>
                <h4 className="text-xs font-semibold text-discord-muted uppercase tracking-wider mb-3">Service</h4>
                <div className="space-y-2">
                  <div className="px-4 py-3 rounded-xl bg-debi-primary/10 border border-debi-primary/20">
                    <div className="text-sm font-bold text-debi-primary">Discord Bot</div>
                    <div className="text-xs text-discord-muted">Python / discord.py / Cogs</div>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-debi-primary/10 border border-debi-primary/20">
                    <div className="text-sm font-bold text-debi-primary">Flask API</div>
                    <div className="text-xs text-discord-muted">Gunicorn + nginx</div>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-violet-500/10 border border-violet-500/20">
                    <div className="text-sm font-bold text-violet-300">AI TTS (Modal)</div>
                    <div className="text-xs text-discord-muted">CosyVoice3 / T4 GPU</div>
                  </div>
                </div>
              </div>

              {/* Infra Layer */}
              <div>
                <h4 className="text-xs font-semibold text-discord-muted uppercase tracking-wider mb-3">Infrastructure</h4>
                <div className="space-y-2">
                  <div className="px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
                    <div className="text-sm font-bold text-amber-300">GCP VM</div>
                    <div className="text-xs text-discord-muted">Docker + Seoul Region</div>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                    <div className="text-sm font-bold text-white">GCS / Artifact Registry</div>
                    <div className="text-xs text-discord-muted">설정 저장 / 이미지 레지스트리</div>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                    <div className="text-sm font-bold text-white">Cloudflare</div>
                    <div className="text-xs text-discord-muted">CDN / 도메인 / SSL</div>
                  </div>
                </div>
              </div>
            </div>

            {/* External APIs */}
            <div className="mt-6 pt-5 border-t border-white/[0.06]">
              <h4 className="text-xs font-semibold text-discord-muted uppercase tracking-wider mb-3">External APIs</h4>
              <div className="flex flex-wrap gap-2">
                {['dak.gg API', 'Eternal Return API', 'YouTube Data API', 'Discord OAuth2', 'Anthropic Claude API', 'HuggingFace'].map(api => (
                  <span key={api} className="px-3 py-1.5 rounded-lg text-xs bg-white/[0.03] text-discord-muted border border-white/[0.06]">{api}</span>
                ))}
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── Tech Stack with Reasons ── */}
      <section className="py-16">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle
            label="Tech Stack"
            title="기술 스택 & 선택 이유"
            description="각 기술을 선택한 구체적인 이유"
          />

          <div className="grid md:grid-cols-2 gap-6">
            {/* AI / ML */}
            <FadeIn className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <h3 className="text-sm font-semibold text-violet-400 uppercase tracking-wider mb-4">AI / ML</h3>
              <TechRow name="Claude API" reason="캐릭터 대화 기능 시도 + NYPC 코드배틀 활용. 비용 문제로 현재 키만 보유, 옴니모델 음성대화 계획 중" category="ai" />
              <TechRow name="CosyVoice3" reason="6종 TTS 비교 후 채택. 비자기회귀 모델 중 가장 빠르고 음질 우수" category="ai" />
              <TechRow name="Modal" reason="서버리스 GPU. 요청 시에만 T4 GPU 과금. 상시 GPU 서버 대비 비용 절감" category="ai" />
              <TechRow name="Colab" reason="로컬 4070 Ti는 학습 중 다른 작업 불가. 셀 단위 실행이 직관적" category="ai" />
            </FadeIn>

            {/* Backend */}
            <FadeIn delay={0.05} className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <h3 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-4">Backend</h3>
              <TechRow name="Python" reason="넥슨게임즈 ML팀 친누나 추천. 패키지 생태계 풍부, AI/ML 라이브러리 연동 용이" category="backend" />
              <TechRow name="discord.py" reason="Python 선택의 자연스러운 귀결. JS 기반 discord.js 대신" category="backend" />
              <TechRow name="Flask" reason="경량 웹 프레임워크. 대시보드/웹패널 API 서버로 사용" category="backend" />
              <TechRow name="Gunicorn" reason="Flask 내장 서버는 동시 요청 처리 불가{' -> '}멀티 워커 프로덕션 서버" category="backend" />
            </FadeIn>

            {/* Frontend */}
            <FadeIn delay={0.1} className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <h3 className="text-sm font-semibold text-debi-400 uppercase tracking-wider mb-4">Frontend</h3>
              <TechRow name="React 19" reason="학교 기말과제에서 성공적으로 사용. Next.js는 당시 문제 있었음" category="frontend" />
              <TechRow name="TypeScript" reason="오류를 더 명확하게 잡을 수 있어서" category="frontend" />
              <TechRow name="Tailwind 4" reason="CSS 파일 왔다갔다 하는 게 귀찮아서. 컴포넌트 내에서 스타일 완결" category="frontend" />
              <TechRow name="Framer Motion" reason="다른 애니메이션 라이브러리보다 가볍고 모션이 다양함" category="frontend" />
            </FadeIn>

            {/* Infrastructure */}
            <FadeIn delay={0.15} className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider mb-4">Infrastructure</h3>
              <TechRow name="GCP VM" reason="AWS 비용 폭탄 + Cloud Run 상시실행 불가{' -> '}24시간 운영 가능한 VM" category="infra" />
              <TechRow name="Docker" reason="로컬과 VM 환경 일관성 보장. 빌드{' -> '}Registry Push{' -> '}VM Pull 배포" category="infra" />
              <TechRow name="Cloudflare" reason="도메인 구입 + CDN + SSL. 대시보드와 웹패널 서비스" category="infra" />
              <TechRow name="Makefile" reason="에이전트에게 배포시키면 토큰 낭비. 터미널에서 한 줄로 빌드/배포/확인" category="infra" />
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ── Development Process ── */}
      <section className="py-16 bg-white/[0.01]">
        <div className="max-w-5xl mx-auto px-6">
          <SectionTitle label="Process" title="개발 프로세스" />

          <div className="grid md:grid-cols-3 gap-5">
            <FadeIn delay={0.05} className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <div className="text-2xl font-bold text-debi-primary mb-1">01</div>
              <h3 className="text-white font-bold mb-2">AI Native 개발</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                Claude Code를 핵심 개발 도구로 활용.
                아키텍처 설계, 코드 작성, 디버깅까지
                AI 에이전트와의 협업으로 빠르게 반복.
                이 포트폴리오 페이지도 Claude Code로 제작.
              </p>
            </FadeIn>

            <FadeIn delay={0.1} className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <div className="text-2xl font-bold text-debi-primary mb-1">02</div>
              <h3 className="text-white font-bold mb-2">컨테이너 배포</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                Docker 이미지 빌드 후 GCP Artifact Registry에 Push.
                Makefile 기반 자동화로 빌드/배포/롤백을
                단일 커맨드로 처리. Quick Deploy로 무중단 반영.
              </p>
            </FadeIn>

            <FadeIn delay={0.15} className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
              <div className="text-2xl font-bold text-debi-primary mb-1">03</div>
              <h3 className="text-white font-bold mb-2">유저 피드백 반영</h3>
              <p className="text-sm text-discord-muted leading-relaxed">
                웹패널로 봇 사용 현황과 유저 니즈를 파악.
                TTS 속도 피드백{' -> '}6종 엔진 비교 후 교체.
                저작권 이슈{' -> '}유료화를 후원으로 전환.
                실제 사용자 반응 기반의 의사결정.
              </p>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ── Footer CTA ── */}
      <section className="py-16">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <FadeIn>
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">
              더 자세한 내용이 궁금하시면
            </h2>
            <p className="text-discord-muted mb-8">
              코드와 커밋 히스토리에서 개발 과정을 확인할 수 있습니다.
            </p>
            <div className="flex justify-center gap-4">
              <a href="https://github.com/2rami/debi-marlene" target="_blank" rel="noopener noreferrer"
                className="px-6 py-3 rounded-xl text-sm font-semibold text-white bg-white/[0.06] border border-white/[0.1] hover:bg-white/[0.1] transition-all">
                GitHub
              </a>
              <a href="mailto:goenho0613@gmail.com"
                className="px-6 py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-debi-primary to-marlene-primary hover:brightness-110 transition-all">
                Contact
              </a>
            </div>
          </FadeIn>
        </div>
      </section>

      <div className="h-16" />
    </div>
  )
}
