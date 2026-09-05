import LegalLayout, { Section } from '../components/legal/LegalLayout'

/**
 * 이용약관. 개인정보처리방침은 /privacy 로 분리했다(→ LegalLayout 주석).
 * 크레딧·광고 조항은 실제 운영에 맞춰 새로 추가한 것이다.
 */
export default function Terms() {
  return (
    <LegalLayout active="terms" title="이용약관" updated="2026년 9월 5일">
      <div className="space-y-8 text-discord-muted leading-relaxed">
        <Section title="1. 서비스 개요">
          <p className="mb-3">
            Debi &amp; Marlene(이하 &ldquo;봇&rdquo;)은 디스코드(Discord) 플랫폼에서 동작하는 종합 관리 및 편의 봇이며,
            debimarlene.com(이하 &ldquo;대시보드&rdquo;)은 그 설정과 이용 현황을 관리하는 웹 서비스입니다.
          </p>
          <p>
            현재 제공하는 주요 기능은 이터널리턴 전적 검색과 캐릭터 통계, 데비·마를렌 목소리의 TTS,
            유튜브 음악 재생, 미니게임(퀴즈), AI 대화, 그리고 대시보드를 통한 서버 관리(환영 메시지, 알림, 채널 설정 등)입니다.
            각 기능의 사용법은 <a href="/commands/" className="text-debi-primary underline">명령어 목록</a>과 기능별 가이드 문서에서 확인하실 수 있습니다.
          </p>
        </Section>

        <Section title="2. 서비스 이용 조건">
          <ul className="list-disc list-inside space-y-2">
            <li>본 서비스를 이용하기 위해서는 디스코드 계정이 필요하며, 디스코드의 자체 이용약관을 함께 준수해야 합니다.</li>
            <li>봇의 버그를 악용하거나, 과도한 요청(도배 등)으로 서버 엔진에 부하를 주는 행위는 엄격히 금지됩니다.</li>
            <li>타인에게 불쾌감을 주거나, 서버 분위기를 훼손하는 등 비정상적인 목적으로 봇을 사용하는 경우 봇 이용이 제한될 수 있습니다.</li>
            <li>자동화된 수단으로 크레딧을 취득하거나 출석 보상을 반복 수령하는 행위, 타인의 계정을 도용하는 행위는 금지되며 적발 시 크레딧 회수 및 이용 제한 대상이 됩니다.</li>
          </ul>
        </Section>

        <Section title="3. 서비스의 제공 및 변경">
          <ul className="list-disc list-inside space-y-2">
            <li>봇의 대부분 기능은 무료로 제공되나, 음성 합성과 같이 외부 자원을 소모하는 기능은 크레딧을 차감하는 방식으로 제공됩니다.</li>
            <li>점검이나 외부 API(이터널리턴 오픈 API, 디스코드 API 등)의 장애 시 사전 통지 없이 서비스가 중단될 수 있습니다.</li>
            <li>서비스의 질적 향상과 기능 보충을 위해 기능 일부가 변경되거나 종료될 수 있습니다. 이용에 큰 영향을 주는 변경은 대시보드 또는 공지 채널을 통해 미리 안내합니다.</li>
          </ul>
        </Section>

        <Section title="4. 크레딧">
          <ul className="list-disc list-inside space-y-2">
            <li>크레딧은 음성 합성 등 일부 기능을 이용할 때 차감되는 서비스 내 이용 단위이며, 현금이나 다른 재화로 환전되지 않습니다.</li>
            <li>크레딧은 대시보드의 출석체크로 무료로 적립할 수 있으며, 별도의 충전 수단을 통해서도 확보할 수 있습니다.</li>
            <li>무료로 적립된 크레딧은 환불 대상이 아닙니다. 유상으로 취득한 크레딧의 환불은 아래 5항을 따릅니다.</li>
            <li>서비스 종료 시에는 사전 공지 후 잔여 크레딧의 처리 방안을 안내합니다.</li>
          </ul>
        </Section>

        <Section title="5. 결제 및 환불">
          <ul className="list-disc list-inside space-y-2">
            <li>결제는 TossPayments 등 외부 결제 대행사를 통해 처리되며, 개발자는 카드 번호 등 결제 수단 정보를 직접 보관하지 않습니다.</li>
            <li>결제 취소 및 환불은 관련 법령 및 소비자 보호 정책에 따라 처리됩니다. 이미 사용한 크레딧에 해당하는 금액은 환불 대상에서 제외될 수 있습니다.</li>
            <li>환불 요청은 <code className="px-1.5 py-0.5 rounded bg-discord-dark text-debi-primary text-sm">/피드백</code> 명령어 또는 아래 문의처로 접수해 주시기 바랍니다.</li>
          </ul>
        </Section>

        <Section title="6. 광고">
          <ul className="list-disc list-inside space-y-2">
            <li>대시보드의 일부 페이지에는 서비스 운영 비용을 충당하기 위한 제3자 광고가 게재될 수 있습니다.</li>
            <li>광고의 내용과 광고주가 제공하는 상품·서비스에 대해 개발자는 책임지지 않으며, 거래는 이용자와 광고주 사이에서 이루어집니다.</li>
            <li>광고 게재에 사용되는 쿠키와 그 거부 방법은 <a href="/privacy/" className="text-debi-primary underline">개인정보처리방침</a>에 안내되어 있습니다.</li>
          </ul>
        </Section>

        <Section title="7. AI 대화 기능">
          <ul className="list-disc list-inside space-y-2">
            <li>AI 대화 기능이 생성하는 답변은 사실과 다를 수 있으며, 의료·법률·금융 등 전문적 판단이 필요한 사안의 근거로 삼아서는 안 됩니다.</li>
            <li>대화 내용은 응답 생성을 위해 외부 AI 서비스로 전송됩니다. 자세한 내용은 <a href="/privacy/" className="text-debi-primary underline">개인정보처리방침</a>을 참고하시기 바랍니다.</li>
            <li>AI 답변으로 인해 발생한 판단이나 결과에 대해 개발자는 책임지지 않습니다.</li>
          </ul>
        </Section>

        <Section title="8. 면책 조항">
          <ul className="list-disc list-inside space-y-2">
            <li>봇 사용 중 외부 플랫폼(유튜브, 이터널리턴, 디스코드 등)의 정책 변경 또는 장애로 인해 발생하는 직간접적인 손해에 대해서는 책임지지 않습니다.</li>
            <li>봇이 메시지를 처리하고 읽어주는 과정에서 생길 수 있는 서버 내 구성원 간의 분쟁에 대해 개발자는 개입할 의무가 없습니다.</li>
            <li>개발자는 무료로 제공되는 기능의 영속성이나 완전무결성을 보장하지 않습니다.</li>
          </ul>
        </Section>

        <Section title="9. 약관 변경 및 문의">
          <p>
            본 약관은 서비스 정책 및 법령 변경에 따라 수정될 수 있습니다. 변경된 약관은 대시보드 또는 봇 공지 채널을 통해 안내합니다.
            서비스 이용에 대한 건의사항 및 문의는 디스코드 채팅창에서 <code className="px-1.5 py-0.5 rounded bg-discord-dark text-debi-primary text-sm">/피드백</code> 명령어를 사용하거나,
            <a href="mailto:goenho0613@gmail.com" className="text-debi-primary underline">goenho0613@gmail.com</a>으로 전달해 주시기 바랍니다.
          </p>
        </Section>
      </div>
    </LegalLayout>
  )
}
