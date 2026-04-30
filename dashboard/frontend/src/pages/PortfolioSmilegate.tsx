/**
 * 스마일게이트 RPG 로스트아크 DBA 포트폴리오 — V2 톤 통일
 * /portfolio/smilegate
 * A4 5페이지. 따뜻한 크림 배경 + 명조 디스플레이 + 산세리프 본문 + 골드 액센트.
 */

const FONT_BODY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, '맑은 고딕', 'Malgun Gothic', Pretendard, 'Apple SD Gothic Neo', sans-serif"
const FONT_SERIF = "'Charter', 'Iowan Old Style', 'Noto Serif KR', 'KoPub Batang', '바탕', Georgia, serif"
const FONT_MONO = "'JetBrains Mono', 'IBM Plex Mono', 'SF Mono', Menlo, Consolas, monospace"

const C = {
  bg: '#f5f0e6',
  bgSoft: '#ebe4d3',
  surface: '#ffffff',
  ink: '#1a1816',
  inkSoft: '#5c574d',
  inkMuted: '#8a847a',
  border: '#d6cfbf',
  borderSoft: '#e4ddcc',
  gold: '#a07f30',
  goldSoft: '#c19c44',
  goldFaint: '#e6d8a8',
}

// ────────────────────────────────────────────────
// 공통 컴포넌트
// ────────────────────────────────────────────────

function Page({ children, radial }: { children: React.ReactNode; radial?: boolean }) {
  return (
    <div style={{
      background: C.bg,
      padding: '64px 80px',
      pageBreakAfter: 'always',
      minHeight: '100vh',
      boxSizing: 'border-box',
      borderBottom: `1px solid ${C.border}`,
      position: 'relative',
      overflow: 'hidden',
    }}>
      {radial && (
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'radial-gradient(ellipse at 100% 0%, rgba(160, 127, 48, 0.08), transparent 55%)',
        }} />
      )}
      <div style={{ maxWidth: 1080, margin: '0 auto', position: 'relative' }}>{children}</div>
    </div>
  )
}

function PageBar({ no, kicker }: { no: string; kicker: string }) {
  return (
    <header style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
      paddingBottom: 24, borderBottom: `1px solid ${C.border}`,
    }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
        <span style={{ fontFamily: FONT_SERIF, fontSize: 13, color: C.gold, fontStyle: 'italic' }}>
          No. {no}
        </span>
        <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.08em' }}>
          {kicker}
        </span>
      </div>
      <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted }}>
        SMILEGATE RPG · LOST ARK · DBA
      </span>
    </header>
  )
}

function PageTitle({ children, sub }: { children: React.ReactNode; sub?: string }) {
  return (
    <div style={{ marginTop: 56, marginBottom: 48 }}>
      <h2 style={{
        fontFamily: FONT_SERIF,
        fontSize: 56, fontWeight: 400, lineHeight: 1.05,
        letterSpacing: '-0.025em', color: C.ink, margin: 0,
      }}>
        {children}
      </h2>
      {sub && (
        <p style={{
          fontSize: 13, color: C.inkMuted, marginTop: 16, maxWidth: 560,
          fontStyle: 'italic', fontFamily: FONT_SERIF,
        }}>
          {sub}
        </p>
      )}
    </div>
  )
}

function SectionLabel({ children }: { children: string }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'baseline', gap: 14,
      marginTop: 40, marginBottom: 24,
    }}>
      <span style={{
        fontFamily: FONT_MONO, fontSize: 11, color: C.gold,
        letterSpacing: '0.18em', textTransform: 'uppercase',
      }}>{children}</span>
      <span style={{ flex: 1, height: 1, background: C.border }} />
    </div>
  )
}

function MatchRow({ idx, req, target, mine }: { idx: string; req: string; target: string; mine: string }) {
  return (
    <article style={{
      display: 'grid', gridTemplateColumns: '60px 200px 1fr', gap: 32,
      paddingTop: 22, paddingBottom: 22,
      borderTop: `1px solid ${C.borderSoft}`,
    }}>
      <span style={{
        fontFamily: FONT_SERIF, fontSize: 24, fontStyle: 'italic',
        color: C.gold, fontWeight: 400, lineHeight: 1,
      }}>{idx}</span>
      <div>
        <div style={{ fontSize: 14, fontWeight: 600, color: C.ink, marginBottom: 6 }}>{req}</div>
        <div style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.inkMuted, letterSpacing: '0.05em' }}>{target}</div>
      </div>
      <p style={{ fontSize: 13.5, color: C.inkSoft, lineHeight: 1.8, margin: 0 }}>{mine}</p>
    </article>
  )
}

