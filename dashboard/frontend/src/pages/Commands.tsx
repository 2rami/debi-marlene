import { useState, useMemo } from 'react'
import Header from '../components/common/Header'
import AnimatedSection from '../components/common/AnimatedSection'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Copy,
  Check,
  Command,
  Filter,
  Shield,
  Settings,
  Music,
  Gamepad2,
  Mic,
  MoreHorizontal
} from 'lucide-react'

interface CommandItem {
  name: string
  description: string
  /** 언제 쓰는 명령인지와 알아 두면 좋은 제약. 한 줄 설명만으로는 알 수 없는 것을 담는다. */
  detail: string
  usage: string
  category: string
  adminOnly?: boolean
}

const commands: CommandItem[] = [
  // 이터널리턴
  {
    name: '/전적', description: '플레이어 전적을 검색합니다',
    detail: '티어와 MMR, 평균 순위, 승률, 평균 킬, 많이 플레이한 실험체를 한 화면에 보여줍니다. 랭크게임과 일반게임 기록은 버튼으로 전환합니다. 디스코드 이름이 아니라 인게임 닉네임을 넣어야 하며, 대소문자와 띄어쓰기를 구분합니다.',
    usage: '/전적 닉네임:<플레이어명>', category: '이터널리턴',
  },
  {
    name: '/통계', description: '캐릭터별 통계를 보여줍니다 (다이아+)',
    detail: '다이아몬드 이상 구간의 최근 경기를 모아 실험체별 승률과 픽률을 보여줍니다. 집계 기간을 3일과 7일로 바꾸고, 티어순·승률순·픽률순으로 정렬할 수 있습니다. 패치 번호와 표본 게임 수가 함께 표시됩니다.',
    usage: '/통계', category: '이터널리턴',
  },
  {
    name: '/시즌', description: '현재 시즌 정보를 확인합니다',
    detail: '진행 중인 시즌이 몇 번째인지와 시작일로부터 며칠이 지났는지 알려줍니다. 시즌 종료가 가까우면 티어 배치나 보상 일정을 가늠하는 기준으로 쓸 수 있습니다.',
    usage: '/시즌', category: '이터널리턴',
  },
  {
    name: '/동접', description: '현재 동접자 수를 확인합니다',
    detail: '지금 이터널 리턴을 플레이 중인 인원을 보여줍니다. 매칭이 잘 잡히는 시간대인지 판단하거나, 서버 사람들과 접속 시간을 맞출 때 참고합니다.',
    usage: '/동접', category: '이터널리턴',
  },

  // 음악
  {
    name: '/음악', description: 'YouTube 음악을 재생합니다',
    detail: '검색어를 넣으면 후보를 찾아 재생하고, YouTube 주소를 그대로 넣어도 됩니다. 재생 중에는 버튼으로 대기열 확인·건너뛰기·반복을 조작합니다. 봇이 소리를 내려면 먼저 음성 채널에 들어가 있어야 합니다.',
    usage: '/음악 검색어:<URL 또는 검색어>', category: '음악',
  },

  // 음성 (TTS)
  {
    name: '/tts', description: '봇이 음성 채널에 입장하여 채팅을 읽어줍니다',
    detail: '본인이 들어가 있는 음성 채널로 봇이 따라 들어옵니다. 이후 서버에 지정된 TTS 채널에 글을 쓰면 그 문장을 소리 내어 읽습니다. 아무 채널에나 쓴 글은 읽지 않으며, 송출 시간에 따라 크레딧이 차감됩니다.',
    usage: '/tts', category: '음성',
  },

  // 퀴즈
  {
    name: '/퀴즈', description: '노래 맞추기와 이터널 리턴 퀴즈를 시작합니다',
    detail: '노래를 듣고 맞히기, 이터널 리턴 지식 겨루기, 직접 곡을 등록해 출제하기 중에서 고릅니다. 문제 수도 함께 정합니다. 노래 맞추기는 제목과 가수 점수가 따로 집계되어 아는 쪽만 맞혀도 점수를 얻습니다.',
    usage: '/퀴즈', category: '기타',
  },

  // 설정
  {
    name: '/설정', description: '서버 설정을 관리합니다 (공지 채널, TTS, 알림, 대시보드)',
    detail: '공지 채널과 명령어 채널, TTS가 읽을 채널과 목소리, 환영 메시지, 유튜브 알림을 지정합니다. 관리자 권한이 필요하며, 같은 항목을 대시보드에서 화면으로도 관리할 수 있습니다.',
    usage: '/설정', category: '설정', adminOnly: true,
  },

  // 기타
  {
    name: '/피드백', description: '봇 개발자에게 피드백을 보냅니다',
    detail: '버그 제보나 기능 제안을 개발자에게 바로 전달합니다. 오작동을 알릴 때는 어느 서버의 어떤 명령에서 무엇이 일어났는지 함께 적어 주시면 확인이 빠릅니다.',
    usage: '/피드백 내용:<피드백 내용>', category: '기타',
  },
]

