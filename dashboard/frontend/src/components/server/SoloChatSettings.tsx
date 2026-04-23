import { useEffect, useState } from 'react'
import { api } from '../../services/api'

interface Channel {
  id: string
  name: string
  type: number
  parentId: string | null
  position: number
}

interface Props {
  channels: Channel[]
  guildId: string
}

type Identity = 'debi' | 'marlene'
type SoloMap = Record<Identity, string[]>

interface SoloBotStatus {
  in_guild: boolean
  in_guild_unknown?: boolean
  invite_url: string | null
  configured: boolean
}

interface SoloBotsStatusResponse {
  debi: SoloBotStatus
  marlene: SoloBotStatus
  mainBotInGuild: boolean
}

// Discord snowflake는 19자리 (> 2^53). JS Number로 다루면 정밀도 손실되므로
// 항상 string으로 정규화. 중복도 제거.
const normalizeIds = (raw: unknown): string[] => {
  if (!Array.isArray(raw)) return []
  const asStrings = raw
    .filter(v => v !== null && v !== undefined)
    .map(v => String(v))
    .filter(v => v.length > 0)
  return Array.from(new Set(asStrings))
}

const MAX_CHANNELS = 5

const IDENTITY_META: Record<Identity, { label: string; border: string; bg: string; accent: string }> = {
  debi: {
    label: '데비',
    border: 'border-debi-primary',
    bg: 'bg-debi-primary/10',
    accent: 'text-debi-primary',
  },
  marlene: {
    label: '마를렌',
    border: 'border-marlene-primary',
    bg: 'bg-marlene-primary/10',
    accent: 'text-marlene-primary',
  },
}

