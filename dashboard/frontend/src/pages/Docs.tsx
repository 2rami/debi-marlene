import { useState } from 'react'
import { Link } from 'react-router-dom'
import Header from '../components/common/Header'

interface DocSection {
  id: string
  title: string
  content: React.ReactNode
}

const docSections: DocSection[] = [
  {
    id: 'getting-started',
    title: '시작하기',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-discord-text">봇 초대하기</h3>
        <p className="text-discord-muted">
          Debi & Marlene 봇을 서버에 초대하려면 관리자 권한이 필요합니다.
          메인 페이지의 "봇 초대하기" 버튼을 클릭하여 봇을 서버에 추가하세요.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">권한 설정</h3>
        <p className="text-discord-muted">
          봇이 정상적으로 작동하려면 다음 권한이 필요합니다:
        </p>
        <ul className="list-disc list-inside text-discord-muted space-y-1 ml-4">
          <li>메시지 읽기/보내기</li>
          <li>임베드 링크</li>
          <li>음성 채널 연결 및 말하기 (TTS/음악)</li>
          <li>멤버 관리 (제재 기능)</li>
        </ul>
      </div>
    ),
  },
  {
    id: 'eternal-return',
    title: '이터널리턴',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-discord-text">전적 검색</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/이터널리턴 전적 닉네임:플레이어명</code>
        </p>
        <p className="text-discord-muted">
          플레이어의 최근 시즌 전적, 티어, 승률 등을 확인할 수 있습니다.
          팀원 정보도 함께 표시됩니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">캐릭터 통계</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/이터널리턴 통계</code>
        </p>
        <p className="text-discord-muted">
          다이아몬드 이상 티어의 캐릭터별 통계를 확인합니다.
          픽률, 승률, 평균 등수 등을 볼 수 있습니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">추천 캐릭터</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/이터널리턴 추천 [티어]</code>
        </p>
        <p className="text-discord-muted">
          티어별 승률 높은 캐릭터 Top 5를 추천받습니다.
          티어를 지정하지 않으면 다이아몬드 이상 기준으로 표시됩니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">동접자 수</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/이터널리턴 동접</code>
        </p>
        <p className="text-discord-muted">
          현재 이터널리턴의 동시 접속자 수를 확인합니다.
        </p>
      </div>
    ),
  },
  {
    id: 'youtube',
    title: '유튜브 알림',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-discord-text">서버 알림 설정 (관리자)</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/설정</code>
        </p>
        <p className="text-discord-muted">
          서버에서 유튜브 새 영상 알림을 받을 채널을 설정합니다.
          관리자 권한이 필요합니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">개인 DM 알림</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/유튜브 알림 받기:True</code>
        </p>
        <p className="text-discord-muted">
          새 영상이 업로드되면 DM으로 알림을 받습니다.
          알림을 끄려면 받기:False로 설정하세요.
        </p>
      </div>
    ),
  },
  {
    id: 'music',
    title: '음악 재생',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-discord-text">음악 재생</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/음악 재생 검색어:노래 제목 또는 URL</code>
        </p>
        <p className="text-discord-muted">
          음성 채널에 입장한 상태에서 사용하세요. 봇이 자동으로 음성 채널에 입장하고 음악을 재생합니다.
          YouTube URL이나 검색어를 입력할 수 있습니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">대기열 관리</h3>
        <ul className="list-disc list-inside text-discord-muted space-y-2 ml-4">
          <li><code className="bg-discord-dark px-2 py-1 rounded">/음악 대기열</code> - 현재 대기열 확인</li>
          <li><code className="bg-discord-dark px-2 py-1 rounded">/음악 스킵</code> - 현재 곡 건너뛰기</li>
          <li><code className="bg-discord-dark px-2 py-1 rounded">/음악 정지</code> - 재생 중지 및 대기열 비우기</li>
        </ul>
      </div>
    ),
  },
  {
    id: 'tts',
    title: 'TTS (음성 읽기)',
    content: (
      <div className="space-y-4">
        <div className="p-4 rounded-lg bg-gradient-to-r from-debi-primary/10 to-marlene-primary/10 border border-debi-primary/30">
          <p className="text-debi-primary font-medium">Premium 기능</p>
          <p className="text-discord-muted text-sm mt-1">
            TTS 기능은 프리미엄 구독자만 사용할 수 있습니다.
          </p>
        </div>

        <h3 className="text-xl font-semibold text-discord-text mt-6">TTS 채널 설정</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/음성 채널설정 채널:#텍스트채널</code>
        </p>
        <p className="text-discord-muted">
          지정한 텍스트 채널에 작성된 메시지를 음성으로 읽어줍니다.
          관리자 권한이 필요합니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">음성 선택</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/음성 목소리 음성:데비</code>
        </p>
        <p className="text-discord-muted">
          TTS 음성을 데비 또는 마를렌 중에서 선택할 수 있습니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">봇 음성 채널 제어</h3>
        <ul className="list-disc list-inside text-discord-muted space-y-2 ml-4">
          <li><code className="bg-discord-dark px-2 py-1 rounded">/음성 입장</code> - 봇을 음성 채널에 입장시킵니다</li>
          <li><code className="bg-discord-dark px-2 py-1 rounded">/음성 퇴장</code> - 봇을 음성 채널에서 퇴장시킵니다</li>
          <li><code className="bg-discord-dark px-2 py-1 rounded">/음성 채널해제</code> - TTS 채널 설정을 해제합니다</li>
        </ul>
      </div>
    ),
  },
  {
    id: 'dashboard',
    title: '대시보드',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-discord-text">대시보드 접속</h3>
        <p className="text-discord-muted">
          Discord 계정으로 로그인하면 관리자 권한이 있는 서버의 설정을 웹에서 관리할 수 있습니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">관리 가능한 설정</h3>
        <ul className="list-disc list-inside text-discord-muted space-y-2 ml-4">
          <li><strong>일반 설정</strong> - 공지 채널 설정</li>
          <li><strong>환영 메시지</strong> - 새 멤버 환영 메시지 설정</li>
          <li><strong>TTS</strong> - TTS 채널 및 음성 설정</li>
          <li><strong>자동응답</strong> - 키워드 기반 자동 응답</li>
          <li><strong>필터</strong> - 금지어 필터링</li>
          <li><strong>제재</strong> - 제재 로그 채널 설정</li>
          <li><strong>티켓</strong> - 문의 티켓 시스템</li>
        </ul>

        <div className="mt-6">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 btn-gradient px-4 py-2 rounded-lg text-white font-medium"
          >
            대시보드로 이동
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </div>
    ),
  },
  {
    id: 'premium',
    title: '프리미엄',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-discord-text">프리미엄 기능</h3>
        <p className="text-discord-muted">
          프리미엄 구독 시 다음 기능을 사용할 수 있습니다:
        </p>
        <ul className="list-disc list-inside text-discord-muted space-y-2 ml-4">
          <li>TTS (음성 읽기) 기능</li>
          <li>우선 지원</li>
          <li>프리미엄 배지</li>
        </ul>

        <h3 className="text-xl font-semibold text-discord-text mt-6">요금</h3>
        <ul className="list-disc list-inside text-discord-muted space-y-2 ml-4">
          <li><strong>월간</strong>: 9,900원/월</li>
          <li><strong>연간</strong>: 99,000원/년 (16% 할인)</li>
        </ul>

        <div className="mt-6">
          <Link
            to="/premium"
            className="inline-flex items-center gap-2 btn-gradient px-4 py-2 rounded-lg text-white font-medium"
          >
            프리미엄 구독하기
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </div>
    ),
  },
  {
    id: 'feedback',
    title: '피드백 & 지원',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-discord-text">피드백 보내기</h3>
        <p className="text-discord-muted">
          <code className="bg-discord-dark px-2 py-1 rounded">/피드백 내용:피드백 내용</code>
        </p>
        <p className="text-discord-muted">
          버그 제보, 기능 제안, 문의 등을 개발자에게 직접 보낼 수 있습니다.
        </p>

        <h3 className="text-xl font-semibold text-discord-text mt-6">서포트 서버</h3>
        <p className="text-discord-muted">
          더 자세한 도움이 필요하시면 서포트 서버에 참여해주세요.
        </p>
        <a
          href="https://discord.gg/your-server"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 mt-2 text-debi-primary hover:text-debi-light transition-colors"
        >
          서포트 서버 참여
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    ),
  },
]

export default function Docs() {
  const [activeSection, setActiveSection] = useState('getting-started')

  return (
    <div className="min-h-screen bg-discord-darkest">
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <aside className="lg:w-64 flex-shrink-0">
            <nav className="sticky top-24 space-y-1">
              <p className="text-xs font-semibold text-discord-muted uppercase tracking-wider mb-3 px-3">
                Documentation
              </p>
              {docSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeSection === section.id
                      ? 'bg-debi-primary/20 text-debi-primary font-medium'
                      : 'text-discord-muted hover:text-discord-text hover:bg-discord-light/10'
                  }`}
                >
                  {section.title}
                </button>
              ))}
            </nav>
          </aside>

          {/* Content */}
          <main className="flex-1 min-w-0">
            <div className="bg-discord-dark rounded-xl p-8 border border-discord-light/20">
              {docSections.map((section) => (
                <div
                  key={section.id}
                  className={activeSection === section.id ? 'block' : 'hidden'}
                >
                  <h2 className="text-2xl font-bold text-discord-text mb-6">
                    {section.title}
                  </h2>
                  {section.content}
                </div>
              ))}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
