# Debi Marlene - Makefile
#
# 배포 대상은 사내 맥미니 한 대다. GCP Compute Engine VM 은 2026-08-25 에 삭제됐고
# Docker·Artifact Registry 경로도 함께 끊겼다 — 미니엔 docker 가 없고 봇·대시보드·웹패널이
# 전부 venv 로 돈다. 그래서 배포는 rsync 로 파일을 밀고 프로세스를 죽이는 것이 전부다.
#
# 죽이면 launchd(KeepAlive)가 30초 스로틀로 되살린다. 이게 유일한 재시작 수단이다 —
# launchctl 직접 조작은 LaunchDaemon 이라 root 가 필요하고 원격 sudo 는 비번을 묻는다.
SHELL := /bin/bash
.ONESHELL:
export LANG := C.UTF-8
export LC_ALL := C.UTF-8
export PYTHONIOENCODING := utf-8
export PYTHONUTF8 := 1

# 배포 대상 (~/.ssh/config 의 Host 별칭)
MINI = nachoneko
REMOTE = /Users/nachoneko/debimarlene

DASH_STATIC = $(REMOTE)/dashboard/static
PANEL_STATIC = $(REMOTE)/webpanel/static

# Cloudflare 캐시 퍼지용 토큰 (.env 에서 자동 로드)
CF_ZONE = 49337200d8d2ff73047081d747d42074
CF_API_TOKEN ?= $(shell grep -E '^CF_API_TOKEN=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]')

RSYNC = rsync -az --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store'

.PHONY: help guard status
.PHONY: deploy-bot deploy-dashboard deploy-dashboard-frontend deploy-dashboard-backend
.PHONY: deploy-webpanel deploy-webpanel-frontend deploy-webpanel-backend
.PHONY: restart-bot restart-dashboard restart-webpanel restart-caddy
.PHONY: logs logs-bot logs-dashboard logs-webpanel logs-caddy
.PHONY: stop-bot start-bot test-local
.PHONY: inject-dashboard-env purge-cache sync-check

help:
	@echo "Debi Marlene — 배포 대상: 맥미니($(MINI):$(REMOTE))"
	@echo ""
	@echo "-- 배포 --"
	@echo "  make deploy-bot                - 봇 코드(run/, main.py) 배포 + 재시작"
	@echo "  make deploy-dashboard          - 대시보드 프론트+백엔드"
	@echo "  make deploy-dashboard-frontend - 대시보드 프론트만 (빌드 포함)"
	@echo "  make deploy-dashboard-backend  - 대시보드 백엔드만"
	@echo "  make deploy-webpanel           - 웹패널 프론트+백엔드"
	@echo ""
	@echo "-- 제어 --"
	@echo "  make restart-bot / restart-dashboard / restart-webpanel / restart-caddy"
	@echo "  make status                    - 서비스 프로세스 + 라이브 응답 확인"
	@echo "  make logs / logs-bot / logs-dashboard / logs-webpanel / logs-caddy"
	@echo ""
	@echo "-- 로컬 테스트 --"
	@echo "  make stop-bot                  - 미니 봇 정지 (sudo 비번 입력 필요)"
	@echo "  make start-bot                 - 미니 봇 재개 (sudo 비번 입력 필요)"
	@echo "  make test-local                - 로컬 봇 실행 (stop-bot 을 먼저 할 것)"
	@echo ""
	@echo "-- 기타 --"
	@echo "  make sync-check                - 로컬 .env 와 미니 시크릿 대조"
	@echo "  make purge-cache               - Cloudflare 캐시 퍼지"

# ssh 가 안 붙는 상태에서 rsync 가 절반만 올라가는 것을 막는다.
guard:
	@ssh -o ConnectTimeout=8 -o BatchMode=yes $(MINI) 'test -d $(REMOTE)' 2>/dev/null || { \
		echo "[ERROR] $(MINI) 에 접속할 수 없거나 $(REMOTE) 가 없다."; \
		echo "        사내 VPN 연결과 ~/.ssh/config 의 Host $(MINI) 항목을 확인할 것."; exit 1; }

# ============================================================
# 봇
# ============================================================

