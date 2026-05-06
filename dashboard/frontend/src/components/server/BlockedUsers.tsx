import { useEffect, useState, useCallback, useMemo } from 'react'
import { api } from '../../services/api'
import {
  blocklistApi, BlockableFeature, BlockedUserItem,
} from '../../lib/credits'

const FEATURE_OPTIONS: { key: BlockableFeature; label: string; help: string }[] = [
  { key: 'chat', label: '대화', help: '/대화 슬래시 + 호명 응답' },
  { key: 'solo_chat', label: '솔로봇 끼어들기', help: '데비/마를렌 솔로봇 자동 응답' },
  { key: 'tts', label: 'TTS', help: 'TTS 음성 읽기' },
  { key: 'credits', label: '크레딧/도박', help: '향후 확장 — 잔고/베팅 봉인' },
]

interface Member {
  id: string
  username: string
  displayName: string
  avatar: string | null
}

interface Props {
  guildId: string
}

function avatarUrl(m: Member): string | null {
  if (!m.avatar) return null
  return `https://cdn.discordapp.com/avatars/${m.id}/${m.avatar}.png?size=64`
}

export default function BlockedUsers({ guildId }: Props) {
  const [items, setItems] = useState<BlockedUserItem[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  // 폼 상태
  const [pickerOpen, setPickerOpen] = useState(false)
  const [pickerQuery, setPickerQuery] = useState('')
  const [selectedUser, setSelectedUser] = useState<Member | null>(null)
  const [newFeatures, setNewFeatures] = useState<BlockableFeature[]>(['chat'])

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await blocklistApi.list(guildId)
      setItems(r.items)
    } catch (e) {
      setError((e as Error).message ?? '조회 실패')
    } finally {
      setLoading(false)
    }
  }, [guildId])

  // TTS 설정 페이지와 동일 — 봇 토큰으로 길드 멤버 100명 페치
  const fetchMembers = useCallback(async () => {
    try {
      const res = await api.get<{ members: Member[]; serverDefault: string }>(
        `/servers/${guildId}/members`,
      )
      setMembers(res.data.members)
    } catch (e) {
      console.error('멤버 페치 실패', e)
    }
  }, [guildId])

  useEffect(() => { void refresh(); void fetchMembers() }, [refresh, fetchMembers])

  // user_id → Member 매핑 (목록 표시용)
  const memberById = useMemo(() => {
    const map = new Map<string, Member>()
    members.forEach(m => map.set(m.id, m))
    return map
  }, [members])

  const filteredMembers = useMemo(() => {
    const q = pickerQuery.trim().toLowerCase()
    const blockedSet = new Set(items.map(i => i.user_id))
    const list = members.filter(m => !blockedSet.has(m.id))
    if (!q) return list.slice(0, 50)
    return list.filter(m =>
      m.displayName.toLowerCase().includes(q)
      || m.username.toLowerCase().includes(q)
      || m.id.includes(q),
    ).slice(0, 50)
  }, [members, items, pickerQuery])

  const toggleFeature = (f: BlockableFeature) => {
    setNewFeatures(prev =>
      prev.includes(f) ? prev.filter(x => x !== f) : [...prev, f],
    )
  }

  const submit = async () => {
    if (!selectedUser) {
      setError('차단할 멤버를 선택하세요')
      return
    }
    if (newFeatures.length === 0) {
      setError('최소 한 개 기능 선택')
      return
    }
    setBusy(true)
    setError(null)
    try {
      await blocklistApi.upsert(guildId, selectedUser.id, newFeatures)
      setSelectedUser(null)
      setPickerQuery('')
      setNewFeatures(['chat'])
      await refresh()
    } catch (e) {
      setError((e as Error).message ?? '저장 실패')
    } finally {
      setBusy(false)
    }
  }

  const editFeatures = async (uid: string, features: BlockableFeature[]) => {
    if (features.length === 0) {
      await blocklistApi.remove(guildId, uid)
    } else {
      await blocklistApi.upsert(guildId, uid, features)
    }
    await refresh()
  }

  const remove = async (uid: string) => {
    const m = memberById.get(uid)
    const label = m ? m.displayName : uid
    if (!confirm(`${label} 차단을 해제할까요?`)) return
    await blocklistApi.remove(guildId, uid)
    await refresh()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-1">기능 차단</h2>
        <p className="text-discord-muted text-sm">
          특정 멤버가 이 서버에서 봇 기능을 사용하지 못하도록 차단합니다.
          서버 관리자만 설정 가능합니다.
        </p>
      </div>

      {/* 추가 폼 */}
      <div className="p-4 rounded-lg bg-discord-dark border border-discord-darkest space-y-3">
        <div className="relative">
          <label className="block text-xs text-discord-muted mb-1">멤버 선택</label>
          {selectedUser ? (
            <div className="flex items-center gap-2 px-3 py-2 rounded-md bg-discord-darkest border border-debi-primary/40">
              {avatarUrl(selectedUser) ? (
                <img
                  src={avatarUrl(selectedUser) as string}
                  alt=""
                  className="w-7 h-7 rounded-full"
                />
              ) : (
                <div className="w-7 h-7 rounded-full bg-discord-light/20" />
              )}
              <div className="flex-1 min-w-0">
                <div className="text-sm text-white truncate">{selectedUser.displayName}</div>
                <div className="text-[10px] text-discord-muted truncate">
                  @{selectedUser.username} · {selectedUser.id}
                </div>
              </div>
              <button
                onClick={() => { setSelectedUser(null); setPickerQuery('') }}
                className="text-xs px-2 py-1 rounded bg-discord-light/10 text-discord-muted hover:text-white"
              >
                변경
              </button>
            </div>
          ) : (
            <>
              <input
                type="text"
                value={pickerQuery}
                onChange={(e) => { setPickerQuery(e.target.value); setPickerOpen(true) }}
                onFocus={() => setPickerOpen(true)}
                placeholder="이름·ID 검색"
                className="w-full px-3 py-2 rounded-md bg-discord-darkest border border-discord-light/20 text-white text-sm"
              />
              {pickerOpen && filteredMembers.length > 0 && (
                <div className="absolute z-30 mt-1 left-0 right-0 max-h-72 overflow-y-auto rounded-md bg-discord-darkest border border-discord-light/20 shadow-xl">
                  {filteredMembers.map(m => (
                    <button
                      key={m.id}
                      onClick={() => {
                        setSelectedUser(m)
                        setPickerOpen(false)
                        setPickerQuery('')
                      }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-discord-light/10"
                    >
                      {avatarUrl(m) ? (
                        <img src={avatarUrl(m) as string} alt="" className="w-7 h-7 rounded-full" />
                      ) : (
                        <div className="w-7 h-7 rounded-full bg-discord-light/20" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-white truncate">{m.displayName}</div>
                        <div className="text-[10px] text-discord-muted truncate">@{m.username}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
              {pickerOpen && pickerQuery && filteredMembers.length === 0 && (
                <div className="absolute z-30 mt-1 left-0 right-0 px-3 py-2 rounded-md bg-discord-darkest border border-discord-light/20 text-discord-muted text-xs">
                  일치하는 멤버 없음 (서버에 들어와 있고 차단 안 된 멤버만 노출, 최대 100명)
                </div>
              )}
            </>
          )}
          <p className="text-[10px] text-discord-muted mt-1">
            서버에 들어와 있는 멤버 중에서 선택. 봇은 자동 제외.
          </p>
        </div>

        <div>
          <label className="block text-xs text-discord-muted mb-1">차단 기능</label>
          <div className="grid grid-cols-2 gap-2">
            {FEATURE_OPTIONS.map(opt => (
              <label
                key={opt.key}
                className={`flex items-start gap-2 p-2 rounded-md border cursor-pointer transition-colors text-sm
                  ${newFeatures.includes(opt.key)
                    ? 'bg-debi-primary/15 border-debi-primary/50 text-white'
                    : 'bg-discord-darkest border-discord-light/15 text-discord-muted hover:text-white'}`}
              >
                <input
                  type="checkbox"
                  checked={newFeatures.includes(opt.key)}
                  onChange={() => toggleFeature(opt.key)}
                  className="mt-0.5"
                />
                <div className="leading-tight">
                  <div className="font-medium">{opt.label}</div>
                  <div className="text-[10px] opacity-70">{opt.help}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={submit}
            disabled={busy || !selectedUser || newFeatures.length === 0}
            className="px-4 py-2 rounded-md bg-debi-primary text-white text-sm font-bold disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {busy ? '저장 중…' : '차단 추가'}
          </button>
          {error && <span className="text-discord-red text-xs">{error}</span>}
        </div>
      </div>

      {/* 목록 */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-discord-muted">
            현재 차단 목록 · {items.length}명
          </div>
          <button
            onClick={() => { void refresh(); void fetchMembers() }}
            className="text-xs px-2 py-1 rounded bg-discord-light/10 text-discord-muted hover:text-white"
          >
            새로고침
          </button>
        </div>

        {loading ? (
          <div className="text-discord-muted text-sm">불러오는 중…</div>
        ) : items.length === 0 ? (
          <div className="p-4 rounded-md bg-discord-dark text-center text-discord-muted text-sm">
            차단된 멤버가 없습니다.
          </div>
        ) : (
          <div className="space-y-2">
            {items.map(item => (
              <BlockedRow
                key={item.user_id}
                item={item}
                member={memberById.get(item.user_id) || null}
                onEdit={(f) => editFeatures(item.user_id, f)}
                onRemove={() => remove(item.user_id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function BlockedRow({
  item, member, onEdit, onRemove,
}: {
  item: BlockedUserItem
  member: Member | null
  onEdit: (features: BlockableFeature[]) => void
  onRemove: () => void
}) {
  const toggle = (f: BlockableFeature) => {
    const next = item.features.includes(f)
      ? item.features.filter(x => x !== f)
      : [...item.features, f]
    onEdit(next)
  }

  return (
    <div className="p-3 rounded-md bg-discord-dark border border-discord-darkest">
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {member && avatarUrl(member) ? (
            <img src={avatarUrl(member) as string} alt="" className="w-7 h-7 rounded-full" />
          ) : (
            <div className="w-7 h-7 rounded-full bg-discord-light/20" />
          )}
          <div className="min-w-0">
            <div className="text-sm text-white truncate">
              {member ? member.displayName : '(서버에 없는 유저)'}
            </div>
            <div className="text-[10px] text-discord-muted font-mono truncate tabular-nums">
              {item.user_id}
            </div>
          </div>
        </div>
        <button
          onClick={onRemove}
          className="text-xs px-2 py-1 rounded bg-discord-red/20 text-discord-red hover:bg-discord-red/30 shrink-0"
        >
          차단 해제
        </button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {FEATURE_OPTIONS.map(opt => {
          const active = item.features.includes(opt.key)
          return (
            <button
              key={opt.key}
              onClick={() => toggle(opt.key)}
              className={`px-2 py-1 rounded-full text-[11px] font-medium border transition-colors
                ${active
                  ? 'bg-discord-red/30 border-discord-red/50 text-discord-red'
                  : 'bg-discord-darkest border-discord-light/15 text-discord-muted hover:text-white'}`}
              title={opt.help}
            >
              {opt.label}
            </button>
          )
        })}
      </div>
      {item.blocked_at && (
        <div className="text-[10px] text-discord-muted mt-2">
          {new Date(item.blocked_at).toLocaleString()}
          {item.blocked_by ? ` · by ${item.blocked_by}` : ''}
        </div>
      )}
    </div>
  )
}
