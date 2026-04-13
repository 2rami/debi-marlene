import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import { useTheme } from '../../contexts/ThemeContext'

interface MermaidDiagramProps {
  chart: string
  className?: string
  id?: string
}

let idCounter = 0

export default function MermaidDiagram({ chart, className = '', id }: MermaidDiagramProps) {
  const ref = useRef<HTMLDivElement>(null)
  const { isDark } = useTheme()
  const [svg, setSvg] = useState<string>('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: isDark ? 'dark' : 'default',
      themeVariables: isDark
        ? {
            primaryColor: '#0B5ED7',
            primaryTextColor: '#e5e7eb',
            primaryBorderColor: '#6DC8E8',
            lineColor: '#6DC8E8',
            secondaryColor: '#1e293b',
            tertiaryColor: '#0f172a',
            background: 'transparent',
            fontFamily: 'Paperlogy, system-ui, sans-serif',
          }
        : {
            primaryColor: '#e8f4ff',
            primaryTextColor: '#0f172a',
            primaryBorderColor: '#0B5ED7',
            lineColor: '#0B5ED7',
            secondaryColor: '#f1f5f9',
            tertiaryColor: '#ffffff',
            background: 'transparent',
            fontFamily: 'Paperlogy, system-ui, sans-serif',
          },
      flowchart: {
        curve: 'basis',
        padding: 20,
        htmlLabels: true,
      },
    })

    const uniqueId = id ?? `mermaid-${++idCounter}-${Date.now()}`
    let cancelled = false

    mermaid
      .render(uniqueId, chart)
      .then(({ svg: renderedSvg }) => {
        if (!cancelled) {
          setSvg(renderedSvg)
          setError(null)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err?.message ?? 'Mermaid render failed')
        }
      })

    return () => {
      cancelled = true
    }
  }, [chart, isDark, id])

  if (error) {
    return (
      <div className={`p-4 rounded-xl border border-red-500/30 bg-red-500/5 text-sm ${className}`}>
        <div className="font-bold text-red-400 mb-1">Mermaid render error</div>
        <pre className="text-xs text-red-300 whitespace-pre-wrap">{error}</pre>
      </div>
    )
  }

  return (
    <div
      ref={ref}
      className={`mermaid-diagram w-full flex items-center justify-center ${className}`}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
}
