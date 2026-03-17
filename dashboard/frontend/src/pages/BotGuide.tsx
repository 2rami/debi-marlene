import Header from '../components/common/Header'
import { motion } from 'framer-motion'
import { Shield, Users, MessageSquare, Activity, CheckCircle2 } from 'lucide-react'

export default function BotGuide() {
  const intents = [
    {
      title: 'Presence Intent (상태 인텐트)',
      icon: <Activity className="w-8 h-8" />,
      color: 'from-blue-500/20 to-cyan-500/20 text-cyan-400',
      border: 'border-cyan-500/30',
      description: '봇이 유저의 현재 상태나 플레이 중인 게임 정보를 읽어오기 위해 필요합니다.',
      reasons: [
        '특정 게임(이터널 리턴 등) 플레이 상태에 따른 자동 역할 부여',
        '유저의 상태(온라인, 자리비움 등)에 맞춘 맞춤형 기능 제공'
      ]
    },
    {
      title: 'Server Members Intent (서버 멤버 인텐트)',
      icon: <Users className="w-8 h-8" />,
      color: 'from-purple-500/20 to-pink-500/20 text-pink-400',
      border: 'border-pink-500/30',
      description: '새로운 서버 멤버가 입장하거나 퇴장할 때 발생하는 이벤트를 감지하기 위해 필요합니다.',
      reasons: [
        '새로운 멤버 입장 시 데비&마를렌 커스텀 환영 메시지(인사말 카드) 전송',
        '입장 시 기본 역할(Role) 자동 부여',
        '서버 멤버 통계 기능 제공'
      ]
    },
    {
      title: 'Message Content Intent (메시지 콘텐츠 인텐트)',
      icon: <MessageSquare className="w-8 h-8" />,
      color: 'from-emerald-500/20 to-green-500/20 text-emerald-400',
      border: 'border-emerald-500/30',
      description: '유저가 채팅 채널에 입력하는 텍스트 내용을 봇이 직접 읽고 이해하기 위해 필수적인 권한입니다.',
      reasons: [
        'TTS(음성 읽기) 기능: 유저가 친 채팅을 읽고 음성 채널에 송출',
        '금지어 필터링 설정 및 자동 응답 기능 작동',
        '음악 재생 시 텍스트 채널에서 곡 이름 검색 및 명령 수행'
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-discord-darkest overflow-x-hidden selection:bg-debi-primary/30 selection:text-white">
      <Header />
      
      <main className="max-w-5xl mx-auto px-6 pt-32 pb-24">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-debi-primary mb-6">
            <Shield className="w-5 h-5" />
            <span className="font-semibold text-sm">개인정보 보호 및 앱 권한 안내</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-6">
            <span className="gradient-text">디스코드 인텐트(Intents)</span> 사용 안내
          </h1>
          <p className="text-lg text-discord-muted max-w-2xl mx-auto leading-relaxed">
            Debi & Marlene 봇은 서버 운영과 원활한 기능 제공을 위해 Discord의 <b>Privileged Intents(특권 인텐트)</b> 세 가지를 요청하고 있습니다. 아래에서 봇이 해당 권한들을 어떤 용도로 사용하는지 투명하게 안내해 드립니다.
          </p>
        </motion.div>

        <div className="grid gap-8">
          {intents.map((intent, index) => (
            <motion.div
              key={intent.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.15 }}
              className={`bg-discord-dark rounded-3xl p-8 md:p-10 border ${intent.border} shadow-2xl relative overflow-hidden group`}
            >
              <div className={`absolute -right-20 -top-20 w-64 h-64 bg-gradient-to-br ${intent.color} blur-[80px] opacity-30 group-hover:opacity-50 transition-opacity duration-500`} />
              
              <div className="relative z-10">
                <div className="flex items-center gap-4 mb-6">
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${intent.color} flex items-center justify-center`}>
                    {intent.icon}
                  </div>
                  <h2 className="text-2xl md:text-3xl font-bold text-white">{intent.title}</h2>
                </div>
                
                <p className="text-discord-muted text-lg mb-8 leading-relaxed">
                  {intent.description}
                </p>
                
                <div className="bg-black/20 rounded-2xl p-6 border border-white/5">
                  <h3 className="text-sm font-bold text-white/70 uppercase tracking-widest mb-4">주요 사용 목적</h3>
                  <ul className="space-y-4">
                    {intent.reasons.map((reason, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <CheckCircle2 className="w-6 h-6 text-debi-primary shrink-0 mt-0.5" />
                        <span className="text-gray-200 text-base leading-relaxed">{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  )
}
