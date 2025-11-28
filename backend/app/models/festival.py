# backend/app/models/festival.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# API 요청 시 (새 축제 생성)
class FestivalCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, example="서울 재즈 페스티벌")
    description: Optional[str] = Field(None, example="서울에서 열리는 최고의 재즈 페스티벌")
    location: str = Field(..., min_length=1, max_length=200, example="올림픽공원, 송파구")
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', example="2025-05-24")
    end_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', example="2025-05-26")
    time: Optional[str] = Field(None, max_length=50, example="18:00 - 22:00")
    category: str = Field(..., max_length=50, example="페스티벌")
    price: Optional[str] = Field(None, max_length=100, example="무료")
    image_url: Optional[str] = Field(None, max_length=500, example="https://example.com/image.jpg")

# API 응답 시 (ID 및 타임스탬프 포함)
class FestivalResponse(FestivalCreate):
    id: int = Field(..., example=1)
    created_at: datetime
    updated_at: datetime

    class Config:
        # ORM 모델(Entity)과의 호환성 설정
        from_attributes = True

# 축제 업데이트 모델 (모든 필드 선택적)
class FestivalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    time: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)
    price: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
