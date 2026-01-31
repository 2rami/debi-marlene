import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import Sidebar from '../components/common/Sidebar'
import Loading from '../components/common/Loading'

interface ServerSettings {
  id: string
  name: string
  icon: string | null
  features: {
    announcement: {
      enabled: boolean
      channelId: string | null
    }
    welcome: {
      enabled: boolean
      channelId: string | null
      message: string
    }
    tts: {
      enabled: boolean
      channelId: string | null
      character: string
    }
    autoresponse: {
      enabled: boolean
    }
    filter: {
      enabled: boolean
      action: string
    }
    moderation: {
      enabled: boolean
      warnThreshold: number
    }
    tickets: {
      enabled: boolean
      categoryId: string | null
    }
  }
}

type TabType = 'general' | 'welcome' | 'autoresponse' | 'filter' | 'moderation' | 'tickets'

export default function ServerManagement() {
  const { guildId } = useParams<{ guildId: string }>()
  const [settings, setSettings] = useState<ServerSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<TabType>('general')

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await api.get<ServerSettings>(`/servers/${guildId}`)
        setSettings(response.data)
      } catch (error) {
        console.error('Failed to fetch server settings:', error)
      } finally {
        setLoading(false)
      }
    }
    if (guildId) {
      fetchSettings()
    }
  }, [guildId])

  if (loading) {
    return <Loading />
  }

  if (!settings) {
    return (
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 p-8 flex items-center justify-center">
          <div className="text-center">
            <p className="text-discord-muted mb-4">서버를 찾을 수 없습니다</p>
            <Link to="/dashboard" className="text-debi-primary hover:underline">
              대시보드로 돌아가기
            </Link>
          </div>
        </main>
      </div>
    )
  }

  const tabs: { id: TabType; label: string }[] = [
    { id: 'general', label: '일반' },
    { id: 'welcome', label: '환영 메시지' },
    { id: 'autoresponse', label: '자동응답' },
    { id: 'filter', label: '채팅 필터' },
    { id: 'moderation', label: '제재 관리' },
    { id: 'tickets', label: '티켓' },
  ]

  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 text-discord-muted hover:text-discord-text mb-4"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              대시보드
            </Link>

            <div className="flex items-center gap-4">
              {settings.icon ? (
                <img
                  src={`https://cdn.discordapp.com/icons/${settings.id}/${settings.icon}.png?size=64`}
                  alt={settings.name}
                  className="w-16 h-16 rounded-xl"
                />
              ) : (
                <div className="w-16 h-16 rounded-xl bg-discord-light flex items-center justify-center text-2xl font-semibold text-discord-muted">
                  {settings.name.charAt(0)}
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold text-discord-text">
                  {settings.name}
                </h1>
                <p className="text-discord-muted">서버 설정</p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mb-6 border-b border-discord-light/20">
            <div className="flex gap-1 overflow-x-auto">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-debi-primary text-debi-primary'
                      : 'border-transparent text-discord-muted hover:text-discord-text'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="bg-discord-dark rounded-xl p-6 border border-discord-light/20">
            {activeTab === 'general' && (
              <div>
                <h2 className="text-xl font-semibold text-discord-text mb-4">일반 설정</h2>
                <p className="text-discord-muted">공지 채널 및 기본 설정을 관리합니다.</p>
                {/* TODO: Add general settings form */}
              </div>
            )}

            {activeTab === 'welcome' && (
              <div>
                <h2 className="text-xl font-semibold text-discord-text mb-4">환영 메시지</h2>
                <p className="text-discord-muted">새 멤버가 서버에 참가했을 때 보낼 메시지를 설정합니다.</p>
                {/* TODO: Add welcome message editor */}
              </div>
            )}

            {activeTab === 'autoresponse' && (
              <div>
                <h2 className="text-xl font-semibold text-discord-text mb-4">자동응답</h2>
                <p className="text-discord-muted">특정 키워드에 자동으로 응답하도록 설정합니다.</p>
                {/* TODO: Add autoresponse list */}
              </div>
            )}

            {activeTab === 'filter' && (
              <div>
                <h2 className="text-xl font-semibold text-discord-text mb-4">채팅 필터</h2>
                <p className="text-discord-muted">금지어 및 스팸 필터를 설정합니다.</p>
                {/* TODO: Add filter list */}
              </div>
            )}

            {activeTab === 'moderation' && (
              <div>
                <h2 className="text-xl font-semibold text-discord-text mb-4">제재 관리</h2>
                <p className="text-discord-muted">경고, 뮤트, 킥, 밴 등 제재 기록을 관리합니다.</p>
                {/* TODO: Add moderation panel */}
              </div>
            )}

            {activeTab === 'tickets' && (
              <div>
                <h2 className="text-xl font-semibold text-discord-text mb-4">티켓 시스템</h2>
                <p className="text-discord-muted">사용자 문의 티켓을 관리합니다.</p>
                {/* TODO: Add ticket settings */}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
