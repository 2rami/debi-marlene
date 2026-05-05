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
  useMotionValue,
  useScroll,
  useSpring,
  useTransform,
  animate as fmAnimate,
} from 'framer-motion'
import { Send, X, Loader2 } from 'lucide-react'
import { FONT_BODY, FONT_DISPLAY } from './colors'
import { useCharacterDock } from './dockContext'

const DEFAULT_HASH =
  'MDJEJPMDEMDJHNEBBNNMJECMFOIONCHJIBOCJJPBFCKNKIGKBBENDHPPFHLIDKILPPFEBOKAIFAAKEJLHEFKOHJLCMDDILIMKIMBGIMEHGCPBKLEPJLPEDJJNJJCAGDEJHMAAOGLLFGLBMMHDNCPPFLPPCPACKODADBBKKEGDIGMKDHJALDIDBOBMGMPMKNJMJNENGMFMPONCFMLNIDJMFAHPNKMBCPEILEMDIDFDFBHNAPPHMPEKIMKNCJAOOIB'

const NEXON_LOOK_BASE = 'https://open.api.nexon.com/static/maplestory/character/look'

const PROMPT_MAX_LEN = 500

type MotionState =
  | 'idle' | 'thinking' | 'talk' | 'drag' | 'grab'
  | 'walk1' | 'walk2'
  | 'jump' | 'attack1' | 'attack2' | 'attack3' | 'attack4' | 'attackF'

const POSE: Record<MotionState, { wmotion: string; emotion: string; action: string }> = {
  idle: { wmotion: 'W00', emotion: 'E00', action: 'A00' },
  thinking: { wmotion: 'W02', emotion: 'E03', action: 'A01' },
  talk: { wmotion: 'W04', emotion: 'E01', action: 'A06' },
  drag: { wmotion: 'W04', emotion: 'E02', action: 'A05' }, // 점프(Fly)
  grab: { wmotion: 'W04', emotion: 'E20', action: 'A06' }, // 마우스로 잡힘
  walk1: { wmotion: 'W01', emotion: 'E00', action: 'A02' },
  walk2: { wmotion: 'W01', emotion: 'E00', action: 'A03' },
  jump: { wmotion: 'W02', emotion: 'E07', action: 'A06' }, // Alt 점프
  // 공격 5프레임 — frame 분리 활용 (A20.0~2 = 들기→휘두름, A22.2 = 광채, A23.0 = 잔상)
  attack1: { wmotion: 'W02', emotion: 'E04', action: 'A20.0' },
  attack2: { wmotion: 'W02', emotion: 'E04', action: 'A20.1' },
  attack3: { wmotion: 'W02', emotion: 'E04', action: 'A20.2' },
  attack4: { wmotion: 'W02', emotion: 'E04', action: 'A22.2' },
  attackF: { wmotion: 'W02', emotion: 'E04', action: 'A23.0' },
}

const ATTACK_SEQUENCE: MotionState[] = ['attack1', 'attack2', 'attack3', 'attack4', 'attackF']
const ATTACK_FRAME_MS = 100

const JUMP_HEIGHT = 90 // 위로 점프 픽셀
const JUMP_DURATION_MS = 600

// walk cycle: walk1.0~3 4프레임. walk2 는 팔 자세가 walk1 과 달라서 cycle 끊김 보임 → walk1 만 사용.
type WalkStep = { state: 'walk1' | 'walk2'; frame: number }
const WALK_CYCLE: WalkStep[] = [
  { state: 'walk1', frame: 0 },
  { state: 'walk1', frame: 1 },
  { state: 'walk1', frame: 2 },
  { state: 'walk1', frame: 3 },
]
const WALK_FRAME_MS = 130

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

