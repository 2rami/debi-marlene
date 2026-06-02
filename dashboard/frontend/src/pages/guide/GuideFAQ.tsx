import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 자주 묻는 질문 (FAQ) — 공개 페이지. AdSense 심사에서 QA 구조가 가장 빠르게
 * 콘텐츠로 인정된다. 봇 실제 기능 + 이터널 리턴 게임 지식 기반의 독창적 답변.
 */
export default function GuideFAQ() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            FAQ
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            자주 묻는 질문
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Debi &amp; Marlene 봇을 처음 쓰는 분들이 가장 많이 묻는 질문을 모았습니다.
            이터널 리턴 전적 검색, TTS 음성, 음악, 크레딧까지 — 막히는 부분을 여기서 먼저 찾아보세요.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="봇 시작하기" color="#5865f2" delay={0.1}>
            <QA q="봇을 서버에 어떻게 초대하나요?">
              <p>
                debimarlene.com 메인 페이지의 <strong>봇 초대</strong> 버튼을 누르면 Discord 인증 화면이 열립니다.
                봇을 추가할 서버를 고르고 권한에 동의하면 끝입니다. 초대에는 서버 <strong>관리자 권한</strong>이 필요하므로,
                관리자가 아니라면 서버 관리자에게 요청해 주세요.
              </p>
            </QA>
            <QA q="봇이 메시지에 반응하지 않아요." delay={0.05}>
              <p>
                대부분 권한 문제입니다. 봇 역할이 해당 채널에서 <strong>메시지 보기·메시지 보내기</strong> 권한을 갖고 있는지,
                그리고 봇 역할이 다른 역할에 의해 채널에서 차단되지 않았는지 확인하세요.
                슬래시 명령어(<code>/</code>)가 목록에 안 뜨면 봇을 한 번 추방했다가 다시 초대하면 명령어가 재등록됩니다.
              </p>
            </QA>
          </Section>

          <Section title="이터널 리턴 전적 · 통계" color="#3cabc9" delay={0.15}>
            <QA q="전적은 어떻게 검색하나요?">
              <p>
                <code>/전적 닉네임:플레이어명</code> 형식으로 입력합니다. 닉네임은 이터널 리턴 게임 내 닉네임과 정확히 일치해야 하며,
                대소문자·띄어쓰기까지 같아야 검색됩니다. 결과로 최근 시즌 MMR(랭크 점수), 평균 순위, 모스트 캐릭터,
                최근 경기 기록을 보여줍니다.
              </p>
            </QA>
            <QA q="전적이 '플레이어를 찾을 수 없음'으로 나와요." delay={0.05}>
              <p>
                ① 닉네임 철자가 게임 내 표기와 다를 때, ② 해당 시즌에 랭크 게임 전적이 없을 때 주로 발생합니다.
                이터널 리턴은 닉네임 변경이 가능하므로, 옛 닉네임으로 검색하면 안 나올 수 있습니다. 현재 사용 중인 닉네임으로 다시 시도해 보세요.
              </p>
            </QA>
            <QA q="/통계는 왜 다이아 이상만 볼 수 있나요?" delay={0.1}>
              <p>
                <code>/통계</code>는 캐릭터별 픽률·승률 같은 메타 지표를 보여주는데, 이 통계는 일정 티어(다이아몬드+) 이상의
                경기 데이터를 기준으로 집계됩니다. 낮은 티어 데이터까지 섞으면 숙련도 편차가 커서 메타 판단에 방해가 되기 때문에,
                상위 티어 표본만으로 신뢰도 높은 통계를 제공합니다.
              </p>
            </QA>
            <QA q="시즌 정보나 동접자 수도 볼 수 있나요?" delay={0.15}>
              <p>
                <code>/시즌</code>으로 현재 시즌 번호와 시즌 종료까지 남은 추정 기간을, <code>/동접</code>으로 실시간 동접자 수를 확인할 수 있습니다.
                시즌 막바지에는 랭크 점수가 초기화되므로, 티어 보상을 노린다면 <code>/시즌</code>으로 남은 일수를 미리 체크하는 걸 추천합니다.
              </p>
            </QA>
          </Section>

          <Section title="TTS 음성 · 음악" color="#e58fb6" delay={0.2}>
            <QA q="TTS(음성 읽기)는 어떻게 쓰나요?">
              <p>
                음성 채널에 들어간 뒤 <code>/tts</code>를 입력하면 봇이 같은 채널에 입장합니다. 이후 지정된 TTS 채팅 채널에
                글을 쓰면 봇이 데비 또는 마를렌 목소리로 읽어줍니다. 목소리 종류와 읽어줄 채널은 대시보드(debimarlene.com)의
                서버 설정에서 바꿀 수 있습니다.
              </p>
            </QA>
            <QA q="TTS 소리가 안 들려요." delay={0.05}>
              <p>
                ① 봇과 같은 음성 채널에 있는지, ② 본인 Discord에서 봇이 음소거되지 않았는지, ③ 글을 쓴 채널이 설정된
                TTS 채널이 맞는지 확인하세요. 봇이 음성 채널 <strong>연결·말하기</strong> 권한을 가져야 송출됩니다.
              </p>
            </QA>
            <QA q="음악 재생이 안 돼요." delay={0.1}>
              <p>
                <code>/음악 검색어:URL또는검색어</code>로 재생합니다. YouTube 정책상 일부 영상(연령 제한·지역 차단·라이브)은
                재생되지 않을 수 있습니다. 다른 영상으로 시도하거나 검색어 방식으로 바꿔 보세요. 봇이 음성 채널에 있어야 재생됩니다.
              </p>
            </QA>
          </Section>

          <Section title="크레딧 · 대화" color="#34a853" delay={0.25}>
            <QA q="크레딧은 어디에 쓰나요?">
              <p>
                크레딧은 봇의 AI 대화(<code>/대화</code>)와 TTS 사용에 쓰이는 재화입니다. <code>/대화</code>는 하루 무료 5회가 주어지고,
                그 이후부터 메시지당 크레딧이 차감됩니다. TTS는 10초당 1크레딧이 소모됩니다.
              </p>
            </QA>
            <QA q="크레딧은 어떻게 모으나요?" delay={0.05}>
              <p>
                debimarlene.com에 Discord로 로그인한 뒤 <strong>매일 출석체크</strong>로 +10, 연속 출석 보너스(3일 +30, 7일 +100)를 받을 수 있습니다.
                더 필요하면 대시보드의 <strong>크레딧 충전</strong>으로 채울 수 있고, 충전 시 금액대별 보너스 크레딧이 추가로 지급됩니다.
              </p>
            </QA>
            <QA q="충전한 크레딧을 환불할 수 있나요?" delay={0.1}>
              <p>
                결제일로부터 7일 이내, 충전한 크레딧을 <strong>아직 사용하지 않은 경우</strong>에 한해 환불할 수 있습니다.
                일부라도 사용한 충전분은 환불 대상에서 제외됩니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              찾는 답이 없나요? <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
