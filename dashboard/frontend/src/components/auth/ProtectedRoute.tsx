import { Outlet } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import Loading from '../common/Loading'
import { useEffect } from 'react'

export default function ProtectedRoute() {
  const { user, loading, login } = useAuth()

  useEffect(() => {
    if (!loading && !user) {
      login()
    }
  }, [loading, user, login])

  if (loading || !user) {
    return <Loading />
  }

  return <Outlet />
}
