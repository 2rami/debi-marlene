# Debi Marlene Bot - Makefile
SHELL := /bin/bash
.ONESHELL:
export LANG := C.UTF-8
export LC_ALL := C.UTF-8
export PYTHONIOENCODING := utf-8
export PYTHONUTF8 := 1

# GCP 설정
PROJECT_ID = ironic-objectivist-465713-a6
VM_NAME = debi-marlene-bot
ZONE = asia-northeast3-a
REGION = asia-northeast3
VM_PATH = /home/2rami/debi-marlene
CONTAINER_NAME = debi-marlene
REGISTRY = $(REGION)-docker.pkg.dev/$(PROJECT_ID)/debi-marlene
IMAGE_TAG = $(REGISTRY)/$(CONTAINER_NAME):latest

# Dashboard 설정
DASHBOARD_CONTAINER = debi-marlene-dashboard
DASHBOARD_IMAGE_TAG = $(REGISTRY)/$(DASHBOARD_CONTAINER):latest

# Cloudflare 캐시 퍼지용 토큰 (.env 에서 자동 로드)
CF_API_TOKEN ?= $(shell grep -E '^CF_API_TOKEN=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]')

# Companion-bot (나쵸네코) 설정 — 별도 Dockerfile, 별도 이미지
COMPANION_CONTAINER = companion-bot
COMPANION_IMAGE_TAG = $(REGISTRY)/$(COMPANION_CONTAINER):latest

.PHONY: help deploy build-local push-image restart stop start logs status clean test-local stop-vm start-vm
.PHONY: deploy-dashboard build-dashboard push-dashboard start-dashboard stop-dashboard restart-dashboard logs-dashboard
.PHONY: deploy-dashboard-frontend deploy-dashboard-backend deploy-dashboard-quick inject-dashboard-env
.PHONY: deploy-webpanel-frontend deploy-webpanel-backend deploy-webpanel-quick logs-webpanel
.PHONY: deploy-quick
.PHONY: deploy-solo-debi deploy-solo-marlene start-solo-debi start-solo-marlene stop-solo-debi stop-solo-marlene logs-solo-debi logs-solo-marlene restart-solo-debi restart-solo-marlene
.PHONY: deploy-companion build-companion push-companion restart-companion stop-companion start-companion logs-companion
.PHONY: sync-check preflight deploy-guard deploy-env-guard

# 솔로봇 컨테이너 이름 (기존 이미지 $(IMAGE_TAG) 재사용 — 별도 빌드 불필요)
SOLO_DEBI_NAME = debi-solo
SOLO_MARLENE_NAME = marlene-solo

# 기본 명령어 (make 입력 시 도움말 표시)
help:
	@echo "Debi Marlene Bot - 사용 가능한 명령어:"
	@echo ""
	@echo "-- 빠른 배포 (코드만 교체, Docker 리빌드 없음) --"
	@echo "  make deploy-quick              - 봇 코드만 빠른 배포"
	@echo "  make deploy-dashboard-quick    - 대시보드 프론트+백엔드 빠른 배포"
	@echo "  make deploy-webpanel-quick     - 웹패널 프론트+백엔드 빠른 배포"
	@echo ""
	@echo "-- 전체 배포 (Docker 이미지 리빌드, 의존성 변경 시) --"
	@echo "  make deploy                    - 봇 전체 배포"
	@echo "  make deploy-dashboard          - 대시보드 전체 배포"
	@echo "  make deploy-webpanel-backend   - 웹패널 백엔드 전체 배포"
	@echo ""
	@echo "-- VM 제어 --"
	@echo "  make stop-vm       - VM 봇 중지 (로컬 테스트 전)"
	@echo "  make start-vm      - VM 봇 시작 (로컬 테스트 후)"
	@echo "  make logs          - 봇 로그"
	@echo "  make logs-dashboard - 대시보드 로그"
	@echo "  make logs-webpanel  - 웹패널 로그"
	@echo "  make status        - VM 및 컨테이너 상태 확인"
	@echo ""
	@echo "-- 솔로봇 (데비/마를렌 분리) --"
	@echo "  make deploy-solo-debi      - 데비 솔로봇 배포 (기존 이미지 재사용)"
	@echo "  make deploy-solo-marlene   - 마를렌 솔로봇 배포"
	@echo "  make logs-solo-debi        - 데비 솔로봇 로그"
	@echo "  make logs-solo-marlene     - 마를렌 솔로봇 로그"
	@echo "  make stop-solo-debi / stop-solo-marlene"
	@echo ""
	@echo "-- 나쵸네코 (companion-bot) --"
	@echo "  make deploy-companion          - 나쵸네코 봇 빌드 + 푸시 + 재시작"
	@echo "  make restart-companion         - 나쵸네코 봇 재시작 (이미지 재사용)"
	@echo "  make logs-companion            - 나쵸네코 봇 로그"
	@echo "  make stop-companion / start-companion"
	@echo ""
	@echo "-- 기타 --"
	@echo "  make test-local    - 로컬에서 봇 실행 (VM 봇 자동 중지)"
	@echo "  make clean         - 중지된 컨테이너 및 이미지 정리"
	@echo ""

