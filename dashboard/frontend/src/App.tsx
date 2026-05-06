import { Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import CookieConsent from './components/common/CookieConsent'
import { initGA, trackPageView } from './lib/analytics'
import { pauseAds, removeAdSlots, resumeAds } from './lib/adsBlock'
import CharacterSelect from './pages/CharacterSelect'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import ServerManagement from './pages/ServerManagement'
import PaymentSuccess from './pages/PaymentSuccess'
import PaymentFail from './pages/PaymentFail'
import Commands from './pages/Commands'
import Docs from './pages/Docs'
import Terms from './pages/Terms'
import AuthCallback from './pages/AuthCallback'
import ProtectedRoute from './components/auth/ProtectedRoute'
import BotGuide from './pages/BotGuide'
import PortfolioKrafton from './pages/PortfolioKrafton'
import PortfolioNimbleNeuron from './pages/PortfolioNimbleNeuron'
import PortfolioNimbleNeuronPrint from './pages/PortfolioNimbleNeuronPrint'
import PortfolioSmilegate from './pages/PortfolioSmilegate'
import PortfolioSmilegateCompare from './pages/PortfolioSmilegateCompare'
import PageLLM from './pages/PortfolioNexon2026/PageLLM'
import PageService from './pages/PortfolioNexon2026/PageService'
import PageQA from './pages/PortfolioNexon2026/PageQA'
import PageMotionCatalog from './pages/PortfolioNexon2026/PageMotionCatalog'
import Feed from './pages/Feed'
import NotFound from './pages/NotFound'

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    const lenis = (window as any).__lenis
    if (lenis) lenis.scrollTo(0, { immediate: true })
    else window.scrollTo(0, 0)
  }, [pathname])
  return null
}

// 라우트 변경 시 GA page_view 발사. SPA 자동 page_view 는 끄고 여기서만 쏨.
function GAPageTracker() {
  const { pathname, search } = useLocation()
  useEffect(() => {
    trackPageView(pathname + search)
  }, [pathname, search])
  return null
}

// /portfolio/* 진입 시 AdSense Auto Ads 차단. NEXON 면접관 노출 페이지 → 광고 마이너스.
// index.html 의 inline 가드가 첫 로드를 막고, 이 컴포넌트가 SPA 네비게이션을 막음.
function AdsRouteGate() {
  const { pathname } = useLocation()
  useEffect(() => {
    const isPortfolio = pathname.startsWith('/portfolio/')
    if (!isPortfolio) {
      resumeAds()
      return
    }
    pauseAds()
    // Auto Ads 가 비동기로 슬롯을 다시 끼울 수 있어 5초간 0.5초마다 청소
    const cleanId = window.setInterval(removeAdSlots, 500)
    const stopId = window.setTimeout(() => window.clearInterval(cleanId), 5000)
    return () => {
      window.clearInterval(cleanId)
      window.clearTimeout(stopId)
    }
  }, [pathname])
  return null
}

// 앱 부팅 시 1회 GA 초기화. consent === granted + PROD + 측정 ID 모두 만족해야 실제 로드.
function GABootstrap() {
  useEffect(() => {
    initGA()
  }, [])
  return null
}

function App() {
  return (
    <ThemeProvider>
    <AuthProvider>
      <div className="min-h-screen bg-discord-darkest">
        <ScrollToTop />
        <GABootstrap />
        <GAPageTracker />
        <AdsRouteGate />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<CharacterSelect />} />
          <Route path="/landing" element={<Landing />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/commands" element={<Commands />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/bot-guide" element={<BotGuide />} />
          <Route path="/payment/success" element={<PaymentSuccess />} />
          <Route path="/payment/fail" element={<PaymentFail />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/portfolio/krafton" element={<PortfolioKrafton />} />
          <Route path="/portfolio/nimble-neuron" element={<PortfolioNimbleNeuron />} />
          <Route path="/portfolio/nimble-neuron/print" element={<PortfolioNimbleNeuronPrint />} />
          <Route path="/portfolio/smilegate" element={<PortfolioSmilegate />} />
          <Route path="/portfolio/smilegate-compare" element={<PortfolioSmilegateCompare />} />
          <Route path="/portfolio/nexon" element={<PageLLM />} />
          <Route path="/portfolio/nexon/llm" element={<PageLLM />} />
          <Route path="/portfolio/nexon/service" element={<PageService />} />
          <Route path="/portfolio/nexon/qa" element={<PageQA />} />
          <Route path="/portfolio/nexon/maple-motions" element={<PageMotionCatalog />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/servers/:guildId" element={<ServerManagement />} />
          </Route>

          {/* Owner-only hidden route — backend owner_required gate */}
          <Route path="/me/feed" element={<Feed />} />

          <Route path="*" element={<NotFound />} />
        </Routes>
        <CookieConsent />
      </div>
    </AuthProvider>
    </ThemeProvider>
  )
}

export default App
