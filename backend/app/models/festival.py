# backend/app/models/festival.py
from pydantic import BaseModel, Field

# API 요청 시 (새 축제 생성)
class FestivalCreate(BaseModel):
    name: str = Field(..., example="서울 재즈 페스티벌")
    location: str = Field(..., example="올림픽공원")
    start_date: str = Field(..., example="2025-05-24")
    end_date: str = Field(..., example="2025-05-26")

# API 응답 시 (ID 포함)
class FestivalResponse(FestivalCreate):
    id: int = Field(..., example=1)
    
    class Config:
        # ORM 모델(Entity)과의 호환성 설정
        from_attributes = True