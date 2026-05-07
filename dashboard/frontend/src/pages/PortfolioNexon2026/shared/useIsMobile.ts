import { useEffect, useState } from 'react'

const BP = 768

export default function useIsMobile() {
  const [m, set] = useState(() =>
    typeof window === 'undefined' ? false : window.innerWidth <= BP,
  )
  useEffect(() => {
    const onResize = () => set(window.innerWidth <= BP)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])
  return m
}
