import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 환영 메시지·서버 설정 가이드 — 공개 페이지. 관리자 대상.
 * 새 멤버 입장 카드 / 자동 역할 / YouTube 알림 / /설정 / 대시보드 설정 흐름을
 * 실제 운영 시나리오 기준으로 안내. 봇 실제 기능만 사용.
 */
export default function GuideWelcome() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            관리자 가이드
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            환영 메시지와 서버 설정 가이드
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            새 멤버가 들어왔을 때 첫인상을 결정하는 건 환영 메시지입니다. Debi &amp; Marlene 봇은 커스텀 환영 이미지 카드,
            자동 역할 부여, YouTube 채널 알림을 제공하고, 이 모든 설정은 <code>/설정</code> 명령어와 debimarlene.com 대시보드에서
            관리할 수 있습니다. 서버를 처음 세팅하는 관리자라면 이 순서대로 따라오시면 됩니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="새 멤버 입장 — 환영 카드와 자동 역할" color="#5865f2" delay={0.1}>
            <QA q="환영 메시지는 어떻게 동작하나요?">
              <p>
                새 멤버가 서버에 들어오면 봇이 지정된 채널에 <strong>커스텀 환영 이미지 카드</strong>를 자동으로 올립니다.
                단순 텍스트가 아니라 멤버의 프로필과 환영 문구가 담긴 이미지 카드라서, 일반 시스템 메시지보다 훨씬 눈에 띄고
                서버 분위기를 따뜻하게 만들어 줍니다. 새 멤버 입장에서도 "여기 제대로 운영되는 서버구나"라는 첫인상을 받게 됩니다.
              </p>
            </QA>
            <QA q="입장과 동시에 역할을 자동으로 줄 수 있나요?" delay={0.05}>
              <p>
                네, <strong>자동 역할 부여</strong> 기능을 켜 두면 새 멤버가 들어오는 순간 미리 지정한 역할이 자동으로 붙습니다.
                보통 '신규 멤버'나 '인증 대기' 같은 기본 역할을 부여해 두면, 채널 접근 권한을 역할 기준으로 깔끔하게 분리할 수 있어
                서버 관리가 훨씬 수월해집니다. 관리자가 매번 손으로 역할을 달아 줄 필요가 없어지는 게 핵심 이점입니다.
              </p>
            </QA>
            <QA q="누군가 나갈 때 퇴장 메시지도 나오나요?" delay={0.1}>
              <p>
                입장 환영 카드와 마찬가지로 <strong>퇴장 메시지(이미지 카드)</strong>도 설정할 수 있습니다. 멤버 변동을 한눈에
                추적하고 싶은 운영자라면 입장·퇴장을 같은 채널로 모아 두는 걸 추천합니다. 환영 채널과 퇴장 채널을 따로 두는 것도
                가능하니, 서버 규모와 운영 스타일에 맞춰 대시보드에서 자유롭게 지정하세요.
              </p>
            </QA>
          </Section>

          <Section title="대시보드에서 환영 메시지 꾸미기" color="#3cabc9" delay={0.15}>
            <QA q="환영 메시지 채널과 문구는 어디서 바꾸나요?">
              <p>
                debimarlene.com에 Discord로 로그인한 뒤 본인이 관리하는 서버를 선택하면 대시보드가 열립니다. 여기에서
                <strong>환영 메시지를 띄울 채널</strong>과 <strong>환영 문구</strong>를 직접 지정할 수 있습니다. 명령어로 일일이 입력하는 대신
                웹 화면에서 시각적으로 설정하기 때문에, 카드에 어떤 텍스트가 들어갈지 미리 확인하면서 다듬을 수 있습니다.
              </p>
            </QA>
            <QA q="환영 카드 이미지도 직접 꾸밀 수 있나요?" delay={0.05}>
              <p>
                대시보드에서 환영 카드의 문구를 서버 컨셉에 맞게 바꿀 수 있습니다. 게임 서버라면 "루미아 섬에 온 걸 환영해" 같은
                톤으로, 친목 서버라면 좀 더 캐주얼한 인사로 맞춰 보세요. 설정을 저장하면 즉시 반영되므로, 테스트 계정으로 한 번
                들어와 보고 실제 카드가 의도대로 나오는지 확인한 뒤 공개하는 흐름을 권장합니다.
              </p>
            </QA>
            <QA q="설정을 바꿨는데 환영 카드가 안 떠요." delay={0.1}>
              <p>
                먼저 봇이 환영 채널에서 <strong>메시지 보내기·파일 첨부(이미지)</strong> 권한을 가지고 있는지 확인하세요. 이미지 카드는
                첨부 권한이 없으면 송출되지 않습니다. 그리고 대시보드에서 지정한 채널이 실제로 존재하는 채널인지, 저장 버튼을 눌러
                설정이 반영됐는지도 점검하세요. 권한과 채널 지정이 맞는데도 안 뜨면 봇을 추방 후 재초대해 권한을 재동기화하면 해결됩니다.
              </p>
            </QA>
          </Section>

          <Section title="/설정 — 공지 · TTS · YouTube 알림" color="#e58fb6" delay={0.2}>
            <QA q="/설정 명령어는 누가 쓸 수 있나요?">
              <p>
                <code>/설정</code>은 서버 <strong>관리자 전용</strong> 명령어입니다. 공지 채널, TTS 채널, 각종 알림, 대시보드 연동 같은
                서버 전반의 설정을 한곳에서 다룹니다. 일반 멤버에게는 노출되지 않으니, 민감한 설정이 실수로 바뀔 걱정 없이 관리자가
                안전하게 서버를 구성할 수 있습니다. 세부 항목은 대시보드와 연동되어 함께 관리됩니다.
              </p>
            </QA>
            <QA q="YouTube 채널 알림은 어떻게 켜나요?" delay={0.05}>
              <p>
                봇은 지정한 <strong>YouTube 채널의 새 영상 알림</strong>을 서버 채널로 보내 줄 수 있습니다. 스트리머나 콘텐츠 크리에이터가
                운영하는 서버라면, 새 영상이 올라올 때마다 팬들이 놓치지 않도록 알림 채널을 하나 정해 연결해 두는 걸 추천합니다.
                알림이 들어올 채널과 대상 YouTube 채널은 <code>/설정</code>과 대시보드에서 지정합니다.
              </p>
            </QA>
            <QA q="TTS 채널 설정은 환영 설정과 같은 곳에서 하나요?" delay={0.1}>
              <p>
                네, <code>/설정</code>과 대시보드는 공지 채널, 환영 메시지, TTS 채널과 목소리, 각종 알림을 한 화면에서 통합 관리합니다.
                TTS는 음성 채널에 봇이 입장한 뒤 지정된 TTS 채팅 채널의 글을 데비·마를렌 목소리로 읽어 주는 기능인데, 어떤 채널을
                읽을지와 목소리 종류를 여기서 정합니다. 환영부터 음성까지 설정을 한곳에 모아 둔 덕분에 초기 세팅이 직관적입니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              설정이 막히거나 원하는 동작이 안 되나요? <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
