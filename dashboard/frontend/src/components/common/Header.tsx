import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useState, useEffect } from 'react'
import PatchNotesModal from './PatchNotesModal'
import BubbleMenu from './BubbleMenu'
import CreditWalletDropdown from '../credits/CreditWalletDropdown'
import LOGO from '../../assets/images/profile.jpg'

const LATEST_PATCH_VERSION = 'beta'

export default function Header() {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { user: _user, login: _login, logout: _logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [showPatchNotes, setShowPatchNotes] = useState(false)
  const [hasUnread, setHasUnread] = useState(false)

  useEffect(() => {
    const lastRead = localStorage.getItem('patchNotes_lastRead')
    setHasUnread(lastRead !== LATEST_PATCH_VERSION)
  }, [])

  const openPatchNotes = () => {
    setShowPatchNotes(true)
    localStorage.setItem('patchNotes_lastRead', LATEST_PATCH_VERSION)
    setHasUnread(false)
  }

  const handleLogoClick = () => {
    if (location.pathname === '/landing' || location.pathname === '/') {
      const lenis = (window as any).__lenis
      if (lenis) {
        lenis.scrollTo(0, { immediate: true })
      } else {
        window.scrollTo({ top: 0 })
      }
    } else {
      navigate('/landing')
    }
  }

  const menuItems = [
    {
      label: 'Home',
      href: '#',
      ariaLabel: 'Home',
      rotation: -6,
      hoverStyles: { bgColor: '#3cabc9', textColor: '#ffffff' },
      onClick: () => navigate('/landing'),
    },
    {
      label: 'Commands',
      href: '#',
      ariaLabel: 'Commands',
      rotation: 5,
      hoverStyles: { bgColor: '#7DE8ED', textColor: '#111111' },
      onClick: () => navigate('/commands'),
    },
    {
      label: 'Docs',
      href: '#',
      ariaLabel: 'Docs',
      rotation: -4,
      hoverStyles: { bgColor: '#e58fb6', textColor: '#ffffff' },
      onClick: () => navigate('/docs'),
    },
    {
      label: 'Guide',
      href: '#',
      ariaLabel: 'Bot Guide',
      rotation: 7,
      hoverStyles: { bgColor: '#FFA6D7', textColor: '#111111' },
      onClick: () => navigate('/bot-guide'),
    },
  ]

  const logoElement = (
    <img src={LOGO} alt="Debi & Marlene" className="w-full h-full object-cover rounded-full" />
  )

  return (
    <>
      <BubbleMenu
        logo={logoElement}
        onLogoClick={handleLogoClick}
        items={menuItems}
        menuAriaLabel="Toggle navigation"
        menuBg="rgba(255, 255, 255, 0.85)"
        menuContentColor="#374151"
        useFixedPosition={true}
        animationEase="back.out(1.5)"
        animationDuration={0.5}
        staggerDelay={0.1}
      />
      {/* 종 아이콘 (패치노트) — 햄버거 메뉴 왼쪽에 배치 */}
      <button
        onClick={openPatchNotes}
        className="fixed top-8 z-[1002] w-12 h-12 md:w-14 md:h-14 rounded-full pointer-events-auto cursor-pointer hover:scale-110 transition-transform"
        style={{ right: 'calc(6% + 64px)' }}
        aria-label="Patch Notes"
      >
        <div className="absolute inset-0 rounded-full shadow-[0_4px_16px_rgba(0,0,0,0.12)]" style={{ background: 'rgba(255,255,255,0.85)', filter: 'url(#bubble-cloud)' }} />
        <div className="relative z-10 w-full h-full flex items-center justify-center">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#374151" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          {hasUnread && <span className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-[#e58fb6] rounded-full" />}
        </div>
      </button>
      <div className="fixed top-8 z-[1002] pointer-events-auto" style={{ right: 'calc(6% + 128px)' }}>
        <CreditWalletDropdown />
      </div>
      <PatchNotesModal isOpen={showPatchNotes} onClose={() => setShowPatchNotes(false)} />
    </>
  )
}
