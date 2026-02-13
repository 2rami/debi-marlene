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
  backend/              # Flask API (VM port 8080), Discord API 연동
  src/                  # React 프론트엔드 (로컬 port 5173)
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
- **TTS**: Modal Serverless + Qwen3-TTS-0.6B (파인튜닝 모델, T4 GPU)
- **대시보드**: Flask + React 19 + TypeScript + Vite + Tailwind 4
- **웹패널**: Flask (VM 8080) + React
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
- **Modal TTS**: `2R4mi/qwen3-tts-debi-light` (0.6B), `2R4mi/qwen3-tts-marlene` (1.7B)

### 포트 할당

| 서비스 | VM 포트 | 로컬 개발 포트 | 설명 |
|--------|---------|----------------|------|
| 봇 (Discord) | - | - | 포트 노출 없음 |
| 봇 내부 API | 5001 | 5001 | (사용 안 함, 레거시) |
| Dashboard Backend | 8081 | 8081 | Discord OAuth2 인증 |
| Dashboard Frontend | 3080 (nginx) | 3002 | React UI |
| Webpanel Backend | 8080 | 8080 | Discord API 연동 |
| Webpanel Frontend | (번들됨) | 5173 | React 개발 서버 |
| Modal TTS API | - | - | Serverless (외부 URL) |

**포트 충돌 방지:**
- 봇 컨테이너는 5001만 바인딩 (8080 제거됨)
- webpanel-backend가 8080 사용
- 봇과 webpanel은 동시 실행 가능

## GCS 인증

```bash
# 로컬
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
# 또는
gcloud auth application-default login

# 확인
gsutil cat gs://debi-marlene-settings/settings.json
```
