# 데비&마를렌 Discord 봇

이터널리턴(Eternal Return) 데비&마를렌 테마 Discord 봇입니다. Google Cloud Platform(GCP)에서 실행되며 웹 관리 패널(웹/데스크톱)을 통해 관리할 수 있습니다.

## 🎯 주요 기능

### Discord 봇 기능
- **자동 알림**: 이터널리턴 공식 YouTube 자동 알림 (5분마다 체크)
- **전적 검색**: `/전적` 명령어로 실험체, 통계(MMR 그래프) 조회
- **서버 관리**: 공지 채널 설정, 유튜브 알림 구독 관리
- **AI 대화**: 데비와 마를렌 캐릭터 페르소나 기반 대화 기능
- **DM 채널 자동 생성**: 봇과 상호작용한 유저의 DM 채널 자동 저장

### 웹 관리 패널 (React + Flask)
- **실시간 대시보드**: 봇 상태, 서버 수, 사용자 통계 모니터링
- **Discord 스타일 UI**: 실제 Discord와 동일한 인터페이스
- **DM 채팅 인터페이스**: 웹에서 직접 Discord DM 주고받기
- **서버/채널 관리**: 봇이 참여한 서버 및 채널 목록
- **실시간 Gateway 연결**: Discord Gateway를 통한 실시간 이벤트 수신
- **GCS 설정 뷰어**: Google Cloud Storage에 저장된 설정 파일 실시간 조회
- **Electron 데스크톱 앱**: 웹패널을 데스크톱 앱으로 실행 가능

## 🏗️ 아키텍처

### 시스템 구성
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │    │   Web Panel     │    │  Google Cloud   │
│  (Cloud Run)    │◄──►│  (Cloud Run)    │◄──►│   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Cloud Logging   │    │  Electron App   │    │ Secret Manager  │
│ (로그 수집)      │    │ (Desktop Panel) │    │ (환경 변수)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 주요 컴포넌트
- **Discord Bot**: Python 기반, Cloud Run에서 컨테이너로 실행
- **Web Panel**: React + Flask, Discord Gateway 실시간 연결
- **Electron App**: 웹패널의 데스크톱 버전 (macOS/Windows)
- **Google Cloud Run**: 서버리스 컨테이너 실행 환경
- **Google Cloud Storage (GCS)**: 봇 설정 및 DM 채널 정보 저장
- **Google Container Registry (GCR)**: Docker 이미지 저장소
- **Cloud Logging**: 로그 수집 및 모니터링

## 🚀 배포 및 운영

### Cloud Run 서비스
1. **debi-marlene-bot**: Discord 봇 메인 서비스
2. **debi-marlene-webpanel**: 웹 관리 패널 서비스

### Docker 이미지 빌드 및 배포
```bash
# 봇 이미지 빌드
cd /Users/kasa/Desktop/모묘모/debi-marlene
docker build --no-cache --platform linux/amd64 -f Dockerfile -t gcr.io/[PROJECT_ID]/debi-marlene-bot:v1 .

# GCR에 푸시
docker push gcr.io/[PROJECT_ID]/debi-marlene-bot:v1

# Cloud Run 배포
gcloud run deploy debi-marlene-bot \
  --image gcr.io/[PROJECT_ID]/debi-marlene-bot:v1 \
  --platform managed \
  --region asia-northeast3 \
  --set-env-vars DISCORD_TOKEN=[TOKEN],YOUTUBE_API_KEY=[KEY] \
  --memory 512Mi \
  --cpu 1
```

### 웹패널 배포
```bash
# 웹패널 이미지 빌드
docker build --no-cache --platform linux/amd64 -f webpanel/Dockerfile -t gcr.io/[PROJECT_ID]/debi-marlene-webpanel:v1 .

# GCR에 푸시
docker push gcr.io/[PROJECT_ID]/debi-marlene-webpanel:v1

# Cloud Run 배포
gcloud run deploy debi-marlene-webpanel \
  --image gcr.io/[PROJECT_ID]/debi-marlene-webpanel:v1 \
  --platform managed \
  --region asia-northeast3 \
  --port 8080 \
  --set-env-vars DISCORD_BOT_TOKEN=[TOKEN],DISCORD_CLIENT_ID=[ID],DISCORD_CLIENT_SECRET=[SECRET] \
  --memory 512Mi \
  --cpu 1 \
  --allow-unauthenticated
```

