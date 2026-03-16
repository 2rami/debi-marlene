import { useState, useEffect } from 'react'
import { api } from '../../services/api'

interface Channel {
  id: string
  name: string
  type: number
  parentId: string | null
  position: number
}

interface PatchNoteConfig {
  enabled: boolean
  channelId: string | null
}

interface Props {
  channels: Channel[]
  guildId: string
}

export default function NotificationSettings({ channels, guildId }: Props) {
  const [patchNote, setPatchNote] = useState<PatchNoteConfig>({ enabled: false, channelId: null })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [status, setStatus] = useState<{ message: string; error: boolean } | null>(null)

  const textChannels = channels.filter(c => c.type === 0)

  useEffect(() => {
    fetchSettings()
  }, [guildId])

  const fetchSettings = async () => {
    setLoading(true)
    try {
      const res = await api.get<{ patchNote: PatchNoteConfig }>(`/servers/${guildId}/notifications`)
      if (res.data.patchNote) {
        setPatchNote(res.data.patchNote)
      }
    } catch {
      // use defaults
    } finally {
      setLoading(false)
    }
  }

  const savePatchNote = async () => {
    setSaving(true)
    setStatus(null)
    try {
      await api.post(`/servers/${guildId}/notifications/patchnote`, {
        channelId: patchNote.channelId,
        enabled: patchNote.enabled,
      })
      setStatus({ message: '저장되었습니다.', error: false })
    } catch {
      setStatus({ message: '저장에 실패했습니다.', error: true })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12 text-discord-muted text-sm">
        알림 설정을 불러오는 중...
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">알림 설정</h2>
        <p className="text-discord-muted text-sm">이터널 리턴 관련 알림을 서버 채널로 전달합니다.</p>
      </div>

      <div className="space-y-4">
        {/* 이터널 리턴 공식 디스코드 - 수동 팔로우 안내 */}
        <div className="p-4 bg-discord-dark rounded-lg space-y-3">
          <div>
            <p className="font-medium text-white">이터널 리턴 공식 디스코드</p>
            <p className="text-sm text-discord-muted mt-1">
              공식 디스코드의 공지 채널을 팔로우하면 서버에 자동으로 공지가 전달됩니다.
            </p>
          </div>
          <div className="p-3 bg-discord-darkest rounded-lg">
            <p className="text-sm text-white mb-2">설정 방법:</p>
            <ol className="text-sm text-discord-muted space-y-1 list-decimal list-inside">
              <li>아래 링크로 이터널 리턴 공식 디스코드에 입장</li>
              <li>공지 채널에서 "팔로우" 버튼 클릭</li>
              <li>알림을 받을 서버와 채널을 선택</li>
            </ol>
            <a
              href="https://discord.gg/nTQBksUuB8"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-3 px-4 py-2 bg-[#5865F2] hover:bg-[#4752C4] text-white text-sm font-medium rounded-lg transition-colors"
            >
              공식 디스코드 입장
            </a>
          </div>
        </div>

        {/* 패치노트 알림 */}
        <div className="p-4 bg-discord-dark rounded-lg space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-white">패치노트 알림</p>
              <p className="text-sm text-discord-muted">새로운 패치노트가 올라오면 선택한 채널에 알림을 보냅니다.</p>
            </div>
            <button
              onClick={() => { setPatchNote(prev => ({ ...prev, enabled: !prev.enabled })); setStatus(null) }}
              className={`w-12 h-6 rounded-full transition-colors ${patchNote.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${patchNote.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>

          {patchNote.enabled && (
            <div>
              <label className="block text-sm text-discord-muted mb-1">알림 채널</label>
              <select
                value={patchNote.channelId || ''}
                onChange={(e) => { setPatchNote(prev => ({ ...prev, channelId: e.target.value || null })); setStatus(null) }}
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-white focus:border-debi-primary focus:outline-none"
              >
                <option value="">채널을 선택하세요</option>
                {textChannels.map(ch => (
                  <option key={ch.id} value={ch.id}>#{ch.name}</option>
                ))}
              </select>
            </div>
          )}

          <div className="flex items-center gap-3">
            <button
              onClick={savePatchNote}
              disabled={saving || (patchNote.enabled && !patchNote.channelId)}
              className="px-4 py-2 bg-debi-primary hover:bg-debi-primary/80 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
            >
              {saving ? '저장 중...' : '저장'}
            </button>
            {status && (
              <span className={`text-sm ${status.error ? 'text-red-400' : 'text-green-400'}`}>
                {status.message}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
