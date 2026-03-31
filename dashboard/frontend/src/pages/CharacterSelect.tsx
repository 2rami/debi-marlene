import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import debiImage from '../assets/images/event/debi_solo.png'
import marleneImage from '../assets/images/event/marlene_solo.png'
import LOGO from '../assets/images/profile.jpg'

export default function CharacterSelect() {
  const navigate = useNavigate()
  const [phase, setPhase] = useState<'enter' | 'meet' | 'exit'>('enter')

  useEffect(() => {
    // 캐릭터 등장 -> 만남 -> 페이드아웃 -> Landing 이동
    const t1 = setTimeout(() => setPhase('meet'), 800)
    const t2 = setTimeout(() => setPhase('exit'), 2200)
    const t3 = setTimeout(() => navigate('/landing', { replace: true }), 2800)
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
  }, [navigate])

  return (
    <AnimatePresence>
      {phase !== 'exit' ? (
        <motion.div
          className="fixed inset-0 z-[9999] bg-[#e0f7fa] flex items-end justify-center overflow-hidden cursor-pointer"
          onClick={() => navigate('/landing', { replace: true })}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          {/* 배경 그라데이션 */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#e0f7fa] via-[#f0fdff] to-white" />

          {/* 로고 + 텍스트 — 상단 가운데 */}
          <motion.div
            className="absolute top-[18%] left-1/2 -translate-x-1/2 flex flex-col items-center z-10"
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="w-16 h-16 rounded-full overflow-hidden shadow-lg border-2 border-white/60 mb-4">
              <img src={LOGO} alt="Logo" className="w-full h-full object-cover" />
            </div>
            <motion.p
              className="font-title text-2xl md:text-3xl bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.6 }}
            >
              Debi & Marlene
            </motion.p>
            <motion.p
              className="font-body text-sm text-gray-400 mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9, duration: 0.6 }}
            >
              loading...
            </motion.p>
          </motion.div>

          {/* 데비 — 왼쪽에서 등장, 가운데로 이동 */}
          <motion.div
            className="absolute bottom-0 z-10"
            initial={{ x: '-60vw', opacity: 0 }}
            animate={{
              x: phase === 'enter' ? '-15vw' : '-8vw',
              opacity: 1,
            }}
            transition={{
              duration: phase === 'enter' ? 0.8 : 0.6,
              ease: [0.22, 1, 0.36, 1],
            }}
          >
            <img
              src={debiImage}
              alt="Debi"
              className="h-[55vh] md:h-[65vh] object-contain object-bottom drop-shadow-2xl"
              draggable={false}
            />
          </motion.div>

          {/* 마를렌 — 오른쪽에서 등장, 가운데로 이동 */}
          <motion.div
            className="absolute bottom-0 z-10"
            initial={{ x: '60vw', opacity: 0 }}
            animate={{
              x: phase === 'enter' ? '15vw' : '8vw',
              opacity: 1,
            }}
            transition={{
              duration: phase === 'enter' ? 0.8 : 0.6,
              ease: [0.22, 1, 0.36, 1],
              delay: 0.1,
            }}
          >
            <img
              src={marleneImage}
              alt="Marlene"
              className="h-[55vh] md:h-[65vh] object-contain object-bottom drop-shadow-2xl"
              draggable={false}
            />
          </motion.div>

          {/* 하단 스킵 힌트 */}
          <motion.p
            className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 text-xs text-gray-400 font-body"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.6 }}
            transition={{ delay: 1.2, duration: 0.5 }}
          >
            click to skip
          </motion.p>
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}
