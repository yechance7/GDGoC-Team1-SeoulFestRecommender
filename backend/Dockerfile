# backend/Dockerfile

# 공식 Python 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (psycopg2를 위해 필요)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install poetry

# 의존성 파일 복사 및 설치
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --only main

# 애플리케이션 코드 복사
COPY . /app

# 서버가 8000 포트에서 실행됨을 노출
EXPOSE 8000