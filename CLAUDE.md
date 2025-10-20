# Debi Marlene 프로젝트 가이드

## 🚨 중요: 배포 환경

이 프로젝트는 **Google Cloud Platform**을 사용합니다:
- **Google Cloud Storage (GCS)**: 설정 파일 영구 저장 (`debi-marlene-settings` 버킷)
- **Google Cloud Run**: 봇 및 웹패널 컨테이너 실행
- **Google Container Registry (GCR)**: Docker 이미지 저장

## 프로젝트 구조

### 주요 디렉토리
- `/run`: 봇 코어 모듈
- `/webpanel`: 웹 대시보드 (React + Flask)
- `/assets`: 정적 리소스

### 주요 파일
- `main.py`: 봇 메인 엔트리
- `Dockerfile`: 봇 Docker 이미지 빌드 파일
- `webpanel/web_panel.py`: 웹패널 Flask 앱
- `webpanel/Dockerfile`: 웹패널 Docker 이미지 빌드 파일
- `run/config.py`: GCS 연동 설정 관리

## 배포 프로세스

### 1. 봇 배포 (Discord Bot)

#### Docker 이미지 빌드
```bash
cd /Users/kasa/Desktop/모묘모/debi-marlene

# Docker 이미지 빌드
docker build --no-cache --platform linux/amd64 -f Dockerfile -t gcr.io/[PROJECT_ID]/debi-marlene-bot:v[VERSION] .
```

#### GCR에 푸시
```bash
# GCloud 인증 (최초 1회)
gcloud auth configure-docker

# 이미지 푸시
docker push gcr.io/[PROJECT_ID]/debi-marlene-bot:v[VERSION]
```

#### Cloud Run 배포
```bash
gcloud run deploy debi-marlene-bot \
  --image gcr.io/[PROJECT_ID]/debi-marlene-bot:v[VERSION] \
  --platform managed \
  --region asia-northeast3 \
  --set-env-vars DISCORD_TOKEN=[TOKEN],YOUTUBE_API_KEY=[KEY] \
  --memory 512Mi \
  --cpu 1
```

### 2. 웹패널 배포 (Web Panel)

#### Docker 빌드 시 주의사항
1. **Dockerfile 경로**: 빌드 컨텍스트는 프로젝트 루트에서 실행
   - `COPY webpanel/requirements.txt .` (✅ 올바른 경로)
   - `COPY requirements.txt .` (❌ 틀린 경로)

2. **필수 Python 패키지**: `webpanel/requirements.txt`
   ```
   Flask==3.0.0
   Flask-CORS==4.0.0
   python-dotenv==1.0.0
   requests==2.31.0
   Werkzeug==3.0.1
   psutil==5.9.6
   pytz==2024.1
   flask-session==0.5.0
   google-cloud-storage==2.10.0  # GCS 연동 필수
   discord.py==2.3.2
   ```

#### Docker 이미지 빌드
```bash
cd /Users/kasa/Desktop/모묘모/debi-marlene

# Docker 이미지 빌드
docker build --no-cache --platform linux/amd64 -f webpanel/Dockerfile -t gcr.io/[PROJECT_ID]/debi-marlene-webpanel:v[VERSION] .
```

#### GCR에 푸시 및 배포
```bash
# 이미지 푸시
docker push gcr.io/[PROJECT_ID]/debi-marlene-webpanel:v[VERSION]

# Cloud Run 배포
gcloud run deploy debi-marlene-webpanel \
  --image gcr.io/[PROJECT_ID]/debi-marlene-webpanel:v[VERSION] \
  --platform managed \
  --region asia-northeast3 \
  --port 8080 \
  --set-env-vars DISCORD_BOT_TOKEN=[TOKEN],DISCORD_CLIENT_ID=[ID],DISCORD_CLIENT_SECRET=[SECRET] \
  --memory 512Mi \
  --cpu 1 \
  --allow-unauthenticated
```

