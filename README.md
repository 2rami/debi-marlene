# 데비&마를렌 Discord 봇

이터널리턴(Eternal Return) 데비&마를렌 테마 Discord 봇입니다.

## 주요 기능

### 전적 검색
- `/이터널리턴 전적 <닉네임>` - 유저 전적 조회 (MMR, 티어, 승률)
- `/이터널리턴 통계 [티어] [기간]` - 캐릭터별 통계 조회 (승률, 픽률, 평균 순위)

### 음성 채널 (TTS)
- `/음성 입장` - 봇이 음성 채널에 입장
- `/음성 퇴장` - 봇이 음성 채널에서 퇴장
- `/음성설정 <채널>` - TTS 사용 채널 지정
- 데비/마를렌 캐릭터 목소리로 채팅을 읽어줌 (AI 음성 합성)

### 음악 재생
- `/음악 재생 <URL/검색어>` - YouTube 음악 재생
- `/음악 스킵` - 다음 곡으로 넘기기
- `/음악 정지` - 재생 중지

### 유튜브 알림
- 이터널리턴 공식 YouTube 새 영상 자동 알림 (5분마다 체크)
- `/유튜브 알림 <받기/안받기>` - 개인 DM 알림 설정
- `/설정` - [관리자] 서버 알림 채널 설정

### 기타
- `/피드백 <내용>` - 봇 개발자에게 피드백 전송

## 프로젝트 구조

```
debi-marlene/
├── main.py                      # 봇 실행 진입점
├── run/
│   ├── core/
│   │   ├── bot.py               # Discord 봇 로직
│   │   └── config.py            # GCS 설정 관리
│   ├── cogs/                    # 명령어 모듈
│   │   ├── eternal_return.py    # 전적/통계 명령어
│   │   ├── voice.py             # 음성 채널 (TTS)
│   │   ├── music.py             # 음악 재생
│   │   ├── youtube.py           # 유튜브 알림
│   │   ├── settings.py          # 서버 설정
│   │   └── utility.py           # 피드백 등
│   ├── services/
│   │   ├── eternal_return/      # 이터널리턴 API
│   │   │   ├── api_client.py    # Dak.gg API 클라이언트
│   │   │   └── graph_generator.py
│   │   ├── tts/                 # TTS 서비스
│   │   │   ├── tts_service.py   # TTS 엔진 추상화
│   │   │   ├── modal_tts_client.py
│   │   │   └── qwen3_tts_client.py
│   │   ├── music/               # 음악 재생
│   │   └── youtube_service.py   # 유튜브 알림
│   ├── utils/
│   │   ├── command_logger.py
│   │   ├── embeds.py
│   │   └── emoji_utils.py
│   └── views/                   # UI 컴포넌트
├── webpanel/                    # 웹 대시보드 (Electron)
├── requirements.txt
├── Dockerfile
└── CLAUDE.md                    # 개발/배포 가이드
```

## 로컬 개발

```bash
# 저장소 클론
git clone <repository-url>
cd debi-marlene

# Python 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 필요한 API 키들 입력

# 봇 실행
python3 main.py
```

### 필요한 환경 변수

```
DISCORD_TOKEN       # Discord 봇 토큰
YOUTUBE_API_KEY     # YouTube Data API 키
OWNER_ID            # 봇 소유자 Discord ID
TTS_ENGINE          # TTS 엔진 선택 (modal / qwen3_api / qwen3)
```

## 기술 스택

- **언어**: Python 3.11+
- **프레임워크**: discord.py
- **TTS**: Qwen3-TTS (커스텀 음성 모델)
- **API**: Dak.gg (전적), YouTube Data API
- **클라우드**: Google Cloud Platform (Cloud Run, Cloud Storage)

## 배포

GCP Cloud Run에 배포됩니다. 자세한 내용은 [CLAUDE.md](CLAUDE.md) 참고.

```bash
# Docker 빌드
docker build --platform linux/amd64 -t gcr.io/[PROJECT_ID]/debi-marlene-bot:v1 .

# Cloud Run 배포
gcloud run deploy debi-marlene-bot \
  --image gcr.io/[PROJECT_ID]/debi-marlene-bot:v1 \
  --region asia-northeast3
```

---

> 이 봇은 이터널리턴의 데비&마를렌 캐릭터를 테마로 제작되었습니다.
