# backend/app/entity/festival_entity.py
from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
from app.entity.base_entity import BaseEntity

class Festival(BaseEntity):
    # 테이블 이름
    __tablename__ = "festivals"

    # 기본 정보
    name = Column(String(200), index=True, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=False)

    # 날짜 및 시간
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    end_date = Column(String(10), nullable=False)    # YYYY-MM-DD
    time = Column(String(50), nullable=True)         # HH:MM - HH:MM

    # 카테고리 및 가격
    category = Column(String(50), nullable=False, index=True)  # 페스티벌, 콘서트, 전시회
    price = Column(String(100), nullable=True)

    # 이미지
    image_url = Column(String(500), nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Festival(id={self.id}, name='{self.name}', category='{self.category}')>"