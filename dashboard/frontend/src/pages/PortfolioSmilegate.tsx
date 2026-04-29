/**
 * 스마일게이트 RPG 로스트아크 DBA 포트폴리오 - PDF/웹 겸용
 * /portfolio/smilegate
 * 한 섹션 = 한 페이지. A4 최적화. DBA 직무 관점 (데이터 정합성·마이그레이션·운영 안정성).
 */

const C = {
  bg: '#1a1d2e',
  card: '#252838',
  cardAlt: '#2a2d40',
  cyan: '#3cabc9',
  gold: '#e8b34a',
  white: '#f0f0f5',
  gray: '#a0a5b4',
  muted: '#6e7382',
  border: '#2d3041',
  red: '#ed4245',
  yellow: '#faa61a',
  green: '#43b581',
}

function Page({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      background: C.bg,
      padding: '40px 48px',
      pageBreakAfter: 'always',
      minHeight: '100vh',
      boxSizing: 'border-box',
    }}>
      {children}
    </div>
  )
}

function Title({ children, sub }: { children: string; sub?: string }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <h2 style={{ fontSize: 32, fontWeight: 800, margin: 0, color: C.cyan }}>{children}</h2>
      {sub && <p style={{ color: C.gray, fontSize: 14, marginTop: 6 }}>{sub}</p>}
      <div style={{ width: 40, height: 3, background: C.cyan, marginTop: 12, borderRadius: 2 }} />
    </div>
  )
}

function Card({ children, accent, style: s }: { children: React.ReactNode; accent?: string; style?: React.CSSProperties }) {
  return (
    <div style={{
      background: C.card, border: `1px solid ${C.border}`, borderRadius: 12,
      padding: 16, position: 'relative', overflow: 'hidden', ...s,
    }}>
      {accent && <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 3, background: accent }} />}
      {children}
    </div>
  )
}

function Label({ children, color = C.cyan }: { children: string; color?: string }) {
  return <span style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.5, color }}>{children}</span>
}

function Tag({ children, color = C.cyan }: { children: string; color?: string }) {
  return (
    <span style={{
      display: 'inline-block', padding: '3px 10px', borderRadius: 20, fontSize: 11,
      color, border: `1px solid ${color}33`, background: `${color}11`, marginRight: 6, marginBottom: 4,
    }}>{children}</span>
  )
}

function Bullet({ children, color = C.cyan }: { children: React.ReactNode; color?: string }) {
  return (
    <div style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: color, marginTop: 7, flexShrink: 0 }} />
      <span style={{ fontSize: 13, color: C.gray, lineHeight: 1.6 }}>{children}</span>
    </div>
  )
}

function TroubleCard({ title, problem, cause, solution, color }: {
  title: string; problem: string; cause: string; solution: string; color: string
}) {
  return (
    <Card accent={color} style={{ marginBottom: 10 }}>
      <div style={{ paddingLeft: 8 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: C.white, marginBottom: 10 }}>{title}</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div>
            <Label color={C.red}>Problem</Label>
            <p style={{ fontSize: 11, color: C.gray, marginTop: 4, lineHeight: 1.5 }}>{problem}</p>
          </div>
          <div>
            <Label color={C.yellow}>Root Cause</Label>
            <p style={{ fontSize: 11, color: C.gray, marginTop: 4, lineHeight: 1.5 }}>{cause}</p>
          </div>
          <div>
            <Label color={C.green}>Solution</Label>
            <p style={{ fontSize: 11, color: C.gray, marginTop: 4, lineHeight: 1.5 }}>{solution}</p>
          </div>
        </div>
      </div>
    </Card>
  )
}

