import { motion } from 'framer-motion'
import { useTheme } from '../../contexts/ThemeContext'

/**
 * 가이드/FAQ 공통 요소 — BotGuide 의 Section/QA/FadeIn 패턴을 추출.
 * 모든 공개 가이드 페이지가 같은 톤을 쓰도록 단일 출처로 관리.
 */

export function FadeIn({ children, className = '', delay = 0 }: {
  children: React.ReactNode; className?: string; delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export function QA({ q, children, delay = 0 }: {
  q: string; children: React.ReactNode; delay?: number
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className="mb-6">
      <div className={`text-sm font-bold mb-2 ${isDark ? 'text-white' : 'text-gray-800'}`}>{q}</div>
      <div className={`text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{children}</div>
    </FadeIn>
  )
}

export function Section({ title, color, children, delay = 0 }: {
  title: string; color: string; children: React.ReactNode; delay?: number
}) {
  const { isDark } = useTheme()
  return (
    <FadeIn delay={delay} className={`p-6 md:p-8 rounded-2xl border ${isDark ? 'bg-white/[0.03] border-white/[0.06]' : 'bg-white/80 border-gray-200/80'}`}>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1.5 h-8 rounded-full" style={{ backgroundColor: color }} />
        <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-800'}`}>{title}</h2>
      </div>
      {children}
    </FadeIn>
  )
}
