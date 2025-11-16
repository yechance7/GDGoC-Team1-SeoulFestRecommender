# ==============================================================================
# GDGOC-Team1-SeoulFestRecommender Makefile
# 프로젝트 빌드, 실행, DB 관리를 위한 자동화 스크립트
# ==============================================================================

.PHONY: setup shell build run stop clean

# --------------------------
# 1. 초기 설정 및 환경
# --------------------------

# .env 파일을 환경 변수로 로드합니다. (Docker Compose에서 자동으로 처리되므로, 개발 환경용)
include .env

# Poetry 가상 환경 초기 설정 및 의존성 설치 (처음 1회)
setup:
	@echo "✨ 0. Rust 컴파일러 설치 (tokenizers 빌드용)..."
	@echo "--- 이 단계는 인터넷 연결이 필요하며, rustup이 설치되지 않은 경우에만 실행됩니다. ---"
	/bin/bash -c "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && . $$HOME/.cargo/env"
	@echo "✅ Rust 설치 완료."
	@echo "✨ 1. Poetry 가상 환경 설정 및 의존성 설치 중..."
	@poetry env use 3.11
	@poetry install

# 🌟 Poetry 가상 환경 쉘 활성화 (재접속)
shell:
	@echo "🐚 Poetry 가상 환경 쉘로 진입합니다. (종료하려면 'exit' 입력)"
	@poetry shell

# Docker 이미지 빌드
build:
	docker-compose build

# 통합 서비스 실행 (DB, Backend)
run:
	docker-compose up --build -d

# 서비스 중지
stop:
	docker-compose down

# Docker 볼륨 및 이미지 정리
clean:
	docker-compose down -v --rmi all
