import { useEffect, useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { C, FONT_BODY, FONT_MONO } from './colors'

type Guild = {
  id: string
  name: string
  icon_url: string | null
  member_count: number
  online_count: number
}

const API_BASE =
  (import.meta as any).env?.VITE_API_BASE ??
  ((import.meta as any).env?.DEV ? 'http://localhost:8081' : '')

function Initials({ name }: { name: string }) {
  const ch = name.trim().charAt(0).toUpperCase() || '?'
  return (
    <div
      style={{
        width: 40,
        height: 40,
        borderRadius: 12,
        background: 'rgba(0,0,0,0.06)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: FONT_MONO,
        fontWeight: 700,
        fontSize: 16,
        color: C.ink,
        flexShrink: 0,
      }}
    >
      {ch}
    </div>
  )
}

function ServerChip({ g, compact = false }: { g: Guild; compact?: boolean }) {
  const iconSize = compact ? 26 : 40
  const radius = compact ? 8 : 12
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: compact ? 8 : 12,
        padding: compact ? '6px 12px 6px 6px' : '10px 16px 10px 10px',
        borderRadius: 999,
        background: 'rgba(255,255,255,0.78)',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(0,0,0,0.06)',
        whiteSpace: 'nowrap',
        flexShrink: 0,
      }}
    >
      {g.icon_url ? (
        <img
          src={g.icon_url}
          alt=""
          width={iconSize}
          height={iconSize}
          loading="lazy"
          style={{ borderRadius: radius, flexShrink: 0, objectFit: 'cover' }}
          onError={(e) => {
            ;(e.currentTarget as HTMLImageElement).style.display = 'none'
          }}
        />
      ) : (
        <Initials name={g.name} />
      )}
      {compact ? (
        <span style={{ fontSize: 11, fontWeight: 700, color: C.ink, lineHeight: 1.2, maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {g.name}
        </span>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <span style={{ fontSize: 13, fontWeight: 700, color: C.ink, lineHeight: 1.2, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {g.name}
          </span>
          <span style={{ fontSize: 11, fontFamily: FONT_MONO, color: C.inkSoft, marginTop: 2 }}>
            {g.member_count.toLocaleString()}명
            {g.online_count > 0 && (
              <span style={{ color: '#22c55e', marginLeft: 6 }}>● {g.online_count.toLocaleString()}</span>
            )}
          </span>
        </div>
      )}
    </div>
  )
}

export default function LiveServersMarquee({ compact = false }: { compact?: boolean } = {}) {
  const [guilds, setGuilds] = useState<Guild[] | null>(null)

  useEffect(() => {
    let alive = true
    fetch(`${API_BASE}/api/public/bot-guilds`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data) => {
        if (!alive) return
        setGuilds(data.guilds || [])
      })
      .catch(() => alive && setGuilds([]))
    return () => {
      alive = false
    }
  }, [])

  const list = useMemo(() => {
    if (!guilds || guilds.length === 0) return []
    // 너무 적으면 반복해서 마퀴 길이 채움
    const minCount = 20
    if (guilds.length >= minCount) return guilds
    const out: Guild[] = []
    while (out.length < minCount) out.push(...guilds)
    return out
  }, [guilds])

  if (!guilds) {
    return (
      <div style={{ padding: compact ? '8px 0' : '24px 0', textAlign: 'center', color: C.inkSoft, fontFamily: FONT_BODY, fontSize: compact ? 11 : 13 }}>
        지금 운영 중인 서버 불러오는 중…
      </div>
    )
  }
  if (guilds.length === 0) return null

  // duplicate for seamless loop
  const loop = [...list, ...list]
  const totalMembers = guilds.reduce((acc, g) => acc + g.member_count, 0)

  return (
    <section
      aria-label="현재 운영 중인 디스코드 서버"
      style={{
        position: 'relative',
        padding: compact ? '0' : '32px 0 36px',
        overflow: 'hidden',
        zIndex: 2,
      }}
    >
      {!compact && (
        <div
          style={{
            maxWidth: 1280,
            margin: '0 auto 16px',
            padding: '0 48px',
            display: 'flex',
            alignItems: 'baseline',
            justifyContent: 'space-between',
            gap: 16,
            flexWrap: 'wrap',
          }}
        >
          <div style={{ fontSize: 11, letterSpacing: '0.18em', fontFamily: FONT_MONO, color: C.inkSoft }}>
            NOW LIVE · {guilds.length} SERVERS
          </div>
          <div style={{ fontSize: 11, fontFamily: FONT_MONO, color: C.inkSoft }}>
            누적 멤버 {totalMembers.toLocaleString()}명 · 5분 캐시
          </div>
        </div>
      )}

      <div
        style={{
          position: 'relative',
          maskImage:
            'linear-gradient(to right, transparent 0, black 60px, black calc(100% - 60px), transparent 100%)',
          WebkitMaskImage:
            'linear-gradient(to right, transparent 0, black 60px, black calc(100% - 60px), transparent 100%)',
        }}
      >
        <motion.div
          style={{ display: 'flex', gap: compact ? 8 : 12, width: 'max-content' }}
          animate={{ x: ['0%', '-50%'] }}
          transition={{ duration: Math.max(40, loop.length * 1.2), repeat: Infinity, ease: 'linear' }}
        >
          {loop.map((g, i) => (
            <ServerChip key={`${g.id}-${i}`} g={g} compact={compact} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}
