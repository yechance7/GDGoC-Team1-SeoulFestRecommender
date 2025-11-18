# backend/app/entity/base_entity.py
from sqlalchemy import Column, Integer
from app.db.database import Base

class BaseEntity(Base):
    __abstract__ = True
    
    # 모든 테이블이 가질 기본 ID 컬럼
    id = Column(Integer, primary_key=True, index=True)