import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Coffee, Pizza, Zap, Heart, X } from 'lucide-react'

const DONATION_TIERS = [
    { amount: 1000, icon: Coffee, label: '캔커피', desc: '카페인 충전!' },
    { amount: 3000, icon: Zap, label: '에너지드링크', desc: '코딩 불태우기' },
    { amount: 5000, icon: Pizza, label: '조각피자', desc: '든든한 간식' },
    { amount: 10000, icon: Heart, label: '치킨 한마리', desc: '최고의 응원' },
]

interface DonationModalProps {
    isOpen: boolean
    onClose: () => void
}

export default function DonationModal({ isOpen, onClose }: DonationModalProps) {
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
            onClose()
        } catch (error) {
            console.error('Donation error:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                    />

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="relative w-full max-w-2xl bg-[#0f0f0f] rounded-3xl border border-white/10 shadow-2xl overflow-hidden"
                    >
                        {/* Close Button */}
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 p-2 text-gray-400 hover:text-white rounded-full hover:bg-white/10 transition-colors z-10"
                        >
                            <X size={24} />
                        </button>

                        <div className="p-8">
                            <div className="text-center mb-8">
                                <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-debi-primary to-marlene-primary mb-2">
                                    개발자 응원하기
                                </h2>
                                <p className="text-gray-400 text-sm">
                                    데비&마를렌이 더 열심히 일할 수 있도록 간식을 선물해주세요! 🧁
                                </p>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                                {DONATION_TIERS.map((tier) => (
                                    <motion.button
                                        key={tier.amount}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => handleTierSelect(tier.amount)}
                                        className={`relative flex flex-col items-center p-3 rounded-2xl border transition-all duration-300 ${amount === tier.amount && !isCustom
                                                ? 'bg-gradient-to-br from-debi-primary/20 to-marlene-primary/20 border-debi-primary/50 ring-2 ring-debi-primary/20'
                                                : 'bg-[#1a1b1e] border-white/5 hover:border-white/10 hover:bg-[#202225]'
                                            }`}
                                    >
                                        <div className={`p-2 rounded-full mb-2 ${amount === tier.amount && !isCustom
                                                ? 'bg-gradient-to-br from-debi-primary to-marlene-primary text-white shadow-lg'
                                                : 'bg-white/5 text-gray-400'
                                            }`}>
                                            <tier.icon size={20} />
                                        </div>
                                        <div className="font-bold text-white text-sm mb-0.5">{tier.label}</div>
                                        <div className="text-[10px] text-debi-primary font-medium mb-0.5">
                                            {tier.amount.toLocaleString()}원
                                        </div>
                                        <div className="text-[9px] text-gray-500">{tier.desc}</div>
                                    </motion.button>
                                ))}
                            </div>

                            <div className="bg-[#1a1b1e] rounded-2xl p-6 border border-white/5">
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
                                                className="w-full bg-[#0f0f0f] text-white px-4 py-3 rounded-xl border border-white/10 focus:border-debi-primary focus:ring-1 focus:ring-debi-primary outline-none transition-all font-medium placeholder-gray-600"
                                            />
                                            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 font-medium text-sm">
                                                KRW
                                            </span>
                                        </div>
                                    </div>

                                    <div className="w-full md:w-1/2 flex flex-col items-center">
                                        <div className="text-center mb-3">
                                            <span className="text-gray-400 text-xs">보내실 금액</span>
                                            <div className="text-2xl font-bold text-white">
                                                {amount.toLocaleString()}
                                                <span className="text-base text-debi-primary ml-1">원</span>
                                            </div>
                                        </div>

                                        <button
                                            onClick={handleDonate}
                                            disabled={loading || amount < 100}
                                            className="w-full py-3 rounded-xl font-bold text-white shadow-lg shadow-debi-primary/20 bg-gradient-to-r from-debi-primary to-marlene-primary hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                                        >
                                            {loading ? '처리 중...' : '후원하기 🎁'}
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <p className="text-center text-[10px] text-gray-600 mt-6">
                                후원금은 서버 운영비와 개발자의 커피값으로 소중하게 사용됩니다.<br />
                                항상 응원해 주셔서 감사합니다! 🙇‍♂️
                            </p>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    )
}
