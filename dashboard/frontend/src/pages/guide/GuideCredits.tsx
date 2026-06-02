import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 크레딧과 AI 대화 가이드 — 공개 페이지. 크레딧 재화의 개념·획득·소비·충전·환불과
 * /대화 사용 경험을 실제 시나리오 중심으로 설명한다. AdSense 심사용 독창 콘텐츠.
 */
export default function GuideCredits() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            Credits Guide
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            크레딧과 AI 대화 가이드
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Debi &amp; Marlene의 AI 대화와 TTS 음성은 &apos;크레딧&apos;이라는 재화로 움직입니다.
            크레딧이 정확히 무엇이고, 출석과 충전으로 어떻게 모으며, 어디에 얼마나 쓰이는지 —
            데비·마를렌과 더 오래 떠들기 위한 모든 것을 한 페이지에 정리했습니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="크레딧이란 무엇인가요" color="#34a853" delay={0.1}>
            <QA q="크레딧은 어떤 재화인가요?">
              <p>
                크레딧은 Debi &amp; Marlene 봇 안에서 AI 기능을 사용할 때 소모되는 가상 재화입니다.
                무료로 제공되는 분량을 다 쓴 뒤에도 데비·마를렌과 계속 대화하거나, 긴 문장을 TTS로 읽게 하고 싶을 때
                크레딧이 그 사용량을 대신합니다. 게임 내 화폐와는 무관하며, 오직 봇 서비스 안에서만 쓰이는 별도의 포인트라고
                생각하면 됩니다. 출석만으로도 매일 쌓이기 때문에, 가볍게 쓰는 정도라면 돈을 들이지 않고도 충분히 즐길 수 있습니다.
              </p>
            </QA>
            <QA q="크레딧 잔액은 어디서 확인하나요?" delay={0.05}>
              <p>
                debimarlene.com 대시보드에 Discord 계정으로 로그인하면 화면 상단의 크레딧 지갑에서 현재 잔액을 바로 볼 수 있습니다.
                출석으로 받은 적립분, 충전한 분량, 그동안 차감된 내역이 함께 관리되므로 &apos;왜 줄었지?&apos; 싶을 때 사용 흐름을 되짚어 볼 수 있습니다.
                크레딧은 Discord 계정 단위로 따라다니기 때문에, 어느 서버에서 데비·마를렌을 만나든 같은 잔액을 그대로 사용합니다.
              </p>
            </QA>
          </Section>

          <Section title="크레딧 모으기" color="#34a853" delay={0.15}>
            <QA q="가장 쉬운 무료 적립 방법은 출석인가요?">
              <p>
                네. debimarlene.com에 로그인해 <strong>매일 출석체크</strong>를 누르면 하루 +10크레딧이 적립됩니다.
                여기에 연속 출석 보너스가 더해지는데, <strong>3일 연속 +30</strong>, <strong>7일 연속 +100</strong>처럼 빠짐없이 들를수록 보상이 커집니다.
                매일 잠깐 들러 출석만 챙겨도 일주일이면 가벼운 대화 정도는 무료로 이어가기에 충분한 크레딧이 모입니다.
                습관처럼 출석하는 것이 가장 부담 없는 적립 루트입니다.
              </p>
            </QA>
            <QA q="출석 말고 다른 방법도 있나요?" delay={0.05}>
              <p>
                있습니다. 봇 안의 <strong>도박</strong>으로 크레딧을 걸어 불릴 수 있고(잃을 수도 있으니 여유분으로만 즐기세요),
                서버 차원의 <strong>기부</strong>로 크레딧을 주고받는 것도 가능합니다. 그리고 가장 확실한 방법은 대시보드에서의 직접 <strong>충전</strong>입니다.
                출석으로 천천히 모으는 길과, 충전으로 한 번에 채우는 길을 상황에 맞게 섞어 쓰면 됩니다.
              </p>
            </QA>
            <QA q="충전하면 보너스가 붙는다던데 얼마나 더 주나요?" delay={0.1}>
              <p>
                충전 금액이 클수록 보너스 비율이 점점 커지는 점증 구조입니다.
                <strong>1,000원 → 100크레딧</strong>, <strong>5,000원 → 600크레딧(+20%)</strong>,
                <strong>10,000원 → 1,300크레딧(+30%)</strong>, <strong>30,000원 → 4,500크레딧(+50%)</strong>로 단가가 유리해집니다.
                자주, 길게 대화할 계획이라면 큰 단위로 한 번에 충전하는 쪽이 같은 돈으로 더 많은 크레딧을 얻는 방법입니다.
                반대로 가끔만 쓴다면 작은 단위로 채워도 부담이 없습니다.
              </p>
            </QA>
          </Section>

          <Section title="쓰기 · 충전 · 환불" color="#34a853" delay={0.2}>
            <QA q="/대화는 어떻게 즐기고, 크레딧은 언제 차감되나요?">
              <p>
                <code>/대화</code>를 입력하면 데비·마를렌과 자유롭게 이야기를 나눌 수 있습니다. 안부를 묻거나, 오늘 게임 한 판 이야기를 풀거나,
                그냥 시시콜콜한 잡담을 던져도 캐릭터의 말투로 답을 돌려줍니다. <strong>하루 5회까지는 무료</strong>이며, 그 이후 메시지부터는
                메시지당 <strong>2크레딧</strong>이 차감됩니다. 짧게 인사만 나눌 거라면 무료 횟수로 충분하고, 길게 수다를 떨고 싶을 때 크레딧이 그 시간을 늘려준다고 보면 됩니다.
              </p>
            </QA>
            <QA q="TTS는 크레딧을 얼마나 먹나요?" delay={0.05}>
              <p>
                TTS(음성 읽기)는 재생 시간 기준으로 <strong>10초당 1크레딧</strong>이 소모됩니다. 짧은 한두 문장은 크레딧이 거의 들지 않지만,
                긴 글을 통째로 읽게 하면 그만큼 누적되니 잔액을 한 번씩 확인하는 게 좋습니다. 목소리(데비/마를렌)와 읽어줄 채널은
                debimarlene.com 대시보드의 서버 설정에서 바꿀 수 있어, 통화방 분위기에 맞춰 자유롭게 조정할 수 있습니다.
              </p>
            </QA>
            <QA q="충전은 어떻게 하나요?" delay={0.1}>
              <p>
                debimarlene.com 대시보드에 로그인한 뒤 크레딧 지갑의 <strong>충전</strong> 버튼을 누르면 충전 화면이 열립니다.
                원하는 금액대를 고르고 Toss 결제로 진행하면, 결제가 완료되는 즉시 보너스를 포함한 크레딧이 잔액에 반영됩니다.
                결제가 끝나면 성공 안내 화면으로 이동하며, 혹시 중간에 실패하더라도 별도 차감 없이 다시 시도할 수 있으니 안심하고 진행하세요.
              </p>
            </QA>
            <QA q="충전한 크레딧을 환불받을 수 있나요?" delay={0.15}>
              <p>
                결제일로부터 <strong>7일 이내</strong>이고, 충전한 크레딧을 <strong>아직 한 번도 사용하지 않은 경우</strong>에 한해 환불이 가능합니다.
                대화나 TTS로 일부라도 사용한 충전분은 환불 대상에서 제외됩니다. 출석·도박·기부로 받은 무상 크레딧은 환불 대상이 아닙니다.
                환불이 필요하면 결제 정보와 함께 <a href="mailto:goenho0613@gmail.com" className="text-[#34a853] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              크레딧·결제 관련해 더 궁금한 점이 있나요? <a href="mailto:goenho0613@gmail.com" className="text-[#34a853] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