### 배포 후 확인사항

1. **Cloud Run 서비스 상태 확인**
   ```bash
   gcloud run services list
   gcloud run services describe debi-marlene-bot --region asia-northeast3
   gcloud run services describe debi-marlene-webpanel --region asia-northeast3
   ```

2. **로그 확인**
   ```bash
   # 봇 로그
   gcloud run logs read debi-marlene-bot --region asia-northeast3 --limit 50

   # 웹패널 로그
   gcloud run logs read debi-marlene-webpanel --region asia-northeast3 --limit 50
   ```

3. **GCS 버킷 확인**
   ```bash
   # settings.json 확인
   gsutil cat gs://debi-marlene-settings/settings.json

   # 버킷 권한 확인
   gsutil iam get gs://debi-marlene-settings
   ```

## GCS (Google Cloud Storage) 설정

### 로컬 개발 환경
```bash
# GCS 인증 (서비스 계정 키 사용)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# 또는 gcloud 인증
gcloud auth application-default login
```

### 프로덕션 환경
- Cloud Run은 자동으로 IAM 권한을 통해 GCS 접근
- 별도 인증 설정 불필요

### GCS 버킷 구조
```
debi-marlene-settings/
├── settings.json          # 메인 설정 파일 (서버, 사용자, DM 채널)
└── chat_logs/
    └── guilds/
        └── guild_[ID].json  # 서버별 채팅 로그
```

## 자주 발생하는 문제와 해결방법

### 1. ModuleNotFoundError: No module named 'google.cloud.storage'
- **원인**: google-cloud-storage 패키지가 설치되지 않음
- **해결**:
  ```bash
  pip install google-cloud-storage
  # 또는
  pip install --break-system-packages google-cloud-storage  # macOS의 경우
  ```

### 2. GCS 인증 실패 (403 Forbidden)
- **원인**: 서비스 계정 키 또는 IAM 권한 문제
- **해결**:
  1. 로컬: `GOOGLE_APPLICATION_CREDENTIALS` 환경변수 확인
  2. Cloud Run: 서비스 계정에 Storage Object Admin 권한 부여
  ```bash
  gcloud projects add-iam-policy-binding [PROJECT_ID] \
    --member="serviceAccount:[SERVICE_ACCOUNT]@[PROJECT_ID].iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
  ```

### 3. DM 채널이 웹패널에 표시되지 않음
- **원인**: DM 채널 정보가 GCS에 저장되지 않음
- **해결**:
  1. 봇에게 DM 메시지 전송 → 자동으로 GCS에 채널 ID 저장됨
  2. GCS settings.json의 `users` 섹션에 `dm_channel_id` 확인
  3. 웹패널 DM 목록 자동 새로고침 (10초마다)

### 4. 배포 후에도 변경사항이 반영되지 않음
- **원인**: Docker 이미지 캐시 또는 Cloud Run 리비전 문제
- **해결**:
  1. `--no-cache` 옵션으로 이미지 다시 빌드
  2. Cloud Run 새 리비전 강제 배포:
  ```bash
  gcloud run services update-traffic debi-marlene-bot --to-latest
  ```

## 웹패널 기능

### 1. 대시보드 기능
- 서버 통계, 봇 사용자 정보 표시
- GCS에서 `settings.json` 실시간 로드
- 실시간 시스템 리소스 모니터링

### 2. Discord 연동
- Discord OAuth2 로그인 (OWNER_ID만 접근 가능)
- 실시간 서버 목록, 채널 목록 표시
- DM 채팅 인터페이스 (3초마다 자동 새로고침)
- DM 목록 자동 업데이트 (10초마다)

### 3. Discord Gateway 실시간 연결
- discord.py Gateway를 통한 실시간 이벤트 수신
- DM 수신 시 자동으로 GCS에 채널 정보 저장
- 서버 멤버 수, 온라인 상태 실시간 업데이트

