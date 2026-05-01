import { C, FONT_MONO } from './colors'

interface FooterProps {
  email: string
  github: string
  domain: string
  edu: string
}

export default function Footer({ email, github, domain, edu }: FooterProps) {
  return (
    <footer
      style={{
        background: C.ink,
        color: C.inverse,
        padding: '64px 48px 48px',
      }}
    >
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 32,
            marginBottom: 48,
          }}
        >
          <FooterCol label="EMAIL" value={email} href={`mailto:${email}`} />
          <FooterCol label="GITHUB" value={github.replace('https://', '')} href={github} />
          <FooterCol label="DOMAIN" value={domain.replace('https://', '')} href={domain} />
          <FooterCol label="EDU" value={edu} />
        </div>
        <div
          style={{
            paddingTop: 24,
            borderTop: `1px solid rgba(245, 250, 249, 0.15)`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 16,
            fontFamily: FONT_MONO,
            fontSize: 11,
            color: 'rgba(245, 250, 249, 0.6)',
            letterSpacing: '0.05em',
          }}
        >
          <span>© 2026 YANG GEONHO · PORTFOLIO FOR NEXON</span>
          <span>BUILT WITH REACT · TYPESCRIPT · VITE</span>
        </div>
      </div>
    </footer>
  )
}

function FooterCol({ label, value, href }: { label: string; value: string; href?: string }) {
  return (
    <div>
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 10,
          letterSpacing: '0.15em',
          color: C.honey,
          marginBottom: 8,
          fontWeight: 700,
        }}
      >
        {label}
      </div>
      {href ? (
        <a
          href={href}
          target={href.startsWith('http') ? '_blank' : undefined}
          rel={href.startsWith('http') ? 'noopener noreferrer' : undefined}
          style={{ color: C.inverse, fontSize: 14, textDecoration: 'none', borderBottom: `1px solid rgba(245, 250, 249, 0.3)` }}
        >
          {value}
        </a>
      ) : (
        <span style={{ color: C.inverse, fontSize: 14 }}>{value}</span>
      )}
    </div>
  )
}
