# backend/app/core/dependencies.py
from typing import Generator
from app.db.database import SessionLocal

def get_db() -> Generator:
    """
    DB 세션을 생성하고 API 요청 완료 후 닫아주는 의존성 주입 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()