## 최근 수정사항

### 2025-10-15 (2): Electron 앱 스플래시 스크린 및 UI 개선

1. **Discord 스타일 스플래시 스크린 추가**
   - 파일: `webpanel/splash.html` (신규 생성)
   - 회전하는 로고 애니메이션 (360° 연속 회전)
   - 상하로 움직이는 플로팅 애니메이션
   - "Debi Marlene" 텍스트 펄스 효과
   - 3개의 점이 순차적으로 튀는 로딩 애니메이션
   - 앱 테마와 일치하는 다크 그라디언트 배경

2. **Electron 메인 프로세스 수정**
   - 파일: `webpanel/electron/main.cjs`
   - `createSplashWindow()` 함수 추가: 프레임 없는 투명한 스플래시 윈도우
   - 앱 시작 시 스플래시 윈도우 먼저 표시
   - Flask 백엔드 로딩 완료 후 메인 윈도우 생성
   - 메인 윈도우 로딩 완료 시 스플래시 자동 닫기

3. **UI 이모지 제거**
   - 파일: `webpanel/src/components/ChannelList.tsx`
   - 파일: `webpanel/src/components/MessageArea.tsx`
   - "서버를 선택해주세요" 및 "채널을 선택해주세요" 텍스트에서 이모지 제거
   - 콘솔 로그에서도 이모지 제거

4. **패키징 설정 업데이트**
   - 파일: `webpanel/package.json`
   - `splash.html`과 `build/icon.png`를 files 배열에 추가
   - asarUnpack 배열에도 추가하여 프로덕션 빌드에 포함

5. **상태 지속성 구현** (이전 작업)
   - localStorage를 사용하여 서버/채널 선택 상태 저장
   - 앱 재시작 시 마지막 선택한 서버/채널 자동 복원
   - 자동 메시지 새로고침 제거 (스크롤 이슈 해결)

### 2025-10-15 (1): 채팅 로그 제거 및 DM 채널 양방향 저장

1. **채팅 로그 저장 기능 제거 (GCS Rate Limit 방지)**
   - 파일: `run/discord_bot.py:1550`
   - 파일: `run/config.py` (save_chat_log, fetch_old_messages_for_guild 함수 제거)
   - 원인: GCS Rate Limit (1초당 1번 쓰기 제한) 초과로 429 에러 발생
   - 해결: 채팅 로그 기능 완전 제거, settings.json만 업데이트

2. **유튜브 알림 시 DM 채널 자동 저장**
   - 파일: `run/youtube_service.py:75-131` (_send_notification 함수)
   - 봇이 유저에게 DM을 보낼 때 (유튜브 알림 등) 채널 정보를 자동으로 GCS에 저장
   - 기존: 유저 → 봇 DM만 저장됨
   - 수정 후: 봇 → 유저 DM도 저장됨 (양방향 저장)
   - 저장 실패 시에도 메시지는 정상 전송됨

3. **배포 방법 개선**
   - VM에서 직접 빌드 후 Artifact Registry에 푸시
   - 로컬에서 빌드 시 업로드 속도 느림 → VM 빌드로 해결
   - 명령어 예시:
     ```bash
     # VM에 소스 업로드
     tar -czf /tmp/debi-marlene-code.tar.gz --exclude=node_modules --exclude=.git .
     gcloud compute scp /tmp/debi-marlene-code.tar.gz debi-marlene-bot:~/build/ --zone=asia-northeast3-a

     # VM에서 빌드
     gcloud compute ssh debi-marlene-bot --zone=asia-northeast3-a --command="cd ~/build && docker build --platform linux/amd64 -f Dockerfile -t asia-northeast3-docker.pkg.dev/[PROJECT_ID]/debi-marlene/bot:gcs-v2 ."
     ```

### 2025-10-14: DM 채널 자동 저장 기능 추가

