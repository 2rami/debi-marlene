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

.PHONY: help deploy build-local push-image restart stop start logs status clean test-local stop-vm start-vm

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
	@echo "🧪 로컬 테스트:"
	@echo "  make test-local    - 로컬에서 봇 실행 (VM 봇 자동 중지)"
	@echo ""
	@echo "🧹 기타:"
	@echo "  make clean         - 중지된 컨테이너 및 이미지 정리"
	@echo ""

# 전체 배포 프로세스
deploy: build-local push-image restart
	@echo "✅ 배포 완료!"

# 로컬에서 Docker 이미지 빌드
build-local:
	@echo "🔨 로컬에서 Docker 이미지 빌드 중 (linux/amd64)..."
	@DOCKER_BUILDKIT=1 docker build --platform linux/amd64 -t $(CONTAINER_NAME) -t $(IMAGE_TAG) .
	@echo "✅ 빌드 완료"

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
		--command="docker run -d --name $(CONTAINER_NAME) -p 5001:5001 -p 8080:8080 --restart unless-stopped $(IMAGE_TAG)"
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
	@echo "🧪 로컬 봇 시작 중..."
	@echo "⚠️  테스트 종료 후 'make start-vm'을 실행하세요!"
	@python3 main.py
