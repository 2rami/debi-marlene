import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 캐릭터 통계 활용 가이드 — 공개 페이지. /통계 메타 지표를 읽는 법과
 * 픽률·승률을 함께 보는 이유를 실제 활용 시나리오 중심으로 정리. 구체 수치/캐릭터명은 지어내지 않는다.
 */
export default function GuideCharacters() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            GUIDE
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            캐릭터 통계 활용 가이드
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            이터널 리턴은 시즌마다 강한 캐릭터가 바뀌는 메타 중심 게임입니다. Debi &amp; Marlene 봇의 <code>/통계</code> 명령어는
            지금 어떤 캐릭터가 많이 뽑히고 실제로 이기고 있는지를 한눈에 보여줍니다. 이 페이지에서는 통계를 읽는 법과,
            픽률과 승률을 함께 봐야 하는 이유, 그리고 그 숫자를 실제 캐릭터 선택과 밴픽에 연결하는 방법을 설명합니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="/통계는 어떤 숫자를 보여주나요" color="#e58fb6" delay={0.1}>
            <QA q="픽률과 승률은 각각 무엇을 뜻하나요?">
              <p>
                <code>/통계</code>는 캐릭터별 <strong>픽률</strong>과 <strong>승률</strong>이라는 두 가지 메타 지표를 보여줍니다.
                픽률은 집계된 전체 경기 중 그 캐릭터가 선택된 비율로, 사람들이 얼마나 자주 고르는지 — 즉 메타에서의 인기와 체감 강함을 나타냅니다.
                승률은 그 캐릭터를 골랐을 때 실제로 좋은 결과(이터널 리턴은 배틀로얄이라 보통 최종 1위 또는 상위권 진입)로 이어진 비율입니다.
                두 숫자는 측정하는 대상이 완전히 다르기 때문에, 하나만 보면 캐릭터의 진짜 가치를 오판하기 쉽습니다.
              </p>
            </QA>
            <QA q="통계 숫자는 실시간으로 계속 바뀌나요?" delay={0.05}>
              <p>
                메타 통계는 누적된 경기 데이터를 바탕으로 집계되므로, 패치로 캐릭터가 상향·하향되거나 새 캐릭터가 추가되면
                며칠에 걸쳐 픽률과 승률이 함께 움직입니다. 그래서 패치 직후의 숫자는 아직 표본이 적어 출렁일 수 있고,
                메타가 안정되면 값이 차분해집니다. 정확한 현재 수치와 캐릭터별 순위는 시점에 따라 달라지므로,
                직접 <code>/통계</code>를 입력해 그날의 데이터를 확인하는 것이 가장 정확합니다.
              </p>
            </QA>
          </Section>

          <Section title="왜 다이아몬드+ 기준으로 집계하나요" color="#3cabc9" delay={0.15}>
            <QA q="낮은 티어 데이터를 빼는 이유가 뭔가요?">
              <p>
                <code>/통계</code>는 다이아몬드 이상 티어의 경기 데이터를 기준으로 집계합니다. 낮은 티어에서는 같은 캐릭터라도
                숙련도 편차가 워낙 커서, 캐릭터 자체의 성능보다 플레이어 개인 실력이 결과를 좌우하는 경우가 많습니다.
                이런 데이터까지 모두 섞으면 캐릭터의 본래 강함이 노이즈에 묻혀 메타 판단이 흐려집니다. 반대로 상위 티어는
                운영·교전·아이템 빌드가 어느 정도 정석화돼 있어, 캐릭터 간 성능 차이가 결과에 더 또렷하게 반영됩니다.
              </p>
            </QA>
            <QA q="그 통계를 일반 게임에 그대로 적용해도 되나요?" delay={0.05}>
              <p>
                큰 흐름(어떤 캐릭터가 강세인지)은 대부분 티어에 공통으로 적용되지만, 상위 티어 통계는 어려운 콤보나
                정교한 운영을 전제로 한 수치라는 점을 기억해야 합니다. 손에 익지 않은 고난도 캐릭터가 통계상 강하다고 해서
                바로 골랐다가는 그 승률을 본인이 재현하지 못할 수 있습니다. 통계는 <strong>메타의 방향</strong>을 알려주는
                지표로 쓰고, 최종 선택은 본인이 안정적으로 다룰 수 있는 캐릭터인지까지 함께 판단하는 편이 좋습니다.
              </p>
            </QA>
          </Section>

          <Section title="통계를 캐릭터 선택과 밴픽에 쓰는 법" color="#34a853" delay={0.2}>
            <QA q="픽률과 승률을 왜 같이 봐야 하나요?">
              <p>
                픽률이 높은데 승률은 평범한 캐릭터는 인기는 많지만 실제 성능은 무난한 경우이고, 반대로 픽률은 낮은데
                승률이 높은 캐릭터는 아직 덜 발굴됐거나 다루기 까다로워 잘하는 사람만 쓰는 <strong>숨은 강캐</strong>일 수 있습니다.
                픽률만 보면 유행을 따라가게 되고, 승률만 보면 표본이 적어 우연히 높게 찍힌 캐릭터에 속을 수 있습니다.
                두 지표를 겹쳐 봐야 비로소 그 캐릭터가 지금 메타에서 어떤 위치인지가 입체적으로 드러납니다.
              </p>
            </QA>
            <QA q="이 통계를 밴픽에 어떻게 활용하나요?" delay={0.05}>
              <p>
                밴픽이 있는 모드라면, 픽률과 승률이 동시에 높은 캐릭터는 상대가 먼저 가져갈 가능성이 크니 우선 밴 또는 빠른 선픽 대상으로 고려할 수 있습니다.
                내가 픽할 때는 통계상 안정적인 캐릭터 중 손에 익은 것을 1순위로 두고, 상대 조합을 보고 카운터가 되는 캐릭터를
                보조로 준비해 두면 좋습니다. 단, 통계는 평균값일 뿐이라 그날의 동선·구도·팀 합에 따라 결과는 얼마든지 달라질 수 있으니,
                숫자를 절대 기준이 아니라 <strong>판단의 출발점</strong>으로 삼는 것이 핵심입니다.
              </p>
            </QA>
            <QA q="내 캐릭터 숙련도는 어디서 확인하나요?" delay={0.1}>
              <p>
                메타 통계가 전체 플레이어 기준이라면, 본인이 어떤 캐릭터로 잘 풀리는지는 개인 전적으로 봐야 합니다.
                <code>/전적 닉네임:플레이어명</code>으로 모스트 캐릭터와 평균 순위를 확인하면, 내가 실제로 좋은 성적을 내는
                캐릭터가 무엇인지 알 수 있습니다. <code>/통계</code>의 메타 강캐와 내 전적의 모스트 캐릭터가 겹치는 지점을 찾으면,
                메타와 숙련도가 모두 받쳐주는 가장 안정적인 선택지를 고를 수 있습니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              통계 해석이나 봇 사용이 궁금하신가요? <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
