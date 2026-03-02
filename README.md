# Debi & Marlene

이터널 리턴(Eternal Return) 데비&마를렌 테마 다기능 Discord 봇.
AI 음성 합성(TTS), 음악 재생, 게임 통계, 퀴즈, 웹 대시보드 등을 제공합니다.

## 주요 기능

- **AI TTS** - Qwen3-TTS 기반 음성 합성으로 텍스트 채팅을 음성 채널에서 읽어줌 (데비/마를렌/교대 모드)
- **음악 재생** - YouTube 검색/URL 재생, 대기열 관리
- **게임 통계** - 이터널 리턴 전적 검색, 캐릭터 통계, 승률 기반 추천
- **퀴즈** - 노래 맞추기 퀴즈, 이터널 리턴 4지선다 퀴즈
- **유튜브 알림** - 새 영상 업로드 시 DM/채널 자동 알림
- **환영 메시지** - 멤버 입장/퇴장 시 커스텀 메시지 및 이미지 생성
- **웹 대시보드** - 서버별 설정 관리 UI ([debimarlene.com](https://debimarlene.com))

## 명령어

### /이터널리턴

| 명령어 | 설명 |
|--------|------|
| `/이터널리턴 전적 [닉네임]` | 플레이어 전적 검색 (MMR, 티어, 승률) |
| `/이터널리턴 통계 [티어] [기간]` | 캐릭터별 승률/픽률 통계 |
| `/이터널리턴 추천` | 승률 기준 상위 5 캐릭터 추천 |
| `/이터널리턴 동접` | 현재 동시접속자 수 (Steam API) |

### /음성 (TTS)

| 명령어 | 설명 |
|--------|------|
| `/음성 입장` | 음성 채널에 봇 입장 (TTS 시작) |
| `/음성 퇴장` | 음성 채널에서 봇 퇴장 |
| `/음성 채널설정 [채널]` | TTS 읽기 대상 텍스트 채널 지정 (관리자) |
| `/음성 채널해제` | TTS 채널 제한 해제 (관리자) |
| `/음성 음성설정 [음성]` | TTS 음성 선택: 데비 / 마를렌 / 교대 (관리자) |

### /음악

| 명령어 | 설명 |
|--------|------|
| `/음악 재생 [검색어/URL]` | YouTube 음악 재생 |
| `/음악 정지` | 재생 중지 및 대기열 초기화 |
| `/음악 스킵` | 현재 곡 건너뛰기 |
| `/음악 대기열` | 현재 대기열 확인 |

### /퀴즈

| 명령어 | 설명 |
|--------|------|
| `/퀴즈 노래 [문제수]` | 노래 맞추기 퀴즈 (5/10/15문제) |
| `/퀴즈 노래출제` | 커스텀 노래 퀴즈 출제 |
| `/퀴즈 이터널리턴` | 이터널 리턴 4지선다 퀴즈 |
| `/퀴즈 중지` | 진행 중인 퀴즈 중지 |

### /유튜브

| 명령어 | 설명 |
|--------|------|
| `/유튜브 알림 [받기]` | 새 영상 DM 알림 구독/해제 |
| `/유튜브 테스트` | 유튜브 알림 수동 테스트 (관리자) |

### 기타

| 명령어 | 설명 |
|--------|------|
| `/설정` | 서버 설정 - 유튜브 알림 채널, 명령어 전용 채널 (관리자) |
| `/피드백 [내용]` | 개발자에게 피드백 전송 |

## 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| 봇 | Python 3.11+, discord.py 2.6.4, anthropic (Claude AI) |
| TTS | Modal Serverless + Qwen3-TTS-0.6B (파인튜닝 모델, T4 GPU) |
| 대시보드 | Flask + React 19 + TypeScript + Vite + Tailwind 4 |
| 웹패널 | Flask + React |
| 결제 | TossPayments SDK |
| 인프라 | GCP Compute Engine VM, Google Cloud Storage, Artifact Registry |
| 게임 데이터 | DAK.GG API |

## 도메인

| URL | 용도 |
|-----|------|
| [debimarlene.com](https://debimarlene.com) | 대시보드 |
| [panel.debimarlene.com](https://panel.debimarlene.com) | 웹패널 |

## 프로젝트 구조

```
run/                        # Discord 봇
  core/                     # 봇 초기화 (bot.py, config.py)
  cogs/                     # 명령어 그룹 (이터널리턴, 음성, 음악, 퀴즈, 유튜브 등)
  services/                 # 비즈니스 로직
    eternal_return/          # DAK.GG API, 그래프 생성
    tts/                     # TTS 엔진 (Qwen3-TTS, Modal)
    music/                   # YouTube 음악 재생
    quiz/                    # 퀴즈 시스템
    welcome/                 # 환영 메시지/이미지 생성
  views/                    # Discord embed/UI 포맷팅
  utils/                    # 유틸리티
dashboard/
  backend/                  # Flask API (port 8081, Discord OAuth2)
  frontend/                 # React + Vite + Tailwind (port 3002)
webpanel/
  backend/                  # Flask API (port 8080)
  src/                      # React 프론트엔드
```

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

### 필요한 환경 변수

```
DISCORD_TOKEN       # Discord 봇 토큰
YOUTUBE_API_KEY     # YouTube Data API 키
OWNER_ID            # 봇 소유자 Discord ID
TTS_ENGINE          # TTS 엔진 (modal / edgetts_rvc / qwen3_api / qwen3)
```

## 배포

GCP Compute Engine VM에 Docker 컨테이너로 배포됩니다.

```bash
make deploy      # 전체: 빌드 + Artifact Registry Push + VM 재시작
make stop-vm     # VM 봇 중지
make start-vm    # VM 봇 시작
make logs        # 컨테이너 로그
make status      # VM/컨테이너 상태
```

자세한 배포/인프라 정보는 [CLAUDE.md](CLAUDE.md) 참고.

---

> 이 봇은 이터널리턴의 데비&마를렌 캐릭터를 테마로 제작되었습니다.
