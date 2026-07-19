import { useEffect, useRef, useState } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import SectionShell from '../shared/SectionShell'
import ArchitectureDiagram from '../shared/ArchitectureDiagram'
import { C, FONT_MONO, FONT_BODY, FONT_DISPLAY } from '../shared/colors'
import { ARCHITECTURE } from '../content/frontend'

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
        kicker="STACK · 다이어그램 밖 나머지 도구"
        title="이 화면을 굴리는 나머지 스택"
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
    category: 'FRONTEND · 프레임워크',
    headline: 'React 19 + Vite + TypeScript + Tailwind — 이 페이지의 뼈대',
    chips: ['React 19', 'Vite', 'TypeScript', 'Tailwind'],
  },
  {
    category: 'FRONTEND · 스크롤·모션',
    headline: 'GSAP ScrollTrigger + Lenis + framer-motion 을 한 루프로',
    chips: ['GSAP', 'ScrollTrigger', 'Lenis', 'framer-motion'],
  },
  {
    category: 'FRONTEND · 3D·그래픽스',
    headline: 'three.js 배경 3종 + WebGL 셰이더 (섹션별 교체)',
    chips: ['three.js', 'WebGL', 'Ballpit', 'Aurora', 'Lightning'],
  },
  {
    category: 'NATIVE · GPU 터미널',
    headline: 'kasaterm — Rust 로 직접 짠 GPU 셀 렌더러',
    chips: ['Rust', 'wgpu', 'winit', 'vt100'],
  },
  {
    category: 'NATIVE · 렌더 최적화',
    headline: 'damage tracking + P3/Bradford 색 파이프라인 (1.25GB→113MB)',
    chips: ['damage tracking', 'P3', 'Bradford', 'GPU readback'],
  },
  {
    category: 'AI · 모델 연동',
    headline: 'Anthropic Managed Agent SSE 스트리밍 챗봇 (이 페이지 하단)',
    chips: ['Managed Agents', 'SSE', 'streaming'],
  },
  {
    category: 'AI · 개발 하네스',
    headline: 'MCP + hook + 서브에이전트 + LiteLLM 멀티모델 스위칭',
    chips: ['MCP', 'hook', '서브에이전트', 'LiteLLM'],
  },
  {
    category: 'INFRA · 배포',
    headline: 'PWA + Cloudflare 캐시 + GCP · Docker',
    chips: ['PWA', 'Cloudflare', 'GCP', 'Docker'],
  },
]

function StackList({ items }: { items: StackItem[] }) {
  const [expanded, setExpanded] = useState(false)
  const wrapRef = useRef<HTMLOListElement>(null)

  useEffect(() => {
    if (!expanded) return
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
          duration: 0.5,
          ease: 'power3.out',
          stagger: 0.05,
        },
      )
    }, el)
    return () => ctx.revert()
  }, [expanded])

  if (!expanded) {
    return (
      <button
        type="button"
        onClick={() => setExpanded(true)}
        style={{
          fontFamily: FONT_MONO,
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: '0.18em',
          textTransform: 'uppercase',
          color: C.nexonBlue,
          background: 'transparent',
          border: `1px solid ${C.cardBorder}`,
          padding: '14px 22px',
          borderRadius: 999,
          cursor: 'pointer',
          transition: 'background 200ms ease, border-color 200ms ease',
          alignSelf: 'flex-start',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = C.bgWhite
          e.currentTarget.style.borderColor = C.nexonBlue
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'transparent'
          e.currentTarget.style.borderColor = C.cardBorder
        }}
      >
        + 운영 인프라 {items.length}개 펼쳐 보기
      </button>
    )
  }

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
