import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import DashboardLayout from '../components/layout/DashboardLayout'
import Loading from '../components/common/Loading'

import {
  Plus,
  Search,
  Crown,
  ShieldAlert,
  Server as ServerIcon,
  ChevronRight,
  ExternalLink
} from 'lucide-react'
import AnimatedSection from '../components/common/AnimatedSection'

interface Server {
  id: string
  name: string
  icon: string | null
  memberCount: number
  isAdmin: boolean
  hasBot: boolean
}

export default function Dashboard() {
  const { user } = useAuth()
  const [servers, setServers] = useState<Server[]>([])
  const [botClientId, setBotClientId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const fetchServers = async () => {
      try {
        const response = await api.get<{ servers: Server[], botClientId: string }>('/servers')
        setServers(response.data.servers.filter(s => s.isAdmin))
        setBotClientId(response.data.botClientId)
      } catch (error) {
        console.error('Failed to fetch servers:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchServers()
  }, [])

  const getInviteUrl = (guildId: string) => {
    if (!botClientId) return '#'
    const permissions = '8'
    return `https://discord.com/api/oauth2/authorize?client_id=${botClientId}&permissions=${permissions}&scope=bot%20applications.commands&guild_id=${guildId}`
  }

  const filteredServers = servers.filter(server =>
    server.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return <Loading />
  }

  return (
    <DashboardLayout>
      <div className="p-8 max-w-7xl mx-auto">
        {/* Welcome Header */}
        <AnimatedSection className="mb-10">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <h1 className="text-3xl md:text-4xl font-black text-white mb-2">
                Dashboard
              </h1>
              <p className="text-discord-muted text-lg">
                <span className="text-debi-primary font-bold">Bot</span>과 함께 관리할 서버를 선택하세요
              </p>
            </div>

            {/* Search Bar */}
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-discord-muted group-focus-within:text-debi-primary transition-colors" />
              <input
                type="text"
                placeholder="서버 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full md:w-80 bg-discord-dark/50 border border-discord-light/10 text-white pl-12 pr-4 py-3 rounded-xl focus:outline-none focus:border-debi-primary/50 focus:bg-discord-dark transition-all placeholder:text-discord-muted/50"
              />
            </div>
          </div>
        </AnimatedSection>

        {/* Premium Status Banner */}
        <AnimatedSection delay={0.1} className="mb-10">
          {user?.premium?.isActive ? (
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-debi-primary/20 via-discord-dark/50 to-marlene-primary/20 border border-debi-primary/20 p-6">
              <div className="flex items-center gap-4 relative z-10">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center shadow-lg shadow-debi-primary/20">
                  <Crown className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    Premium Active
                    <span className="px-2 py-0.5 rounded-full bg-debi-primary/20 text-debi-primary text-xs font-mono border border-debi-primary/20">PRO</span>
                  </h3>
                  <p className="text-discord-muted text-sm">모든 프리미엄 기능을 제한 없이 이용할 수 있습니다.</p>
                </div>
              </div>
              {/* Background glow */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-debi-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
            </div>
          ) : (
            <div className="relative overflow-hidden rounded-2xl bg-discord-dark/50 border border-discord-light/10 p-6 group hover:border-debi-primary/30 transition-colors">
              <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gray-800 flex items-center justify-center">
                    <ShieldAlert className="w-6 h-6 text-gray-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Free Plan</h3>
                    <p className="text-discord-muted text-sm">TTS 등 고급 기능을 사용하려면 업그레이드가 필요합니다.</p>
                  </div>
                </div>
                <Link
                  to="/premium"
                  className="px-6 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium text-sm border border-white/5 transition-all flex items-center gap-2 group/btn"
                >
                  업그레이드
                  <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-0.5 transition-transform" />
                </Link>
              </div>
            </div>
          )}
        </AnimatedSection>

        {/* Server Grid */}
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredServers.map((server, idx) => (
            <AnimatedSection key={server.id} delay={0.2 + (idx * 0.05)}>
              {server.hasBot ? (
                <Link
                  to={`/servers/${server.id}`}
                  className="block h-full relative group"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-debi-primary/0 to-marlene-primary/0 group-hover:from-debi-primary/10 group-hover:to-marlene-primary/10 rounded-2xl transition-all duration-500" />
                  <div className="relative h-full bg-discord-dark/40 backdrop-blur-sm border border-discord-light/10 rounded-2xl p-5 hover:border-debi-primary/30 hover:-translate-y-1 hover:shadow-xl hover:shadow-black/20 transition-all duration-300">
                    <div className="flex items-start justify-between mb-4">
                      {server.icon ? (
                        <img
                          src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png?size=128`}
                          alt={server.name}
                          className="w-16 h-16 rounded-2xl shadow-lg"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-2xl bg-discord-light/10 flex items-center justify-center text-2xl font-bold text-discord-muted border border-white/5">
                          {server.name.charAt(0)}
                        </div>
                      )}
                      <div className="p-2 rounded-lg bg-green-500/10 text-green-400 border border-green-500/10">
                        <ServerIcon className="w-5 h-5" />
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-bold text-white truncate mb-1 group-hover:text-debi-primary transition-colors">
                        {server.name}
                      </h3>
                      <p className="text-discord-muted text-sm flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-green-500" />
                        {server.memberCount.toLocaleString()} Members
                      </p>
                    </div>
                  </div>
                </Link>
              ) : (
                <div className="h-full relative group">
                  <div className="relative h-full bg-discord-dark/20 border border-discord-light/5 rounded-2xl p-5 hover:bg-discord-dark/30 transition-colors">
                    <div className="flex items-start justify-between mb-4 opacity-50">
                      {server.icon ? (
                        <img
                          src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png?size=128`}
                          alt={server.name}
                          className="w-16 h-16 rounded-2xl grayscale"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-2xl bg-discord-light/5 flex items-center justify-center text-2xl font-bold text-discord-muted/50 border border-white/5">
                          {server.name.charAt(0)}
                        </div>
                      )}
                      <div className="p-2 rounded-lg bg-white/5 text-gray-500">
                        <Plus className="w-5 h-5" />
                      </div>
                    </div>

                    <div className="mb-6">
                      <h3 className="text-lg font-bold text-white/50 truncate mb-1">
                        {server.name}
                      </h3>
                      <p className="text-discord-muted/50 text-sm">
                        봇이 서버에 없습니다
                      </p>
                    </div>

                    <a
                      href={getInviteUrl(server.id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/5 hover:border-white/20 transition-all font-medium text-sm group/invite"
                    >
                      봇 초대하기
                      <ExternalLink className="w-4 h-4 group-hover/invite:translate-x-0.5 group-hover/invite:-translate-y-0.5 transition-transform" />
                    </a>
                  </div>
                </div>
              )}
            </AnimatedSection>
          ))}
        </div>

        {filteredServers.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-20 h-20 bg-discord-dark/50 rounded-full flex items-center justify-center mb-6">
              <Search className="w-10 h-10 text-discord-muted" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">서버를 찾을 수 없습니다</h3>
            <p className="text-discord-muted">
              검색어와 일치하는 서버가 없거나 관리자 권한이 있는 서버가 없습니다.
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
