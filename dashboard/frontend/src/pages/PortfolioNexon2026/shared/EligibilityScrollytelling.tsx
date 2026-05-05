import { useEffect, useRef } from 'react'
import {
  motion,
  useMotionValue,
  useMotionValueEvent,
  useScroll,
  useTransform,
  type MotionValue,
} from 'framer-motion'
import { C, FONT_BODY, FONT_DISPLAY, FONT_MONO } from './colors'
import frozenshaUrl from '../../../assets/portfolio-nexon-2026/frozensha.png'
import serenUrl from '../../../assets/portfolio-nexon-2026/seren.gif'
import { useRevealOff } from './useRevealOff'
import { useCharacterDock } from './dockContext'

interface EligibilityData {
  body: string
}

interface CharacterAchievement {
  title: string
  sub: string
}

interface CharacterData {
  name: string
  server: string
  job: string
  level: number
  experience: string
  achievement?: CharacterAchievement
}

interface Props {
  eligibility: EligibilityData
  character: CharacterData
}

/**
 * CH 3·05 ELIGIBILITY — sticky scroll-pinned, character-anchored stage reveal.
 *
 * 우측: 프로즌샤 캐릭터 (idle bob 모션, 항상 보임)
 * 좌측: 4 stage text — Heavy User 라벨 / 메이플 + 프로즌샤 / 본문 / Endgame achievement
 * 스크롤 진행 → localPos 0..STAGES, 각 stage 가 가운데 들어오면 opacity 1
 *
 * ?reveal=off → 정적 레이아웃 (Figma 캡처용)
 */

const STAGE_VH = 500 // 한 stage 당 1.8 viewport 스크롤 — 느린 진행
const STAGES = 4
const ITEM_H = 200
const SLIDE_HEIGHT = 480
const VERTICAL_OFFSET = -36

export default function EligibilityScrollytelling({ eligibility, character }: Props) {
  const ref = useRef<HTMLDivElement>(null)
  const revealOff = useRevealOff()

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end end'],
  })

  const localPos = useMotionValue(0)
  // 첫 WARMUP 구간은 캐릭터가 도착할 시간 — localPos 0 고정.
  // 이후 [WARMUP, 1] → [0, STAGES] 로 매핑해서 좌측 텍스트 진행
  const WARMUP = 0.15
  useMotionValueEvent(scrollYProgress, 'change', (p) => {
    const adjusted = p < WARMUP ? 0 : ((p - WARMUP) / (1 - WARMUP)) * STAGES
    localPos.set(Math.max(0, Math.min(STAGES - 0.0001, adjusted)))
  })

  if (revealOff) {
    return <StaticEligibility eligibility={eligibility} character={character} />
  }

  return (
    <section
      ref={ref}
      id="eligibility"
      style={{
        position: 'relative',
        height: `${STAGES * STAGE_VH}vh`,
        background: C.bgLight,
      }}
    >
      <div
        style={{
          position: 'sticky',
          top: 0,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          padding: 'clamp(80px, 10vh, 120px) clamp(40px, 6vw, 120px)',
          overflow: 'hidden',
        }}
      >
        <Header localPos={localPos} />

        {/* 본문 — 좌 text stack / 우 캐릭터 */}
        <div
          style={{
            flex: 1,
            display: 'grid',
            gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
            gap: 'clamp(40px, 5vw, 80px)',
            alignItems: 'center',
            maxWidth: 1280,
            margin: '0 auto',
            width: '100%',
          }}
        >
          <TextStack eligibility={eligibility} character={character} localPos={localPos} />
          <DockSlot />
        </div>

        <ProgressBar localPos={localPos} />
      </div>
    </section>
  )
}

// ─────────────────────────────────────────────

function Header({ localPos }: { localPos: MotionValue<number> }) {
  const stageDisplay = useTransform(localPos, (p) =>
    String(Math.min(STAGES, Math.max(1, Math.floor(p) + 1))).padStart(2, '0'),
  )
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 32 }}>
      <span style={metaStyle(C.nexonBlue)}>CH 3 · 05</span>
      <span style={metaStyle(C.inkMuted)}>Eligibility · 지원 자격</span>
      <span style={{ flex: 1, height: 1, background: C.cardBorder }} />
      <motion.span
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          fontWeight: 700,
          color: C.inkMuted,
          letterSpacing: '0.18em',
        }}
      >
        {stageDisplay}
      </motion.span>
      <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.18em' }}>
        {' '}/ {String(STAGES).padStart(2, '0')}
      </span>
    </div>
  )
}

function metaStyle(color: string): React.CSSProperties {
  return {
    fontFamily: FONT_MONO,
    fontSize: 11,
    fontWeight: 800,
    color,
    letterSpacing: '0.22em',
    textTransform: 'uppercase',
  }
}

// ─────────────────────────────────────────────

