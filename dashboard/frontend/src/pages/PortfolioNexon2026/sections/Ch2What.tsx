import SectionShell from '../shared/SectionShell'
import ArchitectureDiagram from '../shared/ArchitectureDiagram'
import { C, FONT_MONO, FONT_BODY } from '../shared/colors'
import { ARCHITECTURE } from '../content/llm'
import { FadeIn } from './_shared'

/**
 * CH 2 — WHAT
 * 02 ARCHITECTURE : 라이트 매거진 파이프라인 (각 노드에 스택 라벨)
 * 03 OTHER       : 다이어그램 밖 주변 시스템 (한 블록)
 */
export default function Ch2What() {
  return (
    <>
      <ArchitectureDiagram steps={ARCHITECTURE.steps} title={ARCHITECTURE.title} />

      <SectionShell
        id="tech"
        ch="CH 2"
        no="03"
        kicker="OTHER · 다이어그램 밖 주변 시스템"
        title="이 봇을 굴리는 나머지 인프라"
        variant="aside"
        background={C.bgSoft}
      >
        <FadeIn delay={0.05}>
          <OtherStackBlock items={OTHER_STACK} />
        </FadeIn>
      </SectionShell>
    </>
  )
}

const OTHER_STACK = [
  { label: '폴백 백엔드', value: 'Modal Gemma4 LoRA — CHAT_BACKEND=modal 스위치' },
  { label: 'Daily Feed 큐레이터', value: 'claude-sonnet-4-6 · GitHub Actions cron 47분' },
  { label: '음성 파이프라인', value: 'Qwen3.5-Omni STT · CosyVoice3 TTS (Modal)' },
  { label: '스토리지', value: 'Firestore 3컬렉션 + GCS · feed_seen 30d TTL' },
  { label: '컴퓨트 / 컨테이너', value: 'GCP VM · Cloud Run · Modal · Docker 3컨테이너' },
  { label: '시크릿 / 도메인', value: 'GCP Secret Manager · Cloudflare debimarlene.com' },
  { label: '대시보드', value: 'React 18 · Vite · TypeScript · Tailwind' },
  { label: '웹패널', value: 'Vite + vite-plugin-pwa' },
] as const

function OtherStackBlock({ items }: { items: readonly { label: string; value: string }[] }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        columnGap: 'clamp(16px, 2vw, 28px)',
        rowGap: 0,
        borderTop: `1px solid ${C.cardBorder}`,
      }}
    >
      {items.map((it) => (
        <div
          key={it.label}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 6,
            padding: '18px 0',
            borderBottom: `1px solid ${C.cardBorder}`,
          }}
        >
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              letterSpacing: '0.16em',
              color: C.nexonBlue,
              fontWeight: 800,
              textTransform: 'uppercase',
            }}
          >
            {it.label}
          </span>
          <span
            style={{
              fontFamily: FONT_BODY,
              fontSize: 15,
              lineHeight: 1.55,
              color: C.ink,
              fontWeight: 500,
              letterSpacing: '-0.005em',
              wordBreak: 'keep-all',
            }}
          >
            {it.value}
          </span>
        </div>
      ))}
    </div>
  )
}
