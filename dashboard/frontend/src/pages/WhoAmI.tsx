import { useCallback, useEffect, useState } from 'react'
import type { MouseEvent, ReactNode, SVGProps } from 'react'
import './whoami.css'
import mapleUrl from '../assets/games/maplestory-poster.jpg'
import erUrl from '../assets/games/eternal-return-poster.jpg'
import owUrl from '../assets/games/overwatch-poster.jpg'
import scUrl from '../assets/games/starcraft-box.jpg'
import wowUrl from '../assets/games/wow.png'
import loaUrl from '../assets/games/lostark-poster.jpg'
import zutoBannerUrl from '../assets/whoami/subculture-zutomayo-banner.jpg'
import zutoLiveUrl from '../assets/whoami/subculture-zutomayo-live.jpg'
import snowboardUrl from '../assets/whoami/snowboard.jpg'
import shotDebiUrl from '../assets/whoami/proj-debimarlene.png'
import shotKasaUrl from '../assets/whoami/proj-kasaterm.png'
import shotAiUrl from '../assets/whoami/proj-aipipeline.png'

/**
 * Goenho 자기소개 — 공개 라우트 /whoami. 사이트 전역 스타일/테마와 격리된
 * self-contained 슬라이드 덱 (.whoami-root 스코프 + 로컬 테마 + 키보드/클릭 네비).
 */

const REDUCE =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

/* ---------- nexon maple character (same one that powers the nexon portfolio chatbot) ---------- */
const NEXON_LOOK_BASE = 'https://open.api.nexon.com/static/maplestory/character/look'
const MAPLE_HASH =
  'MDJEJPMDEMDJHNEBBNNMJECMFOIONCHJIBOCJJPBFCKNKIGKBBENDHPPFHLIDKILPPFEBOKAIFAAKEJLHEFKOHJLCMDDILIMKIMBGIMEHGCPBKLEPJLPEDJJNJJCAGDEJHMAAOGLLFGLBMMHDNCPPFLPPCPACKODADBBKKEGDIGMKDHJALDIDBOBMGMPMKNJMJNENGMFMPONCFMLNIDJMFAHPNKMBCPEILEMDIDFDFBHNAPPHMPEKIMKNCJAOOIB'
const mapleWalkUrl = (frame: number) =>
  `${NEXON_LOOK_BASE}/${MAPLE_HASH}?wmotion=W01&emotion=E00&action=A02.${frame}`
const mapleIdleUrl = () =>
  `${NEXON_LOOK_BASE}/${MAPLE_HASH}?wmotion=W00&emotion=E00&action=A00`

/* ---------- icons ---------- */
type IcoProps = SVGProps<SVGSVGElement> & { children: ReactNode; fill?: string }
function Ico({ children, fill = 'none', ...rest }: IcoProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill={fill}
      stroke={fill === 'none' ? 'currentColor' : 'none'}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...rest}
    >
      {children}
    </svg>
  )
}