### 환경 변수 (Cloud Run Environment Variables)
```
DISCORD_TOKEN: Discord 봇 토큰
CLAUDE_API_KEY: Anthropic Claude API 키
YOUTUBE_API_KEY: YouTube Data API 키
EternalReturn_API_KEY: 이터널리턴 API 키
OWNER_ID: 봇 소유자 Discord ID
DISCORD_CLIENT_ID: Discord OAuth 클라이언트 ID
DISCORD_CLIENT_SECRET: Discord OAuth 클라이언트 시크릿
DISCORD_REDIRECT_URI: OAuth 리다이렉트 URI
GOOGLE_APPLICATION_CREDENTIALS: GCS 서비스 계정 키 경로 (로컬 개발용)
```

## 🛠️ 개발 환경 설정

### 로컬 개발
```bash
# 저장소 클론
git clone <repository-url>
cd debi-marlene

# Python 의존성 설치
pip install --break-system-packages google-cloud-storage discord.py Flask Flask-CORS

# 환경 변수 설정
cp .env.example .env
# .env 파일에 필요한 API 키들 입력

# 봇 실행
python3 main.py

# 웹패널 실행 (별도 터미널)
cd webpanel
python3 web_panel.py      # Flask 서버 (포트 8080)
npm run dev               # Vite 개발 서버 (포트 5173)

# Electron 데스크톱 앱 실행
npm run electron:dev
```

### GCS 인증 설정
```bash
# 로컬 개발 환경
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# 또는 gcloud CLI 인증
gcloud auth application-default login

# GCS 버킷 확인
gsutil ls gs://debi-marlene-settings/
gsutil cat gs://debi-marlene-settings/settings.json
```

## 📁 프로젝트 구조

```
debi-marlene/
├── main.py                     # 봇 메인 실행 파일
├── run/                        # 봇 핵심 모듈
│   ├── discord_bot.py          # Discord 봇 로직, Gateway 연동
│   ├── youtube_service.py      # YouTube API 연동, 알림 전송
│   ├── config.py               # GCS 설정 관리, DM 채널 저장
│   ├── api_clients.py          # 이터널리턴 API 클라이언트
│   ├── graph_generator.py      # MMR 그래프 생성
│   └── recent_games_image_generator.py  # 최근 전적 이미지
├── webpanel/                   # 웹 관리 패널 (React + Flask)
│   ├── web_panel.py            # Flask 백엔드 API
│   ├── discord_gateway_service.py  # Discord Gateway 서비스
│   ├── src/                    # React 프론트엔드
│   │   ├── components/         # UI 컴포넌트
│   │   │   ├── DiscordApp.tsx  # 메인 Discord UI
│   │   │   ├── ServerList.tsx  # 서버 목록
│   │   │   ├── ChannelList.tsx # 채널 목록
│   │   │   └── MessageArea.tsx # 메시지 영역
│   │   └── App.tsx             # React 메인
│   ├── electron/               # Electron 데스크톱 앱
│   │   └── main.cjs            # Electron 메인 프로세스
│   ├── splash.html             # 스플래시 스크린
│   ├── package.json            # Node.js 의존성
│   ├── requirements.txt        # Python 의존성
│   ├── Dockerfile              # 웹패널 Docker 이미지
│   └── run/                    # 심볼릭 링크 (봇 모듈)
├── assets/                     # 이미지 및 정적 자원
├── requirements.txt            # 봇 Python 의존성
├── Dockerfile                  # 봇 Docker 이미지
├── CLAUDE.md                   # 프로젝트 가이드 (개발자용)
└── README.md                   # 프로젝트 문서
```

## 🔧 최근 업데이트

### 2025-10-20
- ✅ **Duet AI 구독 취소**: Google Cloud Duet AI 비활성화로 비용 절감
- ✅ **DM 채널 자동 생성**: `get_interaction_users()` 함수에서 자동으로 DM 채널 생성 및 GCS 저장