# ============================================================
# 빠른 배포 (코드만 교체, Docker 리빌드 없음)
# ============================================================

# 배포 사전 체크 — Docker Desktop wrapper가 거짓 exit 0 내거나 gcloud 미인증 상태에서 deploy가 침묵 실패하던 함정 차단
deploy-guard:
	@echo "[guard] docker daemon 응답 확인..."
	@docker info --format '{{.ServerVersion}}' >/dev/null 2>&1 || { echo "[ERROR] docker daemon 응답 없음. Docker Desktop 실행 + WSL 통합 활성화 필요"; exit 1; }
	@echo "[guard] gcloud 인증 확인..."
	@gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null | grep -q . || { echo "[ERROR] gcloud 미인증. 'gcloud auth login' 실행 필요"; exit 1; }
	@echo "[guard] gcloud project 확인..."
	@test "$$(gcloud config get-value project 2>/dev/null)" = "$(PROJECT_ID)" || { echo "[ERROR] gcloud project가 $(PROJECT_ID) 가 아님. 'gcloud config set project $(PROJECT_ID)' 실행 필요"; exit 1; }
	@echo "[guard] OK"

# env drift 가드 — deploy(전체, env-file 영향) 전용. deploy-quick(docker cp, env 무관)은 미적용.
# project_env_drift_guard 사고 재발 방지: SM/VM/로컬 .env 어긋난 상태로 deploy 시 OAuth/서버목록 깨짐.
deploy-env-guard:
	@echo "[env-guard] env 3-way sync-check (local x Secret Manager x VM)..."
	@bash scripts/sync_check.sh >/dev/null 2>&1 || { echo "[ERROR] env drift 감지. 'make sync-check' 로 상세 확인 후 './scripts/sync_env.sh pull' 또는 'push' 로 정렬 필요. drift 상태에서 deploy 시 OAuth/서버목록 깨짐 (project_env_drift_guard)"; exit 1; }
	@echo "[env-guard] OK"

# 봇 빠른 배포
deploy-quick: deploy-guard
	@echo "[1/3] 봇 코드를 VM에 업로드 중..."
	@tar -czf /tmp/bot-upload.tar.gz --exclude='__pycache__' --exclude='*.pyc' run/ main.py
	@gcloud compute scp /tmp/bot-upload.tar.gz $(VM_NAME):~/bot-upload.tar.gz --zone=$(ZONE)
	@echo "[2/3] 컨테이너에 복사 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="mkdir -p ~/bot-upload && tar -xzf ~/bot-upload.tar.gz -C ~/bot-upload && docker cp ~/bot-upload/run/. $(CONTAINER_NAME):/app/run/ && docker cp ~/bot-upload/main.py $(CONTAINER_NAME):/app/main.py && rm -rf ~/bot-upload ~/bot-upload.tar.gz"
	@echo "[3/3] 컨테이너 재시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker restart $(CONTAINER_NAME)"
	@rm -f /tmp/bot-upload.tar.gz
	@echo "봇 빠른 배포 완료!"