1. **봇 DM 메시지 이벤트 핸들러 수정**
   - 파일: `run/discord_bot.py:1331-1381`
   - DM 메시지 수신 시 자동으로 채널 ID를 GCS에 저장
   - `users` 섹션에 `dm_channel_id`, `user_name`, `last_dm` 저장

2. **웹패널 Gateway 서비스**
   - 파일: `webpanel/discord_gateway_service.py`
   - DM 채널 목록 가져오기 시 GCS에 자동 저장
   - Gateway private_channels 및 GCS 데이터 병합

3. **작동 방식**
   - 사용자가 봇에게 DM 전송 → 봇이 자동으로 채널 정보 GCS 저장
   - 웹패널에서 DM 목록 로드 → GCS에서 채널 정보 가져와서 표시
   - 10초마다 자동 새로고침으로 최신 DM 목록 유지

### 2025-10-06 (2): 봇 프로필 동적 로딩 기능 추가

1. **봇 프로필 API 엔드포인트 추가**
   - `/api/bot-info` (GET) 엔드포인트
   - Discord API `/users/@me`에서 봇 정보 가져오기
   - 파일: `webpanel/web_panel.py`

2. **프론트엔드 봇 프로필 동적 로딩**
   - 컴포넌트 마운트 시 봇 정보 자동 로드
   - 봇 프로필 사진, 이름, 태그 동적 표시
   - 파일: `webpanel/src/components/DiscordApp.tsx`

### 2025-10-06 (1): GCS 설정 뷰어 기능 추가

1. **GCS 설정 모달**
   - 웹패널에서 GCS settings.json 실시간 확인
   - `/api/load-settings` 엔드포인트 추가

2. **CORS 설정**
   - Vite 개발 서버 포트 지원 (5179, 5180)

## 로컬 개발 환경

### 필수 설치 패키지
```bash
# Python 패키지
pip install --break-system-packages google-cloud-storage discord.py Flask Flask-CORS

# Node.js (웹패널 프론트엔드)
cd webpanel
npm install
```

### 실행 방법
```bash
# 봇 실행
python main.py

# 웹패널 실행
cd webpanel
python3 web_panel.py  # Flask 서버 (포트 8080)
npm run dev           # Vite 개발 서버 (포트 5173)

# Electron 앱 실행 (선택)
npm run electron:dev
```

## 향후 개발 계획 (v1.1+)

### 봇 기능
1. **모바일 앱 개발**
   - iOS/Android 네이티브 앱 또는 React Native 앱
   - 봇 관리 및 모니터링 기능
   - 푸시 알림 지원

2. **AI 대화 기능**
   - GPT/Claude API 연동
   - 자연어 처리 기반 대화형 봇
   - 컨텍스트 기억 및 학습 기능

3. **전적 분석 기능**
   - 게임 전적 조회 (LoL, Valorant 등)
   - 통계 시각화 및 분석
   - 랭킹 추적 기능

### 웹패널 기능
1. **서버 목록 폴더 기능**
   - 서버를 폴더로 그룹화
   - 폴더 생성/삭제/이름 변경
   - 서버 드래그 앤 드롭으로 폴더 간 이동
   - 폴더 접기/펼치기 기능

2. **서버/채널 위치 바꾸기 기능**
   - 드래그 앤 드롭으로 서버 순서 변경
   - 채널 순서 커스터마이징
   - 변경사항 로컬 저장 (localStorage)

3. **사용자 상태창 구현**
   - 사용자 클릭 시 디스코드 스타일 프로필 모달
   - 실시간 온라인/오프라인/자리비움/다른 용무중 상태 표시
   - 사용자 정보 (프로필 사진, 배너, 소개, 역할)
   - DM 보내기, 프로필 보기 등 액션 버튼
   - 서버 내 역할 및 권한 표시
   - 멤버 가입 날짜, 서버 참여 날짜

## 연락처
문제 발생 시 봇 소유자에게 문의