deploy-bot: guard
	@echo "[1/2] 봇 코드 업로드..."
	@$(RSYNC) --delete run/ $(MINI):$(REMOTE)/run/
	@$(RSYNC) main.py $(MINI):$(REMOTE)/main.py
	@$(MAKE) --no-print-directory restart-bot
	@echo "봇 배포 완료"

# KeepAlive 가 되살리므로 kill 이 곧 재시작이다. plist 의 ThrottleInterval 이 30 이라
# 죽인 직후 최대 30초는 봇이 없다 — 로그로 복귀를 확인한다.
restart-bot: guard
	@echo "봇 재시작 (launchd 가 되살릴 때까지 최대 30초)..."
	@ssh $(MINI) 'pkill -f "venv-bot/bin/python -u main.py" || true'
	@for i in $$(seq 1 20); do \
		sleep 3; \
		if ssh $(MINI) 'pgrep -f "venv-bot/bin/python -u main.py" >/dev/null'; then \
			echo "봇 기동 확인"; exit 0; fi; \
	done; \
	echo "[ERROR] 60초 안에 안 올라왔다. 'make logs-bot' 으로 확인할 것"; exit 1

# LaunchDaemon 이라 root 권한이 필요하다 — ssh -t 로 비번 프롬프트를 띄운다.
stop-bot:
	@echo "미니 봇 정지 (sudo 비번 입력 필요)..."
	@ssh -t $(MINI) 'sudo launchctl bootout system/com.geono.debimarlene-bot'
	@echo "정지 완료 — 로컬 테스트 가능. 끝나면 'make start-bot'"

start-bot:
	@echo "미니 봇 재개 (sudo 비번 입력 필요)..."
	@ssh -t $(MINI) 'sudo launchctl bootstrap system /Library/LaunchDaemons/com.geono.debimarlene-bot.plist'
	@echo "재개 완료"

# 같은 토큰으로 두 세션이 붙으면 Discord 가 재연결을 반복한다 — 먼저 stop-bot 할 것.
test-local:
	@echo "로컬 봇 시작 (미니 봇이 떠 있으면 세션이 충돌한다 — 'make stop-bot' 먼저)"
	@PYTHONUNBUFFERED=1 BOT_ENV=local python3 -u main.py

# ============================================================
# 대시보드 (debimarlene.com)
# ============================================================

deploy-dashboard: deploy-dashboard-frontend deploy-dashboard-backend
	@echo "대시보드 배포 완료"

# Vite 는 빌드 시 .env.production 이 .env 를 override 하므로 루트 .env 를 단일 소스로 쓴다.
inject-dashboard-env:
	@echo "[env] 루트 .env -> dashboard/frontend/.env.production 주입..."
	@set -e; \
	if [ ! -f .env ]; then echo "[ERROR] 루트 .env 없음 (DISCORD_CLIENT_ID 필요)"; exit 1; fi; \
	CLIENT_ID=$$(grep -E '^DISCORD_CLIENT_ID=' .env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]'); \
	if [ -z "$$CLIENT_ID" ]; then echo "[ERROR] DISCORD_CLIENT_ID 가 .env 에 비어있음"; exit 1; fi; \
	TOSS_CK=$$(grep -E '^TOSS_CLIENT_KEY=' .env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]'); \
	{ echo "VITE_API_URL=/api"; echo "VITE_DISCORD_CLIENT_ID=$$CLIENT_ID"; echo "VITE_TOSS_CLIENT_KEY=$$TOSS_CK"; } > dashboard/frontend/.env.production; \
	echo "  -> VITE_DISCORD_CLIENT_ID=$$CLIENT_ID"; \
	echo "  -> VITE_TOSS_CLIENT_KEY=$${TOSS_CK:+[set]}$${TOSS_CK:-[EMPTY — 충전 비활성]}"

