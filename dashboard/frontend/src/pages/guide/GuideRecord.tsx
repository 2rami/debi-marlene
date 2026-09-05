import Header from '../../components/common/Header'
import { useTheme } from '../../contexts/ThemeContext'
import { FadeIn, QA, Section } from '../../components/guide/GuideElements'

/**
 * 전적 검색 가이드 — 공개 페이지. /전적 화면에 실제로 뜨는 항목(티어·MMR·평균 순위·
 * 승률·평균 킬·모드 전환·실험체 목록)을 하나씩 읽는 법으로 설명한다.
 */
export default function GuideRecord() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen font-body transition-colors duration-500 ${isDark ? 'bg-discord-darkest text-white' : 'bg-[#f8fcfd] text-gray-800'}`}>
      <Header />

      <main className="max-w-4xl mx-auto px-6 pt-32 pb-24">
        <FadeIn className="mb-12">
          <div className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider uppercase mb-4 ${isDark ? 'bg-white/[0.05] text-discord-muted border border-white/[0.08]' : 'bg-white/70 text-gray-500 border border-gray-200/50'}`}>
            전적 검색 가이드
          </div>
          <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            전적 검색 결과 읽는 법
          </h1>
          <p className={`text-base leading-relaxed max-w-2xl ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            <code>/전적</code>은 이터널 리턴 플레이어의 시즌 성적을 디스코드 안에서 바로 불러오는 명령입니다.
            게임을 껐다 켜거나 브라우저로 전적 사이트를 찾아 들어갈 필요 없이, 팀원과 대화하던 채널에서 그대로 확인할 수 있습니다.
            그런데 화면에 뜨는 숫자가 여럿이라 처음 보면 어디를 봐야 할지 헷갈립니다.
            이 문서는 검색하는 방법부터 티어·MMR·평균 순위·승률·평균 킬이 각각 무엇을 뜻하는지, 그리고 그 숫자로 무엇을 판단할 수 있는지를 정리합니다.
          </p>
        </FadeIn>

        <div className="space-y-8">
          <Section title="검색하기" color="#3cabc9" delay={0.1}>
            <QA q="전적은 어떻게 검색하나요?">
              <p>
                채팅창에 <code>/전적</code>을 입력하면 닉네임을 넣는 칸이 나옵니다. 거기에 찾고 싶은 플레이어의 인게임 닉네임을 그대로 적고 보내면 됩니다.
                디스코드 계정 이름이 아니라 <strong>이터널 리턴에서 쓰는 닉네임</strong>이라는 점에 주의하세요. 두 이름이 다른 사람이 많아서, 여기서 어긋나면 검색이 실패합니다.
                본인 전적뿐 아니라 다른 사람의 닉네임도 검색할 수 있으므로, 같이 게임할 팀원의 실력을 미리 보고 싶을 때도 씁니다.
              </p>
            </QA>
            <QA q="닉네임을 정확히 썼는데 못 찾는다고 나와요." delay={0.05}>
              <p>
                이터널 리턴 닉네임은 <strong>대소문자와 띄어쓰기를 구분</strong>합니다. 눈으로는 같아 보여도 공백이 하나 더 들어갔거나 대문자가 소문자로 바뀌면 다른 닉네임으로 취급됩니다.
                게임 안에서 닉네임을 복사해 그대로 붙여넣는 것이 가장 확실합니다.
                또 해당 시즌에 <strong>한 판도 하지 않은 계정</strong>은 기록 자체가 없어 검색되지 않습니다. 시즌 초반이거나 오랜만에 접속한 계정이라면 몇 판 플레이한 뒤 다시 찾아보세요.
              </p>
            </QA>
            <QA q="아무 채널에서나 쓸 수 있나요?" delay={0.1}>
              <p>
                서버 관리자가 명령어 채널을 따로 지정해 두었다면, 그 채널에서만 동작하고 다른 곳에서는 &ldquo;이 명령어는 OO 채널에서만 사용할 수 있어요&rdquo;라는 안내가 나옵니다.
                채널을 나누는 이유는 전적 검색 결과가 화면을 꽤 차지해서 대화가 밀려 올라가기 때문입니다. 안내가 뜨면 알려 준 채널로 옮겨 다시 입력하면 됩니다.
                채널 지정이 없는 서버라면 어느 채널에서든 바로 쓸 수 있습니다.
              </p>
            </QA>
          </Section>

          <Section title="상단 숫자 — 티어와 MMR" color="#e58fb6" delay={0.15}>
            <QA q="티어와 MMR은 무엇이 다른가요?">
              <p>
                <strong>티어</strong>는 아이언부터 이터니티까지 이어지는 등급 이름이고, <strong>MMR</strong>은 그 등급을 결정하는 실제 점수입니다.
                티어가 성적표의 &lsquo;수·우·미&rsquo;라면 MMR은 점수 그 자체라고 보면 됩니다. 같은 다이아몬드라도 MMR이 다르면 실력 차이가 있을 수 있습니다.
                랭크 게임에서 순위가 높으면 MMR이 오르고, 낮으면 내려갑니다. 일정 점수를 넘으면 티어가 한 칸 올라갑니다.
                아직 배치가 끝나지 않았거나 그 시즌 랭크를 하지 않았다면 언랭크로 표시됩니다.
              </p>
            </QA>
            <QA q="MMR 그래프는 무엇을 보여주나요?" delay={0.05}>
              <p>
                최근 경기들의 MMR 변화를 선으로 이어 보여줍니다. 숫자 하나만 보면 지금 위치는 알 수 있어도 <strong>올라가는 중인지 내려가는 중인지</strong>는 알 수 없는데, 그래프는 그 흐름을 보여줍니다.
                꾸준히 우상향이면 실력이 지금 티어보다 위라는 뜻이고, 톱니처럼 오르내리기만 한다면 그 구간에서 정체 중이라는 신호입니다.
                한두 판의 부진보다 전체 기울기를 보는 편이 판단에 도움이 됩니다.
              </p>
            </QA>
          </Section>

          <Section title="핵심 지표 — 평균 순위·승률·평균 킬" color="#34a853" delay={0.2}>
            <QA q="평균 순위가 왜 승률보다 중요한가요?">
              <p>
                이터널 리턴은 여러 팀이 한 판에서 겨루는 배틀로얄이라, 1등이 아니어도 높은 순위로 마치면 점수를 얻습니다.
                그래서 <strong>승률(1등 비율)</strong>은 낮아도 <strong>평균 순위</strong>가 앞이면 꾸준히 점수를 쌓는 플레이어입니다.
                반대로 승률은 높은데 평균 순위가 뒤쪽이면, 잘 풀린 판에서는 이기지만 그렇지 않은 판에서 일찍 탈락한다는 뜻입니다.
                한 판의 결과보다 <strong>평균적으로 어디까지 살아남는가</strong>가 실력을 더 잘 보여주기 때문에, 순위 지표를 먼저 보는 것을 권합니다.
              </p>
            </QA>
            <QA q="평균 킬은 어떻게 읽나요?" delay={0.05}>
              <p>
                평균 킬은 한 판에서 평균 몇 명을 잡았는지입니다. 이 숫자만 따로 보면 오해하기 쉬워서, <strong>평균 순위와 함께</strong> 읽어야 합니다.
                평균 킬이 높은데 평균 순위가 뒤라면 교전은 즐기지만 마무리 단계에서 자주 무너진다는 뜻이고,
                평균 킬이 낮은데 평균 순위가 앞이라면 싸움을 피하며 생존을 우선하는 운영형입니다. 어느 쪽이 옳다기보다 플레이 성향의 차이입니다.
                같이 팀을 짤 사람의 전적을 볼 때 이 조합을 보면, 서로 스타일이 맞을지 가늠할 수 있습니다.
              </p>
            </QA>
            <QA q="게임 수는 왜 같이 봐야 하나요?" delay={0.1}>
              <p>
                표본이 적으면 모든 비율이 흔들립니다. 열 판 남짓한 기록에서 나온 승률 30%와 200판에서 나온 승률 30%는 신뢰도가 전혀 다릅니다.
                게임 수가 적다면 그 숫자는 &lsquo;아직 판단하기 이르다&rsquo;는 뜻으로 받아들이는 편이 안전합니다.
                시즌 초반에 유난히 화려하거나 처참해 보이는 전적이 자주 나오는 것도 이 때문입니다.
              </p>
            </QA>
          </Section>

          <Section title="모드 전환과 실험체 목록" color="#3cabc9" delay={0.25}>
            <QA q="랭크게임과 일반게임을 따로 볼 수 있나요?">
              <p>
                검색 결과 아래 버튼으로 <strong>랭크게임·일반게임·유니온</strong> 기록을 전환해 볼 수 있습니다.
                일반게임은 점수가 걸려 있지 않아 새 실험체를 시험하거나 편하게 즐기는 경우가 많고, 랭크게임은 MMR이 오르내리므로 더 신중하게 플레이합니다.
                그래서 같은 사람이라도 두 모드의 성적이 꽤 다르게 나옵니다. 실력을 가늠하려면 랭크게임 쪽을, 어떤 실험체를 연습 중인지 보려면 일반게임 쪽을 보세요.
              </p>
            </QA>
            <QA q="많이 플레이한 실험체 목록은 어떻게 활용하나요?" delay={0.05}>
              <p>
                가장 많이 플레이한 실험체가 게임 수·승률·평균 순위와 함께 나옵니다. 여기서 그 사람의 <strong>주력 픽</strong>과 <strong>그 픽으로 실제 성적이 나오는지</strong>를 한눈에 볼 수 있습니다.
                게임 수는 많은데 승률과 평균 순위가 낮은 실험체가 있다면 애정으로 잡는 픽이고, 게임 수가 적어도 성적이 좋다면 잘 맞는 픽입니다.
                팀을 짤 때 서로의 주력 실험체를 미리 확인해 두면 역할이 겹치는 상황을 피할 수 있습니다.
                랭크게임 목록에는 그 실험체로 얻거나 잃은 점수도 함께 표시되어, 어떤 픽이 실제로 점수를 벌어다 주는지 알 수 있습니다.
              </p>
            </QA>
          </Section>

          <FadeIn delay={0.3} className={`p-6 rounded-2xl text-center border ${isDark ? 'bg-white/[0.02] border-white/[0.06]' : 'bg-white/60 border-gray-200/50'}`}>
            <p className={`text-sm ${isDark ? 'text-discord-muted' : 'text-gray-500'}`}>
              캐릭터별 승률·픽률이 궁금하다면 <a href="/guide/stats/" className="text-[#3cabc9] underline">캐릭터 통계 가이드</a>를,
              티어 체계가 궁금하다면 <a href="/guide/tier-season/" className="text-[#3cabc9] underline">티어·시즌 가이드</a>를 함께 보세요.
            </p>
          </FadeIn>
        </div>
      </main>
    </div>
  )
}
