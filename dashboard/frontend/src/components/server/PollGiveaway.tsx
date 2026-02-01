import { useState } from 'react'

interface Channel {
  id: string
  name: string
  type: number
}

interface Props {
  channels: Channel[]
  guildId: string
}

export default function PollGiveaway({ channels, guildId }: Props) {
  const [activeTab, setActiveTab] = useState<'poll' | 'giveaway'>('poll')

  // Poll state
  const [pollChannel, setPollChannel] = useState('')
  const [pollQuestion, setPollQuestion] = useState('')
  const [pollOptions, setPollOptions] = useState(['', ''])
  const [pollDuration, setPollDuration] = useState('24')
  const [pollMultiple, setPollMultiple] = useState(false)

  // Giveaway state
  const [giveawayChannel, setGiveawayChannel] = useState('')
  const [giveawayPrize, setGiveawayPrize] = useState('')
  const [giveawayWinners, setGiveawayWinners] = useState('1')
  const [giveawayDuration, setGiveawayDuration] = useState('24')
  const [giveawayRequireRole] = useState('')

  const [sending, setSending] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  const textChannels = channels.filter(c => c.type === 0)

  const addPollOption = () => {
    if (pollOptions.length < 10) {
      setPollOptions([...pollOptions, ''])
    }
  }

  const removePollOption = (index: number) => {
    if (pollOptions.length > 2) {
      setPollOptions(pollOptions.filter((_, i) => i !== index))
    }
  }

  const updatePollOption = (index: number, value: string) => {
    setPollOptions(pollOptions.map((opt, i) => i === index ? value : opt))
  }

  const createPoll = async () => {
    if (!pollChannel || !pollQuestion || pollOptions.some(o => !o.trim())) {
      setMessage('모든 필드를 입력해주세요')
      return
    }

    setSending(true)
    setMessage(null)

    try {
      const response = await fetch(`/api/servers/${guildId}/poll`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          channelId: pollChannel,
          question: pollQuestion,
          options: pollOptions.filter(o => o.trim()),
          duration: parseInt(pollDuration),
          multiple: pollMultiple
        })
      })

      if (response.ok) {
        setMessage('투표가 생성되었습니다!')
        setPollQuestion('')
        setPollOptions(['', ''])
      } else {
        setMessage('생성에 실패했습니다')
      }
    } catch {
      setMessage('생성에 실패했습니다')
    } finally {
      setSending(false)
    }
  }

  const createGiveaway = async () => {
    if (!giveawayChannel || !giveawayPrize) {
      setMessage('모든 필드를 입력해주세요')
      return
    }

    setSending(true)
    setMessage(null)

    try {
      const response = await fetch(`/api/servers/${guildId}/giveaway`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          channelId: giveawayChannel,
          prize: giveawayPrize,
          winners: parseInt(giveawayWinners),
          duration: parseInt(giveawayDuration),
          requireRole: giveawayRequireRole || null
        })
      })

      if (response.ok) {
        setMessage('경품추첨이 생성되었습니다!')
        setGiveawayPrize('')
      } else {
        setMessage('생성에 실패했습니다')
      }
    } catch {
      setMessage('생성에 실패했습니다')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab('poll')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'poll'
              ? 'bg-debi-primary text-white'
              : 'bg-discord-darker text-discord-muted hover:text-discord-text'
          }`}
        >
          투표
        </button>
        <button
          onClick={() => setActiveTab('giveaway')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'giveaway'
              ? 'bg-debi-primary text-white'
              : 'bg-discord-darker text-discord-muted hover:text-discord-text'
          }`}
        >
          경품추첨
        </button>
      </div>

      {/* Poll Tab */}
      {activeTab === 'poll' && (
        <div className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold text-discord-text mb-2">투표 만들기</h2>
            <p className="text-discord-muted text-sm">멤버들이 투표할 수 있는 설문을 만듭니다.</p>
          </div>

          <div className="p-4 bg-discord-darker rounded-lg space-y-4">
            <div>
              <label className="block text-sm font-medium text-discord-muted mb-2">채널</label>
              <select
                value={pollChannel}
                onChange={(e) => setPollChannel(e.target.value)}
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
              >
                <option value="">채널 선택...</option>
                {textChannels.map(ch => (
                  <option key={ch.id} value={ch.id}>#{ch.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-discord-muted mb-2">질문</label>
              <input
                type="text"
                value={pollQuestion}
                onChange={(e) => setPollQuestion(e.target.value)}
                placeholder="투표 질문을 입력하세요"
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-discord-muted">선택지</label>
                <button
                  onClick={addPollOption}
                  disabled={pollOptions.length >= 10}
                  className="text-xs px-3 py-1 bg-debi-primary text-white rounded hover:bg-debi-primary/80 disabled:opacity-50"
                >
                  + 추가
                </button>
              </div>
              <div className="space-y-2">
                {pollOptions.map((option, i) => (
                  <div key={i} className="flex gap-2">
                    <input
                      type="text"
                      value={option}
                      onChange={(e) => updatePollOption(i, e.target.value)}
                      placeholder={`선택지 ${i + 1}`}
                      className="flex-1 p-2 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text text-sm focus:border-debi-primary focus:outline-none"
                    />
                    {pollOptions.length > 2 && (
                      <button
                        onClick={() => removePollOption(i)}
                        className="p-2 text-discord-red hover:bg-discord-red/20 rounded"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-discord-muted mb-2">기간 (시간)</label>
                <select
                  value={pollDuration}
                  onChange={(e) => setPollDuration(e.target.value)}
                  className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
                >
                  <option value="1">1시간</option>
                  <option value="6">6시간</option>
                  <option value="12">12시간</option>
                  <option value="24">24시간</option>
                  <option value="48">48시간</option>
                  <option value="168">1주일</option>
                </select>
              </div>
              <div className="flex items-center gap-3 pt-7">
                <input
                  type="checkbox"
                  id="pollMultiple"
                  checked={pollMultiple}
                  onChange={(e) => setPollMultiple(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="pollMultiple" className="text-sm text-discord-text">복수 선택 허용</label>
              </div>
            </div>
          </div>

          <button
            onClick={createPoll}
            disabled={sending}
            className="w-full py-3 btn-gradient text-white font-medium rounded-lg disabled:opacity-50"
          >
            {sending ? '생성 중...' : '투표 만들기'}
          </button>
        </div>
      )}

      {/* Giveaway Tab */}
      {activeTab === 'giveaway' && (
        <div className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold text-discord-text mb-2">경품추첨 만들기</h2>
            <p className="text-discord-muted text-sm">참여자 중 당첨자를 무작위로 선정합니다.</p>
          </div>

          <div className="p-4 bg-discord-darker rounded-lg space-y-4">
            <div>
              <label className="block text-sm font-medium text-discord-muted mb-2">채널</label>
              <select
                value={giveawayChannel}
                onChange={(e) => setGiveawayChannel(e.target.value)}
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
              >
                <option value="">채널 선택...</option>
                {textChannels.map(ch => (
                  <option key={ch.id} value={ch.id}>#{ch.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-discord-muted mb-2">경품</label>
              <input
                type="text"
                value={giveawayPrize}
                onChange={(e) => setGiveawayPrize(e.target.value)}
                placeholder="경품 이름을 입력하세요"
                className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-discord-muted mb-2">당첨자 수</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={giveawayWinners}
                  onChange={(e) => setGiveawayWinners(e.target.value)}
                  className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-discord-muted mb-2">기간 (시간)</label>
                <select
                  value={giveawayDuration}
                  onChange={(e) => setGiveawayDuration(e.target.value)}
                  className="w-full p-3 bg-discord-darkest border border-discord-light/20 rounded-lg text-discord-text focus:border-debi-primary focus:outline-none"
                >
                  <option value="1">1시간</option>
                  <option value="6">6시간</option>
                  <option value="12">12시간</option>
                  <option value="24">24시간</option>
                  <option value="48">48시간</option>
                  <option value="168">1주일</option>
                </select>
              </div>
            </div>
          </div>

          <button
            onClick={createGiveaway}
            disabled={sending}
            className="w-full py-3 btn-gradient text-white font-medium rounded-lg disabled:opacity-50"
          >
            {sending ? '생성 중...' : '경품추첨 만들기'}
          </button>
        </div>
      )}

      {message && (
        <p className={`text-sm text-center ${message.includes('실패') ? 'text-discord-red' : 'text-green-400'}`}>
          {message}
        </p>
      )}
    </div>
  )
}
