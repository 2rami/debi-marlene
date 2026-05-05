import { createContext, ReactNode, useCallback, useContext, useState } from 'react'

interface DockState {
  dockEl: HTMLElement | null
  setDockEl: (el: HTMLElement | null) => void
  /**
   * 같은 element 만 unset (다른 도커가 이미 자리 잡았으면 무시).
   * 언마운트/뷰포트 이탈 시 자기 슬롯만 해제하려고 사용.
   */
  releaseDockEl: (el: HTMLElement) => void
}

const Ctx = createContext<DockState>({
  dockEl: null,
  setDockEl: () => {},
  releaseDockEl: () => {},
})

/**
 * 떠다니는 캐릭터(MapleChatbot)를 특정 섹션 슬롯에 docking 하기 위한 컨텍스트.
 * 슬롯이 뷰포트에 들어오면 setDockEl(slotEl) → 캐릭터가 그 위치로 이동.
 */
export function CharacterDockProvider({ children }: { children: ReactNode }) {
  const [dockEl, setDockEl] = useState<HTMLElement | null>(null)
  const releaseDockEl = useCallback((el: HTMLElement) => {
    setDockEl((cur) => (cur === el ? null : cur))
  }, [])
  return <Ctx.Provider value={{ dockEl, setDockEl, releaseDockEl }}>{children}</Ctx.Provider>
}

export function useCharacterDock() {
  return useContext(Ctx)
}
