import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

export default function Sidebar() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const navItems = [
    {
      path: '/dashboard',
      label: '대시보드',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
    },
    {
      path: '/premium',
      label: '프리미엄',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
      ),
    },
  ]

  return (
    <aside className="w-64 bg-discord-darker border-r border-discord-light/10 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-discord-light/10">
        <Link to="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center">
            <span className="text-white font-bold">D</span>
          </div>
          <span className="font-semibold gradient-text">Debi Dashboard</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              location.pathname === item.path
                ? 'bg-discord-light text-discord-text'
                : 'text-discord-muted hover:bg-discord-dark hover:text-discord-text'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-discord-light/10">
        <div className="flex items-center gap-3 mb-4">
          <img
            src={user?.avatar ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=64` : '/icons/default-avatar.png'}
            alt={user?.username}
            className="w-10 h-10 rounded-full"
          />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-discord-text truncate">
              {user?.username}
            </p>
            <p className="text-xs text-discord-muted">
              {user?.premium.isActive ? 'Premium' : 'Free'}
            </p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-discord-dark text-discord-muted hover:text-discord-red transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>로그아웃</span>
        </button>
      </div>
    </aside>
  )
}
