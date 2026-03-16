import { useState, useRef } from 'react'
import { api } from '../../services/api'
import defaultBg from '../../assets/images/feature-bg.jpg'

interface Channel {
  id: string
  name: string
  type: number
}

interface ImageConfig {
  avatar?: {
    shape?: 'circle' | 'rounded' | 'square'
    enabled?: boolean
  }
  welcome_title?: string
  welcome_subtitle?: string
  tags?: string[]
  background_color?: string
  background_image_url?: string
  member_count?: {
    enabled?: boolean
  }
  custom_welcome_text?: string
  custom_goodbye_text?: string
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
  welcome_image_config?: ImageConfig
  goodbye_image_config?: ImageConfig
}

interface Props {
  features: WelcomeFeatures
  channels: Channel[]
  saving: boolean
  guildId: string
  onSave: (features: Partial<WelcomeFeatures>) => void
}

const VARIABLES = [
  { name: '@user', desc: '멤버 멘션' },
  { name: '@server', desc: '서버 이름' },
  { name: '@membercount', desc: '멤버 수' },
  { name: '{break}', desc: '줄바꿈' },
]

const DEFAULT_IMAGE_CONFIG: ImageConfig = {
  avatar: { shape: 'circle', enabled: true },
  welcome_title: 'Welcome, {user}',
  welcome_subtitle: '서버에 오신 것을 환영합니다!',
  tags: ['NEW MEMBER', '#WELCOME'],
  background_color: '#1a1a2e',
  member_count: { enabled: true },
}

const SAMPLE_USER = '예시 유저'
const SAMPLE_SERVER = '예시 서버'
const SAMPLE_MEMBER_COUNT = 128
const DEFAULT_AVATAR = 'https://cdn.discordapp.com/embed/avatars/0.png'

function resolveVariables(text: string): string {
  return text
    .replace(/\{user\}/g, SAMPLE_USER)
    .replace(/\{server\}/g, SAMPLE_SERVER)
    .replace(/\{membercount\}/g, String(SAMPLE_MEMBER_COUNT))
}

