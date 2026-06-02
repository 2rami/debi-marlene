import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 봇 소개 — 공개 페이지. 서비스가 무엇이고 왜 만들었는지, 두 캐릭터 컨셉,
 * 핵심 기능과 운영 규모를 신뢰감 있는 톤으로 정리한 독창적 한국어 콘텐츠.
 */
export default function GuideAbout() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            ABOUT
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            Debi &amp; Marlene 소개
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Debi &amp; Marlene은 이터널 리턴을 즐기는 한국 디스코드 커뮤니티를 위해 만든 다기능 봇입니다.
            전적 검색부터 음성 읽기, 음악, 음악 퀴즈, 환영 카드까지 — 서버 운영에 필요한 기능을 하나의 봇으로 묶었습니다.
            로그인 없이 누구나 어떤 봇인지 살펴볼 수 있도록 이 페이지를 준비했습니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="어떤 봇인가요" color="#5865f2" delay={0.1}>
            <QA q="Debi & Marlene은 무엇을 하는 봇인가요?">
              <p>
                이터널 리턴은 루미아 섬을 배경으로 한 쿼터뷰 배틀로얄입니다. MMR 기반 랭크와 티어 시스템, 시즌제로 굴러가는
                이 게임을 디스코드에서 함께 즐기는 한국 커뮤니티가 많지만, 전적 확인·음성 채널 도우미·서버 환영 같은 기능은
                보통 봇 여러 개를 따로 붙여야 했습니다. Debi &amp; Marlene은 그 흩어진 기능들을 하나로 모아, 이터널 리턴
                서버 운영에 필요한 거의 모든 것을 한 봇 안에서 처리하도록 만든 다기능 디스코드 봇입니다.
              </p>
            </QA>
            <QA q="왜 만들게 되었나요?" delay={0.05}>
              <p>
                직접 이터널 리턴을 하면서 친구들과 쓸 봇을 찾다가, 마음에 드는 한 가지가 없어 직접 만든 것이 시작이었습니다.
                전적은 A봇, 음악은 B봇, 환영 메시지는 C봇처럼 봇을 여러 개 굴리는 불편함을 없애고 싶었고, 한국 유저에게
                자연스러운 한글 인터페이스와 게임 친화적인 기능을 한곳에 담고자 했습니다. 그렇게 커뮤니티의 실제 필요에서
                출발해, 지금은 여러 서버가 함께 쓰는 봇으로 자리 잡았습니다.
              </p>
            </QA>
            <QA q="데비와 마를렌은 어떤 캐릭터인가요?" delay={0.1}>
              <p>
                봇은 데비(Debi)와 마를렌(Marlene)이라는 두 캐릭터 컨셉으로 운영됩니다. 두 캐릭터가 짝을 이루는 정체성은
                봇의 분위기뿐 아니라 음성 기능에도 이어집니다. TTS(음성 읽기)에서는 데비 또는 마를렌의 목소리 중 하나를 골라
                채팅을 읽게 할 수 있어, 단순한 기계음이 아니라 서버에 어울리는 개성 있는 목소리를 입힐 수 있습니다.
                목소리 선택은 대시보드(debimarlene.com)의 서버 설정에서 바꿉니다.
              </p>
            </QA>
          </Section>

          <Section title="핵심 기능" color="#3cabc9" delay={0.15}>
            <QA q="이터널 리턴 전적과 메타 통계를 볼 수 있나요?">
              <p>
                <code>/전적 닉네임:플레이어명</code>으로 시즌 MMR(랭크 점수), 평균 순위, 모스트 캐릭터, 최근 경기를 한 번에 확인합니다.
                평균 순위는 실력을 가늠하는 핵심 지표라 자기 폼이나 팀원 폼을 빠르게 읽을 수 있습니다. 메타가 궁금하면
                <code>/통계</code>로 캐릭터별 픽률·승률을 보고, <code>/시즌</code>으로 현재 시즌과 종료까지 남은 추정 일수,
                <code>/동접</code>으로 실시간 동접자 수까지 챙길 수 있습니다.
              </p>
            </QA>
            <QA q="음성 채널에서는 무엇을 할 수 있나요?" delay={0.05}>
              <p>
                음성 채널에 들어가 <code>/tts</code>를 쓰면 지정한 TTS 채널의 채팅을 데비/마를렌 목소리로 읽어 줍니다.
                화면을 못 보는 상황이나 핸즈프리로 채팅을 따라가야 할 때 유용합니다. <code>/음악 검색어:URL또는검색어</code>로
                YouTube 음악을 재생하고, <code>/퀴즈</code>로는 노래 맞히기 음악 퀴즈를 돌려 채팅으로 정답을 판정할 수 있어
                함께 모인 음성 채널을 더 즐겁게 만들어 줍니다.
              </p>
            </QA>
            <QA q="서버 운영과 커뮤니티 기능도 있나요?" delay={0.1}>
              <p>
                새 멤버가 들어오면 커스텀 이미지 카드로 된 환영 메시지를 띄우고, 퇴장 메시지와 입장 시 자동 역할 부여,
                YouTube 채널 새 영상 알림까지 지원합니다. <code>/대화</code>로 AI와 자연스럽게 대화할 수 있고(하루 무료 5회 제공),
                <code>/피드백 내용:...</code>으로 개발자에게 직접 의견을 보낼 수도 있습니다. 대화·TTS 같은 기능에는 크레딧이라는
                재화가 쓰이며, 출석체크나 충전으로 모을 수 있습니다.
              </p>
            </QA>
          </Section>

          <Section title="운영 · 문의" color="#34a853" delay={0.2}>
            <QA q="얼마나 많은 곳에서 쓰고 있나요?">
              <p>
                Debi &amp; Marlene은 현재 약 100개 서버에서 11,000명이 넘는 이용자와 함께 운영되고 있습니다. 여러 커뮤니티가
                매일 쓰는 만큼 안정적인 동작을 우선에 두고, 게임 시즌 변화나 사용자 피드백에 맞춰 기능을 꾸준히 다듬고 있습니다.
                특정 캐릭터 수치나 현재 시즌 번호처럼 자주 바뀌는 정보는 이 페이지에 박제하지 않고, 봇 명령어로 그때그때
                최신값을 확인하도록 안내합니다.
              </p>
            </QA>
            <QA q="대시보드와 웹패널은 무엇인가요?" delay={0.05}>
              <p>
                debimarlene.com은 이용자용 대시보드입니다. Discord로 로그인해 출석체크로 크레딧을 모으고, 크레딧을 충전하거나
                TTS 목소리·읽을 채널 같은 서버 설정을 바꿀 수 있습니다. panel.debimarlene.com은 관리자용 웹패널로, 봇을 도입한
                서버의 운영자가 공지 채널·알림·환영 설정 등을 세부적으로 관리하는 공간입니다. 서버 안에서는 관리자 전용
                <code>/설정</code> 명령어로도 주요 설정을 다룰 수 있습니다.
              </p>
            </QA>
            <QA q="문제가 생기거나 제안하고 싶을 땐 어디로 연락하나요?" delay={0.1}>
              <p>
                서버 안에서는 <code>/피드백 내용:...</code> 명령어로 개발자에게 곧장 의견을 보낼 수 있습니다. 버그 제보, 기능 제안,
                도입 문의 등 더 긴 이야기가 필요하면 개발자 이메일 goenho0613@gmail.com으로 연락해 주세요. 보내 주신 피드백은
                다음 업데이트 우선순위를 정하는 데 직접 반영됩니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              도입이나 제휴가 궁금하신가요? <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
