import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import SectionShell from '../shared/SectionShell'
import ArchitectureDiagram from '../shared/ArchitectureDiagram'
import { C, FONT_MONO, FONT_BODY, FONT_DISPLAY } from '../shared/colors'
import { ARCHITECTURE } from '../content/llm'

gsap.registerPlugin(ScrollTrigger)

/**
 * CH 2 — WHAT
 * 02 ARCHITECTURE : 다이어그램 + 클릭 evidence
 * 03 OTHER       : 다이어그램 밖 인프라 — 매거진 풍 stagger reveal 스택 카드
 */
export default function Ch2What() {
  return (
    <>
      <ArchitectureDiagram steps={ARCHITECTURE.steps} title={ARCHITECTURE.title} />

      <SectionShell
        id="tech"
        ch="CH 2"
        no="03"
        kicker="OTHER · 다이어그램 밖 운영 인프라"
        title="이 봇을 굴리는 나머지 시스템"
        variant="aside"
        background={C.bgSoft}
      >
        <StackList items={STACK} />
      </SectionShell>
    </>
  )
}

type StackItem = {
  category: string  // 카테고리 (kicker)
  headline: string  // 한 줄 요약 (큰 글자)
  chips: string[]   // 기술 chip 묶음
}

const STACK: StackItem[] = [
  {
    category: 'LLM · 폴백 백엔드',
    headline: 'Modal Gemma4 LoRA — CHAT_BACKEND 스위치 한 줄로 교체',
    chips: ['Modal', 'Gemma4', 'LoRA', 'CHAT_BACKEND=modal'],
  },
  {
    category: 'LLM · Daily Feed',
    headline: 'Sonnet curator + GitHub Actions cron(정각 회피 47분)',
    chips: ['claude-sonnet-4-6', 'GitHub Actions', 'cron', 'Smol AI/HN/HF'],
  },
  {
    category: 'VOICE · 음성 파이프라인',
    headline: 'DAVE 복호화 → VAD → Qwen3.5-Omni STT → CosyVoice3 TTS',
    chips: ['discord-ext-voice-recv', 'webrtcvad', 'Qwen3.5-Omni', 'CosyVoice3'],
  },
  {
    category: 'INFRA · 스토리지',
    headline: 'Firestore 3컬렉션 + GCS — feed_seen 30d TTL 자동 정리',
    chips: ['Firestore', 'GCS', 'settings·feed_seen·daily_feeds'],
  },
  {
    category: 'INFRA · 컴퓨트 / 컨테이너',
    headline: 'GCP VM · Cloud Run · Modal — Docker 3컨테이너 분리',
    chips: ['GCP VM', 'Cloud Run', 'Modal', 'Docker', 'unified·solo×2'],
  },
  {
    category: 'INFRA · 시크릿 / 도메인',
    headline: 'GCP Secret Manager 단일 출처 + Cloudflare 캐시',
    chips: ['Secret Manager', '.env 3종', 'Cloudflare', 'debimarlene.com'],
  },
  {
    category: 'FRONTEND · 대시보드',
    headline: 'React 18 + Vite + TypeScript + Tailwind',
    chips: ['React 18', 'Vite', 'TypeScript', 'Tailwind'],
  },
  {
    category: 'FRONTEND · 웹패널',
    headline: 'Vite + vite-plugin-pwa (PWA 캐시)',
    chips: ['Vite', 'vite-plugin-pwa', 'Service Worker'],
  },
]

function StackList({ items }: { items: StackItem[] }) {
  const wrapRef = useRef<HTMLOListElement>(null)

  useEffect(() => {
    const el = wrapRef.current
    if (!el) return
    const rows = el.querySelectorAll('.stack-row')
    const ctx = gsap.context(() => {
      gsap.fromTo(
        rows,
        { opacity: 0, y: 28 },
        {
          opacity: 1,
          y: 0,
          duration: 0.65,
          ease: 'power3.out',
          stagger: 0.07,
          scrollTrigger: {
            trigger: el,
            start: 'top bottom-=10%',
            once: true,
          },
        },
      )
    }, el)
    return () => ctx.revert()
  }, [])

  return (
    <ol
      ref={wrapRef}
      style={{
        listStyle: 'none',
        margin: 0,
        padding: 0,
        display: 'flex',
        flexDirection: 'column',
        borderTop: `1px solid ${C.cardBorder}`,
      }}
    >
      {items.map((item, i) => (
        <StackRow key={item.category} item={item} index={i} />
      ))}
    </ol>
  )
}

function StackRow({ item, index }: { item: StackItem; index: number }) {
  return (
    <li
      className="stack-row"
      style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(56px, 84px) minmax(0, 1fr)',
        gap: 'clamp(20px, 3vw, 40px)',
        padding: '24px 0',
        borderBottom: `1px solid ${C.cardBorder}`,
        position: 'relative',
        cursor: 'default',
      }}
      onMouseEnter={(e) => {
        const num = e.currentTarget.querySelector<HTMLElement>('.stack-num')
        const head = e.currentTarget.querySelector<HTMLElement>('.stack-head')
        if (num) num.style.color = C.nexonBlue
        if (head) head.style.color = C.nexonBlue
      }}
      onMouseLeave={(e) => {
        const num = e.currentTarget.querySelector<HTMLElement>('.stack-num')
        const head = e.currentTarget.querySelector<HTMLElement>('.stack-head')
        if (num) num.style.color = C.cardBorder
        if (head) head.style.color = C.ink
      }}
    >
      <span
        className="stack-num"
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 'clamp(28px, 3.4vw, 44px)',
          fontWeight: 800,
          lineHeight: 1,
          color: C.cardBorder,
          letterSpacing: '-0.04em',
          transition: 'color 220ms ease',
        }}
      >
        {String(index + 1).padStart(2, '0')}
      </span>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            fontWeight: 800,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
            color: C.nexonBlue,
          }}
        >
          {item.category}
        </div>
        <div
          className="stack-head"
          style={{
            fontFamily: FONT_BODY,
            fontSize: 'clamp(17px, 1.6vw, 20px)',
            fontWeight: 600,
            lineHeight: 1.45,
            color: C.ink,
            letterSpacing: '-0.01em',
            wordBreak: 'keep-all',
            transition: 'color 220ms ease',
          }}
        >
          {item.headline}
        </div>
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 6,
            marginTop: 4,
          }}
        >
          {item.chips.map((chip) => (
            <span
              key={chip}
              style={{
                fontFamily: FONT_MONO,
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: '0.04em',
                color: C.inkSoft,
                background: C.bgWhite,
                border: `1px solid ${C.cardBorder}`,
                padding: '4px 10px',
                borderRadius: 999,
                whiteSpace: 'nowrap',
              }}
            >
              {chip}
            </span>
          ))}
        </div>
      </div>
    </li>
  )
}
