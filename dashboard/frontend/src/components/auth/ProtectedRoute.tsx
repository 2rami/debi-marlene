import { Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import Loading from '../common/Loading'
import { useEffect } from 'react'

export default function ProtectedRoute() {
  const { user, loading, refreshing, login } = useAuth()
  const location = useLocation()

  useEffect(() => {
    // refreshing 동안엔 user=null 이어도 login() 재호출 금지 — OAuth 콜백 race 방지
    if (!loading && !refreshing && !user) {
      // 로그인 뒤 원래 가려던 곳으로 돌아오게 남겨 둔다. 이게 없으면 무조건
      // /dashboard 로 떨어져서, 디스코드 /그림 안내를 눌러 온 사람이 설정을
      // 처음부터 다시 찾아야 한다.
      try {
        sessionStorage.setItem('post_login_path', location.pathname + location.search)
      } catch {
        // 프라이빗 모드 등에서 막힐 수 있다 — 복귀를 못 할 뿐이라 로그인은 계속한다
      }
      login()
    }
  }, [loading, refreshing, user, login, location])

  if (loading || refreshing || !user) {
    return <Loading />
  }

  return <Outlet />
}