const categories = [
  { id: '전체', label: 'All', icon: <Command className="w-4 h-4" /> },
  { id: '이터널리턴', label: 'Eternal Return', icon: <Gamepad2 className="w-4 h-4" /> },
  { id: '음악', label: 'Music', icon: <Music className="w-4 h-4" /> },
  { id: '음성', label: 'Voice (TTS)', icon: <Mic className="w-4 h-4" /> },
  { id: '설정', label: 'Settings', icon: <Settings className="w-4 h-4" /> },
  { id: '기타', label: 'Other', icon: <MoreHorizontal className="w-4 h-4" /> },
]

/** 명령어 목록에서 상세 가이드로 잇는 내부 링크. 목록만으로는 알 수 없는 사용법·해석을 담당한다. */
const GUIDE_LINKS = [
  { href: '/guide/record/', title: '전적 검색 가이드', desc: '/전적 결과의 티어·MMR·평균 순위·승률·평균 킬을 각각 어떻게 읽는지, 랭크와 일반게임 기록을 어떻게 나눠 보는지 설명합니다.' },
  { href: '/guide/stats/', title: '캐릭터 통계 가이드', desc: '/통계 표가 어느 구간의 표본인지, 승률과 픽률을 왜 함께 봐야 하는지, 픽을 고를 때 빠지기 쉬운 함정을 정리했습니다.' },
  { href: '/guide/tts/', title: 'TTS 음성 가이드', desc: '봇을 음성 채널로 부르는 법, 목소리와 읽을 채널 설정, 크레딧 소모, 소리가 안 들릴 때의 점검 순서를 다룹니다.' },
  { href: '/guide/music/', title: '음악 재생 가이드', desc: '/음악 으로 곡을 트는 법과 대기열·스킵·반복을 버튼으로 다루는 방법을 안내합니다.' },
  { href: '/guide/quiz/', title: '퀴즈 가이드', desc: '노래 맞추기·이터널 리턴 퀴즈·직접 출제 세 방식의 차이와, 제목과 가수가 따로 채점되는 규칙을 설명합니다.' },
  { href: '/guide/server-setup/', title: '서버 설정 가이드', desc: '관리자용. 봇 권한, 명령어 채널과 공지 채널 지정, 환영 메시지와 유튜브 알림 설정을 순서대로 정리했습니다.' },
  { href: '/guide/credits/', title: '크레딧 가이드', desc: '출석체크로 크레딧을 모으는 법과 어떤 기능에서 얼마나 소모되는지 확인하는 방법입니다.' },
  { href: '/guide/faq/', title: '자주 묻는 질문', desc: '봇이 반응하지 않을 때, 명령어가 보이지 않을 때 등 자주 들어오는 질문을 모았습니다.' },
]

