# Debi Marlene Bot - Makefile
# GCP 설정
PROJECT_ID = ironic-objectivist-465713-a6
VM_NAME = debi-marlene-bot
ZONE = asia-northeast3-a
REGION = asia-northeast3
VM_PATH = ~/debi-marlene
CONTAINER_NAME = debi-marlene
REGISTRY = $(REGION)-docker.pkg.dev/$(PROJECT_ID)/debi-marlene
IMAGE_TAG = $(REGISTRY)/$(CONTAINER_NAME):latest

# Dashboard 설정
DASHBOARD_CONTAINER = debi-marlene-dashboard
DASHBOARD_IMAGE_TAG = $(REGISTRY)/$(DASHBOARD_CONTAINER):latest

.PHONY: help deploy build-local push-image restart stop start logs status clean test-local stop-vm start-vm
.PHONY: deploy-dashboard build-dashboard push-dashboard start-dashboard stop-dashboard restart-dashboard logs-dashboard
.PHONY: deploy-webpanel-frontend deploy-webpanel-backend logs-webpanel

# 기본 명령어 (make 입력 시 도움말 표시)
help:
	@echo "Debi Marlene Bot - 사용 가능한 명령어:"
	@echo ""
	@echo "📦 배포 관련:"
	@echo "  make deploy        - 전체 배포 (로컬 빌드 + Registry Push + 재시작)"
	@echo "  make build-local   - 로컬에서 Docker 이미지 빌드"
	@echo "  make push-image    - Docker 이미지를 Artifact Registry에 푸시"
	@echo ""
	@echo "🔧 VM 제어:"
	@echo "  make restart       - 컨테이너 재시작"
	@echo "  make stop-vm       - VM 봇 중지 (로컬 테스트 전)"
	@echo "  make start-vm      - VM 봇 시작 (로컬 테스트 후)"
	@echo "  make logs          - 컨테이너 로그 확인"
	@echo "  make status        - VM 및 컨테이너 상태 확인"
	@echo ""
	@echo "  [Dashboard]"
	@echo "  make deploy-dashboard   - 대시보드 배포 (빌드 + Push + 시작)"
	@echo "  make stop-dashboard     - 대시보드 중지"
	@echo "  make start-dashboard    - 대시보드 시작"
	@echo "  make restart-dashboard  - 대시보드 재시작"
	@echo "  make logs-dashboard     - 대시보드 로그 확인"
	@echo ""
	@echo "  [Webpanel]"
	@echo "  make deploy-webpanel-frontend  - 웹패널 프론트엔드 빌드 + VM 배포"
	@echo "  make deploy-webpanel-backend   - 웹패널 백엔드 VM 배포"
	@echo "  make logs-webpanel             - 웹패널 백엔드 로그"
	@echo ""
	@echo "  [Test]"
	@echo "  make test-local    - 로컬에서 봇 실행 (VM 봇 자동 중지)"
	@echo ""
	@echo "  [Misc]"
	@echo "  make clean         - 중지된 컨테이너 및 이미지 정리"
	@echo ""

# 전체 배포 프로세스
deploy: build-local push-image restart
	@echo "✅ 배포 완료!"

# 로컬에서 Docker 이미지 빌드
build-local:
	@echo "로컬에서 Docker 이미지 빌드 중 (linux/amd64)..."
	@docker build --platform linux/amd64 -t $(CONTAINER_NAME) -t $(IMAGE_TAG) .
	@echo "빌드 완료"

# Docker 이미지를 Artifact Registry에 푸시
push-image:
	@echo "📤 Docker 이미지를 Artifact Registry에 푸시 중..."
	@docker push $(IMAGE_TAG)
	@echo "✅ 푸시 완료"

# 컨테이너 재시작
restart: stop start
	@echo "✅ 재시작 완료"

# 컨테이너 중지 및 제거
stop:
	@echo "🛑 컨테이너 중지 중..."
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop debi-marlene-bot $(CONTAINER_NAME) 2>/dev/null || true && docker rm debi-marlene-bot $(CONTAINER_NAME) 2>/dev/null || true"
	@echo "✅ 중지 완료"

# 새 컨테이너 시작
start:
	@echo "📥 VM에서 최신 이미지 pull 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker pull $(IMAGE_TAG) && docker image prune -f"
	@echo "🚀 컨테이너 시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker run -d --name $(CONTAINER_NAME) -p 5001:5001 -p 8080:8080 --env-file $(VM_PATH)/.env --restart unless-stopped $(IMAGE_TAG)"
	@echo "✅ 시작 완료"

