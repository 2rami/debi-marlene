import JdScrollytelling from '../shared/JdScrollytelling'
import EligibilityScrollytelling from '../shared/EligibilityScrollytelling'
import PreferredMarquee from '../shared/PreferredMarquee'
import CasesScrollStack from '../shared/CasesScrollStack'
import { JD_MATCHES, CASES, CHARACTER, GAMES, ELIGIBILITY } from '../content/llm'

/**
 * CH 3 — WHY
 * 04 JD MATCH (4)         : sticky scrollytelling — VaultDial + ContentDial flat stack
 * 05 ELIGIBILITY          : sticky scrollytelling — 캐릭터 도킹 + 좌측 텍스트 dial
 * 06 PREFERRED            : dual marquee (좌/우 반대 방향, scroll velocity 반응)
 * 07 TROUBLESHOOTING (6)  : tabs — Case pills + Row tabs (4 row 컬러)
 *
 * COLLAB 콘텐츠는 JD 4번 evidence 에 이미 들어가 있어 별도 섹션 제거.
 */
export default function Ch3Why() {
  return (
    <>
      {/* 04 — 주요 업무 매칭 */}
      <div id="jdmatch">
        <JdScrollytelling items={JD_MATCHES} />
      </div>

      {/* 05 — 지원 자격 */}
      <EligibilityScrollytelling eligibility={ELIGIBILITY} character={CHARACTER} />

      {/* 06 — 우대 사항 */}
      <PreferredMarquee games={GAMES} />

      {/* 07 — 트러블슈팅 (scroll-stack) */}
      <CasesScrollStack items={CASES} />
    </>
  )
}
