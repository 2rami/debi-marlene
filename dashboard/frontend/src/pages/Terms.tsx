import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from '../components/common/Header'

const termsContent = (
  <div className="space-y-8 text-discord-muted leading-relaxed">
    <Section title="1. 서비스 개요">
      Debi & Marlene(이하 "봇")은 디스코드(Discord) 플랫폼에서 동작하는 종합 관리 및 편의 봇입니다.
      현재 제공하는 주요 기능은 이터널리턴 전적 검색, 게임 통계 제공, 데비/마를렌 목소리의 고품질 TTS 기능, 유튜브 음악 재생, 미니게임(퀴즈), 그리고 대시보드를 통한 서버 관리(환영 메시지, 자동 응답 등)입니다.
    </Section>

    <Section title="2. 서비스 이용 조건">
      <ul className="list-disc list-inside space-y-2">
        <li>본 서비스를 이용하기 위해서는 디스코드 계정이 필요하며, 디스코드의 자체 이용약관을 함께 준수해야 합니다.</li>
        <li>봇의 버그를 악용하거나, 과도한 요청(도배 등)으로 서버 엔진에 부하를 주는 행위는 엄격히 금지됩니다.</li>
        <li>타인에게 불쾌감을 주거나, 서버 분위기를 훼손하는 등 비정상적인 목적으로 봇을 사용하는 경우 봇 이용이 제한될 수 있습니다.</li>
      </ul>
    </Section>

    <Section title="3. 서비스의 제공 및 변경">
      <ul className="list-disc list-inside space-y-2">
        <li>봇의 대부분 기능은 무료로 제공되나, 일부 고급 기능(특정 캐릭터 TTS, 추가 봇 기능 등)은 시스템 안정성을 위해 프리미엄 서비스로 제한되어 제공될 수 있습니다.</li>
        <li>점검이나 외부 API(이터널리턴 오픈 API, 디스코드 API 등)의 장애 시 사전 통지 없이 서비스가 중단될 수 있습니다.</li>
        <li>서비스의 질적 향상과 기능 보충을 위해 기능 일부가 변경되거나 종료될 수 있습니다.</li>
      </ul>
    </Section>

    <Section title="4. 프리미엄 서비스 및 결제">
      <ul className="list-disc list-inside space-y-2">
        <li>프리미엄 서비스 결제는 TossPayments 등 신뢰할 수 있는 외부 결제 대행사를 통해 안전하게 처리됩니다.</li>
        <li>결제 취소 및 환불은 관련 법령 및 소비자 보호 정책에 따라 정당한 사유가 있을 시 처리됩니다.</li>
        <li>프리미엄 혜택은 결제를 진행한 해당 서버에 한하여 적용되며, 서버 내부 사정으로 인한 봇 추방 또는 서버 삭제 시 잔여 기간 혜택 적용에 제한이 있을 수 있습니다.</li>
      </ul>
    </Section>

    <Section title="5. 면책 조항">
      <ul className="list-disc list-inside space-y-2">
        <li>봇 사용 중 외부 플랫폼(유튜브, 이터널리턴, 디스코드 등)의 정책 변경 또는 장애로 인해 발생하는 직간접적인 손해에 대해서는 책임지지 않습니다.</li>
        <li>봇이 메시지를 처리하고 읽어주는 과정에서 생길 수 있는 서버 내 구성원 간의 분쟁에 대해 개발자는 개입할 의무가 없습니다.</li>
        <li>개발자는 무료로 제공되는 기능의 영속성이나 완전무결성을 보장하지 않습니다.</li>
      </ul>
    </Section>

    <Section title="6. 약관 변경 및 문의">
      본 약관은 서비스 정책 및 법령 변경에 따라 수정될 수 있습니다. 변경된 약관은 대시보드 홈페이지 또는 봇 공지 채널을 통해 안내합니다.
      서비스 이용에 대한 건의사항 및 문의는 디스코드 채팅창에서 <code className="px-1.5 py-0.5 rounded bg-discord-dark text-debi-primary text-sm">/피드백</code> 명령어를 사용하거나 공식 서포트 서버를 통해 전달해 주시기 바랍니다.
    </Section>
  </div>
)

