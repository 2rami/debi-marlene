import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 이터널 리턴 전적 검색 가이드 — 공개 페이지. /전적 명령어 한 가지를 깊게 파고드는
 * 독창적 한국어 콘텐츠. 검색 방법 / 결과 해석 / 자주 막히는 점 3단 구성.
 */
export default function GuideEternalReturn() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            가이드
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            이터널 리턴 전적 검색 가이드
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            이터널 리턴은 루미아 섬을 무대로 한 쿼터뷰 배틀로얄입니다. 누가 얼마나 잘하는지는 결국 기록으로 드러나죠.
            Debi &amp; Marlene 봇의 <code>/전적</code> 명령어 하나면 디스코드를 떠나지 않고도 시즌 MMR, 평균 순위, 모스트 캐릭터,
            최근 경기를 한눈에 확인할 수 있습니다. 이 페이지에서는 검색하는 법부터 숫자를 읽는 법, 그리고 잘 안 될 때 무엇을
            점검해야 하는지까지 차근차근 정리했습니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="전적 검색하기" color="#3cabc9" delay={0.1}>
            <QA q="/전적 명령어는 어떻게 입력하나요?">
              <p>
                디스코드 채팅창에 <code>/전적 닉네임:플레이어명</code> 형식으로 입력합니다. 슬래시(<code>/</code>)를 치면
                명령어 목록이 뜨는데 거기서 <code>전적</code>을 고른 뒤, 닉네임 칸에 찾고 싶은 플레이어의 게임 내 이름을 적으면 됩니다.
                예를 들어 친구의 인게임 닉네임이 &ldquo;루미아장인&rdquo;이라면 <code>/전적 닉네임:루미아장인</code>이 되는 식입니다.
                봇이 데이터를 불러와 해당 플레이어의 시즌 성적을 카드 형태로 보여줍니다.
              </p>
            </QA>
            <QA q="닉네임을 정확히 적어야 한다던데, 얼마나 정확해야 하나요?" delay={0.05}>
              <p>
                게임 내 표기와 글자 하나까지 똑같아야 합니다. 대문자와 소문자, 띄어쓰기, 특수문자, 숫자가 모두 일치해야 검색됩니다.
                예컨대 &ldquo;Debi Player&rdquo;와 &ldquo;debiplayer&rdquo;는 봇 입장에서 전혀 다른 닉네임입니다. 검색이 자꾸 빈손으로 돌아온다면
                먼저 닉네임을 게임 로비나 친구 목록에서 복사해 그대로 붙여넣는 방법을 추천합니다. 사람 눈에는 같아 보여도
                공백 하나가 숨어 있는 경우가 의외로 많습니다.
              </p>
            </QA>
            <QA q="내 전적만 볼 수 있나요, 아니면 다른 사람도 검색되나요?" delay={0.1}>
              <p>
                닉네임만 알면 누구든 검색할 수 있습니다. 본인 기록은 물론, 같은 파티의 듀오·스쿼드 팀원, 또는 자꾸 마주치는 상대의
                전적까지 확인할 수 있습니다. 한 판 끝나고 &ldquo;방금 그 사람 잘하던데&rdquo; 싶을 때 닉네임을 넣어 보면 평소 평균 순위와
                모스트 캐릭터가 바로 나오니, 다음 매칭에서 어떤 플레이를 할지 가늠하는 데 도움이 됩니다.
              </p>
            </QA>
          </Section>

          <Section title="결과 해석하기" color="#3cabc9" delay={0.15}>
            <QA q="MMR(랭크 점수)은 무엇을 뜻하나요?">
              <p>
                MMR은 매치 메이킹 레이팅, 즉 실력을 점수로 환산한 값입니다. 랭크 게임에서 좋은 순위로 마무리하면 오르고 일찍 탈락하면
                내려가며, 이 점수에 따라 티어가 정해집니다. 결과 카드에 표시되는 시즌 MMR은 그 플레이어가 이번 시즌에 도달한 위치를
                보여주는 가장 직관적인 지표입니다. 다만 시즌이 끝나면 랭크가 초기화되므로, MMR은 &ldquo;이 시즌 기준&rdquo;의 현재 위치라는
                점을 기억해 두세요. 구체적인 티어 명칭이나 컷 점수는 시즌마다 달라지니, 정확한 값은 항상 봇 결과를 직접 확인하는 게 안전합니다.
              </p>
            </QA>
            <QA q="평균 순위는 왜 중요한가요?" delay={0.05}>
              <p>
                이터널 리턴은 한 경기에 여러 팀이 들어와 최후까지 살아남는 방식이라, 평균 순위가 실력을 가장 솔직하게 드러냅니다.
                킬을 많이 따도 중반에 죽어 버리면 순위가 낮고, 화려하지 않아도 꾸준히 상위권으로 마무리하면 평균 순위가 좋습니다.
                숫자가 작을수록(1등에 가까울수록) 운영과 생존 판단이 안정적이라는 뜻입니다. 모스트 캐릭터의 평균 순위가 유독 좋다면
                그 캐릭터를 손에 익혔다는 신호이니, 듀오나 스쿼드를 짤 때 참고하기 좋습니다.
              </p>
            </QA>
            <QA q="모스트 캐릭터와 최근 경기는 어떻게 읽나요?" delay={0.1}>
              <p>
                모스트 캐릭터는 그 플레이어가 가장 많이, 그리고 보통 가장 잘 다루는 캐릭터입니다. 상대의 모스트를 알면 그 사람이
                초반 교전형인지 후반 캐리형인지 대략 짐작할 수 있고, 같은 팀이라면 캐릭터가 겹치지 않게 픽을 조율할 수 있습니다.
                최근 경기는 가장 마지막에 치른 게임들의 순위 흐름을 보여줍니다. 최근 몇 판이 연달아 상위권이면 폼이 올라온 상태,
                반대로 들쭉날쭉하면 캐릭터를 바꿔 가며 연습 중일 가능성이 높습니다. 한 줄의 숫자보다 흐름을 보는 게 핵심입니다.
              </p>
            </QA>
            <QA q="전적으로 실력을 가늠하는 팁이 있나요?" delay={0.15}>
              <p>
                한 가지 숫자만 보지 말고 조합으로 읽으세요. MMR이 높아도 최근 경기가 흔들린다면 슬럼프일 수 있고, MMR이 평범해도
                모스트 캐릭터의 평균 순위가 1~3위권이라면 그 캐릭터 한정으로는 위협적입니다. 또한 캐릭터별 메타 흐름이 궁금하다면
                <code>/통계</code>로 픽률·승률을 함께 보면 좋습니다. 통계는 다이아몬드+ 상위 티어 경기를 기준으로 집계되므로,
                지금 상위권에서 무엇이 강한지 판단하는 기준선이 됩니다. 개인 전적과 메타 통계를 나란히 놓고 보면 훨씬 입체적으로 실력을 가늠할 수 있습니다.
              </p>
            </QA>
          </Section>

          <Section title="자주 막히는 점" color="#3cabc9" delay={0.2}>
            <QA q="'플레이어를 찾을 수 없음'이 떠요.">
              <p>
                가장 흔한 원인은 닉네임 불일치입니다. 띄어쓰기나 대소문자가 한 글자라도 다르면 봇은 다른 사람으로 인식해 빈 결과를 돌려줍니다.
                두 번째로 잦은 경우는 해당 시즌에 랭크 전적이 아직 없는 플레이어입니다. 이번 시즌 랭크를 한 판도 돌리지 않았다면 보여줄 기록이
                없는 게 정상입니다. 닉네임을 게임에서 그대로 복사해 다시 시도해 보고, 그래도 안 나오면 본인 또는 그 플레이어가 이번 시즌 랭크를
                돌렸는지 확인해 보세요.
              </p>
            </QA>
            <QA q="분명 아는 사람인데 검색이 안 돼요." delay={0.05}>
              <p>
                이터널 리턴은 닉네임 변경이 가능합니다. 예전에 쓰던 이름으로 검색하면 당연히 안 나오니, 지금 그 사람이 실제로 쓰고 있는
                현재 닉네임으로 다시 찾아보세요. 또 게임을 막 시작했거나 일반전만 즐기는 플레이어라면 랭크 데이터 자체가 없을 수 있습니다.
                이름은 맞는데도 결과가 비어 있다면, 닉네임 문제가 아니라 &lsquo;보여줄 랭크 기록이 없는&rsquo; 상태일 가능성을 함께 의심해 보면 됩니다.
              </p>
            </QA>
            <QA q="결과가 며칠 전 경기까지밖에 안 보여요." delay={0.1}>
              <p>
                전적 데이터는 외부 집계를 거쳐 반영되기 때문에, 방금 끝난 한두 판은 결과에 곧바로 나타나지 않을 수 있습니다. 잠시 뒤 다시
                <code>/전적</code>을 입력하면 최신 경기가 반영되는 경우가 많습니다. 또한 시즌이 바뀌는 시점에는 랭크가 초기화되므로, 새 시즌
                초반에는 전적이 비어 보이는 게 정상입니다. 지금이 시즌 어디쯤인지, 종료까지 얼마나 남았는지 궁금하면 <code>/시즌</code> 명령어로
                현재 시즌 번호와 추정 잔여 일수를 확인할 수 있습니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              검색이 계속 막히거나 버그가 의심되면 <a href="mailto:goenho0613@gmail.com" className="text-[#3cabc9] underline">goenho0613@gmail.com</a>으로 문의해 주세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
