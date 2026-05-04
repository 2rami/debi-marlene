import { useEffect, useState } from 'react'
import { C, FONT_BODY, FONT_DISPLAY, FONT_MONO } from './shared/colors'

/**
 * 메이플 캐릭터 모션 카탈로그 (정확한 enum 기준)
 * — NEXON Open API character/look 엔드포인트 W/E/A 코드 전체 미리보기.
 * — enum 출처: SpiralMoon/maplestory.openapi (kms/character_image.py)
 * — 라우트: /portfolio/nexon/maple-motions
 *
 * 사용:
 *   1. 카드 클릭 → 코드(W01, E03 등) 클립보드 복사 + sticky 패널에 합성 미리보기.
 *   2. Walk Cycle 비교 섹션에서 wmotion별 다리 움직임 차이 비교.
 *   3. 골랐으면 shared/MapleChatbot.tsx 의 POSE 테이블에 반영.
 */

const NEXON_LOOK_BASE = 'https://open.api.nexon.com/static/maplestory/character/look'

const DEFAULT_HASH =
  'MDJEJPMDEMDJHNEBBNNMJECMFOIONCHJIBOCJJPBFCKNKIGKBBENDHPPFHLIDKILPPFEBOKAIFAAKEJLHEFKOHJLCMDDILIMKIMBGIMEHGCPBKLEPJLPEDJJNJJCAGDEJHMAAOGLLFGLBMMHDNCPPFLPPCPACKODADBBKKEGDIGMKDHJALDIDBOBMGMPMKNJMJNENGMFMPONCFMLNIDJMFAHPNKMBCPEILEMDIDFDFBHNAPPHMPEKIMKNCJAOOIB'

const BASE = { wmotion: 'W00', emotion: 'E00', action: 'A00' }

interface CodeEntry {
  code: string
  name: string
  ko: string
}

// W00~W04 — 무기 종류 (전신 모션 아님)
const W_CODES: CodeEntry[] = [
  { code: 'W00', name: 'Default', ko: '기본' },
  { code: 'W01', name: 'OneHand', ko: '한손 무기' },
  { code: 'W02', name: 'TwoHands', ko: '양손 무기' },
  { code: 'W03', name: 'Gun', ko: '총' },
  { code: 'W04', name: 'Nothing', ko: '무기 없음' },
]

// E00~E24 — 표정
const E_CODES: CodeEntry[] = [
  { code: 'E00', name: 'Default', ko: '기본' },
  { code: 'E01', name: 'Wink', ko: '윙크' },
  { code: 'E02', name: 'Smile', ko: '미소' },
  { code: 'E03', name: 'Cry', ko: '눈물' },
  { code: 'E04', name: 'Angry', ko: '분노' },
  { code: 'E05', name: 'Bewildered', ko: '당황' },
  { code: 'E06', name: 'Blink', ko: '눈깜빡' },
  { code: 'E07', name: 'Blaze', ko: '활활' },
  { code: 'E08', name: 'Bowing', ko: '인사' },
  { code: 'E09', name: 'Cheers', ko: '환호' },
  { code: 'E10', name: 'Chu', ko: '뽀뽀' },
  { code: 'E11', name: 'Dam', ko: '댐' },
  { code: 'E12', name: 'Despair', ko: '절망' },
  { code: 'E13', name: 'Glitter', ko: '반짝' },
  { code: 'E14', name: 'Hit', ko: '맞음' },
  { code: 'E15', name: 'Hot', ko: '더위' },
  { code: 'E16', name: 'Hum', ko: '흥얼' },
  { code: 'E17', name: 'Love', ko: '사랑' },
  { code: 'E18', name: 'Oops', ko: '아차' },
  { code: 'E19', name: 'Pain', ko: '아픔' },
  { code: 'E20', name: 'Troubled', ko: '곤란' },
  { code: 'E21', name: 'QBlue', ko: '?파랑' },
  { code: 'E22', name: 'Shine', ko: '빛남' },
  { code: 'E23', name: 'Stunned', ko: '멍' },
  { code: 'E24', name: 'Vomit', ko: '구토' },
]