export default function Commands() {
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('전체')
  const [copied, setCopied] = useState<string | null>(null)

  const filteredCommands = useMemo(() => {
    return commands.filter(cmd => {
      const matchesSearch = search === '' ||
        cmd.name.toLowerCase().includes(search.toLowerCase()) ||
        cmd.description.toLowerCase().includes(search.toLowerCase())
      const matchesCategory = selectedCategory === '전체' || cmd.category === selectedCategory
      return matchesSearch && matchesCategory
    })
  }, [search, selectedCategory])

  const copyCommand = (command: string) => {
    navigator.clipboard.writeText(command)
    setCopied(command)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="min-h-screen bg-discord-darkest selection:bg-debi-primary/30 selection:text-white">
      <Header />

      <main className="max-w-7xl mx-auto px-6 py-24 md:py-32">
        {/* Header Section */}
        <AnimatedSection className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-black mb-6 text-white">
            <span className="gradient-text">Command List</span>
          </h1>
          <p className="text-white/60 text-lg max-w-2xl mx-auto leading-relaxed">
            디스코드 봇을 100% 활용하기 위한 모든 명령어 가이드입니다.<br className="hidden md:block" />
            클릭 한 번으로 명령어를 복사하여 바로 사용보세요.
          </p>
        </AnimatedSection>

        {/* Search & Filter Section */}
        <AnimatedSection delay={0.1} className="mb-12 space-y-8">
          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto group">
            <div className="absolute inset-0 bg-gradient-to-r from-debi-primary/20 to-marlene-primary/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative">
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40 group-focus-within:text-debi-primary transition-colors" />
              <input
                type="text"
                placeholder="명령어 또는 설명 검색..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-14 pr-6 py-4 rounded-2xl bg-discord-dark/50 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-debi-primary/50 focus:bg-discord-dark transition-all shadow-lg"
              />
            </div>
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap justify-center gap-2 max-w-4xl mx-auto">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 ${selectedCategory === category.id
                  ? 'bg-gradient-to-r from-debi-primary to-marlene-primary text-white shadow-lg shadow-debi-primary/25 scale-105'
                  : 'bg-white/5 text-white/60 hover:text-white hover:bg-white/10 border border-white/5 hover:border-white/10'
                  }`}
              >
                {category.icon}
                {category.label}
                {category.id !== '전체' && (
                  <span className={`ml-1 px-1.5 py-0.5 rounded text-[10px] ${selectedCategory === category.id ? 'bg-black/20 text-white' : 'bg-black/20 text-white/40'
                    }`}>
                    {commands.filter(c => c.category === category.id).length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </AnimatedSection>

        {/* Commands Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence mode="popLayout">
            {filteredCommands.map((cmd) => (
              <motion.div
                layout
                key={cmd.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2 }}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-debi-primary/0 to-marlene-primary/0 group-hover:from-debi-primary/5 group-hover:to-marlene-primary/5 rounded-2xl transition-all duration-500" />
                <div className="relative h-full bg-discord-dark/40 backdrop-blur border border-white/5 rounded-2xl p-6 hover:border-debi-primary/30 transition-all hover:-translate-y-1 hover:shadow-xl hover:shadow-black/20">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex flex-wrap gap-2">
                      {cmd.adminOnly && (
                        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-red-500/10 text-red-400 border border-red-500/10 text-xs font-medium">
                          <Shield className="w-3 h-3" />
                          Admin
                        </div>
                      )}
                    </div>

                    <button
                      onClick={() => copyCommand(cmd.name)}
                      className={`p-2 rounded-lg transition-all ${copied === cmd.name
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-white/5 text-white/40 hover:bg-white/10 hover:text-white'
                        }`}
                      title={copied === cmd.name ? "복사됨!" : "명령어 복사"}
                    >
                      {copied === cmd.name ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* Content */}
                  <div className="mb-6">
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-debi-primary transition-colors flex items-center gap-2">
                      {cmd.name}
                    </h3>
                    <p className="text-white/60 text-sm leading-relaxed mb-3">
                      {cmd.description}
                    </p>
                    <p className="text-white/40 text-[13px] leading-relaxed">
                      {cmd.detail}
                    </p>
                  </div>

                  {/* Usage Footer */}
                  <div className="mt-auto">
                    <div className="bg-black/30 rounded-xl p-3 border border-white/5 group-hover:border-white/10 transition-colors">
                      <div className="flex items-center gap-2 text-[10px] text-white/40 mb-1 uppercase tracking-wider font-bold">
                        <Command className="w-3 h-3" />
                        Usage
                      </div>
                      <code className="text-sm text-debi-primary/90 font-mono block overflow-x-auto whitespace-nowrap scrollbar-hide">
                        {cmd.usage}
                      </code>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {filteredCommands.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-32 text-center"
          >
            <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mb-6 animate-pulse">
              <Filter className="w-12 h-12 text-white/20" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">검색 결과가 없습니다</h3>
            <p className="text-white/40">
              다른 카테고리를 선택하거나 검색어를 변경해보세요.
            </p>
          </motion.div>
        )}

        <section className="mt-20 pt-12 border-t border-white/10">
          <h2 className="text-2xl font-bold text-white mb-3">명령어별 자세한 사용법</h2>
          <p className="text-white/50 text-sm leading-relaxed mb-8 max-w-3xl">
            위 목록은 명령어와 입력 형식을 빠르게 확인하는 용도입니다.
            각 기능을 실제로 어떻게 쓰는지, 결과 화면의 숫자가 무엇을 뜻하는지, 뜻대로 동작하지 않을 때 무엇을 확인하면 되는지는
            아래 가이드에 자세히 정리해 두었습니다. 처음 봇을 들인 서버라면 서버 설정 가이드부터 보는 것을 권합니다.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {GUIDE_LINKS.map(({ href, title, desc }) => (
              <a
                key={href}
                href={href}
                className="block p-5 rounded-2xl bg-white/[0.03] border border-white/10 hover:border-white/20 transition-colors"
              >
                <div className="text-white font-bold mb-1.5">{title}</div>
                <div className="text-white/45 text-sm leading-relaxed">{desc}</div>
              </a>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}