export default function PortfolioSmilegate() {
  return (
    <div style={{ fontFamily: "'Pretendard', 'Apple SD Gothic Neo', sans-serif", color: C.white, background: C.bg }}>

      {/* ═══ PAGE 1: HERO ═══ */}
      <Page>
        <div style={{ display: 'flex', alignItems: 'center', minHeight: 'calc(100vh - 80px)' }}>
          <div style={{ flex: 1 }}>
            <div style={{
              display: 'inline-block', padding: '4px 14px', borderRadius: 20, fontSize: 11,
              fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase',
              color: C.muted, border: `1px solid ${C.border}`, marginBottom: 20,
            }}>Smilegate RPG -- LOST ARK -- DBA</div>

            <h1 style={{ fontSize: 48, fontWeight: 800, lineHeight: 1.2, margin: '0 0 8px', color: C.cyan }}>양건호</h1>

            <h2 style={{ fontSize: 36, fontWeight: 800, margin: '0 0 24px', color: C.white }}>
              데이터의 <span style={{ color: C.cyan }}>정합성</span>이 곧 서비스
            </h2>

            <p style={{ fontSize: 16, color: C.gray, lineHeight: 1.7, maxWidth: 460, marginBottom: 32 }}>
              디스코드 봇 서비스를 1인으로 24/7 운영하며,<br />
              데이터 모델 설계·마이그레이션·정합성 진단을<br />
              현장에서 익혀온 신입 지원자입니다.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, maxWidth: 540 }}>
              {[
                { value: '6+', label: '개월 24/7 운영' },
                { value: '148', label: '디스코드 서버' },
                { value: '172', label: '문서 무중단 이관' },
                { value: '7년+', label: '로스트아크 누적' },
              ].map((s, i) => (
                <div key={i} style={{ textAlign: 'center', padding: '14px 8px', background: C.card, borderRadius: 12, border: `1px solid ${C.border}` }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: C.cyan }}>{s.value}</div>
                  <div style={{ fontSize: 10, color: C.muted, marginTop: 4 }}>{s.label}</div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 28, padding: '14px 18px', background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, maxWidth: 540 }}>
              <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, color: C.cyan, marginBottom: 8 }}>
                Profile
              </div>
              <div style={{ fontSize: 13, color: C.gray, lineHeight: 1.7 }}>
                <div>신구대학교 시각디자인과 졸업 (2026.02)</div>
                <div>비전공자, 6개월 자력 풀스택 구축</div>
                <div style={{ marginTop: 6 }}>
                  <span style={{ color: C.muted }}>GitHub</span>{' '}
                  <span style={{ color: C.white }}>github.com/2rami/debi-marlene</span>
                </div>
                <div>
                  <span style={{ color: C.muted }}>Email</span>{' '}
                  <span style={{ color: C.white }}>goenho0613@gmail.com</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Page>

      {/* ═══ PAGE 2: 공고 매칭 ═══ */}
      <Page>
        <Title sub="DBA 신입 트랙 — 직무 요건 ↔ 운영 경험 매핑">공고 매칭</Title>

        <Label>REQUIRED</Label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 10, marginBottom: 24 }}>
          {[
            { n: '1', title: 'RDBMS 기본 이해', req: 'SQL · 인덱스 · 실행계획', match: 'SQLite 실서비스 운영 경험. RDBMS 핵심 개념 보유. MSSQL은 Microsoft Learn 트랙으로 학습 중 (Stored Procedure / 인덱스 단계).' },
            { n: '2', title: '데이터 정합성 사고', req: '서비스 데이터를 다치게 하지 않는 감각', match: '멀티 컨테이너 동시 쓰기로 인한 lost update 진단. 단일 JSON → 도메인 분리(Firestore 3컬렉션) 재설계 + 무중단 이관.' },
            { n: '3', title: '모니터링·트러블슈팅', req: '이슈 원인 추적 + 재발 방지', match: '24/7 봇 운영 중 race condition · env drift · 세션 충돌 직접 디버깅. 체크리스트 대신 자동 검증 가드(`make sync-check`)로 재발 방지.' },
            { n: '4', title: '문서 작성', req: '운영 절차 · 장애 보고서', match: 'dak.gg 비공식 API 엔드포인트 Network 탭 분석 → 전수 문서화. 운영 함정·배포 절차 자체 메모리 시스템 운용.' },
          ].map(item => (
            <Card key={item.n}>
              <div style={{ width: 24, height: 24, borderRadius: '50%', background: `${C.cyan}1a`, border: `1px solid ${C.cyan}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: C.cyan }}>{item.n}</span>
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.white, marginBottom: 4 }}>{item.title}</div>
              <div style={{ fontSize: 10, color: C.muted, marginBottom: 8 }}>{item.req}</div>
              <div style={{ fontSize: 12, color: C.gray, lineHeight: 1.6 }}>{item.match}</div>
            </Card>
          ))}
        </div>

        <Label color={C.gold}>PREFERRED</Label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginTop: 10 }}>
          {[
            { n: '1', title: '로스트아크 플레이', req: '게임 도메인 이해', match: '오픈베타부터 라이트 유저로 누적, 휴식기 포함 7년+ 관찰. 최근 기상술사 주력. 시즌·재화·콘텐츠 흐름을 사용자 시점에서 길게 본 라이브 서비스.' },
            { n: '2', title: 'MySQL 운영', req: '쿼리 튜닝 · 백업', match: 'RDBMS 기본 개념(SQLite 운영 경험)에서 MySQL로 확장 학습 중. 실서비스 정합성·마이그레이션 의사결정 경험은 RDBMS 종류와 무관하게 이식 가능.' },
            { n: '3', title: '협업 도구', req: 'Git · 이슈 트래킹', match: 'Git/GitHub 일상 사용. Makefile 기반 배포 파이프라인 + Discord 커뮤니티 운영으로 비동기 협업 경험.' },
          ].map(item => (
            <Card key={item.n}>
              <div style={{ width: 24, height: 24, borderRadius: '50%', background: `${C.gold}1a`, border: `1px solid ${C.gold}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: C.gold }}>{item.n}</span>
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.white, marginBottom: 4 }}>{item.title}</div>
              <div style={{ fontSize: 10, color: C.muted, marginBottom: 8 }}>{item.req}</div>
              <div style={{ fontSize: 12, color: C.gray, lineHeight: 1.6 }}>{item.match}</div>
            </Card>
          ))}
        </div>
      </Page>

      {/* ═══ PAGE 3: 데이터 운영 핵심 사례 ═══ */}
      <Page>
        <Title sub="GCS 단일 JSON → Firestore 3컬렉션 무중단 이관 (2026-04)">데이터 모델 재설계 사례</Title>

        <Card style={{ marginBottom: 14 }}>
          <Label color={C.red}>문제 정의</Label>
          <p style={{ fontSize: 13, color: C.gray, lineHeight: 1.7, marginTop: 8 }}>
            단일 <code style={{ color: C.cyan }}>settings.json</code>(GCS) 저장 구조에서 (a) 봇 멀티 컨테이너 동시 쓰기에 의한
            lost update + (b) 대시보드 백엔드가 자체 GCS 클라이언트로 같은 파일을 읽고 쓰는 <strong style={{ color: C.gold }}>split-brain</strong> 패턴이
            결합되어 정합성 사고가 반복됨을 진단.
          </p>
        </Card>

        <Card style={{ marginBottom: 14 }}>
          <Label color={C.cyan}>모델 재설계</Label>
          <p style={{ fontSize: 13, color: C.gray, lineHeight: 1.7, marginTop: 8, marginBottom: 8 }}>
            한 덩어리 JSON 을 도메인 단위로 분해 → Firestore 3 컬렉션으로 분리.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
            {[
              { name: 'guilds/', count: '148', desc: '길드별 봇 설정' },
              { name: 'users/', count: '23', desc: '사용자별 캐릭터·구독' },
              { name: 'global/', count: '1', desc: '서비스 전역 설정' },
            ].map(c => (
              <div key={c.name} style={{ padding: '10px 12px', background: C.cardAlt, borderRadius: 8, border: `1px solid ${C.border}` }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: C.cyan }}>{c.name}</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: C.white, marginTop: 2 }}>{c.count}</div>
                <div style={{ fontSize: 10, color: C.muted, marginTop: 2 }}>{c.desc}</div>
              </div>
            ))}
          </div>
          <p style={{ fontSize: 12, color: C.muted, marginTop: 10, lineHeight: 1.5 }}>
            한 길드 변경이 다른 길드 문서에 영향 0, 사용자 한 명의 토글이 다른 사용자에 영향 0.
          </p>
        </Card>

        <Card style={{ marginBottom: 14 }}>
          <Label color={C.green}>마이그레이션 스크립트 — 재실행 안전성</Label>
          <div style={{ marginTop: 8 }}>
            <Bullet color={C.green}>dry-run 모드로 사전 검증 후 실행 (운영 중 재시도 가능)</Bullet>
            <Bullet color={C.green}><code style={{ color: C.cyan }}>set(merge=True)</code> 채택해 멱등성 확보</Bullet>
            <Bullet color={C.green}>root level stray 길드 ID 자동 탐지 → 정상 위치로 병합 보정</Bullet>
            <Bullet color={C.green}>결과: <strong style={{ color: C.white }}>148 guild + 23 user + 1 global = 172 문서 무손실 이관</strong></Bullet>
          </div>
        </Card>

        <Card>
          <Label color={C.gold}>운영 swap 전략 — Read-only fallback</Label>
          <p style={{ fontSize: 13, color: C.gray, lineHeight: 1.7, marginTop: 8 }}>
            Firestore 단일 진실 + GCS 자동 fallback. <code style={{ color: C.cyan }}>SETTINGS_BACKEND</code> 환경변수로
            <Tag color={C.green}>firestore</Tag><Tag color={C.gold}>dual</Tag><Tag color={C.muted}>gcs</Tag>
            즉시 전환 가능 — 사고 시 재배포 없이 롤백.
          </p>
        </Card>
      </Page>

      {/* ═══ PAGE 4: 트러블슈팅 ═══ */}
      <Page>
        <Title sub="라이브 서비스 운영 중 만난 정합성·동시성 이슈와 가드 제도화">트러블슈팅</Title>

        <Label>DATA · CONCURRENCY</Label>
        <div style={{ marginTop: 8, marginBottom: 16 }}>
          <TroubleCard color={C.cyan}
            title="길드 cleanup race condition"
            problem="`cleanup_removed_servers` 와 `on_ready` 이벤트가 겹쳐 일부 길드 데이터가 누락."
            cause="봇 시작 시 캐시가 채워지기 전에 cleanup 이 돌아 정상 길드도 'removed' 로 판정."
            solution="이벤트 순서 가드 추가 + 보정 절차 문서화. 재발 방지를 위해 캐시 ready 상태를 명시적으로 대기."
          />
          <TroubleCard color={C.cyan}
            title="환경 변수 4곳 분기 (env drift)"
            problem="동일 변수가 컨테이너·VM·시크릿·로컬에 따로 존재해 운영 드리프트 발생."
            cause="설정 단일 진실 공급원이 정해지지 않아 각 진입점이 자기 값을 그대로 유지."
            solution="`make sync-check` 자동 검증 가드 제도화. 4곳 값이 일치하지 않으면 빌드 차단."
          />
        </div>

        <Label color={C.gold}>OPS · DEPLOY</Label>
        <div style={{ marginTop: 8 }}>
          <TroubleCard color={C.gold}
            title="VM·로컬 동시 연결 시 무한 재연결"
            problem="개발 중 같은 봇 토큰이 VM·로컬에서 동시 접속 → 디스코드 세션 충돌."
            cause="디스코드 게이트웨이는 같은 토큰의 두 세션을 허용하지 않으며 강제 종료 후 재시도 사이클 진입."
            solution="`make stop-vm` 절차 강제 + 로컬 테스트 스크립트가 VM 상태를 사전 점검."
          />
          <TroubleCard color={C.gold}
            title="다수 솔로봇 정리 시 pkill 함정"
            problem="`pkill -f` 로 솔로봇만 죽이려다 무관한 python 프로세스가 같이 종료."
            cause="-f 옵션은 cmdline 부분 매치 → 키워드가 겹치는 다른 프로세스도 매칭."
            solution="환경 블록(`/proc/*/environ`) 기반 정확한 PID 식별 스크립트(`scripts/kill_solo_bots.sh`) 작성."
          />
        </div>
      </Page>

      {/* ═══ PAGE 5: 게임 경험 + 끝맺음 ═══ */}
      <Page>
        <Title sub="라이트 유저 관점 · 라이브 서비스 흐름 누적">게임 경험</Title>

        <Card style={{ marginBottom: 20 }}>
          <Label color={C.cyan}>로스트아크 PC</Label>
          <p style={{ fontSize: 13, color: C.gray, lineHeight: 1.7, marginTop: 8 }}>
            오픈베타부터 라이트 유저로 누적 플레이, 휴식기 포함 <strong style={{ color: C.white }}>7년+</strong> 관찰. 최근 기상술사 주력.
            시즌·재화 정책·콘텐츠 흐름을 사용자 시점에서 길게 지켜본 라이브 서비스.
          </p>
          <p style={{ fontSize: 12, color: C.muted, marginTop: 8, lineHeight: 1.6 }}>
            하드코어 레이더는 아니지만, 그렇기에 시즌 변화·시스템 개편·재화 정책의 흐름을 라이트 유저 관점에서
            누적해 본 시간이 있습니다. 게임 DB는 화려하지 않지만 가장 단단해야 한다는 점에서 관심을 두었습니다.
          </p>
        </Card>

        <Card style={{ marginBottom: 24 }}>
          <Label color={C.gold}>이터널 리턴</Label>
          <p style={{ fontSize: 13, color: C.gray, lineHeight: 1.7, marginTop: 8 }}>
            <strong style={{ color: C.white }}>1,100시간+</strong> 코어 플레이. Debi Marlene 봇 운영 동기. dak.gg 비공식 API 분석으로
            데이터 수집·정규화 파이프라인 구축.
          </p>
        </Card>

        {/* 자기 진단 */}
        <div style={{ fontSize: 14, fontWeight: 700, color: C.white, marginBottom: 12 }}>자기 진단 (DBA 직무 기준)</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 24 }}>
          {[
            { area: '데이터 모델링 사고', level: '강점', desc: 'Firestore 3컬렉션 분해 설계·실이관' },
            { area: '데이터 마이그레이션', level: '강점', desc: '172문서 무중단·재실행 안전 스크립트' },
            { area: '모니터링·장애 대응', level: '강점', desc: 'env drift 가드 자체 제작' },
            { area: 'RDBMS / SQL', level: '입문~기초', desc: 'MSSQL/MySQL Microsoft Learn 트랙 진행' },
          ].map(d => (
            <Card key={d.area} accent={d.level === '강점' ? C.green : C.gold}>
              <div style={{ paddingLeft: 8 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: C.white }}>{d.area}</div>
                <div style={{ fontSize: 11, color: d.level === '강점' ? C.green : C.gold, marginTop: 2, fontWeight: 600 }}>{d.level}</div>
                <div style={{ fontSize: 11, color: C.muted, marginTop: 6, lineHeight: 1.5 }}>{d.desc}</div>
              </div>
            </Card>
          ))}
        </div>

        {/* 끝맺음 */}
        <div style={{ textAlign: 'center', paddingTop: 20, borderTop: `1px solid ${C.border}` }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: C.white, marginBottom: 8 }}>
            오래 신뢰해 온 서비스의 가장 단단한 부분을 직접 지키고 싶습니다.
          </div>
          <p style={{ fontSize: 13, color: C.gray, maxWidth: 540, margin: '0 auto', lineHeight: 1.6 }}>
            십수 년에 걸쳐 누적된 캐릭터·아이템·재화·시즌 데이터를 단 한 번의 오류 없이 다뤄야 하는 서비스에서,
            작은 봇 운영에서 배운 데이터 책임감을 발전시키고 싶습니다.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 16 }}>
            <span style={{ fontSize: 12, color: C.muted }}>github.com/2rami/debi-marlene</span>
            <span style={{ color: C.border }}>|</span>
            <span style={{ fontSize: 12, color: C.muted }}>goenho0613@gmail.com</span>
          </div>
        </div>
      </Page>

      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        @page { margin: 0; size: A4; }
        @media print { * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; } }
        img { display: inline-block; }
      `}</style>
    </div>
  )
}
