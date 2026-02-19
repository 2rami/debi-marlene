import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import Loading from '../components/common/Loading'

export default function AuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const exchanged = useRef(false)

  useEffect(() => {
    if (exchanged.current) return
    exchanged.current = true

    const exchangeCode = async () => {
      const code = searchParams.get('code')
      const oauthError = searchParams.get('error')

      if (oauthError || !code) {
        setError('Discord 인증에 실패했습니다.')
        setTimeout(() => navigate('/', { replace: true }), 2000)
        return
      }

      try {
        await api.post('/auth/exchange', { code })
        await refreshUser()
        navigate('/dashboard', { replace: true })
      } catch {
        setError('로그인에 실패했습니다. 다시 시도해주세요.')
        setTimeout(() => navigate('/', { replace: true }), 2000)
      }
    }

    exchangeCode()
  }, [])

  if (error) {
    return (
      <div className="min-h-screen bg-discord-darkest flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-2">{error}</p>
          <p className="text-discord-muted text-sm">잠시 후 메인 페이지로 이동합니다...</p>
        </div>
      </div>
    )
  }

  return <Loading />
}
