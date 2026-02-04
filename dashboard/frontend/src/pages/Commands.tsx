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
  Sparkles,
  Settings,
  Music,
  Youtube,
  Gamepad2,
  Mic,
  MoreHorizontal
} from 'lucide-react'

interface CommandItem {
  name: string
  description: string
  usage: string
  category: string
  adminOnly?: boolean
  premium?: boolean
}

const commands: CommandItem[] = [
  // 이터널리턴
  { name: '/이터널리턴 전적', description: '플레이어 전적을 검색합니다', usage: '/이터널리턴 전적 닉네임:<플레이어명>', category: '이터널리턴' },
  { name: '/이터널리턴 통계', description: '캐릭터별 통계를 보여줍니다 (다이아+)', usage: '/이터널리턴 통계', category: '이터널리턴' },
  { name: '/이터널리턴 추천', description: '티어별 승률 높은 실험체 Top 5', usage: '/이터널리턴 추천 [티어]', category: '이터널리턴' },
  { name: '/이터널리턴 동접', description: '현재 동접자 수를 확인합니다', usage: '/이터널리턴 동접', category: '이터널리턴' },

  // 유튜브
  { name: '/유튜브 알림', description: '새 영상 알림을 DM으로 받거나 해제합니다', usage: '/유튜브 알림 받기:<True/False>', category: '유튜브' },
  { name: '/유튜브 테스트', description: '새 영상 확인을 수동으로 테스트합니다', usage: '/유튜브 테스트', category: '유튜브', adminOnly: true },

  // 음악
  { name: '/음악 재생', description: 'YouTube 음악을 재생합니다', usage: '/음악 재생 검색어:<URL 또는 검색어>', category: '음악' },
  { name: '/음악 정지', description: '음악을 정지하고 대기열을 비웁니다', usage: '/음악 정지', category: '음악' },
  { name: '/음악 스킵', description: '현재 곡을 건너뜁니다', usage: '/음악 스킵', category: '음악' },
  { name: '/음악 대기열', description: '현재 대기열을 확인합니다', usage: '/음악 대기열', category: '음악' },

  // 음성 (TTS)
  { name: '/음성 입장', description: '봇이 음성 채널에 입장합니다', usage: '/음성 입장', category: '음성', premium: true },
  { name: '/음성 퇴장', description: '봇이 음성 채널에서 퇴장합니다', usage: '/음성 퇴장', category: '음성', premium: true },
  { name: '/음성 채널설정', description: '메시지를 읽어줄 TTS 채널을 설정합니다', usage: '/음성 채널설정 채널:<텍스트채널>', category: '음성', adminOnly: true, premium: true },
  { name: '/음성 목소리', description: 'TTS 음성을 설정합니다 (데비/마를렌)', usage: '/음성 목소리 음성:<데비/마를렌>', category: '음성', adminOnly: true, premium: true },
  { name: '/음성 채널해제', description: 'TTS 채널 설정을 해제합니다', usage: '/음성 채널해제', category: '음성', adminOnly: true, premium: true },

  // 설정
  { name: '/설정', description: '서버의 유튜브 알림 채널을 설정합니다', usage: '/설정', category: '설정', adminOnly: true },

  // 기타
  { name: '/피드백', description: '봇 개발자에게 피드백을 보냅니다', usage: '/피드백 내용:<피드백 내용>', category: '기타' },
]

const categories = [
  { id: '전체', label: 'All', icon: <Command className="w-4 h-4" /> },
  { id: '이터널리턴', label: 'Eternal Return', icon: <Gamepad2 className="w-4 h-4" /> },
  { id: '유튜브', label: 'YouTube', icon: <Youtube className="w-4 h-4" /> },
  { id: '음악', label: 'Music', icon: <Music className="w-4 h-4" /> },
  { id: '음성', label: 'Voice (TTS)', icon: <Mic className="w-4 h-4" /> },
  { id: '설정', label: 'Settings', icon: <Settings className="w-4 h-4" /> },
  { id: '기타', label: 'Other', icon: <MoreHorizontal className="w-4 h-4" /> },
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
                      {cmd.premium && (
                        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/10 text-xs font-medium">
                          <Sparkles className="w-3 h-3" />
                          Premium
                        </div>
                      )}
                      {!cmd.adminOnly && !cmd.premium && (
                        <div className="px-2.5 py-1 rounded-lg bg-white/5 text-white/40 border border-white/5 text-xs font-medium">
                          Basic
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
                    <p className="text-white/60 text-sm leading-relaxed">
                      {cmd.description}
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
      </main>
    </div>
  )
}
