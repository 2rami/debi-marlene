import { useState, useEffect } from 'react'
import { api } from '../../services/api'

interface TTSFeatures {
  tts: {
    enabled: boolean
    channelId: string | null
    character: string
    userVoices?: Record<string, string>
  }
}

interface Channel {
  id: string
  name: string
  type: number
  parentId: string | null
  position: number
}

interface Member {
  id: string
  username: string
  displayName: string
  avatar: string | null
  voice: string | null
}

interface Props {
  features: TTSFeatures
  channels: Channel[]
  saving: boolean
  guildId: string
  onSave: (features: Partial<TTSFeatures>) => void
}

const VOICES = [
  { id: 'debi', name: '데비', description: '밝고 활발한 목소리', borderActive: 'border-debi-primary', bgActive: 'bg-debi-primary/10' },
  { id: 'marlene', name: '마를렌', description: '차분하고 부드러운 목소리', borderActive: 'border-marlene-primary', bgActive: 'bg-marlene-primary/10' },
  { id: 'alex', name: '알렉스', description: '낮고 편안한 목소리', borderActive: 'border-blue-500', bgActive: 'bg-blue-500/10' },
]

export default function TTSSettings({ features, channels, saving, guildId, onSave }: Props) {
  const [members, setMembers] = useState<Member[]>([])
  const [, setServerDefault] = useState('debi')
  const [loadingMembers, setLoadingMembers] = useState(false)
  const [search, setSearch] = useState('')
  const [updatingMember, setUpdatingMember] = useState<string | null>(null)

  const textChannels = channels.filter(c => c.type === 0)
  const tts = features.tts

  useEffect(() => {
    fetchMembers()
  }, [guildId])

  const fetchMembers = async () => {
    setLoadingMembers(true)
    try {
      const res = await api.get<{ members: Member[]; serverDefault: string }>(`/servers/${guildId}/members`)
      setMembers(res.data.members)
      setServerDefault(res.data.serverDefault)
    } catch (e) {
      console.error('Failed to fetch members:', e)
    } finally {
      setLoadingMembers(false)
    }
  }

  const updateMemberVoice = async (userId: string, voice: string | null) => {
    setUpdatingMember(userId)
    try {
      await api.patch(`/servers/${guildId}/members/${userId}/voice`, { voice })
      setMembers(prev => prev.map(m => m.id === userId ? { ...m, voice } : m))
    } catch (e) {
      console.error('Failed to update member voice:', e)
    } finally {
      setUpdatingMember(null)
    }
  }

  const filteredMembers = members.filter(m =>
    m.displayName.toLowerCase().includes(search.toLowerCase()) ||
    m.username.toLowerCase().includes(search.toLowerCase())
  )

  const voiceLabel = (v: string | null) => {
    if (!v) return '서버 기본값'
    return VOICES.find(voice => voice.id === v)?.name || v
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">TTS 설정</h2>
        <p className="text-discord-muted text-sm">음성 채널에서 텍스트를 읽어주는 기능을 설정합니다.</p>
      </div>

      <div className="space-y-4">
        {/* TTS 활성화 토글 */}
        <div className="flex items-center justify-between p-4 bg-discord-dark rounded-lg">
          <div>
            <p className="font-medium text-white">TTS 기능</p>
            <p className="text-sm text-discord-muted">텍스트 음성 변환 활성화</p>
          </div>
          <button
            onClick={() => onSave({ tts: { ...tts, enabled: !tts.enabled } })}
            className={`w-12 h-6 rounded-full transition-colors ${tts.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
          >
            <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${tts.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
          </button>
        </div>

        {/* TTS 채널 선택 */}
        <div className="p-4 bg-discord-dark rounded-lg">
          <label className="block font-medium text-white mb-2">TTS 채널</label>
          <p className="text-xs text-discord-muted mb-2">선택한 채널의 메시지만 읽어줍니다. 비어있으면 모든 채널을 읽습니다.</p>
          <select
            value={tts.channelId || ''}
            onChange={(e) => onSave({ tts: { ...tts, channelId: e.target.value || null } })}
            disabled={saving}
            className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-white focus:border-debi-primary focus:outline-none"
          >
            <option value="">모든 채널</option>
            {textChannels.map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
          </select>
        </div>

        {/* 서버 기본 목소리 */}
        <div className="p-4 bg-discord-dark rounded-lg">
          <label className="block font-medium text-white mb-3">서버 기본 목소리</label>
          <p className="text-xs text-discord-muted mb-3">개인 설정이 없는 멤버에게 적용되는 기본 목소리입니다.</p>
          <div className="grid grid-cols-3 gap-3">
            {VOICES.map(v => (
              <button
                key={v.id}
                onClick={() => onSave({ tts: { ...tts, character: v.id } })}
                className={`p-4 rounded-lg border-2 transition-all ${tts.character === v.id ? `${v.borderActive} ${v.bgActive}` : 'border-discord-light/20 hover:border-discord-light/40'}`}
              >
                <p className="font-semibold text-white">{v.name}</p>
                <p className="text-xs text-discord-muted mt-1">{v.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* 멤버별 목소리 설정 */}
        <div className="p-4 bg-discord-dark rounded-lg">
          <label className="block font-medium text-white mb-1">멤버별 목소리</label>
          <p className="text-xs text-discord-muted mb-3">각 멤버의 TTS 목소리를 개별적으로 설정할 수 있습니다.</p>

          {/* 검색 */}
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="멤버 검색..."
            className="w-full p-2.5 mb-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-white text-sm placeholder-discord-muted focus:border-debi-primary focus:outline-none"
          />

          {loadingMembers ? (
            <div className="text-center py-8 text-discord-muted text-sm">멤버 목록을 불러오는 중...</div>
          ) : filteredMembers.length === 0 ? (
            <div className="text-center py-8 text-discord-muted text-sm">
              {search ? '검색 결과가 없습니다.' : '멤버가 없습니다.'}
            </div>
          ) : (
            <div className="space-y-1 max-h-80 overflow-y-auto">
              {filteredMembers.map(member => (
                <div key={member.id} className="flex items-center justify-between p-2.5 rounded-lg hover:bg-discord-darkest transition-colors">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <img
                      src={member.avatar
                        ? `https://cdn.discordapp.com/avatars/${member.id}/${member.avatar}.png?size=32`
                        : `https://cdn.discordapp.com/embed/avatars/${parseInt(member.id) % 5}.png`
                      }
                      alt=""
                      className="w-8 h-8 rounded-full flex-shrink-0"
                    />
                    <div className="min-w-0">
                      <p className="text-sm text-white truncate">{member.displayName}</p>
                      {member.displayName !== member.username && (
                        <p className="text-xs text-discord-muted truncate">{member.username}</p>
                      )}
                    </div>
                  </div>
                  <select
                    value={member.voice || ''}
                    onChange={(e) => updateMemberVoice(member.id, e.target.value || null)}
                    disabled={updatingMember === member.id}
                    className="ml-3 px-2.5 py-1.5 bg-discord-darkest border border-discord-light/20 rounded text-sm text-white focus:border-debi-primary focus:outline-none flex-shrink-0"
                  >
                    <option value="">서버 기본값 ({voiceLabel(tts.character)})</option>
                    {VOICES.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                  </select>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
