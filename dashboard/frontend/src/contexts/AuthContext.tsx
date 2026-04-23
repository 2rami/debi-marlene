import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { api } from '../services/api'
import { DISCORD_CLIENT_ID } from '../config/discord'

interface User {
  id: string
  username: string
  avatar: string
  email?: string
  premium: {
    isActive: boolean
    plan: string | null
    expiresAt: string | null
  }
  adminServers: string[]
}

interface AuthContextType {
  user: User | null
  loading: boolean
  refreshing: boolean
  login: () => void
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  // OAuth 콜백 직후 refreshUser 가 끝나기 전에 ProtectedRoute 가 user=null 로 읽어 login()을 재호출하는 race 방지
  const [refreshing, setRefreshing] = useState(false)

  const refreshUser = useCallback(async () => {
    setRefreshing(true)
    try {
      const response = await api.get<{ user: User }>('/auth/me')
      if (response.data.user) {
        setUser(response.data.user)
      } else {
        setUser(null)
      }
    } catch {
      setUser(null)
    } finally {
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    const checkAuth = async () => {
      setLoading(true)
      await refreshUser()
      setLoading(false)
    }
    checkAuth()
  }, [])

  const login = () => {
    const redirectUri = encodeURIComponent(`${window.location.origin}/api/auth/callback`)
    const scope = encodeURIComponent('identify email guilds')

    window.location.href = `https://discord.com/api/oauth2/authorize?client_id=${DISCORD_CLIENT_ID}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } finally {
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, refreshing, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
