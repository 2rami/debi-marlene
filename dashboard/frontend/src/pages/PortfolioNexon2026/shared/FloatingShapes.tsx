import { C } from './colors'

/**
 * Hero 배경 떠다니는 픽토그램 SVG
 * 넥슨 아이덴티티를 살린 Playful & Trendy 기하학 도형 및 무빙
 */
export default function FloatingShapes() {
  return (
    <svg
      aria-hidden
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
      }}
      viewBox="0 0 1200 900"
      preserveAspectRatio="xMidYMid slice"
    >
      <style>
        {`
          @keyframes float-slow {
            0% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-30px) rotate(10deg); }
            100% { transform: translateY(0px) rotate(0deg); }
          }
          @keyframes float-fast {
            0% { transform: translateY(0px) scale(1); }
            50% { transform: translateY(-50px) scale(1.1); }
            100% { transform: translateY(0px) scale(1); }
          }
          @keyframes spin-slow {
            100% { transform: rotate(360deg); }
          }
          @keyframes pulse-soft {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 0.8; transform: scale(1.2); }
          }
          .anim-float-1 { animation: float-slow 8s ease-in-out infinite; transform-origin: center; }
          .anim-float-2 { animation: float-fast 6s ease-in-out infinite; transform-origin: center; }
          .anim-spin { animation: spin-slow 15s linear infinite; transform-origin: center; }
          .anim-pulse { animation: pulse-soft 4s ease-in-out infinite; transform-origin: center; }
        `}
      </style>

      {/* Blue Plus (Nexon Blue) */}
      <g className="anim-float-1" transform="translate(180, 150)">
        <path d="M-15,-40 h30 v25 h25 v30 h-25 v25 h-30 v-25 h-25 v-30 h25 z" fill={C.nexonLightBlue} opacity="0.6" />
      </g>

      {/* Yellow Ring */}
      <g className="anim-float-2" transform="translate(1000, 200)">
        <circle cx="0" cy="0" r="50" fill="none" stroke={C.yellow} strokeWidth="16" opacity="0.8" />
      </g>

      {/* Lime Triangle */}
      <g className="anim-spin" transform="translate(950, 600)">
        <polygon points="0,-40 35,20 -35,20" fill={C.lime} opacity="0.7" />
      </g>

      {/* Coral Circle */}
      <g className="anim-float-1" transform="translate(200, 700)">
        <circle cx="0" cy="0" r="80" fill={C.coral} opacity="0.5" />
      </g>

      {/* Blue Square with dots */}
      <g className="anim-float-2" transform="translate(700, 120)">
        <rect x="-30" y="-30" width="60" height="60" rx="16" fill="none" stroke={C.nexonBlue} strokeWidth="12" opacity="0.5" />
      </g>

      {/* Decorative Dots */}
      <circle cx="850" cy="800" r="10" fill={C.lavender} className="anim-pulse" style={{ transformOrigin: '850px 800px' }} />
      <circle cx="100" cy="400" r="8" fill={C.nexonLightBlue} className="anim-pulse" style={{ transformOrigin: '100px 400px', animationDelay: '1s' }} />
      <circle cx="500" cy="850" r="12" fill={C.yellow} className="anim-pulse" style={{ transformOrigin: '500px 850px', animationDelay: '2s' }} />
    </svg>
  )
}
