import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import Header from '../components/common/Header'
import ScrollFloat from '../components/common/ScrollFloat'
import { useTheme } from '../contexts/ThemeContext'

import KRAFTON_LOGO from '../assets/images/event/krafton_logo.png'
import CHRONO_LOGO from '../assets/images/event/chrono_studio_c_logo.png'
import NIMBLE_LOGO from '../assets/images/event/nimble_neuron_logo.png'
import NEXON_LOGO from '../assets/images/event/nexon_logo.png'

const companies = [
  {
    id: 'krafton',
    name: 'KRAFTON',
    position: 'AI FDE',
    dept: 'AI Transformation Dept.',
    color: '#3cabc9',
    ready: true,
    logo: KRAFTON_LOGO,
    logoStyle: 'contain' as const,
    invertOnDark: false,
  },
  {
    id: 'chrono',
    name: 'Chrono Studio',
    position: '개발 자동화 엔지니어',
    dept: 'AI 기반',
    color: '#C4A265',
    ready: true,
    logo: CHRONO_LOGO,
    logoStyle: 'cover' as const,
    invertOnDark: false,
  },
  {
    id: 'nimble-neuron',
    name: 'Nimble Neuron',
    position: '캐릭터 QA',
    dept: '',
    color: '#7aa2f7',
    ready: true,
    logo: NIMBLE_LOGO,
    logoStyle: 'contain' as const,
    invertOnDark: true,
  },
  {
    id: 'nexon',
    name: 'NEXON',
    position: 'AI Agent Full-Stack Engineer',
    dept: 'AX-Tech / Intelligence Labs',
    color: '#0B5ED7',
    ready: true,
    logo: NEXON_LOGO,
    logoStyle: 'contain' as const,
    invertOnDark: false,
  },
]

export default function Portfolio() {
  const navigate = useNavigate()
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <div className={`min-h-screen ${isDark ? 'bg-[#0e0f14]' : 'bg-[#f8f9fc]'}`}>
      <Header />

      <div className="flex flex-col items-center justify-center min-h-screen px-6">
        <ScrollFloat
          containerClassName="font-title bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent leading-tight mb-4"
          textClassName="text-4xl md:text-[64px]"
        >
          Portfolio
        </ScrollFloat>

        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className={`text-lg mb-16 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}
        >
          회사를 선택하세요
        </motion.p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl w-full">
          {companies.map((company, i) => (
            <motion.div
              key={company.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              onClick={() => company.ready && navigate(`/portfolio/${company.id}`)}
              className={`relative group rounded-2xl border p-8 flex flex-col items-center text-center transition-all duration-300 ${
                company.ready
                  ? `cursor-pointer ${isDark ? 'bg-white/[0.02] border-white/[0.06] hover:border-white/20 hover:bg-white/[0.04]' : 'bg-white/80 border-gray-200/50 hover:border-gray-300 hover:shadow-lg'}`
                  : `${isDark ? 'bg-white/[0.01] border-white/[0.03]' : 'bg-gray-50/50 border-gray-200/30'} opacity-50 cursor-default`
              }`}
            >
              {/* Color accent line */}
              <div
                className="absolute top-0 left-1/2 -translate-x-1/2 h-1 rounded-b-full transition-all duration-300"
                style={{
                  backgroundColor: company.color,
                  width: company.ready ? '60px' : '30px',
                  opacity: company.ready ? 1 : 0.3,
                }}
              />

              {/* Logo */}
              <div
                className="w-20 h-20 rounded-2xl flex items-center justify-center mb-5 overflow-hidden"
                style={{ backgroundColor: `${company.color}15` }}
              >
                {company.logo ? (
                  <img
                    src={company.logo}
                    alt={company.name}
                    className={`rounded-2xl ${company.logoStyle === 'contain' ? 'w-14 h-14 object-contain' : 'w-full h-full object-cover'} ${isDark && company.invertOnDark ? 'invert' : ''}`}
                  />
                ) : (
                  <span className="text-2xl font-bold font-title" style={{ color: company.color }}>
                    {company.name.charAt(0)}
                  </span>
                )}
              </div>

              {/* Company info */}
              <h3 className={`text-xl font-bold mb-1 ${isDark ? 'text-white' : 'text-gray-800'}`}>
                {company.name}
              </h3>

              {company.position && (
                <p className={`text-sm font-medium mb-1`} style={{ color: company.color }}>
                  {company.position}
                </p>
              )}

              {company.dept && (
                <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  {company.dept}
                </p>
              )}

              {!company.ready && (
                <span className={`text-xs mt-3 px-3 py-1 rounded-full ${isDark ? 'bg-white/[0.05] text-gray-500' : 'bg-gray-100 text-gray-400'}`}>
                  준비중
                </span>
              )}

              {/* Hover arrow */}
              {company.ready && (
                <div className={`mt-4 flex items-center gap-1 text-xs transition-opacity duration-300 opacity-0 group-hover:opacity-100 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  <span>보기</span>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
