import { useState } from 'react'

interface Channel {
  id: string
  name: string
  type: number
}

interface EmbedData {
  title: string
  description: string
  color: string
  footer: string
  thumbnail: string
  image: string
  author: {
    name: string
    iconUrl: string
  }
  fields: {
    name: string
    value: string
    inline: boolean
  }[]
}

interface Props {
  channels: Channel[]
  guildId: string
}

const DEFAULT_EMBED: EmbedData = {
  title: '',
  description: '',
  color: '#5865F2',
  footer: '',
  thumbnail: '',
  image: '',
  author: { name: '', iconUrl: '' },
  fields: [],
}

export default function EmbedBuilder({ channels, guildId }: Props) {
  const [embed, setEmbed] = useState<EmbedData>(DEFAULT_EMBED)
  const [selectedChannel, setSelectedChannel] = useState<string>('')
  const [sending, setSending] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  const textChannels = channels.filter(c => c.type === 0)

  const updateEmbed = (updates: Partial<EmbedData>) => {
    setEmbed(prev => ({ ...prev, ...updates }))
  }

  const addField = () => {
    setEmbed(prev => ({
      ...prev,
      fields: [...prev.fields, { name: '', value: '', inline: false }]
    }))
  }

  const updateField = (index: number, updates: Partial<EmbedData['fields'][0]>) => {
    setEmbed(prev => ({
      ...prev,
      fields: prev.fields.map((f, i) => i === index ? { ...f, ...updates } : f)
    }))
  }

  const removeField = (index: number) => {
    setEmbed(prev => ({
      ...prev,
      fields: prev.fields.filter((_, i) => i !== index)
    }))
  }

  const sendEmbed = async () => {
    if (!selectedChannel) {
      setMessage('채널을 선택해주세요')
      return
    }

    setSending(true)
    setMessage(null)

    try {
      const response = await fetch(`/api/servers/${guildId}/embed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ channelId: selectedChannel, embed })
      })

      if (response.ok) {
        setMessage('임베드가 전송되었습니다!')
        setEmbed(DEFAULT_EMBED)
      } else {
        setMessage('전송에 실패했습니다')
      }
    } catch {
      setMessage('전송에 실패했습니다')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-discord-text mb-2">임베드 빌더</h2>
        <p className="text-discord-muted text-sm">커스텀 임베드 메시지를 만들어 채널에 전송합니다.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Editor */}
        <div className="space-y-4">
          {/* Channel Select */}
          <div className="p-4 bg-discord-darker rounded-lg">
            <label className="block text-sm font-medium text-discord-muted mb-2">전송할 채널</label>
            <select
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
              className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
            >
              <option value="">채널 선택...</option>
              {textChannels.map(ch => (
                <option key={ch.id} value={ch.id}>#{ch.name}</option>
              ))}
            </select>
          </div>

          {/* Basic Info */}
          <div className="p-4 bg-discord-darker rounded-lg space-y-3">
            <div>
              <label className="block text-sm font-medium text-discord-muted mb-1">제목</label>
              <input
                type="text"
                value={embed.title}
                onChange={(e) => updateEmbed({ title: e.target.value })}
                placeholder="임베드 제목"
                className="w-full p-2 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text text-sm focus:border-debi-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-discord-muted mb-1">설명</label>
              <textarea
                value={embed.description}
                onChange={(e) => updateEmbed({ description: e.target.value })}
                placeholder="임베드 내용을 입력하세요..."
                rows={4}
                className="w-full p-2 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text text-sm focus:border-debi-primary focus:outline-none resize-none"
              />
            </div>
            <div className="flex gap-3">
              <div className="flex-1">
                <label className="block text-sm font-medium text-discord-muted mb-1">색상</label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={embed.color}
                    onChange={(e) => updateEmbed({ color: e.target.value })}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={embed.color}
                    onChange={(e) => updateEmbed({ color: e.target.value })}
                    className="flex-1 p-2 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text text-sm focus:border-debi-primary focus:outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 bg-discord-darker rounded-lg">
            <label className="block text-sm font-medium text-discord-muted mb-1">푸터</label>
            <input
              type="text"
              value={embed.footer}
              onChange={(e) => updateEmbed({ footer: e.target.value })}
              placeholder="푸터 텍스트"
              className="w-full p-2 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text text-sm focus:border-debi-primary focus:outline-none"
            />
          </div>

          {/* Images */}
          <div className="p-4 bg-discord-darker rounded-lg space-y-3">
            <div>
              <label className="block text-sm font-medium text-discord-muted mb-1">썸네일 URL</label>
              <input
                type="text"
                value={embed.thumbnail}
                onChange={(e) => updateEmbed({ thumbnail: e.target.value })}
                placeholder="https://example.com/image.png"
                className="w-full p-2 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text text-sm focus:border-debi-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-discord-muted mb-1">이미지 URL</label>
              <input
                type="text"
                value={embed.image}
                onChange={(e) => updateEmbed({ image: e.target.value })}
                placeholder="https://example.com/image.png"
                className="w-full p-2 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text text-sm focus:border-debi-primary focus:outline-none"
              />
            </div>
          </div>

          {/* Fields */}
          <div className="p-4 bg-discord-darker rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium text-discord-muted">필드</label>
              <button
                onClick={addField}
                className="text-xs px-3 py-1 bg-debi-primary text-white rounded hover:bg-debi-primary/80"
              >
                + 필드 추가
              </button>
            </div>
            <div className="space-y-3">
              {embed.fields.map((field, i) => (
                <div key={i} className="p-3 bg-discord-darkest rounded-lg space-y-2">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={field.name}
                      onChange={(e) => updateField(i, { name: e.target.value })}
                      placeholder="필드 이름"
                      className="flex-1 p-2 bg-discord-darker border border-discord-light/20 rounded text-discord-text text-sm focus:border-debi-primary focus:outline-none"
                    />
                    <button
                      onClick={() => removeField(i)}
                      className="p-2 text-discord-red hover:bg-discord-red/20 rounded"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <input
                    type="text"
                    value={field.value}
                    onChange={(e) => updateField(i, { value: e.target.value })}
                    placeholder="필드 값"
                    className="w-full p-2 bg-discord-darker border border-discord-light/20 rounded text-discord-text text-sm focus:border-debi-primary focus:outline-none"
                  />
                  <label className="flex items-center gap-2 text-sm text-discord-muted">
                    <input
                      type="checkbox"
                      checked={field.inline}
                      onChange={(e) => updateField(i, { inline: e.target.checked })}
                      className="rounded"
                    />
                    인라인
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Send Button */}
          <button
            onClick={sendEmbed}
            disabled={sending || !selectedChannel}
            className="w-full py-3 btn-gradient text-white font-medium rounded-lg disabled:opacity-50"
          >
            {sending ? '전송 중...' : '임베드 전송'}
          </button>

          {message && (
            <p className={`text-sm text-center ${message.includes('실패') ? 'text-discord-red' : 'text-green-400'}`}>
              {message}
            </p>
          )}
        </div>

        {/* Preview */}
        <div className="p-4 bg-discord-darker rounded-lg">
          <h3 className="text-sm font-medium text-discord-muted mb-3">미리보기</h3>
          <div
            className="rounded-lg overflow-hidden"
            style={{ borderLeft: `4px solid ${embed.color}` }}
          >
            <div className="p-4 bg-discord-darkest">
              {embed.author.name && (
                <div className="flex items-center gap-2 mb-2">
                  {embed.author.iconUrl && (
                    <img src={embed.author.iconUrl} alt="" className="w-6 h-6 rounded-full" />
                  )}
                  <span className="text-sm text-discord-text">{embed.author.name}</span>
                </div>
              )}

              {embed.title && (
                <h4 className="font-semibold text-discord-text mb-2">{embed.title}</h4>
              )}

              {embed.description && (
                <p className="text-sm text-discord-muted whitespace-pre-wrap mb-3">{embed.description}</p>
              )}

              {embed.fields.length > 0 && (
                <div className="grid grid-cols-3 gap-2 mb-3">
                  {embed.fields.map((field, i) => (
                    <div key={i} className={field.inline ? '' : 'col-span-3'}>
                      <p className="text-xs font-semibold text-discord-text">{field.name || 'Field'}</p>
                      <p className="text-xs text-discord-muted">{field.value || '-'}</p>
                    </div>
                  ))}
                </div>
              )}

              {embed.image && (
                <img src={embed.image} alt="" className="w-full rounded mb-3" />
              )}

              {embed.thumbnail && (
                <img src={embed.thumbnail} alt="" className="absolute top-4 right-4 w-20 h-20 rounded" />
              )}

              {embed.footer && (
                <p className="text-xs text-discord-muted">{embed.footer}</p>
              )}

              {!embed.title && !embed.description && embed.fields.length === 0 && (
                <p className="text-discord-muted text-sm">임베드 내용을 입력하세요...</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