# 대시보드 빠른 배포 (프론트+백엔드)
deploy-dashboard-quick: deploy-dashboard-frontend deploy-dashboard-backend
	@echo "대시보드 빠른 배포 완료!"

# 웹패널 빠른 배포 (프론트+백엔드)
deploy-webpanel-quick: deploy-webpanel-frontend deploy-webpanel-backend-quick
	@echo "웹패널 빠른 배포 완료!"

# 웹패널 백엔드 빠른 배포 (Docker 리빌드 없이 코드만 교체)
deploy-webpanel-backend-quick:
	@echo "[1/3] 웹패널 백엔드 코드를 VM에 업로드 중..."
	@tar -czf ./wb-quick.tar.gz --exclude='__pycache__' --exclude='*.pyc' \
		$$(ls -d webpanel/backend/ 2>/dev/null) \
		$$(ls -d run/__init__.py 2>/dev/null) \
		$$(ls -d run/core/ 2>/dev/null) \
		$$(ls -d run/services/__init__.py 2>/dev/null) \
		$$(ls -d run/services/quiz/ 2>/dev/null)
	@gcloud compute scp ./wb-quick.tar.gz $(VM_NAME):~/wb-quick.tar.gz --zone=$(ZONE)
	@echo "[2/3] 컨테이너에 복사 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="mkdir -p ~/wb-quick && tar -xzf ~/wb-quick.tar.gz -C ~/wb-quick && docker cp ~/wb-quick/webpanel/backend/. webpanel-backend:/app/backend/ && docker cp ~/wb-quick/run/. webpanel-backend:/app/run/ && rm -rf ~/wb-quick ~/wb-quick.tar.gz"
	@echo "[3/3] 컨테이너 재시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker restart webpanel-backend"
	@rm -f ./wb-quick.tar.gz
	@echo "웹패널 백엔드 빠른 배포 완료!"

# ============================================================
# 전체 배포 (Docker 이미지 리빌드, 의존성 변경 시)
# ============================================================

# 전체 배포 프로세스
deploy: deploy-guard deploy-env-guard build-local push-image restart
	@echo "배포 완료!"

# 로컬에서 Docker 이미지 빌드 — wrapper가 거짓 exit 0 내는 케이스를 위해 명시적 실패 체크
build-local:
	@echo "로컬에서 Docker 이미지 빌드 중 (linux/amd64)..."
	@docker build --platform linux/amd64 -t $(CONTAINER_NAME) -t $(IMAGE_TAG) . || { echo "[ERROR] docker build 실패"; exit 1; }
	@docker image inspect $(IMAGE_TAG) >/dev/null 2>&1 || { echo "[ERROR] 빌드 결과 이미지($(IMAGE_TAG)) 없음. wrapper가 거짓 성공 보고"; exit 1; }
	@echo "빌드 완료"

# Docker 이미지를 Artifact Registry에 푸시
push-image:
	@echo "Docker 이미지를 Artifact Registry에 푸시 중..."
	@docker push $(IMAGE_TAG) || { echo "[ERROR] docker push 실패. 'gcloud auth configure-docker $(REGION)-docker.pkg.dev' 실행 후 재시도"; exit 1; }
	@echo "푸시 완료"

# 컨테이너 재시작
restart: stop start
	@echo "재시작 완료"

# 컨테이너 중지 및 제거
stop:
	@echo "컨테이너 중지 중..."
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop debi-marlene-bot $(CONTAINER_NAME) 2>/dev/null || true && docker rm debi-marlene-bot $(CONTAINER_NAME) 2>/dev/null || true"
	@echo "중지 완료"