function buildLookUrl(hash: string, state: MotionState, frame?: number) {
  const p = POSE[state]
  const action = frame != null ? `${p.action}.${frame}` : p.action
  return `${NEXON_LOOK_BASE}/${hash}?wmotion=${p.wmotion}&emotion=${p.emotion}&action=${action}`
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
  const [walkFrame, setWalkFrame] = useState(0) // 0~3, walk1/walk2 각각 4프레임
  const [facingRight, setFacingRight] = useState(false)
  const [isWalking, setIsWalking] = useState(false)
  const [bubbleText, setBubbleText] = useState('← → 로 움직여요!\nALT 점프 · CTRL 공격 🎮')
  const keyboardHintRef = useRef(true)
  const [hasDragged, setHasDragged] = useState(false)

  // 도킹 — 특정 섹션 슬롯에 캐릭터 고정 (bubble useEffect 가 일찍 참조하니 위로)
  const { dockEl } = useCharacterDock()

  const sessionRef = useRef<string | null>(
    typeof window !== 'undefined' ? localStorage.getItem(SESSION_KEY) : null
  )
  const listRef = useRef<HTMLDivElement>(null)

  // 모든 모션 URL preload — walk cycle 8프레임 + 다른 모션 4종 모두
  useEffect(() => {
    if (typeof window === 'undefined') return
    const staticStates: MotionState[] = [
      'idle', 'thinking', 'talk', 'drag', 'grab',
      'jump', 'attack1', 'attack2', 'attack3', 'attack4', 'attackF',
    ]
    staticStates.forEach((s) => {
      const img = new Image()
      img.src = buildLookUrl(hash, s)
    })
    WALK_CYCLE.forEach(({ state, frame }) => {
      const img = new Image()
      img.src = buildLookUrl(hash, state, frame)
    })
  }, [hash])

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

    return () => {
      window.removeEventListener('resize', onResize)
      mq.removeEventListener('change', onMq)
    }
  }, [])

  const { scrollYProgress } = useScroll()

  // 첫 5초간 키보드 안내 우선 표시 — 그 후 scroll progress 기반
  useEffect(() => {
    const t = window.setTimeout(() => {
      keyboardHintRef.current = false
      // 5초 후 진행도 따라 즉시 전환
      const v = scrollYProgress.get()
      if (v < 0.1) setBubbleText('아래로 스크롤 해보세요! 👇')
    }, 5000)
    return () => window.clearTimeout(t)
  }, [scrollYProgress])

  useEffect(() => {
    return scrollYProgress.onChange((v) => {
      if (keyboardHintRef.current) return // 안내 표시 중엔 덮어쓰지 않음
      if (dockEl) return // 도킹 중엔 dock 전용 버블 유지
      if (v < 0.1) {
        setBubbleText('아래로 스크롤 해보세요! 👇')
      } else if (v >= 0.1 && v < 0.3) {
        setBubbleText('저는 데비&마를렌을 9개월째\n1인 운영 중인 양건호입니다! 😎')
      } else if (v >= 0.3 && v < 0.6) {
        setBubbleText('넥슨의 JD와 제가\n어떻게 매칭되는지 볼까요? 🎯')
      } else {
        setBubbleText('저에게 궁금한 점을\n물어보세요! 💬')
      }
    })
  }, [scrollYProgress, dockEl])

  const controls = useAnimationControls()
  const firstRunRef = useRef(true)
  const currentXRef = useRef(viewport.w - MARGIN - CHAR_SIZE)
  const lastDragPosRef = useRef<{ x: number; y: number } | null>(null)
  const charDivRef = useRef<HTMLDivElement>(null)
  // 챗 헤더 캐릭터 Y motion value — base 60 (80은 발 잘림, 40은 너무 위), jump 시 위로 spring
  const HEADER_BASE_Y = 60
  const HEADER_JUMP_Y = -30
  const headerY = useMotionValue(120)
  // 챗 헤더 캐릭터 X motion value — base 0, ←→ 키로 좌우 이동
  const headerX = useMotionValue(0)
  const HEADER_HALF_RANGE = 70 // 헤더 폭 (PANEL_W=380) - 캐릭터 폭(240) 의 절반

  // 챗 열릴 때 등장 애니메이션 (120 → 40) — 닫힐 땐 다음 mount 위해 reset
  useEffect(() => {
    if (open) {
      fmAnimate(headerY, HEADER_BASE_Y, { type: 'spring', bounce: 0.4, delay: 0.1 })
    } else {
      headerY.set(120)
      headerX.set(0)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  // 테두리 걷기 로직 (bottom edge) — 도킹 중엔 정지
  useEffect(() => {
    if (open || isDragging || reduced || dockEl) return;

    let cancelled = false;
    
    async function roam() {
      if (firstRunRef.current) {
        const initX = viewport.w - MARGIN - CHAR_SIZE;
        const initY = viewport.h - MARGIN - CHAR_SIZE;
        controls.set({ x: initX, y: initY, scale: 1, opacity: 1 });
        currentXRef.current = initX;
        firstRunRef.current = false;
      } else if (hasDragged || lastDragPosRef.current) {
        // 사용자가 드래그했거나 도킹에서 빠져나온 상태 — 위치 유지, scale만 1로 부드럽게 복귀.
        await controls.start(
          { scale: 1, opacity: 1 },
          { duration: 0.3, ease: [0.22, 1, 0.36, 1] },
        )
        if (cancelled) return;
        // currentXRef 는 마지막 dock x 그대로 — 다음 random walk 가 거기서 시작
        setMotionState('idle');
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

        // 사용자가 드래그해서 화면에 버려둔 상태면 안 움직임
        if (hasDragged) {
          await new Promise(r => setTimeout(r, 1000));
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
  }, [open, isDragging, reduced, viewport.w, viewport.h, controls, hasDragged, dockEl])

  // 도킹 — dockEl 이 set 되면 매 프레임 lerp 로 slot 위치 따라잡음 (discrete animation 없음)
  const DOCK_SCALE = 1.7
  useEffect(() => {
    if (!dockEl || open || isDragging) return

    let cancelled = false
    let raf = 0

    const getTarget = () => {
      const rect = dockEl.getBoundingClientRect()
      const rawX = rect.left + (rect.width - CHAR_SIZE) / 2
      const rawY = rect.top + (rect.height - CHAR_SIZE) / 2 + 60
      return {
        x: Math.max(MARGIN, Math.min(viewport.w - MARGIN - CHAR_SIZE, rawX)),
        y: Math.max(MARGIN, Math.min(viewport.h - MARGIN - CHAR_SIZE, rawY)),
      }
    }

    setIsWalking(false)
    setMotionState('idle')
    setFacingRight(false)
    setBubbleText('저의 메이플\n경력입니다!')

    // 시작 위치 — 현재 캐릭터 위치 (controls 에 직접 조회 어려워 ref 추정)
    let curX = currentXRef.current
    let curY = lastDragPosRef.current?.y ?? viewport.h - MARGIN - CHAR_SIZE
    let curScale = 1

    // 매 프레임 16% 비율로 따라잡음 — 부드럽고 빠른 spring 느낌
    const SPEED = 0.16
    const tick = () => {
      if (cancelled) return
      const t = getTarget()
      curX += (t.x - curX) * SPEED
      curY += (t.y - curY) * SPEED
      curScale += (DOCK_SCALE - curScale) * SPEED
      controls.set({ x: curX, y: curY, scale: curScale, opacity: 1 })
      currentXRef.current = curX
      lastDragPosRef.current = { x: curX, y: curY }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)

    return () => {
      cancelled = true
      cancelAnimationFrame(raf)
      // 언도킹 — lastDragPosRef 가 마지막 위치로 세팅돼있어 roam 의 resume 분기 진입.
      // rAF tick 에서 Y clamp 했으니 viewport 안 안전 영역. 위치 그대로 두고 scale 만 1로 복귀.
    }
  }, [dockEl, open, isDragging, controls, viewport.w, viewport.h])

  // 걷기 모션: walk1.0 → walk1.3 4프레임 cycle (walk2 는 팔 끊김으로 제외)
  useEffect(() => {
    if (!isWalking || isDragging) return;

    let i = 0;
    const apply = (idx: number) => {
      const step = WALK_CYCLE[idx];
      setMotionState(step.state);
      setWalkFrame(step.frame);
    };
    apply(0);
    const interval = setInterval(() => {
      i = (i + 1) % WALK_CYCLE.length;
      apply(i);
    }, WALK_FRAME_MS);

    return () => {
      clearInterval(interval);
      setMotionState('idle');
      setWalkFrame(0);
    }
  }, [isWalking, isDragging]);

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

  // 키보드 조작: ←→ 좌우 이동 / Alt(Option) 점프 / Ctrl 공격
  useEffect(() => {
    if (reduced) return

    const isInputFocused = () => {
      const el = document.activeElement as HTMLElement | null
      if (!el) return false
      return (
        el.tagName === 'INPUT' ||
        el.tagName === 'TEXTAREA' ||
        el.isContentEditable
      )
    }

    const heldKeys = new Set<string>()
    let attackTimer: number | null = null
    let moveTimer: number | null = null
    let busyAttack = false

    const stopAttack = () => {
      if (attackTimer) {
        window.clearInterval(attackTimer)
        attackTimer = null
      }
      busyAttack = false
    }

    const startAttack = () => {
      if (busyAttack) return
      busyAttack = true
      let i = 0
      setMotionState(ATTACK_SEQUENCE[0])
      attackTimer = window.setInterval(() => {
        i++
        if (i >= ATTACK_SEQUENCE.length) {
          stopAttack()
          setMotionState('idle')
          return
        }
        setMotionState(ATTACK_SEQUENCE[i])
      }, ATTACK_FRAME_MS)
    }

    const stepMove = () => {
      const left = heldKeys.has('ArrowLeft')
      const right = heldKeys.has('ArrowRight')
      if (!left && !right) {
        if (moveTimer) {
          window.clearInterval(moveTimer)
          moveTimer = null
        }
        setIsWalking(false)
        return
      }
      const dir = right ? 1 : -1
      if (open) {
        // 챗 헤더 안 좌우 이동
        const cur = headerX.get()
        const next = Math.max(-HEADER_HALF_RANGE, Math.min(HEADER_HALF_RANGE, cur + dir * 4))
        headerX.set(next)
      } else {
        // 떠다니는 캐릭터 위치 이동
        const minX = MARGIN
        const maxX = viewport.w - MARGIN - CHAR_SIZE
        const next = Math.max(minX, Math.min(maxX, currentXRef.current + dir * 6))
        currentXRef.current = next
        const y = lastDragPosRef.current?.y ?? viewport.h - MARGIN - CHAR_SIZE
        controls.set({ x: next, y, scale: 1, opacity: 1 })
        lastDragPosRef.current = { x: next, y }
      }
    }

    const isAttackKey = (code: string) =>
      code === 'ControlLeft' || code === 'ControlRight' ||
      code === 'MetaLeft' || code === 'MetaRight' ||
      code === 'KeyZ'
    const isJumpKey = (code: string) =>
      code === 'AltLeft' || code === 'AltRight' || code === 'Space' || code === 'KeyX'

    const doJump = () => {
      setMotionState('jump')
      if (open) {
        // 챗 헤더 캐릭터 점프 — headerY 위로 → 아래로
        fmAnimate(headerY, HEADER_JUMP_Y, { duration: JUMP_DURATION_MS / 2 / 1000, ease: 'easeOut' })
          .then(() =>
            fmAnimate(headerY, HEADER_BASE_Y, { duration: JUMP_DURATION_MS / 2 / 1000, ease: 'easeIn' })
          )
      } else {
        // 떠다니는 캐릭터 점프 — 위치 spring up/down
        const baseY = lastDragPosRef.current?.y ?? viewport.h - MARGIN - CHAR_SIZE
        const x = currentXRef.current
        controls
          .start({ y: baseY - JUMP_HEIGHT }, { duration: JUMP_DURATION_MS / 2 / 1000, ease: 'easeOut' })
          .then(() =>
            controls.start({ y: baseY }, { duration: JUMP_DURATION_MS / 2 / 1000, ease: 'easeIn' })
          )
        lastDragPosRef.current = { x, y: baseY }
      }
      window.setTimeout(() => {
        if (!busyAttack) setMotionState('idle')
      }, JUMP_DURATION_MS)
    }

    const onKeyDown = (e: globalThis.KeyboardEvent) => {
      if (isInputFocused()) return
      if (heldKeys.has(e.code)) return
      heldKeys.add(e.code)

      // 키 한 번 누르면 키보드 안내 즉시 끄기
      if (keyboardHintRef.current) {
        keyboardHintRef.current = false
        const v = scrollYProgress.get()
        if (v < 0.1) setBubbleText('아래로 스크롤 해보세요! 👇')
      }

      if (e.code === 'ArrowLeft' || e.code === 'ArrowRight') {
        e.preventDefault()
        if (busyAttack) return
        const right = e.code === 'ArrowRight'
        setFacingRight(right)
        if (!open) {
          // idle roam 정지 + 키보드 직접 제어
          setHasDragged(true)
        }
        setIsWalking(true)
        if (!moveTimer) {
          stepMove()
          moveTimer = window.setInterval(stepMove, 24)
        }
      } else if (isJumpKey(e.code)) {
        e.preventDefault()
        if (busyAttack) return
        doJump()
      } else if (isAttackKey(e.code)) {
        e.preventDefault()
        startAttack()
      }
    }

    const onKeyUp = (e: globalThis.KeyboardEvent) => {
      heldKeys.delete(e.code)
      if (e.code === 'ArrowLeft' || e.code === 'ArrowRight') {
        if (!heldKeys.has('ArrowLeft') && !heldKeys.has('ArrowRight')) {
          if (moveTimer) {
            window.clearInterval(moveTimer)
            moveTimer = null
          }
          setIsWalking(false)
        }
      }
    }

    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
      if (attackTimer) window.clearInterval(attackTimer)
      if (moveTimer) window.clearInterval(moveTimer)
    }
  }, [open, reduced, viewport.w, viewport.h, controls])

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
    // flip 은 instant — facing 변경 시 회전 없이 바로 바뀜
  }

  return (
    <>
      <AnimatePresence>
        {!open && (
          <motion.div
            ref={charDivRef}
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
            dragMomentum={false}
            onDragStart={() => {
              setIsDragging(true)
              setMotionState('grab')
            }}
            onDragEnd={() => {
              // ref 통해 실제 화면 위 위치 직접 읽기 (info.point 는 cursor 좌표라 부정확)
              // charWrap 이 position:fixed top:0 left:0 이라 rect.left/top 이 motion.div transform x/y.
              const el = charDivRef.current
              if (el) {
                const rect = el.getBoundingClientRect()
                currentXRef.current = rect.left
                lastDragPosRef.current = { x: rect.left, y: rect.top }
              }
              setTimeout(() => {
                setIsDragging(false)
                setMotionState('idle')
                setHasDragged(true)
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
                  src={
                    isWalking && (motionState === 'walk1' || motionState === 'walk2')
                      ? buildLookUrl(hash, motionState, walkFrame)
                      : buildLookUrl(hash, motionState)
                  }
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
                onClick={() => {
                  // 챗 닫으면 캐릭터를 우측하단으로 (drag 위치 reset)
                  setHasDragged(false)
                  lastDragPosRef.current = null
                  setOpen(false)
                }}
                className="absolute top-4 right-4 z-20 w-8 h-8 flex items-center justify-center bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors"
              >
                <X size={18} />
              </button>
              
              <div className="absolute top-4 left-5 z-20">
                <span className="bg-white/20 backdrop-blur-md border border-white/20 text-white text-[12px] font-bold px-3 py-1.5 rounded-full" style={{ fontFamily: FONT_DISPLAY }}>
                  가상 면접자 양건호
                </span>
              </div>
              
              {/* 캐릭터 상반신 — walk frame cycle 적용, ←→ 시 headerX 이동 + facing, 점프 시 headerY spring */}
              <motion.img
                src={
                  isWalking && (motionState === 'walk1' || motionState === 'walk2')
                    ? buildLookUrl(hash, motionState, walkFrame)
                    : buildLookUrl(hash, motionState)
                }
                alt="AI Interviewer"
                className="relative z-10"
                style={{
                  width: 240,
                  height: 240,
                  objectFit: 'contain',
                  objectPosition: 'center bottom',
                  scaleX: facingRight ? -1.2 : 1.2,
                  scaleY: 1.2,
                  x: headerX,
                  y: headerY,
                  imageRendering: 'pixelated',
                }}
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
