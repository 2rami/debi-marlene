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
        background: C.inverse,
        borderRadius: 16,
        padding: 40,
        boxShadow: C.cardShadow,
        border: `1px solid rgba(26, 43, 71, 0.06)`,
      }}
    >
      {/* 메인 헤더 */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 32, flexWrap: 'wrap' }}>
        <span
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            letterSpacing: '0.15em',
            color: C.honey,
            fontWeight: 700,
          }}
        >
          MAPLESTORY · {character.server.toUpperCase()}
        </span>
        <span style={{ flex: 1, height: 1, background: 'rgba(26, 43, 71, 0.1)', minWidth: 40 }} />
        <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.05em' }}>
          {character.experience}
        </span>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
          gap: 32,
          marginBottom: 32,
        }}
      >
        {/* 좌: 닉네임 + 직업 + 레벨 */}
        <div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em', marginBottom: 8 }}>
            CHARACTER
          </div>
          <div style={{ fontSize: 36, fontWeight: 800, color: C.ink, lineHeight: 1.1, letterSpacing: '-0.02em' }}>
            {character.name}
          </div>
          <div style={{ fontSize: 14, color: C.inkSoft, marginTop: 8 }}>
            {character.job} · Lv.{character.level}
          </div>
        </div>

        {/* 우: 랭킹 */}
        <div>
          <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em', marginBottom: 8 }}>
            RANKINGS
          </div>
          <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
            {character.rankings.map((r) => (
              <li
                key={r.label}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: 14,
                  color: C.ink,
                  fontWeight: 500,
                }}
              >
                <span style={{ color: C.inkMuted }}>{r.label}</span>
                <span style={{ fontFamily: FONT_MONO, fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
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
          background: C.cream,
          borderRadius: 12,
          padding: '20px 24px',
          marginBottom: 32,
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 24,
        }}
      >
        <CPItem label="캐릭터 전투력" value={character.combatPower.character} />
        <CPItem label="유니온 전투력" value={character.combatPower.union} />
        <CPItem label="유니온 등급" value={character.combatPower.unionRank} />
      </div>

      {/* Endgame Gear */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em', marginBottom: 12 }}>
          ENDGAME GEAR
        </div>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '8px 24px',
          }}
        >
          {character.endgame.map((g) => (
            <div
              key={g.slot}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: 13,
                paddingBottom: 6,
                borderBottom: `1px dotted rgba(26, 43, 71, 0.15)`,
              }}
            >
              <span style={{ color: C.inkMuted }}>{g.slot}</span>
              <span style={{ color: C.ink, fontWeight: 600 }}>{g.item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Metrics */}
      <div>
        <div style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.1em', marginBottom: 12 }}>
          ENDGAME METRICS
        </div>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 12,
          }}
        >
          {character.metrics.map((m) => (
            <div
              key={m.label}
              style={{
                background: 'rgba(232, 220, 192, 0.3)',
                borderRadius: 8,
                padding: '12px 16px',
              }}
            >
              <div style={{ fontSize: 11, color: C.inkMuted, marginBottom: 4 }}>{m.label}</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: C.ink, fontVariantNumeric: 'tabular-nums' }}>
                {m.value}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function CPItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div style={{ fontSize: 11, color: C.inkMuted, marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 15, fontWeight: 700, color: C.ink, lineHeight: 1.3 }}>{value}</div>
    </div>
  )
}
