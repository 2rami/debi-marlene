import creditSvg from '../../assets/credit/credit.svg'

interface Props {
  size?: number
  className?: string
}

export default function CreditIcon({ size = 18, className = '' }: Props) {
  return (
    <img
      src={creditSvg}
      width={size}
      height={size}
      alt=""
      aria-hidden
      draggable={false}
      className={`inline-block select-none ${className}`}
      style={{ width: size, height: size }}
    />
  )
}
