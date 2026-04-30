import { Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import CharacterSelect from './pages/CharacterSelect'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import ServerManagement from './pages/ServerManagement'
import Premium from './pages/Premium'
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

function App() {
  return (
    <ThemeProvider>
    <AuthProvider>
      <div className="min-h-screen bg-discord-darkest">
        <ScrollToTop />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<CharacterSelect />} />
          <Route path="/landing" element={<Landing />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/commands" element={<Commands />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/bot-guide" element={<BotGuide />} />
          <Route path="/premium" element={<Premium />} />
          <Route path="/payment/success" element={<PaymentSuccess />} />
          <Route path="/payment/fail" element={<PaymentFail />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/portfolio/krafton" element={<PortfolioKrafton />} />
          <Route path="/portfolio/nimble-neuron" element={<PortfolioNimbleNeuron />} />
          <Route path="/portfolio/nimble-neuron/print" element={<PortfolioNimbleNeuronPrint />} />
          <Route path="/portfolio/smilegate" element={<PortfolioSmilegate />} />
          <Route path="/portfolio/smilegate-compare" element={<PortfolioSmilegateCompare />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/servers/:guildId" element={<ServerManagement />} />
          </Route>

          {/* Owner-only hidden route — backend owner_required gate */}
          <Route path="/me/feed" element={<Feed />} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </AuthProvider>
    </ThemeProvider>
  )
}

export default App
