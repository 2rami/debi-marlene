import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * TTS 음성 가이드 — 공개 페이지. /tts 호출부터 목소리 설정, 크레딧 소모,
 * 소리 안 들릴 때 점검까지 실제 사용 흐름 기반의 독창적 한국어 콘텐츠.
 */
export default function GuideTTS() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            TTS 가이드
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            TTS 음성 가이드
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Debi &amp; Marlene 봇은 음성 채널에 들어와 여러분이 채팅에 쓴 글을 데비 또는 마를렌의 목소리로 읽어줍니다.
            이터널 리턴을 플레이하면서 손은 키보드·마우스에 두고, 팀원에게 콜이나 잡담을 음성으로 전달하고 싶을 때 유용합니다.
            아래에서 봇을 음성 채널로 부르는 법, 두 목소리의 차이, 대시보드 설정, 크레딧 소모, 소리가 안 들릴 때 점검 순서를 정리했습니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="TTS 시작하기" color="#34a853" delay={0.1}>
            <QA q="봇을 음성 채널로 부르고 채팅을 읽게 하려면?">
              <p>
                먼저 본인이 읽기를 원하는 음성 채널에 직접 들어간 뒤 <code>/tts</code>를 입력하세요. 그러면 봇이 같은 음성 채널로 따라 들어옵니다.
                이후 서버에 지정된 TTS 채팅 채널에 글을 쓰면, 봇이 그 문장을 데비 또는 마를렌 목소리로 소리 내어 읽어줍니다.
                즉 봇은 음성 채널에서 말하고, 여러분이 읽을 텍스트는 정해진 채팅 채널에 입력하는 구조입니다. 두 가지가 분리되어 있다는 점만 기억하면 됩니다.
              </p>
            </QA>
            <QA q="아무 채팅 채널에 써도 다 읽어주나요?" delay={0.05}>
              <p>
                아닙니다. 봇은 서버 설정에서 <strong>TTS 채널로 지정된 채팅 채널</strong>의 글만 읽습니다. 일반 잡담 채널이나 명령어 채널에 글을 써도 음성으로 나오지 않습니다.
                이렇게 채널을 분리해 두는 이유는, 모든 메시지를 다 읽으면 음성이 끊임없이 겹쳐 시끄러워지기 때문입니다. 읽히길 원하는 글은 반드시 지정된 TTS 채널에 입력하세요.
                어느 채널이 TTS 채널인지는 서버 관리자가 대시보드에서 설정하며, 보통 채널 이름이나 안내 메시지로 구분할 수 있습니다.
              </p>
            </QA>
          </Section>

          <Section title="목소리 선택과 대시보드 설정" color="#e58fb6" delay={0.15}>
            <QA q="데비 목소리와 마를렌 목소리는 어떻게 다른가요?">
              <p>
                봇 이름이기도 한 데비(Debi)와 마를렌(Marlene), 두 가지 목소리 중에서 서버 취향에 맞는 쪽을 고를 수 있습니다.
                같은 문장이라도 어느 목소리로 읽느냐에 따라 분위기가 달라지므로, 두 목소리를 번갈아 들어 보고 서버 멤버들이 더 듣기 편한 쪽으로 정하는 것을 추천합니다.
                목소리는 한 번 설정하면 그 서버의 TTS 전체에 동일하게 적용됩니다.
              </p>
            </QA>
            <QA q="목소리와 읽을 채널은 어디서 바꾸나요?" delay={0.05}>
              <p>
                목소리 종류와 봇이 읽어줄 TTS 채널은 모두 대시보드(debimarlene.com)의 <strong>서버 설정</strong>에서 변경합니다. Discord로 로그인한 뒤 해당 서버를 선택하고 TTS 항목에서 목소리와 채널을 지정하면 됩니다.
                이 설정은 <strong>관리자 권한</strong>이 필요하므로, 일반 멤버라면 서버 관리자에게 원하는 목소리나 채널을 요청하세요.
                서버 안에서 <code>/설정</code> 명령으로도 공지·TTS·알림 등 서버 설정 항목에 접근할 수 있으며, 이 역시 관리자 전용입니다.
              </p>
            </QA>
          </Section>

          <Section title="크레딧 소모와 소리 점검" color="#34a853" delay={0.2}>
            <QA q="TTS를 쓰면 크레딧이 얼마나 드나요?">
              <p>
                TTS는 봇이 실제로 음성을 송출한 시간을 기준으로 <strong>10초당 1크레딧</strong>이 차감됩니다. 짧은 문장은 거의 들지 않고, 긴 글을 자주 읽힐수록 크레딧이 더 빠르게 소모됩니다.
                크레딧은 debimarlene.com에서 매일 출석체크(+10, 연속 3일 +30·7일 +100)로 모으거나, 대시보드 충전으로 채울 수 있습니다.
                남은 크레딧이 부족하면 TTS 송출이 멈출 수 있으니, 음성을 길게 쓸 예정이라면 미리 잔액을 확인해 두는 편이 좋습니다.
              </p>
            </QA>
            <QA q="TTS 소리가 전혀 안 들려요." delay={0.05}>
              <p>
                가장 흔한 세 가지부터 점검하세요. ① 본인이 봇과 <strong>같은 음성 채널</strong>에 들어와 있는지, ② 내 Discord에서 봇 사용자가 개별 <strong>음소거</strong>되어 있지 않은지(봇 아이콘 우클릭으로 확인), ③ 글을 쓴 채널이 실제로 설정된 <strong>TTS 채널</strong>이 맞는지 확인합니다.
                그래도 안 들리면 봇 역할이 그 음성 채널에서 <strong>연결·말하기</strong> 권한을 가지고 있는지, 그리고 크레딧 잔액이 남아 있는지 살펴보세요. 권한이 막혀 있으면 봇이 채널에 들어와도 소리를 내보내지 못합니다.
              </p>
            </QA>
            <QA q="봇이 들어왔는데 일부만 읽거나 중간에 멈춰요." delay={0.1}>
              <p>
                지정된 TTS 채널이 아닌 곳에 쓴 글은 처음부터 읽지 않으므로 누락처럼 느껴질 수 있습니다. 읽히는 글과 안 읽히는 글이 섞여 있다면, 메시지를 입력한 채널이 일관되게 TTS 채널인지 다시 확인하세요.
                또 크레딧이 도중에 소진되면 송출이 중단될 수 있습니다. 그 밖의 끊김이나 오작동이 반복되면 <code>/피드백 내용:상황 설명</code>으로 개발자에게 알려 주시면 점검에 도움이 됩니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              TTS 설정이 헷갈리거나 소리 문제가 계속되나요? <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
