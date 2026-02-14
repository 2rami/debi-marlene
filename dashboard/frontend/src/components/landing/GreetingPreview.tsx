import { useState } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, Download, Sparkles } from 'lucide-react'
import PREVIEW_BG from '../../assets/images/feature-bg.jpg'

export default function GreetingPreview() {
    const [nickname, setNickname] = useState('여행하는 데비')
    const [isGenerating, setIsGenerating] = useState(false)
    const [currentGreeting, setCurrentGreeting] = useState('오늘도 즐거운 이터널 리턴 되세요!')

    const greetings = [
        '오늘도 즐거운 이터널 리턴 되세요!',
        '루미아 섬에 오신 것을 환영합니다!',
        '오늘 저녁은 치킨이닭!',
        '실험체, 준비 완료.',
        '함께라면 두렵지 않아요!',
    ]

    const handleGenerate = () => {
        setIsGenerating(true)
        setTimeout(() => {
            const randomGreeting = greetings[Math.floor(Math.random() * greetings.length)]
            setCurrentGreeting(randomGreeting)
            setIsGenerating(false)
        }, 800)
    }

    return (
        <div className="w-full max-w-4xl mx-auto p-6">
            <div className="bg-discord-dark rounded-2xl border border-discord-light/20 overflow-hidden shadow-2xl">
                <div className="p-6 border-b border-discord-light/20 flex flex-col md:flex-row gap-4 items-center justify-between">
                    <div>
                        <h3 className="text-xl font-bold flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-debi-primary" />
                            <span className="gradient-text">인사말 미리보기</span>
                        </h3>
                        <p className="text-sm text-discord-muted mt-1">
                            닉네임을 입력하고 나만의 인사말 카드를 만들어보세요
                        </p>
                    </div>

                    <div className="flex gap-2 w-full md:w-auto">
                        <input
                            type="text"
                            value={nickname}
                            onChange={(e) => setNickname(e.target.value)}
                            placeholder="닉네임 입력"
                            className="flex-1 md:w-64 bg-discord-darker border border-discord-light/20 rounded-lg px-4 py-2 focus:outline-none focus:border-debi-primary transition-colors"
                        />
                        <button
                            onClick={handleGenerate}
                            disabled={isGenerating}
                            className="btn-gradient p-2 rounded-lg text-white disabled:opacity-50 transition-opacity"
                        >
                            <RefreshCw className={`w-5 h-5 ${isGenerating ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </div>

                <div className="relative aspect-video bg-gray-900 group overflow-hidden">
                    {/* Background Image Area */}
                    <div className="absolute inset-0">
                        <img
                            src={PREVIEW_BG}
                            alt="Background"
                            className="w-full h-full object-cover opacity-60 group-hover:scale-105 transition-transform duration-700"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                    </div>

                    {/* Content Overlay */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                        <motion.div
                            key={currentGreeting}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="relative z-10"
                        >
                            <h2 className="text-4xl md:text-6xl font-black text-white mb-4 drop-shadow-[0_4px_4px_rgba(0,0,0,0.5)]">
                                Welcome, {nickname}
                            </h2>
                            <div className="inline-block bg-white/10 backdrop-blur-md border border-white/20 px-6 py-3 rounded-full">
                                <p className="text-xl text-white/90 font-medium">
                                    {currentGreeting}
                                </p>
                            </div>
                        </motion.div>
                    </div>

                    {/* Decoration */}
                    <div className="absolute top-6 right-6 z-20">
                        <div className="w-12 h-12 rounded-full border-2 border-white/30 p-1">
                            <div className="w-full h-full rounded-full bg-gradient-to-br from-debi-primary to-marlene-primary animate-pulse" />
                        </div>
                    </div>

                    <div className="absolute bottom-6 left-6 z-20 flex gap-2">
                        <span className="px-3 py-1 rounded-full bg-black/50 backdrop-blur text-xs font-mono text-white/70 border border-white/10">
                            SERVER: LUMIA ISLAND
                        </span>
                        <span className="px-3 py-1 rounded-full bg-debi-primary/20 backdrop-blur text-xs font-mono text-debi-primary border border-debi-primary/20">
                            #NEW_CHALLENGER
                        </span>
                    </div>
                </div>

                <div className="p-4 bg-discord-darker flex justify-end gap-2">
                    <button className="text-xs text-discord-muted hover:text-white flex items-center gap-1 transition-colors">
                        <Download className="w-4 h-4" />
                        이미지 저장 (실제 기능 체험)
                    </button>
                </div>
            </div>
        </div>
    )
}
