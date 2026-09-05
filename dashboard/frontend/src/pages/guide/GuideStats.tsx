import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 캐릭터 통계 가이드 — 공개 페이지. /통계 화면의 실제 구성(다이아+ 표본, 3일·7일 기간,
 * 티어순·승률순·픽률순 정렬, 패치 표기)을 기준으로 승률과 픽률을 함께 읽는 법을 설명한다.
 */
export default function GuideStats() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            캐릭터 통계 가이드
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            캐릭터 통계 보는 법
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            <code>/통계</code>는 지금 어떤 실험체가 잘 나가는지를 승률과 픽률로 보여주는 명령입니다.
            패치가 잦은 게임이라 어제까지 좋던 픽이 오늘 나빠지기도 하는데, 이 표는 최근 며칠간의 실제 경기 결과를 모아 그 변화를 따라갑니다.
            다만 승률만 보고 픽을 고르면 자주 실패합니다. 표본이 어디서 왔는지, 픽률이 무엇을 말하는지 함께 읽어야 합니다.
            이 문서는 화면의 각 요소가 무슨 뜻인지와, 이 숫자로 픽을 고를 때 빠지기 쉬운 함정을 정리합니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="표본 — 이 숫자는 어디서 왔나" color="#3cabc9" delay={0.1}>
            <QA q="어떤 플레이어들의 기록인가요?">
              <p>
                <strong>다이아몬드 이상</strong> 구간의 스쿼드 경기만 모은 통계입니다. 화면 아래에 &lsquo;다이아+&rsquo;라고 적혀 있는 것이 그 표시입니다.
                구간을 높게 잡은 이유는, 실험체의 강함을 보려면 그 실험체를 제대로 다루는 사람들의 기록이어야 하기 때문입니다.
                낮은 구간까지 전부 섞으면 조작 난이도가 높은 실험체의 승률이 실제보다 낮게 나와, 강한데 어려운 픽과 그냥 약한 픽이 구분되지 않습니다.
                뒤집어 말하면 <strong>내 구간이 다이아 아래라면 이 표가 곧 내 성적표는 아니라는</strong> 뜻이기도 합니다.
              </p>
            </QA>
            <QA q="3일과 7일 버튼은 무엇을 바꾸나요?" delay={0.05}>
              <p>
                통계를 모으는 기간입니다. <strong>7일</strong>은 표본이 많아 안정적이지만 그만큼 최근 변화가 늦게 반영되고,
                <strong>3일</strong>은 표본이 적어 흔들리는 대신 지금 분위기를 빨리 보여줍니다.
                패치 직후에는 3일로 흐름을 보고, 패치가 안정된 뒤에는 7일로 판단하는 식으로 나눠 쓰면 좋습니다.
                화면 아래에 그 기간에 집계된 총 게임 수가 함께 표시되므로, 숫자를 얼마나 믿을지 가늠하는 기준으로 삼으세요.
              </p>
            </QA>
            <QA q="패치 번호는 왜 표시되나요?" delay={0.1}>
              <p>
                통계가 어느 패치 기준인지 알려 줍니다. 실험체 성능은 패치로 바뀌기 때문에, 방금 패치가 적용됐다면 그 전 데이터가 섞여 있을 수 있습니다.
                패치가 막 나온 직후의 표는 아직 옛 환경의 흔적을 담고 있으므로, 며칠 지나 표본이 쌓인 뒤 다시 보는 편이 정확합니다.
              </p>
            </QA>
          </Section>

          <Section title="승률과 픽률 — 함께 읽어야 하는 이유" color="#e58fb6" delay={0.15}>
            <QA q="승률이 높으면 좋은 픽 아닌가요?">
              <p>
                꼭 그렇지는 않습니다. <strong>승률만 높고 픽률이 아주 낮은</strong> 실험체는 대개 소수의 숙련자만 잡는 픽입니다.
                그 사람들이 잘하기 때문에 나온 승률이지, 처음 잡는 사람이 같은 성적을 내지는 못합니다.
                반대로 <strong>픽률이 높은데 승률이 평범한</strong> 실험체는 누가 잡아도 제 몫은 하는, 무난하고 배우기 쉬운 픽인 경우가 많습니다.
                지금 당장 한 판을 이기고 싶다면 후자가, 시간을 들여 주력 픽을 만들 생각이라면 전자가 나을 수 있습니다.
              </p>
            </QA>
            <QA q="픽률이 높다는 건 강하다는 뜻인가요?" delay={0.05}>
              <p>
                강해서 많이 뽑히기도 하지만, <strong>인기가 있어서</strong> 많이 뽑히기도 합니다. 조작이 재미있거나 외형이 좋아서 성능과 무관하게 픽률이 높은 실험체가 늘 있습니다.
                그래서 픽률은 &lsquo;강함&rsquo;이 아니라 &lsquo;얼마나 자주 만나게 되는가&rsquo;로 읽는 편이 정확합니다.
                픽률이 높은 실험체는 상대로 자주 마주친다는 뜻이므로, 그 실험체의 움직임을 익혀 두는 것만으로도 도움이 됩니다.
              </p>
            </QA>
            <QA q="정렬 버튼은 어떻게 쓰면 되나요?" delay={0.1}>
              <p>
                <strong>티어순</strong>은 봇이 승률과 픽률을 함께 반영해 매긴 종합 등급 순서로, 특별한 목적이 없다면 이 정렬로 보는 것이 가장 무난합니다.
                <strong>승률순</strong>은 성적이 좋은 픽을, <strong>픽률순</strong>은 지금 유행하는 픽을 위로 올립니다.
                실전에서는 세 정렬을 번갈아 보는 것이 유용합니다. 승률순 위쪽에 있는데 픽률순에서는 한참 아래인 실험체를 찾으면,
                아직 많이 알려지지 않았지만 성적은 나오는 픽을 골라낼 수 있습니다.
              </p>
            </QA>
          </Section>

          <Section title="실전에서 고를 때" color="#34a853" delay={0.2}>
            <QA q="이 표대로 픽하면 이길 수 있나요?">
              <p>
                통계는 <strong>평균</strong>입니다. 내가 그 실험체를 처음 잡는다면 표의 승률은 나에게 적용되지 않습니다.
                손에 익은 실험체 세 개를 돌려 쓰는 편이, 매 판 표 맨 위를 새로 잡는 것보다 대체로 성적이 좋습니다.
                통계는 &lsquo;무엇을 골라야 하는가&rsquo;보다 <strong>&lsquo;내가 쓰는 픽이 지금 환경에서 어느 위치인가&rsquo;</strong>를 확인하는 데 쓰는 편이 실속 있습니다.
              </p>
            </QA>
            <QA q="주력 픽이 순위에서 내려갔어요. 바꿔야 하나요?" delay={0.05}>
              <p>
                한 단계 내려간 정도라면 대개 바꿀 이유가 되지 못합니다. 숙련도의 차이가 표의 몇 퍼센트보다 큰 경우가 많기 때문입니다.
                다만 패치로 <strong>크게 하향</strong>되어 순위가 눈에 띄게 밀렸다면, 그때는 비슷한 역할의 다른 실험체를 미리 익혀 두는 것이 안전합니다.
                <code>/전적</code>으로 본인의 실험체별 성적을 확인해, 표의 평균과 내 성적을 나란히 놓고 판단하세요.
                표에서는 좋은데 내 성적은 나쁘다면 그 픽이 나와 안 맞는 것이고, 그 반대라면 남들이 못 살리는 픽을 살리고 있다는 뜻입니다.
              </p>
            </QA>
            <QA q="목록이 길어서 원하는 실험체를 찾기 어려워요." delay={0.1}>
              <p>
                화면 아래 좌우 버튼으로 페이지를 넘기면 전체 실험체를 순서대로 볼 수 있고, 현재 위치는 &lsquo;3/7&rsquo;처럼 표시됩니다.
                특정 실험체의 위치를 보고 싶다면 티어순으로 두고 넘기는 편이 빠릅니다.
                버튼은 명령을 부른 사람뿐 아니라 채널에 있는 누구나 누를 수 있으므로, 한 번 띄워 놓고 팀원과 함께 보며 픽을 정할 수 있습니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              내 성적과 비교하려면 <a href="/guide/record/" className="text-[#3cabc9] underline">전적 검색 가이드</a>를,
              실험체 자체가 궁금하다면 <a href="/guide/characters/" className="text-[#3cabc9] underline">캐릭터 가이드</a>를 함께 보세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
