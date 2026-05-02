import { motion } from 'framer-motion'
import { C, FONT_MONO } from './colors'
import frozenshaUrl from '../../../assets/portfolio-nexon-2026/frozensha.png'
import serenUrl from '../../../assets/portfolio-nexon-2026/seren.gif'

interface Character {
  name: string
  server: string
  job: string
  level: number
  experience: string
  achievement?: { title: string; sub: string }
  // 나머지 필드는 표시하지 않지만 호환성을 위해 받음
  rankings?: readonly { label: string; value: string }[]
  combatPower?: { character: string; union: string; unionRank: string }
  endgame?: readonly { slot: string; item: string }[]
  metrics?: readonly { label: string; value: string }[]
}

export default function CharacterBox({ character }: { character: Character }) {
  const ach = character.achievement ?? {
    title: '하드 세렌 파티 격파',
    sub: '어센틱/시메라 콘텐츠 정점',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      style={{
        position: 'relative',
        background: 'linear-gradient(145deg, #ffffff 0%, #f0f4f8 100%)',
        borderRadius: 28,
        padding: '40px',
        boxShadow: C.cardShadow,
        border: `1px solid ${C.cardBorder}`,
        overflow: 'hidden',
      }}
    >
      {/* Decorative blobs */}
      <div
        aria-hidden
        style={{
          position: 'absolute',
          top: -120,
          right: -120,
          width: 280,
          height: 280,
          borderRadius: '50%',
          background: C.lime,
          opacity: 0.16,
          filter: 'blur(50px)',
          pointerEvents: 'none',
        }}
      />
      <div
        aria-hidden
        style={{
          position: 'absolute',
          bottom: -80,
          left: -80,
          width: 200,
          height: 200,
          borderRadius: '50%',
          background: C.nexonBlue,
          opacity: 0.1,
          filter: 'blur(50px)',
          pointerEvents: 'none',
        }}
      />

      {/* Identity row */}
      <div
        style={{
          position: 'relative',
          display: 'grid',
          gridTemplateColumns: 'auto 1fr',
          gap: 36,
          alignItems: 'center',
          marginBottom: 32,
        }}
      >
        <motion.div
          whileHover={{ scale: 1.04 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          style={{
            width: 200,
            height: 200,
            borderRadius: 28,
            background: 'rgba(255, 255, 255, 0.85)',
            border: `1px solid ${C.cardBorder}`,
            boxShadow: '0 12px 40px rgba(0, 98, 223, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
          }}
        >
          <img
            src={frozenshaUrl}
            alt={character.name}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              imageRendering: 'pixelated',
            }}
          />
        </motion.div>

        <div>
          <div
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              letterSpacing: '0.18em',
              color: C.nexonBlue,
              fontWeight: 700,
              marginBottom: 12,
            }}
          >
            MAPLESTORY · {character.server.toUpperCase()}
          </div>
          <div
            style={{
              fontSize: 'clamp(36px, 4.5vw, 52px)',
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: '-0.025em',
              color: C.ink,
              margin: 0,
            }}
          >
            {character.name}
          </div>
          <div
            style={{
              fontSize: 15.5,
              color: C.inkSoft,
              marginTop: 12,
              fontWeight: 800,
              letterSpacing: '-0.005em',
            }}
          >
            {character.job} · Lv.{character.level} · {character.experience}
          </div>
        </div>
      </div>

      {/* Achievement: 하드 세렌 격파 */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.6, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
        style={{
          position: 'relative',
          display: 'grid',
          gridTemplateColumns: 'auto 1fr auto',
          gap: 24,
          alignItems: 'center',
          background: '#0A1224',
          borderRadius: 20,
          padding: '20px 24px',
          color: C.inverse,
          overflow: 'hidden',
          boxShadow: '0 12px 32px rgba(10, 18, 36, 0.25)',
        }}
      >
        {/* radial backdrop */}
        <div
          aria-hidden
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(40% 60% at 0% 50%, rgba(196, 240, 0, 0.18), transparent), radial-gradient(40% 60% at 100% 50%, rgba(255, 75, 75, 0.16), transparent)',
            pointerEvents: 'none',
          }}
        />

        <div
          style={{
            position: 'relative',
            width: 88,
            height: 88,
            borderRadius: 16,
            overflow: 'hidden',
            border: '1px solid rgba(255,255,255,0.15)',
            background: '#000',
            flexShrink: 0,
          }}
        >
          <img
            src={serenUrl}
            alt="Hard Seren Boss"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
        </div>

        <div style={{ position: 'relative', minWidth: 0 }}>
          <div
            style={{
              fontFamily: FONT_MONO,
              fontSize: 10.5,
              letterSpacing: '0.2em',
              color: '#C4F000',
              fontWeight: 700,
              marginBottom: 6,
            }}
          >
            ENDGAME ACHIEVEMENT
          </div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 800,
              lineHeight: 1.25,
              letterSpacing: '-0.015em',
            }}
          >
            {ach.title}
          </div>
          <div
            style={{
              fontSize: 13,
              color: 'rgba(255,255,255,0.65)',
              marginTop: 4,
              fontWeight: 700,
            }}
          >
            {ach.sub}
          </div>
        </div>

        <div
          style={{
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end',
            gap: 4,
          }}
        >
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 10,
              letterSpacing: '0.12em',
              color: 'rgba(255,255,255,0.55)',
              fontWeight: 800,
            }}
          >
            CLEARED
          </span>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <polyline
              points="20 6 9 17 4 12"
              stroke="#C4F000"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </motion.div>
    </motion.div>
  )
}