### 2025-10-15 (2)
- ✅ **Electron 스플래시 스크린**: Discord 스타일 로딩 애니메이션 추가
- ✅ **UI 이모지 제거**: 웹패널에서 불필요한 이모지 제거
- ✅ **상태 지속성**: localStorage를 사용한 서버/채널 선택 상태 저장

### 2025-10-15 (1)
- ✅ **GCS Rate Limit 해결**: 채팅 로그 저장 기능 제거
- ✅ **양방향 DM 저장**: 봇 → 유저 DM도 자동으로 GCS에 저장

### 2025-10-14
- ✅ **DM 채널 자동 저장**: DM 메시지 수신 시 자동으로 채널 정보 GCS 저장
- ✅ **웹패널 Gateway 서비스**: Discord Gateway 실시간 연결

### 2025-10-06 (2)
- ✅ **봇 프로필 동적 로딩**: `/api/bot-info` 엔드포인트 추가

### 2025-10-06 (1)
- ✅ **GCS 설정 뷰어**: 웹패널에서 GCS settings.json 실시간 확인

## 🐛 트러블슈팅

### 자주 발생하는 문제들

1. **ModuleNotFoundError: No module named 'google.cloud.storage'**
   ```bash
   pip install google-cloud-storage
   # 또는
   pip install --break-system-packages google-cloud-storage  # macOS
   ```

2. **GCS 인증 실패 (403 Forbidden)**
   ```bash
   # 로컬: 환경변수 설정
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

   # Cloud Run: IAM 권한 부여
   gcloud projects add-iam-policy-binding [PROJECT_ID] \
     --member="serviceAccount:[SERVICE_ACCOUNT]@[PROJECT_ID].iam.gserviceaccount.com" \
     --role="roles/storage.objectAdmin"
   ```

3. **DM 채널이 웹패널에 표시되지 않음**
   - 봇에게 DM 메시지 전송 → 자동으로 GCS에 저장됨
   - GCS `settings.json`의 `users` 섹션에 `dm_channel_id` 확인
   - 웹패널 DM 목록 자동 새로고침 (10초마다)

4. **배포 후 변경사항 미반영**
   ```bash
   # Docker 이미지 캐시 없이 재빌드
   docker build --no-cache --platform linux/amd64 -f Dockerfile -t gcr.io/[PROJECT_ID]/bot:v2 .

   # Cloud Run 최신 리비전으로 트래픽 전환
   gcloud run services update-traffic debi-marlene-bot --to-latest
   ```

### 모니터링 명령어

```bash
# Cloud Run 서비스 상태 확인
gcloud run services list
gcloud run services describe debi-marlene-bot --region asia-northeast3

# 로그 확인
gcloud run services logs read debi-marlene-bot --region=asia-northeast3 --limit=50
gcloud run services logs tail debi-marlene-bot --region=asia-northeast3  # 실시간

# GCS 설정 확인
gsutil cat gs://debi-marlene-settings/settings.json
```

## 🌐 배포 환경

- **클라우드 플랫폼**: Google Cloud Platform (GCP)
- **컨테이너 실행**: Cloud Run (서버리스)
- **스토리지**: Cloud Storage (`debi-marlene-settings` 버킷)
- **이미지 저장소**: Google Container Registry (GCR)
- **로깅**: Cloud Logging
- **리전**: asia-northeast3 (서울)

## 📞 지원

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discord**: 봇 관련 문의 및 지원
- **웹 패널**: 실시간 모니터링 및 관리

## 🎮 향후 개발 계획 (v1.1+)

### 봇 기능
- 모바일 앱 개발 (iOS/Android)
- AI 대화 기능 강화 (GPT/Claude API)
- 전적 분석 기능 (게임별 통계)

### 웹패널 기능
- 서버 목록 폴더 기능
- 서버/채널 위치 바꾸기 (드래그 앤 드롭)
- 사용자 상태창 구현 (프로필, 역할, 상태)
- 웹 터미널 기능 (실시간 로그 스트리밍)

---

> 이 봇은 이터널리턴의 데비&마를렌 캐릭터를 테마로 제작되었습니다. 🎮✨
