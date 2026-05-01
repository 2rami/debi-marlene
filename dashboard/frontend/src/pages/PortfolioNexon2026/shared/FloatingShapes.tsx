import { C } from './colors'

/**
 * Hero 배경 떠다니는 픽토그램 SVG
 * 게임 포스터의 라운드 도형 무드
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
      <rect x="80" y="180" width="120" height="120" rx="28" fill={C.cream} opacity="0.45" transform="rotate(-12 140 240)" />
      <circle cx="1080" cy="220" r="60" fill={C.honey} opacity="0.35" />
      {/* 5각 별 */}
      <Star cx={950} cy={540} r={42} fill={C.lime} opacity={0.6} />
      <circle cx="1100" cy="780" r="180" fill={C.cream} opacity="0.35" />
      <rect x="60" y="660" width="180" height="180" rx="40" fill={C.bgMid} opacity="0.35" transform="rotate(8 150 750)" />
      <circle cx="700" cy="120" r="8" fill={C.honey} opacity="0.7" />
      <circle cx="200" cy="500" r="6" fill={C.lime} opacity="0.7" />
      <circle cx="500" cy="780" r="10" fill={C.honey} opacity="0.5" />
    </svg>
  )
}

function Star({ cx, cy, r, fill, opacity }: { cx: number; cy: number; r: number; fill: string; opacity: number }) {
  const points: string[] = []
  for (let i = 0; i < 10; i++) {
    const angle = (Math.PI / 5) * i - Math.PI / 2
    const radius = i % 2 === 0 ? r : r * 0.45
    const x = cx + radius * Math.cos(angle)
    const y = cy + radius * Math.sin(angle)
    points.push(`${x.toFixed(1)},${y.toFixed(1)}`)
  }
  return <polygon points={points.join(' ')} fill={fill} opacity={opacity} />
}
