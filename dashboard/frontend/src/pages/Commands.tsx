import { useState, useMemo } from 'react'
import Header from '../components/common/Header'

interface Command {
  name: string
  description: string
  usage: string
  category: string
  adminOnly?: boolean
  premium?: boolean
}

const commands: Command[] = [
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

const categories = ['전체', '이터널리턴', '유튜브', '음악', '음성', '설정', '기타']

export default function Commands() {
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('전체')

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
  }

  return (
    <div className="min-h-screen bg-discord-darkest">
      <Header />

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="gradient-text">Commands</span>
          </h1>
          <p className="text-discord-muted max-w-2xl mx-auto">
            Debi & Marlene 봇의 모든 슬래시 커맨드 목록입니다
          </p>
        </div>

        {/* Search & Filter */}
        <div className="mb-8 space-y-4">
          {/* Search */}
          <div className="relative max-w-md mx-auto">
            <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-discord-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="커맨드 검색... (Ctrl+/)"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl bg-discord-dark border border-discord-light/20 text-discord-text placeholder-discord-muted focus:outline-none focus:border-debi-primary/50"
            />
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap justify-center gap-2">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === category
                    ? 'bg-debi-primary text-white'
                    : 'bg-discord-dark text-discord-muted hover:text-discord-text hover:bg-discord-light/20'
                }`}
              >
                {category}
                <span className="ml-2 text-xs opacity-70">
                  {category === '전체'
                    ? commands.length
                    : commands.filter(c => c.category === category).length}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Commands Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCommands.map((cmd) => (
            <div
              key={cmd.name}
              className="card-glow bg-discord-dark rounded-xl p-5 border border-discord-light/20 hover:border-debi-primary/30 transition-all"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <code className="text-debi-primary font-semibold">{cmd.name}</code>
                  <button
                    onClick={() => copyCommand(cmd.name)}
                    className="p-1 rounded hover:bg-discord-light/20 text-discord-muted hover:text-discord-text transition-colors"
                    title="복사"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
                <div className="flex gap-1">
                  {cmd.adminOnly && (
                    <span className="px-2 py-0.5 text-xs rounded bg-discord-red/20 text-discord-red">
                      Admin
                    </span>
                  )}
                  {cmd.premium && (
                    <span className="px-2 py-0.5 text-xs rounded bg-gradient-to-r from-debi-primary/20 to-marlene-primary/20 text-debi-primary">
                      Premium
                    </span>
                  )}
                </div>
              </div>

              {/* Description */}
              <p className="text-discord-muted text-sm mb-3">
                {cmd.description}
              </p>

              {/* Usage */}
              <div className="bg-discord-darker rounded-lg p-3">
                <p className="text-xs text-discord-muted mb-1">Usage</p>
                <code className="text-sm text-discord-text">{cmd.usage}</code>
              </div>

              {/* Category Tag */}
              <div className="mt-3">
                <span className="px-2 py-1 text-xs rounded bg-discord-light/10 text-discord-muted">
                  {cmd.category}
                </span>
              </div>
            </div>
          ))}
        </div>

        {filteredCommands.length === 0 && (
          <div className="text-center py-12">
            <p className="text-discord-muted">검색 결과가 없습니다</p>
          </div>
        )}
      </main>
    </div>
  )
}
