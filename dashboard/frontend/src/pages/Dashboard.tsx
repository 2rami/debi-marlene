import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import Sidebar from '../components/common/Sidebar'
import Loading from '../components/common/Loading'

interface Server {
  id: string
  name: string
  icon: string | null
  memberCount: number
  isAdmin: boolean
}

export default function Dashboard() {
  const { user } = useAuth()
  const [servers, setServers] = useState<Server[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchServers = async () => {
      try {
        const response = await api.get<{ servers: Server[] }>('/servers')
        setServers(response.data.servers.filter(s => s.isAdmin))
      } catch (error) {
        console.error('Failed to fetch servers:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchServers()
  }, [])

  if (loading) {
    return <Loading />
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-discord-text mb-2">
              안녕하세요, {user?.username}!
            </h1>
            <p className="text-discord-muted">
              관리할 서버를 선택하세요
            </p>
          </div>

          {/* Premium Status */}
          {user?.premium.isActive ? (
            <div className="mb-8 p-4 rounded-xl bg-gradient-to-r from-debi-primary/20 to-marlene-primary/20 border border-debi-primary/30">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-discord-text">프리미엄 활성화됨</p>
                  <p className="text-sm text-discord-muted">
                    TTS 기능을 사용할 수 있습니다
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="mb-8 p-4 rounded-xl bg-discord-dark border border-discord-light/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-discord-text">무료 플랜</p>
                  <p className="text-sm text-discord-muted">
                    TTS 기능을 사용하려면 프리미엄으로 업그레이드하세요
                  </p>
                </div>
                <Link
                  to="/premium"
                  className="btn-gradient px-4 py-2 rounded-lg text-white font-medium text-sm"
                >
                  업그레이드
                </Link>
              </div>
            </div>
          )}

          {/* Server Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {servers.map(server => (
              <Link
                key={server.id}
                to={`/servers/${server.id}`}
                className="card-glow block p-4 rounded-xl bg-discord-dark border border-discord-light/20 hover:border-debi-primary/50 transition-all"
              >
                <div className="flex items-center gap-4">
                  {server.icon ? (
                    <img
                      src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png?size=64`}
                      alt={server.name}
                      className="w-12 h-12 rounded-xl"
                    />
                  ) : (
                    <div className="w-12 h-12 rounded-xl bg-discord-light flex items-center justify-center text-lg font-semibold text-discord-muted">
                      {server.name.charAt(0)}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-discord-text truncate">
                      {server.name}
                    </p>
                    <p className="text-sm text-discord-muted">
                      {server.memberCount.toLocaleString()} 멤버
                    </p>
                  </div>
                  <svg className="w-5 h-5 text-discord-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            ))}
          </div>

          {servers.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-discord-dark flex items-center justify-center">
                <svg className="w-8 h-8 text-discord-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <p className="text-discord-muted">
                관리자 권한이 있는 서버가 없습니다
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
