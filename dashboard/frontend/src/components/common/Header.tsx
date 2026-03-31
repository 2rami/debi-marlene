import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useState } from 'react'
import PatchNotesModal from './PatchNotesModal'
import BubbleMenu from './BubbleMenu'
import LOGO from '../../assets/images/profile.jpg'

export default function Header() {
  const { user, login, logout } = useAuth()
  const navigate = useNavigate()
  const [showPatchNotes, setShowPatchNotes] = useState(false)

  const menuItems = [
    {
      label: 'Home',
      href: '#',
      ariaLabel: 'Home',
      rotation: -6,
      hoverStyles: { bgColor: '#3cabc9', textColor: '#ffffff' },
      onClick: () => navigate('/'),
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
    {
      label: 'Portfolio',
      href: '#',
      ariaLabel: 'Portfolio',
      rotation: 4,
      hoverStyles: { bgColor: '#3cabc9', textColor: '#ffffff' },
      onClick: () => navigate('/portfolio'),
    },
    {
      label: 'New',
      href: '#',
      ariaLabel: 'Patch Notes',
      rotation: -5,
      hoverStyles: { bgColor: '#f472b6', textColor: '#ffffff' },
      onClick: () => setShowPatchNotes(true),
    },
  ]

  const logoElement = (
    <img src={LOGO} alt="Debi & Marlene" className="w-full h-full object-cover rounded-full" />
  )

  return (
    <>
      <BubbleMenu
        logo={logoElement}
        items={menuItems}
        menuAriaLabel="Toggle navigation"
        menuBg="rgba(255, 255, 255, 0.85)"
        menuContentColor="#374151"
        useFixedPosition={true}
        animationEase="back.out(1.5)"
        animationDuration={0.5}
        staggerDelay={0.1}
      />
      <PatchNotesModal isOpen={showPatchNotes} onClose={() => setShowPatchNotes(false)} />
    </>
  )
}
