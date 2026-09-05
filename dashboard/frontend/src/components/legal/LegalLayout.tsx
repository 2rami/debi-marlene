import Header from '../common/Header'

/**
 * 이용약관·개인정보처리방침 공통 레이아웃.
 *
 * 두 문서는 원래 한 페이지의 탭이었다. 탭은 선택된 쪽만 DOM 에 올라가므로
 * 개인정보처리방침이 크롤러에게 통째로 보이지 않았다 — 광고 심사는 이 문서의
 * 존재를 요구한다. 그래서 /terms 와 /privacy 두 주소로 갈랐고,
 * 탭처럼 보이던 자리는 실제 링크로 바꿨다.
 */
export default function LegalLayout({ active, title, updated, children }: {
  active: 'terms' | 'privacy'
  title: string
  updated: string
  children: React.ReactNode
}) {
  const tabClass = (mine: 'terms' | 'privacy', color: string) =>
    active === mine
      ? `${color} border-b-2 pb-2 -mb-[18px]`
      : 'text-discord-muted hover:text-white pb-2'

  return (
    <div className="min-h-screen bg-discord-darkest">
      <Header />
      <div className="max-w-3xl mx-auto px-6 py-24">
        <nav className="flex gap-4 mb-8 border-b border-white/10 pb-4">
          <a href="/terms/" className={`text-xl font-bold transition-colors ${tabClass('terms', 'text-debi-primary border-debi-primary')}`}>
            이용약관
          </a>
          <a href="/privacy/" className={`text-xl font-bold transition-colors ${tabClass('privacy', 'text-marlene-primary border-marlene-primary')}`}>
            개인정보처리방침
          </a>
        </nav>

        <div className="mb-10">
          <h1 className="text-3xl font-bold text-white mb-2">{title}</h1>
          <p className="text-discord-muted text-sm">최종 수정일: {updated}</p>
        </div>

        {children}
      </div>
    </div>
  )
}

export function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-3">{title}</h2>
      <div>{children}</div>
    </div>
  )
}
