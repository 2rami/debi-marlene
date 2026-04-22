# Debi Marlene

## 안전 규칙
- `make deploy`는 파괴적 — 빌드 + Registry Push + VM 재시작. 명시적 승인 없이 실행 금지.
- 로컬 테스트 전 `make stop-vm` 필수 — VM/로컬 동시 연결 시 Discord 세션 충돌로 무한 재연결.
- git 브랜치는 main만. feature 브랜치 금지. (`archive/legacy-*` 는 백업용)
- 봇 컨테이너 5001 / webpanel 8080 / dashboard 8081 — 포트 충돌 주의.

## 자주 쓰는 명령
| 작업 | 명령 |
|---|---|
| 로컬 봇 (VM 자동 중지) | `make test-local` |
| VM 제어 | `make stop-vm` / `make start-vm` |
| 배포 (승인 필수) | `make deploy` |
| 로그/상태 | `make logs` / `make status` |
| 대시보드 dev | backend `python3 dashboard/backend/app.py` (8081) / frontend `npm run dev` in `dashboard/frontend` (3002) |
| 웹패널 dev | backend `python3 webpanel/backend/app.py` (8080) / frontend `npm run dev` in `webpanel` (5173) |
| env 내려받기 | `./scripts/sync_env.sh pull` (맥↔윈도우 새 환경 셋업 1회) |
| env 업로드 | `./scripts/sync_env.sh push` (로컬 수정 후 모든 기기 동기화) |
| 솔로봇 정리 | `./scripts/kill_solo_bots.sh all` (좀비 python까지 env 블록으로 정확히 kill) |

## env 관리 (중요)
- **단일 진실: Google Cloud Secret Manager**. 노션 평문 저장 폐기 권장.
- Secret 3종: `debi-marlene-env` / `debi-marlene-env-solo-debi` / `debi-marlene-env-solo-marlene`
- 새 기기 셋업: `gcloud auth login` → `gcloud config set project ironic-objectivist-465713-a6` → `./scripts/sync_env.sh pull`
- secret 업데이트: 로컬 `.env` 수정 → `./scripts/sync_env.sh push` → 팀 컨테이너 재시작

## 코딩 규칙
- **이모지 금지** — 코드/임베드/메시지/로그 모두. 대체: SVG 또는 텍스트 기호 (#1, [TOP], *, -)
- **계층 분리**: `run/services/` (데이터/API) ↔ `run/views/` (Discord 포맷팅)
- **LayoutView ≠ Embed** — Container가 Embed 대체. 세부 규칙은 `feedback_discord_v2_layout` 메모리.

## 진입점
`main.py` (봇) · `dashboard/backend/app.py` · `dashboard/frontend/src/main.tsx` · `webpanel/backend/app.py`

## 자세한 정보 (auto-memory)
- 인프라 (VM/Registry/GCS/Modal): `reference_debi_marlene_infra`
- 포트 전체 표: `reference_debi_marlene_ports`
- 도메인: `reference_debi_marlene_domains`
- 기술 스택 + 레거시 잔해 식별: `reference_debi_marlene_tech_stack`
- 배포 함정 (VM_PATH/msys2/env-file): `reference_debi_marlene_deploy_traps`
