import { motion } from 'framer-motion'
import { C, FONT_MONO, FONT_DISPLAY } from './colors'

type CtaItem = {
  label: string
  href: string
  primary?: boolean
}

export default function CtaSection({
  kicker = 'CONTACT',
  headline,
  sub,
  items,
}: {
  kicker?: string
  headline: string
  sub?: string
  items: CtaItem[]
}) {
  return (
    <section
      style={{
        position: 'relative',
        background: '#070B14',
        padding: '160px clamp(48px, 8vw, 120px) 80px',
        overflow: 'hidden',
      }}
    >
      {/* aurora */}
      <div
        aria-hidden
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(60% 50% at 50% 30%, rgba(0, 98, 223, 0.22), transparent 60%), radial-gradient(50% 40% at 20% 80%, rgba(196, 240, 0, 0.10), transparent 70%), radial-gradient(50% 40% at 80% 70%, rgba(138, 95, 255, 0.18), transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* Grid pattern */}
      <div
        aria-hidden
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)',
          backgroundSize: '64px 64px',
          maskImage: 'radial-gradient(60% 50% at 50% 50%, black, transparent)',
          WebkitMaskImage: 'radial-gradient(60% 50% at 50% 50%, black, transparent)',
          pointerEvents: 'none',
        }}
      />

      <div
        style={{
          position: 'relative',
          maxWidth: 960,
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <div
            style={{
              fontFamily: FONT_MONO,
              fontSize: 12,
              letterSpacing: '0.24em',
              color: C.lime,
              fontWeight: 700,
              marginBottom: 20,
              display: 'inline-block',
              padding: '6px 14px',
              border: `1px solid rgba(196, 240, 0, 0.3)`,
              borderRadius: 999,
            }}
          >
            {kicker}
          </div>
        </motion.div>

        <motion.h2
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 'clamp(36px, 5vw, 64px)',
            fontWeight: 700,
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
            color: C.inverse,
            margin: '0 0 24px',
            background: 'linear-gradient(180deg, #FFFFFF 0%, #C8D6E5 100%)',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          {headline}
        </motion.h2>

        {sub && (
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            style={{
              fontSize: 17,
              lineHeight: 1.7,
              color: 'rgba(255,255,255,0.7)',
              margin: '0 0 48px',
              maxWidth: 640,
              marginLeft: 'auto',
              marginRight: 'auto',
              fontWeight: 700,
            }}
          >
            {sub}
          </motion.p>
        )}

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
          style={{
            display: 'flex',
            gap: 14,
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
        >
          {items.map((it) => (
            <CtaLink key={it.href} {...it} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function CtaLink({ label, href, primary }: CtaItem) {
  return (
    <motion.a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.97 }}
      transition={{ duration: 0.2 }}
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        gap: 10,
        padding: '14px 28px',
        borderRadius: 999,
        textDecoration: 'none',
        fontFamily: FONT_MONO,
        fontSize: 13,
        fontWeight: 700,
        letterSpacing: '0.04em',
        background: primary
          ? 'linear-gradient(135deg, #338AFA 0%, #8A5FFF 100%)'
          : 'rgba(255, 255, 255, 0.06)',
        color: primary ? '#FFFFFF' : 'rgba(255, 255, 255, 0.92)',
        border: primary ? '1px solid transparent' : '1px solid rgba(255, 255, 255, 0.18)',
        boxShadow: primary
          ? '0 12px 32px rgba(51, 138, 250, 0.35)'
          : '0 4px 16px rgba(0,0,0,0.2)',
        backdropFilter: 'blur(6px)',
      }}
    >
      <span>{label}</span>
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path
          d="M3 3h8v8M3 11L11 3"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </motion.a>
  )
}
