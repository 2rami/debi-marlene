# 데비&마를렌 봇 🎮

이터널리턴의 스파클링 트윈즈 데비&마를렌을 테마로 한 Discord 봇입니다.

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

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/debi-marlene-bot.git
cd debi-marlene-bot
```

### 2. 의존성 설치
```bash
npm install
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
```

`.env` 파일을 열어서 다음 정보를 입력하세요:

- `DISCORD_TOKEN`: Discord 봇 토큰
- `CLAUDE_API_KEY`: Claude API 키
- `YOUTUBE_API_KEY`: YouTube Data API v3 키 (선택사항)

### 4. 봇 실행
```bash
npm start
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
debi-marlene-bot/
├── assets/           # 이미지 파일들
│   ├── debi.png     # 데비 캐릭터 이미지
│   └── marlen.png   # 마를렌 캐릭터 이미지
├── index.js          # 메인 봇 파일
├── package.json      # 프로젝트 설정
├── .env.example      # 환경 변수 템플릿
├── .gitignore        # Git 무시 파일
└── README.md         # 프로젝트 설명
```

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