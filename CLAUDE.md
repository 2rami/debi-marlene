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

  💡 장점:

  1. 기능별로 분리 - 찾기 쉬움
  2. Discord 명령어 → commands/ 폴더에 모임
  3. UI 컴포넌트 → views/ 폴더에 모임
  4. 이터널리턴 관련 → services/eternal_return/에 모임
  5. 확장 쉬움 - 새 기능 추가할 때 어디 넣을지 명확


## 배포 방법 (VM에서 Docker 실행)

봇은 GCP VM(debi-marlene-bot)에서 Docker 컨테이너로 실행됩니다.

### .dockerignore 설정
- **webpanel/** 폴더가 제외 설정됨
- Docker 이미지 빌드 시 webpanel은 자동으로 제외됩니다

### 배포 절차

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

## 주요 변경사항

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
