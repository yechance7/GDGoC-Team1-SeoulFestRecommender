# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.db.init_db import init_db
from app.api import seoul_event, auth
from app.core.config import settings
from app.services.collect_event import fetch_page, sync_seoul_events

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 서버 시작 및 종료 시 실행할 작업 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시: 데이터베이스 초기화 (테이블 생성 및 초기 데이터 삽입)
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization complete.")
    yield
    # 서버 종료 시: 필요한 정리 작업 수행 (없으면 생략 가능)
    logger.info("Application shutting down.")


app = FastAPI(
    title="Seoul Fest Recommender",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 - 프론트엔드에서 백엔드 API에 접근할 수 있도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js 기본 포트
        "http://localhost:3001",  # 추가 포트 (필요시)
        "http://localhost:3010",  # 사용자의 프론트엔드 포트
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3010",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(seoul_event.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Seoul Festival Recommender API"}

# 서울시 문화행사 데이터 동기화 수동 테스트용
@app.get("/seoul-events")
def get_seoul_events():
    fetch_page(1, 2)

@app.post("/sync-seoul-events")
def sync_seoul_events_endpoint():
    try:
        saved = sync_seoul_events()
        return {"message": "ok", "saved": saved}
    except Exception as e:
        logger.exception("Failed to sync seoul events: %s", e)
        raise