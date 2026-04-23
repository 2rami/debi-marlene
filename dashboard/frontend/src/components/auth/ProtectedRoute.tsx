import { Outlet } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import Loading from '../common/Loading'
import { useEffect } from 'react'

export default function ProtectedRoute() {
  const { user, loading, refreshing, login } = useAuth()

  useEffect(() => {
    // refreshing 동안엔 user=null 이어도 login() 재호출 금지 — OAuth 콜백 race 방지
    if (!loading && !refreshing && !user) {
      login()
    }
  }, [loading, refreshing, user, login])

  if (loading || refreshing || !user) {
    return <Loading />
  }

  return <Outlet />
}