# 새 컨테이너 시작 (SQLite 영속 볼륨 포함)
start:
	@echo "VM에서 최신 이미지 pull 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker pull $(IMAGE_TAG)"
	@echo "컨테이너 시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="mkdir -p /home/2rami/debi-marlene-data && sudo docker run -d --name $(CONTAINER_NAME) -p 5001:5001 --env-file $(VM_PATH)/.env -e BOT_DATA_DIR=/data -v /home/2rami/debi-marlene-data:/data --restart unless-stopped $(IMAGE_TAG)"
	@echo "시작 완료"

# 컨테이너 로그 확인
logs:
	@echo "컨테이너 로그 (Ctrl+C로 종료):"
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f $(CONTAINER_NAME)"

# VM 및 컨테이너 상태 확인
status:
	@echo "VM 상태:"
	gcloud compute instances list --filter="name=$(VM_NAME)"
	@echo ""
	@echo "Docker 컨테이너 상태:"
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker ps -a | grep $(CONTAINER_NAME) || echo '컨테이너 없음'"

# 중지된 컨테이너 및 사용하지 않는 이미지 정리
clean:
	@echo "Docker 및 임시 파일 정리 중..."
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker system prune -f && rm -rf ~/tmp && rm -f ~/$(CONTAINER_NAME).tar"
	@echo "정리 완료"

# VM 봇만 중지 (로컬 테스트 전)
stop-vm:
	@echo "VM 봇 중지 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop $(CONTAINER_NAME) 2>/dev/null || true"
	@echo "VM 봇 중지 완료 (로컬 테스트 가능)"

# VM 봇만 시작 (로컬 테스트 후)
start-vm:
	@echo "VM 봇 시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker start $(CONTAINER_NAME) 2>/dev/null || echo '컨테이너가 없습니다. make deploy를 실행하세요.'"
	@echo "VM 봇 시작 완료"

# 로컬에서 봇 테스트 (VM 봇 자동 중지)
test-local: stop-vm
	@echo "로컬 봇 시작 중..."
	@echo "테스트 종료 후 'make start-vm'을 실행하세요!"
	@PYTHONUNBUFFERED=1 BOT_ENV=local python3 -u main.py

# ============================================================
# Dashboard 배포
# ============================================================

# 대시보드 전체 배포
deploy-dashboard: build-dashboard push-dashboard restart-dashboard
	@echo "대시보드 배포 완료!"