// A00~A41 — 동작 (걷기/대기/공격모션 등)
const A_CODES: CodeEntry[] = [
  { code: 'A00', name: 'Stand1', ko: '대기 1' },
  { code: 'A01', name: 'Stand2', ko: '대기 2' },
  { code: 'A02', name: 'Walk1', ko: '걷기 1' },
  { code: 'A03', name: 'Walk2', ko: '걷기 2' },
  { code: 'A04', name: 'Prone', ko: '엎드림' },
  { code: 'A05', name: 'Fly', ko: '비행' },
  { code: 'A06', name: 'Jump', ko: '점프' },
  { code: 'A07', name: 'Sit', ko: '앉기' },
  { code: 'A08', name: 'Ladder', ko: '사다리' },
  { code: 'A09', name: 'Rope', ko: '로프' },
  { code: 'A10', name: 'Heal', ko: '힐' },
  { code: 'A11', name: 'Alert', ko: '경계' },
  { code: 'A12', name: 'ProneStab', ko: '엎드려찌르기' },
  { code: 'A13', name: 'SwingO1', ko: '한손휘둘 1' },
  { code: 'A14', name: 'SwingO2', ko: '한손휘둘 2' },
  { code: 'A15', name: 'SwingO3', ko: '한손휘둘 3' },
  { code: 'A16', name: 'SwingOF', ko: '한손휘둘 F' },
  { code: 'A17', name: 'SwingP1', ko: '봉휘둘 1' },
  { code: 'A18', name: 'SwingP2', ko: '봉휘둘 2' },
  { code: 'A19', name: 'SwingPF', ko: '봉휘둘 F' },
  { code: 'A20', name: 'SwingT1', ko: '양손휘둘 1' },
  { code: 'A21', name: 'SwingT2', ko: '양손휘둘 2' },
  { code: 'A22', name: 'SwingT3', ko: '양손휘둘 3' },
  { code: 'A23', name: 'SwingTF', ko: '양손휘둘 F' },
  { code: 'A24', name: 'StabO1', ko: '한손찌르기 1' },
  { code: 'A25', name: 'StabO2', ko: '한손찌르기 2' },
  { code: 'A26', name: 'StabOF', ko: '한손찌르기 F' },
  { code: 'A27', name: 'StabT1', ko: '양손찌르기 1' },
  { code: 'A28', name: 'StabT2', ko: '양손찌르기 2' },
  { code: 'A29', name: 'StabTF', ko: '양손찌르기 F' },
  { code: 'A30', name: 'Shoot1', ko: '슈팅 1' },
  { code: 'A31', name: 'Shoot2', ko: '슈팅 2' },
  { code: 'A32', name: 'ShootF', ko: '슈팅 F' },
  { code: 'A33', name: 'Dead', ko: '죽음' },
  { code: 'A34', name: 'GhostWalk', ko: '유령걷기' },
  { code: 'A35', name: 'GhostStand', ko: '유령대기' },
  { code: 'A36', name: 'GhostJump', ko: '유령점프' },
  { code: 'A37', name: 'GhostProneStab', ko: '유령엎드림찌름' },
  { code: 'A38', name: 'GhostLadder', ko: '유령사다리' },
  { code: 'A39', name: 'GhostRope', ko: '유령로프' },
  { code: 'A40', name: 'GhostFly', ko: '유령비행' },
  { code: 'A41', name: 'GhostSit', ko: '유령앉기' },
]

// 현재 MapleChatbot에서 사용 중인 코드 — 카드 하단에 표시
const CURRENT_USE: Record<string, string> = {
  W00: 'idle base',
  W01: '★ walk · talk · drag',
  W02: 'thinking',
  E00: 'idle · walk',
  E01: 'talk',
  E02: 'drag',
  E03: 'thinking',
  A00: 'idle',
  A01: 'thinking',
  A02: '★ walk1',
  A03: '★ walk2',
  A05: 'drag',
  A06: 'talk',
}

