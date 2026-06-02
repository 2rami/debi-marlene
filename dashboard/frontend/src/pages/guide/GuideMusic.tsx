import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 음악과 퀴즈 가이드 — 공개 페이지. /음악 YouTube 재생, 재생 실패 원인,
 * /퀴즈 음악 게임 진행 방식. 봇 실제 기능 기반의 독창적 한국어 콘텐츠.
 */
export default function GuideMusic() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            Music Guide
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            음악과 퀴즈 가이드
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Debi &amp; Marlene 봇은 이터널 리턴 전적 검색만 하는 게 아닙니다. 음성 채널에 들어와 YouTube 음악을 틀어주고,
            친구들과 함께 즐기는 음악 퀴즈 게임까지 진행합니다. 이 페이지에서는 <code>/음악</code>으로 곡을 재생하는 법,
            재생이 안 될 때 무엇을 확인해야 하는지, 그리고 <code>/퀴즈</code>로 음악 퀴즈를 여는 방법을 차근차근 설명합니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="음악 재생" color="#3cabc9" delay={0.1}>
            <QA q="음악은 어떻게 재생하나요?">
              <p>
                먼저 음성 채널에 직접 들어간 상태에서 <code>/음악 검색어:URL또는검색어</code> 형식으로 입력합니다.
                예를 들어 <code>/음악 검색어:lofi study</code>처럼 검색어를 넣으면 봇이 YouTube에서 곡을 찾아 같은 음성 채널로 들어와 재생합니다.
                특정 영상을 정확히 틀고 싶다면 검색어 자리에 YouTube 영상 주소(URL)를 그대로 붙여 넣으면 됩니다.
                봇이 음성 채널에 입장해 있어야 소리가 나가므로, 명령을 입력하기 전에 본인이 음성 채널에 접속해 있는지 먼저 확인하세요.
              </p>
            </QA>
            <QA q="검색어 방식과 URL 방식 중 무엇이 더 정확한가요?" delay={0.05}>
              <p>
                원하는 곡이 명확하게 정해져 있다면 <strong>URL 방식</strong>이 가장 확실합니다. 검색어 방식은 봇이 YouTube 검색 결과 중
                가장 알맞은 영상을 골라 재생하는데, 동명의 커버 영상이나 라이브 버전이 먼저 잡혀 의도와 다른 곡이 나올 수 있기 때문입니다.
                반대로 제목이 잘 기억나지 않거나 분위기만 정해 두었을 때는 검색어 방식이 편합니다. 둘 다 같은 <code>/음악</code> 명령으로 처리되니
                상황에 맞게 골라 쓰면 됩니다.
              </p>
            </QA>
            <QA q="음악 재생이 안 돼요. 무엇을 확인해야 하나요?" delay={0.1}>
              <p>
                가장 흔한 원인은 봇이 음성 채널에 없는 경우입니다. 본인이 음성 채널에 들어간 뒤 다시 <code>/음악</code>을 입력해 보세요.
                채널은 맞는데도 재생이 안 된다면 YouTube 정책상 막힌 영상일 가능성이 큽니다. <strong>연령 제한</strong>이 걸린 영상,
                특정 국가에서 막아 둔 <strong>지역 차단</strong> 영상, 그리고 실시간으로 송출 중인 <strong>라이브 방송</strong>은 봇이 재생할 수 없습니다.
                이럴 때는 같은 곡의 일반 업로드 영상을 찾아 URL로 다시 시도하거나, 검색어 방식으로 다른 버전을 틀어 보면 해결되는 경우가 많습니다.
              </p>
            </QA>
            <QA q="봇이 음성 채널에서 소리를 내지 못해요." delay={0.15}>
              <p>
                영상 자체는 정상인데 소리가 안 들린다면 권한 또는 클라이언트 설정 문제일 수 있습니다. 봇 역할이 해당 음성 채널에서
                <strong>연결·말하기</strong> 권한을 갖고 있는지 확인하고, 본인 Discord에서 봇이 개별 음소거되어 있지 않은지 우클릭 메뉴로 점검하세요.
                또 봇과 다른 음성 채널에 있으면 당연히 들리지 않으니, 봇이 입장한 채널과 같은 채널에 있는지도 함께 확인하면 좋습니다.
              </p>
            </QA>
          </Section>

          <Section title="음악 퀴즈" color="#3cabc9" delay={0.2}>
            <QA q="음악 퀴즈는 어떻게 시작하나요?">
              <p>
                음성 채널에 들어간 상태에서 <code>/퀴즈</code>를 입력하면 음악 퀴즈 게임이 시작됩니다. 봇이 곡을 재생하면 참가자들은
                흘러나오는 음악을 듣고 정답을 맞히면 됩니다. 곡 재생을 사용하는 게임이므로 음악 재생과 마찬가지로 봇이 음성 채널에 함께 있어야 하고,
                참가자들도 같은 음성 채널에서 소리를 들을 수 있어야 제대로 즐길 수 있습니다. 여러 명이 함께 들어와 경쟁하면 훨씬 재미있습니다.
              </p>
            </QA>
            <QA q="정답은 어떻게 입력하나요?" delay={0.05}>
              <p>
                정답은 별도의 버튼이 아니라 <strong>채팅으로</strong> 입력합니다. 음악을 듣고 떠오른 제목을 그대로 채팅 채널에 쓰면 봇이 정답인지 판정해 줍니다.
                즉 음성으로는 곡을 듣고, 텍스트 채팅으로는 답을 적는 방식이라 음성 채널과 텍스트 채널을 함께 보면서 진행하게 됩니다.
                여러 사람이 동시에 답을 입력할 수 있으니, 곡이 나오는 순간 가장 빠르고 정확하게 적는 사람이 유리합니다.
              </p>
            </QA>
            <QA q="퀴즈가 더 재미있어지는 팁이 있나요?" delay={0.1}>
              <p>
                음악 퀴즈는 혼자보다 여러 명이 같은 음성 채널에 모여 즐길 때 진가를 발휘합니다. 이터널 리턴 한 판을 마치고 대기하는 동안이나
                친구들과 모인 자리에서 가볍게 돌리기 좋습니다. 곡이 재생되는 동안 채팅창을 함께 띄워 두면 답을 빠르게 적을 수 있고,
                서로 정답을 가린 채 경쟁하면 분위기가 한층 살아납니다. 음악 재생이 막힌 곡이 있을 수 있는 것처럼 일부 영상은 게임에서 제외될 수 있으니,
                재생이 매끄럽지 않다면 잠시 후 다시 <code>/퀴즈</code>로 새 라운드를 열어 보세요.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              음악·퀴즈 사용 중 문제가 있나요? <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
