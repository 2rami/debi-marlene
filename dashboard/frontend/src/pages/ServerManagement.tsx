import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import DashboardLayout from '../components/layout/DashboardLayout'
import Loading from '../components/common/Loading'
import WelcomeSettings from '../components/server/WelcomeSettings'
import EmbedBuilder from '../components/server/EmbedBuilder'
import LogSettings from '../components/server/LogSettings'
import PollGiveaway from '../components/server/PollGiveaway'
import StickyMessage from '../components/server/StickyMessage'
import ServerStats from '../components/server/ServerStats'
import OnboardingSettings from '../components/server/OnboardingSettings'

interface ServerSettings {
  id: string
  name: string
  icon: string | null
  features: {
    announcement: { enabled: boolean; channelId: string | null }
    welcome: { enabled: boolean; channelId: string | null; message: string; imageEnabled?: boolean }
    goodbye: { enabled: boolean; channelId: string | null; message: string; imageEnabled?: boolean }
    tts: { enabled: boolean; channelId: string | null; character: string }
    autoresponse: { enabled: boolean; rules: { id: string; trigger: string; response: string; enabled: boolean }[] }
    filter: { enabled: boolean; action: string; words: string[] }
    moderation: { enabled: boolean; warnThreshold: number }
    tickets: { enabled: boolean; categoryId: string | null }
    logs: {
      enabled: boolean
      channelId: string | null
      events: {
        memberJoin: boolean; memberLeave: boolean; messageDelete: boolean; messageEdit: boolean
        roleChange: boolean; channelChange: boolean; ban: boolean; kick: boolean; warn: boolean
      }
    }
  }
}

interface Channel {
  id: string
  name: string
  type: number
  parentId: string | null
  position: number
}