const privacyContent = (
  <div className="space-y-8 text-discord-muted leading-relaxed">
    <Section title="1. 수집하는 개인정보의 항목">
      <p className="mb-3">봇과 대시보드는 원활한 기능 제공을 위해 다음과 같은 최소한의 정보를 취급합니다:</p>
      <ul className="list-disc list-inside space-y-2">
        <li><strong className="text-white">사용자 식별 정보</strong>: 디스코드 고유 ID, 닉네임, 아바타 이미지 (Discord OAuth2 연동 시)</li>
        <li><strong className="text-white">디스코드 서버 정보</strong>: 서버 ID, 서버 이름, 멤버 수, 길드 아이콘 설정 (웹 대시보드 관리 및 봇 데이터 연동 목적)</li>
        <li><strong className="text-white">봇 이용 데이터</strong>: 서버 내 봇 설정값(금지어, 환영메시지, TTS 채널 등), 사용자가 입력한 이터널리턴 닉네임 및 명령어 사용 로그 (오류 버그 수정 및 분석 목적)</li>
        <li><strong className="text-white">채팅 데이터 (일시적)</strong>: TTS 서버에서 음성 합성을 위해 채팅 메시지를 읽어들이나, 음성 변환 즉시 파기합니다.</li>
      </ul>
    </Section>

    <Section title="2. 개인정보의 이용 목적">
      <ul className="list-disc list-inside space-y-2">
        <li>Discord 봇 고유의 기능 제공 (이터널리턴 전적 정보 요청, 유튜브 음악 재생, TTS 변환, 퀴즈 게임 등)</li>
        <li>대시보드를 통한 서버 관리 편의성 제공 (디스코드 로그인 세션 유지, 권한 인증)</li>
        <li>사용자 문의 대응 및 프리미엄 서비스 등급 관리</li>
        <li>오류 추적, 신기능 기획 등 시스템 품질 향상을 위한 익명화된 통계 자료 활용</li>
      </ul>
    </Section>

    <Section title="3. 개인정보의 저장, 위탁 및 제3자 제공">
      <ul className="list-disc list-inside space-y-2">
        <li>원칙적으로 사용자 개인정보는 제3자에게 판매하거나 부당하게 제공되지 않습니다.</li>
        <li>단, 원활한 서비스 운영을 위해 다음의 외부 서비스와 API를 연동하고 있으며 이 과정에서 최소한의 데이터가 송수신됩니다.
          <ul className="list-circle list-inside ml-6 mt-1 space-y-1 text-sm text-discord-muted/80">
            <li><span className="text-white">결제 처리</span>: TossPayments</li>
            <li><span className="text-white">음성 생성</span>: Qwen3-TTS 및 외부 음성 합성망</li>
            <li><span className="text-white">게임 전적</span>: 님블뉴런 이터널리턴 OPEN API</li>
          </ul>
        </li>
        <li>서버 정보 등 정적 데이터는 Google Cloud Storage (클라우드 환경) 등에 안전하게 분산되어 저장 및 관리됩니다.</li>
      </ul>
    </Section>

    <Section title="4. 개인정보의 파기 및 사용자의 권리">
      <ul className="list-disc list-inside space-y-2">
        <li>해당 디스코드 서버에서 봇을 추방하는 경우, 내부 보안 정책에 따라 서버 고유 설정 데이터 및 통계 기록에 파기 예정 플래그가 부여되며, 주기적으로 안전하게 삭제됩니다.</li>
        <li>사용자는 대시보드에서 본인의 계정 연동(로그아웃)을 자유롭게 해제할 수 있으며, 이 때 브라우저 세션 정보는 즉각 소멸합니다.</li>
        <li>개발자에게 본인의 데이터 혹은 특정 로그에 대한 삭제를 직접 요청하고 싶은 경우, <code className="px-1.5 py-0.5 rounded bg-discord-dark text-debi-primary text-sm">/피드백</code> 명령어를 통해 전달 부탁드립니다.</li>
      </ul>
    </Section>

    <Section title="5. 아동의 보호">
      본 서비스는 만 14세 미만의 아동을 특정하여 서비스를 제공하지 않으며, 관련 정보를 수집할 의도가 없습니다. 만 14세 미만의 사용자가 정보를 제공한 것이 발견된 경우 해당 데이터는 통보 없이 삭제될 수 있습니다.
    </Section>

    <Section title="6. 개정 및 안내">
      본 처리방침의 개정이 있을 시, 서비스 내 공지사항 및 본 페이지를 통하여 최소 7일 전 안내해 드립니다.
    </Section>
  </div>
)

export default function Terms() {
  const [activeTab, setActiveTab] = useState<'terms' | 'privacy'>('terms')

  return (
    <div className="min-h-screen bg-discord-darkest">
      <Header />
      <div className="max-w-3xl mx-auto px-6 py-24">

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-8 border-b border-white/10 pb-4">
          <button
            onClick={() => setActiveTab('terms')}
            className={`text-xl font-bold transition-colors ${activeTab === 'terms' ? 'text-debi-primary border-b-2 border-debi-primary pb-2 -mb-[18px]' : 'text-discord-muted hover:text-white pb-2'}`}
          >
            이용약관
          </button>
          <button
            onClick={() => setActiveTab('privacy')}
            className={`text-xl font-bold transition-colors ${activeTab === 'privacy' ? 'text-marlene-primary border-b-2 border-marlene-primary pb-2 -mb-[18px]' : 'text-discord-muted hover:text-white pb-2'}`}
          >
            개인정보처리방침
          </button>
        </div>

        {/* Header Info */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-white mb-2">
            {activeTab === 'terms' ? '이용약관' : '개인정보처리방침'}
          </h1>
          <p className="text-discord-muted text-sm">최종 수정일: 2026년 2월 28일</p>
        </div>

        {/* Content Area with Animation */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'terms' ? termsContent : privacyContent}
          </motion.div>
        </AnimatePresence>

      </div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-3">{title}</h2>
      <div>{children}</div>
    </div>
  )
}
