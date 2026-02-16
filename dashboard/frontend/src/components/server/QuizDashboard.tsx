import { useState, useEffect } from 'react'
import { api } from '../../services/api'

interface LeaderboardEntry {
  user_id: string
  display_name: string
  total_games: number
  total_score: number
  song_games: number
  er_games: number
  wins: number
  title_correct: number
  artist_correct: number
}

interface QuizSession {
  id: string
  quiz_type: string
  timestamp: string
  total_questions: number
  participants: number
  scores: Record<string, number>
  title_scores?: Record<string, number>
  artist_scores?: Record<string, number>
  winner_id: string | null
}

interface Song {
  title: string
  artist: string
  query: string
  aliases?: string[]
}

interface Props {
  guildId: string
}

export default function QuizDashboard({ guildId }: Props) {
  const [activeTab, setActiveTab] = useState<'stats' | 'songs'>('stats')
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [sessions, setSessions] = useState<QuizSession[]>([])
  const [totalSessions, setTotalSessions] = useState(0)
  const [songs, setSongs] = useState<Song[]>([])
  const [songCount, setSongCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  // 곡 추가 폼
  const [newSong, setNewSong] = useState({ title: '', artist: '', query: '', aliases: '' })
  const [editIndex, setEditIndex] = useState<number | null>(null)
  const [editSong, setEditSong] = useState({ title: '', artist: '', query: '', aliases: '' })

  useEffect(() => {
    fetchData()
  }, [guildId])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [statsRes, songsRes] = await Promise.all([
        api.get<{ leaderboard: LeaderboardEntry[]; recent_sessions: QuizSession[]; total_sessions: number }>(`/quiz/${guildId}/stats`),
        api.get<{ songs: Song[]; count: number }>('/quiz/songs'),
      ])
      setLeaderboard(statsRes.data.leaderboard)
      setSessions(statsRes.data.recent_sessions)
      setTotalSessions(statsRes.data.total_sessions)
      setSongs(songsRes.data.songs)
      setSongCount(songsRes.data.count)
    } catch {
      // 데이터 없으면 빈 상태
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (msg: string) => {
    setMessage(msg)
    setTimeout(() => setMessage(null), 3000)
  }

  // -- 곡 CRUD --

  const handleAddSong = async () => {
    if (!newSong.title || !newSong.artist || !newSong.query) return
    setSaving(true)
    try {
      const aliases = newSong.aliases ? newSong.aliases.split(',').map(a => a.trim()).filter(Boolean) : []
      await api.post('/quiz/songs', { ...newSong, aliases })
      setNewSong({ title: '', artist: '', query: '', aliases: '' })
      const res = await api.get<{ songs: Song[]; count: number }>('/quiz/songs')
      setSongs(res.data.songs)
      setSongCount(res.data.count)
      showMessage('곡이 추가되었습니다.')
    } catch {
      showMessage('추가에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  const handleEditSong = async (index: number) => {
    if (!editSong.title || !editSong.artist || !editSong.query) return
    setSaving(true)
    try {
      const aliases = editSong.aliases ? editSong.aliases.split(',').map(a => a.trim()).filter(Boolean) : []
      await api.put(`/quiz/songs/${index}`, { ...editSong, aliases })
      setEditIndex(null)
      const res = await api.get<{ songs: Song[]; count: number }>('/quiz/songs')
      setSongs(res.data.songs)
      setSongCount(res.data.count)
      showMessage('곡이 수정되었습니다.')
    } catch {
      showMessage('수정에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteSong = async (index: number) => {
    setSaving(true)
    try {
      await api.delete(`/quiz/songs/${index}`)
      const res = await api.get<{ songs: Song[]; count: number }>('/quiz/songs')
      setSongs(res.data.songs)
      setSongCount(res.data.count)
      showMessage('곡이 삭제되었습니다.')
    } catch {
      showMessage('삭제에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  const handleResetSongs = async () => {
    if (!confirm('곡 목록을 기본값으로 초기화하시겠습니까?')) return
    setSaving(true)
    try {
      await api.post('/quiz/songs/reset')
      const res = await api.get<{ songs: Song[]; count: number }>('/quiz/songs')
      setSongs(res.data.songs)
      setSongCount(res.data.count)
      showMessage('기본 곡 목록으로 초기화되었습니다.')
    } catch {
      showMessage('초기화에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  const startEdit = (index: number) => {
    const song = songs[index]
    setEditIndex(index)
    setEditSong({
      title: song.title,
      artist: song.artist,
      query: song.query,
      aliases: song.aliases?.join(', ') || '',
    })
  }

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const quizTypeLabel = (type: string) => type === 'song' ? '노래' : '이터널리턴'

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-debi-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white mb-2">퀴즈</h2>
          <p className="text-discord-muted text-sm">퀴즈 통계 확인 및 노래 목록을 관리합니다.</p>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className={`p-3 rounded-lg ${message.includes('실패') ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
          {message}
        </div>
      )}

      {/* Tab Buttons */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab('stats')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'stats' ? 'bg-debi-primary text-white' : 'bg-discord-dark text-discord-muted hover:text-white'
          }`}
        >
          통계 / 랭킹
        </button>
        <button
          onClick={() => setActiveTab('songs')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'songs' ? 'bg-debi-primary text-white' : 'bg-discord-dark text-discord-muted hover:text-white'
          }`}
        >
          곡 관리 ({songCount})
        </button>
      </div>

      {/* Stats Tab */}
      {activeTab === 'stats' && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-discord-dark rounded-lg">
              <p className="text-discord-muted text-sm">총 퀴즈 게임</p>
              <p className="text-2xl font-bold text-white mt-1">{totalSessions}</p>
            </div>
            <div className="p-4 bg-discord-dark rounded-lg">
              <p className="text-discord-muted text-sm">참여자 수</p>
              <p className="text-2xl font-bold text-white mt-1">{leaderboard.length}</p>
            </div>
            <div className="p-4 bg-discord-dark rounded-lg">
              <p className="text-discord-muted text-sm">최다 승자</p>
              <p className="text-2xl font-bold text-white mt-1">
                {leaderboard.length > 0 ? (leaderboard[0].display_name || `#${leaderboard[0].user_id.slice(-4)}`) : '-'}
              </p>
            </div>
          </div>

          {/* Leaderboard */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">리더보드</h3>
            {leaderboard.length === 0 ? (
              <div className="p-6 bg-discord-dark rounded-lg text-center text-discord-muted">
                아직 퀴즈 기록이 없습니다.
              </div>
            ) : (
              <div className="bg-discord-dark rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-discord-light/10">
                      <th className="px-4 py-3 text-left text-xs font-medium text-discord-muted uppercase">#</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-discord-muted uppercase">닉네임</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-discord-muted uppercase">게임</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-discord-muted uppercase">총 점수</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-discord-muted uppercase">승리</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-discord-muted uppercase">제목</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-discord-muted uppercase">가수</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard.map((entry, i) => (
                      <tr key={entry.user_id} className="border-b border-discord-light/5 hover:bg-discord-light/5">
                        <td className="px-4 py-3 text-sm text-discord-muted">{i + 1}</td>
                        <td className="px-4 py-3 text-sm text-white font-medium">
                          {entry.display_name || `User#${entry.user_id.slice(-4)}`}
                        </td>
                        <td className="px-4 py-3 text-sm text-discord-muted text-center">{entry.total_games}</td>
                        <td className="px-4 py-3 text-sm text-white text-center font-semibold">{entry.total_score}</td>
                        <td className="px-4 py-3 text-sm text-debi-primary text-center">{entry.wins}</td>
                        <td className="px-4 py-3 text-sm text-discord-muted text-center">{entry.title_correct}</td>
                        <td className="px-4 py-3 text-sm text-discord-muted text-center">{entry.artist_correct}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Recent Sessions */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">최근 게임</h3>
            {sessions.length === 0 ? (
              <div className="p-6 bg-discord-dark rounded-lg text-center text-discord-muted">
                아직 게임 기록이 없습니다.
              </div>
            ) : (
              <div className="space-y-2">
                {sessions.map(s => (
                  <div key={s.id} className="p-4 bg-discord-dark rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        s.quiz_type === 'song' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {quizTypeLabel(s.quiz_type)}
                      </span>
                      <span className="text-sm text-white">{s.total_questions}문제</span>
                      <span className="text-sm text-discord-muted">{s.participants}명 참여</span>
                    </div>
                    <span className="text-sm text-discord-muted">{formatDate(s.timestamp)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Songs Tab */}
      {activeTab === 'songs' && (
        <div className="space-y-6">
          {/* Add Song Form */}
          <div className="p-4 bg-discord-dark rounded-lg space-y-3">
            <h3 className="text-sm font-semibold text-white">곡 추가</h3>
            <div className="grid grid-cols-2 gap-3">
              <input
                type="text"
                placeholder="제목"
                value={newSong.title}
                onChange={e => setNewSong({ ...newSong, title: e.target.value })}
                className="p-2.5 bg-discord-darkest border border-discord-light/20 rounded-lg text-white text-sm focus:border-debi-primary focus:outline-none"
              />
              <input
                type="text"
                placeholder="가수"
                value={newSong.artist}
                onChange={e => setNewSong({ ...newSong, artist: e.target.value })}
                className="p-2.5 bg-discord-darkest border border-discord-light/20 rounded-lg text-white text-sm focus:border-debi-primary focus:outline-none"
              />
              <input
                type="text"
                placeholder="YouTube 검색어"
                value={newSong.query}
                onChange={e => setNewSong({ ...newSong, query: e.target.value })}
                className="p-2.5 bg-discord-darkest border border-discord-light/20 rounded-lg text-white text-sm focus:border-debi-primary focus:outline-none"
              />
              <input
                type="text"
                placeholder="별칭 (쉼표 구분)"
                value={newSong.aliases}
                onChange={e => setNewSong({ ...newSong, aliases: e.target.value })}
                className="p-2.5 bg-discord-darkest border border-discord-light/20 rounded-lg text-white text-sm focus:border-debi-primary focus:outline-none"
              />
            </div>
            <button
              onClick={handleAddSong}
              disabled={saving || !newSong.title || !newSong.artist || !newSong.query}
              className="px-4 py-2 bg-debi-primary text-white rounded-lg text-sm font-medium hover:bg-debi-primary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              추가
            </button>
          </div>

          {/* Song List */}
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">곡 목록 ({songCount}곡)</h3>
            <button
              onClick={handleResetSongs}
              disabled={saving}
              className="px-3 py-1.5 text-xs text-discord-muted border border-discord-light/20 rounded-lg hover:text-white hover:border-discord-light/40 transition-colors"
            >
              기본값으로 초기화
            </button>
          </div>

          <div className="bg-discord-dark rounded-lg overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-discord-light/10">
                  <th className="px-4 py-3 text-left text-xs font-medium text-discord-muted uppercase w-8">#</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-discord-muted uppercase">제목</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-discord-muted uppercase">가수</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-discord-muted uppercase">검색어</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-discord-muted uppercase">별칭</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-discord-muted uppercase w-24">작업</th>
                </tr>
              </thead>
              <tbody>
                {songs.map((song, i) => (
                  <tr key={i} className="border-b border-discord-light/5 hover:bg-discord-light/5">
                    {editIndex === i ? (
                      <>
                        <td className="px-4 py-2 text-sm text-discord-muted">{i + 1}</td>
                        <td className="px-2 py-2">
                          <input
                            type="text"
                            value={editSong.title}
                            onChange={e => setEditSong({ ...editSong, title: e.target.value })}
                            className="w-full p-1.5 bg-discord-darkest border border-discord-light/20 rounded text-white text-sm focus:border-debi-primary focus:outline-none"
                          />
                        </td>
                        <td className="px-2 py-2">
                          <input
                            type="text"
                            value={editSong.artist}
                            onChange={e => setEditSong({ ...editSong, artist: e.target.value })}
                            className="w-full p-1.5 bg-discord-darkest border border-discord-light/20 rounded text-white text-sm focus:border-debi-primary focus:outline-none"
                          />
                        </td>
                        <td className="px-2 py-2">
                          <input
                            type="text"
                            value={editSong.query}
                            onChange={e => setEditSong({ ...editSong, query: e.target.value })}
                            className="w-full p-1.5 bg-discord-darkest border border-discord-light/20 rounded text-white text-sm focus:border-debi-primary focus:outline-none"
                          />
                        </td>
                        <td className="px-2 py-2">
                          <input
                            type="text"
                            value={editSong.aliases}
                            onChange={e => setEditSong({ ...editSong, aliases: e.target.value })}
                            className="w-full p-1.5 bg-discord-darkest border border-discord-light/20 rounded text-white text-sm focus:border-debi-primary focus:outline-none"
                          />
                        </td>
                        <td className="px-4 py-2 text-right">
                          <div className="flex gap-1 justify-end">
                            <button
                              onClick={() => handleEditSong(i)}
                              disabled={saving}
                              className="px-2 py-1 text-xs bg-debi-primary text-white rounded hover:bg-debi-primary/80 transition-colors"
                            >
                              저장
                            </button>
                            <button
                              onClick={() => setEditIndex(null)}
                              className="px-2 py-1 text-xs text-discord-muted border border-discord-light/20 rounded hover:text-white transition-colors"
                            >
                              취소
                            </button>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="px-4 py-3 text-sm text-discord-muted">{i + 1}</td>
                        <td className="px-4 py-3 text-sm text-white">{song.title}</td>
                        <td className="px-4 py-3 text-sm text-discord-muted">{song.artist}</td>
                        <td className="px-4 py-3 text-sm text-discord-muted truncate max-w-[150px]">{song.query}</td>
                        <td className="px-4 py-3 text-sm text-discord-muted truncate max-w-[120px]">
                          {song.aliases?.join(', ') || '-'}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex gap-1 justify-end">
                            <button
                              onClick={() => startEdit(i)}
                              className="px-2 py-1 text-xs text-discord-muted border border-discord-light/20 rounded hover:text-white transition-colors"
                            >
                              수정
                            </button>
                            <button
                              onClick={() => handleDeleteSong(i)}
                              disabled={saving}
                              className="px-2 py-1 text-xs text-red-400 border border-red-400/30 rounded hover:bg-red-400/10 transition-colors"
                            >
                              삭제
                            </button>
                          </div>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
