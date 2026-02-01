import { useState, useEffect } from 'react'

interface Channel {
  id: string
  name: string
  type: number
}

interface StickyMessageData {
  id: string
  channelId: string
  channelName: string
  content: string
  enabled: boolean
}

interface Props {
  channels: Channel[]
  guildId: string
}

export default function StickyMessage({ channels, guildId }: Props) {
  const [stickyMessages, setStickyMessages] = useState<StickyMessageData[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  // New sticky form
  const [newChannel, setNewChannel] = useState('')
  const [newContent, setNewContent] = useState('')

  const textChannels = channels.filter(c => c.type === 0)

  useEffect(() => {
    fetchStickyMessages()
  }, [guildId])

  const fetchStickyMessages = async () => {
    try {
      const response = await fetch(`/api/servers/${guildId}/sticky`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setStickyMessages(data.stickyMessages || [])
      }
    } catch {
      // Ignore
    } finally {
      setLoading(false)
    }
  }

  const createStickyMessage = async () => {
    if (!newChannel || !newContent.trim()) {
      setMessage('채널과 메시지를 입력해주세요')
      return
    }

    setSaving(true)
    setMessage(null)

    try {
      const response = await fetch(`/api/servers/${guildId}/sticky`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          channelId: newChannel,
          content: newContent
        })
      })

      if (response.ok) {
        setMessage('고정 메시지가 생성되었습니다!')
        setNewChannel('')
        setNewContent('')
        fetchStickyMessages()
      } else {
        setMessage('생성에 실패했습니다')
      }
    } catch {
      setMessage('생성에 실패했습니다')
    } finally {
      setSaving(false)
    }
  }

  const toggleStickyMessage = async (id: string, enabled: boolean) => {
    try {
      await fetch(`/api/servers/${guildId}/sticky/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ enabled })
      })
      setStickyMessages(prev =>
        prev.map(sm => sm.id === id ? { ...sm, enabled } : sm)
      )
    } catch {
      // Ignore
    }
  }

  const deleteStickyMessage = async (id: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return

    try {
      await fetch(`/api/servers/${guildId}/sticky/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      setStickyMessages(prev => prev.filter(sm => sm.id !== id))
      setMessage('삭제되었습니다')
    } catch {
      setMessage('삭제에 실패했습니다')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-discord-text mb-2">고정 메시지</h2>
        <p className="text-discord-muted text-sm">
          채널 하단에 항상 표시되는 메시지를 설정합니다. 다른 메시지가 올라오면 자동으로 다시 전송됩니다.
        </p>
      </div>

      {/* Create New */}
      <div className="p-4 bg-discord-darker rounded-lg space-y-4">
        <h3 className="font-medium text-discord-text">새 고정 메시지</h3>

        <div>
          <label className="block text-sm font-medium text-discord-muted mb-2">채널</label>
          <select
            value={newChannel}
            onChange={(e) => setNewChannel(e.target.value)}
            className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
          >
            <option value="">채널 선택...</option>
            {textChannels.map(ch => (
              <option key={ch.id} value={ch.id}>#{ch.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-discord-muted mb-2">메시지</label>
          <textarea
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="고정할 메시지 내용을 입력하세요..."
            rows={4}
            className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none resize-none"
          />
        </div>

        <button
          onClick={createStickyMessage}
          disabled={saving}
          className="w-full py-3 btn-gradient text-white font-medium rounded-lg disabled:opacity-50"
        >
          {saving ? '생성 중...' : '고정 메시지 만들기'}
        </button>
      </div>

      {message && (
        <p className={`text-sm ${message.includes('실패') ? 'text-discord-red' : 'text-green-400'}`}>
          {message}
        </p>
      )}

      {/* Existing Sticky Messages */}
      <div className="space-y-3">
        <h3 className="font-medium text-discord-text">현재 고정 메시지</h3>

        {loading ? (
          <div className="p-4 bg-discord-darker rounded-lg text-center text-discord-muted">
            로딩 중...
          </div>
        ) : stickyMessages.length === 0 ? (
          <div className="p-4 bg-discord-darker rounded-lg text-center text-discord-muted">
            설정된 고정 메시지가 없습니다
          </div>
        ) : (
          stickyMessages.map(sm => (
            <div key={sm.id} className="p-4 bg-discord-darker rounded-lg">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-medium text-discord-muted">#{sm.channelName}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${sm.enabled ? 'bg-green-500/20 text-green-400' : 'bg-discord-light/20 text-discord-muted'}`}>
                      {sm.enabled ? '활성' : '비활성'}
                    </span>
                  </div>
                  <p className="text-sm text-discord-text whitespace-pre-wrap break-words">
                    {sm.content}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => toggleStickyMessage(sm.id, !sm.enabled)}
                    className={`w-10 h-5 rounded-full transition-colors ${sm.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
                  >
                    <div className={`w-4 h-4 rounded-full bg-white transform transition-transform ${sm.enabled ? 'translate-x-5' : 'translate-x-0.5'}`} />
                  </button>
                  <button
                    onClick={() => deleteStickyMessage(sm.id)}
                    className="p-2 text-discord-red hover:bg-discord-red/20 rounded"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
