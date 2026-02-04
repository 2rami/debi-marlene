import { useState, useRef, useEffect, useCallback } from 'react'
import { api } from '../../services/api'

interface Channel {
  id: string
  name: string
  type: number
}

interface ImageConfig {
  background_color?: string
  background?: {
    fit?: 'cover' | 'fit' | 'stretch'
    scale?: number
    offset_x?: number
    offset_y?: number
  }
  avatar?: {
    x?: number
    y?: number
    size?: number
    shape?: 'circle' | 'square' | 'rounded'
    border_color?: string
    border_width?: number
  }
  username?: {
    x?: number
    y?: number
    font_size?: number
    color?: string
    align?: 'left' | 'center' | 'right'
    shadow?: boolean
  }
  welcome_text?: {
    x?: number
    y?: number
    font_size?: number
    color?: string
  }
  member_count?: {
    enabled?: boolean
    color?: string
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
  background_color: '#2C2F33',
  background: { fit: 'cover', scale: 100, offset_x: 0, offset_y: 0 },
  avatar: { x: 512, y: 180, size: 200, shape: 'circle', border_color: '#FFFFFF', border_width: 5 },
  username: { x: 512, y: 320, font_size: 48, color: '#FFFFFF', align: 'center', shadow: true },
  welcome_text: { x: 512, y: 390, font_size: 32, color: '#99AAB5' },
  member_count: { enabled: true, color: '#7289DA' },
}

export default function WelcomeSettings({ features, channels, saving, guildId, onSave }: Props) {
  const [welcomeMessage, setWelcomeMessage] = useState(features.welcome.message || '')
  const [goodbyeMessage, setGoodbyeMessage] = useState(features.goodbye?.message || '')
  const [activeImageTab, setActiveImageTab] = useState<'welcome' | 'goodbye'>('welcome')
  const [imageConfig, setImageConfig] = useState<ImageConfig>(
    features.welcome_image_config || DEFAULT_IMAGE_CONFIG
  )
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [loadingPreview, setLoadingPreview] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const textChannels = channels.filter(c => c.type === 0)
  const welcomeConfigured = features.welcome.enabled && features.welcome.channelId
  const goodbyeConfigured = features.goodbye?.enabled && features.goodbye?.channelId

  // 실시간 미리보기: 설정 변경 시 자동 업데이트 (debounce 500ms)
  const generatePreviewDebounced = useCallback(async () => {
    setLoadingPreview(true)
    try {
      const response = await api.post<{ image: string }>(`/servers/${guildId}/welcome-preview`, {
        type: activeImageTab,
        config: imageConfig,
      })
      setPreviewImage(response.data.image)
    } catch (error) {
      console.error('Preview failed:', error)
    } finally {
      setLoadingPreview(false)
    }
  }, [guildId, activeImageTab, imageConfig])

  useEffect(() => {
    if (!features.welcome.imageEnabled && !features.goodbye?.imageEnabled) return

    const timer = setTimeout(() => {
      generatePreviewDebounced()
    }, 500)

    return () => clearTimeout(timer)
  }, [imageConfig, activeImageTab, generatePreviewDebounced, features.welcome.imageEnabled, features.goodbye?.imageEnabled])

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

      await api.postFormData(`/servers/${guildId}/welcome-image`, formData)

      await generatePreview()
    } catch (error) {
      console.error('Upload failed:', error)
      alert('이미지 업로드에 실패했습니다.')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteImage = async () => {
    if (!confirm('배경 이미지를 삭제하시겠습니까?')) return

    try {
      await api.delete(`/servers/${guildId}/welcome-image?type=${activeImageTab}`)
      await generatePreview()
    } catch (error) {
      console.error('Delete failed:', error)
    }
  }

  const generatePreview = async () => {
    setLoadingPreview(true)
    try {
      const response = await api.post<{ image: string }>(`/servers/${guildId}/welcome-preview`, {
        type: activeImageTab,
        config: imageConfig,
      })
      setPreviewImage(response.data.image)
    } catch (error) {
      console.error('Preview failed:', error)
    } finally {
      setLoadingPreview(false)
    }
  }

  const saveImageConfig = async () => {
    try {
      await api.patch(`/servers/${guildId}/welcome-image-config`, {
        type: activeImageTab,
        config: imageConfig,
      })

      const configKey = activeImageTab === 'welcome' ? 'welcome_image_config' : 'goodbye_image_config'
      onSave({ [configKey]: imageConfig } as Partial<WelcomeFeatures>)
    } catch (error) {
      console.error('Save config failed:', error)
    }
  }

  const updateConfig = <K extends keyof ImageConfig>(
    key: K,
    value: ImageConfig[K]
  ) => {
    setImageConfig(prev => ({ ...prev, [key]: value }))
  }

  const updateNestedConfig = <K extends keyof ImageConfig>(
    key: K,
    field: string,
    value: unknown
  ) => {
    setImageConfig(prev => ({
      ...prev,
      [key]: { ...(prev[key] as object), [field]: value }
    }))
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

      {/* Two Column Layout */}
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
            <button
              onClick={() => onSave({ welcome: { ...features.welcome, enabled: !features.welcome.enabled } })}
              className={`w-12 h-6 rounded-full transition-colors ${features.welcome.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.welcome.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
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
            <button
              onClick={() => onSave({ welcome: { ...features.welcome, imageEnabled: !features.welcome.imageEnabled } })}
              className={`w-12 h-6 rounded-full transition-colors ${features.welcome.imageEnabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.welcome.imageEnabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
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
            <button
              onClick={() => onSave({ goodbye: { ...features.goodbye, enabled: !features.goodbye?.enabled } })}
              className={`w-12 h-6 rounded-full transition-colors ${features.goodbye?.enabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.goodbye?.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
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
            <button
              onClick={() => onSave({ goodbye: { ...features.goodbye, imageEnabled: !features.goodbye?.imageEnabled } })}
              className={`w-12 h-6 rounded-full transition-colors ${features.goodbye?.imageEnabled ? 'bg-debi-primary' : 'bg-discord-light'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${features.goodbye?.imageEnabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Image Editor */}
      {(features.welcome.imageEnabled || features.goodbye?.imageEnabled) && (
        <div className="p-4 bg-discord-darker rounded-lg border border-discord-light/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-discord-text">이미지 커스터마이징</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setActiveImageTab('welcome')}
                className={`px-3 py-1 rounded text-sm ${activeImageTab === 'welcome' ? 'bg-debi-primary text-white' : 'bg-discord-darkest text-discord-muted'}`}
              >
                환영
              </button>
              <button
                onClick={() => setActiveImageTab('goodbye')}
                className={`px-3 py-1 rounded text-sm ${activeImageTab === 'goodbye' ? 'bg-debi-primary text-white' : 'bg-discord-darkest text-discord-muted'}`}
              >
                작별
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {/* Settings Panel */}
            <div className="space-y-4">
              {/* Background Upload */}
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

                {/* 배경 이미지 설정 */}
                <div className="mt-3 pt-3 border-t border-discord-light/10">
                  <label className="text-xs text-discord-muted mb-2 block">맞춤 방식</label>
                  <div className="grid grid-cols-3 gap-2 mb-2">
                    {(['cover', 'fit', 'stretch'] as const).map(fit => (
                      <button
                        key={fit}
                        onClick={() => updateNestedConfig('background', 'fit', fit)}
                        className={`px-2 py-1 rounded text-xs ${imageConfig.background?.fit === fit ? 'bg-debi-primary text-white' : 'bg-discord-dark text-discord-muted'}`}
                      >
                        {fit === 'cover' ? '채우기' : fit === 'fit' ? '맞추기' : '늘리기'}
                      </button>
                    ))}
                  </div>
                  <div className="space-y-2">
                    <div>
                      <label className="text-xs text-discord-muted">크기 ({imageConfig.background?.scale || 100}%)</label>
                      <input
                        type="range"
                        min="50"
                        max="200"
                        value={imageConfig.background?.scale || 100}
                        onChange={(e) => updateNestedConfig('background', 'scale', parseInt(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-xs text-discord-muted">X 위치</label>
                        <input
                          type="range"
                          min="-200"
                          max="200"
                          value={imageConfig.background?.offset_x || 0}
                          onChange={(e) => updateNestedConfig('background', 'offset_x', parseInt(e.target.value))}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-discord-muted">Y 위치</label>
                        <input
                          type="range"
                          min="-200"
                          max="200"
                          value={imageConfig.background?.offset_y || 0}
                          onChange={(e) => updateNestedConfig('background', 'offset_y', parseInt(e.target.value))}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Avatar Settings */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <label className="block text-sm font-medium text-discord-text mb-2">아바타</label>
                <div className="grid grid-cols-3 gap-2 mb-2">
                  {(['circle', 'rounded', 'square'] as const).map(shape => (
                    <button
                      key={shape}
                      onClick={() => updateNestedConfig('avatar', 'shape', shape)}
                      className={`px-2 py-1 rounded text-xs ${imageConfig.avatar?.shape === shape ? 'bg-debi-primary text-white' : 'bg-discord-dark text-discord-muted'}`}
                    >
                      {shape === 'circle' ? '원형' : shape === 'rounded' ? '둥근' : '사각'}
                    </button>
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-discord-muted">크기</label>
                    <input
                      type="number"
                      value={imageConfig.avatar?.size || 200}
                      onChange={(e) => updateNestedConfig('avatar', 'size', parseInt(e.target.value))}
                      className="w-full p-1 bg-discord-dark border border-discord-light/20 rounded text-discord-text text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-discord-muted">테두리</label>
                    <input
                      type="color"
                      value={imageConfig.avatar?.border_color || '#FFFFFF'}
                      onChange={(e) => updateNestedConfig('avatar', 'border_color', e.target.value)}
                      className="w-full h-7 rounded cursor-pointer"
                    />
                  </div>
                </div>
              </div>

              {/* Text Settings */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <label className="block text-sm font-medium text-discord-text mb-2">텍스트 색상</label>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs text-discord-muted">유저명</label>
                    <input
                      type="color"
                      value={imageConfig.username?.color || '#FFFFFF'}
                      onChange={(e) => updateNestedConfig('username', 'color', e.target.value)}
                      className="w-full h-7 rounded cursor-pointer"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-discord-muted">환영 텍스트</label>
                    <input
                      type="color"
                      value={imageConfig.welcome_text?.color || '#99AAB5'}
                      onChange={(e) => updateNestedConfig('welcome_text', 'color', e.target.value)}
                      className="w-full h-7 rounded cursor-pointer"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-discord-muted">멤버 수</label>
                    <input
                      type="color"
                      value={imageConfig.member_count?.color || '#7289DA'}
                      onChange={(e) => updateNestedConfig('member_count', 'color', e.target.value)}
                      className="w-full h-7 rounded cursor-pointer"
                    />
                  </div>
                </div>
              </div>

              {/* Custom Text */}
              <div className="p-3 bg-discord-darkest rounded-lg">
                <label className="block text-sm font-medium text-discord-text mb-2">커스텀 텍스트</label>
                <input
                  type="text"
                  value={activeImageTab === 'welcome'
                    ? (imageConfig.custom_welcome_text || '')
                    : (imageConfig.custom_goodbye_text || '')}
                  onChange={(e) => updateConfig(
                    activeImageTab === 'welcome' ? 'custom_welcome_text' : 'custom_goodbye_text',
                    e.target.value
                  )}
                  placeholder={activeImageTab === 'welcome' ? '서버에 오신 것을 환영합니다!' : '안녕히 가세요!'}
                  className="w-full p-2 bg-discord-dark border border-discord-light/20 rounded text-discord-text text-sm"
                />
              </div>

              {/* Action Button */}
              <button
                onClick={saveImageConfig}
                className="w-full px-3 py-2 bg-debi-primary text-white rounded hover:bg-debi-primary/80 transition-colors"
              >
                설정 저장
              </button>
            </div>

            {/* Preview Panel */}
            <div className="p-3 bg-discord-darkest rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-discord-text">실시간 미리보기</label>
                {loadingPreview && <span className="text-xs text-discord-muted">업데이트 중...</span>}
              </div>
              <div className="aspect-[2/1] bg-discord-dark rounded-lg overflow-hidden flex items-center justify-center">
                {previewImage ? (
                  <img src={previewImage} alt="Preview" className="w-full h-full object-contain" />
                ) : loadingPreview ? (
                  <div className="text-discord-muted">생성 중...</div>
                ) : (
                  <div className="text-discord-muted text-center p-4">
                    <p>미리보기 버튼을 눌러</p>
                    <p>이미지를 확인하세요</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
