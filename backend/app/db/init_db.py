# backend/app/db/init_db.py
from app.db.database import engine, Base, SessionLocal
from app.entity.seoul_event_entity import SeoulEvent
from app.entity.user_entity import User
from app.entity.seoul_event_like_entity import SeoulEventLike
from datetime import date
from sqlalchemy import text

def init_db():
    db = SessionLocal()
    try:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        print("✅ pgvector 확장 활성화 완료.")
        
        Base.metadata.create_all(bind=engine)
        
        print("✅ DB 스키마 초기화 완료.")
        
    except Exception as e:
        db.rollback()
        print(f"DB 초기화 중 오류 발생: {e}")
    finally:
        db.close()
