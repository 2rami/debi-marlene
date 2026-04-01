import Header from '../components/common/Header'
import { motion } from 'framer-motion'
import { useTheme } from '../contexts/ThemeContext'

function FadeIn({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

/* ── Q&A Block ── */
function QA({ q, children, delay = 0 }: { q: string; children: React.ReactNode; delay?: number }) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className="mb-6">
      <div className={`text-sm font-bold mb-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>{q}</div>
      <div className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{children}</div>
    </FadeIn>
  )
}

/* ── Section Card ── */
function Section({ title, color, children, delay = 0 }: { title: string; color: string; children: React.ReactNode; delay?: number }) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className={`p-6 md:p-8 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/80'}`}>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1.5 h-8 rounded-full" style={{ backgroundColor: color }} />
        <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>{title}</h2>
      </div>
      {children}
    </FadeIn>
  )
}

export default function BotGuide() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        {/* Header */}
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            Privileged Gateway Intents
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            Intent 요청 안내
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Debi & Marlene 봇은 Discord의 Privileged Gateway Intents 3가지를 사용합니다.
            아래는 Discord 개발자 포털 승인 심사에서 요구하는 항목들에 대한 답변입니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          {/* ── 애플리케이션 세부 정보 ── */}
          <Section title="애플리케이션 세부 정보" color="#5865f2" delay={0.1}>
            <QA q="봇의 이름과 목적은 무엇인가요?">
              <p><strong>Debi & Marlene</strong> -- 이터널 리턴(Eternal Return) 게임 커뮤니티를 위한 다기능 Discord 봇입니다.</p>
              <p className="mt-2">게임 전적 검색, AI 캐릭터 음성 합성(TTS), 음악 재생, 노래 퀴즈, 환영/퇴장 메시지, YouTube 채널 알림 등의 기능을 제공합니다.</p>
            </QA>
            <QA q="봇은 어떤 서버에서 사용되나요?" delay={0.05}>
              <p>이터널 리턴 게임을 플레이하는 한국어 Discord 서버들에서 주로 사용됩니다. 현재 약 100개 서버, 11,000명 이상의 유저가 이용 중입니다.</p>
            </QA>
            <QA q="봇의 기능을 관리하는 웹 대시보드가 있나요?" delay={0.1}>
              <p>네. <strong>debimarlene.com</strong>에서 Discord OAuth2 로그인 후 서버별 봇 설정을 관리할 수 있습니다. TTS 음성 선택, 환영 메시지 설정, 퀴즈 곡 관리 등이 가능합니다.</p>
              <p className="mt-1">관리자 전용 웹패널(<strong>panel.debimarlene.com</strong>)에서는 봇 로그 모니터링, 서버 사용 현황 분석 등을 수행합니다.</p>
            </QA>
          </Section>

          {/* ── Presence Intent ── */}
          <Section title="Presence Intent (상태 인텐트)" color="#3cabc9" delay={0.15}>
            <QA q="Presence Intent를 왜 필요로 하나요?">
              <p>유저가 현재 플레이 중인 게임 정보를 감지하여, 이터널 리턴을 플레이 중인 유저에게 자동으로 역할(Role)을 부여하거나 관련 기능을 제공하기 위해 필요합니다.</p>
            </QA>
            <QA q="어떤 사용자 상태/활동 데이터를 수집하나요?" delay={0.05}>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li>유저의 게임 활동 상태 (현재 플레이 중인 게임 이름)</li>
                <li>온라인/자리비움/방해금지 상태</li>
              </ul>
              <p className="mt-2">이 데이터는 실시간으로만 사용되며, 서버에 저장하거나 외부로 전송하지 않습니다.</p>
            </QA>
            <QA q="Presence 데이터를 어떻게 활용하나요?" delay={0.1}>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li>이터널 리턴 플레이 중인 유저에게 "게임 중" 역할 자동 부여/해제</li>
                <li>웹패널에서 서버 멤버의 온라인 상태 표시</li>
                <li>음성채널 멤버의 현재 활동 상태 확인</li>
              </ul>
            </QA>
          </Section>

          {/* ── Server Members Intent ── */}
          <Section title="Server Members Intent (서버 멤버 인텐트)" color="#e58fb6" delay={0.2}>
            <QA q="Server Members Intent를 왜 필요로 하나요?">
              <p>새로운 멤버의 입장/퇴장 이벤트를 감지하여 환영 메시지를 보내고, 서버 멤버 목록을 관리하기 위해 필요합니다.</p>
            </QA>
            <QA q="구체적으로 어떤 기능에 사용되나요?" delay={0.05}>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li><strong>환영/퇴장 메시지:</strong> 새 멤버 입장 시 Pillow로 생성한 커스텀 환영 이미지 카드 전송. 퇴장 시 알림 메시지 발송.</li>
                <li><strong>자동 역할 부여:</strong> 입장 시 서버에서 설정한 기본 역할(Role)을 자동으로 부여.</li>
                <li><strong>서버 통계:</strong> 멤버 수 변동 추적, 웹패널에서 서버 멤버 목록 조회.</li>
                <li><strong>멤버 검색:</strong> 전적 검색 시 Discord 닉네임으로 게임 닉네임 매칭.</li>
              </ul>
            </QA>
            <QA q="멤버 데이터를 저장하나요?" delay={0.1}>
              <p>서버별 설정(환영 채널, 기본 역할 등)만 Google Cloud Storage에 저장합니다. 개별 멤버의 개인정보(DM, 프로필 등)는 저장하지 않습니다.</p>
            </QA>
          </Section>

          {/* ── Message Content Intent ── */}
          <Section title="Message Content Intent (메시지 콘텐츠 인텐트)" color="#34a853" delay={0.25}>
            <QA q="Message Content Intent를 왜 필요로 하나요?">
              <p>유저가 채팅 채널에 입력하는 텍스트를 봇이 읽어야 TTS(음성 읽기), 금지어 필터링, 자동 응답 등 핵심 기능이 작동합니다.</p>
            </QA>
            <QA q="메시지 콘텐츠를 어떤 기능에 사용하나요?" delay={0.05}>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li><strong>TTS (음성 합성):</strong> 유저가 지정된 TTS 채널에 입력한 텍스트를 CosyVoice3 AI 모델로 음성 변환하여 음성 채널에 송출. 이것이 봇의 핵심 기능.</li>
                <li><strong>금지어 필터링:</strong> 서버 관리자가 설정한 금지어 목록과 메시지 내용을 대조하여 자동 삭제/경고.</li>
                <li><strong>자동 응답:</strong> 특정 키워드에 반응하는 자동 응답 기능.</li>
                <li><strong>노래 퀴즈:</strong> 퀴즈 진행 중 유저의 채팅 답변을 읽고 정답 여부 판정.</li>
              </ul>
            </QA>
            <QA q="메시지 내용을 저장하거나 외부로 전송하나요?" delay={0.1}>
              <p><strong>아니요.</strong> 메시지 내용은 실시간 처리 후 즉시 폐기됩니다. TTS의 경우 텍스트를 음성으로 변환한 뒤 원본 텍스트는 보관하지 않습니다. 봇 로그에는 명령어 사용 기록(명령어 이름, 서버 ID, 시간)만 기록되며 메시지 본문은 포함되지 않습니다.</p>
            </QA>
          </Section>

          {/* ── 데이터 처리 및 보안 ── */}
          <Section title="데이터 처리 및 보안" color="#fbbc04" delay={0.3}>
            <QA q="봇이 수집하는 데이터는 무엇인가요?">
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li><strong>서버 설정:</strong> 환영 채널 ID, TTS 채널 ID, 기본 역할 ID, 금지어 목록 등 (GCS 저장)</li>
                <li><strong>명령어 로그:</strong> 명령어 이름, 서버 ID, 사용 시간 (관리 목적)</li>
                <li><strong>퀴즈 곡 목록:</strong> 서버별 커스텀 곡 제목/아티스트 (GCS 저장)</li>
              </ul>
            </QA>
            <QA q="수집하지 않는 데이터는?" delay={0.05}>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li>유저의 DM(개인 메시지) 내용</li>
                <li>채팅 메시지 본문 (실시간 처리 후 폐기)</li>
                <li>유저의 이메일, 전화번호 등 개인정보</li>
                <li>음성 채널 녹음 데이터</li>
              </ul>
            </QA>
            <QA q="데이터는 어디에 저장되나요?" delay={0.1}>
              <p><strong>Google Cloud Storage (GCS)</strong>의 asia-northeast3(서울) 리전 버킷에 저장됩니다. 봇 서버는 같은 리전의 GCP Compute Engine VM에서 Docker 컨테이너로 운영됩니다.</p>
            </QA>
            <QA q="데이터 삭제 정책은?" delay={0.15}>
              <p>봇이 서버에서 추방되면 해당 서버의 설정 데이터는 자동으로 삭제됩니다. 유저가 요청하면 관련 데이터를 수동으로 삭제할 수 있습니다.</p>
            </QA>
          </Section>

          {/* ── 연락처 ── */}
          <FadeIn delay={0.35} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              문의사항이 있으시면 <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 연락해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