export default function ServerManagement() {
  const { guildId } = useParams<{ guildId: string }>()
  const [searchParams] = useSearchParams()
  const [settings, setSettings] = useState<ServerSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [channels, setChannels] = useState<Channel[]>([])
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  const activeTab = searchParams.get('tab') || 'general'

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [settingsRes, channelsRes] = await Promise.all([
          api.get<ServerSettings>(`/servers/${guildId}`),
          api.get<{ channels: Channel[] }>(`/servers/${guildId}/channels`)
        ])
        setSettings(settingsRes.data)
        setChannels(channelsRes.data.channels || [])
      } catch (error) {
        console.error('Failed to fetch server data:', error)
      } finally {
        setLoading(false)
      }
    }
    if (guildId) fetchData()
  }, [guildId])

  const saveSettings = async (newFeatures: Partial<ServerSettings['features']>) => {
    if (!settings) return
    setSaving(true)
    setSaveMessage(null)
    try {
      await api.patch(`/servers/${guildId}/settings`, { features: newFeatures })
      setSettings({ ...settings, features: { ...settings.features, ...newFeatures } })
      setSaveMessage('저장되었습니다!')
      setTimeout(() => setSaveMessage(null), 3000)
    } catch (error) {
      console.error('Failed to save settings:', error)
      setSaveMessage('저장에 실패했습니다.')
      setTimeout(() => setSaveMessage(null), 3000)
    } finally {
      setSaving(false)
    }
  }

  const textChannels = channels.filter(c => c.type === 0)
  const categories = channels.filter(c => c.type === 4)

  if (loading) return <Loading />

  if (!settings) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <p className="text-discord-muted">서버를 찾을 수 없습니다</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="p-6 max-w-4xl">
        {/* Save Message */}
        {saveMessage && (
          <div className={`mb-4 p-3 rounded-lg ${saveMessage.includes('실패') ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
            {saveMessage}
          </div>
        )}

        {/* Tab Content */}
        <div className="bg-discord-darker rounded-xl p-6">
          {/* 일반 설정 */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold text-white mb-2">일반 설정</h2>
                <p className="text-discord-muted text-sm">공지 채널 및 기본 설정을 관리합니다.</p>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-discord-dark rounded-lg">
                  <div>
                    <p className="font-medium text-white">공지 기능</p>
                    <p className="text-sm text-discord-muted">봇이 공지를 보낼 수 있도록 설정</p>
                  </div>
                  <button
                    onClick={() => saveSettings({ announcement: { ...settings.features.announcement, enabled: !settings.features.announcement.enabled } })}
                    className={`w-12 h-6 rounded-full transition-colors ${settings.features.announcement.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
                  >
                    <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${settings.features.announcement.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
                  </button>
                </div>
                <div className="p-4 bg-discord-dark rounded-lg">
                  <label className="block font-medium text-white mb-2">공지 채널</label>
                  <select
                    value={settings.features.announcement.channelId || ''}
                    onChange={(e) => saveSettings({ announcement: { ...settings.features.announcement, channelId: e.target.value || null } })}
                    disabled={saving}
                    className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-white focus:border-debi-primary focus:outline-none"
                  >
                    <option value="">채널 선택...</option>
                    {textChannels.map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* 인사말 */}
          {activeTab === 'welcome' && (
            <WelcomeSettings
              features={{
                welcome: settings.features.welcome,
                goodbye: settings.features.goodbye || { enabled: false, channelId: null, message: '' }
              }}
              channels={channels}
              saving={saving}
              guildId={guildId!}
              onSave={(features) => saveSettings(features as Partial<ServerSettings['features']>)}
            />
          )}

          {/* TTS */}
          {activeTab === 'tts' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold text-white mb-2">TTS 설정</h2>
                <p className="text-discord-muted text-sm">음성 채널에서 텍스트를 읽어주는 기능을 설정합니다.</p>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-discord-dark rounded-lg">
                  <div>
                    <p className="font-medium text-white">TTS 기능</p>
                    <p className="text-sm text-discord-muted">텍스트 음성 변환 활성화</p>
                  </div>
                  <button
                    onClick={() => saveSettings({ tts: { ...settings.features.tts, enabled: !settings.features.tts.enabled } })}
                    className={`w-12 h-6 rounded-full transition-colors ${settings.features.tts.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
                  >
                    <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${settings.features.tts.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
                  </button>
                </div>
                <div className="p-4 bg-discord-dark rounded-lg">
                  <label className="block font-medium text-white mb-2">TTS 채널</label>
                  <select
                    value={settings.features.tts.channelId || ''}
                    onChange={(e) => saveSettings({ tts: { ...settings.features.tts, channelId: e.target.value || null } })}
                    disabled={saving}
                    className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-white focus:border-debi-primary focus:outline-none"
                  >
                    <option value="">채널 선택...</option>
                    {textChannels.map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
                  </select>
                </div>
                <div className="p-4 bg-discord-dark rounded-lg">
                  <label className="block font-medium text-white mb-3">TTS 캐릭터</label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => saveSettings({ tts: { ...settings.features.tts, character: 'debi' } })}
                      className={`p-4 rounded-lg border-2 transition-all ${settings.features.tts.character === 'debi' ? 'border-debi-primary bg-debi-primary/10' : 'border-discord-light/20 hover:border-discord-light/40'}`}
                    >
                      <p className="font-semibold text-white">Debi</p>
                      <p className="text-sm text-discord-muted">밝고 활발한 목소리</p>
                    </button>
                    <button
                      onClick={() => saveSettings({ tts: { ...settings.features.tts, character: 'marlene' } })}
                      className={`p-4 rounded-lg border-2 transition-all ${settings.features.tts.character === 'marlene' ? 'border-marlene-primary bg-marlene-primary/10' : 'border-discord-light/20 hover:border-discord-light/40'}`}
                    >
                      <p className="font-semibold text-white">Marlene</p>
                      <p className="text-sm text-discord-muted">차분하고 부드러운 목소리</p>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 임베드 */}
          {activeTab === 'embed' && <EmbedBuilder channels={channels} guildId={guildId!} />}

          {/* 로그 */}
          {activeTab === 'logs' && (
            <LogSettings
              features={{
                logs: settings.features.logs || {
                  enabled: false, channelId: null,
                  events: { memberJoin: true, memberLeave: true, messageDelete: true, messageEdit: false, roleChange: false, channelChange: false, ban: true, kick: true, warn: true }
                }
              }}
              channels={channels}
              saving={saving}
              onSave={(features) => saveSettings(features as Partial<ServerSettings['features']>)}
            />
          )}

          {/* 투표/추첨 */}
          {activeTab === 'poll' && <PollGiveaway channels={channels} guildId={guildId!} />}

          {/* 고정 메시지 */}
          {activeTab === 'sticky' && <StickyMessage channels={channels} guildId={guildId!} />}

          {/* 통계 */}
          {activeTab === 'stats' && <ServerStats guildId={guildId!} />}

          {/* 온보딩 */}
          {activeTab === 'onboarding' && <OnboardingSettings guildId={guildId!} />}

          {/* 자동응답 */}
          {activeTab === 'autoresponse' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white mb-2">자동응답</h2>
                  <p className="text-discord-muted text-sm">특정 키워드에 자동으로 응답하도록 설정합니다.</p>
                </div>
                <button
                  onClick={() => saveSettings({ autoresponse: { ...settings.features.autoresponse, enabled: !settings.features.autoresponse.enabled } })}
                  className={`w-12 h-6 rounded-full transition-colors ${settings.features.autoresponse.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
                >
                  <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${settings.features.autoresponse.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
                </button>
              </div>
              <div className="p-4 bg-discord-dark rounded-lg text-center text-discord-muted">
                <p>자동응답 규칙 관리 기능은 준비 중입니다.</p>
              </div>
            </div>
          )}

          {/* 필터 */}
          {activeTab === 'filter' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white mb-2">채팅 필터</h2>
                  <p className="text-discord-muted text-sm">금지어 및 스팸 필터를 설정합니다.</p>
                </div>
                <button
                  onClick={() => saveSettings({ filter: { ...settings.features.filter, enabled: !settings.features.filter.enabled } })}
                  className={`w-12 h-6 rounded-full transition-colors ${settings.features.filter.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
                >
                  <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${settings.features.filter.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
                </button>
              </div>
              <div className="p-4 bg-discord-dark rounded-lg">
                <label className="block font-medium text-white mb-2">필터 액션</label>
                <select
                  value={settings.features.filter.action || 'delete'}
                  onChange={(e) => saveSettings({ filter: { ...settings.features.filter, action: e.target.value } })}
                  disabled={saving}
                  className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-white focus:border-debi-primary focus:outline-none"
                >
                  <option value="delete">메시지 삭제</option>
                  <option value="warn">경고 + 삭제</option>
                  <option value="mute">뮤트 + 삭제</option>
                </select>
              </div>
            </div>
          )}

          {/* 제재 */}
          {activeTab === 'moderation' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white mb-2">제재 관리</h2>
                  <p className="text-discord-muted text-sm">경고, 뮤트, 킥, 밴 등 제재 기록을 관리합니다.</p>
                </div>
                <button
                  onClick={() => saveSettings({ moderation: { ...settings.features.moderation, enabled: !settings.features.moderation.enabled } })}
                  className={`w-12 h-6 rounded-full transition-colors ${settings.features.moderation.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
                >
                  <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${settings.features.moderation.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
                </button>
              </div>
              <div className="p-4 bg-discord-dark rounded-lg">
                <label className="block font-medium text-white mb-2">자동 밴 경고 횟수</label>
                <p className="text-xs text-discord-muted mb-2">이 횟수만큼 경고받으면 자동으로 밴됩니다 (0 = 비활성화)</p>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={settings.features.moderation.warnThreshold || 0}
                  onChange={(e) => saveSettings({ moderation: { ...settings.features.moderation, warnThreshold: parseInt(e.target.value) || 0 } })}
                  className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-white focus:border-debi-primary focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* 티켓 */}
          {activeTab === 'tickets' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white mb-2">티켓 시스템</h2>
                  <p className="text-discord-muted text-sm">사용자 문의 티켓을 관리합니다.</p>
                </div>
                <button
                  onClick={() => saveSettings({ tickets: { ...settings.features.tickets, enabled: !settings.features.tickets.enabled } })}
                  className={`w-12 h-6 rounded-full transition-colors ${settings.features.tickets.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
                >
                  <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${settings.features.tickets.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
                </button>
              </div>
              <div className="p-4 bg-discord-dark rounded-lg">
                <label className="block font-medium text-white mb-2">티켓 카테고리</label>
                <select
                  value={settings.features.tickets.categoryId || ''}
                  onChange={(e) => saveSettings({ tickets: { ...settings.features.tickets, categoryId: e.target.value || null } })}
                  disabled={saving}
                  className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-white focus:border-debi-primary focus:outline-none"
                >
                  <option value="">카테고리 선택...</option>
                  {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                </select>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
