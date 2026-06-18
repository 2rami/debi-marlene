/**
 * 사이오닉 포트폴리오 얼음정령 챗봇.
 * 플로팅 캐릭터(GIF) 클릭 → 챗 패널. /api/portfolio/ask/sionic/stream SSE 스트리밍.
 * 넥슨 MapleChatbot 의 메이플 캐릭터 API/모션을 걷어내고 자캐 정적 GIF 로 간소화.
 */

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import iceSpirit from '../../../assets/images/event/ice-spirit.gif'

const FONT = "'Pretendard Variable', 'Pretendard', 'Paperlogy', -apple-system, BlinkMacSystemFont, sans-serif"
const ACCENT = '#007FF5'

type Msg = { role: 'user' | 'bot'; text: string }

const CHIPS = ['양건호가 어떤 사람이야?', 'kasaterm이 뭐야?', 'debi-marlene 소개해줘', 'AI/ML 경험 알려줘']

// **볼드** 마크다운만 간단 렌더 (나머지는 평문)
function renderRich(t: string) {
  return t.split(/(\*\*[^*]+\*\*)/g).map((p, i) =>
    p.startsWith('**') && p.endsWith('**') ? <strong key={i}>{p.slice(2, -2)}</strong> : <span key={i}>{p}</span>
  )
}

export default function SionicChatbot() {
  const [open, setOpen] = useState(false)
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: 'bot', text: '안녕하세요 ❄️ 양건호 포트폴리오에 대해 뭐든 물어보세요!' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 1e9, behavior: 'smooth' })
  }, [msgs, open])

  const send = async (text: string) => {
    const q = text.trim()
    if (!q || loading) return
    setInput('')
    setMsgs((m) => [...m, { role: 'user', text: q }, { role: 'bot', text: '' }])
    setLoading(true)
    try {
      const res = await fetch('/api/portfolio/ask/sionic/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: q }),
      })
      if (!res.body) throw new Error('no body')
      const reader = res.body.getReader()
      const dec = new TextDecoder()
      let buf = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buf += dec.decode(value, { stream: true })
        const parts = buf.split('\n\n')
        buf = parts.pop() || ''
        for (const part of parts) {
          const line = part.trim()
          if (!line.startsWith('data:')) continue
          try {
            const ev = JSON.parse(line.slice(5).trim())
            if (ev.type === 'chunk' && ev.text) {
              setMsgs((m) => {
                const c = [...m]
                c[c.length - 1] = { role: 'bot', text: c[c.length - 1].text + ev.text }
                return c
              })
            }
          } catch {
            /* 부분 JSON 무시 */
          }
        }
      }
    } catch {
      setMsgs((m) => {
        const c = [...m]
        c[c.length - 1] = { role: 'bot', text: '앗, 잠깐 문제가 생겼어요 ❄️ 다시 물어봐 주세요!' }
        return c
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* 플로팅 캐릭터 */}
      <AnimatePresence>
        {!open && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={() => setOpen(true)}
            style={{ position: 'fixed', bottom: 16, right: 16, zIndex: 150, background: 'none', border: 'none', cursor: 'pointer', padding: 0, width: 96, height: 96 }}
            aria-label="포트폴리오 챗봇 열기"
          >
            <img src={iceSpirit} alt="포트폴리오 챗봇" style={{ width: '100%', height: '100%', objectFit: 'contain', filter: `drop-shadow(0 6px 18px ${ACCENT}66)` }} />
            <span style={{ position: 'absolute', top: 2, right: 2, background: ACCENT, color: '#fff', fontFamily: FONT, fontSize: 11, fontWeight: 800, width: 20, height: 20, borderRadius: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 2px 8px ${ACCENT}66` }}>?</span>
          </motion.button>
        )}
      </AnimatePresence>

      {/* 챗 패널 */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.96 }}
            transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 151, width: 'min(380px, calc(100vw - 32px))', height: 'min(560px, calc(100vh - 90px))', background: '#fff', borderRadius: 20, boxShadow: '0 24px 70px rgba(10,18,36,0.3)', display: 'flex', flexDirection: 'column', overflow: 'hidden', border: `1px solid ${ACCENT}22` }}
          >
            {/* 헤더 */}
            <div style={{ background: `linear-gradient(135deg, ${ACCENT}, #4DA3FF)`, padding: '16px 18px', display: 'flex', alignItems: 'center', gap: 12 }}>
              <img src={iceSpirit} alt="" style={{ width: 50, height: 50, objectFit: 'contain' }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: FONT, fontSize: 15, fontWeight: 800, color: '#fff' }}>포트폴리오 안내봇</div>
                <div style={{ fontFamily: FONT, fontSize: 11.5, color: 'rgba(255,255,255,0.85)' }}>양건호 포트폴리오를 안내해요 ❄️</div>
              </div>
              <button onClick={() => setOpen(false)} aria-label="닫기" style={{ background: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: 9999, width: 30, height: 30, color: '#fff', cursor: 'pointer', fontSize: 18, lineHeight: 1 }}>×</button>
            </div>

            {/* 메시지 */}
            <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', padding: 18, display: 'flex', flexDirection: 'column', gap: 12, background: '#F4F7FB' }}>
              {msgs.map((m, i) => (
                <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '82%' }}>
                  <div style={{ fontFamily: FONT, fontSize: 14, lineHeight: 1.6, padding: '10px 14px', borderRadius: 14, wordBreak: 'keep-all', whiteSpace: 'pre-wrap', ...(m.role === 'user' ? { background: ACCENT, color: '#fff', borderBottomRightRadius: 4 } : { background: '#fff', color: '#1A2233', border: '1px solid rgba(10,18,36,0.07)', borderBottomLeftRadius: 4 }) }}>
                    {m.text ? renderRich(m.text) : (loading && i === msgs.length - 1 ? '…' : '')}
                  </div>
                </div>
              ))}
              {msgs.length === 1 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, marginTop: 4 }}>
                  {CHIPS.map((c) => (
                    <button key={c} onClick={() => send(c)} style={{ fontFamily: FONT, fontSize: 12.5, fontWeight: 600, color: ACCENT, background: '#fff', border: `1px solid ${ACCENT}44`, borderRadius: 9999, padding: '7px 12px', cursor: 'pointer' }}>{c}</button>
                  ))}
                </div>
              )}
            </div>

            {/* 입력 */}
            <div style={{ padding: '12px 14px', borderTop: '1px solid rgba(10,18,36,0.08)', display: 'flex', gap: 8, background: '#fff' }}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') send(input) }}
                placeholder="포트폴리오에 대해 물어보세요…"
                disabled={loading}
                style={{ flex: 1, fontFamily: FONT, fontSize: 14, padding: '10px 14px', borderRadius: 9999, border: '1px solid rgba(10,18,36,0.14)', outline: 'none' }}
              />
              <button onClick={() => send(input)} disabled={loading || !input.trim()} aria-label="전송" style={{ background: ACCENT, border: 'none', borderRadius: 9999, width: 42, height: 42, color: '#fff', cursor: 'pointer', flexShrink: 0, fontSize: 18, opacity: loading || !input.trim() ? 0.5 : 1 }}>↑</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
