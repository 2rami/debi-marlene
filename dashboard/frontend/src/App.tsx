import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
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

function App() {
  return (
    <ThemeProvider>
    <AuthProvider>
      <div className="min-h-screen bg-discord-darkest">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/commands" element={<Commands />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/bot-guide" element={<BotGuide />} />
          <Route path="/premium" element={<Premium />} />
          <Route path="/payment/success" element={<PaymentSuccess />} />
          <Route path="/payment/fail" element={<PaymentFail />} />
          <Route path="/terms" element={<Terms />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/servers/:guildId" element={<ServerManagement />} />
          </Route>
        </Routes>
      </div>
    </AuthProvider>
    </ThemeProvider>
  )
}

export default App
