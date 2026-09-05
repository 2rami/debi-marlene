import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Header from '../components/common/Header'
import TerminalBlock from '../components/docs/TerminalBlock'
import { DISCORD_CLIENT_ID } from '../config/discord'
import {
  Book,
  Settings,
  Zap,
  MessageSquare,
  Music,
  ChevronRight,
  ExternalLink,
  Menu,
  X
} from 'lucide-react'
interface DocSection {
  id: string
  title: string
  icon: React.ReactNode
  content: React.ReactNode
}
/** 탭 밖에 상시 노출하는 기능별 문서 링크. 탭 하나에 갇힌 내용을 밖으로 잇는다. */
const DOC_GUIDES = [
  { href: '/guide/server-setup/', title: '서버 설정', desc: '봇 권한 확인, 명령어 채널과 공지 채널 지정, 환영 메시지와 유튜브 알림까지 관리자가 처음 잡아야 할 순서를 정리했습니다.' },
  { href: '/guide/record/', title: '전적 검색', desc: '/전적 결과에 나오는 티어·MMR·평균 순위·승률·평균 킬이 각각 무엇을 뜻하고, 그 숫자로 무엇을 판단할 수 있는지 설명합니다.' },
  { href: '/guide/stats/', title: '캐릭터 통계', desc: '/통계 표의 표본 구간과 집계 기간, 승률과 픽률을 함께 읽어야 하는 이유를 다룹니다.' },
  { href: '/guide/tts/', title: 'TTS 음성', desc: '음성 채널로 봇을 부르는 법, 목소리와 읽을 채널 설정, 소리가 안 들릴 때의 점검 순서입니다.' },
  { href: '/guide/music/', title: '음악 재생', desc: 'YouTube 검색과 URL 재생, 대기열·스킵·반복 조작 방법입니다.' },
  { href: '/guide/quiz/', title: '퀴즈', desc: '노래 맞추기와 이터널 리턴 퀴즈, 직접 출제 방식의 차이와 채점 규칙입니다.' },
  { href: '/guide/eternal-return/', title: '이터널 리턴 기초', desc: '게임 자체가 처음인 분을 위한 개요와, 봇의 게임 기능이 무엇을 보여주는지 설명합니다.' },
  { href: '/guide/faq/', title: '자주 묻는 질문', desc: '봇이 반응하지 않거나 명령어가 보이지 않을 때 가장 먼저 확인할 것들을 모았습니다.' },
]
export default function Docs() {
  const [activeSection, setActiveSection] = useState('getting-started')
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  // 섹션을 전부 펼쳐 두고 사이드바는 목차로 쓴다. 탭으로 감춰 두면 선택된 하나만
  // DOM 에 올라가 크롤러가 나머지를 못 읽는다(개인정보처리방침이 그렇게 통째로
  // 누락됐다). 지금 보이는 섹션은 스크롤 위치로 추적해 목차에 표시한다.
  useEffect(() => {
    const ids = ['getting-started', 'dashboard-guide', 'voice-tts', 'music-guide', 'support']
    // IntersectionObserver 는 여기 안 맞는다. 섹션이 뷰포트보다 길어 여러 개가 동시에
    // 걸치는데, 콜백은 상태가 바뀐 것만 넘겨 주므로 이미 걸쳐 있던 섹션이 빠진다.
    // 헤더(112px) 바로 아래를 지난 마지막 섹션을 직접 고른다.
    const onScroll = () => {
      let current = ids[0]
      for (const id of ids) {
        const el = document.getElementById(id)
        if (el && el.getBoundingClientRect().top <= 140) current = id
      }
      setActiveSection(current)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])
  const docSections: DocSection[] = [
    {
      id: 'getting-started',
      title: '시작하기',
      icon: <Book className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-debi-primary/20 text-debi-primary">
                <Book className="w-6 h-6" />
              </span>
              시작하기
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              Debi & Marlene은 이터널리턴 전적 검색, 고품질 TTS, 음악 재생 등 디스코드 서버 운영에 필요한 모든 기능을 제공합니다.
              지금 바로 봇을 초대하고 서버를 업그레이드하세요.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-discord-dark/50 border border-discord-light/10">
              <h3 className="text-lg font-bold text-white mb-2">1. 봇 초대하기</h3>
              <p className="text-discord-muted mb-4 text-sm">
                관리자 권한이 있는 서버에 봇을 초대할 수 있습니다.
              </p>
              <a
                href={`https://discord.com/api/oauth2/authorize?client_id=${DISCORD_CLIENT_ID}&permissions=8&scope=bot%20applications.commands`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-debi-primary hover:underline font-medium"
              >
                봇 초대 링크 바로가기 <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <div className="p-6 rounded-2xl bg-discord-dark/50 border border-discord-light/10">
              <h3 className="text-lg font-bold text-white mb-2">2. 권한 확인</h3>
              <p className="text-discord-muted mb-4 text-sm">
                원활한 기능 사용을 위해 봇에게 <strong>관리자 권한</strong>을 부여하는 것을 권장합니다.
              </p>
              <div className="flex flex-wrap gap-2">
                {['메시지 보기', '메시지 보내기', '음성 연결', '말하기'].map(perm => (
                  <span key={perm} className="px-2 py-1 rounded bg-discord-light/10 text-xs text-discord-muted">
                    {perm}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div>
            <h3 className="text-xl font-bold text-white mb-4">첫 명령어 실행해보기</h3>
            <p className="text-discord-muted mb-4">
              봇이 서버에 들어왔다면 채팅창에 <code className="text-debi-primary">/</code>를 입력하여 슬래시 커맨드를 확인해보세요.
            </p>
            <TerminalBlock
              command="/전적 닉네임:플레이어명"
              output="[Debi & Marlene] 플레이어 전적을 검색합니다."
            />
          </div>

          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white">초대 직후 자주 겪는 일</h3>
            <div className="space-y-3">
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <strong className="text-white block mb-1.5">명령어 목록에 봇이 안 보여요</strong>
                <p className="text-discord-muted text-sm leading-relaxed">
                  슬래시 명령은 디스코드가 서버마다 목록을 갱신하는 데 잠시 시간이 걸립니다. 초대 직후라면 몇 분 뒤 다시 <code className="text-debi-primary">/</code>를 입력해 보세요.
                  그래도 없다면 초대할 때 <strong>applications.commands</strong> 권한이 빠졌을 수 있습니다. 봇을 추방한 뒤 위의 초대 링크로 다시 초대하면 해결됩니다.
                </p>
              </div>
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <strong className="text-white block mb-1.5">명령을 넣었는데 아무 반응이 없어요</strong>
                <p className="text-discord-muted text-sm leading-relaxed">
                  권한이 없으면 봇은 오류를 내는 대신 <strong>조용히 아무것도 하지 않습니다.</strong> 고장으로 오해하기 쉬운 부분입니다.
                  해당 채널에서 봇 역할이 메시지 보내기 권한을 가지고 있는지 먼저 확인하세요.
                  서버 관리자가 명령어 채널을 지정해 둔 경우에는 그 채널에서만 동작하며, 다른 곳에서는 어느 채널로 가야 하는지 안내가 나옵니다.
                </p>
              </div>
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <strong className="text-white block mb-1.5">권한을 좁게 주고 싶어요</strong>
                <p className="text-discord-muted text-sm leading-relaxed">
                  관리자 권한을 통째로 주지 않아도 됩니다. 위에 적힌 네 가지(메시지 보기·보내기, 음성 연결·말하기)만 열어 두면 대부분의 기능이 동작합니다.
                  다만 메시지 삭제나 제재 같은 관리 기능을 쓸 계획이라면 그에 맞는 권한이 추가로 필요합니다.
                </p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'dashboard-guide',
      title: '대시보드 사용법',
      icon: <Settings className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-purple-500/20 text-purple-400">
                <Settings className="w-6 h-6" />
              </span>
              대시보드 가이드
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              웹 대시보드를 통해 봇의 설정을 직관적으로 관리할 수 있습니다.
              복잡한 명령어 입력 없이 UI에서 클릭 몇 번으로 설정을 변경해보세요.
            </p>
          </div>
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white">주요 기능</h3>
            <ul className="grid md:grid-cols-2 gap-4">
              {[
                { title: '공지 채널', desc: '봇이 먼저 말을 거는 알림이 나갈 곳입니다. 유튜브 새 영상 알림 등이 여기로 갑니다. 대화 채널로 지정하면 알림이 대화를 끊으므로 공지용 채널을 권합니다.' },
                { title: '봇 명령어 채널', desc: '명령을 받을 채널을 한 곳으로 제한합니다. 전적·통계 결과는 화면을 꽤 차지해서, 사람이 많은 서버라면 대화 채널과 분리하는 편이 낫습니다.' },
                { title: 'TTS 설정', desc: '봇이 읽어 줄 채팅 채널과 목소리를 지정합니다. 모든 채팅을 다 읽으면 음성이 겹쳐 시끄러워지므로 지정된 채널의 글만 읽습니다.' },
                { title: '환영 메시지', desc: '새 멤버가 들어왔을 때 보낼 인사말과 이미지를 설정합니다. 규칙이나 채널 안내를 전달하는 자리로 쓰기 좋습니다.' },
                { title: '자동응답', desc: '특정 키워드에 반응하는 답변을 등록합니다. 자주 나오는 질문에 사람이 매번 답하지 않아도 되게 만듭니다.' },
                { title: '채팅 필터', desc: '걸러 낼 단어와 그때 취할 조치(경고·삭제 등)를 정합니다. 서버 분위기를 지키는 용도입니다.' },
                { title: '제재 관리', desc: '경고가 몇 번 쌓이면 자동으로 제재할지 정합니다. 기준을 미리 정해 두면 관리자마다 판단이 갈리지 않습니다.' },
                { title: '티켓 시스템', desc: '문의를 개별 채널로 받는 기능입니다. 티켓이 생성될 카테고리를 지정해 둡니다.' },
              ].map((item, idx) => (
                <li key={idx} className="flex gap-4 p-4 rounded-xl bg-discord-dark border border-discord-light/5">
                  <div className="w-1.5 h-1.5 rounded-full bg-debi-primary mt-2 shrink-0" />
                  <div>
                    <strong className="text-white block mb-1">{item.title}</strong>
                    <span className="text-discord-muted text-sm">{item.desc}</span>
                  </div>
                </li>
              ))}
            </ul>
            <p className="text-discord-muted text-sm leading-relaxed">
              설정은 <strong>관리자 권한</strong>이 있어야 보이며, 디스코드 계정으로 로그인한 뒤 관리할 서버를 골라 변경합니다.
              같은 항목을 서버 안에서 <code className="text-debi-primary">/설정</code> 명령으로도 다룰 수 있습니다. 항목이 여럿일 때는 대시보드가, 한 가지만 빠르게 바꿀 때는 명령이 편합니다.
              바꿨는데 반영이 안 된다면 먼저 <strong>바꾼 서버가 맞는지</strong> 확인하고, 다음으로 봇이 그 채널에 들어갈 권한이 있는지 보세요. 설정은 저장됐는데 권한이 없으면 동작만 조용히 실패합니다.
            </p>
          </div>
          <div className="p-6 rounded-2xl bg-gradient-to-r from-debi-primary/10 to-marlene-primary/10 border border-debi-primary/20">
            <div className="flex flex-col md:flex-row items-center gap-6 justify-between">
              <div>
                <h3 className="text-lg font-bold text-white mb-1">대시보드 바로가기</h3>
                <p className="text-discord-muted text-sm">지금 바로 내 서버를 관리해보세요.</p>
              </div>
              <Link
                to="/dashboard"
                className="px-6 py-3 rounded-xl bg-white text-discord-darkest font-bold hover:scale-105 transition-transform shadow-lg"
              >
                관리 시작하기
              </Link>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'voice-tts',
      title: '음성 & TTS',
      icon: <MessageSquare className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-green-500/20 text-green-400">
                <MessageSquare className="w-6 h-6" />
              </span>
              음성 (TTS) 기능
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              채팅을 치면 봇이 음성으로 읽어주는 TTS 기능을 제공합니다.
              데비, 마를렌, 알렉스의 AI 음성과 Edge TTS 음성을 선택할 수 있어요.
            </p>
          </div>
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold text-white mb-3">1. 봇 부르기</h3>
              <p className="text-discord-muted mb-3">먼저 음성 채널에 있어야 합니다. 그 후 아래 명령어를 입력하세요.</p>
              <TerminalBlock command="/tts" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white mb-3">2. 목소리 & 채널 설정</h3>
              <p className="text-discord-muted mb-3">입장 후 나타나는 UI에서 목소리 변경, 읽을 채널 설정을 할 수 있습니다. AI 음성(데비/마를렌/알렉스)과 Edge TTS 음성(SunHi/InJoon/Hyunsu)을 선택할 수 있어요.</p>
              <TerminalBlock command="/tts" output="[TTS 입장] 음성 채널에 입장했어요! 목소리와 채널을 UI에서 설정하세요." />
            </div>

            <div>
              <h3 className="text-xl font-bold text-white mb-3">3. 알아 두면 좋은 것</h3>
              <ul className="space-y-3">
                <li className="p-4 rounded-xl bg-discord-dark border border-discord-light/10 text-discord-muted text-sm leading-relaxed">
                  <strong className="text-white">봇은 지정된 채널의 글만 읽습니다.</strong> 잡담 채널이나 명령어 채널에 쓴 글은 음성으로 나오지 않습니다.
                  모든 메시지를 다 읽으면 음성이 끊임없이 겹쳐 시끄러워지기 때문에 채널을 나눠 두는 구조입니다.
                  즉 봇은 음성 채널에서 말하고, 읽을 텍스트는 정해진 채팅 채널에 입력합니다.
                </li>
                <li className="p-4 rounded-xl bg-discord-dark border border-discord-light/10 text-discord-muted text-sm leading-relaxed">
                  <strong className="text-white">송출 시간만큼 크레딧이 차감됩니다.</strong> 짧은 문장은 거의 들지 않고, 긴 글을 자주 읽힐수록 빠르게 소모됩니다.
                  크레딧은 대시보드의 출석체크로 매일 무료로 모을 수 있습니다.
                </li>
                <li className="p-4 rounded-xl bg-discord-dark border border-discord-light/10 text-discord-muted text-sm leading-relaxed">
                  <strong className="text-white">소리가 안 들릴 때는 셋을 먼저 봅니다.</strong> 본인이 봇과 같은 음성 채널에 있는지,
                  디스코드에서 봇이 개별 음소거되어 있지 않은지, 글을 쓴 채널이 실제로 TTS 채널이 맞는지 확인하세요.
                  그래도 안 되면 봇 역할에 그 음성 채널의 연결·말하기 권한이 있는지 봅니다.
                </li>
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'music-guide',
      title: '음악 재생',
      icon: <Music className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-pink-500/20 text-pink-400">
                <Music className="w-6 h-6" />
              </span>
              음악 재생
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              고음질로 유튜브 음악을 감상하세요. 간편한 검색과 대기열 관리를 지원합니다.
            </p>
          </div>
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold text-white mb-3">음악 틀기</h3>
              <p className="text-discord-muted mb-3">제목이나 URL을 입력하면 자동으로 검색하여 재생합니다.</p>
              <TerminalBlock command="/음악 검색어:NewJeans Hype Boy" />
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <h4 className="font-bold text-white mb-2">대기열 확인</h4>
                <p className="text-sm text-discord-muted mb-3">현재 재생 중인 곡과 다음 곡 목록을 보여줍니다.</p>
                <code className="text-xs bg-black/30 px-2 py-1 rounded text-pink-400">UI 대기열 버튼</code>
              </div>
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <h4 className="font-bold text-white mb-2">스킵 / 정지</h4>
                <p className="text-sm text-discord-muted mb-3">재생 중 나타나는 UI 버튼으로 스킵, 정지, 반복 등을 조작할 수 있습니다.</p>
                <div className="flex gap-2">
                  <code className="text-xs bg-black/30 px-2 py-1 rounded text-pink-400">UI 버튼으로 조작</code>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <strong className="text-white block mb-1.5">봇이 소리를 내지 않아요</strong>
                <p className="text-discord-muted text-sm leading-relaxed">
                  음악도 TTS와 마찬가지로 봇이 음성 채널에 들어가야 소리가 납니다. 먼저 본인이 음성 채널에 들어간 뒤 명령을 넣으세요.
                  봇 역할에 그 채널의 <strong>연결·말하기</strong> 권한이 없으면 들어와도 소리가 나오지 않습니다.
                </p>
              </div>
              <div className="p-5 rounded-xl bg-discord-dark border border-discord-light/10">
                <strong className="text-white block mb-1.5">여러 곡을 이어서 틀고 싶어요</strong>
                <p className="text-discord-muted text-sm leading-relaxed">
                  재생 중에 명령을 다시 넣으면 곡이 대기열에 쌓입니다. 지금 무엇이 재생 중이고 다음에 무엇이 나오는지는 대기열 버튼으로 확인합니다.
                  버튼은 명령을 넣은 사람뿐 아니라 채널에 있는 누구나 누를 수 있어, 여럿이 함께 들을 때 서로 곡을 넘기며 쓸 수 있습니다.
                </p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'support',
      title: '문의 및 지원',
      icon: <Zap className="w-4 h-4" />,
      content: (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="p-2 rounded-lg bg-yellow-500/20 text-yellow-400">
                <Zap className="w-6 h-6" />
              </span>
              문의 및 지원
            </h2>
            <p className="text-lg text-discord-muted leading-relaxed">
              사용 중 문제가 발생했거나 건의사항이 있으신가요? 언제든 편하게 말씀해주세요.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-discord-dark border border-discord-light/10 hover:border-debi-primary/30 transition-colors">
              <h3 className="text-xl font-bold text-white mb-4">공식 서포트 서버</h3>
              <p className="text-discord-muted mb-6">
                개발자와 직접 소통하고 업데이트 소식을 가장 먼저 받아볼 수 있습니다.
              </p>
              <a
                href="https://discord.gg/aDemda3qC9"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-[#5865F2] hover:bg-[#4752C4] text-white font-bold transition-colors"
              >
                서포트 서버 참여하기
              </a>
            </div>
            <div className="p-6 rounded-2xl bg-discord-dark border border-discord-light/10">
              <h3 className="text-xl font-bold text-white mb-4">피드백 명령어</h3>
              <p className="text-discord-muted mb-4">
                디스코드 내에서 바로 피드백을 보낼 수도 있습니다.
              </p>
              <TerminalBlock command="/피드백 내용:이런 기능이 추가되었으면 좋겠어요!" />
            </div>
          </div>

          <div>
            <h3 className="text-xl font-bold text-white mb-3">문의할 때 함께 적어 주시면 좋은 것</h3>
            <p className="text-discord-muted mb-4 leading-relaxed">
              같은 명령이라도 서버 설정과 권한에 따라 다르게 동작하기 때문에, 상황을 알 수 있는 정보가 있으면 원인을 훨씬 빨리 찾습니다.
              아래 항목을 적어 주시면 대부분 한 번에 확인됩니다.
            </p>
            <ul className="grid md:grid-cols-2 gap-3">
              {[
                { title: '어느 서버인지', desc: '서버 이름이나 초대 코드. 설정은 서버마다 따로 저장됩니다.' },
                { title: '어떤 명령이었는지', desc: '입력한 명령과 넣은 값. 닉네임 검색이라면 그 닉네임까지.' },
                { title: '무엇을 기대했고 무엇이 일어났는지', desc: '"아무 반응이 없었다", "다른 결과가 나왔다"처럼 실제로 본 것.' },
                { title: '언제였는지', desc: '대략의 시각. 그 무렵의 기록을 되짚어 볼 수 있습니다.' },
              ].map((item, idx) => (
                <li key={idx} className="p-4 rounded-xl bg-discord-dark border border-discord-light/5">
                  <strong className="text-white block mb-1">{item.title}</strong>
                  <span className="text-discord-muted text-sm leading-relaxed">{item.desc}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-6 rounded-2xl bg-discord-dark/50 border border-discord-light/10">
            <h3 className="text-lg font-bold text-white mb-2">문의 전에 확인하면 좋은 것</h3>
            <p className="text-discord-muted text-sm leading-relaxed">
              반응이 없는 경우는 대부분 권한 문제이거나 명령어 채널 제한입니다. 위 <a href="#getting-started" className="text-debi-primary underline">시작하기</a> 항목의 점검 순서를 먼저 밟아 보세요.
              기능별로 자주 나오는 질문은 <a href="/guide/faq/" className="text-debi-primary underline">자주 묻는 질문</a>에 모아 두었습니다.
              계정·데이터 처리에 관한 문의는 <a href="/privacy/" className="text-debi-primary underline">개인정보처리방침</a>의 문의처로 보내 주시면 됩니다.
            </p>
          </div>
        </div>
      )
    }
  ]
  return (
    <div className="min-h-screen bg-discord-darkest selection:bg-debi-primary/30 selection:text-white">
      <Header />
      <div className="max-w-7xl mx-auto px-6 py-8 md:py-16">
        <div className="grid lg:grid-cols-[280px_1fr] gap-8 xl:gap-12">
          {/* Mobile Sidebar Toggle */}
          <div className="lg:hidden mb-6">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="flex items-center gap-2 px-4 py-3 rounded-xl bg-discord-dark border border-white/10 text-white font-medium w-full"
            >
              <Menu className="w-5 h-5" />
              {docSections.find(s => s.id === activeSection)?.title || '메뉴 선택'}
              <ChevronRight className={`w-4 h-4 ml-auto transition-transform ${isSidebarOpen ? 'rotate-90' : ''}`} />
            </button>
          </div>
          {/* Sidebar */}
          <aside className={`
            fixed inset-0 z-40 bg-discord-darkest/95 backdrop-blur-xl lg:static lg:bg-transparent lg:block
            ${isSidebarOpen ? 'block' : 'hidden'}
          `}>
            <div className="h-full overflow-y-auto p-6 lg:p-0">
              <div className="flex items-center justify-between lg:hidden mb-8">
                <span className="font-bold text-xl text-white">Documentation</span>
                <button onClick={() => setIsSidebarOpen(false)} className="p-2 text-white/50 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="sticky top-28 space-y-2">
                <p className="px-4 text-xs font-bold text-discord-muted uppercase tracking-wider mb-4 hidden lg:block">
                  Documentation
                </p>
                {docSections.map((section) => (
                  <a
                    key={section.id}
                    href={`#${section.id}`}
                    onClick={() => setIsSidebarOpen(false)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${activeSection === section.id
                      ? 'bg-gradient-to-r from-debi-primary/20 to-marlene-primary/20 text-white shadow-lg shadow-debi-primary/10 border border-debi-primary/20'
                      : 'text-discord-muted hover:text-white hover:bg-white/5 border border-transparent'
                      }`}
                  >
                    <span className={activeSection === section.id ? 'text-debi-primary' : 'text-gray-500'}>
                      {section.icon}
                    </span>
                    {section.title}
                    {activeSection === section.id && (
                      <ChevronRight className="w-3 h-3 ml-auto text-debi-primary" />
                    )}
                  </a>
                ))}
              </div>
            </div>
          </aside>
          {/* Main Content */}
          <main className="min-w-0">
            <div className="space-y-10">
              {docSections.map((section) => (
                <section
                  key={section.id}
                  id={section.id}
                  className="scroll-mt-28 bg-discord-dark/30 rounded-3xl p-6 md:p-10 border border-white/5 shadow-2xl backdrop-blur-sm"
                >
                  {section.content}
                </section>
              ))}
            </div>
            {/* 탭 밖 상시 노출 영역 — 탭은 한 번에 하나만 보이므로, 어느 탭에 있든
                기능별 상세 문서로 갈 수 있는 길을 여기 둔다. */}
            <section className="mt-16 pt-10 border-t border-white/5">
              <h2 className="text-2xl font-bold text-white mb-3">기능별 상세 가이드</h2>
              <p className="text-discord-muted text-sm leading-relaxed mb-8 max-w-3xl">
                이 문서는 봇을 처음 들일 때 필요한 최소한의 절차를 담고 있습니다.
                각 기능을 실제로 다루는 방법, 결과 화면을 읽는 법, 문제가 생겼을 때의 점검 순서는
                아래 문서에 기능별로 나누어 정리했습니다.
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                {DOC_GUIDES.map(({ href, title, desc }) => (
                  <a
                    key={href}
                    href={href}
                    className="block p-5 rounded-2xl bg-discord-dark/50 border border-discord-light/10 hover:border-debi-primary/40 transition-colors"
                  >
                    <div className="text-white font-bold mb-1.5">{title}</div>
                    <div className="text-discord-muted text-sm leading-relaxed">{desc}</div>
                  </a>
                ))}
              </div>
            </section>
            {/* Footer Navigation (Next/Prev) */}
            <div className="mt-12 flex justify-between border-t border-white/5 pt-8">
              {/* Logic for prev/next buttons can be improved, simple implementation for now */}
              <div />
              <div className="text-right">
                <p className="text-xs text-discord-muted mb-1">도움이 더 필요하신가요?</p>
                <a href="https://discord.gg/aDemda3qC9" target="_blank" rel="noopener noreferrer" className="text-debi-primary font-bold hover:underline text-sm flex items-center gap-1 justify-end">
                  서포트 서버 바로가기 <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
