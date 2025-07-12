# 데비&마를렌 Discord 봇 (Python 버전) 🎮

이터널리턴 스파클링 트윈즈 데비&마를렌 테마 Discord 봇의 Python 버전입니다.

## ✨ 주요 기능

### 🤖 AI 캐릭터 대화
- **데비**: 밝고 활발한 성격으로 전적검색 담당
- **마를렌**: 차갑고 도도한 성격으로 정보제공 담당
- 실제 인게임 대사를 학습한 Claude AI 기반

### 🎬 자동 알림
- 이터널리턴 공식 YouTube 쇼츠 자동 알림 (5분마다 체크)

### 🎯 게임 관련 기능
- `!전적 [닉네임]` - 전적 검색
- `!랭킹` - 현재 랭킹 정보
- `!캐릭터 [이름]` - 캐릭터 정보
- `!안녕`, `!테스트` - 캐릭터와 대화
- `![아무거나]` - AI가 이터널리턴 관련으로 응답

## 🐳 Docker로 실행하기 (권장)

### 방법 1: docker-compose 사용

```bash
# 1. 환경 변수 파일 설정
cp env .env
# .env 파일을 편집하여 실제 토큰들로 변경

# 2. Docker 컨테이너 빌드 및 실행
docker-compose up -d

# 3. 로그 확인
docker-compose logs -f

# 4. 봇 중지
docker-compose down
```

### 방법 2: Docker 직접 사용

```bash
# 1. Docker 이미지 빌드
docker build -t debi-marlene-bot .

# 2. 컨테이너 실행
docker run -d \
  --name debi-marlene-bot \
  --env-file .env \
  -v $(pwd)/assets:/app/assets:ro \
  debi-marlene-bot

# 3. 로그 확인
docker logs -f debi-marlene-bot

# 4. 봇 중지
docker stop debi-marlene-bot
docker rm debi-marlene-bot
```



  # 처음 시작할 때
  make dev

  # 코드 수정 후 업데이트
  make update

  # 단순히 재시작만 하고 싶을 때
  make restart

  # 로그만 보고 싶을 때
  make logs

## 💻 로컬에서 실행하기

```bash
# 1. Python 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정 (.env 파일 생성)
cp env .env
# .env 파일 편집

# 3. 봇 실행
python main.py
```

## 🔧 환경 변수 설정

`env` 파일에 다음 내용을 설정하세요:

```bash
# Discord 봇 토큰 (필수)
DISCORD_TOKEN=your_discord_bot_token_here

# Claude AI API 키 (선택사항 - AI 응답 기능용)
CLAUDE_API_KEY=your_claude_api_key_here

# YouTube Data API 키 (선택사항 - YouTube 알림 기능용)
YOUTUBE_API_KEY=your_youtube_api_key_here
```

## 🔑 API 키 발급 방법

### Discord Bot Token
1. [Discord Developer Portal](https://discord.com/developers/applications) 접속
2. "New Application" → 봇 이름 입력
3. Bot 탭 → "Add Bot"
4. MESSAGE CONTENT INTENT 활성화
5. 토큰 복사

### Claude API Key
1. [Anthropic Console](https://console.anthropic.com) 접속
2. API Keys → Create Key
3. $5 무료 크레딧 제공

### YouTube API Key (선택사항)
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. YouTube Data API v3 활성화
3. API 키 생성

## 📁 프로젝트 구조

```
debi-marlene/
├── main.py              # 메인 Python 봇 코드
├── requirements.txt     # Python 의존성
├── Dockerfile          # Docker 이미지 설정
├── docker-compose.yml  # Docker Compose 설정
├── env                 # 환경 변수 템플릿
├── assets/             # 봇 이미지 파일들
│   ├── debi.png
│   ├── marlen.png
│   ├── background.png
│   └── ...
└── README.md           # 이 파일
```

## 🎮 슬래시 커맨드

| 명령어 | 설명 | 담당 캐릭터 |
|--------|------|------------|
| `/안녕` | 인사하기 | 데비 & 마를렌 |
| `/도움` | 도움말 표시 | 마를렌 |
| `/전적 [닉네임]` | 전적 검색 | 데비 |
| `/랭킹` | 랭킹 정보 | 마를렌 |
| `/캐릭터 [캐릭터명]` | 캐릭터 정보 | 마를렌 |
| `/설정 [설정내용]` | 봇 설정 | 마를렌 |
| `/테스트` | 봇 테스트 | 데비 & 마를렌 |
| `/유튜브 [검색어]` | 이터널리턴 관련 유튜브 영상 검색 | 데비 |
| `/대화 [메시지] [캐릭터]` | AI와 자유 대화 | 자동 선택 또는 지정 |
| 멘션 | 봇 멘션 시 응답 | 데비 |

## 🔧 문제 해결

### 봇이 시작되지 않는 경우
1. `.env` 파일의 `DISCORD_TOKEN`이 올바른지 확인
2. Docker 로그 확인: `docker-compose logs`
3. 봇이 Discord 서버에 초대되었는지 확인

### AI 응답이 작동하지 않는 경우
- `CLAUDE_API_KEY`가 설정되지 않았거나 잘못된 경우 기본 응답 패턴을 사용합니다
- Claude API 키가 유효한지 확인하세요

### YouTube 알림이 작동하지 않는 경우
- `YOUTUBE_API_KEY`가 설정되지 않은 경우 YouTube 기능이 비활성화됩니다
- YouTube Data API v3가 활성화되었는지 확인하세요

## 🔄 업데이트

봇 코드를 업데이트한 후:

```bash
# Docker Compose 사용시
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Docker 직접 사용시
docker stop debi-marlene-bot
docker rm debi-marlene-bot
docker build -t debi-marlene-bot .
# 그 후 다시 실행
```

## ⚠️ 주의사항

- API 키들은 절대 공개 저장소에 업로드하지 마세요
- Docker 컨테이너는 기본적으로 재시작 정책이 `unless-stopped`로 설정되어 있습니다
- 봇이 정상 작동하려면 Discord 서버에서 적절한 권한을 가져야 합니다

## 🎭 캐릭터 설정

### 데비 (언니, 파란색)
- **성격**: 쾌활하고 활발한 성격, 천진난만하고 적극적
- **담당**: 전적검색, 유튜브 알림
- **대사**: "각고 단단히 해!", "내가 할게!", "엄청 수상한 놈이 오는데!"

### 마를렌 (동생, 빨간색)
- **성격**: 차갑고 도도한 성격, 냉소적이고 현실적
- **담당**: 랭킹 정보, 캐릭터 정보
- **대사**: "Like hell you do.", "Hope it's not too cold."

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이센스

MIT License - 자세한 내용은 `LICENSE` 파일을 확인하세요.

## 🎮 관련 링크

- [이터널리턴 공식 사이트](https://eternalreturn.nimbleneuro.com/)
- [이터널리턴 공식 YouTube](https://www.youtube.com/@EternalReturnKR)
- [Discord.js 문서](https://discord.js.org/)
- [Claude API 문서](https://docs.anthropic.com/)

---

**Made with ❤️ for Eternal Return players**