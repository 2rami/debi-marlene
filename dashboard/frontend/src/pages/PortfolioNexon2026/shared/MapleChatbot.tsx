import {
  CSSProperties,
  KeyboardEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react'
import {
  AnimatePresence,
  motion,
  useAnimationControls,
  useScroll,
  useSpring,
  useTransform,
} from 'framer-motion'
import { Send, X, Loader2 } from 'lucide-react'
import { FONT_BODY, FONT_DISPLAY } from './colors'

const DEFAULT_HASH =
  'MDJEJPMDEMDJHNEBBNNMJECMFOIONCHJIBOCJJPBFCKNKIGKBBENDHPPFHLIDKILPPFEBOKAIFAAKEJLHEFKOHJLCMDDILIMKIMBGIMEHGCPBKLEPJLPEDJJNJJCAGDEJHMAAOGLLFGLBMMHDNCPPFLPPCPACKODADBBKKEGDIGMKDHJALDIDBOBMGMPMKNJMJNENGMFMPONCFMLNIDJMFAHPNKMBCPEILEMDIDFDFBHNAPPHMPEKIMKNCJAOOIB'

const NEXON_LOOK_BASE = 'https://open.api.nexon.com/static/maplestory/character/look'

const PROMPT_MAX_LEN = 500

type MotionState = 'idle' | 'thinking' | 'talk' | 'drag' | 'walk1' | 'walk2'

const POSE: Record<MotionState, { wmotion: string; emotion: string; action: string }> = {
  idle: { wmotion: 'W00', emotion: 'E00', action: 'A00' },
  thinking: { wmotion: 'W02', emotion: 'E03', action: 'A01' },
  talk: { wmotion: 'W04', emotion: 'E01', action: 'A06' },
  drag: { wmotion: 'W04', emotion: 'E02', action: 'A05' }, // 점프 모션 (A05)
  walk1: { wmotion: 'W01', emotion: 'E00', action: 'A02' }, // 걷기 프레임 1
  walk2: { wmotion: 'W01', emotion: 'E00', action: 'A03' }, // 걷기 프레임 2
}

const MOTION_STATES: MotionState[] = ['idle', 'thinking', 'talk']

const CHAR_SIZE = 180
const CHAR_IMG_SCALE = 1.6
const MARGIN = 32
const PANEL_W = 380
const PANEL_H = 600
const PANEL_RIGHT = 32
const PANEL_BOTTOM = 32

type ChatRole = 'user' | 'agent'
interface ChatMsg {
  id: string
  role: ChatRole
  text: string
}

const PROMPT_CHIPS = [
  '양건호는 어떤 사람?',
  '메이플 어디까지 했어?',
  '봇 9개월 운영, 어땠어?',
  'NEXON 왜 지원해?',
  'JD 매칭은?',
] as const

const API_BASE =
  (import.meta as any).env?.VITE_API_BASE ?? 'http://localhost:8081'

const SESSION_KEY = 'nexon-portfolio-chatbot-session'

function buildLookUrl(hash: string, state: MotionState) {
  const p = POSE[state]
  return `${NEXON_LOOK_BASE}/${hash}?wmotion=${p.wmotion}&emotion=${p.emotion}&action=${p.action}`
}

function fakeReply(prompt: string): string {
  if (prompt.includes('어떤 사람'))
    return '저는 메이플스토리 16년 차 헤비 게이머이자, Discord LLM 봇 데비&마를렌을 9개월간 158개 서버에 1인 운영 중인 개발자 양건호입니다. ✨'
  if (prompt.includes('메이플'))
    return '오로라 서버 프로즌샤 · 아크메이지(썬콜) · Lv.284 · 하드 세렌 파티 격파까지 직접 경험했습니다.'
  if (prompt.includes('봇'))
    return 'LangGraph 2-tier + Anthropic Managed Agents + 패치노트 RAG + 음성 파이프라인을 한 봇에 통합해 운영하고 있습니다. 매일 라이브로 LLM 응답을 정량/정성 검증 중입니다.'
  if (prompt.includes('NEXON'))
    return '게임 도메인 16년 사용자 시점과 라이브 LLM 운영 검증 감각이 같이 필요한 자리, 그게 바로 LLM 평가 어시스턴트라고 생각합니다.'
  if (prompt.includes('JD') || prompt.includes('매칭'))
    return '벤치마크 / 평가지표 / 응답품질 평가 / 결과 보고 4가지 업무에 1:1로 매칭됩니다. 페이지 04 섹션을 참고해 주세요.'
  return '잠시 응답이 지연되고 있습니다. 곧 정상화될 예정이니 다시 한 번 질문해 주세요.'
}

export default function MapleChatbot({
  hash = DEFAULT_HASH,
}: {
  hash?: string
}) {
  const [open, setOpen] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [msgs, setMsgs] = useState<ChatMsg[]>([
    {
      id: 'init',
      role: 'agent',
      text: '안녕하세요! 저는 디지털 클론 양건호입니다. 저에 대해 궁금한 점이 있으신가요?',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [motionState, setMotionState] = useState<MotionState>('idle')
  const [facingRight, setFacingRight] = useState(false)
  const [isWalking, setIsWalking] = useState(false)
  const [bubbleText, setBubbleText] = useState('아래로 스크롤 해보세요! 👇')
  const [paintingMode, setPaintingMode] = useState(false)
  const paintingRect = useRef<DOMRect | null>(null)

  const sessionRef = useRef<string | null>(
    typeof window !== 'undefined' ? localStorage.getItem(SESSION_KEY) : null
  )
  const listRef = useRef<HTMLDivElement>(null)

  const [viewport, setViewport] = useState(() =>
    typeof window !== 'undefined'
      ? { w: window.innerWidth, h: window.innerHeight }
      : { w: 1280, h: 800 }
  )
  const [reduced, setReduced] = useState(false)

  // 이미지 프리로드 (깜빡임 방지)
  useEffect(() => {
    const states: MotionState[] = ['walk1', 'walk2', 'drag', 'idle', 'thinking', 'talk']
    states.forEach(state => {
      const img = new Image()
      img.src = buildLookUrl(hash, state)
    })
  }, [hash])

  useEffect(() => {
    function onResize() {
      setViewport({ w: window.innerWidth, h: window.innerHeight })
    }
    window.addEventListener('resize', onResize)
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReduced(mq.matches)
    function onMq(e: MediaQueryListEvent) {
      setReduced(e.matches)
    }
    mq.addEventListener('change', onMq)
    
    // 전우치 모드 옵저버
    const interval = setInterval(() => {
      const el = document.getElementById('character-painting')
      if (el) {
        const rect = el.getBoundingClientRect()
        // 그림이 화면의 중앙 부근에 들어왔는지 체크 (약 화면 20% ~ 80% 사이)
        if (rect.top > window.innerHeight * 0.1 && rect.bottom < window.innerHeight * 0.9) {
          paintingRect.current = rect
          setPaintingMode(true)
        } else {
          setPaintingMode(false)
        }
      }
    }, 200)

    return () => {
      window.removeEventListener('resize', onResize)
      mq.removeEventListener('change', onMq)
      clearInterval(interval)
    }
  }, [])

  const { scrollYProgress } = useScroll()

  useEffect(() => {
    return scrollYProgress.onChange((v) => {
      if (v < 0.1) {
        setBubbleText('아래로 스크롤 해보세요! 👇')
      } else if (v >= 0.1 && v < 0.3) {
        setBubbleText('저는 데비&마를렌을 9개월째\n1인 운영 중인 양건호입니다! 😎')
      } else if (v >= 0.3 && v < 0.6) {
        setBubbleText('넥슨의 JD와 제가\n어떻게 매칭되는지 볼까요? 🎯')
      } else if (v >= 0.6 && v < 0.8) {
        setBubbleText('저 그림 속으로 들어갑니다!!\n얍!! 전우치!! 🏃‍♂️💨')
      } else {
        setBubbleText('저에게 궁금한 점을\n물어보세요! 💬')
      }
    })
  }, [scrollYProgress])

  const controls = useAnimationControls()
  const firstRunRef = useRef(true)
  const currentXRef = useRef(viewport.w - MARGIN - CHAR_SIZE)

  // 테두리 걷기 로직 (bottom edge)
  useEffect(() => {
    if (open || isDragging || reduced) return;
    
    let cancelled = false;
    
    async function roam() {
      if (firstRunRef.current) {
        const initX = viewport.w - MARGIN - CHAR_SIZE;
        const initY = viewport.h - MARGIN - CHAR_SIZE;
        controls.set({ x: initX, y: initY, scale: 1, opacity: 1 });
        currentXRef.current = initX;
        firstRunRef.current = false;
      } else {
        // 채팅창에서 튀어나오는 팝업 아웃 애니메이션
        const chatX = viewport.w - PANEL_RIGHT - PANEL_W / 2 - CHAR_SIZE / 2;
        const chatY = viewport.h - PANEL_BOTTOM - PANEL_H + 50;
        const targetX = viewport.w - MARGIN - CHAR_SIZE;
        const targetY = viewport.h - MARGIN - CHAR_SIZE;

        controls.set({ x: chatX, y: chatY, scale: 0.3, opacity: 1 });
        setMotionState('drag'); // 튀어나올 때 점프(만세) 포즈
        
        await controls.start(
          { x: targetX, y: targetY, scale: 1 },
          { type: 'spring', stiffness: 90, damping: 14, mass: 1 }
        );
        
        if (cancelled) return;
        setMotionState('idle');
        currentXRef.current = targetX;
      }
      
      while (!cancelled) {
        // 4~8초 대기
        const dwell = 4000 + Math.random() * 4000;
        await new Promise(r => setTimeout(r, dwell));
        if (cancelled) break;
        
        // 전우치 모드: 그림으로 빨려들어감
        if (paintingMode && paintingRect.current) {
          const rect = paintingRect.current;
          const targetX = rect.left + rect.width / 2 - CHAR_SIZE / 2;
          const targetY = rect.top + rect.height / 2 - CHAR_SIZE / 2;
          
          setMotionState('drag');
          await controls.start(
            { x: targetX, y: targetY, scale: 0, opacity: 0, rotate: 720 },
            { duration: 1.2, ease: 'easeInOut' }
          );
          
          // 그림 안에 들어간 상태로 대기하면서 위치 동기화
          while (paintingMode && !cancelled) {
            const el = document.getElementById('character-painting');
            if (el) {
               const r = el.getBoundingClientRect();
               controls.set({ 
                 x: r.left + r.width / 2 - CHAR_SIZE / 2, 
                 y: r.top + r.height / 2 - CHAR_SIZE / 2 
               });
            }
            await new Promise(r => setTimeout(r, 100));
          }
          
          if (cancelled) break;
          
          // 다시 튀어나옴
          setMotionState('drag');
          await controls.start(
            { x: viewport.w - MARGIN - CHAR_SIZE, y: viewport.h - MARGIN - CHAR_SIZE, scale: 1, opacity: 1, rotate: 0 },
            { type: 'spring', stiffness: 70, damping: 14 }
          );
          setMotionState('idle');
          currentXRef.current = viewport.w - MARGIN - CHAR_SIZE;
          continue;
        }

        // 새 목적지 (bottom edge의 랜덤 X좌표)
        const minX = MARGIN;
        const maxX = viewport.w - MARGIN - CHAR_SIZE;
        // 최소 100px 이상 움직이도록
        let targetX = minX + Math.random() * (maxX - minX);
        if (Math.abs(targetX - currentXRef.current) < 100) {
          targetX = currentXRef.current > viewport.w / 2 ? minX : maxX;
        }
        
        const isGoingRight = targetX > currentXRef.current;
        setFacingRight(isGoingRight);
        setIsWalking(true);
        
        // 이동 거리 비례해서 시간 계산 (속도: 40px per second)
        const distance = Math.abs(targetX - currentXRef.current);
        const duration = distance / 40;
        
        await controls.start(
          { x: targetX, y: viewport.h - MARGIN - CHAR_SIZE },
          { duration: duration, ease: 'linear' }
        );
        
        currentXRef.current = targetX;
        setIsWalking(false);
      }
    }
    
    roam();
    
    return () => {
      cancelled = true;
      setIsWalking(false);
    }
  }, [open, isDragging, reduced, viewport.w, viewport.h, controls])

  // 걷기 모션 프레임 교체 (W01, W02 번갈아가며)
  useEffect(() => {
    if (!isWalking || open || isDragging) return;
    
    let frame = 1;
    const interval = setInterval(() => {
      setMotionState(frame === 1 ? 'walk1' : 'walk2');
      frame = frame === 1 ? 2 : 1;
    }, 250);
    
    return () => {
      clearInterval(interval);
      setMotionState('idle');
    }
  }, [isWalking, open, isDragging]);

  // 대기 중 랜덤 모션 (idle, thinking, talk)
  useEffect(() => {
    if (open || isDragging || isWalking || reduced) return
    const id = window.setInterval(() => {
      setMotionState((prev) => {
        const choices = MOTION_STATES.filter((s) => s !== prev)
        return choices[Math.floor(Math.random() * choices.length)]
      })
    }, 4000)
    return () => window.clearInterval(id)
  }, [open, isDragging, isWalking, reduced])

  const { scrollY } = useScroll()
  const bobRaw = useTransform(scrollY, (v) => Math.sin(v / 240) * 4)
  const bob = useSpring(bobRaw, { stiffness: 60, damping: 14, mass: 0.4 })

  useEffect(() => {
    if (!listRef.current) return
    listRef.current.scrollTop = listRef.current.scrollHeight
  }, [msgs, loading])

  const send = useCallback(
    async (text: string) => {
      const prompt = text.trim()
      if (!prompt || loading) return

      if (prompt.length > PROMPT_MAX_LEN) {
        setMsgs((m) => [
          ...m,
          {
            id: `a-${Date.now()}`,
            role: 'agent',
            text: `질문은 ${PROMPT_MAX_LEN}자 이내로 부탁해 (지금 ${prompt.length}자).`,
          },
        ])
        return
      }

      const userMsg: ChatMsg = {
        id: `u-${Date.now()}`,
        role: 'user',
        text: prompt,
      }
      setMsgs((m) => [...m, userMsg])
      setInput('')
      setLoading(true)
      setMotionState('thinking')

      const talkSwap = window.setTimeout(() => setMotionState('talk'), 350)

      function pushAgent(t: string) {
        setMsgs((m) => [
          ...m,
          { id: `a-${Date.now()}`, role: 'agent', text: t },
        ])
      }

      try {
        const res = await fetch(`${API_BASE}/api/portfolio/ask`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt,
            session_id: sessionRef.current,
          }),
        })

        let body: any = null
        try {
          body = await res.json()
        } catch {
        }

        if (res.ok) {
          if (body?.session_id && body.session_id !== sessionRef.current) {
            sessionRef.current = body.session_id
            try {
              localStorage.setItem(SESSION_KEY, body.session_id)
            } catch {}
          }
          pushAgent(body?.text ?? body?.answer ?? fakeReply(prompt))
          return
        }

        const code = body?.error as string | undefined
        switch (res.status) {
          case 400:
            if (code === 'prompt_too_long') {
              pushAgent(`질문이 다소 깁니다. ${PROMPT_MAX_LEN}자 이내로 다시 입력해 주세요.`)
            } else {
              pushAgent('질문을 다시 한 번 입력해 주세요.')
            }
            return
          case 429:
            pushAgent('잠시 후 다시 물어봐주세요.')
            return
          case 502:
            pushAgent('잠깐만요... 다시 시도해주세요.')
            return
          case 503:
            pushAgent(fakeReply(prompt))
            return
          case 504:
            pushAgent('답변이 다소 지연되고 있습니다. 잠시 후 다시 질문해 주세요.')
            return
          default:
            pushAgent('잠깐만요... 다시 시도해주세요.')
            return
        }
      } catch {
        pushAgent(fakeReply(prompt))
      } finally {
        window.clearTimeout(talkSwap)
        setLoading(false)
        setMotionState('idle')
      }
    },
    [loading]
  )

  function onKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  const charWrap: CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    width: CHAR_SIZE,
    height: CHAR_SIZE,
    zIndex: 9999,
    fontFamily: FONT_BODY,
    pointerEvents: 'none',
  }

  const charBtn: CSSProperties = {
    width: CHAR_SIZE,
    height: CHAR_SIZE,
    background: 'transparent',
    border: 'none',
    padding: 0,
    cursor: 'pointer',
    pointerEvents: 'auto',
    position: 'relative',
    outline: 'none',
  }

  const charImg: CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit: 'contain',
    imageRendering: 'pixelated',
    transform: `scaleX(${facingRight ? -CHAR_IMG_SCALE : CHAR_IMG_SCALE}) scaleY(${CHAR_IMG_SCALE}) translateY(${isDragging ? -5 : 0}px)`,
    transformOrigin: 'center bottom',
    filter: 'drop-shadow(0 6px 14px rgba(10,18,36,0.3))',
    pointerEvents: 'none',
    transition: 'transform 0.15s ease-out'
  }

  return (
    <>
      <AnimatePresence>
        {!open && (
          <motion.div
            style={charWrap}
            initial={{ opacity: 0 }}
            animate={controls}
            exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.2 } }}
            onAnimationComplete={() => {
              if (firstRunRef.current === false && !open) {
                 controls.set({ opacity: 1 });
              }
            }}
            drag
            dragConstraints={{ left: MARGIN, top: MARGIN, right: viewport.w - MARGIN - CHAR_SIZE, bottom: viewport.h - MARGIN - CHAR_SIZE }}
            dragElastic={0.1}
            onDragStart={() => {
              setIsDragging(true)
              setMotionState('drag')
            }}
            onDragEnd={(_, info) => {
              setTimeout(() => {
                setIsDragging(false)
                setMotionState('idle')
                // 드래그가 끝난 x 위치를 기록하여 계속 그 위치에서부터 걷도록 설정
                currentXRef.current = info.point.x;
              }, 150)
            }}
          >
            <motion.div
              style={{
                width: '100%',
                height: '100%',
                y: bob,
                position: 'relative',
              }}
            >
              <button
                style={charBtn}
                onClick={(e) => {
                  if (isDragging) {
                    e.preventDefault();
                    return;
                  }
                  setOpen(true);
                }}
                aria-label="챗봇 열기"
              >
                <motion.div
                  animate={isWalking ? { y: [0, -6, 0] } : { y: [0, -3, 0] }}
                  transition={isWalking ? { duration: 0.5, repeat: Infinity } : { duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                  className="absolute bottom-full mb-4 left-1/2 -translate-x-1/2 bg-white text-[#0062DF] font-bold px-5 py-3 rounded-2xl shadow-[0_12px_40px_rgb(0,0,0,0.18)] border-[1.5px] border-[#0062DF] text-[15px] leading-snug whitespace-pre-wrap text-center min-w-[180px]"
                  style={{ fontFamily: FONT_DISPLAY }}
                >
                  {bubbleText}
                  <div className="absolute -bottom-2.5 left-1/2 -translate-x-1/2 border-[6px] border-transparent border-t-[#0062DF]" />
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 border-[5px] border-transparent border-t-white" />
                </motion.div>
                
                <motion.img
                  src={buildLookUrl(hash, motionState)}
                  alt="거노 캐릭터"
                  style={charImg}
                  draggable={false}
                  whileHover={!isDragging ? { scale: CHAR_IMG_SCALE * 1.05 } : {}}
                  onError={(e) => {
                    const t = e.currentTarget
                    const fallback = buildLookUrl(hash, 'idle')
                    if (t.src !== fallback) t.src = fallback
                  }}
                />
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {open && (
          <motion.div
            className="fixed z-[10000] bg-white rounded-3xl shadow-[0_24px_60px_rgba(10,18,36,0.15)] flex flex-col overflow-hidden border border-gray-100"
            style={{
              right: PANEL_RIGHT,
              bottom: PANEL_BOTTOM,
              width: PANEL_W,
              maxWidth: 'calc(100vw - 32px)',
              height: PANEL_H,
              maxHeight: 'calc(100vh - 64px)',
              fontFamily: FONT_BODY,
            }}
            initial={{ opacity: 0, scale: 0.9, y: 30, originX: 1, originY: 1 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', bounce: 0.25, duration: 0.5 }}
          >
            {/* Header with Character Upper Body */}
            <div className="relative bg-gradient-to-br from-[#0062DF] to-[#1E3A8A] h-36 flex-shrink-0 flex items-end justify-center overflow-hidden">
              <button 
                onClick={() => setOpen(false)}
                className="absolute top-4 right-4 z-20 w-8 h-8 flex items-center justify-center bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors"
              >
                <X size={18} />
              </button>
              
              <div className="absolute top-4 left-5 z-20">
                <span className="bg-white/20 backdrop-blur-md border border-white/20 text-white text-[12px] font-bold px-3 py-1.5 rounded-full" style={{ fontFamily: FONT_DISPLAY }}>
                  가상 면접자 양건호
                </span>
              </div>
              
              {/* 캐릭터 상반신 */}
              <motion.img 
                src={buildLookUrl(hash, motionState)}
                alt="AI Interviewer" 
                className="relative z-10"
                style={{
                  width: 240,
                  height: 240,
                  objectFit: 'contain',
                  objectPosition: 'center bottom',
                  transform: 'translateY(80px) scale(1.2)',
                  imageRendering: 'pixelated',
                }}
                initial={{ y: 120 }}
                animate={{ y: 80 }}
                transition={{ type: 'spring', delay: 0.1, bounce: 0.4 }}
              />
            </div>

            {/* Chat List */}
            <div ref={listRef} className="flex-1 overflow-y-auto p-5 bg-[#F7F9FC] flex flex-col gap-4">
              {msgs.map((m) => (
                <motion.div 
                  key={m.id}
                  initial={{ opacity: 0, y: 10, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div 
                    className={`max-w-[85%] px-4 py-3 text-[14px] leading-[1.6] shadow-sm whitespace-pre-wrap break-keep ${
                      m.role === 'user' 
                        ? 'bg-[#0062DF] text-white rounded-2xl rounded-tr-sm' 
                        : 'bg-white text-[#0A1224] rounded-2xl rounded-tl-sm border border-gray-100'
                    }`}
                  >
                    {m.text}
                  </div>
                </motion.div>
              ))}
              
              {loading && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm border border-gray-100 flex items-center gap-2 text-[#8A95A6]">
                    <Loader2 size={16} className="animate-spin text-[#0062DF]" />
                    <span className="text-[13.5px] font-medium">답변 작성 중...</span>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Chips (Suggestions) */}
            <AnimatePresence>
              {msgs.length === 1 && (
                <motion.div
                  className="bg-white border-t border-gray-100 px-4 py-3 flex flex-wrap gap-2"
                  initial={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0, padding: 0 }}
                >
                  {PROMPT_CHIPS.map((p) => (
                    <button
                      key={p}
                      onClick={() => send(p)}
                      disabled={loading}
                      className="text-[12px] font-bold text-[#0062DF] border border-[#0062DF]/30 bg-[#0062DF]/5 hover:bg-[#0062DF]/10 rounded-full px-3 py-1.5 transition-colors whitespace-nowrap"
                    >
                      {p}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-100">
              <div className="flex items-end gap-2 bg-[#F7F9FC] p-1.5 rounded-2xl border border-gray-200 focus-within:border-[#0062DF] transition-colors">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={onKey}
                  placeholder="양건호 지원자에 대해 물어보세요 (Enter 전송)"
                  className="flex-1 bg-transparent border-none outline-none px-3 py-2 text-[14px] text-[#0A1224] placeholder-[#8A95A6] resize-none max-h-[80px]"
                  rows={1}
                  disabled={loading}
                />
                <button
                  onClick={() => send(input)}
                  disabled={loading || !input.trim()}
                  className="w-10 h-10 shrink-0 rounded-xl bg-[#0062DF] text-white flex items-center justify-center disabled:opacity-50 transition-opacity mb-0.5"
                >
                  <Send size={18} className="ml-0.5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
