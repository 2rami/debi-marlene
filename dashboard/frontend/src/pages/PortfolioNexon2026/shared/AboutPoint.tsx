import { motion } from 'framer-motion'
import { C, FONT_MONO } from './colors'

export default function AboutPoint({
  kicker,
  title,
  body,
}: {
  kicker: string
  title: string
  body: string
}) {
  return (
    <motion.article
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
      style={{
        position: 'relative',
        background: '#FAFCFE',
        borderRadius: 20,
        padding: '28px 28px 32px',
        border: `1px solid ${C.cardBorder}`,
        boxShadow: '0 4px 16px rgba(0, 98, 223, 0.04)',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: 4,
          height: 32,
          background: C.nexonBlue,
          borderRadius: '0 4px 4px 0',
        }}
      />
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
        {kicker}
      </div>
      <h3
        style={{
          fontSize: 19,
          fontWeight: 800,
          lineHeight: 1.35,
          color: C.ink,
          margin: '0 0 12px',
          letterSpacing: '-0.015em',
        }}
      >
        {title}
      </h3>
      <p
        style={{
          fontSize: 14,
          lineHeight: 1.65,
          color: C.inkSoft,
          margin: 0,
          fontWeight: 500,
        }}
      >
        {body}
      </p>
    </motion.article>
  )
}
