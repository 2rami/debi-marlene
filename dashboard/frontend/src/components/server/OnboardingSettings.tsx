import { useState, useEffect } from 'react'
import { api } from '../../services/api'

interface OnboardingOption {
  id?: string
  title: string
  description?: string
  channel_ids: string[]
  role_ids: string[]
}

interface OnboardingPrompt {
  id?: string
  type: number  // 0=MULTIPLE_CHOICE, 1=DROPDOWN
  title: string
  single_select: boolean
  required: boolean
  in_onboarding: boolean
  options: OnboardingOption[]
}

interface Channel {
  id: string
  name: string
  type: number
  parentId: string | null
}

interface Role {
  id: string
  name: string
  color: number
  position: number
}

interface Props {
  guildId: string
}

export default function OnboardingSettings({ guildId }: Props) {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [isCommunity, setIsCommunity] = useState(false)
  const [enabled, setEnabled] = useState(false)
  const [mode, setMode] = useState(0)
  const [prompts, setPrompts] = useState<OnboardingPrompt[]>([])
  const [defaultChannelIds, setDefaultChannelIds] = useState<string[]>([])
  const [channels, setChannels] = useState<Channel[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [editingPrompt, setEditingPrompt] = useState<OnboardingPrompt | null>(null)
  const [showAddPrompt, setShowAddPrompt] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 커뮤니티 서버 여부 확인
        const communityRes = await api.get<{ isCommunity: boolean }>(`/servers/${guildId}/community-check`)
        setIsCommunity(communityRes.data.isCommunity)

        if (communityRes.data.isCommunity) {
          // 온보딩 설정 가져오기
          const onboardingRes = await api.get<{
            enabled: boolean
            mode: number
            prompts: OnboardingPrompt[]
            defaultChannelIds: string[]
          }>(`/servers/${guildId}/onboarding`)

          setEnabled(onboardingRes.data.enabled)
          setMode(onboardingRes.data.mode)
          setPrompts(onboardingRes.data.prompts)
          setDefaultChannelIds(onboardingRes.data.defaultChannelIds)
        }

        // 채널과 역할 가져오기
        const [channelsRes, rolesRes] = await Promise.all([
          api.get<{ channels: Channel[] }>(`/servers/${guildId}/channels`),
          api.get<{ roles: Role[] }>(`/servers/${guildId}/roles`),
        ])
        setChannels(channelsRes.data.channels.filter(c => c.type === 0))
        setRoles(rolesRes.data.roles.filter(r => r.name !== '@everyone'))
      } catch (error) {
        console.error('Failed to fetch onboarding data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [guildId])

  const saveOnboarding = async () => {
    setSaving(true)
    try {
      await api.put(`/servers/${guildId}/onboarding`, {
        enabled,
        mode,
        prompts,
        defaultChannelIds,
      })
    } catch (error) {
      console.error('Failed to save onboarding:', error)
      alert('저장 실패')
    } finally {
      setSaving(false)
    }
  }

  const addPrompt = async () => {
    if (!editingPrompt) return

    setSaving(true)
    try {
      await api.post(`/servers/${guildId}/onboarding/prompts`, {
        type: editingPrompt.type,
        title: editingPrompt.title,
        singleSelect: editingPrompt.single_select,
        required: editingPrompt.required,
        options: editingPrompt.options,
      })

      // 새로고침
      const res = await api.get<{
        enabled: boolean
        mode: number
        prompts: OnboardingPrompt[]
        defaultChannelIds: string[]
      }>(`/servers/${guildId}/onboarding`)
      setPrompts(res.data.prompts)
      setShowAddPrompt(false)
      setEditingPrompt(null)
    } catch (error) {
      console.error('Failed to add prompt:', error)
      alert('프롬프트 추가 실패')
    } finally {
      setSaving(false)
    }
  }

  const deletePrompt = async (promptId: string) => {
    if (!confirm('이 질문을 삭제하시겠습니까?')) return

    setSaving(true)
    try {
      await api.delete(`/servers/${guildId}/onboarding/prompts/${promptId}`)

      // 새로고침
      const res = await api.get<{
        enabled: boolean
        mode: number
        prompts: OnboardingPrompt[]
        defaultChannelIds: string[]
      }>(`/servers/${guildId}/onboarding`)
      setPrompts(res.data.prompts)
    } catch (error) {
      console.error('Failed to delete prompt:', error)
      alert('프롬프트 삭제 실패')
    } finally {
      setSaving(false)
    }
  }

  const getRoleColor = (color: number) => {
    if (color === 0) return '#99aab5'
    return `#${color.toString(16).padStart(6, '0')}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-discord-muted">로딩 중...</div>
      </div>
    )
  }

  // 커뮤니티 서버가 아닌 경우
  if (!isCommunity) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-white mb-2">온보딩 설정</h2>
          <p className="text-discord-muted text-sm">새 멤버가 서버에 가입할 때 표시되는 슬라이드쇼 설정</p>
        </div>

        <div className="p-6 bg-discord-dark rounded-lg text-center">
          <svg className="w-16 h-16 mx-auto text-discord-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 className="text-white font-medium text-lg mb-2">커뮤니티 서버가 아닙니다</h3>
          <p className="text-discord-muted mb-4">
            온보딩 기능을 사용하려면 서버 설정에서 커뮤니티 기능을 먼저 활성화해야 합니다.
          </p>
          <a
            href={`https://discord.com/channels/${guildId}/customize-community`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-debi-primary hover:bg-debi-primary/80 text-white rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Discord에서 커뮤니티 활성화
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white mb-2">온보딩 설정</h2>
          <p className="text-discord-muted text-sm">새 멤버가 서버에 가입할 때 표시되는 슬라이드쇼 설정</p>
        </div>
        <button
          onClick={saveOnboarding}
          disabled={saving}
          className="px-4 py-2 bg-debi-primary hover:bg-debi-primary/80 disabled:opacity-50 text-white rounded-lg transition-colors"
        >
          {saving ? '저장 중...' : '저장'}
        </button>
      </div>

      {/* 활성화 토글 */}
      <div className="p-4 bg-discord-dark rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-medium">온보딩 활성화</h3>
            <p className="text-discord-muted text-sm">새 멤버에게 온보딩 화면 표시</p>
          </div>
          <button
            onClick={() => setEnabled(!enabled)}
            className={`relative w-12 h-6 rounded-full transition-colors ${
              enabled ? 'bg-green-500' : 'bg-discord-light'
            }`}
          >
            <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
              enabled ? 'left-7' : 'left-1'
            }`} />
          </button>
        </div>
      </div>

      {/* 모드 선택 */}
      <div className="p-4 bg-discord-dark rounded-lg">
        <h3 className="text-white font-medium mb-3">온보딩 모드</h3>
        <div className="flex gap-3">
          <button
            onClick={() => setMode(0)}
            className={`flex-1 p-3 rounded-lg border-2 transition-colors ${
              mode === 0
                ? 'border-debi-primary bg-debi-primary/10'
                : 'border-discord-light hover:border-discord-muted'
            }`}
          >
            <p className="text-white font-medium">기본</p>
            <p className="text-discord-muted text-xs">필수 질문만 표시</p>
          </button>
          <button
            onClick={() => setMode(1)}
            className={`flex-1 p-3 rounded-lg border-2 transition-colors ${
              mode === 1
                ? 'border-debi-primary bg-debi-primary/10'
                : 'border-discord-light hover:border-discord-muted'
            }`}
          >
            <p className="text-white font-medium">고급</p>
            <p className="text-discord-muted text-xs">모든 질문 표시</p>
          </button>
        </div>
      </div>

      {/* 기본 채널 */}
      <div className="p-4 bg-discord-dark rounded-lg">
        <h3 className="text-white font-medium mb-3">기본 채널</h3>
        <p className="text-discord-muted text-sm mb-3">온보딩 완료 후 기본으로 표시될 채널</p>
        <div className="flex flex-wrap gap-2">
          {channels.map(channel => (
            <button
              key={channel.id}
              onClick={() => {
                if (defaultChannelIds.includes(channel.id)) {
                  setDefaultChannelIds(defaultChannelIds.filter(id => id !== channel.id))
                } else {
                  setDefaultChannelIds([...defaultChannelIds, channel.id])
                }
              }}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                defaultChannelIds.includes(channel.id)
                  ? 'bg-debi-primary text-white'
                  : 'bg-discord-darkest text-discord-muted hover:text-white'
              }`}
            >
              #{channel.name}
            </button>
          ))}
        </div>
      </div>

      {/* 질문 목록 */}
      <div className="p-4 bg-discord-dark rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-white font-medium">질문 목록</h3>
            <p className="text-discord-muted text-sm">멤버에게 표시될 질문들</p>
          </div>
          <button
            onClick={() => {
              setEditingPrompt({
                type: 0,
                title: '',
                single_select: true,
                required: true,
                in_onboarding: true,
                options: [{ title: '', channel_ids: [], role_ids: [] }],
              })
              setShowAddPrompt(true)
            }}
            className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
          >
            + 질문 추가
          </button>
        </div>

        {prompts.length === 0 ? (
          <div className="text-center py-8 text-discord-muted">
            아직 질문이 없습니다. 질문을 추가해보세요.
          </div>
        ) : (
          <div className="space-y-3">
            {prompts.map((prompt, index) => (
              <div key={prompt.id || index} className="p-3 bg-discord-darkest rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-white font-medium">{prompt.title || '(제목 없음)'}</span>
                      {prompt.required && (
                        <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 text-xs rounded">필수</span>
                      )}
                      <span className="px-1.5 py-0.5 bg-discord-light text-discord-muted text-xs rounded">
                        {prompt.type === 0 ? '다중 선택' : '드롭다운'}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {prompt.options.map((opt, optIdx) => (
                        <span
                          key={opt.id || optIdx}
                          className="px-2 py-1 bg-discord-dark text-discord-muted text-xs rounded"
                        >
                          {opt.title || '(옵션)'}
                          {opt.role_ids.length > 0 && (
                            <span className="ml-1 text-debi-primary">
                              +{opt.role_ids.length} 역할
                            </span>
                          )}
                          {opt.channel_ids.length > 0 && (
                            <span className="ml-1 text-green-400">
                              +{opt.channel_ids.length} 채널
                            </span>
                          )}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => prompt.id && deletePrompt(prompt.id)}
                    className="p-1.5 text-discord-muted hover:text-red-400 transition-colors"
                    disabled={!prompt.id}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 질문 추가 모달 */}
      {showAddPrompt && editingPrompt && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-discord-dark rounded-lg w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4">
            <div className="p-4 border-b border-discord-light">
              <h3 className="text-white font-medium text-lg">질문 추가</h3>
            </div>

            <div className="p-4 space-y-4">
              {/* 질문 제목 */}
              <div>
                <label className="block text-discord-muted text-sm mb-1">질문</label>
                <input
                  type="text"
                  value={editingPrompt.title}
                  onChange={e => setEditingPrompt({ ...editingPrompt, title: e.target.value })}
                  placeholder="예: 어떤 게임을 좋아하시나요?"
                  className="w-full px-3 py-2 bg-discord-darkest text-white rounded border border-discord-light focus:border-debi-primary outline-none"
                />
              </div>

              {/* 타입 & 옵션 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-discord-muted text-sm mb-1">표시 방식</label>
                  <select
                    value={editingPrompt.type}
                    onChange={e => setEditingPrompt({ ...editingPrompt, type: Number(e.target.value) })}
                    className="w-full px-3 py-2 bg-discord-darkest text-white rounded border border-discord-light focus:border-debi-primary outline-none"
                  >
                    <option value={0}>다중 선택 (버튼)</option>
                    <option value={1}>드롭다운</option>
                  </select>
                </div>
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={editingPrompt.required}
                      onChange={e => setEditingPrompt({ ...editingPrompt, required: e.target.checked })}
                      className="w-4 h-4 rounded border-discord-light"
                    />
                    <span className="text-discord-muted text-sm">필수</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={editingPrompt.single_select}
                      onChange={e => setEditingPrompt({ ...editingPrompt, single_select: e.target.checked })}
                      className="w-4 h-4 rounded border-discord-light"
                    />
                    <span className="text-discord-muted text-sm">단일 선택</span>
                  </label>
                </div>
              </div>

              {/* 선택지 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-discord-muted text-sm">선택지</label>
                  <button
                    onClick={() => setEditingPrompt({
                      ...editingPrompt,
                      options: [...editingPrompt.options, { title: '', channel_ids: [], role_ids: [] }]
                    })}
                    className="text-debi-primary text-sm hover:underline"
                  >
                    + 선택지 추가
                  </button>
                </div>
                <div className="space-y-3">
                  {editingPrompt.options.map((option, idx) => (
                    <div key={idx} className="p-3 bg-discord-darkest rounded-lg space-y-2">
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={option.title}
                          onChange={e => {
                            const newOptions = [...editingPrompt.options]
                            newOptions[idx] = { ...option, title: e.target.value }
                            setEditingPrompt({ ...editingPrompt, options: newOptions })
                          }}
                          placeholder="선택지 제목"
                          className="flex-1 px-3 py-2 bg-discord-dark text-white rounded border border-discord-light focus:border-debi-primary outline-none text-sm"
                        />
                        {editingPrompt.options.length > 1 && (
                          <button
                            onClick={() => {
                              const newOptions = editingPrompt.options.filter((_, i) => i !== idx)
                              setEditingPrompt({ ...editingPrompt, options: newOptions })
                            }}
                            className="p-2 text-discord-muted hover:text-red-400"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        )}
                      </div>

                      {/* 역할 연결 */}
                      <div>
                        <p className="text-xs text-discord-muted mb-1">연결할 역할</p>
                        <div className="flex flex-wrap gap-1">
                          {roles.slice(0, 10).map(role => (
                            <button
                              key={role.id}
                              onClick={() => {
                                const newOptions = [...editingPrompt.options]
                                const roleIds = option.role_ids.includes(role.id)
                                  ? option.role_ids.filter(id => id !== role.id)
                                  : [...option.role_ids, role.id]
                                newOptions[idx] = { ...option, role_ids: roleIds }
                                setEditingPrompt({ ...editingPrompt, options: newOptions })
                              }}
                              style={{
                                borderColor: option.role_ids.includes(role.id) ? getRoleColor(role.color) : undefined,
                                backgroundColor: option.role_ids.includes(role.id) ? `${getRoleColor(role.color)}20` : undefined,
                              }}
                              className={`px-2 py-0.5 rounded text-xs border transition-colors ${
                                option.role_ids.includes(role.id)
                                  ? 'border-2'
                                  : 'border-discord-light hover:border-discord-muted'
                              }`}
                            >
                              <span style={{ color: getRoleColor(role.color) }}>{role.name}</span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* 채널 연결 */}
                      <div>
                        <p className="text-xs text-discord-muted mb-1">연결할 채널</p>
                        <div className="flex flex-wrap gap-1">
                          {channels.slice(0, 10).map(channel => (
                            <button
                              key={channel.id}
                              onClick={() => {
                                const newOptions = [...editingPrompt.options]
                                const channelIds = option.channel_ids.includes(channel.id)
                                  ? option.channel_ids.filter(id => id !== channel.id)
                                  : [...option.channel_ids, channel.id]
                                newOptions[idx] = { ...option, channel_ids: channelIds }
                                setEditingPrompt({ ...editingPrompt, options: newOptions })
                              }}
                              className={`px-2 py-0.5 rounded text-xs border transition-colors ${
                                option.channel_ids.includes(channel.id)
                                  ? 'border-green-500 bg-green-500/20 text-green-400'
                                  : 'border-discord-light text-discord-muted hover:border-discord-muted'
                              }`}
                            >
                              #{channel.name}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-discord-light flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowAddPrompt(false)
                  setEditingPrompt(null)
                }}
                className="px-4 py-2 text-discord-muted hover:text-white transition-colors"
              >
                취소
              </button>
              <button
                onClick={addPrompt}
                disabled={!editingPrompt.title || editingPrompt.options.every(o => !o.title) || saving}
                className="px-4 py-2 bg-debi-primary hover:bg-debi-primary/80 disabled:opacity-50 text-white rounded transition-colors"
              >
                {saving ? '추가 중...' : '추가'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
