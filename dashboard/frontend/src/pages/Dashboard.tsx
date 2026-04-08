import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import DashboardLayout from '../components/layout/DashboardLayout'
import Loading from '../components/common/Loading'
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from 'framer-motion'
import {
  Plus,
  Search,
  Server as ServerIcon,
  ExternalLink,
  ChevronRight
} from 'lucide-react'
import AnimatedSection from '../components/common/AnimatedSection'

const getServerAcronym = (name: string) => {
  const acronym = name.split(/\s+/).map(w => w[0]).join('').substring(0, 3).toUpperCase()
  return acronym || name.substring(0, 2).toUpperCase()
}

const getServerGradient = (name: string) => {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const gradients = [
    'from-rose-500 to-pink-500',
    'from-blue-500 to-cyan-500',
    'from-emerald-500 to-teal-500',
    'from-violet-500 to-purple-500',
    'from-amber-500 to-orange-500',
    'from-indigo-500 to-blue-500',
    'from-fuchsia-500 to-rose-500'
  ]
  return gradients[Math.abs(hash) % gradients.length];
}

interface Server {
  id: string
  name: string
  icon: string | null
  memberCount: number
  isAdmin: boolean
  hasBot: boolean
}

const InteractiveServerCard = ({ server, bgGradient, onHover, onLeave }: { server: Server, bgGradient: string, onHover: () => void, onLeave: () => void }) => {
  const ref = useRef<HTMLDivElement>(null)
  
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  
  const mouseXSpring = useSpring(x, { stiffness: 300, damping: 30 })
  const mouseYSpring = useSpring(y, { stiffness: 300, damping: 30 })
  
  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["10deg", "-10deg"])
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-10deg", "10deg"])

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const width = rect.width
    const height = rect.height
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top
    const xPct = mouseX / width - 0.5
    const yPct = mouseY / height - 0.5
    x.set(xPct)
    y.set(yPct)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
    onLeave()
  }
  
  return (
    <div style={{ perspective: 1200 }} className="h-[280px] md:h-[320px]">
      <motion.div
        ref={ref}
        onMouseEnter={onHover}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
        className="block h-full relative group"
      >
        <Link to={`/servers/${server.id}`} className="block h-full outline-none">
          {/* Glowing Shadow Background */}
          <div 
            className={`absolute -inset-1 rounded-[2.5rem] blur-xl opacity-0 group-hover:opacity-40 transition-opacity duration-500 bg-gradient-to-br ${bgGradient}`} 
            style={{ transform: "translateZ(-20px)" }} 
          />
          
          <div 
            style={{ transform: "translateZ(30px)" }} 
            className="relative h-full flex flex-col bg-discord-dark/40 backdrop-blur-2xl border border-white/5 hover:border-white/20 rounded-[2.5rem] p-6 md:p-8 overflow-hidden shadow-2xl transition-colors duration-500"
          >
            {/* Ambient inner glow */}
            <div className={`absolute -right-20 -top-20 w-64 h-64 bg-gradient-to-br ${bgGradient} rounded-full blur-[80px] opacity-10 group-hover:opacity-30 transition-opacity duration-700 pointer-events-none`} />
            
            <div className="flex items-start justify-between mb-8 relative z-10 w-full">
              <div style={{ transform: "translateZ(20px)" }} className="relative">
                {server.icon ? (
                  <img
                    src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.webp?size=256`}
                    alt={server.name}
                    className="w-20 h-20 md:w-24 md:h-24 rounded-[1.8rem] shadow-xl object-cover ring-1 ring-white/10 group-hover:ring-white/30 transition-all duration-300"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden') }}
                  />
                ) : null}
                <div className={`${server.icon ? 'hidden' : ''} w-20 h-20 md:w-24 md:h-24 rounded-[1.8rem] flex items-center justify-center text-3xl font-black text-white shadow-xl bg-gradient-to-br ${bgGradient} ring-1 ring-white/10 group-hover:ring-white/30 transition-all duration-300`}>
                  {getServerAcronym(server.name)}
                </div>
              </div>
              
              <div 
                style={{ transform: "translateZ(15px)" }}
                className="p-3.5 rounded-2xl bg-white/5 text-white/70 border border-white/5 backdrop-blur-md group-hover:bg-white/10 group-hover:text-white transition-all duration-300 shadow-lg"
               >
                <ServerIcon className="w-6 h-6" />
              </div>
            </div>

            <div className="mt-auto relative z-10" style={{ transform: "translateZ(25px)" }}>
              <div className="flex items-center gap-2 mb-3">
                <h3 className="text-2xl font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-white/60 transition-all truncate max-w-full">
                  {server.name}
                </h3>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-black/40 border border-white/5 backdrop-blur-md">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.6)] animate-pulse" />
                  <span className="text-sm font-medium text-emerald-400/90 tracking-wide">{server.memberCount.toLocaleString()} 멤버</span>
                </div>
                <div className="w-10 h-10 rounded-full bg-white/10 border border-white/20 flex justify-center items-center opacity-0 group-hover:opacity-100 -translate-x-4 group-hover:translate-x-0 outline-none transition-all duration-300 shadow-xl">
                  <ChevronRight className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>
          </div>
        </Link>
      </motion.div>
    </div>
  )
}

const InteractiveInviteCard = ({ server, bgGradient, inviteUrl }: { server: Server, bgGradient: string, inviteUrl: string }) => {
  return (
    <div className="h-[280px] md:h-[320px]">
      <div className="relative h-full bg-discord-dark/20 backdrop-blur-xl border border-white/5 rounded-[2.5rem] p-6 md:p-8 hover:bg-discord-dark/30 transition-all duration-500 group overflow-hidden">
        {/* Subtle hover reveal gradient */}
        <div className={`absolute inset-0 bg-gradient-to-br ${bgGradient} opacity-0 group-hover:opacity-5 transition-opacity duration-700`} />
        
        <div className="flex items-start justify-between mb-8 opacity-60 group-hover:opacity-80 transition-opacity duration-300 relative z-10">
          {server.icon ? (
            <img
              src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.png?size=256`}
              alt={server.name}
              className="w-20 h-20 md:w-24 md:h-24 rounded-[1.8rem] grayscale group-hover:grayscale-[50%] transition-all duration-500 object-cover shadow-lg"
            />
          ) : (
            <div className={`w-20 h-20 md:w-24 md:h-24 rounded-[1.8rem] flex items-center justify-center text-3xl font-black text-white/50 grayscale group-hover:grayscale-[50%] transition-all duration-500 bg-gradient-to-br ${bgGradient} shadow-lg`}>
              {getServerAcronym(server.name)}
            </div>
          )}
          <div className="p-3.5 rounded-2xl bg-white/5 text-gray-400 border border-white/5">
            <Plus className="w-6 h-6" />
          </div>
        </div>

        <div className="mt-auto relative z-10">
          <h3 className="text-xl font-bold text-white/40 group-hover:text-white/60 truncate mb-2 transition-colors duration-300">
            {server.name}
          </h3>
          <p className="text-discord-muted/40 font-medium text-sm mb-6 group-hover:text-discord-muted/60 transition-colors duration-300">
            봇이 서버에 없습니다
          </p>
          
          <a
            href={inviteUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center gap-2 py-3.5 rounded-2xl bg-white/5 hover:bg-white/10 text-white/60 hover:text-white border border-white/5 hover:border-white/20 transition-all duration-300 font-semibold text-sm group/invite"
          >
            <span>봇 초대하기</span>
            <ExternalLink className="w-4 h-4 group-hover/invite:translate-x-0.5 group-hover/invite:-translate-y-0.5 transition-transform" />
          </a>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [servers, setServers] = useState<Server[]>([])
  const [botClientId, setBotClientId] = useState<string>(import.meta.env.VITE_DISCORD_CLIENT_ID || '')
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [hoveredGradient, setHoveredGradient] = useState<string | null>(null)

  useEffect(() => {
    const fetchServers = async () => {
      try {
        const response = await api.get<{ servers: Server[], botClientId: string }>('/servers')
        setServers(response.data.servers.filter(s => s.isAdmin))
        if (response.data.botClientId) setBotClientId(response.data.botClientId)
      } catch (error) {
        console.error('Failed to fetch servers:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchServers()
  }, [])

  const getInviteUrl = (guildId: string) => {
    if (!botClientId) return '#'
    const permissions = '8'
    return `https://discord.com/api/oauth2/authorize?client_id=${botClientId}&permissions=${permissions}&scope=bot%20applications.commands&guild_id=${guildId}`
  }

  const filteredServers = servers.filter(server =>
    server.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return <Loading />
  }

  return (
    <DashboardLayout>
      {/* Background Ambient Glow */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <AnimatePresence>
          {hoveredGradient && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 0.15, scale: 1 }}
              exit={{ opacity: 0, scale: 1.1 }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className={`absolute inset-0 bg-gradient-to-br ${hoveredGradient} blur-[150px]`}
            />
          )}
        </AnimatePresence>
      </div>

      <div className="p-6 md:p-12 lg:p-16 max-w-[1600px] mx-auto relative z-10 min-h-screen flex flex-col">
        {/* Welcome Header */}
        <AnimatedSection className="mb-12 md:mb-20">
          <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-8">
            <div className="max-w-2xl">
              <h1 className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-white/50 tracking-tight leading-tight mb-4">
                서버 <br className="hidden md:block" />대시보드
              </h1>
              <p className="text-discord-muted text-lg md:text-xl font-medium leading-relaxed max-w-xl">
                관리할 서버를 선택하세요.
              </p>
            </div>

            {/* Search Bar - Floating Glassmorphic */}
            <div className="relative group w-full xl:w-96">
              <div className="absolute inset[-2px] bg-gradient-to-r from-debi-primary/50 to-marlene-primary/50 rounded-2xl blur-lg opacity-0 group-focus-within:opacity-20 transition-opacity duration-500" />
              <div className="relative flex items-center bg-discord-dark/50 backdrop-blur-xl border border-white/10 rounded-2xl p-2 transition-all duration-300 group-focus-within:border-white/30 group-focus-within:bg-discord-dark/80 group-focus-within:shadow-2xl">
                <div className="pl-4 pr-3">
                  <Search className="w-6 h-6 text-white/40 group-focus-within:text-debi-primary transition-colors duration-300" />
                </div>
                <input
                  type="text"
                  placeholder="서버 이름을 검색하세요..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-transparent text-white text-lg placeholder:text-white/30 py-3 pr-4 focus:outline-none font-medium"
                />
              </div>
            </div>
          </div>
        </AnimatedSection>

        {/* Server Grid - Bento Box / Portfolio Style */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 md:gap-8 pb-20">
          {filteredServers.map((server, idx) => {
            const bgGradient = getServerGradient(server.name)
            // Use larger span for first item naturally if we wanted a true asymmetrical bento, 
            // but for dynamic generated content, a clean consistent 3D grid is very beautiful and robust.
            return (
              <AnimatedSection 
                key={server.id} 
                delay={0.1 + (idx * 0.05)}
                className={`w-full ${idx === 0 && filteredServers.length > 3 ? 'md:col-span-2 lg:col-span-2 xl:col-span-2' : ''}`}
              >
                {server.hasBot ? (
                  <InteractiveServerCard 
                    server={server} 
                    bgGradient={bgGradient} 
                    onHover={() => setHoveredGradient(bgGradient)} 
                    onLeave={() => setHoveredGradient(null)} 
                  />
                ) : (
                  <InteractiveInviteCard 
                    server={server} 
                    bgGradient={bgGradient} 
                    inviteUrl={getInviteUrl(server.id)} 
                  />
                )}
              </AnimatedSection>
            )
          })}
        </div>

        {filteredServers.length === 0 && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex-1 flex flex-col items-center justify-center py-20 text-center"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-white/5 rounded-full blur-2xl transform scale-150" />
              <div className="w-24 h-24 bg-discord-dark/50 backdrop-blur-md border border-white/10 rounded-full flex items-center justify-center mb-8 relative z-10 shadow-xl">
                <Search className="w-10 h-10 text-white/30" />
              </div>
            </div>
            <h3 className="text-3xl font-black text-white mb-4 tracking-tight">서버를 찾을 수 없습니다</h3>
            <p className="text-discord-muted/80 text-lg max-w-md mx-auto">
              검색어와 일치하는 서버가 없거나 접속 가능한 관리자 권한의 서버가 존재하지 않습니다.
            </p>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  )
}