function TextStack({
  eligibility,
  character,
  localPos,
}: {
  eligibility: EligibilityData
  character: CharacterData
  localPos: MotionValue<number>
}) {
  const ach = character.achievement ?? { title: '하드 세렌 파티 격파', sub: '어센틱/시메라 콘텐츠 정점' }

  const y = useTransform(
    localPos,
    (p) => (SLIDE_HEIGHT - ITEM_H) / 2 - p * ITEM_H + VERTICAL_OFFSET,
  )

  return (
    <div
      style={{
        position: 'relative',
        height: SLIDE_HEIGHT,
        width: '100%',
        overflow: 'hidden',
        WebkitMaskImage:
          'linear-gradient(180deg, transparent 0%, black 18%, black 82%, transparent 100%)',
        maskImage:
          'linear-gradient(180deg, transparent 0%, black 18%, black 82%, transparent 100%)',
      }}
    >
      <motion.div style={{ y, display: 'flex', flexDirection: 'column', width: '100%' }}>
        <Slot index={0} localPos={localPos}>
          <div style={metaStyle(C.nexonBlue)}>Heavy User · 16년+</div>
        </Slot>
        <Slot index={1} localPos={localPos}>
          <div>
            <div style={{ ...metaStyle(C.inkMuted), marginBottom: 12 }}>Maplestory · {character.server}</div>
            <h3
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 'clamp(32px, 4vw, 48px)',
                fontWeight: 800,
                lineHeight: 1.1,
                letterSpacing: '-0.03em',
                color: C.ink,
                margin: 0,
              }}
            >
              {character.name}
              <span style={{ color: C.nexonBlue }}> · {character.level} LV</span>
            </h3>
            <p
              style={{
                fontFamily: FONT_BODY,
                fontSize: 14,
                color: C.inkSoft,
                margin: '10px 0 0',
                fontWeight: 600,
                letterSpacing: '-0.005em',
              }}
            >
              {character.job} · {character.experience}
            </p>
          </div>
        </Slot>
        <Slot index={2} localPos={localPos}>
          <p
            style={{
              fontFamily: FONT_BODY,
              fontSize: 'clamp(14px, 1.15vw, 16px)',
              lineHeight: 1.7,
              color: C.inkSoft,
              margin: 0,
              fontWeight: 500,
              wordBreak: 'keep-all',
              maxWidth: 540,
            }}
          >
            {eligibility.body}
          </p>
        </Slot>
        <Slot index={3} localPos={localPos}>
          <AchievementCard ach={ach} />
        </Slot>
      </motion.div>
    </div>
  )
}

function Slot({
  index,
  localPos,
  children,
}: {
  index: number
  localPos: MotionValue<number>
  children: React.ReactNode
}) {
  const opacity = useTransform(localPos, (p) => {
    const d = Math.abs(p - index)
    if (d <= 0.45) return 1
    if (d >= 2) return 0.1
    return 1 - ((d - 0.45) / (2 - 0.45)) * (1 - 0.1)
  })
  return (
    <motion.div
      style={{
        height: ITEM_H,
        display: 'flex',
        alignItems: 'flex-start',
        paddingTop: 24,
        opacity,
      }}
    >
      <div style={{ width: '100%', maxWidth: 560 }}>{children}</div>
    </motion.div>
  )
}

function AchievementCard({ ach }: { ach: CharacterAchievement }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '88px 1fr auto',
        gap: 18,
        alignItems: 'center',
        paddingTop: 20,
        borderTop: `1px solid ${C.cardBorder}`,
        maxWidth: 540,
      }}
    >
      <div
        style={{
          width: 88,
          height: 88,
          borderRadius: 12,
          overflow: 'hidden',
          background: '#000',
        }}
      >
        <img src={serenUrl} alt="Hard Seren" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>
      <div style={{ minWidth: 0 }}>
        <div style={{ ...metaStyle(C.nexonBlue), marginBottom: 6 }}>Endgame Achievement</div>
        <div
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 18,
            fontWeight: 800,
            lineHeight: 1.25,
            letterSpacing: '-0.015em',
            color: C.ink,
          }}
        >
          {ach.title}
        </div>
        <div style={{ fontSize: 12.5, color: C.inkMuted, marginTop: 3, fontWeight: 600 }}>{ach.sub}</div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
        <span style={{ ...metaStyle(C.inkMuted) }}>Cleared</span>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <polyline
            points="20 6 9 17 4 12"
            stroke={C.nexonBlue}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────

/**
 * 떠다니는 MapleChatbot 캐릭터를 dock 시키기 위한 빈 슬롯.
 * IntersectionObserver 로 화면 절반 이상 보이면 dockEl=this.
 * 화면 밖이면 release.
 */
