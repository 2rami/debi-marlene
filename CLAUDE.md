 ## 코딩 규칙

  - 코드 수정 시 claude's question (선택하는거) 적극적으로 사용

 **중요: 이모지 사용 금지**
 - 코드에서 이모지(🎉, 📊, ✅, 🔴, 🟢 등) 절대 사용하지 말 것
 - Discord 임베드, 메시지, 로그 등 모든 곳에서 이모지 금지
 - 대신 텍스트나 기호 사용 (#1, [TOP], *, - 등)
 - 디버그 로그 추가하고 해결되면 삭제

## 역할 구분 원칙

### api_client (데이터 계층)
- 순수 데이터 추출/변환 로직
- Discord와 무관한 비즈니스 로직
- API 호출 및 응답 처리
- 데이터 캐싱 및 가공
- 예: extract_team_members_info, get_weather_image_url

### views (UI 계층)
- Discord embed 생성 및 포맷팅
- 사용자 인터랙션 처리 (버튼, 셀렉트)
- Discord 전용 표시 로직
- 예: format_teammate_info, create_game_embed

### 원칙
- 데이터 추출은 api_client
- UI 포맷팅은 views
- 명확한 책임 분리로 유지보수성 향상

## Claude Code 활용

### Agent 병렬 작업
- 독립적인 여러 작업을 동시에 처리 가능
- 예시:
  - 대규모 리팩토링: 여러 폴더 동시 정리
  - 코드 탐색 + 계획 수립 동시 진행
  - 독립적인 기능들 동시 구현
  - 테스트 + 문서화 동시 작업

### TODO 관리
- 복잡한 작업은 TodoWrite로 단계별 추적
- 각 작업의 진행 상태 관리

### 주의사항
- 순차적 의존성이 있는 작업은 병렬 불가
- 독립적인 작업만 병렬로 진행

  ## dak gg 사용가능한 api endpoint.md 많이 참고

## 뎁마봇 폴더 구조

run/
├── __init__.py
├── main.py                    # 봇 시작점 (간단하게)
│
├── core/                      # 핵심 기능
│   ├── __init__.py
│   ├── bot.py                # Discord 봇 인스턴스, 이벤트
│   └── config.py             # GCS 설정 (기존)
│
├── commands/                  # 슬래시 커맨드들
│   ├── __init__.py
│   ├── stats.py              # /전적 명령어
│   ├── character.py          # /통계 명령어
│   ├── settings.py           # /설정 명령어
│   ├── youtube.py            # /유튜브알림, /유튜브테스트
│   └── feedback.py           # /피드백 명령어
│
├── views/                     # Discord UI (버튼, 셀렉트 등)
│   ├── __init__.py
│   ├── stats_view.py         # StatsView (전적 UI)
│   ├── character_view.py     # CharacterStatsView
│   ├── welcome_view.py       # WelcomeView
│   └── settings_view.py      # SettingsView, ChannelSelectView
│
├── services/                  # 외부 서비스 연동
│   ├── __init__.py
│   ├── eternal_return/       # 이터널리턴 관련
│   │   ├── __init__.py
│   │   ├── api_client.py     # API 호출 (기존 api_clients.py)
│   │   ├── graph_generator.py # 그래프 (기존)
│   │   └── image_generator.py # 이미지 (기존 recent_games_image_generator.py)
│   └── youtube.py            # 유튜브 서비스 (기존)
│
└── utils/                     # 유틸리티
    ├── __init__.py
    ├── embeds.py             # Embed 생성 함수들
    └── gcs.py                # GCS 헬퍼 (필요시)


## 웹패널 폴더 구조

webpanel/
├── src/                             # 프론트엔드 (React/TypeScript)
│   ├── core/                        # 앱 진입점
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── components/                  # UI 컴포넌트
│   │   ├── layout/                  # 레이아웃 컴포넌트
│   │   │   ├── ServerList.tsx
│   │   │   ├── ChannelList.tsx
│   │   │   └── MemberList.tsx
│   │   ├── chat/                    # 채팅 관련
│   │   │   └── MessageArea.tsx
│   │   └── auth/                    # 인증 관련
│   │       └── Login.tsx
│   │
│   ├── services/                    # 프론트엔드 서비스
│   │   ├── discord-api.ts
│   │   ├── discord-oauth.ts
│   │   └── theme-service.ts
│   │
│   └── types/                       # TypeScript 타입
│       └── discord.ts
│
└── backend/                         # 백엔드 (Python/Flask)
    ├── __init__.py
    ├── app.py                      # Flask 앱 시작점 (메인 실행 파일)
    ├── config.py                   # 앱 설정 (CORS, 세션, OAuth, 환경변수)
    ├── gateway.py                  # Discord Gateway (기존 discord_gateway_webpanel.py)
    │
    ├── routes/                      # 라우트 정의 (URL → 핸들러 연결)
    │   ├── __init__.py
    │   ├── auth_routes.py          # /login, /auth/callback, /logout, /auth/discord
    │   ├── main_routes.py          # /, /version (메인 페이지)
    │   └── api_routes.py           # 모든 /api/* 라우트 등록
    │
    ├── api/                         # API 엔드포인트 핸들러 (비즈니스 로직)
    │   ├── __init__.py
    │   ├── auth.py                 # /api/check-auth, /api/logout
    │   ├── servers.py              # /api/servers, /api/bot-info
    │   ├── settings.py             # /api/raw-settings, /api/save-settings, /api/load-settings
    │   ├── channels.py             # /api/channels/<guild_id>
    │   ├── members.py              # /api/discord/guilds/<guild_id>/members
    │   ├── messages.py             # /api/discord/channels/<channel_id>/messages (GET/POST)
    │   └── users.py                # /api/discord/users/<user_id>, /api/discord/users/@me/channels
    │
    ├── services/                    # 비즈니스 로직 / 외부 서비스 연동
    │   ├── __init__.py
    │   └── discord_api.py          # Discord API 호출 함수들
    │                                # - get_bot_guilds()
    │                                # - get_discord_user_info()
    │                                # - get_discord_channels()
    │                                # - send_discord_message()
    │
    └── utils/                       # 유틸리티 / 헬퍼
        ├── __init__.py
        ├── decorators.py           # @login_required 데코레이터
        └── helpers.py              # get_discord_avatar_url() 등



## 배포 위치

봇은 GCP VM(debi-marlene-bot)에서 Docker 컨테이너로 실행됩니다.

### .dockerignore 설정
- **webpanel/** 폴더가 제외 설정됨
- Docker 이미지 빌드 시 webpanel은 자동으로 제외됩니다

### **중요 로컬 도커 오류 시 배포 방법(코드 수정했다고 바로 배포 금지!!! 로컬에서 사용자가 우선 테스트)

```bash
# 1. 로컬 코드를 VM에 업로드
gcloud compute scp --recurse . debi-marlene-bot:~/debi-marlene/ --zone=asia-northeast3-a

# 2. VM에서 Docker 이미지 빌드
gcloud compute ssh debi-marlene-bot --zone=asia-northeast3-a --command="cd ~/debi-marlene && docker build -t debi-marlene-bot ."

# 3. 기존 컨테이너 중지 및 제거
gcloud compute ssh debi-marlene-bot --zone=asia-northeast3-a --command="docker stop debi-marlene || true && docker rm debi-marlene || true"

# 4. 새 컨테이너 실행
gcloud compute ssh debi-marlene-bot --zone=asia-northeast3-a --command="docker run -d --name debi-marlene -p 5000:5000 -p 8080:8080 debi-marlene-bot"
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

3. **AI 전적 분석 기능**

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
