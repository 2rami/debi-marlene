import DashboardLayout from '../components/layout/DashboardLayout'
import OGKeySettings from '../components/settings/OGKeySettings'

export default function Settings() {
  return (
    <DashboardLayout>
      <div className="p-6 md:p-12 lg:p-16 max-w-3xl mx-auto">
        <div className="mb-10">
          <h1 className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-white/50 tracking-tight mb-3">
            개인 설정
          </h1>
          <p className="text-discord-muted text-base md:text-lg">
            서버가 아니라 내 계정에만 적용되는 설정입니다.
          </p>
        </div>

        <div className="bg-discord-darker/60 border border-discord-light/10 rounded-2xl p-6">
          <OGKeySettings />
        </div>
      </div>
    </DashboardLayout>
  )
}
