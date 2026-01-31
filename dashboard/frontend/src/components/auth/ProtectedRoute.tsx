import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import Loading from '../common/Loading'

export default function ProtectedRoute() {
  const { user, loading } = useAuth()

  if (loading) {
    return <Loading />
  }

  if (!user) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
