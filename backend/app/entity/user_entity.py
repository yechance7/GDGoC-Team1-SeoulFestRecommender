# backend/app/entity/user_entity.py
from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from app.entity.base_entity import BaseEntity

class User(BaseEntity):
    __tablename__ = "users"

    # 사용자 기본 정보
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
