import { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import CountUp from '../components/common/CountUp'
import LOGO from '../assets/images/profile.jpg'
import debiImage from '../assets/images/event/debi_solo.png'
import marleneImage from '../assets/images/event/marlene_solo.png'

import CHAR_02 from '../assets/images/event/imgi_47_ch02.png'
import CHAR_03 from '../assets/images/event/imgi_48_ch03.png'
import CHAR_05 from '../assets/images/event/imgi_49_ch05.png'
import CHAR_06 from '../assets/images/event/imgi_50_ch06.png'
import CHAR_07 from '../assets/images/event/imgi_51_ch07.png'
import CURSOR from '../assets/images/event/imgi_45_cursor01.png'

const ICONS = [CHAR_02, CHAR_03, CHAR_05, CHAR_06, CHAR_07, CURSOR]

export default function CharacterSelect() {
  const navigate = useNavigate()
  const [phase, setPhase] = useState<'loading' | 'burst' | 'exit'>('loading')
  const [countDone, setCountDone] = useState(false)

  // 캡슐 안 파티클 — 랜덤 위치 + 흔들림
  const particles = useMemo(() =>
    Array.from({ length: 20 }).map((_, i) => ({
      id: i,
      src: ICONS[i % ICONS.length],
      size: 40 + Math.random() * 35,
      x: 15 + Math.random() * 70,  // 캡슐 내부 %
      y: 20 + Math.random() * 60,
      jiggleDuration: 0.3 + Math.random() * 0.4,
      jiggleAmount: 3 + Math.random() * 5,
      rotation: Math.random() * 360,
      delay: i * 0.05,
      // burst 시 날아갈 방향
      burstX: -800 - Math.random() * 600,
      burstY: (Math.random() - 0.5) * 800,
      burstRotate: (Math.random() - 0.5) * 720,
    })), [])

  useEffect(() => {
    if (countDone) {
      const t1 = setTimeout(() => setPhase('burst'), 200)
      const t2 = setTimeout(() => setPhase('exit'), 1000)
      const t3 = setTimeout(() => navigate('/landing', { replace: true }), 1600)
      return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
    }
  }, [countDone, navigate])

  return (
    <>
      <style>{`
        @keyframes jiggle {
          0%, 100% { transform: translate(0, 0) rotate(var(--rot)); }
          25% { transform: translate(calc(var(--jig) * 1px), calc(var(--jig) * -0.7px)) rotate(calc(var(--rot) + 3deg)); }
          50% { transform: translate(calc(var(--jig) * -0.8px), calc(var(--jig) * 1px)) rotate(calc(var(--rot) - 2deg)); }
          75% { transform: translate(calc(var(--jig) * 0.5px), calc(var(--jig) * 0.8px)) rotate(calc(var(--rot) + 2deg)); }
        }
        @keyframes capsuleShake {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          20% { transform: translate(-2px, 1px) rotate(-0.5deg); }
          40% { transform: translate(2px, -1px) rotate(0.5deg); }
          60% { transform: translate(-1px, 2px) rotate(-0.3deg); }
          80% { transform: translate(1px, -1px) rotate(0.3deg); }
        }
        @keyframes capsuleShakeHard {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          10% { transform: translate(-5px, 3px) rotate(-1.5deg); }
          20% { transform: translate(5px, -2px) rotate(1.5deg); }
          30% { transform: translate(-4px, 4px) rotate(-1deg); }
          40% { transform: translate(3px, -3px) rotate(1deg); }
          50% { transform: translate(-6px, 2px) rotate(-2deg); }
          60% { transform: translate(6px, -4px) rotate(2deg); }
          70% { transform: translate(-3px, 5px) rotate(-1.5deg); }
          80% { transform: translate(4px, -2px) rotate(1deg); }
          90% { transform: translate(-5px, 3px) rotate(-1.5deg); }
        }
        @keyframes starBottom {
          0% { transform: translate(0%, 0%); opacity: 1; }
          100% { transform: translate(-100%, 0%); opacity: 0.3; }
        }
        @keyframes starTop {
          0% { transform: translate(0%, 0%); opacity: 1; }
          100% { transform: translate(100%, 0%); opacity: 0.3; }
        }
        @keyframes charReveal {
          0% { clip-path: inset(100% 0 0 0); filter: brightness(2) saturate(0); }
          60% { clip-path: inset(0 0 0 0); filter: brightness(1.3) saturate(0.5); }
          100% { clip-path: inset(0 0 0 0); filter: brightness(1) saturate(1); }
        }
        @keyframes charGlow {
          0%, 100% { filter: drop-shadow(0 0 8px rgba(125,232,237,0.4)); }
          50% { filter: drop-shadow(0 0 16px rgba(255,166,215,0.5)); }
        }
      `}</style>

      <AnimatePresence>
        {phase !== 'exit' ? (
          <motion.div
            className="fixed inset-0 z-[9999] bg-[#f8fcfd] flex items-center justify-center overflow-hidden cursor-pointer"
            onClick={() => navigate('/landing', { replace: true })}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="absolute inset-0 bg-gradient-to-b from-[#e8f8fa] via-[#f8fcfd] to-white" />

            {/* 데비 — 왼쪽 */}
            <div className="absolute bottom-0 left-[5%] md:left-[10%] z-[5]">
              <img
                src={debiImage}
                alt="Debi"
                className="h-[45vh] md:h-[58vh] object-contain object-bottom"
                style={{ animation: 'charReveal 1s ease-out 0.2s both, charGlow 3s ease-in-out 1.2s infinite' }}
                draggable={false}
              />
            </div>

            {/* 마를렌 — 오른쪽 뒤 */}
            <div className="absolute bottom-0 right-[5%] md:right-[10%] z-[4]">
              <img
                src={marleneImage}
                alt="Marlene"
                className="h-[45vh] md:h-[58vh] object-contain object-bottom"
                style={{ animation: 'charReveal 1s ease-out 0.4s both, charGlow 3s ease-in-out 1.4s infinite' }}
                draggable={false}
              />
            </div>

            {/* 캡슐 (인형뽑기 캡슐) — 중앙 우측, 크게 */}
            <div
              className="absolute right-[5%] top-[8%] z-[6] w-[280px] h-[360px] md:w-[340px] md:h-[440px]"
              style={{ animation: phase === 'burst' ? 'capsuleShakeHard 0.15s linear infinite' : 'capsuleShake 2s ease-in-out infinite' }}
            >
              {/* 전기 테두리 — StarBorder 스타일 */}
              <div className="absolute inset-0 rounded-[40%] overflow-hidden">
                <div
                  className="absolute w-[300%] h-[50%] opacity-70 bottom-[-11px] right-[-250%] rounded-full"
                  style={{ background: 'radial-gradient(circle, #7DE8ED, transparent 10%)', animation: 'starBottom 4s linear infinite alternate' }}
                />
                <div
                  className="absolute w-[300%] h-[50%] opacity-70 top-[-10px] left-[-250%] rounded-full"
                  style={{ background: 'radial-gradient(circle, #FFA6D7, transparent 10%)', animation: 'starTop 4s linear infinite alternate' }}
                />
              </div>
              {/* 캡슐 본체 */}
              <div className="absolute inset-[2px] rounded-[40%] bg-white/40 backdrop-blur-sm overflow-hidden border border-white/50">
                {/* 파티클들 */}
                {particles.map((p) => (
                  <motion.img
                    key={p.id}
                    src={p.src}
                    className="absolute pointer-events-none"
                    style={{
                      width: p.size,
                      height: 'auto',
                      left: `${p.x}%`,
                      top: `${p.y}%`,
                      '--rot': `${p.rotation}deg`,
                      '--jig': p.jiggleAmount,
                      animation: `jiggle ${p.jiggleDuration}s ease-in-out infinite`,
                      animationDelay: `${p.delay}s`,
                    } as React.CSSProperties}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={phase === 'burst' ? {
                      x: p.burstX,
                      y: p.burstY,
                      rotate: p.burstRotate,
                      opacity: 0,
                      scale: 1.5,
                    } : {
                      opacity: 0.8,
                      scale: 1,
                    }}
                    transition={phase === 'burst' ? {
                      duration: 0.6,
                      ease: [0.22, 1, 0.36, 1],
                      delay: Math.random() * 0.15,
                    } : {
                      delay: p.delay,
                      duration: 0.3,
                    }}
                    draggable={false}
                    alt=""
                  />
                ))}
              </div>

              {/* 캡슐 빛 반사 */}
              <div className="absolute top-[10%] left-[15%] w-[30%] h-[15%] bg-white/50 rounded-full blur-sm" />

              {/* 금 갈라지는 효과 (burst 시) */}
              {phase === 'burst' && (
                <motion.div
                  className="absolute inset-0 rounded-[40%]"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  style={{
                    background: 'repeating-conic-gradient(from 0deg, transparent 0deg, transparent 8deg, rgba(125,232,237,0.6) 8deg, rgba(125,232,237,0.6) 9deg)',
                  }}
                />
              )}
            </div>

            {/* 중앙: 로고 + CountUp */}
            <motion.div
              className="relative z-10 flex flex-col items-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            >
              <div
                className="w-20 h-20 rounded-full overflow-hidden shadow-xl border-2 border-white/60 mb-6"
                style={{ animation: 'electricOutline 3s ease-in-out infinite' }}
              >
                <img src={LOGO} alt="Logo" className="w-full h-full object-cover" />
              </div>

              <div className="font-title text-6xl md:text-8xl bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent mb-2">
                <CountUp to={100} from={0} duration={2.2} separator="" onEnd={() => setCountDone(true)} />
                <span className="text-4xl md:text-5xl ml-1">%</span>
              </div>

              <p className="font-title text-lg bg-gradient-to-r from-[#3cabc9] to-[#e58fb6] bg-clip-text text-transparent">
                Debi & Marlene
              </p>
            </motion.div>

            {/* 스킵 */}
            <motion.p
              className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 text-xs text-gray-400 font-body"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.6 }}
              transition={{ delay: 1 }}
            >
              click to skip
            </motion.p>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </>
  )
}
