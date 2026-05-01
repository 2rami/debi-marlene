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
        background: C.nexonBlue,
        color: C.inverse,
        padding: '80px 48px 48px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Abstract Background Shapes */}
      <div style={{ position: 'absolute', top: -50, right: -50, width: 200, height: 200, borderRadius: '50%', background: C.nexonLightBlue, opacity: 0.5, filter: 'blur(30px)' }} />
      <div style={{ position: 'absolute', bottom: -50, left: 100, width: 150, height: 150, borderRadius: '50%', background: C.lime, opacity: 0.15, filter: 'blur(40px)' }} />

      <div style={{ maxWidth: 1280, margin: '0 auto', position: 'relative', zIndex: 1 }}>
        {/* Giant Footer Title */}
        <h2 style={{ fontSize: 'clamp(40px, 8vw, 120px)', fontWeight: 900, lineHeight: 1, letterSpacing: '-0.04em', margin: '0 0 64px', opacity: 0.9 }}>
          LET'S WORK<br />TOGETHER.
        </h2>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 32,
            marginBottom: 64,
          }}
        >
          <FooterCol label="EMAIL" value={email} href={`mailto:${email}`} />
          <FooterCol label="GITHUB" value={github.replace('https://', '')} href={github} />
          <FooterCol label="DOMAIN" value={domain.replace('https://', '')} href={domain} />
          <FooterCol label="EDU" value={edu} />
        </div>
        <div
          style={{
            paddingTop: 32,
            borderTop: `1px solid rgba(255, 255, 255, 0.2)`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 16,
            fontFamily: FONT_MONO,
            fontSize: 12,
            color: 'rgba(255, 255, 255, 0.7)',
            letterSpacing: '0.05em',
            fontWeight: 600,
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
          fontSize: 11,
          letterSpacing: '0.15em',
          color: C.lime,
          marginBottom: 10,
          fontWeight: 800,
        }}
      >
        {label}
      </div>
      {href ? (
        <a
          href={href}
          target={href.startsWith('http') ? '_blank' : undefined}
          rel={href.startsWith('http') ? 'noopener noreferrer' : undefined}
          style={{
            color: C.inverse,
            fontSize: 16,
            fontWeight: 600,
            textDecoration: 'none',
            borderBottom: `2px solid rgba(255, 255, 255, 0.3)`,
            paddingBottom: 2,
            transition: 'border-color 0.2s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.borderBottomColor = C.inverse)}
          onMouseLeave={(e) => (e.currentTarget.style.borderBottomColor = 'rgba(255, 255, 255, 0.3)')}
        >
          {value}
        </a>
      ) : (
        <span style={{ color: C.inverse, fontSize: 16, fontWeight: 600 }}>{value}</span>
      )}
    </div>
  )
}
