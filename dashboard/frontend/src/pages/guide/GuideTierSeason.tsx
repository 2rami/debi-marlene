import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 티어와 시즌 가이드 — 공개 페이지. MMR/티어 개념과 시즌 운영을 봇 명령어와 엮어
 * 설명한다. 구체 티어 명칭·시즌 번호는 명령어 확인으로 유도(hallucination 방지).
 */
export default function GuideTierSeason() {
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
            티어와 시즌 가이드
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            이터널 리턴은 루미아 섬을 배경으로 한 쿼터뷰 배틀로얄이고, 랭크 게임은 MMR 점수로
            실력을 가르는 시즌제로 굴러갑니다. 내 점수가 어디쯤인지, 시즌이 언제 끝나는지,
            막바지에 티어를 어떻게 굳히는지를 Debi &amp; Marlene 봇 명령어와 함께 정리했습니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="MMR과 티어, 무엇이 다른가" color="#fbbc04" delay={0.1}>
            <QA q="MMR이 정확히 뭔가요?">
              <p>
                MMR(Match Making Rating)은 랭크 게임의 결과로 오르내리는 숫자 점수입니다. 좋은 순위로
                마무리하면 오르고, 일찍 탈락하면 내려갑니다. 티어는 이 MMR 구간을 사람이 읽기 쉽게 묶어
                이름표를 붙인 것이라, 본질은 같은 지표를 다르게 보여주는 셈입니다. 봇에서
                <code>/전적 닉네임:플레이어명</code>을 입력하면 현재 시즌 MMR을 바로 확인할 수 있고,
                닉네임은 게임 내 표기와 대소문자·띄어쓰기까지 정확히 같아야 검색됩니다.
              </p>
            </QA>
            <QA q="티어 이름이나 점수 구간은 어디서 확인하나요?" delay={0.05}>
              <p>
                티어 명칭과 승급에 필요한 점수 구간은 게임 패치마다 조정될 수 있어, 이 페이지에서 특정
                숫자를 못박기보다 봇으로 직접 확인하는 쪽을 권합니다. <code>/전적</code> 결과에 표시되는
                시즌 MMR이 지금 내가 어느 위치인지 알려주는 가장 확실한 기준입니다. 점수가 막 승급선
                근처라면 한두 판의 순위가 티어를 바꿀 수 있으니, 무리한 교전보다 안정적인 순위 관리가
                점수를 지키는 데 유리합니다.
              </p>
            </QA>
            <QA q="평균 순위는 왜 중요한 지표인가요?" delay={0.1}>
              <p>
                이터널 리턴은 막판 한 명만 살아남는 배틀로얄이라, 매판 1등을 강요하기보다 꾸준히 높은
                순위로 마무리하는 실력이 점수에 직접 반영됩니다. 그래서 <code>/전적</code>이 보여주는
                평균 순위가 킬 수보다 더 솔직한 실력 지표입니다. 평균 순위가 낮을수록(=상위권 마무리가
                잦을수록) MMR이 안정적으로 우상향하니, 모스트 캐릭터와 평균 순위를 함께 보면 어떤
                캐릭터에서 내 성적이 가장 좋은지 판단할 수 있습니다.
              </p>
            </QA>
          </Section>

          <Section title="시즌 흐름 읽기 — /시즌 · /동접" color="#fbbc04" delay={0.15}>
            <QA q="현재 시즌과 남은 기간은 어떻게 보나요?">
              <p>
                <code>/시즌</code>을 입력하면 현재 진행 중인 시즌 번호와 시즌 종료까지 남은 추정 일수를
                알려줍니다. 시즌 번호 자체는 패치에 따라 바뀌므로 이 페이지에 적어두기보다 명령어로 그때그때
                확인하는 게 정확합니다. 남은 일수를 미리 알아두면 티어 보상을 노리는 막판 일정 관리가
                훨씬 수월해지고, 친구들과 듀오·스쿼드 약속을 잡을 때도 기준이 됩니다.
              </p>
            </QA>
            <QA q="시즌이 끝나면 내 점수는 어떻게 되나요?" delay={0.05}>
              <p>
                시즌제 게임의 공통 규칙대로, 시즌이 종료되면 랭크 점수(MMR)는 초기화되고 다음 시즌에
                새로 시작합니다. 시즌 보상의 구체적인 지급 기준은 게임 내 공지를 따르지만, 보통 시즌 중 도달한
                티어가 기준이 되는 만큼 목표 구간에 올라가 두는 것이 중요합니다. 그래서 시즌 막바지에는 <code>/시즌</code>으로
                남은 일수를 확인하고, 목표 티어에 도달했다면 점수를 깎아먹을 위험한 판을 줄이는 전략이 유효합니다.
              </p>
            </QA>
            <QA q="/동접으로는 뭘 알 수 있나요?" delay={0.1}>
              <p>
                <code>/동접</code>은 실시간 동접자 수를 보여줍니다. 동접이 많은 시간대에는 매칭이 빠르고
                비슷한 실력대끼리 만날 확률이 높아, 랭크 점수를 안정적으로 올리기에 유리합니다. 반대로
                동접이 적은 새벽 시간대에는 매칭 폭이 넓어져 실력 편차가 큰 판이 나오기도 합니다. 시즌
                막바지에는 보상 경쟁이 몰리며 동접이 늘기 쉬우니, <code>/동접</code>으로 활성도를 보고
                플레이 타이밍을 잡으면 됩니다.
              </p>
            </QA>
          </Section>

          <Section title="시즌 막바지, 티어 굳히기" color="#fbbc04" delay={0.2}>
            <QA q="목표 티어를 찍었는데 더 해야 하나요?">
              <p>
                목표 티어에 도달했고 보상만 받으면 충분하다면, 남은 기간에는 점수를 지키는 쪽으로
                태세를 바꾸는 게 합리적입니다. 한 판의 큰 손실이 어렵게 올린 점수를 깎아내릴 수 있기
                때문입니다. <code>/전적</code>으로 본인 MMR이 승급·강등선에서 얼마나 떨어져 있는지 확인하고,
                여유가 빠듯하다면 익숙한 모스트 캐릭터로 안정적인 순위를 노리는 게 변수를 줄이는 길입니다.
              </p>
            </QA>
            <QA q="막판에 점수를 효율적으로 올리려면?" delay={0.05}>
              <p>
                새 캐릭터 연습이나 모험적인 빌드는 시즌 초·중반에 끝내두고, 막바지에는 평균 순위가 좋은
                검증된 픽으로 좁혀 들어가는 편이 안전합니다. 어떤 캐릭터가 메타에서 강한지 감을 잡고 싶다면
                <code>/통계</code>로 다이아몬드+ 티어 경기 기준의 픽률·승률을 참고하세요. 다만 통계는 흐름을
                읽는 보조 자료일 뿐, 결국 내 평균 순위가 가장 잘 나오는 캐릭터가 막판 점수 방어에는 제일 든든합니다.
              </p>
            </QA>
            <QA q="시즌 끝나기 직전엔 뭘 챙겨두면 좋나요?" delay={0.1}>
              <p>
                먼저 <code>/시즌</code>으로 남은 일수를 한 번 더 확인해 마지막 플레이 일정을 잡고,
                <code>/전적</code>으로 현재 시즌 MMR과 평균 순위를 기록해두면 다음 시즌과 비교하기 좋습니다.
                활성 시간대를 노린다면 <code>/동접</code>으로 매칭이 빠른 타이밍을 고르세요. 점수 초기화는
                실력 리셋이 아니라 모두가 같은 출발선에 서는 것이니, 이번 시즌의 평균 순위 데이터를 기준으로
                다음 시즌 목표를 세우면 꾸준한 성장으로 이어집니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              티어·시즌 관련해 더 궁금한 점이 있으면 <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