function TroubleEntry({ idx, title, problem, cause, solution }: {
  idx: string; title: string; problem: string; cause: string; solution: string
}) {
  return (
    <article style={{
      paddingTop: 24, paddingBottom: 24,
      borderTop: `1px solid ${C.borderSoft}`,
    }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 16 }}>
        <span style={{
          fontFamily: FONT_SERIF, fontSize: 22, fontStyle: 'italic',
          color: C.gold, fontWeight: 400, lineHeight: 1,
        }}>{idx}</span>
        <h3 style={{
          fontFamily: FONT_SERIF, fontSize: 22, fontWeight: 400,
          color: C.ink, margin: 0, letterSpacing: '-0.015em',
        }}>{title}</h3>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '90px 1fr', rowGap: 12, columnGap: 24, paddingLeft: 38 }}>
        <span style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.inkMuted, paddingTop: 2, letterSpacing: '0.1em' }}>문제</span>
        <p style={{ fontSize: 13, color: C.inkSoft, margin: 0, lineHeight: 1.75 }}>{problem}</p>
        <span style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.inkMuted, paddingTop: 2, letterSpacing: '0.1em' }}>원인</span>
        <p style={{ fontSize: 13, color: C.inkSoft, margin: 0, lineHeight: 1.75 }}>{cause}</p>
        <span style={{ fontFamily: FONT_MONO, fontSize: 10, color: C.gold, paddingTop: 2, letterSpacing: '0.1em' }}>대응</span>
        <p style={{ fontSize: 13, color: C.ink, margin: 0, lineHeight: 1.75, fontWeight: 500 }}>{solution}</p>
      </div>
    </article>
  )
}

function FootStrip() {
  return (
    <footer style={{
      paddingTop: 24, marginTop: 64,
      borderTop: `1px solid ${C.border}`,
      display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
      fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.05em',
    }}>
      <span>github.com/2rami/debi-marlene</span>
      <span>goenho0613@gmail.com</span>
      <span style={{ color: C.gold }}>신구대 시각디자인 · 2026.02 졸업</span>
    </footer>
  )
}

// ────────────────────────────────────────────────
// 메인
// ────────────────────────────────────────────────

