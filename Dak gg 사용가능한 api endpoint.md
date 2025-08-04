# Dak.gg API 엔드포인트

## 플레이어 정보
- **프로필**: `/players/{닉네임}/profile`
- **시즌 성적표**: `/rpc/season-report/{닉네임}?season=SEASON_16`

https://er.dakgg.io/api/v1/players/%EB%AA%A8%EB%AC%98%EB%AA%A8/matches?season=SEASON_17&matchingMode=ALL&teamMode=ALL&page=1

https://er.dakgg.io/api/v1/players/%EB%AA%A8%EB%AC%98%EB%AA%A8/matches?season=SEASON_17&matchingMode=RANK&teamMode=ALL&page=1

https://er.dakgg.io/api/v1/players/%EB%AA%A8%EB%AC%98%EB%AA%A8/union-teams?season=SEASON_17

https://er.dakgg.io/api/v1/players/%EB%AA%A8%EB%AC%98%EB%AA%A8/profile?season=SEASON_17

https://er.dakgg.io/api/v1/players/%EB%AA%A8%EB%AC%98%EB%AA%A8/union-teams


## 게임 데이터
- **캐릭터**: `/data/characters?hl=ko`
- **무기/마스터리**: `/data/masteries?hl=ko`
- **아이템**: `/data/items?hl=ko`
- **스킬**: `/data/skills?hl=ko`
- **전술스킬**: `/data/tactical-skills?hl=ko`
- **특성스킬**: `/data/trait-skills?hl=ko`
- **티어**: `/data/tiers?hl=ko`
- **맵/지역**: `/data/areas?hl=ko`
- **야생동물**: `/data/monsters?hl=ko`
- **날씨**: `/data/weathers?hl=ko`
- **인퓨전**: `/data/infusions?hl=ko`
- **시즌**: `/data/seasons?hl=ko` 
https://er.dakgg.io/api/v0/current-season
- **즐겨찾기**:https://er.dakgg.io/api/v0/bookmarks/players?userNums=4132167&teamMode=SQUAD&hl=ko

## 통계
- **캐릭터 통계**: `/character-stats?dt=7&teamMode=SQUAD&tier={티어}`

https://er.dakgg.io/api/v0/leaderboard?page=1&seasonKey=SEASON_17&serverName=seoul&teamMode=SQUAD&hl=ko
장인랭킹: 
https://er.dakgg.io/api/v0/leaderboard/characters/Theodore?teamMode=ALL&sortType=MATCH_COUNT&page=1&hl=ko

https://er.dakgg.io/api/v0/leaderboard/characters/Garnet?teamMode=ALL&sortType=MATCH_COUNT&page=1&hl=ko
티어통계: https://er.dakgg.io/api/v0/statistics/tier-distribution?teamMode=SQUAD

모스트통계: https://er.dakgg.io/api/v0/statistics/most-character?hl=ko&dt=3&teamMode=SQUAD
스킨통계: https://er.dakgg.io/api/v0/statistics/character-skin?period=DAYS7&hl=ko

### 티어 파라미터
- `iron` - 아이언
- `bronze` - 브론즈  
- `silver` - 실버
- `gold` - 골드
- `platinum` - 플래티넘
- `platinum_plus` - 플래티넘+
- `diamond` - 다이아몬드
- `diamond_plus` - 다이아몬드+
- `mithril` - 미스릴
- `mithril_plus` - 미스릴+
- `meteorite_plus` - 메테오라이트+
- `in1000` - 상위 1000명

### 팀모드 파라미터
- `SOLO` - 솔로
- `DUO` - 듀오
- `SQUAD` - 스쿼드
## Base URL
`https://er.dakgg.io/api/v1`