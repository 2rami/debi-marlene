import { motion, AnimatePresence } from 'framer-motion'
import { X, Sparkles } from 'lucide-react'

interface PatchNotesModalProps {
    isOpen: boolean
    onClose: () => void
}

interface PatchNote {
    version: string
    date: string
    type: 'feature' | 'fix' | 'improvement'
    title: string
    description: string
}

const patchNotes: PatchNote[] = [
    {
        version: '1.2.0',
        date: '2025.05.20',
        type: 'feature',
        title: '대시보드 & 모바일 최적화',
        description: '웹패널과 대시보드가 모바일 환경에 최적화되었습니다! 이제 폰에서도 편하게 관리하세요.',
    },
    {
        version: '1.1.5',
        date: '2025.05.15',
        type: 'improvement',
        title: 'PWA 지원',
        description: '이제 데비&마를렌 대시보드를 앱처럼 홈 화면에 추가하여 사용할 수 있습니다.',
    },
    {
        version: '1.1.0',
        date: '2025.05.01',
        type: 'fix',
        title: '이미지 로딩 & 성능 개선',
        description: '일부 이미지가 로딩되지 않는 문제를 수정하고 전반적인 로딩 속도를 개선했습니다.',
    },
]

export default function PatchNotesModal({ isOpen, onClose }: PatchNotesModalProps) {
    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed inset-0 flex items-center justify-center z-50 p-4 pointer-events-none"
                    >
                        <div className="bg-discord-dark border border-white/10 rounded-2xl w-full max-w-lg max-h-[80vh] overflow-hidden shadow-2xl pointer-events-auto flex flex-col">
                            {/* Header */}
                            <div className="p-6 border-b border-white/5 flex items-center justify-between bg-white/5">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-gradient-to-br from-debi-primary/20 to-marlene-primary/20 text-debi-primary">
                                        <Sparkles className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-bold text-white">What's New</h2>
                                        <p className="text-sm text-discord-muted">최근 업데이트 소식</p>
                                    </div>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Content */}
                            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                                {patchNotes.map((note, idx) => (
                                    <div key={idx} className="relative pl-8 before:absolute before:left-3 before:top-8 before:bottom-[-24px] before:w-0.5 before:bg-white/10 last:before:hidden">
                                        <div className="absolute left-0 top-1.5 w-6 h-6 rounded-full border-4 border-discord-dark flex items-center justify-center bg-discord-dark z-10">
                                            <div className={`w-2.5 h-2.5 rounded-full ${note.type === 'feature' ? 'bg-debi-primary' :
                                                note.type === 'fix' ? 'bg-red-400' : 'bg-green-400'
                                                }`} />
                                        </div>

                                        <div className="bg-white/5 rounded-xl p-4 border border-white/5 hover:border-white/10 transition-colors">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className={`text-xs font-bold px-2 py-0.5 rounded uppercase ${note.type === 'feature' ? 'bg-debi-primary/20 text-debi-primary' :
                                                    note.type === 'fix' ? 'bg-red-500/20 text-red-400' :
                                                        'bg-green-500/20 text-green-400'
                                                    }`}>
                                                    {note.type}
                                                </span>
                                                <span className="text-xs text-discord-muted">{note.date}</span>
                                            </div>
                                            <h3 className="font-bold text-white mb-1 group-hover:text-debi-primary transition-colors">
                                                {note.title}
                                                <span className="ml-2 text-xs font-normal text-discord-muted opacity-50">v{note.version}</span>
                                            </h3>
                                            <p className="text-sm text-gray-300 leading-relaxed">
                                                {note.description}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="p-4 border-t border-white/5 bg-black/20 text-center">
                                <p className="text-xs text-discord-muted">
                                    더 많은 업데이트 소식은 <a href="https://discord.gg/aDemda3qC9" target="_blank" className="text-debi-primary hover:underline">공식 디스코드</a>에서 확인하세요.
                                </p>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    )
}