# 컨테이너 로그 확인
logs:
	@echo "📋 컨테이너 로그 (Ctrl+C로 종료):"
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f $(CONTAINER_NAME)"

# VM 및 컨테이너 상태 확인
status:
	@echo "📊 VM 상태:"
	gcloud compute instances list --filter="name=$(VM_NAME)"
	@echo ""
	@echo "📊 Docker 컨테이너 상태:"
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker ps -a | grep $(CONTAINER_NAME) || echo '컨테이너 없음'"

# 중지된 컨테이너 및 사용하지 않는 이미지 정리
clean:
	@echo "🧹 Docker 및 임시 파일 정리 중..."
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker system prune -f && rm -rf ~/tmp && rm -f ~/$(CONTAINER_NAME).tar"
	@echo "✅ 정리 완료"

# VM 봇만 중지 (로컬 테스트 전)
stop-vm:
	@echo "🛑 VM 봇 중지 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker stop $(CONTAINER_NAME) 2>/dev/null || true"
	@echo "✅ VM 봇 중지 완료 (로컬 테스트 가능)"

# VM 봇만 시작 (로컬 테스트 후)
start-vm:
	@echo "🚀 VM 봇 시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker start $(CONTAINER_NAME) 2>/dev/null || echo '⚠️  컨테이너가 없습니다. make deploy를 실행하세요.'"
	@echo "✅ VM 봇 시작 완료"

# 로컬에서 봇 테스트 (VM 봇 자동 중지)
test-local: stop-vm
	@echo "로컬 봇 시작 중... (venv 자동 활성화)"
	@echo "테스트 종료 후 'make start-vm'을 실행하세요!"
	@bash -c "source venv/bin/activate && python3 main.py"

# ============================================================
# Dashboard 배포
# ============================================================

# 대시보드 전체 배포
deploy-dashboard: build-dashboard push-dashboard restart-dashboard
	@echo "대시보드 배포 완료!"

# 대시보드 Docker 이미지 빌드
build-dashboard:
	@echo "대시보드 Docker 이미지 빌드 중 (linux/amd64)..."
	@docker build --platform linux/amd64 -t $(DASHBOARD_CONTAINER) -t $(DASHBOARD_IMAGE_TAG) ./dashboard
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
		--command="docker pull $(DASHBOARD_IMAGE_TAG) && docker image prune -f"
	@echo "대시보드 컨테이너 시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker run -d --name $(DASHBOARD_CONTAINER) -p 80:80 --env-file ~/dashboard.env --restart unless-stopped $(DASHBOARD_IMAGE_TAG)"
	@echo "대시보드 시작 완료"

# 대시보드 로그
logs-dashboard:
	@echo "대시보드 로그 (Ctrl+C로 종료):"
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f $(DASHBOARD_CONTAINER)"

# ============================================================
# Webpanel 배포
# ============================================================

# 웹패널 프론트엔드 빌드 + VM 배포
deploy-webpanel-frontend:
	@echo "[1/3] 프론트엔드 빌드 중..."
	@cd webpanel && npm run build
	@echo "[2/3] dist를 VM에 업로드 중..."
	@gcloud compute scp --recurse webpanel/dist/* $(VM_NAME):~/webpanel-upload/ --zone=$(ZONE)
	@echo "[3/3] VM에서 배포 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="rm -rf ~/webpanel-dist/* && mv ~/webpanel-upload/* ~/webpanel-dist/ && rmdir ~/webpanel-upload && docker exec nginx-webpanel nginx -s reload"
	@echo "웹패널 프론트엔드 배포 완료"

# 웹패널 백엔드 VM 배포
deploy-webpanel-backend:
	@echo "[1/3] 백엔드를 VM에 업로드 중..."
	@gcloud compute scp --recurse webpanel/backend/* $(VM_NAME):~/webpanel-backend-upload/ --zone=$(ZONE)
	@echo "[2/3] 컨테이너에 복사 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker cp ~/webpanel-backend-upload/. webpanel-backend:/app/ && rm -rf ~/webpanel-backend-upload"
	@echo "[3/3] 백엔드 재시작 중..."
	@gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker restart webpanel-backend"
	@echo "웹패널 백엔드 배포 완료"

# 웹패널 백엔드 로그
logs-webpanel:
	@echo "웹패널 백엔드 로그 (Ctrl+C로 종료):"
	gcloud compute ssh $(VM_NAME) --zone=$(ZONE) \
		--command="docker logs -f webpanel-backend"
