import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 서버 설정 가이드 — 공개 페이지. 관리자가 봇을 들인 직후 밟는 순서(권한·채널 지정·
 * 기능별 설정)를 실제 설정 항목(공지 채널·명령어 채널·TTS·환영·유튜브 알림) 기준으로 설명한다.
 */
export default function GuideServerSetup() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            서버 설정 가이드
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            서버 관리자를 위한 설정 안내
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            봇을 서버에 초대한 다음 무엇부터 만져야 할지 정리한 문서입니다.
            초대만 해도 대부분의 명령은 바로 동작하지만, 어느 채널에서 명령을 받을지와 알림을 어디로 보낼지는 서버마다 달라 직접 정해 주어야 합니다.
            설정을 건너뛰면 명령 결과가 대화 채널을 가득 채우거나, 알림이 엉뚱한 곳으로 가서 사람들이 불편해집니다.
            아래 순서대로 한 번만 잡아 두면 그 뒤로는 손댈 일이 거의 없습니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="초대 직후 확인할 것" color="#3cabc9" delay={0.1}>
            <QA q="봇에게 어떤 권한이 필요한가요?">
              <p>
                기본은 <strong>메시지 보기·메시지 보내기</strong>이고, 음성 기능을 쓸 거라면 <strong>음성 채널 연결·말하기</strong>가 추가로 필요합니다.
                권한이 빠져 있으면 봇이 오류를 내는 대신 <strong>아무 반응도 하지 않는</strong> 경우가 많아, 고장으로 오해하기 쉽습니다.
                명령을 넣었는데 조용하다면 그 채널에서 봇 역할의 권한부터 확인해 보세요.
                가장 간단한 방법은 초대할 때 관리자 권한을 함께 주는 것이지만, 권한을 좁게 유지하고 싶다면 위의 네 가지만 열어 두어도 대부분의 기능이 동작합니다.
              </p>
            </QA>
            <QA q="설정은 어디서 하나요?" delay={0.05}>
              <p>
                두 갈래가 있습니다. 서버 안에서 <code>/설정</code>을 입력하면 공지 채널·TTS·알림 같은 항목에 바로 접근할 수 있고,
                웹 대시보드(debimarlene.com)에 디스코드 계정으로 로그인하면 서버 목록에서 해당 서버를 골라 같은 항목을 화면으로 관리할 수 있습니다.
                항목이 여럿일 때는 대시보드 쪽이 한눈에 보여 편하고, 한 가지만 빠르게 바꿀 때는 명령이 빠릅니다.
                두 곳 모두 <strong>관리자 권한</strong>이 있어야 보입니다.
              </p>
            </QA>
            <QA q="일반 멤버도 설정을 볼 수 있나요?" delay={0.1}>
              <p>
                설정 변경은 관리자만 할 수 있습니다. 일반 멤버가 <code>/설정</code>을 입력하면 권한 안내가 나옵니다.
                다만 <code>/전적</code>·<code>/통계</code>·<code>/퀴즈</code> 같은 기능은 누구나 쓸 수 있으므로,
                멤버들에게는 설정 대신 <a href="/commands/" className="text-[#3cabc9] underline">명령어 목록</a>을 안내해 주면 됩니다.
              </p>
            </QA>
          </Section>

          <Section title="채널 지정" color="#e58fb6" delay={0.15}>
            <QA q="명령어 채널을 따로 두는 게 좋나요?">
              <p>
                사람이 많은 서버라면 권합니다. 전적 검색이나 통계 결과는 화면을 꽤 차지해서, 대화 채널에서 쓰면 나누던 이야기가 위로 밀려 올라갑니다.
                명령어 채널을 지정해 두면 그 채널 밖에서 명령을 넣었을 때 봇이 <strong>어느 채널로 가야 하는지 안내</strong>하므로, 멤버들이 자연스럽게 자리를 옮깁니다.
                반대로 인원이 적고 채널이 하나뿐인 서버라면 지정하지 않는 편이 편합니다. 지정하지 않으면 어느 채널에서든 동작합니다.
              </p>
            </QA>
            <QA q="공지 채널은 무엇에 쓰이나요?" delay={0.05}>
              <p>
                봇이 <strong>먼저 말을 거는 알림</strong>이 나가는 곳입니다. 유튜브 채널에 새 영상이 올라왔을 때의 알림이 대표적입니다.
                사람들이 대화하는 채널로 지정하면 알림이 대화를 끊고, 아무도 안 보는 채널로 지정하면 알림이 묻힙니다.
                공지용 채널이 이미 있다면 그곳이 가장 무난합니다.
              </p>
            </QA>
            <QA q="TTS가 읽을 채널은 왜 따로 정하나요?" delay={0.1}>
              <p>
                모든 채팅을 다 읽으면 음성이 끝없이 겹쳐 시끄러워지기 때문입니다. 그래서 봇은 <strong>지정된 채널의 글만</strong> 읽습니다.
                게임 중 콜을 주고받을 채널을 하나 정해 두고 그곳을 TTS 채널로 지정하는 방식이 가장 많이 쓰입니다.
                목소리 선택을 포함한 자세한 설정은 <a href="/guide/tts/" className="text-[#3cabc9] underline">TTS 가이드</a>에 있습니다.
              </p>
            </QA>
          </Section>

          <Section title="기능별 설정" color="#34a853" delay={0.2}>
            <QA q="환영 메시지는 어떻게 켜나요?">
              <p>
                새 멤버가 들어왔을 때 인사 메시지와 이미지를 자동으로 보내는 기능입니다. 대시보드의 환영 항목에서 켜고, 문구와 보낼 채널을 지정합니다.
                서버에 처음 들어온 사람에게 규칙이나 채널 안내를 전달하는 자리로 쓰면 유용합니다.
                문구와 이미지 구성은 <a href="/guide/welcome/" className="text-[#3cabc9] underline">환영 메시지 가이드</a>를 참고하세요.
              </p>
            </QA>
            <QA q="유튜브 알림은 어떻게 설정하나요?" delay={0.05}>
              <p>
                알림을 받고 싶은 유튜브 채널을 등록해 두면, 새 영상이 올라올 때 지정한 공지 채널로 알려 줍니다.
                봇이 주기적으로 확인하는 방식이라 업로드와 알림 사이에 약간의 시차가 있습니다. 즉시 오지 않는다고 설정이 잘못된 것은 아닙니다.
                알림이 계속 오지 않는다면 등록한 채널 주소가 맞는지, 공지 채널이 지정되어 있고 그곳에 봇의 메시지 보내기 권한이 있는지 확인하세요.
              </p>
            </QA>
            <QA q="설정을 바꿨는데 반영이 안 돼요." delay={0.1}>
              <p>
                먼저 <strong>바꾼 서버가 맞는지</strong> 확인하세요. 여러 서버를 관리한다면 대시보드에서 다른 서버를 고른 채 저장했을 수 있습니다.
                다음으로 봇이 그 채널에 들어갈 권한이 있는지 봅니다. 설정은 저장됐는데 권한이 없으면 동작만 조용히 실패합니다.
                둘 다 이상이 없는데도 반복된다면 <code>/피드백 내용:상황 설명</code>으로 알려 주세요. 어느 서버의 어떤 항목인지 함께 적어 주시면 확인이 빠릅니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              설정 중 막히는 부분이 있으면 <a href="/guide/faq/" className="text-[#3cabc9] underline">자주 묻는 질문</a>을 먼저 확인하거나,
              <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
