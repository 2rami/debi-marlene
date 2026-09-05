import LegalLayout, { Section } from '../components/legal/LegalLayout'

/**
 * 개인정보처리방침. 원래 Terms 의 탭 안에 있어 크롤러에게 보이지 않았다(→ LegalLayout 주석).
 * 쿠키(방문 통계·광고)와 AI 대화 전송 조항은 실제 동작에 맞춰 새로 추가한 것이다.
 */
export default function Privacy() {
  return (
    <LegalLayout active="privacy" title="개인정보처리방침" updated="2026년 9월 5일">
      <div className="space-y-8 text-discord-muted leading-relaxed">
        <Section title="1. 수집하는 개인정보의 항목">
          <p className="mb-3">봇과 대시보드는 원활한 기능 제공을 위해 다음과 같은 최소한의 정보를 취급합니다:</p>
          <ul className="list-disc list-inside space-y-2">
            <li><strong className="text-white">사용자 식별 정보</strong>: 디스코드 고유 ID, 닉네임, 아바타 이미지 (Discord OAuth2 연동 시)</li>
            <li><strong className="text-white">디스코드 서버 정보</strong>: 서버 ID, 서버 이름, 멤버 수, 길드 아이콘 설정 (웹 대시보드 관리 및 봇 데이터 연동 목적)</li>
            <li><strong className="text-white">봇 이용 데이터</strong>: 서버 내 봇 설정값(공지 채널, 명령어 채널, TTS 채널, 환영 메시지 등), 사용자가 입력한 이터널리턴 닉네임, 명령어 사용 로그 (오류 수정 및 이용 통계 목적)</li>
            <li><strong className="text-white">크레딧 기록</strong>: 출석체크·충전·사용 내역과 잔액</li>
            <li><strong className="text-white">채팅 데이터 (일시적)</strong>: TTS 기능은 지정된 채널의 메시지를 음성으로 합성하며, 변환 직후 해당 텍스트를 파기합니다.</li>
            <li><strong className="text-white">AI 대화 내용</strong>: 사용자가 봇을 호출해 나눈 대화와 그 요약 (아래 4항 참조)</li>
          </ul>
        </Section>

        <Section title="2. 개인정보의 이용 목적">
          <ul className="list-disc list-inside space-y-2">
            <li>Discord 봇 고유의 기능 제공 (이터널리턴 전적 정보 요청, 유튜브 음악 재생, TTS 변환, 퀴즈 게임 등)</li>
            <li>대시보드를 통한 서버 관리 편의성 제공 (디스코드 로그인 세션 유지, 권한 인증)</li>
            <li>크레딧 잔액 관리와 충전·사용 내역 확인</li>
            <li>사용자 문의 대응</li>
            <li>오류 추적, 신기능 기획 등 시스템 품질 향상을 위한 익명화된 통계 자료 활용</li>
          </ul>
        </Section>

        <Section title="3. 쿠키와 유사 기술">
          <p className="mb-3">
            대시보드(debimarlene.com)는 다음 목적으로 쿠키를 사용합니다. 방문 통계와 광고 쿠키는 첫 방문 시 안내 배너를 통해 동의 여부를 확인하며, 거부하셔도 사이트 이용에는 지장이 없습니다.
          </p>
          <ul className="list-disc list-inside space-y-2">
            <li><strong className="text-white">필수 쿠키</strong>: 디스코드 로그인 세션 유지. 이 쿠키가 없으면 로그인 상태가 유지되지 않습니다.</li>
            <li><strong className="text-white">방문 통계 쿠키</strong>: Google Analytics를 통해 어떤 페이지가 얼마나 열람되는지 익명화된 형태로 집계합니다.</li>
            <li><strong className="text-white">광고 쿠키</strong>: 본 사이트는 제3자 광고 제공업체인 Google을 이용하고 있습니다. Google을 포함한 제3자 공급업체는 쿠키를 사용하여 사용자가 이 웹사이트나 다른 웹사이트에 방문한 기록을 바탕으로 광고를 게재합니다.
              <ul className="list-circle list-inside ml-6 mt-1 space-y-1 text-sm text-discord-muted/80">
                <li>Google이 광고 쿠키를 사용함으로써 Google과 그 파트너는 이 사이트 및 다른 사이트 방문 기록을 바탕으로 사용자에게 적절한 광고를 게재할 수 있습니다.</li>
                <li>사용자는 <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer" className="text-debi-primary underline">Google 광고 설정</a>에서 개인 맞춤 광고를 해제할 수 있습니다.</li>
                <li>제3자 공급업체의 쿠키 사용을 해제하려면 <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener noreferrer" className="text-debi-primary underline">www.aboutads.info</a>를 방문하시기 바랍니다.</li>
                <li>브라우저 설정에서 쿠키를 차단하거나 삭제하는 것으로도 언제든 거부할 수 있습니다.</li>
              </ul>
            </li>
          </ul>
        </Section>

        <Section title="4. AI 대화 기능에 관한 고지">
          <ul className="list-disc list-inside space-y-2">
            <li>봇을 호출해 나누는 대화는 응답 생성을 위해 <strong className="text-white">외부 AI 서비스(Anthropic Claude)로 전송</strong>됩니다. 개인정보나 민감한 내용은 입력하지 않으시기를 권합니다.</li>
            <li>대화의 맥락을 이어 가기 위해 사용자별 대화 세션과 요약이 저장됩니다. 이 기록은 다음 대화에서 맥락을 참고하는 용도로만 쓰입니다.</li>
            <li>AI가 생성한 답변은 사실과 다를 수 있으며, 그 내용의 정확성을 보장하지 않습니다.</li>
            <li>본인의 대화 기록 삭제를 원하시는 경우 <code className="px-1.5 py-0.5 rounded bg-discord-dark text-debi-primary text-sm">/피드백</code> 명령어로 요청해 주시기 바랍니다.</li>
          </ul>
        </Section>

        <Section title="5. 개인정보의 저장, 위탁 및 제3자 제공">
          <ul className="list-disc list-inside space-y-2">
            <li>원칙적으로 사용자 개인정보는 제3자에게 판매하거나 부당하게 제공되지 않습니다.</li>
            <li>단, 원활한 서비스 운영을 위해 다음의 외부 서비스와 API를 연동하고 있으며 이 과정에서 최소한의 데이터가 송수신됩니다.
              <ul className="list-circle list-inside ml-6 mt-1 space-y-1 text-sm text-discord-muted/80">
                <li><span className="text-white">AI 대화</span>: Anthropic (Claude)</li>
                <li><span className="text-white">결제 처리</span>: TossPayments</li>
                <li><span className="text-white">음성 생성</span>: 음성 합성 서비스</li>
                <li><span className="text-white">게임 전적</span>: 님블뉴런 이터널리턴 OPEN API</li>
                <li><span className="text-white">음악 재생</span>: YouTube Data API</li>
                <li><span className="text-white">방문 통계·광고</span>: Google (Analytics, AdSense)</li>
              </ul>
            </li>
            <li>서버 설정·크레딧 기록 등은 Google Cloud Firestore와 Google Cloud Storage에 저장되며, 접근 권한은 운영자에게 한정됩니다.</li>
          </ul>
        </Section>

        <Section title="6. 개인정보의 파기 및 사용자의 권리">
          <ul className="list-disc list-inside space-y-2">
            <li>해당 디스코드 서버에서 봇을 추방하는 경우, 내부 보안 정책에 따라 서버 고유 설정 데이터 및 통계 기록에 파기 예정 플래그가 부여되며, 주기적으로 안전하게 삭제됩니다.</li>
            <li>사용자는 대시보드에서 본인의 계정 연동(로그아웃)을 자유롭게 해제할 수 있으며, 이 때 브라우저 세션 정보는 즉각 소멸합니다.</li>
            <li>본인의 데이터 열람·정정·삭제를 원하시는 경우 <code className="px-1.5 py-0.5 rounded bg-discord-dark text-debi-primary text-sm">/피드백</code> 명령어 또는 아래 문의처로 요청해 주시기 바랍니다.</li>
          </ul>
        </Section>

        <Section title="7. 아동의 보호">
          본 서비스는 만 14세 미만의 아동을 특정하여 서비스를 제공하지 않으며, 관련 정보를 수집할 의도가 없습니다. 만 14세 미만의 사용자가 정보를 제공한 것이 발견된 경우 해당 데이터는 통보 없이 삭제될 수 있습니다.
        </Section>

        <Section title="8. 개정 및 문의">
          <p>
            본 처리방침의 개정이 있을 시, 서비스 내 공지사항 및 본 페이지를 통하여 최소 7일 전 안내해 드립니다.
            개인정보 처리에 관한 문의는 <a href="mailto:goenho0613@gmail.com" className="text-debi-primary underline">goenho0613@gmail.com</a>으로 보내 주시기 바랍니다.
          </p>
        </Section>
      </div>
    </LegalLayout>
  )
}