# Caddy 가 static 을 직접 읽으므로 파일만 바꾸면 즉시 반영된다(리로드 불필요).
# --delete 를 쓰지만 sitemap.xml·ads.txt·소유권 확인 파일은 frontend/public/ 에 있어
# 빌드 산출물에 포함된다 — 지워지지 않는다.
deploy-dashboard-frontend: guard inject-dashboard-env
	@set -euo pipefail; \
	echo "[1/3] 프론트엔드 빌드..."; \
	(cd dashboard/frontend && npm run build); \
	test -f dashboard/frontend/dist/index.html || { echo "[ERROR] dist/index.html 없음 — 빌드 실패"; exit 1; }; \
	test -f dashboard/frontend/dist/google046aee18f88daa1e.html || { \
		echo "[ERROR] Search Console 소유권 확인 파일이 빌드에 없다. 올리면 소유권이 풀린다"; exit 1; }; \
	echo "[2/3] 미니로 동기화..."; \
	$(RSYNC) --delete --exclude='*.map' dashboard/frontend/dist/ $(MINI):$(DASH_STATIC)/; \
	echo "[3/3] Cloudflare 캐시 퍼지..."; \
	$(MAKE) --no-print-directory purge-cache; \
	echo "대시보드 프론트엔드 배포 완료"

# backend 는 run/core/config.py 등을 import 하므로 run/ 도 같이 올린다.
deploy-dashboard-backend: guard
	@echo "[1/2] 백엔드 + run/ 업로드..."
	@$(RSYNC) dashboard/backend/ $(MINI):$(REMOTE)/dashboard/backend/
	@$(RSYNC) run/ $(MINI):$(REMOTE)/run/
	@$(MAKE) --no-print-directory restart-dashboard
	@echo "대시보드 백엔드 배포 완료"

restart-dashboard: guard
	@echo "대시보드(gunicorn) 재시작..."
	@ssh $(MINI) 'pkill -f "gunicorn app:app" || true'
	@for i in $$(seq 1 10); do \
		sleep 2; \
		if ssh $(MINI) 'pgrep -f "gunicorn app:app" >/dev/null'; then \
			echo "gunicorn 기동 확인"; exit 0; fi; \
	done; \
	echo "[ERROR] 안 올라왔다. 'make logs-dashboard' 로 확인할 것"; exit 1

# ============================================================
# 웹패널 (panel.debimarlene.com)
# ============================================================

deploy-webpanel: deploy-webpanel-frontend deploy-webpanel-backend
	@echo "웹패널 배포 완료"

# --delete 를 쓰지 않는다. 미니 static 에 옛 PWA 빌드의 잔해(sw.js·manifest·workbox)가
# 남아 있는데 지금 vite 설정엔 PWA 플러그인이 없어 빌드 산출물에 그 파일들이 없다 —
# 지우면 이미 서비스워커를 등록해 둔 브라우저가 갱신 경로를 잃는다.
deploy-webpanel-frontend: guard
	@set -euo pipefail; \
	echo "[1/2] 웹패널 프론트 빌드..."; \
	(cd webpanel && npm run build); \
	test -f webpanel/dist/index.html || { echo "[ERROR] webpanel/dist/index.html 없음 — 빌드 실패"; exit 1; }; \
	echo "[2/2] 미니로 동기화..."; \
	$(RSYNC) --exclude='*.map' webpanel/dist/ $(MINI):$(PANEL_STATIC)/; \
	echo "웹패널 프론트엔드 배포 완료"

deploy-webpanel-backend: guard
	@echo "[1/2] 웹패널 백엔드 + run/ 업로드..."
	@$(RSYNC) webpanel/backend/ $(MINI):$(REMOTE)/webpanel/backend/
	@$(RSYNC) run/ $(MINI):$(REMOTE)/run/
	@$(MAKE) --no-print-directory restart-webpanel
	@echo "웹패널 백엔드 배포 완료"

# 이 백엔드도 Discord Gateway 에 붙는다 — 같은 토큰의 다른 세션과 겹치면 경합이 난다.
restart-webpanel: guard
	@echo "웹패널 재시작..."
	@ssh $(MINI) 'pkill -f "venv-webpanel/bin/python backend/app.py" || true'
	@for i in $$(seq 1 10); do \
		sleep 2; \
		if ssh $(MINI) 'pgrep -f "venv-webpanel/bin/python backend/app.py" >/dev/null'; then \
			echo "웹패널 기동 확인"; exit 0; fi; \
	done; \
	echo "[ERROR] 안 올라왔다. 'make logs-webpanel' 로 확인할 것"; exit 1

