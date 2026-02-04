import { useState, useEffect } from 'react'
import { api } from '../../services/api'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface DailyStats {
  date: string
  messages: number
  member_count: number
  active_users: number
}

interface MemberStats {
  id: string
  name: string
  messages: number
}

interface LogEntry {
  type: string
  user_id: string
  user_name: string
  timestamp: string
  channel?: string
  roles?: string[]
}

interface Props {
  guildId: string
}

const LOG_TYPE_LABELS: Record<string, string> = {
  join: '입장',
  leave: '퇴장',
  role_add: '역할 추가',
  role_remove: '역할 제거',
  message_delete: '메시지 삭제',
  message_edit: '메시지 수정',
}

const LOG_TYPE_COLORS: Record<string, string> = {
  join: 'text-green-400',
  leave: 'text-red-400',
  role_add: 'text-blue-400',
  role_remove: 'text-orange-400',
  message_delete: 'text-yellow-400',
  message_edit: 'text-purple-400',
}

export default function ServerStats({ guildId }: Props) {
  const [loading, setLoading] = useState(true)
  const [daily, setDaily] = useState<DailyStats[]>([])
  const [topMembers, setTopMembers] = useState<MemberStats[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [activeTab, setActiveTab] = useState<'overview' | 'members' | 'logs'>('overview')
  const [logFilter, setLogFilter] = useState<string>('')

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get<{
          daily: DailyStats[]
          topMembers: MemberStats[]
          logs: LogEntry[]
        }>(`/servers/${guildId}/stats`)

        setDaily(response.data.daily)
        setTopMembers(response.data.topMembers)
        setLogs(response.data.logs)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [guildId])

  const fetchFilteredLogs = async (type: string) => {
    setLogFilter(type)
    try {
      const url = type
        ? `/servers/${guildId}/stats/logs?type=${type}&limit=100`
        : `/servers/${guildId}/stats/logs?limit=100`
      const response = await api.get<{ logs: LogEntry[] }>(url)
      setLogs(response.data.logs)
    } catch (error) {
      console.error('Failed to fetch logs:', error)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-discord-muted">로딩 중...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">서버 통계</h2>
        <p className="text-discord-muted text-sm">멤버 활동 및 서버 통계를 확인합니다.</p>
      </div>

      {/* 탭 */}
      <div className="flex gap-2">
        {(['overview', 'members', 'logs'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              activeTab === tab
                ? 'bg-debi-primary text-white'
                : 'bg-discord-dark text-discord-muted hover:text-white'
            }`}
          >
            {tab === 'overview' ? '개요' : tab === 'members' ? '멤버 순위' : '활동 로그'}
          </button>
        ))}
      </div>

      {/* 개요 탭 */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* 요약 카드 */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-discord-dark rounded-lg">
              <p className="text-discord-muted text-sm">오늘 메시지</p>
              <p className="text-2xl font-bold text-white">
                {daily.length > 0 ? daily[daily.length - 1]?.messages || 0 : 0}
              </p>
            </div>
            <div className="p-4 bg-discord-dark rounded-lg">
              <p className="text-discord-muted text-sm">현재 멤버</p>
              <p className="text-2xl font-bold text-white">
                {daily.length > 0 ? daily[daily.length - 1]?.member_count || 0 : 0}
              </p>
            </div>
            <div className="p-4 bg-discord-dark rounded-lg">
              <p className="text-discord-muted text-sm">오늘 활성 유저</p>
              <p className="text-2xl font-bold text-white">
                {daily.length > 0 ? daily[daily.length - 1]?.active_users || 0 : 0}
              </p>
            </div>
          </div>

          {/* 메시지 수 차트 */}
          <div className="p-4 bg-discord-dark rounded-lg">
            <h3 className="text-white font-medium mb-4">일별 메시지 수</h3>
            {daily.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={daily}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#40444b" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={formatDate}
                    stroke="#72767d"
                    fontSize={12}
                  />
                  <YAxis stroke="#72767d" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#2f3136',
                      border: 'none',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="messages"
                    stroke="#5865f2"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-discord-muted">
                아직 데이터가 없습니다
              </div>
            )}
          </div>

          {/* 멤버 수 차트 */}
          <div className="p-4 bg-discord-dark rounded-lg">
            <h3 className="text-white font-medium mb-4">멤버 수 추이</h3>
            {daily.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={daily}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#40444b" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={formatDate}
                    stroke="#72767d"
                    fontSize={12}
                  />
                  <YAxis stroke="#72767d" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#2f3136',
                      border: 'none',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="member_count"
                    stroke="#57f287"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-discord-muted">
                아직 데이터가 없습니다
              </div>
            )}
          </div>
        </div>
      )}

      {/* 멤버 순위 탭 */}
      {activeTab === 'members' && (
        <div className="p-4 bg-discord-dark rounded-lg">
          <h3 className="text-white font-medium mb-4">메시지 순위 (상위 20명)</h3>
          {topMembers.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={topMembers.slice(0, 10)} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#40444b" />
                  <XAxis type="number" stroke="#72767d" fontSize={12} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    stroke="#72767d"
                    fontSize={12}
                    width={100}
                    tickFormatter={(value) => value.slice(0, 10)}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#2f3136',
                      border: 'none',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="messages" fill="#5865f2" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>

              <div className="mt-4 space-y-2">
                {topMembers.map((member, index) => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-2 bg-discord-darkest rounded"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-discord-muted w-6">#{index + 1}</span>
                      <span className="text-white">{member.name || `User ${member.id}`}</span>
                    </div>
                    <span className="text-debi-primary font-medium">
                      {member.messages.toLocaleString()} 메시지
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-64 flex items-center justify-center text-discord-muted">
              아직 데이터가 없습니다
            </div>
          )}
        </div>
      )}

      {/* 활동 로그 탭 */}
      {activeTab === 'logs' && (
        <div className="space-y-4">
          {/* 필터 */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => fetchFilteredLogs('')}
              className={`px-3 py-1 rounded text-sm ${
                !logFilter ? 'bg-debi-primary text-white' : 'bg-discord-dark text-discord-muted'
              }`}
            >
              전체
            </button>
            {Object.entries(LOG_TYPE_LABELS).map(([type, label]) => (
              <button
                key={type}
                onClick={() => fetchFilteredLogs(type)}
                className={`px-3 py-1 rounded text-sm ${
                  logFilter === type
                    ? 'bg-debi-primary text-white'
                    : 'bg-discord-dark text-discord-muted'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* 로그 목록 */}
          <div className="p-4 bg-discord-dark rounded-lg max-h-[500px] overflow-y-auto">
            {logs.length > 0 ? (
              <div className="space-y-2">
                {logs.map((log, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-discord-darkest rounded text-sm"
                  >
                    <div className="flex items-center gap-3">
                      <span className={`font-medium ${LOG_TYPE_COLORS[log.type] || 'text-white'}`}>
                        [{LOG_TYPE_LABELS[log.type] || log.type}]
                      </span>
                      <span className="text-white">{log.user_name}</span>
                      {log.channel && (
                        <span className="text-discord-muted">#{log.channel}</span>
                      )}
                      {log.roles && (
                        <span className="text-discord-muted">{log.roles.join(', ')}</span>
                      )}
                    </div>
                    <span className="text-discord-muted text-xs">
                      {formatTimestamp(log.timestamp)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-discord-muted">
                로그가 없습니다
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
