import { useState } from 'react'

interface Channel {
  id: string
  name: string
  type: number
}

interface WelcomeFeatures {
  welcome: {
    enabled: boolean
    channelId: string | null
    message: string
    imageEnabled?: boolean
  }
  goodbye: {
    enabled: boolean
    channelId: string | null
    message: string
    imageEnabled?: boolean
  }
}

interface Props {
  features: WelcomeFeatures
  channels: Channel[]
  saving: boolean
  onSave: (features: Partial<WelcomeFeatures>) => void
}

const VARIABLES = [
  { name: '@user', desc: '방금 참여한 멤버를 멘션합니다' },
  { name: '@server', desc: '서버 이름을 표시합니다' },
  { name: '@membercount', desc: '서버의 멤버 수를 표시합니다' },
  { name: '#channelname', desc: '텍스트 채널을 표시합니다 (예: #rules)' },
  { name: '{break}', desc: '새 줄을 삽입합니다 (Enter 키와 동일)' },
]

export default function WelcomeSettings({ features, channels, saving, onSave }: Props) {
  const [welcomeMessage, setWelcomeMessage] = useState(features.welcome.message || '')
  const [goodbyeMessage, setGoodbyeMessage] = useState(features.goodbye?.message || '')

  const textChannels = channels.filter(c => c.type === 0)

  const welcomeConfigured = features.welcome.enabled && features.welcome.channelId
  const goodbyeConfigured = features.goodbye?.enabled && features.goodbye?.channelId

  return (
    <div className="space-y-6">
      {/* Status */}
      <div className="flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${welcomeConfigured ? 'bg-green-500' : 'bg-discord-muted'}`} />
          <span className="text-discord-muted">
            {welcomeConfigured ? '환영 메시지가 설정됨' : '환영 메시지가 설정되지 않음'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${goodbyeConfigured ? 'bg-green-500' : 'bg-discord-muted'}`} />
          <span className="text-discord-muted">
            {goodbyeConfigured ? '작별 메시지가 설정됨' : '작별 메시지가 설정되지 않음'}
          </span>
        </div>
      </div>

      {/* Variables Info */}
      <div className="p-4 bg-discord-darker rounded-lg border border-discord-light/10">
        <h3 className="text-lg font-semibold text-discord-text mb-3">유용한 변수</h3>
        <ul className="space-y-2">
          {VARIABLES.map(v => (
            <li key={v.name} className="flex items-start gap-2 text-sm">
              <code className="text-debi-primary font-mono">{v.name}</code>
              <span className="text-discord-muted">- {v.desc}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Two Column Layout */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Welcome Message */}
        <div className="p-4 bg-discord-darker rounded-lg border border-discord-light/10">
          <h3 className="text-lg font-semibold text-discord-text mb-4">환영 메시지</h3>

          {/* Channel Select */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-discord-muted mb-2">환영 채널</label>
            <select
              value={features.welcome.channelId || ''}
              onChange={(e) => onSave({
                welcome: { ...features.welcome, channelId: e.target.value || null }
              })}
              disabled={saving}
              className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
            >
              <option value="">채널을 선택하세요</option>
              {textChannels.map(ch => (
                <option key={ch.id} value={ch.id}>#{ch.name}</option>
              ))}
            </select>
          </div>

          {/* Welcome Message Toggle */}
          <div className="flex items-center justify-between p-3 bg-discord-darkest rounded-lg mb-3">
            <span className="text-discord-text">환영 메시지</span>
            <button
              onClick={() => onSave({
                welcome: { ...features.welcome, enabled: !features.welcome.enabled }
              })}
              className={`w-12 h-6 rounded-full transition-colors ${features.welcome.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.welcome.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>

          {/* Welcome Message Input */}
          {features.welcome.enabled && (
            <div className="mb-3">
              <textarea
                value={welcomeMessage}
                onChange={(e) => setWelcomeMessage(e.target.value)}
                onBlur={() => onSave({
                  welcome: { ...features.welcome, message: welcomeMessage }
                })}
                placeholder="환영합니다, @user님! @server에 오신 것을 환영해요!"
                rows={4}
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none resize-none text-sm"
              />
            </div>
          )}

          {/* Welcome Image Toggle */}
          <div className="flex items-center justify-between p-3 bg-discord-darkest rounded-lg">
            <span className="text-discord-text">환영 이미지 메시지</span>
            <button
              onClick={() => onSave({
                welcome: { ...features.welcome, imageEnabled: !features.welcome.imageEnabled }
              })}
              className={`w-12 h-6 rounded-full transition-colors ${features.welcome.imageEnabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.welcome.imageEnabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>
        </div>

        {/* Goodbye Message */}
        <div className="p-4 bg-discord-darker rounded-lg border border-discord-light/10">
          <h3 className="text-lg font-semibold text-discord-text mb-4">작별 메시지</h3>

          {/* Channel Select */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-discord-muted mb-2">작별 채널</label>
            <select
              value={features.goodbye?.channelId || ''}
              onChange={(e) => onSave({
                goodbye: { ...features.goodbye, channelId: e.target.value || null }
              })}
              disabled={saving}
              className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
            >
              <option value="">작별 채널을 선택하세요</option>
              {textChannels.map(ch => (
                <option key={ch.id} value={ch.id}>#{ch.name}</option>
              ))}
            </select>
          </div>

          {/* Goodbye Message Toggle */}
          <div className="flex items-center justify-between p-3 bg-discord-darkest rounded-lg mb-3">
            <span className="text-discord-text">작별 메시지</span>
            <button
              onClick={() => onSave({
                goodbye: { ...features.goodbye, enabled: !features.goodbye?.enabled }
              })}
              className={`w-12 h-6 rounded-full transition-colors ${features.goodbye?.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.goodbye?.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>

          {/* Goodbye Message Input */}
          {features.goodbye?.enabled && (
            <div className="mb-3">
              <textarea
                value={goodbyeMessage}
                onChange={(e) => setGoodbyeMessage(e.target.value)}
                onBlur={() => onSave({
                  goodbye: { ...features.goodbye, message: goodbyeMessage }
                })}
                placeholder="@user님이 서버를 떠났습니다. 안녕히 가세요!"
                rows={4}
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none resize-none text-sm"
              />
            </div>
          )}

          {/* Goodbye Image Toggle */}
          <div className="flex items-center justify-between p-3 bg-discord-darkest rounded-lg">
            <span className="text-discord-text">작별 이미지 메시지</span>
            <button
              onClick={() => onSave({
                goodbye: { ...features.goodbye, imageEnabled: !features.goodbye?.imageEnabled }
              })}
              className={`w-12 h-6 rounded-full transition-colors ${features.goodbye?.imageEnabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.goodbye?.imageEnabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
