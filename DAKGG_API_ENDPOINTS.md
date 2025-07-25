# 닥지지 API 엔드포인트 목록

## 기본 정보
- **Base URL**: `https://er.dakgg.io/api/v1`
- **Headers 필요**: 
  ```
  Accept: application/json, text/plain, */*
  Origin: https://dak.gg
  Referer: https://dak.gg/
  User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
  ```

## 📊 플레이어 관련 API

### 플레이어 프로필
```
GET /players/{닉네임}/profile?season=SEASON_17
```
**기능**: 플레이어 기본 정보, MMR, 티어, 시즌별 통계
**응답 예시**:
```json
{
  "player": {
    "userNum": 4132167,
    "name": "모묘모",
    "accountLevel": 118
  },
  "playerSeasons": [{
    "mmr": 4800,
    "tierId": 5,
    "tierGradeId": 1,
    "tierMmr": 150
  }]
}
```

### 플레이어 경기 기록
```
GET /players/{닉네임}/matches?season=SEASON_17&matchingMode=RANK&teamMode=ALL&page=1
```
**파라미터**:
- `matchingMode`: RANK, NORMAL, COBALT
- `teamMode`: ALL, SOLO, DUO, SQUAD
- `page`: 페이지 번호

### 플레이어 캐릭터 통계
```
GET /players/{닉네임}/characters?season=SEASON_17&matchingMode=RANK
```

### 플레이어 무기 통계
```
GET /players/{닉네임}/weapons?season=SEASON_17&matchingMode=RANK
```

## 🎮 게임 데이터 API

### 티어 정보
```
GET /data/tiers?hl=ko
```
**기능**: 모든 티어 정보 (ID, 이름, 아이콘)

### 캐릭터 정보
```
GET /data/characters?hl=ko
```
**기능**: 모든 캐릭터 정보 (스킬, 이미지, 스탯)

### 무기 정보
```
GET /data/weapons?hl=ko
```
**기능**: 모든 무기 정보 (데미지, 타입, 이미지)

### 아이템 정보
```
GET /data/items?hl=ko
```
**기능**: 모든 아이템 정보 (스탯, 조합법, 이미지)

### 지역 정보
```
GET /data/areas?hl=ko
```
**기능**: 맵 지역 정보

### 동물 정보
```
GET /data/animals?hl=ko
```
**기능**: 야생동물 정보

## 🏆 랭킹 API

### 플레이어 랭킹
```
GET /rankings/players?season=SEASON_17&matchingMode=RANK&region=ALL&page=1
```
**파라미터**:
- `region`: ALL, ASIA, NA, EU 등
- `matchingMode`: RANK, NORMAL
- `page`: 페이지 번호

### 팀 랭킹 (팀전용)
```
GET /rankings/teams?season=SEASON_17&matchingMode=SQUAD_RUMBLE&region=ALL&page=1
```

### 캐릭터 랭킹
```
GET /rankings/characters?season=SEASON_17&matchingMode=RANK&region=ALL
```

### 무기 랭킹
```
GET /rankings/weapons?season=SEASON_17&matchingMode=RANK&region=ALL
```

## 📈 통계 API

### 캐릭터 통계
```
GET /statistics/characters?season=SEASON_17&matchingMode=RANK&region=ALL
```
**기능**: 캐릭터별 픽률, 승률, 평균 킬

### 무기 통계
```
GET /statistics/weapons?season=SEASON_17&matchingMode=RANK&region=ALL
```
**기능**: 무기별 픽률, 승률, 평균 데미지

### 아이템 통계
```
GET /statistics/items?season=SEASON_17&matchingMode=RANK&region=ALL
```
**기능**: 아이템별 픽률, 승률

### 메타 통계
```
GET /statistics/meta?season=SEASON_17&matchingMode=RANK&region=ALL
```
**기능**: 현재 메타 정보, 트렌드

### 지역별 통계
```
GET /statistics/regions?season=SEASON_17&matchingMode=RANK
```

## 🔍 검색 API

### 플레이어 검색
```
GET /search/players?query={검색어}&limit=10
```

### 팀 검색
```
GET /search/teams?query={검색어}&limit=10
```

## ⚔️ 게임 상세 API

### 개별 게임 정보
```
GET /games/{gameId}
```
**기능**: 특정 게임의 상세 정보 (참가자, 결과, 타임라인)

### 게임 리플레이
```
GET /games/{gameId}/replay
```

## 🎯 개인화 API

### 즐겨찾기 플레이어
```
GET /favorites/players
POST /favorites/players/{userNum}
DELETE /favorites/players/{userNum}
```

### 비교 기능
```
GET /compare/players?players={userNum1},{userNum2}&season=SEASON_17
```

## 📊 리더보드 API

### 일일 베스트
```
GET /leaderboards/daily?date={YYYY-MM-DD}&type=kills
```
**타입**: kills, damage, wins, rank

### 주간 베스트
```
GET /leaderboards/weekly?week={YYYY-WW}&type=kills
```

### 월간 베스트
```
GET /leaderboards/monthly?month={YYYY-MM}&type=kills
```

## 🔥 핫 트렌드 API

### 인기 상승 캐릭터
```
GET /trends/characters/rising?period=week
```

### 인기 하락 캐릭터
```
GET /trends/characters/falling?period=week
```

### 신규 빌드
```
GET /trends/builds/new?period=week
```

## 💎 프리미엄 API (가능할 경우)

### 상세 분석
```
GET /analysis/players/{userNum}/performance?season=SEASON_17
```

### 개선 제안
```
GET /analysis/players/{userNum}/recommendations?season=SEASON_17
```

### 예측 데이터
```
GET /predictions/tier/{userNum}?season=SEASON_17
```

## 🎮 실시간 API

### 라이브 게임
```
GET /live/games?region=ALL
```

### 실시간 랭킹
```
GET /live/rankings?matchingMode=RANK&region=ALL
```

## 🔧 유틸리티 API

### 서버 상태
```
GET /status
```

### API 버전
```
GET /version
```

### 시즌 정보
```
GET /seasons
```

---

## 🚀 봇에서 구현 가능한 기능들

### 기본 기능
- ✅ `/전적` - 플레이어 티어 조회
- `/상세전적` - 상세한 통계 정보
- `/최근경기` - 최근 20경기 결과
- `/랭킹` - 서버 내 순위 조회

### 고급 기능
- `/캐릭터통계` - 캐릭터별 승률
- `/메타` - 현재 메타 정보
- `/비교` - 두 플레이어 비교
- `/랭킹` - 각종 랭킹 조회

### 실시간 기능
- `/라이브` - 실시간 게임 정보
- `/트렌드` - 인기 상승/하락 정보

### 유틸리티
- `/검색` - 플레이어/팀 검색
- `/서버상태` - API 서버 상태

---

**주의사항**: 
- 모든 API가 공개되어 있지 않을 수 있음
- Rate Limit 존재 가능성
- 일부 API는 인증이 필요할 수 있음
- 실제 사용 전 테스트 필요