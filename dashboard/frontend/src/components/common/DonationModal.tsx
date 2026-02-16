import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CreditCard, MessageCircle, Copy, ExternalLink, RefreshCw } from 'lucide-react'
import { QRCodeSVG } from 'qrcode.react'

// Images
import KAKAO_QR from '../../assets/images/kakao-qr.jpg'

interface DonationModalProps {
    isOpen: boolean
    onClose: () => void
}

const PRESET_AMOUNTS = [1000, 3000, 5000, 10000, 30000, 50000]

export default function DonationModal({ isOpen, onClose }: DonationModalProps) {
    const [activeTab, setActiveTab] = useState<'toss' | 'kakao'>('toss')
    const [amount, setAmount] = useState<number>(3000)
    const [customAmount, setCustomAmount] = useState('')
    const [isCustom, setIsCustom] = useState(false)

    // Toss Bank Info
    const TOSS_BANK_ACCOUNT = '1000-4242-1882'

    // KakaoPay URL
    // 기본 링크: https://qr.kakaopay.com/281006011000009859887675
    // 금액 지정 시도: ?money={amount} (작동 여부 확인 필요)
    const KAKAO_PAY_LINK = 'https://qr.kakaopay.com/281006011000009859887675'

    const handleAmountSelect = (value: number) => {
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

    const getTossLink = () => {
        // supertoss://send?bank=토스뱅크&accountNo=100042421882&amount=3000
        return `supertoss://send?bank=토스뱅크&accountNo=${TOSS_BANK_ACCOUNT.replace(/-/g, '')}&amount=${amount}`
    }

    const getKakaoLink = () => {
        // 시도: 금액 파라미터 추가
        return `${KAKAO_PAY_LINK}${amount > 0 ? `?money=${amount}` : ''}`
    }

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        alert('복사되었습니다!')
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
                        className="relative w-full max-w-md bg-[#1a1b1e] rounded-3xl border border-white/10 shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto"
                    >
                        {/* Close Button */}
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 p-2 text-gray-400 hover:text-white rounded-full hover:bg-white/10 transition-colors z-10"
                        >
                            <X size={24} />
                        </button>

                        <div className="p-6 md:p-8">
                            <div className="text-center mb-6">
                                <h2 className="text-2xl font-bold text-white mb-2">
                                    개발자 후원하기
                                </h2>
                                <p className="text-gray-400 text-sm">
                                    따뜻한 커피 한 잔은 큰 힘이 됩니다 ☕
                                </p>
                            </div>

                            {/* Amount Selection */}
                            <div className="mb-6">
                                <div className="grid grid-cols-3 gap-2 mb-3">
                                    {PRESET_AMOUNTS.map((amt) => (
                                        <button
                                            key={amt}
                                            onClick={() => handleAmountSelect(amt)}
                                            className={`py-2 rounded-xl text-sm font-medium transition-all ${amount === amt && !isCustom
                                                    ? 'bg-white text-black font-bold shadow-lg'
                                                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                                                }`}
                                        >
                                            {amt.toLocaleString()}원
                                        </button>
                                    ))}
                                </div>

                                {/* Custom Amount Input */}
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={isCustom ? customAmount : ''}
                                        onChange={(e) => handleCustomChange(e.target.value)}
                                        onFocus={() => {
                                            setIsCustom(true)
                                            setCustomAmount(amount > 0 ? String(amount) : '')
                                        }}
                                        placeholder="직접 입력"
                                        className={`w-full bg-[#0f0f0f] px-4 py-3 rounded-xl border outline-none transition-all font-medium text-center ${isCustom
                                                ? 'border-debi-primary text-white ring-1 ring-debi-primary'
                                                : 'border-white/10 text-gray-400 hover:border-white/20'
                                            }`}
                                    />
                                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 text-sm">KRW</span>
                                </div>
                            </div>

                            {/* Tabs */}
                            <div className="flex bg-black/20 p-1 rounded-xl mb-6">
                                <button
                                    onClick={() => setActiveTab('toss')}
                                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all ${activeTab === 'toss'
                                            ? 'bg-blue-500 text-white shadow-lg'
                                            : 'text-gray-400 hover:text-white'
                                        }`}
                                >
                                    <CreditCard size={16} />
                                    Toss
                                </button>
                                <button
                                    onClick={() => setActiveTab('kakao')}
                                    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-bold transition-all ${activeTab === 'kakao'
                                            ? 'bg-yellow-400 text-black shadow-lg'
                                            : 'text-gray-400 hover:text-white'
                                        }`}
                                >
                                    <MessageCircle size={16} />
                                    KakaoPay
                                </button>
                            </div>

                            {/* QR Code Display */}
                            <div className="bg-white rounded-2xl p-6 mb-6 aspect-square flex flex-col items-center justify-center overflow-hidden relative group">
                                <AnimatePresence mode="wait">
                                    {/* Toss Bank Dynamic QR */}
                                    {activeTab === 'toss' ? (
                                        <motion.div
                                            key="toss"
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            exit={{ opacity: 0, scale: 0.9 }}
                                            transition={{ duration: 0.2 }}
                                            className="flex flex-col items-center w-full h-full"
                                        >
                                            {/* Dynamic QR Code for encoded URL */}
                                            <QRCodeSVG
                                                value={getTossLink()}
                                                size={200}
                                                level="H"
                                                includeMargin={true}
                                            />
                                            <p className="mt-4 text-sm font-bold text-blue-600">
                                                {amount.toLocaleString()}원 보내기
                                            </p>
                                        </motion.div>
                                    ) : (
                                        <motion.div
                                            key="kakao"
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            exit={{ opacity: 0, scale: 0.9 }}
                                            transition={{ duration: 0.2 }}
                                            className="flex flex-col items-center w-full h-full"
                                        >
                                            {/* Try Dynamic Link QR first (may not work deep link without scheme), 
                          fallback to static image if needed, but here we try encoding the link */}
                                            <QRCodeSVG
                                                value={getKakaoLink()}
                                                size={200}
                                                level="H"
                                                includeMargin={true}
                                                imageSettings={{
                                                    src: KAKAO_QR,
                                                    x: undefined,
                                                    y: undefined,
                                                    height: 40,
                                                    width: 40,
                                                    excavate: true,
                                                }}
                                            />
                                            <p className="mt-4 text-sm font-bold text-yellow-600">
                                                {amount.toLocaleString()}원 보내기
                                            </p>
                                        </motion.div>
                                    )}
                                </AnimatePresence>

                                {/* Scan Instruction Overlay */}
                                <div className="absolute inset-0 bg-white/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                    <p className="text-gray-800 font-bold text-sm">
                                        카메라로 스캔하여 송금하기
                                    </p>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="space-y-3">
                                {activeTab === 'toss' ? (
                                    <>
                                        <a
                                            href={getTossLink()}
                                            className="w-full py-3.5 rounded-xl bg-blue-500 hover:bg-blue-600 text-white font-bold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-blue-500/20"
                                        >
                                            <ExternalLink size={18} />
                                            토스 앱으로 열기
                                        </a>
                                        <button
                                            onClick={() => copyToClipboard(TOSS_BANK_ACCOUNT)}
                                            className="w-full py-3.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 font-medium flex items-center justify-center gap-2 transition-colors border border-white/5"
                                        >
                                            <Copy size={18} />
                                            계좌번호 복사하기 ({TOSS_BANK_ACCOUNT})
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        <a
                                            href={getKakaoLink()}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="w-full py-3.5 rounded-xl bg-[#FAE100] hover:bg-[#FADB00] text-[#371D1E] font-bold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-yellow-500/20"
                                        >
                                            <ExternalLink size={18} />
                                            카카오페이 열기
                                        </a>
                                    </>
                                )}
                            </div>

                            <div className="mt-6 text-center">
                                <p className="text-xs text-gray-600 bg-white/5 rounded-lg py-2 px-3 inline-block">
                                    QR 코드를 스캔하거나 앱 열기 버튼을 눌러주세요
                                </p>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    )
}
