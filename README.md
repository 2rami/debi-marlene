# 데비&마를렌 Discord 봇

이터널리턴(Eternal Return) 데비&마를렌 테마 Discord 봇입니다.

## 주요 기능

### 전적 검색

- `/전적 <닉네임>`: 유저 전적 조회 (MMR, 티어, 승률)
- `/통계 [티어] [기간]`: 캐릭터별 통계 조회 (승률, 픽률, 평균 순위)

### 유튜브 알림

- **자동 알림**: 이터널리턴 공식 YouTube 새 영상 자동 알림 (5분마다 체크)
- `/설정`: [관리자] 서버의 유튜브 알림 채널 설정
- `/유튜브알림 <받기>`: 개인 DM으로 유튜브 알림 받기/해제
- `/유튜브테스트`: [관리자] 유튜브 알림 수동 테스트

### 피드백

- `/피드백 <내용>`: 봇 개발자에게 피드백 전송

## 프로젝트 구조

```
debi-marlene/
├── main.py                         # 봇 실행 진입점
├── run/                            # 봇 핵심 모듈
│   ├── commands/                   # 슬래시 명령어
│   │   ├── stats.py                # /전적 명령어
│   │   ├── character.py            # /통계 명령어
│   │   ├── settings.py             # /설정 명령어
│   │   ├── youtube.py              # /유튜브알림, /유튜브테스트 명령어
│   │   ├── feedback.py             # /피드백 명령어
│   │   └── voice.py                # 음성 채널 명령어 (비활성화)
│   ├── core/                       # 핵심 시스템
│   │   ├── bot.py                  # Discord 봇 로직
│   │   └── config.py               # GCS 설정 관리
│   ├── services/                   # 외부 서비스 연동
│   │   ├── eternal_return/         # 이터널리턴 API
│   │   │   ├── api_client.py       # API 클라이언트
│   │   │   └── graph_generator.py  # MMR 그래프 생성
│   │   ├── tts/                    # TTS 서비스
│   │   └── youtube_service.py      # 유튜브 알림 서비스
│   ├── utils/                      # 유틸리티
│   │   ├── command_logger.py       # 명령어 사용 로깅
│   │   ├── embeds.py               # Discord 임베드 헬퍼
│   │   └── emoji_utils.py          # 이모지 관리
│   └── views/                      # UI 포맷팅
│       ├── character_view.py       # 캐릭터 통계 UI
│       ├── settings_view.py        # 설정 UI
│       ├── stats_view.py           # 전적 검색 UI
│       └── welcome_view.py         # 환영 메시지 UI
├── assets/                         # 이미지 및 정적 자원
├── requirements.txt                # Python 의존성
├── Dockerfile                      # Docker 이미지
├── CLAUDE.md                       # 개발 가이드
└── README.md                       # 프로젝트 문서
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
DISCORD_TOKEN: Discord 봇 토큰
CLAUDE_API_KEY: Anthropic Claude API 키
YOUTUBE_API_KEY: YouTube Data API 키
EternalReturn_API_KEY: 이터널리턴 API 키
OWNER_ID: 봇 소유자 Discord ID
```

## 기술 스택

- **언어**: Python 3.11+
- **프레임워크**: discord.py
- **AI**: Anthropic Claude API
- **클라우드**: Google Cloud Platform (Cloud Run, Cloud Storage)
- **API**: 이터널리턴 API, YouTube Data API

> 이 봇은 이터널리턴의 데비&마를렌 캐릭터를 테마로 제작되었습니다.
