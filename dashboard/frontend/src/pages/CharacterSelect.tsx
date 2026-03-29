import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import debiImage from '../assets/images/event/debi_select.png'
import marleneImage from '../assets/images/event/marlene_select.png'

type Side = 'left' | 'right' | null

export default function CharacterSelect() {
  const navigate = useNavigate()
  const [hovered, setHovered] = useState<Side>(null)

  const handleClick = useCallback((side: Side) => {
    if (side === 'left') navigate('/dashboard')
    else navigate('/landing')
  }, [navigate])

  const leftFlex = hovered === 'left' ? 2.2 : hovered === 'right' ? 0.8 : 1
  const rightFlex = hovered === 'right' ? 2.2 : hovered === 'left' ? 0.8 : 1

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-[#0a0a0f] select-none">
      {/* Grain overlay */}
      <div className="grain-overlay pointer-events-none absolute inset-0 z-50 opacity-[0.03]" />

      {/* Ambient glow based on hover */}
      <AnimatePresence>
        {hovered === 'left' && (
          <motion.div
            key="glow-left"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="pointer-events-none absolute inset-0 z-10"
            style={{
              background: 'radial-gradient(ellipse at 30% 50%, rgba(0, 199, 206, 0.08) 0%, transparent 70%)',
            }}
          />
        )}
        {hovered === 'right' && (
          <motion.div
            key="glow-right"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="pointer-events-none absolute inset-0 z-10"
            style={{
              background: 'radial-gradient(ellipse at 70% 50%, rgba(244, 114, 182, 0.08) 0%, transparent 70%)',
            }}
          />
        )}
      </AnimatePresence>

      {/* Main split container */}
      <div className="relative z-20 flex h-full">
        {/* LEFT - DEBI */}
        <motion.div
          className="relative cursor-pointer overflow-hidden"
          animate={{ flex: leftFlex }}
          transition={{ type: 'spring', stiffness: 200, damping: 30 }}
          onMouseEnter={() => setHovered('left')}
          onMouseLeave={() => setHovered(null)}
          onClick={() => handleClick('left')}
        >
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-[#0a1628] via-[#0a0a0f] to-[#0a0a0f]" />

          {/* Hover glow ring */}
          <motion.div
            className="pointer-events-none absolute inset-0"
            animate={{
              boxShadow: hovered === 'left'
                ? 'inset 0 0 120px rgba(0, 199, 206, 0.15)'
                : 'inset 0 0 0px rgba(0, 199, 206, 0)',
            }}
            transition={{ duration: 0.5 }}
          />

          {/* Character image - Debi */}
          <motion.div
            className="absolute bottom-0 h-[85%] flex items-end justify-center w-full"
            animate={{
              scale: hovered === 'left' ? 1.05 : hovered === 'right' ? 0.92 : 1,
              filter: hovered === 'right'
                ? 'brightness(0.3) grayscale(0.5)'
                : hovered === 'left'
                  ? 'brightness(1.1) drop-shadow(0 0 40px rgba(0, 199, 206, 0.4))'
                  : 'brightness(0.85)',
            }}
            transition={{ type: 'spring', stiffness: 150, damping: 25 }}
          >
            <img
              src={debiImage}
              alt="Debi"
              className="h-full object-contain"
              draggable={false}
            />
          </motion.div>

          {/* Character name */}
          <div className="absolute bottom-12 left-0 w-full px-8">
            <motion.div
              animate={{
                opacity: hovered === 'right' ? 0.3 : 1,
                y: hovered === 'left' ? -8 : 0,
              }}
              transition={{ duration: 0.4 }}
            >
              <p className="mb-1 font-body text-sm tracking-[0.3em] text-debi-400/60 uppercase">
                Dashboard
              </p>
              <h2
                className="font-display text-6xl font-bold tracking-tight"
                style={{
                  color: '#00c7ce',
                  textShadow: hovered === 'left'
                    ? '0 0 30px rgba(0, 199, 206, 0.5), 0 0 60px rgba(0, 199, 206, 0.2)'
                    : 'none',
                }}
              >
                DEBI
              </h2>
              <motion.div
                className="mt-3 h-[2px] bg-debi-primary"
                animate={{ width: hovered === 'left' ? '100%' : '40%' }}
                transition={{ duration: 0.5 }}
              />
            </motion.div>
          </div>

          {/* Decorative corner bracket */}
          <motion.div
            className="absolute top-8 left-8"
            animate={{ opacity: hovered === 'left' ? 1 : 0.2 }}
          >
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <path d="M0 20V0H20" stroke="#00c7ce" strokeWidth="2" />
            </svg>
          </motion.div>
        </motion.div>

        {/* CENTER DIVIDER - VS LINE */}
        <div className="relative z-30 flex w-[3px] flex-col items-center justify-center">
          {/* Spark line */}
          <div className="absolute inset-0 overflow-hidden">
            <motion.div
              className="absolute left-0 w-full"
              animate={{
                background: hovered
                  ? 'linear-gradient(180deg, transparent 0%, rgba(255,255,255,0.8) 50%, transparent 100%)'
                  : 'linear-gradient(180deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%)',
                boxShadow: hovered
                  ? '0 0 15px rgba(255,255,255,0.5), 0 0 30px rgba(255,255,255,0.2)'
                  : '0 0 5px rgba(255,255,255,0.1)',
              }}
              style={{ top: 0, bottom: 0 }}
              transition={{ duration: 0.3 }}
            />
            {/* Spark particles */}
            {hovered && (
              <>
                <motion.div
                  className="absolute left-1/2 h-1 w-1 -translate-x-1/2 rounded-full bg-white"
                  animate={{ top: ['20%', '80%', '30%', '70%', '20%'] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                  style={{ boxShadow: '0 0 6px #fff, 0 0 12px #fff' }}
                />
                <motion.div
                  className="absolute left-1/2 h-1 w-1 -translate-x-1/2 rounded-full bg-white"
                  animate={{ top: ['70%', '20%', '60%', '30%', '70%'] }}
                  transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
                  style={{ boxShadow: '0 0 6px #fff, 0 0 12px #fff' }}
                />
              </>
            )}
          </div>

          {/* VS badge */}
          <motion.div
            className="relative z-10 flex h-14 w-14 items-center justify-center rounded-full border border-white/20 bg-[#0a0a0f]"
            animate={{
              scale: hovered ? 1.15 : 1,
              borderColor: hovered === 'left'
                ? 'rgba(0, 199, 206, 0.6)'
                : hovered === 'right'
                  ? 'rgba(244, 114, 182, 0.6)'
                  : 'rgba(255, 255, 255, 0.2)',
              boxShadow: hovered === 'left'
                ? '0 0 20px rgba(0, 199, 206, 0.3)'
                : hovered === 'right'
                  ? '0 0 20px rgba(244, 114, 182, 0.3)'
                  : '0 0 0px transparent',
            }}
            transition={{ duration: 0.3 }}
          >
            <span className="font-display text-lg font-bold text-white/80">VS</span>
          </motion.div>
        </div>

        {/* RIGHT - MARLENE */}
        <motion.div
          className="relative cursor-pointer overflow-hidden"
          animate={{ flex: rightFlex }}
          transition={{ type: 'spring', stiffness: 200, damping: 30 }}
          onMouseEnter={() => setHovered('right')}
          onMouseLeave={() => setHovered(null)}
          onClick={() => handleClick('right')}
        >
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-bl from-[#1a0a1a] via-[#0a0a0f] to-[#0a0a0f]" />

          {/* Hover glow ring */}
          <motion.div
            className="pointer-events-none absolute inset-0"
            animate={{
              boxShadow: hovered === 'right'
                ? 'inset 0 0 120px rgba(244, 114, 182, 0.15)'
                : 'inset 0 0 0px rgba(244, 114, 182, 0)',
            }}
            transition={{ duration: 0.5 }}
          />

          {/* Character image - Marlene */}
          <motion.div
            className="absolute bottom-0 h-[85%] flex items-end justify-center w-full"
            animate={{
              scale: hovered === 'right' ? 1.05 : hovered === 'left' ? 0.92 : 1,
              filter: hovered === 'left'
                ? 'brightness(0.3) grayscale(0.5)'
                : hovered === 'right'
                  ? 'brightness(1.1) drop-shadow(0 0 40px rgba(244, 114, 182, 0.4))'
                  : 'brightness(0.85)',
            }}
            transition={{ type: 'spring', stiffness: 150, damping: 25 }}
          >
            <img
              src={marleneImage}
              alt="Marlene"
              className="h-full object-contain"
              draggable={false}
            />
          </motion.div>

          {/* Character name */}
          <div className="absolute right-0 bottom-12 w-full px-8 text-right">
            <motion.div
              animate={{
                opacity: hovered === 'left' ? 0.3 : 1,
                y: hovered === 'right' ? -8 : 0,
              }}
              transition={{ duration: 0.4 }}
            >
              <p className="mb-1 font-body text-sm tracking-[0.3em] text-marlene-400/60 uppercase">
                Landing
              </p>
              <h2
                className="font-display text-6xl font-bold tracking-tight"
                style={{
                  color: '#f472b6',
                  textShadow: hovered === 'right'
                    ? '0 0 30px rgba(244, 114, 182, 0.5), 0 0 60px rgba(244, 114, 182, 0.2)'
                    : 'none',
                }}
              >
                MARLENE
              </h2>
              <motion.div
                className="mt-3 ml-auto h-[2px] bg-marlene-primary"
                animate={{ width: hovered === 'right' ? '100%' : '40%' }}
                transition={{ duration: 0.5 }}
              />
            </motion.div>
          </div>

          {/* Decorative corner bracket */}
          <motion.div
            className="absolute top-8 right-8"
            animate={{ opacity: hovered === 'right' ? 1 : 0.2 }}
          >
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <path d="M40 20V0H20" stroke="#f472b6" strokeWidth="2" />
            </svg>
          </motion.div>
        </motion.div>
      </div>

      {/* Top center logo */}
      <div className="pointer-events-none absolute top-8 left-1/2 z-40 -translate-x-1/2 text-center">
        <motion.p
          className="font-display text-sm tracking-[0.5em] text-white/30 uppercase"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          Select Your Path
        </motion.p>
      </div>

      {/* Bottom center hint */}
      <motion.div
        className="pointer-events-none absolute bottom-6 left-1/2 z-40 -translate-x-1/2"
        animate={{ opacity: hovered ? 0 : 0.4 }}
      >
        <p className="font-body text-xs tracking-widest text-white/40">
          HOVER TO SELECT
        </p>
      </motion.div>

      {/* Scanline effect */}
      <div
        className="pointer-events-none absolute inset-0 z-40"
        style={{
          background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)',
        }}
      />
    </div>
  )
}