const IconPin = () => (<Ico><path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7z" /><circle cx="12" cy="9" r="2.5" /></Ico>)
const IconCal = () => (<Ico><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M3 9h18M8 4v5" /></Ico>)
const IconBranch = () => (<Ico><path d="M4 17l6-6-6-6M12 19h8" /></Ico>)
const IconArrowUR = () => (<Ico><path d="M7 17L17 7M9 7h8v8" /></Ico>)
const IconArrowR = () => (<Ico><path d="M5 12h14M13 6l6 6-6 6" /></Ico>)
const IconMail = () => (<Ico><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 7l9 6 9-6" /></Ico>)
const IconGlobe = () => (<Ico><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" /></Ico>)
const IconGithub = () => (<Ico fill="currentColor"><path d="M12 2C6.5 2 2 6.6 2 12.3c0 4.5 2.9 8.3 6.8 9.7.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.4-3.4-1.4-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.6 2.4 1.1 3 .8.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.7 1a9.4 9.4 0 0 1 5 0c1.9-1.3 2.7-1 2.7-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9v2.8c0 .3.2.6.7.5 3.9-1.4 6.8-5.2 6.8-9.7C22 6.6 17.5 2 12 2z" /></Ico>)
const IconSun = () => (<Ico><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></Ico>)
const IconMoon = () => (<Ico><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" /></Ico>)

/* ---------- data ---------- */
type Project = { idx: string; name: string; status: string; live: boolean; href: string; cta: string; desc: string; tags: string[]; shot: string; shotAlt: string }
type Contact = { label: string; href: string; icon: ReactNode; text: string; external: boolean }

const PHRASES = [
  '디자인하는 개발자',
  '혼자 제품을 끝까지 만드는 사람',
  'AI로 아이디어를 물건으로',
  'design × development × AI',
]

const NAV: { id: string; label: string }[] = [
  { id: 'hero', label: 'whoami' },
  { id: 'about', label: 'about' },
  { id: 'projects', label: 'projects' },
  { id: 'stack', label: 'stack' },
  { id: 'games', label: 'games' },
  { id: 'contact', label: 'contact' },
]
const N = NAV.length

const PROJECTS: Project[] = [
  {
    idx: '01', name: 'Debi & Marlene', status: 'live · in use', live: true,
    href: 'https://debimarlene.com', cta: 'visit',
    desc: '실제 유저가 매일 쓰는 디스코드 봇. 캐릭터와 대화하고, 목소리(TTS)로 답하고, 이미지까지 생성해요. 기획·프론트·백엔드·배포·운영까지 전부 혼자.',
    tags: ['Python', 'discord.py', 'TTS', 'image-gen', 'Docker', 'GCP'],
    shot: shotDebiUrl, shotAlt: '디스코드에서 실행 중인 Debi & Marlene 봇 화면',
  },
  {
    idx: '02', name: 'kasaterm', status: 'rust · desktop', live: false,
    href: 'https://github.com/2rami', cta: 'github',
    desc: '여러 AI 세션을 한 화면에서 오케스트레이션하는 터미널 UI. Rust로 처음부터 짰고, 크로스플랫폼 빌드와 자동 업데이트까지 붙였어요. 매일 제 작업 환경 그 자체.',
    tags: ['Rust', 'React', 'WebView', 'cross-platform', 'CI/CD'],
    shot: shotKasaUrl, shotAlt: '여러 세션이 한 화면에서 도는 kasaterm 대시보드',
  },
  {
    idx: '03', name: 'AI creative pipeline', status: 'experiments', live: false,
    href: 'https://github.com/2rami', cta: 'github',
    desc: 'ComfyUI로 노드 그래프를 코드처럼 짜서 이미지·영상 워크플로우를 자동화하고, 뮤직비디오 같은 결과물까지 뽑아내는 개인 실험들. AI를 손에 익히는 놀이터예요.',
    tags: ['ComfyUI', 'diffusion', 'After Effects', 'automation'],
    shot: shotAiUrl, shotAlt: '직접 만든 이미지 변환 툴 화면',
  },
]

const STACK: { key: string; items: string[] }[] = [
  { key: 'build', items: ['TypeScript', 'Python', 'Rust', 'React'] },
  { key: 'design', items: ['Figma', 'UI / motion', '디자인 시스템'] },
  { key: 'ai', items: ['Claude / LLM', 'ComfyUI', 'agent harness'] },
  { key: 'ship', items: ['Docker', 'GCP', 'GitHub Actions'] },
]

const GAMES = [
  { name: '메이플스토리', img: mapleUrl },
  { name: '이터널 리턴', img: erUrl },
  { name: '오버워치', img: owUrl },
  { name: '스타크래프트', img: scUrl },
  { name: '월드 오브 워크래프트', img: wowUrl },
  { name: '로스트아크', img: loaUrl },
]

const CONTACTS: Contact[] = [
  { label: 'email', href: 'mailto:goenho0613@gmail.com', icon: <IconMail />, text: 'goenho0613@gmail.com', external: false },
  { label: 'github', href: 'https://github.com/2rami', icon: <IconGithub />, text: 'github.com/2rami', external: true },
  { label: 'web', href: 'https://debimarlene.com', icon: <IconGlobe />, text: 'debimarlene.com', external: true },
]

/* ---------- hooks ---------- */
function useTyping(phrases: string[]): string {
  const [text, setText] = useState('')
  useEffect(() => {
    if (REDUCE) { setText(phrases[0]); return }
    let pi = 0, ci = 0, deleting = false
    let timer = 0
    const tick = () => {
      const full = phrases[pi]
      setText(full.slice(0, ci))
      if (!deleting && ci < full.length) { ci++; timer = window.setTimeout(tick, 65) }
      else if (!deleting && ci === full.length) { deleting = true; timer = window.setTimeout(tick, 1700) }
      else if (deleting && ci > 0) { ci--; timer = window.setTimeout(tick, 28) }
      else { deleting = false; pi = (pi + 1) % phrases.length; timer = window.setTimeout(tick, 320) }
    }
    timer = window.setTimeout(tick, 700)
    return () => window.clearTimeout(timer)
  }, [phrases])
  return text
}

const pad = (n: number) => String(n).padStart(2, '0')

/* roaming maple character — cycles the nexon look walk frames while CSS drifts it across the floor */
function RoamingMapleChar() {
  const [frame, setFrame] = useState(0)
  useEffect(() => {
    for (let f = 0; f < 4; f++) { const im = new Image(); im.src = mapleWalkUrl(f) }
    if (REDUCE) return
    const id = window.setInterval(() => setFrame((f) => (f + 1) % 4), 150)
    return () => window.clearInterval(id)
  }, [])
  return (
    <img
      className="roam-char"
      src={REDUCE ? mapleIdleUrl() : mapleWalkUrl(frame)}
      alt="메이플 프로즌샤 — 넥슨 포트폴리오 챗봇의 그 캐릭터"
      draggable={false}
      onError={(e) => { const t = e.currentTarget; if (!t.src.includes('W00')) t.src = mapleIdleUrl() }}
    />
  )
}

/* ---------- page ---------- */
export default function WhoAmI() {
  const [light, setLight] = useState<boolean>(
    () => typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: light)').matches
  )
  const [i, setI] = useState(0)
  const [mounted, setMounted] = useState(false)
  const typed = useTyping(PHRASES)

  const go = useCallback((n: number) => setI(Math.max(0, Math.min(N - 1, n))), [])
  const next = useCallback(() => setI((p) => Math.min(N - 1, p + 1)), [])
  const prev = useCallback(() => setI((p) => Math.max(0, p - 1)), [])

  // first-paint delay so the opening slide plays its reveal transition
  useEffect(() => {
    const r = requestAnimationFrame(() => setMounted(true))
    return () => cancelAnimationFrame(r)
  }, [])

  useEffect(() => {
    const prevTitle = document.title
    document.title = 'Goenho · whoami'
    return () => { document.title = prevTitle }
  }, [])

  useEffect(() => {
    const NEXT = [' ', 'ArrowRight', 'ArrowDown', 'PageDown']
    const PREV = ['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace']
    const onKey = (e: KeyboardEvent) => {
      if (NEXT.includes(e.key)) { e.preventDefault(); next() }
      else if (PREV.includes(e.key)) { e.preventDefault(); prev() }
      else if (e.key === 'Home') { e.preventDefault(); go(0) }
      else if (e.key === 'End') { e.preventDefault(); go(N - 1) }
      else if (/^[1-9]$/.test(e.key)) { const n = Number(e.key) - 1; if (n < N) { e.preventDefault(); go(n) } }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [next, prev, go])

  // click empty deck area to advance; links/buttons keep their own behavior
  const onDeckClick = (e: MouseEvent<HTMLDivElement>) => {
    if ((e.target as HTMLElement).closest('a, button')) return
    next()
  }

  const cls = (idx: number) => 'slide' + (mounted && i === idx ? ' active' : '')

  return (
    <div className="whoami-root" data-wa={light ? 'light' : 'dark'}>
      <div className="deck-progress" style={{ width: `${((i + 1) / N) * 100}%` }} />

      <div className="topbar">
        <span className="brand"><span className="dot-live" /><b>goenho</b>&nbsp;· self-intro</span>
        <button className="theme-toggle" onClick={() => setLight((v) => !v)} aria-label="테마 전환">
          {light ? <IconMoon /> : <IconSun />}
          <span>{light ? 'dark' : 'light'}</span>
        </button>
      </div>

      <nav className="navdots">
        {NAV.map((n, idx) => (
          <button key={n.id} data-label={n.label} className={i === idx ? 'active' : ''} aria-label={n.label} onClick={() => go(idx)} />
        ))}
      </nav>

      <div className="deck" onClick={onDeckClick}>
        <div className="track" style={{ transform: `translateX(-${i * 100}%)` }}>

          {/* HERO */}
          <div className={cls(0)} id="hero">
            <div className="wrap">
              <div className="prompt reveal"><span className="sig">~/sionic</span> <span className="cmd">$</span> whoami</div>
              <h1 className="hero-name reveal" data-d="1">Goenho<span className="surname">.</span></h1>
              <div className="typed-wrap reveal" data-d="2"><span className="typed">{typed}</span><span className="caret" /></div>
              <div className="hero-meta reveal" data-d="3">
                <span><IconPin />Seoul</span>
                <span><IconCal />2026.07 — Sionic AI</span>
                <span><IconBranch />design × dev × AI</span>
              </div>
            </div>
          </div>

          {/* ABOUT */}
          <div className={cls(1)} id="about">
            <div className="wrap">
              <div className="eyebrow reveal">01 — about</div>
              <h2 className="reveal" data-d="1">경계에서 혼자<br />끝까지 만드는 사람.</h2>
              <div className="about-body">
                <p className="reveal" data-d="2">
                  디자인과 개발 사이 어딘가에서 일해요. 화면을 그리고, 그걸 직접 코드로 옮기고,
                  서버에 올려서 <strong>실제 사용자에게 닿는 데까지</strong> 혼자 끌고 가는 걸 좋아합니다.
                </p>
                <p className="reveal" data-d="2">
                  요즘은 AI를 그림 도구가 아니라 <strong>제품을 완성시키는 파이프라인</strong>으로 씁니다.
                  디스코드 봇부터 터미널 UI, 크리에이티브 워크플로우까지 —
                  아이디어를 붙잡으면 어떻게든 돌아가는 물건으로 만들어내는 게 재미예요.
                  특히 <strong>여러 개의 에이전트가 한 화면에서 동시에 돌아가는 걸 구경할 때</strong>가 제일 짜릿하고요.
                </p>
                <p className="reveal" data-d="3">
                  그리고 오늘, 그 방식을 제대로 해보려고 <strong>Sionic AI</strong>에 합류했습니다.
                </p>
              </div>
              <div className="facts reveal" data-d="3">
                <span className="fact"><b>2rami</b> on github</span>
                <span className="fact">first job · <b>AI-Native</b></span>
                <span className="fact">solo builder</span>
                <span className="fact">ship &gt; perfect</span>
              </div>
              <div className="about-gallery reveal" data-d="4">
                <figure className="about-photo">
                  <img src={zutoBannerUrl} alt="ZUTOMAYO 서울 공연 현장" loading="lazy" draggable={false} />
                  <figcaption>ZUTOMAYO · 서울</figcaption>
                </figure>
                <figure className="about-photo">
                  <img src={zutoLiveUrl} alt="ZUTOMAYO 공연 관람" loading="lazy" draggable={false} />
                  <figcaption>라이브 · 응원봉</figcaption>
                </figure>
                <figure className="about-photo">
                  <img src={snowboardUrl} alt="스노보드 타는 Goenho" loading="lazy" draggable={false} />
                  <figcaption>겨울엔 · 스노보드</figcaption>
                </figure>
              </div>
            </div>
          </div>

          {/* PROJECTS */}
          <div className={cls(2)} id="projects">
            <div className="wrap">
              <div className="eyebrow reveal">02 — what i build</div>
              <h2 className="reveal" data-d="1">혼자 만든 것들.</h2>
              <div className="proj-list">
                {PROJECTS.map((p, idx) => (
                  <a key={p.idx} className="proj reveal" data-d={Math.min(idx + 1, 3)} href={p.href} target="_blank" rel="noopener noreferrer">
                    <figure className="proj-shot">
                      <img src={p.shot} alt={p.shotAlt} loading="lazy" draggable={false} />
                    </figure>
                    <div className="proj-body">
                      <div className="proj-head">
                        <span className="idx">{p.idx}</span>
                        <h3>{p.name}</h3>
                        <span className={'status' + (p.live ? ' live' : '')}>{p.status}</span>
                      </div>
                      <p className="desc">{p.desc}</p>
                      <div className="tags">{p.tags.map((t) => <span key={t}>{t}</span>)}</div>
                    </div>
                    <span className="go">{p.cta}<IconArrowUR /></span>
                  </a>
                ))}
              </div>
            </div>
          </div>

          {/* STACK */}
          <div className={cls(3)} id="stack">
            <div className="wrap">
              <div className="eyebrow reveal">03 — toolbox</div>
              <h2 className="reveal" data-d="1">이걸로 만들어요.</h2>
              <div className="stack-grid">
                {STACK.map((c, idx) => (
                  <div className="stack-col reveal" data-d={Math.min(idx + 1, 4)} key={c.key}>
                    <h3><span className="k">~/</span>{c.key}</h3>
                    <ul>{c.items.map((it) => <li key={it}>{it}</li>)}</ul>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* GAMES — 관심사 선언 + 정적 게임 그리드 + 배회하는 넥슨 챗봇 캐릭터 */}
          <div className={cls(4)} id="games">
            <div className="wrap">
              <div className="eyebrow reveal">04 — off the clock</div>
              <h2 className="reveal" data-d="1">화면 밖에선.</h2>
              <p className="interest-lead reveal" data-d="2">
                일 안 할 땐 <strong>터미널이랑 dotfiles로 작업 공간을 직접 만들고 꾸미거나</strong>,
                <strong> 게임</strong>하거나, <strong>서브컬쳐</strong>를 파요. 관심사는 늘 이 셋으로 돌아옵니다.
              </p>
              <div className="game-eyebrow reveal" data-d="3">즐겨온 게임들</div>
              <ul className="game-grid reveal" data-d="3">
                {GAMES.map((g) => (
                  <li className="game-poster" key={g.name}>
                    <img src={g.img} alt={g.name} loading="lazy" draggable={false} />
                    <span>{g.name}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="roam-stage" aria-hidden="true">
              <RoamingMapleChar />
            </div>
          </div>

          {/* CONTACT */}
          <div className={cls(5)} id="contact">
            <div className="wrap">
              <div className="eyebrow reveal">05 — say hi</div>
              <h2 className="reveal" data-d="1">잘 부탁드립니다.</h2>
              <p className="lead reveal" data-d="2" style={{ marginTop: 18 }}>
                궁금한 거 있으면 언제든 말 걸어주세요. 같이 뭔가 만드는 거 좋아합니다.
              </p>
              <div className="hi-tip reveal" data-d="2">
                <span className="tip-k">친해지는 꿀팁</span>
                <span className="tip-v">편하게 대해주세요. 그거면 충분해요.</span>
              </div>
              <div className="contact-lines reveal" data-d="2">
                {CONTACTS.map((c) => (
                  <a
                    key={c.label}
                    className="cline"
                    href={c.href}
                    {...(c.external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
                  >
                    <span className="label">{c.label}</span>
                    <span className="val">{c.icon}{c.text}</span>
                    <span className="arrow"><IconArrowR /></span>
                  </a>
                ))}
              </div>
              <footer>
                <span>© 2026 Goenho</span>
                <span>space · ← → 로 이동</span>
              </footer>
            </div>
          </div>

        </div>
      </div>

      <div className="deck-nav">
        <button onClick={prev} disabled={i === 0} aria-label="이전 슬라이드">←</button>
        <span className="counter">{pad(i + 1)} / {pad(N)}</span>
        <button onClick={next} disabled={i === N - 1} aria-label="다음 슬라이드">→</button>
      </div>
    </div>
  )
}
