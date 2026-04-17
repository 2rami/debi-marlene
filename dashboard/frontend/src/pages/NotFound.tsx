import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import FuzzyText from '../components/common/FuzzyText'
import { useTheme } from '../contexts/ThemeContext'

export default function NotFound() {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const accent = isDark ? '#6DC8E8' : '#0B5ED7'

  return (
    <div
      className={`min-h-screen flex flex-col items-center justify-center px-6 ${
        isDark ? 'bg-[#0e0f14]' : 'bg-[#f8f9fc]'
      }`}
    >
      <div className="flex flex-col items-center text-center">
        <FuzzyText
          fontSize="clamp(6rem, 22vw, 16rem)"
          fontWeight={900}
          color={accent}
          baseIntensity={0.2}
          hoverIntensity={0.55}
          fuzzRange={32}
          className="mb-8"
        >
          404
        </FuzzyText>

        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className={`font-title text-2xl md:text-3xl font-bold mb-3 ${
            isDark ? 'text-white' : 'text-gray-800'
          }`}
        >
          페이지를 찾을 수 없어요
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className={`text-sm md:text-base mb-10 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}
        >
          주소를 다시 확인하거나 홈으로 돌아가 주세요
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
        >
          <Link
            to="/landing"
            className={`group inline-flex items-center gap-2 px-6 py-3 rounded-full border font-medium transition-all duration-300 ${
              isDark
                ? 'bg-white/[0.03] border-white/[0.1] text-white hover:bg-white/[0.08] hover:border-white/20'
                : 'bg-white border-gray-200 text-gray-800 hover:border-gray-400 hover:shadow-lg'
            }`}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="transition-transform duration-300 group-hover:-translate-x-1"
            >
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            <span>홈으로</span>
          </Link>
        </motion.div>
      </div>
    </div>
  )
}