function buildUrl(hash: string, override: Partial<typeof BASE>) {
  const p = { ...BASE, ...override }
  return `${NEXON_LOOK_BASE}/${hash}?wmotion=${p.wmotion}&emotion=${p.emotion}&action=${p.action}`
}

// ──────────────────────────────────────────
// Card
// ──────────────────────────────────────────
interface CardProps {
  entry: CodeEntry
  url: string
  selected: boolean
  onClick: () => void
}

function Card({ entry, url, selected, onClick }: CardProps) {
  const [broken, setBroken] = useState(false)
  const note = CURRENT_USE[entry.code]

  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 10,
        padding: 16,
        background: selected ? C.nexonBlue : C.bgWhite,
        border: `1px solid ${selected ? C.nexonBlue : C.cardBorder}`,
        borderRadius: 10,
        cursor: 'pointer',
        transition: 'transform 120ms ease, box-shadow 120ms ease',
        boxShadow: selected ? '0 8px 24px rgba(0, 60, 255, 0.18)' : 'none',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
      }}
    >
      <div
        style={{
          width: 100,
          height: 100,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: selected ? 'rgba(255,255,255,0.12)' : C.bgSoft,
          borderRadius: 6,
        }}
      >
        {broken ? (
          <span style={{ fontSize: 28, color: selected ? '#fff' : C.inkMuted, opacity: 0.4 }}>
            ✕
          </span>
        ) : (
          <img
            src={url}
            alt={entry.code}
            onError={() => setBroken(true)}
            style={{ maxWidth: '100%', maxHeight: '100%', imageRendering: 'pixelated', transform: 'scale(1.5)' }}
          />
        )}
      </div>
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 13,
          fontWeight: 800,
          color: selected ? '#fff' : C.ink,
          letterSpacing: '0.06em',
        }}
      >
        {entry.code}
      </div>
      <div
        style={{
          fontFamily: FONT_BODY,
          fontSize: 11,
          color: selected ? 'rgba(255,255,255,0.9)' : C.inkSoft,
          textAlign: 'center',
          fontWeight: 600,
        }}
      >
        {entry.ko}
      </div>
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 9,
          color: selected ? 'rgba(255,255,255,0.65)' : C.inkMuted,
          letterSpacing: '0.04em',
        }}
      >
        {entry.name}
      </div>
      {note && (
        <div
          style={{
            marginTop: 4,
            padding: '2px 8px',
            background: selected ? 'rgba(255,255,255,0.18)' : 'rgba(0,60,255,0.08)',
            color: selected ? '#fff' : C.nexonBlue,
            fontSize: 9,
            fontFamily: FONT_MONO,
            letterSpacing: '0.05em',
            borderRadius: 999,
            fontWeight: 700,
          }}
        >
          {note}
        </div>
      )}
    </button>
  )
}

// ──────────────────────────────────────────
// Walk Cycle 비교 — walk1 4프레임 vs walk2 4프레임 (각각 분리)
// 실제 채택: walk1 만 사용 (walk2 는 팔 자세 끊김)
// ──────────────────────────────────────────
const WALK1_FRAMES = [
  { action: 'A02.0', label: 'walk1.0' },
  { action: 'A02.1', label: 'walk1.1' },
  { action: 'A02.2', label: 'walk1.2' },
  { action: 'A02.3', label: 'walk1.3' },
]
const WALK2_FRAMES = [
  { action: 'A03.0', label: 'walk2.0' },
  { action: 'A03.1', label: 'walk2.1' },
  { action: 'A03.2', label: 'walk2.2' },
  { action: 'A03.3', label: 'walk2.3' },
]
const WALK_FRAME_MS = 130