function Toggle({ enabled, onChange }: { enabled: boolean; onChange: () => void }) {
  return (
    <button
      onClick={onChange}
      className={`w-12 h-6 rounded-full transition-colors ${enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
    >
      <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
    </button>
  )
}

// --- Live CSS Preview ---
function LivePreview({ config }: { config: ImageConfig }) {
  const avatarEnabled = config.avatar?.enabled !== false
  const avatarShape = config.avatar?.shape || 'circle'
  const title = resolveVariables(config.welcome_title || 'Welcome, {user}')
  const subtitle = resolveVariables(config.welcome_subtitle || '')
  const tags = config.tags || []
  const bgColor = config.background_color || '#1a1a2e'
  const bgImageUrl = config.background_image_url || defaultBg
  const memberCountEnabled = config.member_count?.enabled !== false

  const avatarRadius =
    avatarShape === 'circle' ? 'rounded-full' :
    avatarShape === 'rounded' ? 'rounded-2xl' :
    'rounded-none'

  return (
    <div
      className="relative w-full overflow-hidden rounded-lg"
      style={{ aspectRatio: '2 / 1', backgroundColor: bgColor }}
    >
      {/* Background image */}
      {bgImageUrl && (
        <div className="absolute inset-0">
          <img src={bgImageUrl} alt="" className="w-full h-full object-cover opacity-60" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
        </div>
      )}
      {/* Gradient overlay when no image */}
      {!bgImageUrl && (
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30" />
      )}

      {/* Content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-4 md:p-8">
        {/* Avatar */}
        {avatarEnabled && (
          <div className={`w-16 h-16 md:w-24 md:h-24 ${avatarRadius} border-4 border-white/80 shadow-2xl mb-3 md:mb-5 overflow-hidden bg-discord-dark`}>
            <img src={DEFAULT_AVATAR} alt="" className="w-full h-full object-cover" />
          </div>
        )}

        {/* Title */}
        {title && (
          <h2 className="text-xl md:text-4xl font-black text-white mb-2 md:mb-4 drop-shadow-[0_4px_4px_rgba(0,0,0,0.5)]">
            {title}
          </h2>
        )}

        {/* Subtitle / Greeting */}
        {subtitle && (
          <div className="inline-block bg-white/10 backdrop-blur-md border border-white/20 px-4 py-2 md:px-6 md:py-3 rounded-full">
            <p className="text-sm md:text-lg text-white/90 font-medium">
              {subtitle}
            </p>
          </div>
        )}

        {/* Member count */}
        {memberCountEnabled && (
          <p className="text-xs md:text-sm text-white/50 mt-2 md:mt-3">
            {SAMPLE_MEMBER_COUNT}번째 멤버
          </p>
        )}
      </div>

      {/* Tags at bottom */}
      {tags.length > 0 && (
        <div className="absolute bottom-3 left-3 md:bottom-6 md:left-6 flex gap-2 flex-wrap">
          {tags.map((tag, i) => (
            <span
              key={i}
              className="px-2 py-0.5 md:px-3 md:py-1 rounded-full bg-black/50 backdrop-blur text-[10px] md:text-xs font-mono text-white/70 border border-white/10"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

export default function WelcomeSettings({ features, channels, saving, guildId, onSave }: Props) {
  const [welcomeMessage, setWelcomeMessage] = useState(features.welcome.message || '')
  const [goodbyeMessage, setGoodbyeMessage] = useState(features.goodbye?.message || '')
  const [activeImageTab, setActiveImageTab] = useState<'welcome' | 'goodbye'>('welcome')
  const [imageConfig, setImageConfig] = useState<ImageConfig>(
    features.welcome_image_config || DEFAULT_IMAGE_CONFIG
  )
  const [uploading, setUploading] = useState(false)
  const [savingConfig, setSavingConfig] = useState(false)
  const [testChannel, setTestChannel] = useState('')
  const [sendingTest, setSendingTest] = useState(false)
  const [testResult, setTestResult] = useState<{ message: string; error: boolean } | null>(null)

  const handleTestSend = async () => {
    if (!testChannel) return
    setSendingTest(true)
    setTestResult(null)
    try {
      await api.post(`/servers/${guildId}/welcome-test`, {
        channelId: testChannel,
        type: activeImageTab,
        config: imageConfig,
      })
      setTestResult({ message: '테스트 메시지를 전송했습니다.', error: false })
    } catch {
      setTestResult({ message: '전송에 실패했습니다.', error: true })
    } finally {
      setSendingTest(false)
    }
  }
  const fileInputRef = useRef<HTMLInputElement>(null)

  const textChannels = channels.filter(c => c.type === 0)
  const welcomeConfigured = features.welcome.enabled && features.welcome.channelId
  const goodbyeConfigured = features.goodbye?.enabled && features.goodbye?.channelId

  // Switch config when tab changes
  const handleTabChange = (tab: 'welcome' | 'goodbye') => {
    setActiveImageTab(tab)
    const config = tab === 'welcome'
      ? features.welcome_image_config
      : features.goodbye_image_config
    setImageConfig(config || DEFAULT_IMAGE_CONFIG)
  }

  const updateConfig = (patch: Partial<ImageConfig>) => {
    setImageConfig(prev => ({ ...prev, ...patch }))
  }

  const updateAvatar = (field: string, value: unknown) => {
    setImageConfig(prev => ({
      ...prev,
      avatar: { ...(prev.avatar || {}), [field]: value },
    }))
  }

  const updateMemberCount = (field: string, value: unknown) => {
    setImageConfig(prev => ({
      ...prev,
      member_count: { ...(prev.member_count || {}), [field]: value },
    }))
  }

  // Tags
  const addTag = () => {
    const tags = [...(imageConfig.tags || []), '']
    updateConfig({ tags })
  }

  const removeTag = (index: number) => {
    const tags = [...(imageConfig.tags || [])]
    tags.splice(index, 1)
    updateConfig({ tags })
  }

  const updateTag = (index: number, value: string) => {
    const tags = [...(imageConfig.tags || [])]
    tags[index] = value
    updateConfig({ tags })
  }

  // Image upload
  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > 3 * 1024 * 1024) {
      alert('파일 크기는 3MB 이하여야 합니다.')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('type', activeImageTab)

      const response = await api.postFormData<{ url: string }>(`/servers/${guildId}/welcome-image`, formData)
      if (response.data.url) {
        updateConfig({ background_image_url: response.data.url })
      }
    } catch {
      alert('이미지 업로드에 실패했습니다.')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteImage = async () => {
    if (!confirm('배경 이미지를 삭제하시겠습니까?')) return

    try {
      await api.delete(`/servers/${guildId}/welcome-image?type=${activeImageTab}`)
      updateConfig({ background_image_url: undefined })
    } catch {
      alert('이미지 삭제에 실패했습니다.')
    }
  }

  // Save
  const saveImageConfig = async () => {
    setSavingConfig(true)
    try {
      await api.patch(`/servers/${guildId}/welcome-image-config`, {
        type: activeImageTab,
        config: imageConfig,
      })
      const configKey = activeImageTab === 'welcome' ? 'welcome_image_config' : 'goodbye_image_config'
      onSave({ [configKey]: imageConfig } as Partial<WelcomeFeatures>)
    } catch {
      alert('설정 저장에 실패했습니다.')
    } finally {
      setSavingConfig(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Status */}
      <div className="flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${welcomeConfigured ? 'bg-green-500' : 'bg-discord-muted'}`} />
          <span className="text-discord-muted">
            {welcomeConfigured ? '환영 메시지 설정됨' : '환영 메시지 미설정'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${goodbyeConfigured ? 'bg-green-500' : 'bg-discord-muted'}`} />
          <span className="text-discord-muted">
            {goodbyeConfigured ? '작별 메시지 설정됨' : '작별 메시지 미설정'}
          </span>
        </div>
      </div>

      {/* Variables Info */}
      <div className="p-3 bg-discord-darker rounded-lg border border-discord-light/10">
        <div className="flex flex-wrap gap-3">
          {VARIABLES.map(v => (
            <span key={v.name} className="text-sm">
              <code className="text-debi-primary font-mono">{v.name}</code>
              <span className="text-discord-muted ml-1">({v.desc})</span>
            </span>
          ))}
        </div>
      </div>

      {/* Two Column Layout: Welcome / Goodbye */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Welcome Message */}
        <div className="p-4 bg-discord-darker rounded-lg border border-discord-light/10">
          <h3 className="text-lg font-semibold text-discord-text mb-4">환영 메시지</h3>

          <div className="mb-4">
            <label className="block text-sm font-medium text-discord-muted mb-2">환영 채널</label>
            <select
              value={features.welcome.channelId || ''}
              onChange={(e) => onSave({ welcome: { ...features.welcome, channelId: e.target.value || null } })}
              disabled={saving}
              className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
            >
              <option value="">채널 선택...</option>
              {textChannels.map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
            </select>
          </div>

          <div className="flex items-center justify-between p-3 bg-discord-darkest rounded-lg mb-3">
            <span className="text-discord-text">텍스트 메시지</span>
            <Toggle
              enabled={features.welcome.enabled}
              onChange={() => onSave({ welcome: { ...features.welcome, enabled: !features.welcome.enabled } })}
            />
          </div>

          {features.welcome.enabled && (
            <div className="mb-3">
              <textarea
                value={welcomeMessage}
                onChange={(e) => setWelcomeMessage(e.target.value)}
                onBlur={() => onSave({ welcome: { ...features.welcome, message: welcomeMessage } })}
                placeholder="환영합니다, @user님!"
                rows={3}
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none resize-none text-sm"
              />
            </div>
          )}

          <div className="flex items-center justify-between p-3 bg-discord-darkest rounded-lg">
            <span className="text-discord-text">이미지 메시지</span>
            <Toggle
              enabled={!!features.welcome.imageEnabled}
              onChange={() => onSave({ welcome: { ...features.welcome, imageEnabled: !features.welcome.imageEnabled } })}
            />
          </div>
        </div>

        {/* Goodbye Message */}
        <div className="p-4 bg-discord-darker rounded-lg border border-discord-light/10">
          <h3 className="text-lg font-semibold text-discord-text mb-4">작별 메시지</h3>

          <div className="mb-4">
            <label className="block text-sm font-medium text-discord-muted mb-2">작별 채널</label>
            <select
              value={features.goodbye?.channelId || ''}
              onChange={(e) => onSave({ goodbye: { ...features.goodbye, channelId: e.target.value || null } })}
              disabled={saving}
              className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
            >
              <option value="">채널 선택...</option>
              {textChannels.map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
            </select>
          </div>

          <div className="flex items-center justify-between p-3 bg-discord-darkest rounded-lg mb-3">
            <span className="text-discord-text">텍스트 메시지</span>
            <Toggle
              enabled={!!features.goodbye?.enabled}
              onChange={() => onSave({ goodbye: { ...features.goodbye, enabled: !features.goodbye?.enabled } })}
            />
          </div>

          {features.goodbye?.enabled && (
            <div className="mb-3">
              <textarea
                value={goodbyeMessage}
                onChange={(e) => setGoodbyeMessage(e.target.value)}
                onBlur={() => onSave({ goodbye: { ...features.goodbye, message: goodbyeMessage } })}
                placeholder="@user님이 떠났습니다."
                rows={3}
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none resize-none text-sm"
              />
            </div>
          )}

          <div className="flex items-center justify-between p-3 bg-discord-darkest rounded-lg">
            <span className="text-discord-text">이미지 메시지</span>
            <Toggle
              enabled={!!features.goodbye?.imageEnabled}
              onChange={() => onSave({ goodbye: { ...features.goodbye, imageEnabled: !features.goodbye?.imageEnabled } })}
            />
          </div>
        </div>
      </div>

      {/* Image Editor: Controls + Live Preview */}
      {(features.welcome.imageEnabled || features.goodbye?.imageEnabled) && (
        <div className="p-4 bg-discord-darker rounded-lg border border-discord-light/10">
          {/* Header with tabs */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-discord-text">이미지 커스터마이징</h3>
            <div className="flex gap-2">
              <button
                onClick={() => handleTabChange('welcome')}
                className={`px-3 py-1 rounded text-sm ${activeImageTab === 'welcome' ? 'bg-debi-primary text-white' : 'bg-discord-darkest text-discord-muted'}`}
              >
                환영
              </button>
              <button
                onClick={() => handleTabChange('goodbye')}
                className={`px-3 py-1 rounded text-sm ${activeImageTab === 'goodbye' ? 'bg-debi-primary text-white' : 'bg-discord-darkest text-discord-muted'}`}
              >
                작별
              </button>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-4">
            {/* Left: Controls */}
            <div className="space-y-3">

              {/* 1. 프로필 사진 토글 */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-discord-text">프로필 사진</label>
                  <Toggle
                    enabled={imageConfig.avatar?.enabled !== false}
                    onChange={() => updateAvatar('enabled', !(imageConfig.avatar?.enabled !== false))}
                  />
                </div>

                {/* 2. 아바타 모양 (avatar on일 때만) */}
                {imageConfig.avatar?.enabled !== false && (
                  <div className="mt-3 pt-3 border-t border-discord-light/10">
                    <label className="text-xs text-discord-muted mb-2 block">아바타 모양</label>
                    <div className="grid grid-cols-3 gap-2">
                      {(['circle', 'rounded', 'square'] as const).map(shape => (
                        <button
                          key={shape}
                          onClick={() => updateAvatar('shape', shape)}
                          className={`px-2 py-1.5 rounded text-xs ${imageConfig.avatar?.shape === shape ? 'bg-debi-primary text-white' : 'bg-discord-dark text-discord-muted hover:bg-discord-light/20'}`}
                        >
                          {shape === 'circle' ? '원형' : shape === 'rounded' ? '둥근' : '사각'}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 3. 환영 문구 */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <label className="block text-sm font-medium text-discord-text mb-1">환영 문구</label>
                <p className="text-xs text-discord-muted mb-2">{'{user}'} = 유저명, {'{server}'} = 서버명</p>
                <input
                  type="text"
                  value={imageConfig.welcome_title || ''}
                  onChange={(e) => updateConfig({ welcome_title: e.target.value })}
                  placeholder="Welcome, {user}"
                  className="w-full p-2 bg-discord-dark border border-discord-light/20 rounded text-discord-text text-sm focus:border-debi-primary focus:outline-none"
                />
              </div>

              {/* 4. 인사말 */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <label className="block text-sm font-medium text-discord-text mb-2">인사말</label>
                <input
                  type="text"
                  value={imageConfig.welcome_subtitle || ''}
                  onChange={(e) => updateConfig({ welcome_subtitle: e.target.value })}
                  placeholder="서버에 오신 것을 환영합니다!"
                  className="w-full p-2 bg-discord-dark border border-discord-light/20 rounded text-discord-text text-sm focus:border-debi-primary focus:outline-none"
                />
              </div>

              {/* 5. 태그 */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <label className="block text-sm font-medium text-discord-text mb-2">태그</label>
                <div className="space-y-2">
                  {(imageConfig.tags || []).map((tag, i) => (
                    <div key={i} className="flex gap-2">
                      <input
                        type="text"
                        value={tag}
                        onChange={(e) => updateTag(i, e.target.value)}
                        placeholder="태그 텍스트"
                        className="flex-1 p-2 bg-discord-dark border border-discord-light/20 rounded text-discord-text text-sm focus:border-debi-primary focus:outline-none"
                      />
                      <button
                        onClick={() => removeTag(i)}
                        className="px-2 py-1 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors text-sm"
                      >
                        삭제
                      </button>
                    </div>
                  ))}
                </div>
                <button
                  onClick={addTag}
                  className="mt-2 px-3 py-1.5 bg-discord-dark text-discord-muted rounded hover:bg-discord-light/20 transition-colors text-sm w-full"
                >
                  + 태그 추가
                </button>
              </div>

              {/* 6. 배경 이미지 업로드 */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <label className="block text-sm font-medium text-discord-text mb-2">배경 이미지</label>
                <div className="flex gap-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/png,image/jpeg,image/jpg"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className="flex-1 px-3 py-2 bg-discord-dark text-discord-text rounded hover:bg-discord-light/20 transition-colors text-sm"
                  >
                    {uploading ? '업로드 중...' : '이미지 업로드'}
                  </button>
                  <button
                    onClick={handleDeleteImage}
                    className="px-3 py-2 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors text-sm"
                  >
                    삭제
                  </button>
                </div>
                <p className="text-xs text-discord-muted mt-1">PNG, JPG (최대 3MB)</p>
              </div>

              {/* 7. 배경색 */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <label className="block text-sm font-medium text-discord-text mb-2">배경색</label>
                <p className="text-xs text-discord-muted mb-2">배경 이미지가 없을 때 적용됩니다</p>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={imageConfig.background_color || '#1a1a2e'}
                    onChange={(e) => updateConfig({ background_color: e.target.value })}
                    className="w-10 h-10 rounded cursor-pointer border-0"
                  />
                  <span className="text-sm text-discord-muted font-mono">
                    {imageConfig.background_color || '#1a1a2e'}
                  </span>
                </div>
              </div>

              {/* 8. 멤버 수 표시 */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-discord-text">멤버 수 표시</label>
                  <Toggle
                    enabled={imageConfig.member_count?.enabled !== false}
                    onChange={() => updateMemberCount('enabled', !(imageConfig.member_count?.enabled !== false))}
                  />
                </div>
              </div>

              {/* 9. 저장 버튼 */}
              <button
                onClick={saveImageConfig}
                disabled={savingConfig}
                className="w-full px-3 py-2.5 bg-debi-primary text-white rounded hover:bg-debi-primary/80 transition-colors font-medium disabled:opacity-50"
              >
                {savingConfig ? '저장 중...' : '설정 저장'}
              </button>
            </div>

            {/* Right: Live CSS Preview */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-discord-text">실시간 미리보기</label>
              <div className="p-3 bg-discord-darkest rounded-lg">
                <LivePreview config={imageConfig} />
              </div>
              <p className="text-xs text-discord-muted mb-3">
                미리보기는 실제 이미지와 약간 다를 수 있습니다. 변수는 샘플 값으로 표시됩니다.
              </p>

              {/* 테스트 전송 */}
              <div className="p-3 bg-discord-darkest rounded-lg space-y-2">
                <label className="text-sm font-medium text-discord-text">테스트 전송</label>
                <div className="flex gap-2">
                  <select
                    value={testChannel}
                    onChange={(e) => setTestChannel(e.target.value)}
                    className="flex-1 p-2 bg-discord-dark border border-discord-light/20 rounded text-sm text-discord-text focus:border-debi-primary focus:outline-none"
                  >
                    <option value="">채널 선택...</option>
                    {textChannels.map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
                  </select>
                  <button
                    onClick={handleTestSend}
                    disabled={!testChannel || sendingTest}
                    className="px-4 py-2 bg-debi-primary text-white text-sm rounded hover:bg-debi-primary/80 transition-colors disabled:opacity-50"
                  >
                    {sendingTest ? '전송 중...' : '전송'}
                  </button>
                </div>
                {testResult && (
                  <p className={`text-xs ${testResult.error ? 'text-red-400' : 'text-green-400'}`}>
                    {testResult.message}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
