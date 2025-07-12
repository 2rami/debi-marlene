# 데비&마를렌 Discord 봇 Makefile

# 기본 타겟
.DEFAULT_GOAL := help

# 도움말 표시
help:
	@echo "🎮 데비&마를렌 Discord 봇 관리 명령어"
	@echo ""
	@echo "📦 빌드 관련:"
	@echo "  make build     - Docker 이미지 빌드 (캐시 무시)"
	@echo "  make rebuild   - 완전히 새로 빌드 (모든 캐시 삭제)"
	@echo ""
	@echo "🚀 실행 관련:"
	@echo "  make up        - 봇 시작 (백그라운드)"
	@echo "  make down      - 봇 중지"
	@echo "  make restart   - 봇 재시작"
	@echo ""
	@echo "📋 모니터링:"
	@echo "  make logs      - 실시간 로그 보기"
	@echo "  make status    - 컨테이너 상태 확인"
	@echo ""
	@echo "🧹 정리:"
	@echo "  make clean     - 중지된 컨테이너 및 이미지 정리"
	@echo "  make prune     - Docker 시스템 전체 정리"
	@echo ""
	@echo "⚡ 빠른 실행:"
	@echo "  make dev       - 개발용 (빌드 + 실행 + 로그)"
	@echo "  make deploy    - 배포용 (빌드 + 백그라운드 실행)"

# Docker 이미지 빌드
build:
	@echo "🔨 Docker 이미지 빌드 중..."
	docker-compose build --no-cache

# 완전 재빌드 (모든 캐시 삭제)
rebuild:
	@echo "🗑️ 기존 이미지 삭제 및 완전 재빌드..."
	docker-compose down --rmi all --volumes --remove-orphans
	docker-compose build --no-cache --pull

# 봇 시작 (백그라운드)
up:
	@echo "🚀 데비&마를렌 봇 시작..."
	docker-compose up -d

# 봇 중지
down:
	@echo "⏹️ 데비&마를렌 봇 중지..."
	docker-compose down

# 봇 재시작
restart:
	@echo "🔄 데비&마를렌 봇 재시작..."
	docker-compose restart

# 실시간 로그 보기
logs:
	@echo "📋 실시간 로그 확인 중... (Ctrl+C로 종료)"
	docker-compose logs -f

# 최근 로그만 보기
logs-tail:
	@echo "📋 최근 로그 확인..."
	docker-compose logs --tail=50

# 컨테이너 상태 확인
status:
	@echo "📊 컨테이너 상태:"
	docker-compose ps
	@echo ""
	@echo "💾 Docker 이미지:"
	docker images | grep debi-marlene

# 개발용 (빌드 + 실행 + 로그)
dev: build up logs

# 배포용 (빌드 + 백그라운드 실행)
deploy: build up
	@echo "✅ 배포 완료! 'make logs'로 로그 확인 가능"
	@echo "📊 상태 확인: 'make status'"

# 정리 작업
clean:
	@echo "🧹 중지된 컨테이너 및 미사용 이미지 정리..."
	docker container prune -f
	docker image prune -f

# Docker 시스템 전체 정리
prune:
	@echo "⚠️ Docker 시스템 전체 정리 (미사용 리소스 모두 삭제)..."
	@echo "계속하려면 Enter를 누르세요 (취소: Ctrl+C)"
	@read
	docker system prune -af --volumes

# 환경 변수 파일 체크
check-env:
	@if [ ! -f .env ]; then \
		echo "⚠️ .env 파일이 없습니다!"; \
		echo "📝 .env 파일을 생성하고 다음 변수들을 설정하세요:"; \
		echo "  DISCORD_TOKEN=your_discord_bot_token"; \
		echo "  CLAUDE_API_KEY=your_claude_api_key"; \
		echo "  YOUTUBE_API_KEY=your_youtube_api_key"; \
		exit 1; \
	else \
		echo "✅ .env 파일 확인됨"; \
	fi

# 컨테이너 접속 (디버깅용)
shell:
	@echo "🐚 컨테이너에 접속... (exit로 종료)"
	docker-compose exec debi-marlene-bot /bin/bash

# 빠른 업데이트 (코드 변경 후)
update: down build up
	@echo "✅ 업데이트 완료!"

# .PHONY 선언 (실제 파일과 충돌 방지)
.PHONY: help build rebuild up down restart logs logs-tail status dev deploy clean prune check-env shell update