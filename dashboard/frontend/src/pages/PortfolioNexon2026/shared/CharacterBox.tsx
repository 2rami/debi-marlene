import { C, FONT_MONO } from './colors'

interface Character {
  name: string
  server: string
  job: string
  level: number
  experience: string
  rankings: readonly { label: string; value: string }[]
  combatPower: { character: string; union: string; unionRank: string }
  endgame: readonly { slot: string; item: string }[]
  metrics: readonly { label: string; value: string }[]
}

export default function CharacterBox({ character }: { character: Character }) {
  return (
    <div
      style={{
        background: 'linear-gradient(145deg, #ffffff 0%, #f0f4f8 100%)',
        borderRadius: 28,
        padding: 40,
        boxShadow: C.cardShadow,
        border: `1px solid ${C.cardBorder}`,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Decorative accent blob */}
      <div
        style={{
          position: 'absolute',
          top: -100,
          right: -100,
          width: 250,
          height: 250,
          borderRadius: '50%',
          background: C.lime,
          opacity: 0.15,
          filter: 'blur(40px)',
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: -80,
          left: -80,
          width: 200,
          height: 200,
          borderRadius: '50%',
          background: C.nexonBlue,
          opacity: 0.1,
          filter: 'blur(40px)',
          pointerEvents: 'none',
        }}
      />

      {/* 메인 헤더 */}
      <div style={{ position: 'relative', display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 32, flexWrap: 'wrap' }}>
        <span
          style={{
            fontFamily: FONT_MONO,
            fontSize: 12,
            letterSpacing: '0.15em',
            color: C.nexonBlue,
            fontWeight: 800,
            background: 'rgba(0, 98, 223, 0.08)',
            padding: '6px 14px',
            borderRadius: 999,
          }}
        >
          MAPLESTORY · {character.server.toUpperCase()}
        </span>
        <span style={{ flex: 1, height: 2, background: 'rgba(0, 98, 223, 0.05)', minWidth: 40, borderRadius: 2 }} />
        <span style={{ fontFamily: FONT_MONO, fontSize: 12, color: C.inkMuted, letterSpacing: '0.05em', fontWeight: 600 }}>
          {character.experience}
        </span>
      </div>

      <div
        style={{
          position: 'relative',
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
          gap: 32,
          marginBottom: 36,
        }}
      >
        {/* 좌: 닉네임 + 직업 + 레벨 */}
        <div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em', marginBottom: 8, fontWeight: 700 }}>
            CHARACTER
          </div>
          <div style={{ fontSize: 40, fontWeight: 900, color: C.ink, lineHeight: 1.1, letterSpacing: '-0.02em' }}>
            {character.name}
          </div>
          <div style={{ fontSize: 16, color: C.nexonBlue, marginTop: 8, fontWeight: 700 }}>
            {character.job} · <span style={{ color: C.inkSoft }}>Lv.{character.level}</span>
          </div>
        </div>

        {/* 우: 랭킹 */}
        <div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em', marginBottom: 8, fontWeight: 700 }}>
            RANKINGS
          </div>
          <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8 }}>
            {character.rankings.map((r) => (
              <li
                key={r.label}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: 14,
                  fontWeight: 600,
                  background: 'rgba(255,255,255,0.6)',
                  padding: '6px 12px',
                  borderRadius: 8,
                }}
              >
                <span style={{ color: C.inkSoft }}>{r.label}</span>
                <span style={{ fontFamily: FONT_MONO, fontWeight: 800, color: C.ink, fontVariantNumeric: 'tabular-nums' }}>
                  {r.value}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Combat Power */}
      <div
        style={{
          position: 'relative',
          background: C.bgWhite,
          borderRadius: 20,
          padding: '24px 28px',
          marginBottom: 36,
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 24,
          boxShadow: '0 4px 16px rgba(0,0,0,0.03)',
          border: `1px solid rgba(0, 98, 223, 0.06)`,
        }}
      >
        <CPItem label="캐릭터 전투력" value={character.combatPower.character} color={C.coral} />
        <CPItem label="유니온 전투력" value={character.combatPower.union} color={C.yellow} />
        <CPItem label="유니온 등급" value={character.combatPower.unionRank} color={C.lavender} />
      </div>

      <div style={{ position: 'relative', display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 32 }}>
        {/* Endgame Gear */}
        <div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em', marginBottom: 16, fontWeight: 700 }}>
            ENDGAME GEAR
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {character.endgame.map((g) => (
              <div
                key={g.slot}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: 14,
                  paddingBottom: 8,
                  borderBottom: `1px dashed rgba(0, 0, 0, 0.08)`,
                }}
              >
                <span style={{ color: C.inkSoft, fontWeight: 500 }}>{g.slot}</span>
                <span style={{ color: C.ink, fontWeight: 700 }}>{g.item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Metrics */}
        <div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em', marginBottom: 16, fontWeight: 700 }}>
            ENDGAME METRICS
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 10 }}>
            {character.metrics.map((m) => (
              <div
                key={m.label}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'rgba(0, 98, 223, 0.04)',
                  borderRadius: 12,
                  padding: '12px 16px',
                  border: '1px solid rgba(0, 98, 223, 0.05)',
                }}
              >
                <div style={{ fontSize: 13, color: C.inkSoft, fontWeight: 600 }}>{m.label}</div>
                <div style={{ fontSize: 16, fontWeight: 800, color: C.nexonBlue, fontVariantNumeric: 'tabular-nums' }}>
                  {m.value}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function CPItem({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
        <div style={{ fontSize: 12, color: C.inkMuted, fontWeight: 600 }}>{label}</div>
      </div>
      <div style={{ fontSize: 18, fontWeight: 800, color: C.ink, lineHeight: 1.2 }}>{value}</div>
    </div>
  )
}
