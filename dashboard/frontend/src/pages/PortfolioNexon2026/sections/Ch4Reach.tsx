import CtaSection from '../shared/CtaSection'
import Footer from '../shared/Footer'
import { CONTACT } from '../content/llm'

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
          headline={`라이브로 운영해 본 사람이\n넥슨 LLM 평가에 합류하면 좋겠습니다`}
          sub="158서버 × 9개월 × 매일 측정. 게임 도메인 16년의 사용자 시점과 운영자의 평가 감각이 한 자리에서 만난다면, 그 자리가 곧 이 직무라고 확신합니다."
          items={[
            { label: 'GitHub · debi-marlene', href: CONTACT.github, primary: true },
            { label: 'Live · debimarlene.com', href: CONTACT.domain },
            { label: `Email · ${CONTACT.email}`, href: `mailto:${CONTACT.email}` },
          ]}
        />
      </div>
      <Footer email={CONTACT.email} github={CONTACT.github} domain={CONTACT.domain} edu={CONTACT.edu} />
    </>
  )
}
