import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 퀴즈 가이드 — 공개 페이지. /퀴즈 의 세 갈래(노래 맞추기·이터널리턴 퀴즈·직접 출제)와
 * 제목/가수 분리 채점, 문제 수 선택 같은 실제 진행 규칙을 설명한다.
 */
export default function GuideQuiz() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            퀴즈 가이드
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            퀴즈로 서버 사람들과 놀기
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            <code>/퀴즈</code>는 서버 사람들이 함께 즐기는 미니게임입니다. 노래를 듣고 제목과 가수를 맞히거나, 이터널 리턴 지식을 겨루거나,
            직접 문제를 내서 나머지가 맞히게 할 수 있습니다.
            게임을 시작하기 전 사람이 모일 때까지의 시간이나, 다들 접속은 했는데 뭘 할지 정하지 못한 저녁에 쓰기 좋습니다.
            이 문서는 세 가지 방식이 어떻게 다른지, 점수는 어떻게 매겨지는지, 진행이 매끄럽지 않을 때 무엇을 확인하면 되는지 정리합니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="시작하기" color="#3cabc9" delay={0.1}>
            <QA q="퀴즈는 어떻게 시작하나요?">
              <p>
                채팅창에 <code>/퀴즈</code>를 입력하면 어떤 퀴즈를 할지 고르는 화면이 나옵니다. 버튼으로 유형을 고르고, 드롭다운에서 문제 수를 정한 뒤 시작하면 됩니다.
                한 사람이 시작하면 그 채널에 있는 <strong>누구나 함께 참여</strong>할 수 있습니다. 따로 참가 신청을 받지 않으므로, 시작해 두고 사람들이 알아서 끼어들게 두면 됩니다.
                문제 수는 분위기에 맞춰 고르세요. 짧게 몸풀기로 할 거라면 적게, 자리를 잡고 길게 놀 거라면 많게 잡습니다.
              </p>
            </QA>
            <QA q="어떤 종류가 있나요?" delay={0.05}>
              <p>
                크게 셋입니다. <strong>노래 맞추기</strong>는 봇이 곡을 틀어 주면 제목과 가수를 맞히는 방식이고,
                <strong>이터널 리턴 퀴즈</strong>는 게임 관련 문제를 버튼으로 골라 답하는 객관식입니다.
                <strong>직접 출제</strong>는 한 사람이 출제자가 되어 곡을 등록하면 나머지가 맞히는 방식으로, 서버 사람들이 아는 노래로 판을 짤 때 씁니다.
                노래 맞추기는 음성 채널이 필요하고, 이터널 리턴 퀴즈는 채팅만으로 됩니다.
              </p>
            </QA>
          </Section>

          <Section title="노래 맞추기" color="#e58fb6" delay={0.15}>
            <QA q="제목과 가수 점수가 따로라는 게 무슨 뜻인가요?">
              <p>
                한 곡에 정답이 둘이라는 뜻입니다. 제목을 맞힌 사람과 가수를 맞힌 사람이 <strong>각각 점수를 가져갑니다.</strong>
                그래서 노래는 아는데 가수 이름이 기억나지 않아도 제목만으로 점수를 얻을 수 있고, 반대로 목소리만 듣고 가수를 아는 사람도 점수를 얻습니다.
                한 사람이 둘 다 맞히면 둘 다 가져갑니다. 아는 만큼 각자 점수를 쌓는 구조라, 음악 취향이 다른 사람들이 섞여 있어도 한쪽만 계속 이기는 상황이 잘 생기지 않습니다.
              </p>
            </QA>
            <QA q="정답은 어떻게 입력하나요?" delay={0.05}>
              <p>
                곡이 재생되는 동안 <strong>채팅창에 그냥 답을 적으면</strong> 됩니다. 별도의 명령이나 버튼이 필요 없습니다.
                맞으면 봇이 바로 정답 처리하고 누가 맞혔는지 알려 줍니다. 띄어쓰기나 약간의 표기 차이는 감안해 인식하지만,
                제목이 아주 길거나 외국어라면 알아보기 쉬운 부분으로 적어 보세요.
                아무도 못 맞히면 힌트가 나오고, 그래도 안 되면 다음 곡으로 넘어갑니다.
              </p>
            </QA>
            <QA q="봇이 곡을 안 틀어요." delay={0.1}>
              <p>
                노래 맞추기는 봇이 음성 채널에서 소리를 내야 하므로, 먼저 <strong>본인이 음성 채널에 들어가 있어야</strong> 합니다.
                봇에게 그 채널의 <strong>연결·말하기 권한</strong>이 없으면 들어와도 소리가 나오지 않습니다. 서버 관리자에게 권한을 확인해 달라고 요청하세요.
                소리는 나는데 내게만 안 들린다면 디스코드에서 봇이 개별 음소거되어 있지 않은지 확인해 보세요.
                같은 점검 순서는 <a href="/guide/tts/" className="text-[#3cabc9] underline">TTS 가이드</a>에 더 자세히 적어 두었습니다.
              </p>
            </QA>
          </Section>

          <Section title="직접 출제와 이터널 리턴 퀴즈" color="#34a853" delay={0.2}>
            <QA q="직접 출제는 어떻게 진행되나요?">
              <p>
                출제자가 된 사람이 버튼을 눌러 곡을 등록하면, 나머지 사람들이 그 곡을 듣고 맞힙니다.
                봇이 고른 곡이 아니라 <strong>사람이 고른 곡</strong>이라, 서버 안에서만 통하는 노래나 그날의 주제로 판을 짤 수 있습니다.
                출제자는 문제를 맞힐 수 없으니, 여러 판을 할 거라면 돌아가며 출제를 맡는 편이 재미있습니다.
              </p>
            </QA>
            <QA q="이터널 리턴 퀴즈는 어떤 문제가 나오나요?" delay={0.05}>
              <p>
                게임에 관한 문제가 객관식으로 나오고, <strong>버튼을 눌러</strong> 답을 고릅니다. 채팅으로 답을 적는 방식이 아니라 오타나 표기 차이로 억울할 일이 없습니다.
                총 문제 수는 시작할 때 정한 대로이고, 화면에 몇 번째 문제인지 표시됩니다.
                음성 채널이 필요 없어서 각자 다른 일을 하면서도 참여할 수 있습니다. 게임 대기 중에 돌리기 좋은 쪽입니다.
              </p>
            </QA>
            <QA q="퀴즈에도 크레딧이 드나요?" delay={0.1}>
              <p>
                퀴즈 진행 자체는 크레딧을 쓰지 않습니다. 다만 노래 맞추기처럼 봇이 음성을 송출하는 기능은 서버 사정에 따라 다르게 동작할 수 있으니,
                길게 놀 예정이라면 <a href="/guide/credits/" className="text-[#3cabc9] underline">크레딧 가이드</a>에서 잔액 확인 방법을 미리 봐 두면 좋습니다.
                크레딧은 매일 출석체크로도 모을 수 있어, 꾸준히 들르는 서버라면 부족할 일이 많지 않습니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              퀴즈가 중간에 멈추거나 곡이 재생되지 않는 문제가 반복되면 <code>/피드백 내용:상황 설명</code>으로 알려 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
