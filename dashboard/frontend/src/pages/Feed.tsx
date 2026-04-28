import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { api } from '../services/api'

interface FeedItem {
  source: string
  title: string
  url: string
  summary?: string
  comment?: string
  score?: number
  stars?: number
  downloads?: number
  language?: string
}

interface DailyFeed {
  date: string
  sent_at: string | null
  selected_count: number
  raw_count: number
  new_count: number
  items: FeedItem[]
}

const SOURCE_LABEL: Record<string, { tag: string; color: string }> = {
  'smol-ai': { tag: 'NEWS', color: 'bg-amber-600/20 text-amber-300 border-amber-700/40' },
  'github-trending': { tag: 'GH', color: 'bg-zinc-700/30 text-zinc-200 border-zinc-600/40' },
  'hf-trending': { tag: 'HF', color: 'bg-yellow-700/20 text-yellow-300 border-yellow-700/40' },
  'hn-ai': { tag: 'HN', color: 'bg-orange-700/20 text-orange-300 border-orange-700/40' },
}

function scoreColor(score?: number): string {
  if (!score) return 'text-zinc-500'
  if (score >= 9) return 'text-pink-400'
  if (score >= 7) return 'text-cyan-400'
  if (score >= 5) return 'text-zinc-200'
  return 'text-zinc-500'
}

function ItemCard({ item }: { item: FeedItem }) {
  const src = SOURCE_LABEL[item.source] ?? { tag: '?', color: 'bg-zinc-800 text-zinc-400' }
  return (
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-discord-darker border border-discord-light/30 rounded-lg p-4 hover:border-debi-primary/50 transition-colors"
    >
      <div className="flex items-start gap-3 mb-2">
        <span className={`text-xs px-2 py-0.5 rounded border font-mono ${src.color}`}>
          {src.tag}
        </span>
        <span className={`text-sm font-mono ${scoreColor(item.score)}`}>
          {item.score ?? '?'}/10
        </span>
        <h3 className="flex-1 text-white font-medium leading-snug">{item.title}</h3>
      </div>

      {(item.stars != null || item.downloads != null) && (
        <div className="flex gap-4 text-xs text-zinc-400 mb-2 ml-1 font-mono">
          {item.stars != null && <span>⭐ {item.stars.toLocaleString()}</span>}
          {item.downloads != null && <span>⬇ {item.downloads.toLocaleString()}</span>}
          {item.language && <span className="text-zinc-500">{item.language}</span>}
        </div>
      )}

      {item.comment && (
        <p className="text-sm text-zinc-300 italic border-l-2 border-debi-primary/40 pl-3 my-2">
          {item.comment}
        </p>
      )}

      {item.summary && (
        <p className="text-xs text-zinc-500 mt-2 line-clamp-2">{item.summary}</p>
      )}
    </a>
  )
}

function DaySection({ feed }: { feed: DailyFeed }) {
  return (
    <section className="mb-10">
      <header className="flex items-baseline gap-3 mb-4 pb-2 border-b border-discord-light/20">
        <h2 className="text-xl font-bold text-white font-title">{feed.date}</h2>
        <span className="text-xs text-zinc-500">
          {feed.selected_count}/{feed.new_count} 선별 (raw {feed.raw_count})
        </span>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {feed.items.map((it, i) => (
          <ItemCard key={`${feed.date}-${i}`} item={it} />
        ))}
      </div>
    </section>
  )
}

export default function Feed() {
  const [feeds, setFeeds] = useState<DailyFeed[] | null>(null)
  const [auth, setAuth] = useState<'checking' | 'owner' | 'denied'>('checking')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get<{ is_owner: boolean; authenticated: boolean }>('/me/whoami')
      .then(({ data }) => {
        if (!data.authenticated) {
          window.location.href = '/api/auth/discord'
          return
        }
        setAuth(data.is_owner ? 'owner' : 'denied')
      })
      .catch(() => setAuth('denied'))
  }, [])

  useEffect(() => {
    if (auth !== 'owner') return
    api.get<{ feeds: DailyFeed[] }>('/me/feed?days=14')
      .then(({ data }) => setFeeds(data.feeds))
      .catch((err) => setError(err.message ?? '불러오기 실패'))
  }, [auth])

  if (auth === 'checking') {
    return <div className="min-h-screen flex items-center justify-center text-zinc-400">로딩...</div>
  }

  if (auth === 'denied') {
    return <Navigate to="/" replace />
  }

  return (
    <div className="min-h-screen bg-discord-darkest text-white px-4 md:px-8 py-10">
      <div className="max-w-5xl mx-auto">
        <header className="mb-8 flex items-baseline justify-between">
          <div>
            <h1 className="text-3xl font-title text-white">AI 피드</h1>
            <p className="text-sm text-zinc-400 mt-1">
              매일 09:00 KST 자동 큐레이션 · 거노 맥락 점수순
            </p>
          </div>
          <Link to="/dashboard" className="text-sm text-zinc-500 hover:text-zinc-300">
            ← 대시보드
          </Link>
        </header>

        {error && (
          <div className="bg-red-900/30 border border-red-700/40 text-red-200 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {feeds === null && !error && (
          <div className="text-zinc-400 text-center py-20">로딩...</div>
        )}

        {feeds !== null && feeds.length === 0 && (
          <div className="text-zinc-500 text-center py-20">
            아직 피드 없음. 첫 cron(매일 09:00 KST) 실행을 기다리세요.
          </div>
        )}

        {feeds?.map((f) => <DaySection key={f.date} feed={f} />)}
      </div>
    </div>
  )
}
