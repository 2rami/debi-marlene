import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { motion, useScroll, useMotionValueEvent } from 'framer-motion'
import { useState } from 'react'

export default function Header() {
  const { user, login } = useAuth()
  const location = useLocation()
  const { scrollY } = useScroll()
  const [isScrolled, setIsScrolled] = useState(false)

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50)
  })

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/commands', label: 'Commands' },
    { href: '/docs', label: 'Docs' },
  ]

  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/'
    return location.pathname.startsWith(href)
  }

  return (
    <motion.header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
          ? 'bg-discord-darker/80 backdrop-blur-lg border-b border-discord-light/10 shadow-lg'
          : 'bg-transparent border-transparent'
        }`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-300">
              <span className="text-white font-black text-lg">DM</span>
            </div>
            <div className="absolute inset-0 bg-white/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </div>
          <span className={`font-bold text-xl transition-colors duration-300 ${isScrolled ? 'text-white' : 'text-white drop-shadow-md'
            }`}>
            Debi & Marlene<span className="text-debi-primary">.</span>
          </span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-2 p-1 rounded-full bg-white/5 backdrop-blur-sm border border-white/10">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-300 ${isActive(link.href)
                  ? 'bg-white/10 text-white shadow-sm'
                  : 'text-gray-300 hover:text-white hover:bg-white/5'
                }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Auth Button */}
        <div className="flex items-center gap-4">
          {user ? (
            <Link
              to="/dashboard"
              className="flex items-center gap-3 pl-2 pr-4 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 transition-all hover:scale-105 group"
            >
              {user.avatar ? (
                <img
                  src={`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=32`}
                  alt={user.username}
                  className="w-8 h-8 rounded-full border-2 border-transparent group-hover:border-debi-primary transition-colors"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
                  {user.username.charAt(0)}
                </div>
              )}
              <span className="text-sm font-semibold text-white/90 hidden sm:block">
                Dashboard
              </span>
            </Link>
          ) : (
            <button
              onClick={login}
              className="relative px-6 py-2.5 rounded-xl font-bold text-sm text-white overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-debi-primary to-marlene-primary transition-transform duration-300 group-hover:scale-105" />
              <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
              <span className="relative flex items-center gap-2">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
                </svg>
                Discord Login
              </span>
            </button>
          )}
        </div>
      </div>
    </motion.header>
  )
}
