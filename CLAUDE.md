# Debi Marlene

## 배포 대상 — 사내 맥미니 한 대
GCP Compute Engine VM 은 2026-08-25 에 삭제됐다. Docker·Artifact Registry 경로도 함께
끊겼다 — 미니엔 docker 가 없고 봇·대시보드·웹패널이 전부 venv 프로세스로 돈다.
`gcloud compute` 로 시작하는 지시가 어딘가 남아 있다면 그건 죽은 문서다.

| | |
|---|---|
| 호스트 | `ssh nachoneko` (`~/.ssh/config` 별칭, 사내 VPN 필요) |
| 경로 | `/Users/nachoneko/debimarlene` |
| 상주 | launchd LaunchDaemon `com.geono.debimarlene-{bot,dashboard,webpanel,caddy,tunnel}` |
| 배포 | rsync 로 파일을 밀고 프로세스를 kill — KeepAlive 가 30초 안에 되살린다 |

★**재시작 수단은 kill 뿐이다.** `launchctl` 직접 조작은 LaunchDaemon 이라 root 가 필요하고
원격 sudo 는 비번을 묻는다. 진짜로 멈춰야 할 때만 `make stop-bot`(비번 프롬프트)을 쓴다.

## 안전 규칙
- 로컬 테스트 전 `make stop-bot` 필수 — 같은 토큰으로 두 세션이 붙으면 Discord 가 무한 재연결.
  `make test-local` 은 서버 봇을 자동으로 멈추지 **않는다**(원격 sudo 가 필요해서다).
- git 브랜치는 main만. feature 브랜치 금지. (`archive/legacy-*` 는 백업용)
- 포트: dashboard 8081 / webpanel 8080 / Caddy 8090. 봇은 포트를 안 쓴다(Discord 아웃바운드).
- `dashboard/frontend/public/google046aee18f88daa1e.html` 을 지우면 Search Console 소유권이
  풀린다. 프론트 배포 타겟이 이 파일의 존재를 검사하고 없으면 멈춘다.

## 자주 쓰는 명령
| 작업 | 명령 |
|---|---|
| 전체 명령 목록 | `make` |
| 봇 배포 | `make deploy-bot` |
| 대시보드 배포 | `make deploy-dashboard` (프론트만 `deploy-dashboard-frontend`) |
| 웹패널 배포 | `make deploy-webpanel` |
| 상태 확인 | `make status` (프로세스 + 라이브 응답) |
| 로그 | `make logs-bot` / `logs-dashboard` / `logs-webpanel` / `logs-caddy` |
| 로컬 봇 | `make stop-bot` → `make test-local` → `make start-bot` |
| 대시보드 dev | backend `python3 dashboard/backend/app.py` (8081) / frontend `npm run dev` in `dashboard/frontend` (3002) |
| 웹패널 dev | backend `python3 webpanel/backend/app.py` (8080) / frontend `npm run dev` in `webpanel` (5173) |
| env 내려받기 | `./scripts/sync_env.sh pull` (맥↔윈도우 새 환경 셋업 1회) |
| env 대조 | `make sync-check` (로컬 .env 와 서버 시크릿의 키 목록 비교) |
| env 업로드 | `./scripts/sync_env.sh push` (로컬 수정 후 모든 기기 동기화) |
| 좀비 python 정리 | `./scripts/kill_solo_bots.sh all` |

## env 관리 (중요)
- **단일 진실: Google Cloud Secret Manager**. 노션 평문 저장 폐기 권장.
- Secret 3종: `debi-marlene-env` / `debi-marlene-env-solo-debi` / `debi-marlene-env-solo-marlene`
- 새 기기 셋업: `gcloud auth login` → `gcloud config set project ironic-objectivist-465713-a6` → `./scripts/sync_env.sh pull`
- secret 업데이트: 로컬 `.env` 수정 → `./scripts/sync_env.sh push` → 서버 `secrets/*.env` 반영 후 재시작.
  ⚠️서버가 실제로 읽는 것은 `~/debimarlene/secrets/{bot,dashboard,webpanel}.env` 다 —
  Secret Manager 에 push 한다고 서버에 반영되지 않는다. `make sync-check` 로 어긋남을 먼저 본다.
- `NEXON_API_KEY` (선택) — `/chat` 의 메이플 닉네임 검색용. https://openapi.nexon.com/my-application/ 에서 무료 발급.
  미설정 시 검색만 503 으로 막히고 페이지는 기본 캐릭터로 정상 동작한다. 캐릭터 이미지(static look) 자체는 키가 필요 없다.

## 코딩 규칙
- **이모지 금지** — 코드/임베드/메시지/로그 모두. 대체: SVG 또는 텍스트 기호 (#1, [TOP], *, -)
- **계층 분리**: `run/services/` (데이터/API) ↔ `run/views/` (Discord 포맷팅)
- **LayoutView ≠ Embed** — Container가 Embed 대체. 세부 규칙은 `feedback_discord_v2_layout` 메모리.

## 디스코드 읽기 (MCP)
- `discord-v2` — 봇 토큰으로 서버·채널·메시지를 읽고 보낸다. 본체는 `mcp_servers/discord_v2.py`.
- **전역(`~/.claude.json`)에 등록돼 있다** — 어느 프로젝트에서든 쓴다. 새 기기에서는 한 번 등록:
  `claude mcp add discord-v2 --scope user -- uv run --quiet --with mcp==2.0.0 python <이 레포>/mcp_servers/discord_v2.py`
  ⚠️프로젝트 `.mcp.json` 에 또 넣지 말 것 - 같은 이름이 두 스코프에 있으면 충돌한다(그래서 gitignore 했다).
- **Components V2 화면을 텍스트로 풀어준다.** 공개 디스코드 MCP 들은 `content` 만 읽어서
  우리 봇 화면이 빈 메시지로 보이는데, 이건 `MessageArea.tsx` 의 렌더러를 옮겨와
  Container/Section/Thumbnail/Separator 까지 보여준다. 봇이 보낸 화면을 확인할 때 쓴다.
- 토큰은 `.env` 에서 읽는다 — `.mcp.json` 에 적지 말 것(그 파일은 커밋된다).
- 봇이 초대된 서버만 보인다. 유저 토큰(셀프봇)은 디스코드 ToS 위반이라 쓰지 않는다.

## 진입점
`main.py` (봇) · `dashboard/backend/app.py` · `dashboard/frontend/src/main.tsx` · `webpanel/backend/app.py`

## 자세한 정보 (auto-memory)
- 맥미니 배포 좌표 (서비스·포트·함정): `reference_debi_marlene_macmini_deploy`
- 인프라 (GCS/Firestore/Modal): `reference_debi_marlene_infra`
- 포트 전체 표: `reference_debi_marlene_ports`
- 도메인: `reference_debi_marlene_domains`
- 기술 스택 + 레거시 잔해 식별: `reference_debi_marlene_tech_stack`
- 배포 함정: `reference_debi_marlene_deploy_traps`