function DockSlot() {
  const ref = useRef<HTMLDivElement>(null)
  const { setDockEl, releaseDockEl } = useCharacterDock()

  useEffect(() => {
    const el = ref.current
    if (!el) return
    // 비대칭 threshold:
    //  · dock 은 슬롯이 거의 다 보일 때 (≥ 0.85) → 진입 시 캐릭터가 viewport 하단 너머로 안 꺼짐
    //  · release 는 일찍 (< 0.2) → 사용자가 빠져나가면 바로 roam 재개
    const obs = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.intersectionRatio >= 0.85) {
            setDockEl(el)
          } else if (entry.intersectionRatio < 0.2) {
            releaseDockEl(el)
          }
        }
      },
      { threshold: [0, 0.2, 0.5, 0.85, 1] },
    )
    obs.observe(el)
    return () => {
      obs.disconnect()
      releaseDockEl(el)
    }
  }, [setDockEl, releaseDockEl])

  return (
    <div
      ref={ref}
      style={{
        position: 'relative',
        width: '100%',
        height: SLIDE_HEIGHT,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* 발 그림자 — MapleChatbot dock 타겟 (slot center + 60 Y offset, scale 1.7) 발 위치에 맞춤 */}
      <span
        aria-hidden
        style={{
          position: 'absolute',
          left: '50%',
          // 슬롯 중심 + 60 + (CHAR_SIZE/2 * 1.7) ≈ slot.top + 453 (480px slot 기준 5.6% from bottom)
          bottom: '9%',
          transform: 'translateX(-50%)',
          width: 'min(220px, 50%)',
          height: 18,
          background: 'radial-gradient(closest-side, rgba(10,18,36,0.22), transparent 70%)',
          filter: 'blur(2px)',
          opacity: 0.6,
        }}
      />
    </div>
  )
}

// 정적 캡처(reveal=off) 또는 도킹 비활성 환경 fallback 용 큰 캐릭터 portrait
function CharacterPortrait({ character }: { character: CharacterData }) {
  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: SLIDE_HEIGHT,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* idle bob */}
      <motion.img
        src={frozenshaUrl}
        alt={character.name}
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 2.6, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          maxWidth: 'min(440px, 90%)',
          width: '100%',
          height: 'auto',
          objectFit: 'contain',
          imageRendering: 'pixelated',
          filter: 'drop-shadow(0 18px 28px rgba(10, 18, 36, 0.18))',
        }}
      />
      {/* 발 그림자 */}
      <span
        aria-hidden
        style={{
          position: 'absolute',
          left: '50%',
          bottom: '14%',
          transform: 'translateX(-50%)',
          width: 'min(220px, 50%)',
          height: 18,
          background: 'radial-gradient(closest-side, rgba(10,18,36,0.22), transparent 70%)',
          filter: 'blur(2px)',
        }}
      />
    </div>
  )
}

// ─────────────────────────────────────────────

function ProgressBar({ localPos }: { localPos: MotionValue<number> }) {
  return (
    <div
      style={{
        display: 'flex',
        gap: 6,
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: 24,
      }}
    >
      {Array.from({ length: STAGES }).map((_, i) => (
        <Tick key={i} index={i} localPos={localPos} />
      ))}
    </div>
  )
}

function Tick({ index, localPos }: { index: number; localPos: MotionValue<number> }) {
  const fill = useTransform(localPos, (p) => Math.max(0, Math.min(1, p - index)))
  const bg = useTransform(fill, (f) => `linear-gradient(90deg, ${C.nexonBlue} ${f * 100}%, ${C.cardBorder} ${f * 100}%)`)
  return <motion.span aria-hidden style={{ width: 28, height: 2, background: bg, display: 'block' }} />
}

// ─────────────────────────────────────────────

function StaticEligibility({
  eligibility,
  character,
}: {
  eligibility: EligibilityData
  character: CharacterData
}) {
  const ach = character.achievement ?? { title: '하드 세렌 파티 격파', sub: '어센틱/시메라 콘텐츠 정점' }
  return (
    <section
      id="eligibility"
      style={{
        background: C.bgLight,
        padding: 'clamp(80px, 10vh, 120px) clamp(40px, 6vw, 120px)',
      }}
    >
      <div
        style={{
          maxWidth: 1280,
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
          gap: 'clamp(40px, 5vw, 80px)',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 28, maxWidth: 540 }}>
          <div style={metaStyle(C.nexonBlue)}>Heavy User · 16년+</div>
          <div>
            <div style={{ ...metaStyle(C.inkMuted), marginBottom: 12 }}>Maplestory · {character.server}</div>
            <h3
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 'clamp(32px, 4vw, 48px)',
                fontWeight: 800,
                lineHeight: 1.1,
                letterSpacing: '-0.03em',
                color: C.ink,
                margin: 0,
              }}
            >
              {character.name}
              <span style={{ color: C.nexonBlue }}> · {character.level} LV</span>
            </h3>
            <p style={{ fontFamily: FONT_BODY, fontSize: 14, color: C.inkSoft, margin: '10px 0 0', fontWeight: 600 }}>
              {character.job} · {character.experience}
            </p>
          </div>
          <p
            style={{
              fontFamily: FONT_BODY,
              fontSize: 'clamp(14px, 1.15vw, 16px)',
              lineHeight: 1.7,
              color: C.inkSoft,
              margin: 0,
              fontWeight: 500,
              wordBreak: 'keep-all',
            }}
          >
            {eligibility.body}
          </p>
          <AchievementCard ach={ach} />
        </div>
        <CharacterPortrait character={character} />
      </div>
    </section>
  )
}
