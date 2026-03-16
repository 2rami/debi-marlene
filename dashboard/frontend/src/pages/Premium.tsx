import { useState } from 'react'
import { motion } from 'framer-motion'
import { Coffee, Pizza, Zap, Heart } from 'lucide-react'
import Sidebar from '../components/common/Sidebar'

const DONATION_TIERS = [
  { amount: 1000, icon: Coffee, label: '캔커피', desc: '카페인 충전!' },
  { amount: 3000, icon: Zap, label: '에너지드링크', desc: '코딩 불태우기' },
  { amount: 5000, icon: Pizza, label: '조각피자', desc: '든든한 간식' },
  { amount: 10000, icon: Heart, label: '치킨 한마리', desc: '최고의 응원' },
]

export default function Premium() {
  const [amount, setAmount] = useState<number>(3000)
  const [customAmount, setCustomAmount] = useState('')
  const [isCustom, setIsCustom] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleTierSelect = (value: number) => {
    setAmount(value)
    setIsCustom(false)
    setCustomAmount('')
  }

  const handleCustomChange = (value: string) => {
    const num = parseInt(value.replace(/[^0-9]/g, ''))
    setCustomAmount(value.replace(/[^0-9]/g, ''))
    if (!isNaN(num) && num > 0) {
      setAmount(num)
    } else {
      setAmount(0)
    }
    setIsCustom(true)
  }

  const handleDonate = async () => {
    if (amount < 100) return
    setLoading(true)

    try {
      // TODO: Toss Payments integration
      console.log('Donation started:', amount)
      // Simulate delay
      await new Promise(resolve => setTimeout(resolve, 1000))
    } catch (error) {
      console.error('Donation error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-[#0f0f0f]">
      <Sidebar />

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-10"
          >
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-debi-primary to-marlene-primary mb-3">
              개발자 응원하기
            </h1>
            <p className="text-gray-400">
              데비&마를렌이 더 열심히 일할 수 있도록 간식을 선물해주세요!
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {DONATION_TIERS.map((tier) => (
              <motion.button
                key={tier.amount}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleTierSelect(tier.amount)}
                className={`relative flex flex-col items-center p-4 rounded-2xl border transition-all duration-300 ${amount === tier.amount && !isCustom
                    ? 'bg-gradient-to-br from-debi-primary/20 to-marlene-primary/20 border-debi-primary/50 ring-2 ring-debi-primary/20'
                    : 'bg-[#1a1b1e] border-white/5 hover:border-white/10 hover:bg-[#202225]'
                  }`}
              >
                <div className={`p-3 rounded-full mb-3 ${amount === tier.amount && !isCustom
                    ? 'bg-gradient-to-br from-debi-primary to-marlene-primary text-white shadow-lg'
                    : 'bg-white/5 text-gray-400'
                  }`}>
                  <tier.icon size={24} />
                </div>
                <div className="font-bold text-white mb-1">{tier.label}</div>
                <div className="text-xs text-debi-primary font-medium mb-1">
                  {tier.amount.toLocaleString()}원
                </div>
                <div className="text-[10px] text-gray-500">{tier.desc}</div>
              </motion.button>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-[#1a1b1e] rounded-3xl p-6 border border-white/5 shadow-xl"
          >
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="w-full md:w-1/2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block">
                  직접 입력하기
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={isCustom ? customAmount : ''}
                    onChange={(e) => handleCustomChange(e.target.value)}
                    onFocus={() => {
                      setIsCustom(true)
                      setCustomAmount(amount > 0 ? String(amount) : '')
                    }}
                    placeholder="금액을 입력하세요"
                    className="w-full bg-[#0f0f0f] text-white px-5 py-4 rounded-xl border border-white/10 focus:border-debi-primary focus:ring-1 focus:ring-debi-primary outline-none transition-all text-lg font-medium placeholder-gray-600"
                  />
                  <span className="absolute right-5 top-1/2 -translate-y-1/2 text-gray-500 font-medium">
                    KRW
                  </span>
                </div>
              </div>

              <div className="w-full md:w-1/2 flex flex-col items-center">
                <div className="text-center mb-4">
                  <span className="text-gray-400 text-sm">보내실 금액</span>
                  <div className="text-3xl font-bold text-white mt-1">
                    {amount.toLocaleString()}
                    <span className="text-lg text-debi-primary ml-1">원</span>
                  </div>
                </div>

                <button
                  onClick={handleDonate}
                  disabled={loading || amount < 100}
                  className="w-full py-4 rounded-xl font-bold text-white shadow-lg shadow-debi-primary/20 bg-gradient-to-r from-debi-primary to-marlene-primary hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? '처리 중...' : '후원하기'}
                </button>
              </div>
            </div>
          </motion.div>

          <p className="text-center text-xs text-gray-600 mt-8">
            후원금은 서버 운영비와 개발에 소중하게 사용됩니다.<br />
            항상 응원해 주셔서 감사합니다!
          </p>
        </div>
      </main>
    </div>
  )
}
