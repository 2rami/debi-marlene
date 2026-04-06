# Debi & Marlene

이터널 리턴(Eternal Return) 데비&마를렌 테마 다기능 Discord 봇.
AI 음성 합성(TTS), 음악 재생, 게임 통계, 퀴즈, 웹 대시보드 등을 제공합니다.

## 주요 기능

- **TTS** - CosyVoice3 AI 음성(데비/마를렌/알렉스) + Edge TTS(SunHi/InJoon/Hyunsu) 지원, `/tts` 입력한 채널 자동 읽기
- **음악 재생** - YouTube 검색/URL 재생, UI 버튼으로 대기열/스킵/반복 조작
- **게임 통계** - 이터널 리턴 전적 검색, 캐릭터 통계, 시즌 정보
- **퀴즈** - 음악 퀴즈
- **유튜브 알림** - 새 영상 업로드 시 채널 자동 알림
- **환영 메시지** - 멤버 입장/퇴장 시 커스텀 메시지 및 이미지 생성
- **웹 대시보드** - 서버별 설정 관리 UI
- **AI 대화** - 키워드 트리거(데비야/마를렌아)로 Claude AI 대화, 사용자별 메모리 저장

## 스크린샷

| 전적 검색 | 캐릭터 통계 |
|:---------:|:----------:|
| ![전적](docs/screenshots/screenshot_record.png) | ![통계](docs/screenshots/screenshot_stats.png) |

| 음악 재생 | 시즌 정보 |
|:---------:|:---------:|
| ![음악](docs/screenshots/screenshot_music.png) | ![시즌](docs/screenshots/screenshot_season.png) |

| TTS 설정 (대시보드) |
|:-------------------:|
| ![TTS 설정](docs/screenshots/screenshot_tts_settings.png) |

## 명령어

| 명령어 | 설명 |
|--------|------|
| `/전적 [닉네임]` | 플레이어 전적 검색 (MMR, 티어, 승률) |
| `/통계` | 캐릭터별 승률/픽률 통계 (다이아+) |
| `/시즌` | 현재 시즌 정보 및 경과일 |
| `/동접` | 현재 동시접속자 수 (Steam API) |
| `/tts` | 음성 채널 입장 + TTS 시작 (입력한 채널 자동 설정) |
| `/음악 [검색어/URL]` | YouTube 음악 재생 |
| `/퀴즈` | 음악 퀴즈 시작 |
| `/설정` | 서버 설정 관리 (공지 채널, TTS, 알림, 대시보드) |
| `/피드백 [내용]` | 개발자에게 피드백 전송 |

## TTS 음성

| 음성 | 엔진 | 설명 |
|------|------|------|
| SunHi (기본) | Edge TTS | 여성, 서버 불필요, 즉시 사용 |
| InJoon | Edge TTS | 남성, 서버 불필요, 즉시 사용 |
| Hyunsu | Edge TTS | 남성 다국어, 서버 불필요, 즉시 사용 |
| 데비 | CosyVoice3 (Modal) | AI 파인튜닝 음성, GPU 서버 필요 |
| 마를렌 | CosyVoice3 (Modal) | AI 파인튜닝 음성, GPU 서버 필요 |
| 알렉스 | CosyVoice3 (Modal) | AI 파인튜닝 음성, GPU 서버 필요 |

AI 음성 선택 시 Modal 서버 상태를 자동 표시. 서버 오류 시 Edge TTS로 자동 전환.

## 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| 봇 | Python 3.11+, discord.py 2.6.4, anthropic (Claude AI) |
| TTS (AI) | Modal Serverless + CosyVoice3 파인튜닝 모델 (A10G GPU) |
| TTS (기본) | Edge TTS (Microsoft Neural TTS, 서버 불필요) |
| 대시보드 | Flask + React 19 + TypeScript + Vite + Tailwind 4 |
| 인프라 | GCP Compute Engine VM, Google Cloud Storage, Artifact Registry |
| 게임 데이터 | DAK.GG API |

## 프로젝트 구조

```
run/                        # Discord 봇
  core/                     # 봇 초기화 (bot.py, config.py)
  cogs/                     # 명령어 (eternal_return, voice, music, quiz, youtube 등)
  services/                 # 비즈니스 로직
    eternal_return/          # DAK.GG API, 그래프 생성
    tts/                     # TTS 엔진 (CosyVoice3, Edge TTS, Modal 서버)
    music/                   # YouTube 음악 재생
    quiz/                    # 퀴즈 시스템
    welcome/                 # 환영 메시지/이미지 생성
  views/                    # Discord embed/UI 포맷팅
  utils/                    # 유틸리티
dashboard/
  backend/                  # Flask API (port 8081, Discord OAuth2)
  frontend/                 # React + Vite + Tailwind (port 3002)
```

## 로컬 개발

```bash
# 봇 실행 (VM 봇 자동 중지 후 로컬 실행)
make test-local

# 대시보드
cd dashboard/backend && python3 app.py          # backend (8081)
cd dashboard/frontend && npm run dev            # frontend (3002)

```

### 필요한 환경 변수

```
DISCORD_TOKEN       # Discord 봇 토큰
YOUTUBE_API_KEY     # YouTube Data API 키
OWNER_ID            # 봇 소유자 Discord ID
```

## 배포

GCP Compute Engine VM에 Docker 컨테이너로 배포됩니다.

```bash
make deploy            # 봇: 빌드 + Artifact Registry Push + VM 재시작
make deploy-dashboard  # 대시보드: 빌드 + Push + VM 재시작
make stop-vm           # VM 봇 중지
make start-vm          # VM 봇 시작
make logs              # 컨테이너 로그
make status            # VM/컨테이너 상태
```

자세한 배포/인프라 정보는 [CLAUDE.md](CLAUDE.md) 참고.

---

> 이 봇은 이터널리턴의 데비&마를렌 캐릭터를 테마로 제작되었습니다.
