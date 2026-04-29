# companion-bot

거노 personal Discord 비서. DM → companion Managed Agent → 답장.

## 기능
- DM에서 자유롭게 질문 (owner만)
- gws CLI (Drive 메모리) + GitHub MCP + bash + huggingface-hub/firestore/polars 다 사용
- 30분 idle 후 세션 자동 archive (새 메시지 시 새 세션)
- `/reset` 또는 `!reset` 메시지로 즉시 세션 리셋

## 거노 손작업 (1회 셋업)

### 1. Discord Application 등록
1. https://discord.com/developers/applications 접속
2. **New Application** → 이름: `companion` (또는 자유)
3. **Bot** 탭 → **Add Bot**
4. **Privileged Gateway Intents** → **Message Content Intent** ON (DM 본문 읽기)
5. **Reset Token** → 토큰 복사
6. **OAuth2 → URL Generator** → scopes: `bot` 만 / permissions: `Send Messages`, `Read Message History` / 생성된 URL 로 거노 personal 서버에 봇 초대 (DM 가능 조건)

### 2. 토큰 Secret Manager 저장
```bash
echo -n "<bot_token>" | gcloud secrets create companion-bot-token \
  --replication-policy=automatic --project=ironic-objectivist-465713-a6 --data-file=-
```

또는 기존 Secret 갱신:
```bash
echo -n "<bot_token>" | gcloud secrets versions add companion-bot-token \
  --project=ironic-objectivist-465713-a6 --data-file=-
```

### 3. 빌드 + 배포
docker-compose.yml 의 `companion-bot` 서비스 항목 참조 (Makefile target 추가 예정).

## env 키 (런타임)
| 키 | 출처 |
|---|---|
| `COMPANION_BOT_TOKEN` | Secret Manager `companion-bot-token` |
| `OWNER_ID` | Secret Manager `owner-id` |
| `ANTHROPIC_API_KEY` | Secret Manager `claude-api-key` |
| `MANAGED_COMPANION_AGENT_ID` | `.env` 또는 직접 |
| `MANAGED_COMPANION_ENV_ID` | `.env` 또는 직접 |

## 사용
거노 서버에 봇 초대 → 봇한테 DM 보내기 → 답변 받음.

```
거노: 내 todos 뭐 있어?
봇: (Drive에서 me/todos.md 읽고 정리)
```
