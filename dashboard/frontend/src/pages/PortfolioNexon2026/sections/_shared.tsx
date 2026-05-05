import { motion } from 'framer-motion'
import { useRevealOff } from '../shared/useRevealOff'

export function FadeIn({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const revealOff = useRevealOff()
  if (revealOff) return <div>{children}</div>
  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true, amount: 0.4 }}
      transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}
