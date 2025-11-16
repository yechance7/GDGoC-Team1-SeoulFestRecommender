# backend/app/entity/festival_entity.py
from sqlalchemy import Column, String
from app.entity.base_entity import BaseEntity

class Festival(BaseEntity):
    # 테이블 이름
    __tablename__ = "festivals"

    # 컬럼 정의
    name = Column(String, index=True, nullable=False)
    location = Column(String)
    start_date = Column(String) # 날짜 처리는 필요에 따라 Date 타입으로 변경 가능
    end_date = Column(String)

    def __repr__(self):
        return f"<Festival(name='{self.name}', location='{self.location}')>"