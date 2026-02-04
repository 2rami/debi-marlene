# Debi Marlene - Discord Bot

## 프로젝트 구조

```
run/                    # Discord 봇 메인 코드
  core/                 # bot.py, config.py (봇 초기화)
  cogs/                 # 이벤트 핸들러 (eternal_return, music, voice, welcome, stats, settings, utility, youtube)
  commands/             # 슬래시 커맨드 (character, feedback, music, online, recommend, settings, stats, voice, youtube)
  services/             # 비즈니스 로직 (eternal_return/, music/, tts/, welcome/, voice_manager.py, youtube_service.py)
  views/                # Discord embed/UI 포맷팅
  utils/                # 유틸리티
dashboard/
  backend/              # Flask API (port 8081), Discord OAuth2 인증
  frontend/             # React + Vite + Tailwind (port 3002)
webpanel/
  backend/              # Flask API (port 8080), Discord API 연동
  src/                  # Electron + React 프론트엔드 (port 5173)
```

## 진입점

| 파일 | 설명 |
|------|------|
| `main.py` | 봇 진입점 |
| `dashboard/backend/app.py` | 대시보드 API 서버 |
| `dashboard/frontend/src/main.tsx` | 대시보드 프론트엔드 |
| `webpanel/backend/app.py` | 웹패널 API 서버 |

## 기술 스택

- **봇**: Python, discord.py 2.6.4, anthropic (Claude AI), google-cloud-storage
- **TTS**: GPT-SoVITS API (port 9880, GPU 필요)
- **대시보드**: Flask + React 19 + TypeScript + Vite + Tailwind 4
- **결제**: TossPayments SDK
- **인프라**: GCP Compute Engine VM (asia-northeast3-a), Artifact Registry

## 로컬 개발

```bash
# 봇 실행 (VM 봇 자동 중지 후 로컬 실행)
make test-local

# 대시보드
cd dashboard/backend && python3 app.py          # backend (8081)
cd dashboard/frontend && npm run dev            # frontend (3002)

# 웹패널
cd webpanel && python3 backend/app.py           # backend (8080)
cd webpanel && npm run dev                      # frontend (5173)
```

## 배포

```bash
make deploy      # 전체: 빌드 + Registry Push + VM 재시작
make stop-vm     # VM 봇 중지 (로컬 테스트 전)
make start-vm    # VM 봇 시작 (로컬 테스트 후)
make logs        # 컨테이너 로그
make status      # VM/컨테이너 상태
```

**코드 수정했다고 바로 배포 금지. 로컬에서 사용자가 우선 테스트.**

## 코딩 규칙

**이모지 사용 금지**
- 코드, Discord 임베드, 메시지, 로그 등 모든 곳에서 이모지 금지
- 대신 텍스트나 기호 사용 (#1, [TOP], *, - 등)

**역할 분리**

| 계층 | 역할 | 예시 |
|------|------|------|
| `run/services/` (api_client) | 순수 데이터 추출/변환, API 호출 | `extract_team_members_info` |
| `run/views/` | Discord embed/UI 포맷팅 | `format_teammate_info` |

**기타**
- 디버그 로그 추가하고 해결되면 삭제
- `dak gg 사용가능한 api endpoint.md` 참고 (Eternal Return API)
- `.dockerignore`에 `webpanel/` 제외됨 (봇 이미지에 포함 안 됨)

## 인프라

- **VM**: `debi-marlene-bot` (GCP Compute Engine, asia-northeast3-a)
- **Registry**: `asia-northeast3-docker.pkg.dev/ironic-objectivist-465713-a6/debi-marlene`
- **Storage**: GCS `debi-marlene-settings` 버킷 (봇 설정/DM 채널 저장)
- **포트**: 봇 API 5001, 대시보드 8080, TTS API 9880

## GCS 인증

```bash
# 로컬
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
# 또는
gcloud auth application-default login

# 확인
gsutil cat gs://debi-marlene-settings/settings.json
```
