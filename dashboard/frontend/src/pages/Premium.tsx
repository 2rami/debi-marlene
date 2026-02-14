import { useState } from 'react'
import Sidebar from '../components/common/Sidebar'

const PRESET_AMOUNTS = [1000, 3000, 5000, 10000]

export default function Premium() {
  const [amount, setAmount] = useState<number>(3000)
  const [customAmount, setCustomAmount] = useState('')
  const [isCustom, setIsCustom] = useState(false)
  const [loading, setLoading] = useState(false)

  const handlePreset = (value: number) => {
    setAmount(value)
    setIsCustom(false)
    setCustomAmount('')
  }

  const handleCustom = (value: string) => {
    const num = parseInt(value.replace(/[^0-9]/g, ''))
    setCustomAmount(value.replace(/[^0-9]/g, ''))
    if (!isNaN(num) && num > 0) {
      setAmount(num)
    }
    setIsCustom(true)
  }

  const handleDonate = async () => {
    if (amount < 100) return
    setLoading(true)

    try {
      // TODO: Implement Toss Payments checkout
      console.log('Starting donation:', amount)
    } catch (error) {
      console.error('Payment error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="max-w-lg mx-auto pt-8">
          {/* Header */}
          <div className="text-center mb-10">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-debi-primary to-marlene-primary flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-discord-text mb-2">
              개발자에게 커피 한 잔
            </h1>
            <p className="text-discord-muted text-sm">
              데비&마를렌의 서버 운영과 개발을 응원해주세요
            </p>
          </div>

          {/* Amount Selection */}
          <div className="bg-discord-dark rounded-2xl border border-discord-light/20 p-6">
            <p className="text-sm text-discord-muted mb-3">후원 금액</p>
            <div className="grid grid-cols-4 gap-2 mb-4">
              {PRESET_AMOUNTS.map(value => (
                <button
                  key={value}
                  onClick={() => handlePreset(value)}
                  className={`py-2.5 rounded-lg text-sm font-medium transition-all ${
                    amount === value && !isCustom
                      ? 'bg-gradient-to-r from-debi-primary to-marlene-primary text-white'
                      : 'bg-discord-darker text-discord-muted hover:text-discord-text hover:bg-discord-light/20'
                  }`}
                >
                  {value.toLocaleString()}원
                </button>
              ))}
            </div>

            {/* Custom Amount */}
            <div className="relative">
              <input
                type="text"
                value={isCustom ? customAmount : ''}
                onChange={(e) => handleCustom(e.target.value)}
                onFocus={() => {
                  setIsCustom(true)
                  setCustomAmount(String(amount))
                }}
                placeholder="직접 입력"
                className={`w-full px-4 py-3 rounded-lg border-2 text-sm transition-all outline-none ${
                  isCustom
                    ? 'bg-discord-darker border-debi-primary/50 text-discord-text'
                    : 'bg-discord-darker border-discord-light/20 text-discord-muted'
                }`}
              />
              {isCustom && customAmount && (
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-discord-muted">원</span>
              )}
            </div>

            {/* Total */}
            <div className="mt-6 pt-4 border-t border-discord-light/10 flex items-center justify-between">
              <span className="text-discord-muted text-sm">후원 금액</span>
              <span className="text-xl font-bold text-discord-text">{amount.toLocaleString()}원</span>
            </div>

            {/* Donate Button */}
            <button
              onClick={handleDonate}
              disabled={loading || amount < 100}
              className="w-full mt-4 py-3 rounded-lg font-semibold text-white btn-gradient transition-all disabled:opacity-50"
            >
              {loading ? '처리 중...' : '후원하기'}
            </button>
          </div>

          {/* Info */}
          <p className="text-center text-xs text-discord-muted mt-6">
            후원금은 서버 비용과 기능 개발에 사용됩니다
          </p>
        </div>
      </main>
    </div>
  )
}
