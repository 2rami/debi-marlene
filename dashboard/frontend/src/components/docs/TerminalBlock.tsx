import { useState } from 'react'
import { Copy, Check, Terminal } from 'lucide-react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'

interface TerminalBlockProps {
    command: string
    output?: string
    showCopy?: boolean
    className?: string
    language?: string
}

export default function TerminalBlock({
    command,
    output,
    showCopy = true,
    className
}: TerminalBlockProps) {
    const [copied, setCopied] = useState(false)

    const handleCopy = () => {
        navigator.clipboard.writeText(command)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className={clsx("rounded-xl overflow-hidden bg-[#1e1e1e] border border-white/10 shadow-lg my-4", className)}>
            {/* Terminal Title Bar */}
            <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-white/5">
                <div className="flex items-center gap-2">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
                        <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
                        <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
                    </div>
                </div>
                <div className="text-xs text-gray-400 font-mono flex items-center gap-1.5 opacity-50">
                    <Terminal className="w-3 h-3" />
                    bash
                </div>
            </div>

            {/* Terminal Content */}
            <div className="p-4 font-mono text-sm relative group">
                <div className="flex items-start gap-4">
                    <div className="flex-1 overflow-x-auto">
                        <div className="flex items-center gap-2 text-white">
                            <span className="text-green-400 font-bold shrink-0">$</span>
                            <span className="break-all">{command}</span>
                        </div>
                        {output && (
                            <div className="mt-2 text-gray-400 whitespace-pre-wrap pl-5 border-l-2 border-white/10 ml-0.5">
                                {output}
                            </div>
                        )}
                    </div>

                    {showCopy && (
                        <motion.button
                            whileTap={{ scale: 0.9 }}
                            onClick={handleCopy}
                            className="mt-0.5 p-1.5 rounded-lg bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
                            title="명령어 복사"
                        >
                            {copied ? (
                                <Check className="w-4 h-4 text-green-400" />
                            ) : (
                                <Copy className="w-4 h-4" />
                            )}
                        </motion.button>
                    )}
                </div>
            </div>
        </div>
    )
}
