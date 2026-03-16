import { useState } from 'react'
import { api } from '../../services/api'

interface Channel {
  id: string
  name: string
  type: number
}

interface Props {
  channels: Channel[]
  guildId: string
}

export default function ChannelPurge({ channels, guildId }: Props) {
  const [selectedChannel, setSelectedChannel] = useState('')
  const [count, setCount] = useState('100')
  const [purging, setPurging] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const textChannels = channels.filter(c => c.type === 0)

  const handlePurge = async () => {
    if (!selectedChannel) return
    setPurging(true)
    setResult(null)
    setConfirmOpen(false)

    try {
      const response = await api.post<{ deleted: number }>(`/servers/${guildId}/channels/${selectedChannel}/purge`, {
        count: parseInt(count)
      })
      setResult(`${response.data.deleted}개 메시지 삭제 완료`)
    } catch (error: any) {
      const deleted = error.response?.data?.deleted || 0
      setResult(`오류 발생 (${deleted}개 삭제됨): ${error.response?.data?.error || error.message}`)
    } finally {
      setPurging(false)
    }
  }

  const channelName = textChannels.find(c => c.id === selectedChannel)?.name || ''

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">채널 청소</h2>
        <p className="text-discord-muted text-sm mt-1">선택한 채널의 메시지를 일괄 삭제합니다 (14일 이내 메시지만)</p>
      </div>

      <div className="bg-discord-dark rounded-lg p-6 space-y-4">
        {/* 채널 선택 */}
        <div>
          <label className="block text-sm font-medium text-discord-muted mb-2">채널 선택</label>
          <select
            value={selectedChannel}
            onChange={e => { setSelectedChannel(e.target.value); setResult(null) }}
            className="w-full bg-discord-darker border border-discord-light/20 rounded-md px-3 py-2 text-white focus:outline-none focus:border-discord-blurple"
          >
            <option value="">채널을 선택하세요</option>
            {textChannels.map(c => (
              <option key={c.id} value={c.id}>#{c.name}</option>
            ))}
          </select>
        </div>

        {/* 삭제 개수 */}
        <div>
          <label className="block text-sm font-medium text-discord-muted mb-2">삭제할 메시지 수</label>
          <select
            value={count}
            onChange={e => setCount(e.target.value)}
            className="w-full bg-discord-darker border border-discord-light/20 rounded-md px-3 py-2 text-white focus:outline-none focus:border-discord-blurple"
          >
            <option value="50">50개</option>
            <option value="100">100개</option>
            <option value="200">200개</option>
            <option value="500">500개</option>
            <option value="1000">1000개</option>
          </select>
        </div>

        {/* 경고 */}
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-md p-3">
          <p className="text-yellow-200 text-sm">
            삭제된 메시지는 복구할 수 없습니다. 14일이 넘은 메시지는 Discord 정책으로 일괄 삭제가 불가합니다.
          </p>
        </div>

        {/* 실행 버튼 */}
        {!confirmOpen ? (
          <button
            onClick={() => setConfirmOpen(true)}
            disabled={!selectedChannel || purging}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-md font-medium transition-colors"
          >
            청소 시작
          </button>
        ) : (
          <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/30 rounded-md p-4">
            <p className="text-red-200 text-sm flex-1">
              #{channelName} 채널에서 최대 {count}개의 메시지를 삭제합니다. 계속하시겠습니까?
            </p>
            <button
              onClick={handlePurge}
              disabled={purging}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white rounded-md font-medium transition-colors whitespace-nowrap"
            >
              {purging ? '삭제 중...' : '확인'}
            </button>
            <button
              onClick={() => setConfirmOpen(false)}
              disabled={purging}
              className="px-4 py-2 bg-discord-light/20 hover:bg-discord-light/30 text-white rounded-md font-medium transition-colors whitespace-nowrap"
            >
              취소
            </button>
          </div>
        )}

        {/* 결과 */}
        {result && (
          <div className={`rounded-md p-3 ${result.includes('오류') ? 'bg-red-500/10 border border-red-500/30' : 'bg-green-500/10 border border-green-500/30'}`}>
            <p className={`text-sm ${result.includes('오류') ? 'text-red-200' : 'text-green-200'}`}>{result}</p>
          </div>
        )}
      </div>
    </div>
  )
}
