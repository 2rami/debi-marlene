# Debi Marlene - Discord Bot

## 프로젝트 구조

```
run/                    # Discord 봇 메인 코드
  core/                 # bot.py, config.py (봇 초기화)
  cogs/                 # 슬래시 커맨드 + 이벤트 핸들러 (eternal_return, music, voice, welcome, stats, quiz, utility, youtube)
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

## 코딩 규칙

**이모지 사용 금지**
- 코드, Discord 임베드, 메시지, 로그 등 모든 곳에서 이모지 금지
- 대신 텍스트나 기호 사용 (#1, [TOP], *, - 등)

**역할 분리**

| 계층 | 역할 | 예시 |
|------|------|------|
| `run/services/` (api_client) | 순수 데이터 추출/변환, API 호출 | `extract_team_members_info` |
| `run/views/` | Discord embed/UI 포맷팅 | `format_teammate_info` |

**Discord Components V2 (LayoutView) 규칙**
- LayoutView에서는 Embed 사용 불가 — Container가 Embed 대체
- `Container(accent_colour 없음)` → 깔끔한 테두리 박스 (기본 스타일)
- `Container(accent_colour=색상)` → 왼쪽 색상 줄 추가
- 정보 영역, 컨트롤 영역을 **별도 Container로 분리**해서 시각적 계층 구분
- Section의 Thumbnail(accessory)은 항상 오른쪽, 왼쪽 이미지는 커스텀 이모지로 대체
- 이모지를 크게 보이려면 헤딩(`##`) 안에 넣기

**기타**
- 디버그 로그 추가하고 해결되면 삭제
- `dak gg 사용가능한 api endpoint.md` 참고 (Eternal Return API)
- `.dockerignore`에 `webpanel/` 제외됨 (봇 이미지에 포함 안 됨)

## 인프라

- **VM**: `debi-marlene-bot` (GCP Compute Engine, asia-northeast3-a)
  - IP 확인: `gcloud compute instances describe debi-marlene-bot --zone=asia-northeast3-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'`
- **Registry**: Makefile의 `REGISTRY` 변수 참고
- **Storage**: GCS 버킷 (봇 설정/DM 채널 저장) — 버킷 이름은 `.env` 또는 Makefile 참고
- **Modal TTS**: Modal 앱 설정은 `.env` 참고

### 도메인

| 도메인 | 용도 |
|--------|------|
| `debimarlene.com` | 대시보드 (메인) |
| `panel.debimarlene.com` | 웹패널 |

### 포트 할당

| 서비스 | VM 포트 | 로컬 개발 포트 | 설명 |
|--------|---------|----------------|------|
| 봇 (Discord) | - | - | 포트 노출 없음 |
| Dashboard Backend | 8081 | 8081 | Discord OAuth2 인증 |
| Dashboard Frontend | 3080 (nginx) | 3002 | React UI |
| Webpanel Backend | 8080 | 8080 | Discord API 연동 |
| Webpanel Frontend | (번들됨) | 5173 | React 개발 서버 |

**포트 충돌 방지:**
- 봇 컨테이너는 5001만 바인딩 (8080 제거됨)
- webpanel-backend가 8080 사용
- 봇과 webpanel은 동시 실행 가능

## GCS 인증

```bash
# 로컬
gcloud auth application-default login

# 확인
gsutil cat gs://$(grep BUCKET .env | cut -d= -f2)/settings.json
```