# 대시보드 Docker 이미지 빌드
build-dashboard:
	@echo "봇 모듈 복사 (환영 이미지 생성용)..."
	@rm -rf dashboard/run
	@mkdir -p dashboard/run/core dashboard/run/services/welcome dashboard/run/services/quiz
	@cp run/__init__.py dashboard/run/__init__.py
	@cp run/core/__init__.py dashboard/run/core/__init__.py
	@cp run/core/config.py dashboard/run/core/config.py
	@cp run/services/__init__.py dashboard/run/services/__init__.py
	@cp -r run/services/welcome/* dashboard/run/services/welcome/
	@cp -r run/services/quiz/* dashboard/run/services/quiz/
	@echo "대시보드 Docker 이미지 빌드 중 (linux/amd64)..."
	@docker build --platform linux/amd64 -t $(DASHBOARD_CONTAINER) -t $(DASHBOARD_IMAGE_TAG) ./dashboard
	@rm -rf dashboard/run
	@echo "빌드 완료"

# 대시보드 이미지 푸시
push-dashboard:
	@echo "대시보드 이미지를 Artifact Registry에 푸시 중..."
	@docker push $(DASHBOARD_IMAGE_TAG)
	@echo "푸시 완료"

# 대시보드 재시작
restart-dashboard: stop-dashboard start-dashboard
	@echo "대시보드 재시작 완료"

# 대시보드 중지 및 제거
stop-dashboard:
	@echo "대시보드 중지 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop $(DASHBOARD_CONTAINER) 2>/dev/null || true && docker rm $(DASHBOARD_CONTAINER) 2>/dev/null || true"
	@echo "대시보드 중지 완료"

# 대시보드 시작
start-dashboard:
	@echo "VM에서 대시보드 이미지 pull 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker pull $(DASHBOARD_IMAGE_TAG) && docker image prune -af"
	@echo "대시보드 컨테이너 시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker run -d --name $(DASHBOARD_CONTAINER) --network dashboard-net -p 3080:80 --env-file ~/dashboard.env --restart unless-stopped $(DASHBOARD_IMAGE_TAG)"
	@echo "대시보드 시작 완료"

# 대시보드 로그
logs-dashboard:
	@echo "대시보드 로그 (Ctrl+C로 종료):"
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f $(DASHBOARD_CONTAINER)"

# 루트 .env 의 DISCORD_CLIENT_ID 를 dashboard/frontend/.env.production 에 VITE_DISCORD_CLIENT_ID 로 주입.
# Vite는 빌드 시 .env.production 이 .env 를 override하므로 단일 소스로 관리 가능.
inject-dashboard-env:
	@echo "[env] 루트 .env -> dashboard/frontend/.env.production 주입 중..."
	@set -e; \
	if [ ! -f .env ]; then echo "ERROR: 루트 .env 없음 (DISCORD_CLIENT_ID 포함 필요)"; exit 1; fi; \
	CLIENT_ID=$$(grep -E '^DISCORD_CLIENT_ID=' .env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '[:space:]'); \
	if [ -z "$$CLIENT_ID" ]; then echo "ERROR: DISCORD_CLIENT_ID 가 .env 에 비어있음"; exit 1; fi; \
	{ echo "VITE_API_URL=/api"; echo "VITE_DISCORD_CLIENT_ID=$$CLIENT_ID"; } > dashboard/frontend/.env.production; \
	echo "  -> VITE_DISCORD_CLIENT_ID=$$CLIENT_ID"

# 대시보드 프론트엔드만 배포 (Docker 재빌드 없이 빠른 배포)
deploy-dashboard-frontend: inject-dashboard-env
	@set -euo pipefail; \
	echo "[1/5] 프론트엔드 빌드 중..."; \
	(cd dashboard/frontend && npm run build); \
	test -d dashboard/frontend/dist || { echo "[ERROR] dist 디렉토리 없음 — 빌드 실패"; exit 1; }; \
	echo "[2/5] dist를 tar로 압축..."; \
	tar -czf /tmp/dash-dist.tar.gz -C dashboard/frontend/dist .; \
	echo "[3/5] VM에 업로드 중..."; \
	gcloud compute scp /tmp/dash-dist.tar.gz $(VM_NAME):/tmp/dash-dist.tar.gz --zone=$(ZONE); \
	echo "[4/5] 컨테이너에 복사 + nginx 리로드..."; \
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="mkdir -p ~/dashboard-upload && tar -xzf /tmp/dash-dist.tar.gz -C ~/dashboard-upload && docker cp ~/dashboard-upload/. $(DASHBOARD_CONTAINER):/var/www/dashboard/ && docker exec $(DASHBOARD_CONTAINER) nginx -s reload && rm -rf ~/dashboard-upload /tmp/dash-dist.tar.gz"; \
	rm -f /tmp/dash-dist.tar.gz; \
	echo "[5/5] Cloudflare 캐시 퍼지 중..."; \
	if [ -n "$(CF_API_TOKEN)" ]; then \
		curl -s -X POST "https://api.cloudflare.com/client/v4/zones/49337200d8d2ff73047081d747d42074/purge_cache" \
			-H "Authorization: Bearer $(CF_API_TOKEN)" \
			-H "Content-Type: application/json" \
			--data '{"purge_everything":true}' > /dev/null && echo "캐시 퍼지 완료"; \
	else \
		echo "[WARN] CF_API_TOKEN 미설정 — 캐시 퍼지 스킵 (강제 새로고침 필요)"; \
	fi; \
	echo "대시보드 프론트엔드 배포 완료"

# 대시보드 백엔드만 배포 (Docker 재빌드 없이 빠른 배포)
# dashboard/backend 는 run/core/config.py 등을 import 하므로 run/ 도 같이 동기화한다.
deploy-dashboard-backend:
	@echo "[1/3] 백엔드 + run/ 파일을 VM에 업로드 중..."
	@gcloud compute scp --recurse dashboard/backend $(VM_NAME):~/dashboard-backend-upload --zone=$(ZONE)
	@gcloud compute scp --recurse run $(VM_NAME):~/dashboard-run-upload --zone=$(ZONE)
	@echo "[2/3] 컨테이너에 복사..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker cp ~/dashboard-backend-upload/. $(DASHBOARD_CONTAINER):/app/backend/ && docker cp ~/dashboard-run-upload/. $(DASHBOARD_CONTAINER):/app/run/ && rm -rf ~/dashboard-backend-upload ~/dashboard-run-upload"
	@echo "[3/3] gunicorn 재시작..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker exec $(DASHBOARD_CONTAINER) supervisorctl restart gunicorn"
	@echo "대시보드 백엔드 배포 완료"

# ============================================================
# Webpanel 배포
# ============================================================

# 웹패널 프론트엔드 빌드 + VM 배포
# .ONESHELL 환경에서 cd 가 다음 명령에 누수되던 버그 + tar 실패해도 VM의 sudo rm 이 실행돼 옛 dist 날아가던 침묵 실패 차단
deploy-webpanel-frontend:
	@set -e; \
	echo "[1/4] 프론트엔드 빌드 중..."; \
	(cd webpanel && npm run build) || { echo "[ERROR] webpanel build 실패"; exit 1; }; \
	echo "[2/4] dist를 VM에 업로드 중..."; \
	test -f webpanel/dist/index.html || { echo "[ERROR] webpanel/dist/index.html 없음. 빌드 결과 확인"; exit 1; }; \
	tar -czf /tmp/webpanel-dist.tar.gz -C webpanel/dist . || { echo "[ERROR] tar 실패"; exit 1; }; \
	gcloud compute scp /tmp/webpanel-dist.tar.gz $(VM_NAME):webpanel-dist.tar.gz --zone=$(ZONE) || { echo "[ERROR] scp 실패. VM 의 dist 는 안 건드림 (안전)"; exit 1; }; \
	echo "[3/4] VM에서 배포 중 (nginx 마운트 경로: /home/kasa)..."; \
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="sudo rm -rf /home/kasa/debi-marlene/webpanel/dist/assets/* && sudo rm -f /home/kasa/debi-marlene/webpanel/dist/index.html && sudo tar -xzf ~/webpanel-dist.tar.gz -C /home/kasa/debi-marlene/webpanel/dist/ && sudo chown -R kasa:kasa /home/kasa/debi-marlene/webpanel/dist/ && rm ~/webpanel-dist.tar.gz && sudo docker exec nginx-proxy nginx -s reload"
	@rm -f /tmp/webpanel-dist.tar.gz
	@echo "[4/4] Cloudflare 캐시 퍼지 중..."
	@curl -s -X POST "https://api.cloudflare.com/client/v4/zones/49337200d8d2ff73047081d747d42074/purge_cache" \
		-H "Authorization: Bearer $(CF_API_TOKEN)" \
		-H "Content-Type: application/json" \
		--data '{"purge_everything":true}' > /dev/null
	@echo "웹패널 프론트엔드 배포 완료"

# 웹패널 백엔드 VM 배포 (Docker 이미지 리빌드 방식)
deploy-webpanel-backend:
	@echo "[1/4] 빌드 파일 패키징 중..."
	@rm -rf /tmp/claude/wb-build && mkdir -p /tmp/claude/wb-build/run
	@cp webpanel/Dockerfile.backend /tmp/claude/wb-build/
	@cp webpanel/requirements.txt /tmp/claude/wb-build/
	@cp webpanel/gcs-credentials.json /tmp/claude/wb-build/
	@cp -r webpanel/backend /tmp/claude/wb-build/backend
	@cp run/__init__.py /tmp/claude/wb-build/run/
	@cp -r run/core /tmp/claude/wb-build/run/core
	@mkdir -p /tmp/claude/wb-build/run/services
	@cp run/services/__init__.py /tmp/claude/wb-build/run/services/
	@cp -r run/services/quiz /tmp/claude/wb-build/run/services/quiz
	@tar -czf /tmp/claude/wb-build.tar.gz -C /tmp/claude/wb-build .
	@echo "[2/4] VM에 업로드 + Docker 이미지 빌드 중..."
	@gcloud compute scp /tmp/claude/wb-build.tar.gz $(VM_NAME):~/wb-build.tar.gz --zone=$(ZONE)
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="mkdir -p ~/wb-build && tar -xzf ~/wb-build.tar.gz -C ~/wb-build && cd ~/wb-build && docker build -f Dockerfile.backend -t webpanel-backend:latest . && rm -rf ~/wb-build ~/wb-build.tar.gz"
	@echo "[3/4] 컨테이너 교체 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop webpanel-backend 2>/dev/null || true && docker rm webpanel-backend 2>/dev/null || true && docker run -d --name webpanel-backend -p 8080:8080 --network dashboard-net -v /var/run/docker.sock:/var/run/docker.sock --env-file ~/debi-marlene/.env --restart unless-stopped webpanel-backend:latest"
	@echo "[4/4] 정리 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker image prune -af"
	@rm -rf /tmp/claude/wb-build /tmp/claude/wb-build.tar.gz
	@echo "웹패널 백엔드 배포 완료"

# 웹패널 백엔드 로그
logs-webpanel:
	@echo "웹패널 백엔드 로그 (Ctrl+C로 종료):"
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f webpanel-backend"

# ============================================================
# 솔로봇 배포 (debi-solo, marlene-solo)
# ============================================================
# 기존 데비&마를렌 봇($(CONTAINER_NAME))과 **같은 이미지** 재사용.
# BOT_IDENTITY env만 다르게 주입 → 코드가 내부 분기로 페르소나 설정.
# 볼륨도 같은 /home/2rami/debi-marlene-data 공유 (scope prefix로 행 격리).
# 필요 전제:
#   - VM에 $(VM_PATH)/.env.solo-debi, $(VM_PATH)/.env.solo-marlene 파일이 있어야 함
#   - 각 파일엔 해당 봇의 DISCORD_TOKEN이 들어감 (CLAUDE_API_KEY 등 공통 키는 기존 .env와 동일)
#   - 이미지는 `make deploy`가 이미 push 했다는 전제 (푸시만 다시 하려면 make push-image)

deploy-solo-debi: stop-solo-debi start-solo-debi
	@echo "데비 솔로봇 배포 완료"

deploy-solo-marlene: stop-solo-marlene start-solo-marlene
	@echo "마를렌 솔로봇 배포 완료"

restart-solo-debi: stop-solo-debi start-solo-debi
	@echo "데비 솔로봇 재시작 완료"

restart-solo-marlene: stop-solo-marlene start-solo-marlene
	@echo "마를렌 솔로봇 재시작 완료"

stop-solo-debi:
	@echo "데비 솔로봇 중지 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop $(SOLO_DEBI_NAME) 2>/dev/null || true && docker rm $(SOLO_DEBI_NAME) 2>/dev/null || true"

stop-solo-marlene:
	@echo "마를렌 솔로봇 중지 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop $(SOLO_MARLENE_NAME) 2>/dev/null || true && docker rm $(SOLO_MARLENE_NAME) 2>/dev/null || true"

start-solo-debi:
	@echo "데비 솔로봇 시작 (image=$(IMAGE_TAG), identity=debi)..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker pull $(IMAGE_TAG) >/dev/null && mkdir -p /home/2rami/debi-marlene-data && sudo docker run -d --name $(SOLO_DEBI_NAME) --env-file $(VM_PATH)/.env.solo-debi -e BOT_IDENTITY=debi -e BOT_DATA_DIR=/data -v /home/2rami/debi-marlene-data:/data --restart unless-stopped $(IMAGE_TAG)"

start-solo-marlene:
	@echo "마를렌 솔로봇 시작 (image=$(IMAGE_TAG), identity=marlene)..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker pull $(IMAGE_TAG) >/dev/null && mkdir -p /home/2rami/debi-marlene-data && sudo docker run -d --name $(SOLO_MARLENE_NAME) --env-file $(VM_PATH)/.env.solo-marlene -e BOT_IDENTITY=marlene -e BOT_DATA_DIR=/data -v /home/2rami/debi-marlene-data:/data --restart unless-stopped $(IMAGE_TAG)"

logs-solo-debi:
	@echo "데비 솔로봇 로그 (Ctrl+C 종료):"
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f $(SOLO_DEBI_NAME)"

logs-solo-marlene:
	@echo "마를렌 솔로봇 로그 (Ctrl+C 종료):"
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f $(SOLO_MARLENE_NAME)"

# ============================================================
# Companion-bot (나쵸네코) — geno-companion Managed Agent + Discord DM
# ============================================================
# 메인 봇과 다른 Dockerfile (companion_bot/Dockerfile). 거노 personal 봇.
# 필요 전제:
#   - VM에 $(VM_PATH)/.env.companion 파일 (COMPANION_BOT_TOKEN, OWNER_ID,
#     ANTHROPIC_API_KEY, MANAGED_COMPANION_AGENT_ID, MANAGED_COMPANION_ENV_ID)
#   - 토큰들은 Secret Manager 에서 받아 .env.companion 작성

deploy-companion: build-companion push-companion restart-companion
	@echo "나쵸네코 봇 배포 완료"

build-companion:
	@echo "나쵸네코 Docker 이미지 빌드 중 (linux/amd64)..."
	@docker build --platform linux/amd64 -t $(COMPANION_CONTAINER) -t $(COMPANION_IMAGE_TAG) ./companion_bot
	@echo "빌드 완료"

push-companion:
	@echo "나쵸네코 이미지를 Artifact Registry 에 푸시 중..."
	@docker push $(COMPANION_IMAGE_TAG)
	@echo "푸시 완료"

restart-companion: stop-companion start-companion
	@echo "나쵸네코 봇 재시작 완료"

stop-companion:
	@echo "나쵸네코 봇 중지 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop $(COMPANION_CONTAINER) 2>/dev/null || true && docker rm $(COMPANION_CONTAINER) 2>/dev/null || true"

start-companion:
	@echo "나쵸네코 봇 시작 (image=$(COMPANION_IMAGE_TAG))..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker pull $(COMPANION_IMAGE_TAG) >/dev/null && sudo docker run -d --name $(COMPANION_CONTAINER) --env-file $(VM_PATH)/.env.companion --restart unless-stopped $(COMPANION_IMAGE_TAG)"

logs-companion:
	@echo "나쵸네코 봇 로그 (Ctrl+C 종료):"
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f $(COMPANION_CONTAINER)"

# ============================================================
# env sync-check — 로컬 .env × Secret Manager × VM 해시 비교
# ============================================================
sync-check:
	@bash scripts/sync_check.sh

preflight: sync-check
	@echo "preflight OK — env 일치"
