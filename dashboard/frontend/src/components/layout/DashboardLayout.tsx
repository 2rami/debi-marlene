import { useState, useEffect } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { api } from '../../services/api'

interface Server {
  id: string
  name: string
  icon: string | null
  hasBot: boolean
}

interface Props {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: Props) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const { guildId } = useParams()
  const [servers, setServers] = useState<Server[]>([])

  useEffect(() => {
    const fetchServers = async () => {
      try {
        const response = await api.get<{ servers: Server[] }>('/servers')
        setServers(response.data.servers.filter(s => s.hasBot))
      } catch (error) {
        console.error('Failed to fetch servers:', error)
      }
    }
    fetchServers()
  }, [])

  const menuItems = [
    { id: 'general', label: '일반', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
    { id: 'welcome', label: '인사말', icon: 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z' },
    { id: 'tts', label: 'TTS', icon: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z' },
    { id: 'embed', label: '임베드', icon: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z' },
    { id: 'logs', label: '로그', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
    { id: 'poll', label: '투표/추첨', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'sticky', label: '고정 메시지', icon: 'M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z' },
    { id: 'quiz', label: '퀴즈', icon: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
    { id: 'stats', label: '통계', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'onboarding', label: '온보딩', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
    { id: 'autoresponse', label: '자동응답', icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z' },
    { id: 'filter', label: '필터', icon: 'M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z' },
    { id: 'moderation', label: '제재', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
    { id: 'tickets', label: '티켓', icon: 'M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z' },
  ]

  const currentTab = new URLSearchParams(location.search).get('tab') || 'general'
  const selectedServer = servers.find(s => s.id === guildId)

  // 서버 선택 전: 상단바 레이아웃
  if (!guildId) {
    return (
      <div className="min-h-screen bg-discord-dark">
        {/* Top Header */}
        <header className="h-16 bg-discord-darker border-b border-discord-light/10">
          <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center">
                <span className="text-white font-bold text-lg">D</span>
              </div>
              <span className="text-white font-semibold text-lg">Debi & Marlene</span>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center gap-6">
              <Link
                to="/"
                className={`text-sm font-medium transition-colors ${
                  location.pathname === '/' ? 'text-white' : 'text-discord-muted hover:text-white'
                }`}
              >
                홈
              </Link>
              <Link
                to="/commands"
                className={`text-sm font-medium transition-colors ${
                  location.pathname === '/commands' ? 'text-white' : 'text-discord-muted hover:text-white'
                }`}
              >
                명령어
              </Link>
              <Link
                to="/docs"
                className={`text-sm font-medium transition-colors ${
                  location.pathname === '/docs' ? 'text-white' : 'text-discord-muted hover:text-white'
                }`}
              >
                문서
              </Link>
              <Link
                to="/premium"
                className={`text-sm font-medium transition-colors ${
                  location.pathname === '/premium' ? 'text-white' : 'text-discord-muted hover:text-white'
                }`}
              >
                후원
              </Link>

              {/* Divider */}
              <div className="w-px h-6 bg-discord-light/20" />

              {/* Dashboard Link */}
              <Link
                to="/dashboard"
                className={`text-sm font-medium transition-colors ${
                  location.pathname === '/dashboard' ? 'text-debi-primary' : 'text-discord-muted hover:text-white'
                }`}
              >
                대시보드
              </Link>

              {/* User */}
              <div className="flex items-center gap-3">
                <img
                  src={user?.avatar ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=64` : '/default-avatar.png'}
                  alt={user?.username}
                  className="w-8 h-8 rounded-full"
                />
                <span className="text-sm text-white">{user?.username}</span>
                <button
                  onClick={logout}
                  className="p-1.5 text-discord-muted hover:text-discord-red rounded transition-colors"
                  title="로그아웃"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                </button>
              </div>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="min-h-[calc(100vh-4rem)]">
          {children}
        </main>
      </div>
    )
  }

  // 서버 선택 후: Discord 스타일 레이아웃
  return (
    <div className="flex h-screen bg-discord-darkest overflow-hidden">
      {/* Server Bar - Discord style */}
      <div className="w-[72px] bg-discord-darkest flex flex-col items-center py-3 gap-2 overflow-y-auto">
        {/* Home Button */}
        <Link
          to="/"
          className="w-12 h-12 rounded-2xl bg-discord-dark hover:bg-debi-primary hover:rounded-xl flex items-center justify-center transition-all group relative"
        >
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-debi-primary to-marlene-primary group-hover:rounded-xl flex items-center justify-center transition-all">
            <span className="text-white font-bold text-xl">D</span>
          </div>
          {/* Tooltip */}
          <div className="absolute left-full ml-4 px-3 py-2 bg-discord-darkest rounded-md text-white text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-lg">
            홈
          </div>
        </Link>

        {/* Divider */}
        <div className="w-8 h-0.5 bg-discord-light/20 rounded-full my-1" />

        {/* Dashboard */}
        <Link
          to="/dashboard"
          className="w-12 h-12 rounded-2xl bg-discord-dark hover:bg-debi-primary hover:rounded-xl flex items-center justify-center transition-all group relative"
        >
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <div className="absolute left-full ml-4 px-3 py-2 bg-discord-darkest rounded-md text-white text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-lg">
            대시보드
          </div>
        </Link>

        {/* Divider */}
        <div className="w-8 h-0.5 bg-discord-light/20 rounded-full my-1" />

        {/* Server List */}
        {servers.map(server => (
          <Link
            key={server.id}
            to={`/servers/${server.id}`}
            className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all group relative ${
              guildId === server.id
                ? 'rounded-xl'
                : 'hover:rounded-xl'
            }`}
          >
            {/* Active Indicator */}
            {guildId === server.id && (
              <div className="absolute left-0 w-1 h-10 bg-white rounded-r-full" />
            )}

            {server.icon ? (
              <img
                src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png?size=96`}
                alt={server.name}
                className={`w-12 h-12 transition-all ${
                  guildId === server.id ? 'rounded-xl' : 'rounded-2xl hover:rounded-xl'
                }`}
              />
            ) : (
              <div className={`w-12 h-12 bg-discord-dark flex items-center justify-center text-white font-medium transition-all ${
                guildId === server.id ? 'rounded-xl bg-debi-primary' : 'rounded-2xl hover:rounded-xl hover:bg-debi-primary'
              }`}>
                {server.name.charAt(0)}
              </div>
            )}

            {/* Tooltip */}
            <div className="absolute left-full ml-4 px-3 py-2 bg-discord-darkest rounded-md text-white text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-lg">
              {server.name}
            </div>
          </Link>
        ))}
      </div>

      {/* Channel/Menu Sidebar */}
      <div className="w-60 bg-discord-darker flex flex-col">
        {/* Server Header */}
        <div className="h-12 px-4 flex items-center border-b border-discord-darkest shadow-sm">
          <h2 className="font-semibold text-white truncate">
            {selectedServer?.name || '서버'}
          </h2>
        </div>

        {/* Menu List */}
        <div className="flex-1 overflow-y-auto p-2">
          <div className="px-2 py-1.5 text-xs font-semibold text-discord-muted uppercase">
            서버 관리
          </div>
          {menuItems.map(item => (
            <Link
              key={item.id}
              to={`/servers/${guildId}?tab=${item.id}`}
              className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm transition-colors ${
                currentTab === item.id
                  ? 'bg-discord-light/20 text-white'
                  : 'text-discord-muted hover:text-white hover:bg-discord-light/10'
              }`}
            >
              <svg className="w-5 h-5 text-discord-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
              </svg>
              {item.label}
            </Link>
          ))}
        </div>

        {/* User Panel */}
        <div className="h-[52px] px-2 bg-discord-darkest/50 flex items-center gap-2">
          <img
            src={user?.avatar ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=64` : '/default-avatar.png'}
            alt={user?.username}
            className="w-8 h-8 rounded-full"
          />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.username}</p>
            <p className="text-xs text-discord-muted">{user?.premium?.isActive ? 'Premium' : 'Free'}</p>
          </div>
          <button
            onClick={logout}
            className="p-1.5 text-discord-muted hover:text-discord-red rounded transition-colors"
            title="로그아웃"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-discord-dark">
        {children}
      </main>
    </div>
  )
}
