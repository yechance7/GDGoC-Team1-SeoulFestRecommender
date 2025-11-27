# backend/app/models/festival.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# API 요청 시 (새 이벤트 생성)
class FestivalCreate(BaseModel):
    title: str = Field(..., example="서울 재즈 페스티벌")
    codename: Optional[str] = Field(None, example="문화행사")
    gu_name: Optional[str] = Field(None, example="송파구")
    date_text: Optional[str] = Field(None, example="2025-05-24 ~ 2025-05-26")
    place: Optional[str] = Field(None, example="올림픽공원")
    org_name: Optional[str] = Field(None, example="서울시")
    use_target: Optional[str] = Field(None, example="전체")
    use_fee: Optional[str] = Field(None, example="무료")
    inquiry: Optional[str] = Field(None, example="02-1234-5678")
    player: Optional[str] = Field(None, example="출연자 정보")
    program: Optional[str] = Field(None, example="프로그램 소개")
    etc_desc: Optional[str] = Field(None, example="기타 내용")
    org_link: Optional[str] = Field(None, example="http://example.com")
    main_img: Optional[str] = Field(None, example="http://example.com/image.jpg")
    rgst_date: Optional[date] = Field(None, example="2025-01-01")
    ticket_type: Optional[str] = Field(None, example="시민")
    start_date: Optional[date] = Field(None, example="2025-05-24")
    end_date: Optional[date] = Field(None, example="2025-05-26")
    theme_code: Optional[str] = Field(None, example="음악")
    lot: Optional[float] = Field(None, example=127.123)
    lat: Optional[float] = Field(None, example=37.456)
    is_free: Optional[str] = Field(None, example="무료")
    hmpg_addr: Optional[str] = Field(None, example="http://culture.go.kr")
    pro_time: Optional[str] = Field(None, example="14:00~18:00")

# API 응답 시 (ID 포함)
class FestivalResponse(FestivalCreate):
    id: int = Field(..., example=1)

    class Config:
        # ORM 모델(Entity)과의 호환성 설정
        from_attributes = True