restart-caddy: guard
	@echo "Caddy 재시작 (라우팅·Caddyfile 변경 시에만 필요)..."
	@ssh $(MINI) 'pkill -f "caddy run" || true'
	@sleep 3
	@ssh $(MINI) 'pgrep -f "caddy run" >/dev/null' && echo "Caddy 기동 확인" || { echo "[ERROR] Caddy 가 안 올라왔다"; exit 1; }

# ============================================================
# 상태·로그
# ============================================================

status: guard
	@echo "== 미니 프로세스 =="
	@ssh $(MINI) 'for p in "venv-bot/bin/python -u main.py:봇" "gunicorn app:app:대시보드" "venv-webpanel/bin/python backend/app.py:웹패널" "caddy run:Caddy" "cloudflared --no-autoupdate:터널"; do \
		pat=$${p%:*}; name=$${p##*:}; \
		if pgrep -f "$$pat" >/dev/null; then echo "  [실행중] $$name"; else echo "  [정지]   $$name"; fi; done'
	@echo ""
	@echo "== 라이브 응답 =="
	@for u in https://debimarlene.com/ https://debimarlene.com/api/auth/me https://panel.debimarlene.com/; do \
		printf "  %-42s %s\n" "$$u" "$$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 $$u)"; done

logs: logs-bot

logs-bot: guard
	@ssh $(MINI) 'tail -f $(REMOTE)/logs/bot.log $(REMOTE)/logs/bot.err'

logs-dashboard: guard
	@ssh $(MINI) 'tail -f $(REMOTE)/logs/dash-error.log $(REMOTE)/logs/dashboard.err'

logs-webpanel: guard
	@ssh $(MINI) 'tail -f $(REMOTE)/logs/webpanel.err'

logs-caddy: guard
	@ssh $(MINI) 'tail -f $(REMOTE)/logs/caddy.log $(REMOTE)/logs/caddy.err'

# ============================================================
# env·캐시
# ============================================================

# 미니는 secrets/{bot,dashboard,webpanel}.env 를 읽는다. 로컬 .env 와 갈리면
# OAuth·서버 목록이 조용히 깨지므로 배포 전 대조한다.
# 시크릿 본문은 출력하지 않는다 — 키 이름과 개수만 비교한다.
sync-check: guard
	@echo "== 로컬 .env vs 미니 secrets/bot.env =="
	@local_keys=$$(grep -oE '^[A-Z_][A-Z0-9_]*=' .env 2>/dev/null | sort -u); \
	mini_keys=$$(ssh $(MINI) 'grep -oE "^[A-Z_][A-Z0-9_]*=" $(REMOTE)/secrets/bot.env 2>/dev/null' | sort -u); \
	echo "  로컬 $$(echo "$$local_keys" | grep -c .)개 / 미니 $$(echo "$$mini_keys" | grep -c .)개"; \
	only_local=$$(comm -23 <(echo "$$local_keys") <(echo "$$mini_keys")); \
	only_mini=$$(comm -13 <(echo "$$local_keys") <(echo "$$mini_keys")); \
	if [ -n "$$only_local" ]; then echo "  로컬에만: $$(echo $$only_local | tr '\n' ' ')"; fi; \
	if [ -n "$$only_mini" ]; then echo "  미니에만: $$(echo $$only_mini | tr '\n' ' ')"; fi; \
	if [ -z "$$only_local" ] && [ -z "$$only_mini" ]; then echo "  키 목록 일치"; fi

purge-cache:
	@if [ -n "$(CF_API_TOKEN)" ]; then \
		curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$(CF_ZONE)/purge_cache" \
			-H "Authorization: Bearer $(CF_API_TOKEN)" \
			-H "Content-Type: application/json" \
			--data '{"purge_everything":true}' > /dev/null && echo "  캐시 퍼지 완료"; \
	else \
		echo "  [WARN] CF_API_TOKEN 미설정 — 퍼지 스킵 (브라우저 강제 새로고침 필요)"; \
	fi
