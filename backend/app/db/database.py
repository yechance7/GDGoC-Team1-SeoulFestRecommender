# backend/app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# DB 엔진 생성
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True
)

# 세션 관리 객체
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 모델의 베이스 클래스
Base = declarative_base()