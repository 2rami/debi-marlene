import CtaSection from '../shared/CtaSection'
import Footer from '../shared/Footer'
import { CONTACT } from '../content/frontend'

/**
 * CH 4 — REACH
 * CTA + Footer
 */
export default function Ch4Reach() {
  return (
    <>
      <div id="contact">
        <CtaSection
          kicker="LET'S TALK"
          headline={`라이브로 만들어 본 사람이\n메이플AX실 제작 도구에 합류하면 좋겠습니다`}
          sub="Rust GPU 터미널부터 지금 이 페이지까지, 디자인과 프론트엔드 구현을 한 사람이 해 왔습니다. 브라우저에서 시각 요소를 편집하고 실시간으로 협업하는 생성형 AI 제작 도구 — 이미 만들어 본 그 방향으로 합류하고 싶습니다."
          items={[
            { label: 'GitHub · 2rami', href: CONTACT.github, primary: true, external: true },
            { label: 'Live · debimarlene.com', href: CONTACT.domain },
            { label: '이 페이지가 곧 포트폴리오', href: 'https://debimarlene.com/portfolio/nexon/frontend' },
            { label: `Email · ${CONTACT.email}`, href: `mailto:${CONTACT.email}` },
          ]}
        />
      </div>
      <Footer email={CONTACT.email} github={CONTACT.github} domain={CONTACT.domain} edu={CONTACT.edu} />
    </>
  )
}
