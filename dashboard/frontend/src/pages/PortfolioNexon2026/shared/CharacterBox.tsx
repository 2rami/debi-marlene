import { motion } from 'framer-motion'
import { C, FONT_BODY, FONT_DISPLAY } from './colors'
import frozenshaUrl from '../../../assets/portfolio-nexon-2026/frozensha.png'
import serenUrl from '../../../assets/portfolio-nexon-2026/seren.gif'

interface Character {
  name: string
  server: string
  job: string
  level: number
  experience: string
  achievement?: { title: string; sub: string }
  rankings?: readonly { label: string; value: string }[]
  combatPower?: { character: string; union: string; unionRank: string }
  endgame?: readonly { slot: string; item: string }[]
  metrics?: readonly { label: string; value: string }[]
}

/**
 * 박스 wrap 제거. 큰 캐릭터 이미지 + 라인 구분 텍스트.
 */
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
      style={{ position: 'relative' }}
    >
      {/* 큰 캐릭터 이미지 — 박스/그림자 없이 */}
      <div
        style={{
          width: '100%',
          aspectRatio: '1 / 1',
          maxWidth: 540,
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <img
          id="character-painting"
          src={frozenshaUrl}
          alt={character.name}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            imageRendering: 'pixelated',
          }}
        />
      </div>

      {/* 정체성 라벨 — 이미지 바로 아래, 라인만 */}
      <div
        style={{
          marginTop: 32,
          paddingTop: 24,
          borderTop: `1px solid ${C.cardBorder}`,
        }}
      >
        <div
          style={{
            fontFamily: FONT_BODY,
            fontSize: 11,
            letterSpacing: '0.22em',
            color: C.nexonBlue,
            fontWeight: 800,
            textTransform: 'uppercase',
            marginBottom: 10,
          }}
        >
          Maplestory · {character.server}
        </div>
        <div
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(32px, 3.6vw, 44px)',
            fontWeight: 800,
            lineHeight: 1.05,
            letterSpacing: '-0.025em',
            color: C.ink,
          }}
        >
          {character.name}
        </div>
        <div
          style={{
            fontSize: 14,
            color: C.inkSoft,
            marginTop: 10,
            fontWeight: 600,
            letterSpacing: '-0.005em',
          }}
        >
          {character.job} · Lv.{character.level} · {character.experience}
        </div>
      </div>

      {/* 하드 세렌 achievement — 다크 인셋 라인 (박스 톤 줄임) */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.6, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
        style={{
          marginTop: 24,
          paddingTop: 24,
          borderTop: `1px solid ${C.cardBorder}`,
          display: 'grid',
          gridTemplateColumns: '88px 1fr auto',
          gap: 20,
          alignItems: 'center',
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
          <img
            src={serenUrl}
            alt="Hard Seren"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        </div>

        <div style={{ minWidth: 0 }}>
          <div
            style={{
              fontFamily: FONT_BODY,
              fontSize: 10.5,
              letterSpacing: '0.22em',
              color: C.nexonBlue,
              fontWeight: 800,
              textTransform: 'uppercase',
              marginBottom: 6,
            }}
          >
            Endgame Achievement
          </div>
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
          <div
            style={{
              fontSize: 12.5,
              color: C.inkMuted,
              marginTop: 3,
              fontWeight: 600,
            }}
          >
            {ach.sub}
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end',
            gap: 4,
          }}
        >
          <span
            style={{
              fontFamily: FONT_BODY,
              fontSize: 10,
              letterSpacing: '0.18em',
              color: C.inkMuted,
              fontWeight: 800,
              textTransform: 'uppercase',
            }}
          >
            Cleared
          </span>
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
      </motion.div>
    </motion.div>
  )
}