export default function SoloChatSettings({ channels, guildId }: Props) {
  const [selection, setSelection] = useState<SoloMap>({ debi: [], marlene: [] })
  const [loaded, setLoaded] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [backendMissing, setBackendMissing] = useState(false)
  const [botStatus, setBotStatus] = useState<SoloBotsStatusResponse | null>(null)

  const textChannels = channels.filter(c => c.type === 0)

  useEffect(() => {
    const fetchSolo = async () => {
      // 유효한 Discord 채널 ID 집합 (삭제된 채널/깨진 snowflake 자동 제거용).
      // channels prop이 비어있으면 필터 건너뜀 — 불러오는 중일 수 있음.
      const validIds = new Set(channels.filter(c => c.type === 0).map(c => String(c.id)))
      try {
        const res = await api.get<{ debi?: unknown; marlene?: unknown }>(`/servers/${guildId}/solo-chat-channels`)
        const rawDebi = normalizeIds(res.data.debi)
        const rawMarlene = normalizeIds(res.data.marlene)

        const cleanDebi = validIds.size > 0 ? rawDebi.filter(id => validIds.has(id)) : rawDebi
        const cleanMarlene = validIds.size > 0 ? rawMarlene.filter(id => validIds.has(id)) : rawMarlene

        setSelection({ debi: cleanDebi, marlene: cleanMarlene })

        // stale ID가 있었으면 즉시 PUT으로 덮어써서 GCS 정리. 사용자에게 투명 고지.
        const staleCount =
          (rawDebi.length - cleanDebi.length) + (rawMarlene.length - cleanMarlene.length)
        if (staleCount > 0 && validIds.size > 0) {
          try {
            await api.put(`/servers/${guildId}/solo-chat-channels`, {
              debi: cleanDebi,
              marlene: cleanMarlene,
            })
            setMessage(`삭제된 채널 ${staleCount}개를 자동 정리했습니다.`)
            setTimeout(() => setMessage(null), 3000)
          } catch (e) {
            console.error('Failed to auto-clean stale channel IDs:', e)
          }
        }
      } catch (err: any) {
        if (err?.response?.status === 404) {
          setBackendMissing(true)
        } else {
          console.error('Failed to load solo chat channels:', err)
        }
      } finally {
        setLoaded(true)
      }
    }
    if (guildId) fetchSolo()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [guildId, channels])

  useEffect(() => {
    // 솔로봇 소속 여부 + 초대 URL 조회. 저장 동작과 무관하므로 독립 훅으로 분리.
    const fetchStatus = async () => {
      try {
        const res = await api.get<SoloBotsStatusResponse>(`/servers/${guildId}/solo-bots-status`)
        setBotStatus(res.data)
      } catch (err) {
        console.error('Failed to load solo bots status:', err)
      }
    }
    if (guildId) fetchStatus()
  }, [guildId])

  const persist = async (next: SoloMap) => {
    setSaving(true)
    setMessage(null)
    // snowflake 정밀도 손실 방지: PUT body는 반드시 string[]로 직렬화.
    const payload = {
      debi: normalizeIds(next.debi),
      marlene: normalizeIds(next.marlene),
    }
    try {
      await api.put(`/servers/${guildId}/solo-chat-channels`, payload)
      setMessage('저장되었습니다!')
      setTimeout(() => setMessage(null), 2500)
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setBackendMissing(true)
      }
      setMessage('저장에 실패했습니다.')
      setTimeout(() => setMessage(null), 3000)
    } finally {
      setSaving(false)
    }
  }

  const toggleChannel = (identity: Identity, channelId: unknown) => {
    // snowflake 정밀도 손실 방지: 클릭 이벤트로 들어온 값도 반드시 string으로 고정.
    const idStr = String(channelId)
    if (!idStr) return
    const current = selection[identity]
    const has = current.includes(idStr)
    let nextList: string[]
    if (has) {
      nextList = current.filter(id => id !== idStr)
    } else {
      if (current.length >= MAX_CHANNELS) {
        setMessage(`${IDENTITY_META[identity].label} 채널은 최대 ${MAX_CHANNELS}개까지 지정할 수 있습니다.`)
        setTimeout(() => setMessage(null), 2500)
        return
      }
      nextList = Array.from(new Set([...current, idStr]))
    }
    const next: SoloMap = { ...selection, [identity]: nextList }
    setSelection(next)
    persist(next)
  }

  const clearIdentity = (identity: Identity) => {
    const next: SoloMap = { ...selection, [identity]: [] }
    setSelection(next)
    persist(next)
  }

  if (!loaded) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-white mb-2">솔로봇 대화 채널</h2>
          <p className="text-discord-muted text-sm">불러오는 중...</p>
        </div>
      </div>
    )
  }

  const renderIdentity = (identity: Identity) => {
    const meta = IDENTITY_META[identity]
    const picked = selection[identity]
    const status = botStatus?.[identity]
    // 서버에 솔로봇이 없으면 채널 설정 UI 대신 초대 버튼을 보여준다.
    // status === null(로딩/엔드포인트 없음) 이면 기존 UI 유지 — 하위 호환.
    const needsInvite = status?.configured && !status.in_guild && !status.in_guild_unknown

    return (
      <div className="p-4 bg-discord-dark rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <label className="block font-medium text-white">
            <span className={meta.accent}>{meta.label}</span> 응답 채널
            {!needsInvite && (
              <span className="ml-2 text-xs text-discord-muted">({picked.length}/{MAX_CHANNELS})</span>
            )}
          </label>
          {!needsInvite && picked.length > 0 && (
            <button
              onClick={() => clearIdentity(identity)}
              disabled={saving}
              className="text-xs text-discord-muted hover:text-white transition-colors"
            >
              전체 해제
            </button>
          )}
        </div>

        {needsInvite ? (
          <div className="py-4">
            <p className="text-sm text-discord-muted mb-3">
              이 서버에 <span className={meta.accent}>{meta.label}</span> 솔로봇이 아직 초대되지 않았습니다.
              채널을 지정하려면 먼저 봇을 초대해주세요.
            </p>
            <button
              onClick={() => {
                if (status?.invite_url) {
                  window.open(status.invite_url, '_blank', 'noopener,noreferrer')
                }
              }}
              disabled={!status?.invite_url}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border-2 ${meta.border} ${meta.bg} ${meta.accent} hover:brightness-125 transition-all text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <span>{meta.label} 솔로봇 초대하기</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </button>
            <p className="text-xs text-discord-muted mt-2">
              초대 후 이 페이지를 새로고침하면 채널 설정이 나타납니다.
            </p>
          </div>
        ) : (
          <>
        <p className="text-xs text-discord-muted mb-3">
          채널을 클릭해 {meta.label} 솔로봇이 대화에 끼어들 채널을 지정합니다. 최대 {MAX_CHANNELS}개.
        </p>

        {textChannels.length === 0 ? (
          <p className="text-sm text-discord-muted text-center py-6">텍스트 채널이 없습니다.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-64 overflow-y-auto">
            {textChannels.map(ch => {
              const active = picked.includes(ch.id)
              const disabled = !active && picked.length >= MAX_CHANNELS
              return (
                <button
                  key={ch.id}
                  onClick={() => toggleChannel(identity, ch.id)}
                  disabled={saving || disabled}
                  className={`px-3 py-2 rounded-lg border-2 text-left text-sm transition-all truncate ${
                    active
                      ? `${meta.border} ${meta.bg} text-white`
                      : disabled
                        ? 'border-discord-light/10 text-discord-muted/50 cursor-not-allowed'
                        : 'border-discord-light/20 text-discord-muted hover:border-discord-light/40 hover:text-white'
                  }`}
                  title={`#${ch.name}`}
                >
                  #{ch.name}
                </button>
              )
            })}
          </div>
        )}
          </>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">솔로봇 대화 채널</h2>
        <p className="text-discord-muted text-sm">
          지정된 채널에서만 데비/마를렌 솔로봇이 대화에 끼어듭니다. 채널을 하나도 지정하지 않으면 솔로봇은 어떤 채널에서도 자발적으로 대화하지 않습니다.
        </p>
      </div>

      {backendMissing && (
        <div className="p-3 rounded-lg bg-yellow-500/10 text-yellow-300 text-sm">
          백엔드 API(`/servers/:guildId/solo-chat-channels`)가 아직 구현되지 않아 저장/불러오기가 동작하지 않습니다. 백엔드 반영 후 다시 시도해주세요.
        </div>
      )}

      {message && (
        <div
          className={`p-3 rounded-lg text-sm ${
            message.includes('실패') || message.includes('최대')
              ? 'bg-red-500/20 text-red-400'
              : 'bg-green-500/20 text-green-400'
          }`}
        >
          {message}
        </div>
      )}

      <div className="space-y-4">
        {renderIdentity('debi')}
        {renderIdentity('marlene')}
      </div>
    </div>
  )
}
