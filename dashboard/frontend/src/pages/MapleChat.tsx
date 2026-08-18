import { useCallback, useEffect, useRef, useState } from 'react'
import MapleChatbot, { API_BASE } from './PortfolioNexon2026/shared/MapleChatbot'
import { C, FONT_BODY, FONT_DISPLAY } from './PortfolioNexon2026/shared/colors'

const NICK_KEY = 'maple-chat-nickname'

interface CharInfo {
  name: string
  hash: string
  world?: string
  job?: string
  level?: number
}

/**
 * 공유용 단독 챗봇 페이지. 포폴 본문 없이 캐릭터만 돌아다닌다.
 *
 * hash 를 넘기지 않으면 MapleChatbot 이 기본 캐릭터로 뜬다 — 넥슨 키가 없거나
 * 검색에 실패해도 페이지가 빈 채로 남지 않도록 조회 결과는 덧씌우기만 한다.
 */
export default function MapleChat() {
  const [nick, setNick] = useState('')
  const [char, setChar] = useState<CharInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const lookup = useCallback(async (raw: string) => {
    const name = raw.trim()
    if (!name || loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(
        `${API_BASE}/api/portfolio/maple/character?name=${encodeURIComponent(name)}`
      )
      const body = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(body?.reason || '캐릭터를 불러오지 못했습니다.')
        return
      }
      setChar(body as CharInfo)
      localStorage.setItem(NICK_KEY, name)
    } catch {
      setError('연결에 실패했습니다. 잠시 후 다시 시도해 주세요.')
    } finally {
      setLoading(false)
    }
  }, [loading])

  // 마지막으로 본 캐릭터를 다시 띄운다 — 링크를 받은 사람이 매번 치지 않도록
  useEffect(() => {
    const saved = localStorage.getItem(NICK_KEY)
    if (saved) {
      setNick(saved)
      lookup(saved)
    }
    // 최초 1회만 — lookup 은 loading 에 따라 재생성되므로 deps 에 넣지 않는다
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const meta = char
    ? [char.world, char.job, char.level ? `Lv.${char.level}` : null].filter(Boolean).join(' · ')
    : null

  return (
    <div
      style={{
        minHeight: '100dvh',
        background: `linear-gradient(180deg, ${C.bgWhite} 0%, ${C.bgLight} 55%, ${C.bgSoft} 100%)`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '18vh 24px 0',
        fontFamily: FONT_BODY,
        overflow: 'hidden',
      }}
    >
      <h1
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 'clamp(22px, 4.6vw, 34px)',
          color: C.ink,
          margin: 0,
          letterSpacing: '-0.02em',
          textAlign: 'center',
        }}
      >
        {char ? char.name : '메이플 캐릭터'}
      </h1>

      <p
        style={{
          marginTop: 10,
          marginBottom: 28,
          fontSize: 14,
          color: C.inkMuted,
          textAlign: 'center',
          lineHeight: 1.6,
          minHeight: 22,
        }}
      >
        {meta || '닉네임을 넣으면 그 캐릭터가 화면을 돌아다녀요'}
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          lookup(nick)
        }}
        style={{ display: 'flex', gap: 8, width: '100%', maxWidth: 380 }}
      >
        <input
          ref={inputRef}
          value={nick}
          onChange={(e) => setNick(e.target.value)}
          placeholder="메이플 닉네임"
          maxLength={12}
          spellCheck={false}
          style={{
            flex: 1,
            minWidth: 0,
            height: 46,
            padding: '0 16px',
            fontSize: 15,
            fontFamily: FONT_BODY,
            color: C.ink,
            background: C.cardBg,
            border: `1px solid ${C.cardBorder}`,
            borderRadius: C.radiusSm,
            outline: 'none',
            boxShadow: C.cardShadow,
          }}
        />
        <button
          type="submit"
          disabled={loading || !nick.trim()}
          style={{
            height: 46,
            padding: '0 20px',
            fontSize: 15,
            fontWeight: 600,
            fontFamily: FONT_BODY,
            color: C.inverse,
            background: loading || !nick.trim() ? C.inkMuted : C.nexonBlue,
            border: 'none',
            borderRadius: C.radiusSm,
            cursor: loading || !nick.trim() ? 'default' : 'pointer',
            whiteSpace: 'nowrap',
            transition: 'background 160ms ease',
          }}
        >
          {loading ? '불러오는 중' : '불러오기'}
        </button>
      </form>

      <p
        style={{
          marginTop: 14,
          fontSize: 13,
          color: error ? C.nexonBlueAlt : C.inkMuted,
          textAlign: 'center',
          minHeight: 20,
        }}
      >
        {error || '캐릭터를 클릭하면 대화할 수 있어요'}
      </p>

      <MapleChatbot
        key={char?.hash ?? 'default'}
        hash={char?.hash}
        // 외형만 빌려온 것이므로 화자를 바꾸지 않는다 — 답변 지식은 그대로 양건호다
        intro={
          char
            ? `${char.name} 의 모습을 빌렸어요. 말하는 건 디지털 클론 양건호입니다. 뭐든 물어보세요.`
            : '안녕하세요! 저는 디지털 클론 양건호입니다. 뭐든 물어보세요.'
        }
      />

      <footer
        style={{
          marginTop: 'auto',
          padding: '20px 0 16px',
          fontSize: 11,
          color: C.inkMuted,
          textAlign: 'center',
        }}
      >
        Data based on NEXON Open API
      </footer>
    </div>
  )
}
