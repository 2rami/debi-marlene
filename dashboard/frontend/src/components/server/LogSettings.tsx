interface Channel {
  id: string
  name: string
  type: number
}

interface LogFeatures {
  logs: {
    enabled: boolean
    channelId: string | null
    events: {
      memberJoin: boolean
      memberLeave: boolean
      messageDelete: boolean
      messageEdit: boolean
      roleChange: boolean
      channelChange: boolean
      ban: boolean
      kick: boolean
      warn: boolean
    }
  }
}

interface Props {
  features: LogFeatures
  channels: Channel[]
  saving: boolean
  onSave: (features: Partial<LogFeatures>) => void
}

const LOG_EVENTS = [
  { key: 'memberJoin', label: '멤버 입장', desc: '새 멤버가 서버에 참가했을 때' },
  { key: 'memberLeave', label: '멤버 퇴장', desc: '멤버가 서버를 떠났을 때' },
  { key: 'messageDelete', label: '메시지 삭제', desc: '메시지가 삭제되었을 때' },
  { key: 'messageEdit', label: '메시지 수정', desc: '메시지가 수정되었을 때' },
  { key: 'roleChange', label: '역할 변경', desc: '멤버의 역할이 변경되었을 때' },
  { key: 'channelChange', label: '채널 변경', desc: '채널이 생성/수정/삭제되었을 때' },
  { key: 'ban', label: '밴', desc: '멤버가 밴되었을 때' },
  { key: 'kick', label: '킥', desc: '멤버가 킥되었을 때' },
  { key: 'warn', label: '경고', desc: '멤버에게 경고가 부여되었을 때' },
] as const

export default function LogSettings({ features, channels, saving, onSave }: Props) {
  const textChannels = channels.filter(c => c.type === 0)

  const updateEvent = (eventKey: string, value: boolean) => {
    onSave({
      logs: {
        ...features.logs,
        events: {
          ...features.logs.events,
          [eventKey]: value
        }
      }
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-discord-text mb-2">관리 로그</h2>
          <p className="text-discord-muted text-sm">서버에서 발생하는 이벤트를 기록합니다.</p>
        </div>
        <button
          onClick={() => onSave({
            logs: { ...features.logs, enabled: !features.logs.enabled }
          })}
          className={`w-12 h-6 rounded-full transition-colors ${features.logs.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
        >
          <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.logs.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
        </button>
      </div>

      {/* Log Channel */}
      <div className="p-4 bg-discord-darker rounded-lg">
        <label className="block text-sm font-medium text-discord-muted mb-2">로그 채널</label>
        <select
          value={features.logs.channelId || ''}
          onChange={(e) => onSave({
            logs: { ...features.logs, channelId: e.target.value || null }
          })}
          disabled={saving || !features.logs.enabled}
          className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none disabled:opacity-50"
        >
          <option value="">채널 선택...</option>
          {textChannels.map(ch => (
            <option key={ch.id} value={ch.id}>#{ch.name}</option>
          ))}
        </select>
      </div>

      {/* Event Toggles */}
      <div className="p-4 bg-discord-darker rounded-lg">
        <h3 className="text-sm font-medium text-discord-text mb-4">기록할 이벤트</h3>
        <div className="grid md:grid-cols-2 gap-3">
          {LOG_EVENTS.map(event => (
            <div
              key={event.key}
              className={`flex items-center justify-between p-3 bg-discord-darkest rounded-lg ${!features.logs.enabled ? 'opacity-50' : ''}`}
            >
              <div>
                <p className="text-sm font-medium text-discord-text">{event.label}</p>
                <p className="text-xs text-discord-muted">{event.desc}</p>
              </div>
              <button
                onClick={() => updateEvent(event.key, !features.logs.events[event.key as keyof typeof features.logs.events])}
                disabled={!features.logs.enabled}
                className={`w-10 h-5 rounded-full transition-colors ${features.logs.events[event.key as keyof typeof features.logs.events] ? 'bg-debi-primary' : 'bg-discord-light'}`}
              >
                <div className={`w-4 h-4 rounded-full bg-white transform transition-transform ${features.logs.events[event.key as keyof typeof features.logs.events] ? 'translate-x-5' : 'translate-x-0.5'}`} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