export default function PortfolioSmilegate() {
  return (
    <div style={{
      fontFamily: FONT_BODY, color: C.ink, background: C.bg, minHeight: '100vh',
    }}>

      {/* ── PAGE 1 — HERO ── */}
      <Page radial>
        <header style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          paddingBottom: 24, borderBottom: `1px solid ${C.border}`,
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
            <span style={{ fontFamily: FONT_SERIF, fontSize: 13, color: C.gold, fontStyle: 'italic' }}>
              경력기술서
            </span>
            <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.08em' }}>
              SMILEGATE RPG / LOST ARK / DBA
            </span>
          </div>
          <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted }}>
            2026.04 · 신입 지원
          </span>
        </header>

        <div style={{ marginTop: 100, marginBottom: 100 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 28 }}>
            <span style={{ fontFamily: FONT_SERIF, fontSize: 13, color: C.gold, fontStyle: 'italic' }}>
              No. 00 — 양건호
            </span>
            <span style={{ flex: 1, height: 1, background: C.border }} />
            <span style={{ fontFamily: FONT_MONO, fontSize: 11, color: C.inkMuted, letterSpacing: '0.05em' }}>
              YANG · GEONHO
            </span>
          </div>

          <h1 style={{
            fontFamily: FONT_SERIF, fontSize: 110, fontWeight: 400, lineHeight: 1.02,
            letterSpacing: '-0.025em', margin: '0 0 56px', color: C.ink,
          }}>
            데이터를<br />
            <em style={{ fontStyle: 'italic', color: C.gold }}>다치게 하지</em><br />
            않는 일.
          </h1>

          <div style={{
            display: 'grid', gridTemplateColumns: '5fr 6fr', gap: 64,
            paddingTop: 32, borderTop: `2px solid ${C.ink}`,
          }}>
            <p style={{
              fontFamily: FONT_SERIF, fontSize: 19, lineHeight: 1.75, color: C.ink, margin: 0,
            }}>
              디스코드 봇을 1인으로 24/7 운영하며 데이터 모델 설계,
              무중단 마이그레이션, 정합성 진단을 현장에서 익혀 왔습니다.
            </p>
            <p style={{ fontSize: 14, lineHeight: 1.85, color: C.inkSoft, margin: 0 }}>
              화려한 산출물보다 라이브 서비스의 데이터를 지켜내는 일이
              가장 단단한 기여라고 믿습니다. 단일 GCS JSON에서 출발해
              Firestore 3컬렉션 분리로 정합성을 회복한 운영 사례를 가지고
              스마일게이트 RPG의 라이브 데이터 곁으로 가고자 합니다.
            </p>
          </div>
        </div>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 0,
          borderTop: `1px solid ${C.border}`, borderBottom: `1px solid ${C.border}`,
        }}>
          {[
            { n: '01', v: '6개월+', l: '24/7 라이브 운영' },
            { n: '02', v: '148', l: '디스코드 길드' },
            { n: '03', v: '172', l: '문서 무중단 이관' },
            { n: '04', v: '7년+', l: '로스트아크 누적' },
          ].map((m, i) => (
            <div key={i} style={{
              padding: '28px 24px',
              borderRight: i < 3 ? `1px solid ${C.borderSoft}` : 'none',
            }}>
              <div style={{
                fontFamily: FONT_MONO, fontSize: 10, color: C.gold,
                letterSpacing: '0.15em', marginBottom: 14,
              }}>{m.n}</div>
              <div style={{
                fontFamily: FONT_SERIF, fontSize: 38, fontWeight: 400,
                letterSpacing: '-0.02em', color: C.ink, lineHeight: 1,
              }}>{m.v}</div>
              <div style={{ fontSize: 11, color: C.inkMuted, marginTop: 10 }}>{m.l}</div>
            </div>
          ))}
        </div>

        <FootStrip />
      </Page>

      {/* ── PAGE 2 — 직무 요건 매핑 ── */}
      <Page>
        <PageBar no="01" kicker="공고 요건과 운영 경험의 매핑" />
        <PageTitle sub="공고에 명시된 요건 하나하나를 1인 운영 현장에서 어떤 사례로 충족했는지 정리합니다.">
          직무 요건 정리
        </PageTitle>

        <SectionLabel>필수 요건</SectionLabel>
        <MatchRow idx="i" req="RDBMS 기본"
          target="SQL · 인덱스 · 실행계획"
          mine="SQLite 실서비스 운영 경험으로 RDBMS 핵심 개념 보유. MSSQL은 입사 시점까지 Microsoft Learn 트랙과 Stored Procedure 작성 연습으로 실무 진입 속도를 끌어올릴 계획입니다."
        />
        <MatchRow idx="ii" req="데이터 정합성 사고"
          target="라이브 서비스 데이터 보호"
          mine="멀티 컨테이너 동시 쓰기로 인한 lost update를 직접 진단하고, 단일 JSON을 도메인 단위(Firestore 3컬렉션)로 분리해 무중단 이관까지 마쳤습니다."
        />
        <MatchRow idx="iii" req="모니터링·트러블슈팅"
          target="원인 추적과 재발 방지"
          mine="24/7 봇 운영 중 race condition, env drift, 세션 충돌을 직접 디버깅하고, 체크리스트 대신 자동 검증 가드로 같은 사고가 재발하지 않게 시스템화했습니다."
        />
        <MatchRow idx="iv" req="문서 작성"
          target="운영 절차 · 장애 보고"
          mine="dak.gg 비공식 API 엔드포인트를 Network 탭 분석으로 전수 수집·문서화. 운영 함정과 배포 절차도 자체 메모리 시스템으로 관리해 1인 운영의 컨텍스트 손실을 막아 왔습니다."
        />

        <SectionLabel>우대 사항</SectionLabel>
        <MatchRow idx="v" req="로스트아크 플레이"
          target="게임 도메인 이해"
          mine="오픈베타부터 곁에 두고 즐겨온 라이브 서비스. 휴식기는 있었지만 매번 돌아왔고, 현재는 기상술사를 본캐로 키우는 중입니다. 군단장 시즌의 서사를 가장 깊이 즐겼던 사용자로서, 시즌·재화·콘텐츠 흐름의 변화를 길게 누적해 본 시간이 있습니다."
        />
        <MatchRow idx="vi" req="MySQL 운영"
          target="쿼리 튜닝 · 백업"
          mine="RDBMS 기본 개념(SQLite 운영 경험)에서 MySQL로 확장 학습 중. 정합성·마이그레이션 의사결정 경험은 RDBMS 종류와 무관하게 이식이 가능한 자산이라고 생각합니다."
        />

        <FootStrip />
      </Page>

      {/* ── PAGE 3 — 마이그레이션 사례 ── */}
      <Page>
        <PageBar no="02" kicker="GCS 단일 JSON → Firestore 3컬렉션" />
        <PageTitle sub="2026-04. 봇 멀티 컨테이너 환경의 lost update와 split-brain 패턴을 도메인 분리로 회복.">
          무중단<br />마이그레이션
        </PageTitle>

        <SectionLabel>문제 정의</SectionLabel>
        <p style={{ fontFamily: FONT_SERIF, fontSize: 17, color: C.ink, lineHeight: 1.85, margin: 0, maxWidth: 760 }}>
          단일 <code style={{ fontFamily: FONT_MONO, fontSize: 14, background: C.bgSoft, padding: '2px 8px', borderRadius: 2, color: C.gold }}>settings.json</code>
          (GCS) 저장 구조에서 봇 멀티 컨테이너 동시 쓰기에 의한 lost update와,
          대시보드 백엔드가 자체 GCS 클라이언트로 같은 파일을 읽고 쓰는
          <em style={{ fontStyle: 'italic', color: C.gold }}> split-brain</em> 패턴이 결합되어 정합성 사고가 반복되고 있었습니다.
        </p>

        <SectionLabel>모델 재설계</SectionLabel>
        <p style={{ fontSize: 14, color: C.inkSoft, lineHeight: 1.8, margin: '0 0 28px', maxWidth: 760 }}>
          한 덩어리 JSON을 도메인 단위로 분해해 Firestore 3컬렉션으로 분리.
          한 길드 변경이 다른 길드 문서에 영향을 주지 않고, 사용자 한 명의 토글이
          다른 사용자에 영향을 주지 않는 격리 구조입니다.
        </p>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
          borderTop: `1px solid ${C.border}`, borderBottom: `1px solid ${C.border}`,
        }}>
          {[
            { name: 'guilds/', count: '148', desc: '길드별 봇 설정' },
            { name: 'users/', count: '23', desc: '사용자별 캐릭터·구독' },
            { name: 'global/', count: '1', desc: '서비스 전역 설정' },
          ].map((c, i) => (
            <div key={c.name} style={{
              padding: '24px 24px',
              borderRight: i < 2 ? `1px solid ${C.borderSoft}` : 'none',
            }}>
              <div style={{ fontFamily: FONT_MONO, fontSize: 12, color: C.gold, letterSpacing: '0.05em' }}>{c.name}</div>
              <div style={{
                fontFamily: FONT_SERIF, fontSize: 44, fontWeight: 400,
                letterSpacing: '-0.02em', color: C.ink, lineHeight: 1, marginTop: 10,
              }}>{c.count}</div>
              <div style={{ fontSize: 11, color: C.inkMuted, marginTop: 8 }}>{c.desc}</div>
            </div>
          ))}
        </div>

        <SectionLabel>마이그레이션 스크립트</SectionLabel>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {[
            { h: 'dry-run 모드로 사전 검증', b: '실행 전 차이를 출력해 운영 중 재시도가 가능하도록 설계.' },
            { h: <>set(merge=True)로 멱등성 확보</>, b: '중복 실행해도 결과가 동일해 사고 시 즉시 재실행이 안전.' },
            { h: 'root-level stray 자동 보정', b: '잘못된 위치에 박혀 있던 길드 ID를 자동 탐지해 정상 위치로 병합.' },
          ].map((it, i) => (
            <li key={i} style={{
              display: 'grid', gridTemplateColumns: '40px 1fr',
              paddingTop: 16, paddingBottom: 16, borderTop: `1px solid ${C.borderSoft}`,
            }}>
              <span style={{ fontFamily: FONT_SERIF, fontSize: 16, color: C.gold, fontStyle: 'italic' }}>0{i + 1}</span>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: C.ink, marginBottom: 4 }}>{it.h}</div>
                <p style={{ fontSize: 13, color: C.inkSoft, margin: 0, lineHeight: 1.7 }}>{it.b}</p>
              </div>
            </li>
          ))}
        </ul>
        <div style={{
          marginTop: 24, padding: '16px 20px',
          background: C.surface, borderLeft: `3px solid ${C.gold}`,
          fontFamily: FONT_SERIF, fontSize: 16, color: C.ink, fontStyle: 'italic',
        }}>
          결과 — 148 guild + 23 user + 1 global = <strong style={{ fontWeight: 600 }}>172 문서 무손실 이관 완료.</strong>
        </div>

        <SectionLabel>운영 swap 전략</SectionLabel>
        <p style={{ fontSize: 14, color: C.inkSoft, lineHeight: 1.8, margin: 0, maxWidth: 760 }}>
          Firestore 단일 진실 + GCS 자동 fallback 구조로,
          <code style={{ fontFamily: FONT_MONO, fontSize: 12, background: C.bgSoft, padding: '2px 8px', margin: '0 6px', borderRadius: 2, color: C.gold }}>
            SETTINGS_BACKEND
          </code>
          환경변수만 바꾸면 firestore / dual / gcs로 즉시 전환됩니다. 사고가 발생해도
          재배포 없이 롤백할 수 있도록 둔 안전망입니다.
        </p>

        <FootStrip />
      </Page>

      {/* ── PAGE 4 — 트러블슈팅 ── */}
      <Page>
        <PageBar no="03" kicker="라이브 서비스 운영 중 만난 사고와 가드 제도화" />
        <PageTitle sub="문제는 한 번이면 충분하다. 두 번째부터는 자동 가드가 사람보다 정확합니다.">
          트러블슈팅<br />기록
        </PageTitle>

        <SectionLabel>데이터 · 동시성</SectionLabel>
        <TroubleEntry idx="i"
          title="길드 정리 race condition"
          problem="cleanup_removed_servers 와 on_ready 이벤트가 겹쳐 일부 길드 데이터가 누락되었습니다."
          cause="봇 시작 시 캐시가 채워지기 전에 cleanup이 돌아 정상 길드도 'removed'로 판정되었습니다."
          solution="이벤트 순서 가드를 추가하고 캐시 ready 상태를 명시적으로 대기하도록 보정. 보정 절차는 함께 문서화했습니다."
        />
        <TroubleEntry idx="ii"
          title="환경 변수 4곳 분기 (env drift)"
          problem="동일 변수가 컨테이너·VM·시크릿·로컬에 따로 존재해 운영 드리프트가 발생했습니다."
          cause="설정의 단일 진실 공급원이 정해지지 않아 각 진입점이 자기 값을 그대로 유지하고 있었습니다."
          solution="make sync-check 자동 검증 가드를 만들어 4곳의 값이 일치하지 않으면 빌드 자체를 차단하도록 제도화했습니다."
        />

        <SectionLabel>운영 · 배포</SectionLabel>
        <TroubleEntry idx="iii"
          title="VM·로컬 동시 연결 시 무한 재연결"
          problem="개발 중 같은 봇 토큰이 VM과 로컬에서 동시 접속하며 디스코드 세션이 충돌했습니다."
          cause="디스코드 게이트웨이는 같은 토큰의 두 세션을 허용하지 않아 서로를 강제 종료하는 사이클이 생겼습니다."
          solution="make stop-vm 절차를 강제하고 로컬 테스트 스크립트가 VM 상태를 사전 점검하도록 묶었습니다."
        />
        <TroubleEntry idx="iv"
          title="다수 솔로봇 정리 시 pkill 함정"
          problem="pkill -f로 솔로봇만 죽이려다 무관한 python 프로세스가 같이 종료되었습니다."
          cause="-f 옵션은 cmdline 부분 매치라 키워드가 겹치는 다른 프로세스도 매칭됩니다."
          solution="환경 블록(/proc/*/environ) 기반으로 정확한 PID를 식별하는 scripts/kill_solo_bots.sh를 작성했습니다."
        />

        <FootStrip />
      </Page>

      {/* ── PAGE 5 — 게임 + 자기 진단 + 끝맺음 ── */}
      <Page radial>
        <PageBar no="04" kicker="라이트 유저 관점에서 누적해 본 라이브 서비스" />
        <PageTitle sub="게임 도메인 이해와 직무 자기 진단을 정리합니다.">
          게임 경험과<br />자기 진단
        </PageTitle>

        <SectionLabel>로스트아크</SectionLabel>
        <p style={{ fontFamily: FONT_SERIF, fontSize: 17, color: C.ink, lineHeight: 1.85, margin: 0, maxWidth: 760 }}>
          오픈베타부터 곁에 두고 즐겨온 라이브 서비스입니다. 휴식기는 있었지만
          매번 돌아왔고, 현재는 기상술사를 본캐로 키우며 신규 클래스가 기존
          콘텐츠 흐름과 어떻게 맞물리는지를 사용자로 지켜보고 있습니다.
          <em style={{ fontStyle: 'italic', color: C.gold }}> 군단장 시즌의 서사</em>를 가장 깊게 즐겼던 사용자로서, 한 시즌이 끝나고
          다음 시즌이 어떤 방식으로 이어 붙는지를 보는 재미가 컸습니다.
        </p>

        <SectionLabel>이터널 리턴</SectionLabel>
        <p style={{ fontSize: 14, color: C.inkSoft, lineHeight: 1.8, margin: 0, maxWidth: 760 }}>
          1,100시간+ 코어 플레이. Debi Marlene 봇 운영의 직접적 동기이자,
          dak.gg 비공식 API 분석으로 데이터 수집·정규화 파이프라인을 구축한 영역입니다.
        </p>

        <SectionLabel>자기 진단 — DBA 직무 기준</SectionLabel>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0 }}>
          {[
            { area: '데이터 모델링', level: '강점', desc: 'Firestore 3컬렉션 분해 설계와 무중단 이관' },
            { area: '데이터 마이그레이션', level: '강점', desc: '172문서 무손실, 멱등 보장 스크립트 작성' },
            { area: '모니터링 · 장애 대응', level: '강점', desc: 'env drift 자동 검증 가드 자체 제작' },
            { area: 'RDBMS · SQL', level: '입문~기초', desc: 'MSSQL/MySQL Microsoft Learn 트랙 진행' },
          ].map((d, i) => (
            <div key={d.area} style={{
              padding: '20px 24px',
              borderTop: `1px solid ${C.borderSoft}`,
              borderRight: i % 2 === 0 ? `1px solid ${C.borderSoft}` : 'none',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 8 }}>
                <span style={{ fontFamily: FONT_SERIF, fontSize: 18, color: C.ink }}>{d.area}</span>
                <span style={{
                  fontFamily: FONT_MONO, fontSize: 10,
                  color: d.level === '강점' ? C.gold : C.inkMuted,
                  letterSpacing: '0.1em',
                }}>{d.level}</span>
              </div>
              <p style={{ fontSize: 12, color: C.inkSoft, lineHeight: 1.6, margin: 0 }}>{d.desc}</p>
            </div>
          ))}
        </div>

        <div style={{
          marginTop: 64, paddingTop: 36,
          borderTop: `2px solid ${C.ink}`,
        }}>
          <p style={{
            fontFamily: FONT_SERIF, fontSize: 22, lineHeight: 1.65, color: C.ink,
            margin: '0 0 24px', fontStyle: 'italic', maxWidth: 720,
          }}>
            십수 년에 걸쳐 누적된 캐릭터·아이템·재화·시즌 데이터를 단 한 번의 오류 없이
            다뤄야 하는 서비스에서, 작은 봇 운영에서 배운 데이터 책임감을 발전시키고 싶습니다.
          </p>
        </div>

        <FootStrip />
      </Page>

      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        @page { margin: 0; size: A4; }
        @media print {
          * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        }
        body { background: ${C.bg}; }
        em { font-style: italic; }
      `}</style>
    </div>
  )
}
