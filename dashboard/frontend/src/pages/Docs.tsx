import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Header from '../components/common/Header'

import TerminalBlock from '../components/docs/TerminalBlock'
import {
  Book,
  Settings,
  Zap,
  MessageSquare,
  Music,
  ChevronRight,
  ExternalLink,
  Menu,
  X
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface DocSection {
  id: string
  title: string
  icon: React.ReactNode
  content: React.ReactNode
}

export default function Docs() {
  const [activeSection, setActiveSection] = useState('getting-started')
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // Close sidebar on section change (mobile)
  useEffect(() => {
    setIsSidebarOpen(false)
  }, [activeSection])

  const docSections: DocSection[] = [
    {
      id: 'getting-started',
      title: '시작하기',
      icon: <Book className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-debi-primary/20 text-debi-primary">
                <Book className="w-6 h-6" />
              </span>
              시작하기
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              Debi & Marlene은 이터널리턴 전적 검색, 고품질 TTS, 음악 재생 등 디스코드 서버 운영에 필요한 모든 기능을 제공합니다.
              지금 바로 봇을 초대하고 서버를 업그레이드하세요.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-discord-dark/50 border border-discord-light/10">
              <h3 className="text-lg font-bold text-white mb-2">1. 봇 초대하기</h3>
              <p className="text-discord-muted mb-4 text-sm">
                관리자 권한이 있는 서버에 봇을 초대할 수 있습니다.
              </p>
              <a
                href="https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-debi-primary hover:underline font-medium"
              >
                봇 초대 링크 바로가기 <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <div className="p-6 rounded-2xl bg-discord-dark/50 border border-discord-light/10">
              <h3 className="text-lg font-bold text-white mb-2">2. 권한 확인</h3>
              <p className="text-discord-muted mb-4 text-sm">
                원활한 기능 사용을 위해 봇에게 <strong>관리자 권한</strong>을 부여하는 것을 권장합니다.
              </p>
              <div className="flex flex-wrap gap-2">
                {['메시지 보기', '메시지 보내기', '음성 연결', '말하기'].map(perm => (
                  <span key={perm} className="px-2 py-1 rounded bg-discord-light/10 text-xs text-discord-muted">
                    {perm}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-bold text-white mb-4">첫 명령어 실행해보기</h3>
            <p className="text-discord-muted mb-4">
              봇이 서버에 들어왔다면 채팅창에 <code className="text-debi-primary">/</code>를 입력하여 슬래시 커맨드를 확인해보세요.
            </p>
            <TerminalBlock
              command="/이터널리턴 추천"
              output="[Debi & Marlene] 다이아몬드+ 티어 기준 승률 TOP 5 실험체를 추천해드릴게요!"
            />
          </div>
        </div>
      )
    },
    {
      id: 'dashboard-guide',
      title: '대시보드 사용법',
      icon: <Settings className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-purple-500/20 text-purple-400">
                <Settings className="w-6 h-6" />
              </span>
              대시보드 가이드
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              웹 대시보드를 통해 봇의 설정을 직관적으로 관리할 수 있습니다.
              복잡한 명령어 입력 없이 UI에서 클릭 몇 번으로 설정을 변경해보세요.
            </p>
          </div>

          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white">주요 기능</h3>
            <ul className="grid md:grid-cols-2 gap-4">
              {[
                { title: '환영 메시지 관리', desc: '새로운 멤버 입장 시 보낼 메시지와 이미지를 설정합니다.' },
                { title: '자동 응답 설정', desc: '특정 키워드에 반응하는 자동 응답을 추가/수정합니다.' },
                { title: '금지어 필터링', desc: '서버 분위기를 해치는 단어를 자동으로 차단합니다.' },
                { title: 'TTS 설정', desc: '음성 읽기 채널과 목소리 타입을 변경합니다.' }
              ].map((item, idx) => (
                <li key={idx} className="flex gap-4 p-4 rounded-xl bg-discord-dark border border-discord-light/5">
                  <div className="w-1.5 h-1.5 rounded-full bg-debi-primary mt-2 shrink-0" />
                  <div>
                    <strong className="text-white block mb-1">{item.title}</strong>
                    <span className="text-discord-muted text-sm">{item.desc}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-r from-debi-primary/10 to-marlene-primary/10 border border-debi-primary/20">
            <div className="flex flex-col md:flex-row items-center gap-6 justify-between">
              <div>
                <h3 className="text-lg font-bold text-white mb-1">대시보드 바로가기</h3>
                <p className="text-discord-muted text-sm">지금 바로 내 서버를 관리해보세요.</p>
              </div>
              <Link
                to="/dashboard"
                className="px-6 py-3 rounded-xl bg-white text-discord-darkest font-bold hover:scale-105 transition-transform shadow-lg"
              >
                관리 시작하기
              </Link>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'voice-tts',
      title: '음성 & TTS',
      icon: <MessageSquare className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-green-500/20 text-green-400">
                <MessageSquare className="w-6 h-6" />
              </span>
              음성 (TTS) 기능
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              채팅을 치면 봇이 음성으로 읽어주는 TTS 기능을 제공합니다.
              데비와 마를렌의 생생한 목소리로 대화를 즐겨보세요! (프리미엄 기능)
            </p>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold text-white mb-3">1. 봇 부르기</h3>
              <p className="text-discord-muted mb-3">먼저 음성 채널에 있어야 합니다. 그 후 아래 명령어를 입력하세요.</p>
              <TerminalBlock command="/음성 입장" />
            </div>

            <div>
              <h3 className="text-xl font-bold text-white mb-3">2. 읽어줄 채널 설정 (관리자)</h3>
              <p className="text-discord-muted mb-3">어떤 채널의 채팅을 읽을지 설정해야 합니다.</p>
              <TerminalBlock command="/음성 채널설정 채널:#일반" output="[설정 완료] 이제 #일반 채널의 메시지를 읽어드립니다." />
            </div>

            <div>
              <h3 className="text-xl font-bold text-white mb-3">3. 목소리 변경</h3>
              <p className="text-discord-muted mb-3">취향에 따라 목소리를 변경할 수 있습니다.</p>
              <TerminalBlock command="/음성 목소리 음성:마를렌" />
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'music-guide',
      title: '음악 재생',
      icon: <Music className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-pink-500/20 text-pink-400">
                <Music className="w-6 h-6" />
              </span>
              음악 재생
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              고음질로 유튜브 음악을 감상하세요. 간편한 검색과 대기열 관리를 지원합니다.
            </p>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold text-white mb-3">음악 틀기</h3>
              <p className="text-discord-muted mb-3">제목이나 URL을 입력하면 자동으로 검색하여 재생합니다.</p>
              <TerminalBlock command="/음악 재생 검색어:NewJeans Hype Boy" />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <h4 className="font-bold text-white mb-2">대기열 확인</h4>
                <p className="text-sm text-discord-muted mb-3">현재 재생 중인 곡과 다음 곡 목록을 보여줍니다.</p>
                <code className="text-xs bg-black/30 px-2 py-1 rounded text-pink-400">/음악 대기열</code>
              </div>
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <h4 className="font-bold text-white mb-2">스킵 / 정지</h4>
                <p className="text-sm text-discord-muted mb-3">마음에 들지 않으면 넘기거나 멈출 수 있습니다.</p>
                <div className="flex gap-2">
                  <code className="text-xs bg-black/30 px-2 py-1 rounded text-pink-400">/음악 스킵</code>
                  <code className="text-xs bg-black/30 px-2 py-1 rounded text-pink-400">/음악 정지</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'support',
      title: '문의 및 지원',
      icon: <Zap className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-yellow-500/20 text-yellow-400">
                <Zap className="w-6 h-6" />
              </span>
              문의 및 지원
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              사용 중 문제가 발생했거나 건의사항이 있으신가요? 언제든 편하게 말씀해주세요.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-discord-dark border border-discord-light/10 hover:border-debi-primary/30 transition-colors">
              <h3 className="text-xl font-bold text-white mb-4">공식 서포트 서버</h3>
              <p className="text-discord-muted mb-6">
                개발자와 직접 소통하고 업데이트 소식을 가장 먼저 받아볼 수 있습니다.
              </p>
              <a
                href="https://discord.gg/aDemda3qC9"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-[#5865F2] hover:bg-[#4752C4] text-white font-bold transition-colors"
              >
                서포트 서버 참여하기
              </a>
            </div>

            <div className="p-6 rounded-2xl bg-discord-dark border border-discord-light/10">
              <h3 className="text-xl font-bold text-white mb-4">피드백 명령어</h3>
              <p className="text-discord-muted mb-4">
                디스코드 내에서 바로 피드백을 보낼 수도 있습니다.
              </p>
              <TerminalBlock command="/피드백 내용:이런 기능이 추가되었으면 좋겠어요!" />
            </div>
          </div>
        </div>
      )
    }
  ]

  return (
    <div className="min-h-screen bg-discord-darkest selection:bg-debi-primary/30 selection:text-white">
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-8 md:py-16">
        <div className="grid lg:grid-cols-[280px_1fr] gap-8 xl:gap-12">

          {/* Mobile Sidebar Toggle */}
          <div className="lg:hidden mb-6">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="flex items-center gap-2 px-4 py-3 rounded-xl bg-discord-dark border border-white/10 text-white font-medium w-full"
            >
              <Menu className="w-5 h-5" />
              {docSections.find(s => s.id === activeSection)?.title || '메뉴 선택'}
              <ChevronRight className={`w-4 h-4 ml-auto transition-transform ${isSidebarOpen ? 'rotate-90' : ''}`} />
            </button>
          </div>

          {/* Sidebar */}
          <aside className={`
            fixed inset-0 z-40 bg-discord-darkest/95 backdrop-blur-xl lg:static lg:bg-transparent lg:block
            ${isSidebarOpen ? 'block' : 'hidden'}
          `}>
            <div className="h-full overflow-y-auto p-6 lg:p-0">
              <div className="flex items-center justify-between lg:hidden mb-8">
                <span className="font-bold text-xl text-white">Documentation</span>
                <button onClick={() => setIsSidebarOpen(false)} className="p-2 text-white/50 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="sticky top-28 space-y-2">
                <p className="px-4 text-xs font-bold text-discord-muted uppercase tracking-wider mb-4 hidden lg:block">
                  Documentation
                </p>
                {docSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${activeSection === section.id
                      ? 'bg-gradient-to-r from-debi-primary/20 to-marlene-primary/20 text-white shadow-lg shadow-debi-primary/10 border border-debi-primary/20'
                      : 'text-discord-muted hover:text-white hover:bg-white/5 border border-transparent'
                      }`}
                  >
                    <span className={activeSection === section.id ? 'text-debi-primary' : 'text-gray-500'}>
                      {section.icon}
                    </span>
                    {section.title}
                    {activeSection === section.id && (
                      <ChevronRight className="w-3 h-3 ml-auto text-debi-primary" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="min-w-0">
            <AnimatePresence mode="wait">
              {docSections.map((section) => {
                if (section.id !== activeSection) return null

                return (
                  <motion.div
                    key={section.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.3 }}
                    className="bg-discord-dark/30 rounded-3xl p-6 md:p-10 border border-white/5 shadow-2xl backdrop-blur-sm"
                  >
                    {section.content}
                  </motion.div>
                )
              })}
            </AnimatePresence>

            {/* Footer Navigation (Next/Prev) */}
            <div className="mt-12 flex justify-between border-t border-white/5 pt-8">
              {/* Logic for prev/next buttons can be improved, simple implementation for now */}
              <div />
              <div className="text-right">
                <p className="text-xs text-discord-muted mb-1">도움이 더 필요하신가요?</p>
                <a href="https://discord.gg/aDemda3qC9" target="_blank" rel="noopener noreferrer" className="text-debi-primary font-bold hover:underline text-sm flex items-center gap-1 justify-end">
                  서포트 서버 바로가기 <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