function WalkRow({
  title,
  frames,
  frameIdx,
  active,
  badge,
}: {
  title: string
  frames: { action: string; label: string }[]
  frameIdx: number
  active: boolean
  badge?: string
}) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          color: active ? C.nexonBlue : C.inkMuted,
          letterSpacing: '0.18em',
          marginBottom: 10,
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}
      >
        {title}
        {badge && (
          <span
            style={{
              padding: '2px 8px',
              background: C.nexonBlue,
              color: '#fff',
              borderRadius: 999,
              fontSize: 9,
              letterSpacing: '0.1em',
              fontWeight: 800,
            }}
          >
            {badge}
          </span>
        )}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
        {frames.map((f, i) => (
          <div
            key={f.action}
            style={{
              padding: 12,
              background: active && i === frameIdx ? C.nexonBlue : C.bgWhite,
              border: `1px solid ${
                active && i === frameIdx ? C.nexonBlue : C.cardBorder
              }`,
              borderRadius: 10,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 8,
              opacity: active ? 1 : 0.55,
              transition: 'all 120ms ease',
            }}
          >
            <div
              style={{
                width: 110,
                height: 110,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background:
                  active && i === frameIdx ? 'rgba(255,255,255,0.12)' : C.bgSoft,
                borderRadius: 6,
              }}
            >
              <img
                src={buildUrl(DEFAULT_HASH, { wmotion: 'W00', action: f.action })}
                alt={f.action}
                style={{
                  maxWidth: '100%',
                  maxHeight: '100%',
                  imageRendering: 'pixelated',
                  transform: 'scale(1.5)',
                }}
              />
            </div>
            <div
              style={{
                fontFamily: FONT_MONO,
                fontSize: 11,
                fontWeight: 800,
                color: active && i === frameIdx ? '#fff' : C.ink,
                letterSpacing: '0.04em',
              }}
            >
              {f.label}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function WalkCycleCompare() {
  const [frameIdx, setFrameIdx] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setFrameIdx((i) => (i + 1) % 4)
    }, WALK_FRAME_MS)
    return () => clearInterval(id)
  }, [])

  return (
    <section style={{ marginBottom: 80 }}>
      <header style={{ marginBottom: 24, paddingBottom: 16, borderBottom: `2px solid ${C.ink}` }}>
        <h2
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 28,
            fontWeight: 800,
            color: C.ink,
            margin: '0 0 8px',
            letterSpacing: '-0.02em',
          }}
        >
          🚶 Walk Cycle — walk1 / walk2 분리 비교
        </h2>
        <p style={{ fontSize: 14, color: C.inkSoft, margin: 0, lineHeight: 1.6 }}>
          NEXON API <code style={{ fontFamily: FONT_MONO }}>action=A02.{'{0~3}'}</code> frame 분리 지원.
          walk2 는 walk1 과 팔 자세가 달라서 둘을 합치면 cycle 끊김 → <strong>walk1 4프레임만 사용</strong>.
          ({WALK_FRAME_MS}ms · live frame {frameIdx})
        </p>
      </header>

      <WalkRow
        title="WALK1 (A02.0~3) — 채택"
        frames={WALK1_FRAMES}
        frameIdx={frameIdx}
        active
        badge="USED"
      />

      <WalkRow
        title="WALK2 (A03.0~3) — 미사용 (팔 끊김 비교용)"
        frames={WALK2_FRAMES}
        frameIdx={frameIdx}
        active={false}
      />

      {/* wmotion 5종 × walk1 4프레임 cycle 라이브 */}
      <div style={{ marginTop: 28 }}>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            color: C.inkMuted,
            letterSpacing: '0.18em',
            marginBottom: 10,
            fontWeight: 700,
          }}
        >
          LIVE WALK1 CYCLE (wmotion 5종 동시 재생)
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 16 }}>
          {W_CODES.map((w) => {
            const action = WALK1_FRAMES[frameIdx].action
            const url = buildUrl(DEFAULT_HASH, { wmotion: w.code, action })
            return (
              <div
                key={w.code}
                style={{
                  padding: 16,
                  background: C.bgWhite,
                  border: `1px solid ${C.cardBorder}`,
                  borderRadius: 10,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <div
                  style={{
                    width: 140,
                    height: 140,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: C.bgSoft,
                    borderRadius: 8,
                  }}
                >
                  <img
                    src={url}
                    alt={`${w.code}-${action}`}
                    style={{
                      maxWidth: '100%',
                      maxHeight: '100%',
                      imageRendering: 'pixelated',
                      transform: 'scale(1.8)',
                    }}
                  />
                </div>
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 13,
                    fontWeight: 800,
                    color: C.ink,
                    letterSpacing: '0.06em',
                  }}
                >
                  {w.code}
                </div>
                <div
                  style={{
                    fontFamily: FONT_BODY,
                    fontSize: 11,
                    color: C.inkSoft,
                    textAlign: 'center',
                    fontWeight: 600,
                  }}
                >
                  {w.ko}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

// ──────────────────────────────────────────
// Section
// ──────────────────────────────────────────
interface SectionProps {
  title: string
  desc: string
  entries: CodeEntry[]
  buildOverride: (code: string) => Partial<typeof BASE>
  selected: string | null
  onSelect: (code: string) => void
}

function Section({ title, desc, entries, buildOverride, selected, onSelect }: SectionProps) {
  return (
    <section style={{ marginBottom: 80 }}>
      <header style={{ marginBottom: 24, paddingBottom: 16, borderBottom: `2px solid ${C.ink}` }}>
        <h2
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 28,
            fontWeight: 800,
            color: C.ink,
            margin: '0 0 8px',
            letterSpacing: '-0.02em',
          }}
        >
          {title}
        </h2>
        <p style={{ fontSize: 14, color: C.inkSoft, margin: 0, lineHeight: 1.6 }}>{desc}</p>
      </header>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: 12,
        }}
      >
        {entries.map((entry) => (
          <Card
            key={entry.code}
            entry={entry}
            url={buildUrl(DEFAULT_HASH, buildOverride(entry.code))}
            selected={selected === entry.code}
            onClick={() => {
              onSelect(entry.code)
              navigator.clipboard?.writeText(entry.code).catch(() => {})
            }}
          />
        ))}
      </div>
    </section>
  )
}

