import { motion } from 'framer-motion'
import { C, FONT_BODY, FONT_DISPLAY } from './colors'
import Button from './Button'

type CtaItem = {
  label: string
  href: string
  primary?: boolean
}

/**
 * 라이트 매거진 톤. 카드/그림자/그라디언트 0개.
 * CH 4 REACH 워드마크와 자연 연결되도록 흰 bg + 좌측 sticky 라벨 + 큰 블루 헤드라인.
 */
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
        background: C.bgWhite,
        padding: '160px clamp(40px, 6vw, 120px) 200px',
      }}
    >
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(160px, 220px) minmax(0, 1fr)',
          gap: 'clamp(32px, 5vw, 80px)',
          maxWidth: 1280,
          margin: '0 auto',
        }}
      >
        {/* 좌: sticky 라벨 */}
        <div>
          <div
            style={{
              position: 'sticky',
              top: 'clamp(120px, 14vh, 180px)',
              fontFamily: FONT_BODY,
              fontSize: 11,
              letterSpacing: '0.24em',
              fontWeight: 800,
              color: C.nexonBlue,
              textTransform: 'uppercase',
            }}
          >
            <div style={{ marginBottom: 8 }}>CH 4 / REACH.</div>
            <div style={{ color: C.inkMuted }}>{kicker}</div>
          </div>
        </div>

        {/* 우: 큰 헤드라인 + 작은 본문 + outlined CTA */}
        <div style={{ maxWidth: 760 }}>
          <motion.h2
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 'clamp(40px, 5.4vw, 78px)',
              fontWeight: 800,
              lineHeight: 1.05,
              letterSpacing: '-0.04em',
              color: C.ink,
              margin: 0,
              wordBreak: 'keep-all',
              whiteSpace: 'pre-line',
            }}
          >
            {headline}
          </motion.h2>

          {sub && (
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.6, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
              style={{
                fontFamily: FONT_BODY,
                fontSize: 16,
                lineHeight: 1.85,
                color: C.inkSoft,
                margin: '40px 0 0',
                maxWidth: 580,
                fontWeight: 500,
                wordBreak: 'keep-all',
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
              marginTop: 56,
              display: 'flex',
              gap: 10,
              flexWrap: 'wrap',
            }}
          >
            {items.map((it) => (
              <Button
                key={it.href}
                href={it.href}
                label={it.label}
                variant={it.primary ? 'primary' : 'outline'}
              />
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