// ──────────────────────────────────────────
// Page
// ──────────────────────────────────────────
export default function PageMotionCatalog() {
  const [selectedW, setSelectedW] = useState<string | null>(null)
  const [selectedE, setSelectedE] = useState<string | null>(null)
  const [selectedA, setSelectedA] = useState<string | null>(null)

  const composedUrl =
    selectedW || selectedE || selectedA
      ? buildUrl(DEFAULT_HASH, {
          wmotion: selectedW ?? BASE.wmotion,
          emotion: selectedE ?? BASE.emotion,
          action: selectedA ?? BASE.action,
        })
      : null

  return (
    <div
      style={{
        fontFamily: FONT_BODY,
        background: C.bgLight,
        minHeight: '100vh',
        padding: '64px clamp(24px, 5vw, 80px)',
        color: C.ink,
      }}
    >
      <div style={{ maxWidth: 1480, margin: '0 auto' }}>
        <header style={{ marginBottom: 64 }}>
          <div
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              letterSpacing: '0.22em',
              color: C.nexonBlue,
              fontWeight: 800,
              marginBottom: 12,
            }}
          >
            MAPLE MOTION CATALOG · 정확한 enum 기준
          </div>
          <h1
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(36px, 4vw, 56px)',
              fontWeight: 800,
              color: C.ink,
              margin: '0 0 16px',
              letterSpacing: '-0.03em',
              lineHeight: 1.1,
            }}
          >
            걷기·표정·동작 미리보기
          </h1>
          <p style={{ fontSize: 16, color: C.inkSoft, lineHeight: 1.7, maxWidth: 760, margin: 0 }}>
            NEXON Open API <code style={{ fontFamily: FONT_MONO }}>character/look</code> 의 모든 W/E/A 코드입니다.
            wmotion(W) = 무기 종류 5종, emotion(E) = 표정 25종, action(A) = 동작 42종 (걷기 / 점프 / 공격 / 유령 등).
            ★ 표시는 현재 <code style={{ fontFamily: FONT_MONO }}>MapleChatbot</code> 에서 사용 중인 코드.
          </p>
        </header>

        {/* 합성 미리보기 — sticky */}
        <div
          style={{
            position: 'sticky',
            top: 24,
            zIndex: 10,
            marginBottom: 48,
            padding: 20,
            background: C.bgWhite,
            border: `2px solid ${C.ink}`,
            borderRadius: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 24,
            boxShadow: '0 12px 32px rgba(0,0,0,0.08)',
          }}
        >
          <div
            style={{
              width: 120,
              height: 120,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: C.bgSoft,
              borderRadius: 8,
              flexShrink: 0,
            }}
          >
            {composedUrl ? (
              <img
                src={composedUrl}
                alt="composed"
                style={{ maxWidth: '100%', maxHeight: '100%', imageRendering: 'pixelated', transform: 'scale(1.6)' }}
              />
            ) : (
              <span style={{ fontSize: 11, color: C.inkMuted, textAlign: 'center', padding: 8, lineHeight: 1.5 }}>
                아래에서<br />하나씩 골라봐
              </span>
            )}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.2em', marginBottom: 8 }}>
              SELECTED
            </div>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {[
                { label: 'wmotion', value: selectedW, setter: setSelectedW },
                { label: 'emotion', value: selectedE, setter: setSelectedE },
                { label: 'action', value: selectedA, setter: setSelectedA },
              ].map((row) => (
                <div
                  key={row.label}
                  style={{
                    padding: '8px 14px',
                    background: row.value ? C.nexonBlue : C.bgSoft,
                    color: row.value ? '#fff' : C.inkMuted,
                    borderRadius: 6,
                    fontFamily: FONT_MONO,
                    fontSize: 13,
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <span style={{ opacity: 0.7, fontSize: 10 }}>{row.label}</span>
                  <span>{row.value ?? '—'}</span>
                  {row.value && (
                    <button
                      onClick={() => row.setter(null)}
                      style={{
                        background: 'rgba(255,255,255,0.25)',
                        border: 'none',
                        color: '#fff',
                        width: 18,
                        height: 18,
                        borderRadius: '50%',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 11,
                        padding: 0,
                      }}
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <WalkCycleCompare />

        <Section
          title="01. wmotion · 무기 종류 (5종)"
          desc="W00 Default · W01 OneHand · W02 TwoHands · W03 Gun · W04 Nothing. 한 손 무기(W01)면 무기가 다리 가릴 수 있어요."
          entries={W_CODES}
          buildOverride={(code) => ({ wmotion: code })}
          selected={selectedW}
          onSelect={setSelectedW}
        />

        <Section
          title="02. emotion · 표정 (25종)"
          desc="E00 Default ~ E24 Vomit. 윙크/미소/눈물/사랑/멍 등. 동작은 기본(W00, A00)으로 고정."
          entries={E_CODES}
          buildOverride={(code) => ({ emotion: code })}
          selected={selectedE}
          onSelect={setSelectedE}
        />

        <Section
          title="03. action · 동작 (42종)"
          desc="A00 Stand1 ~ A41 GhostSit. 걷기·점프·공격모션·유령상태 등. wmotion·표정은 기본으로 고정."
          entries={A_CODES}
          buildOverride={(code) => ({ action: code })}
          selected={selectedA}
          onSelect={setSelectedA}
        />

        <footer
          style={{
            marginTop: 80,
            paddingTop: 32,
            borderTop: `1px solid ${C.cardBorder}`,
            fontSize: 12,
            color: C.inkMuted,
            lineHeight: 1.7,
          }}
        >
          반영하려면 <code style={{ fontFamily: FONT_MONO, color: C.nexonBlue }}>shared/MapleChatbot.tsx</code> 의
          <code style={{ fontFamily: FONT_MONO, color: C.nexonBlue }}> POSE</code> 테이블에서 원하는 상태(idle, talk, walk1 등)의
          wmotion / emotion / action 값을 여기서 고른 코드로 바꾸세요. enum 출처:{' '}
          <a
            href="https://github.com/SpiralMoon/maplestory.openapi/blob/master/python/maplestory_openapi/api/common/enum/character_image.py"
            target="_blank"
            rel="noreferrer"
            style={{ color: C.nexonBlue, fontFamily: FONT_MONO }}
          >
            SpiralMoon/maplestory.openapi
          </a>
        </footer>
      </div>
    </div>
  )
}
