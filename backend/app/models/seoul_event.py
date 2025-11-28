# backend/app/models/seoul_event.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# API 요청 시 (새 서울 이벤트 생성)
class SeoulEventCreate(BaseModel):
    codename: Optional[str] = Field(None, max_length=50, example="뮤지컬/오페라")
    gu_name: Optional[str] = Field(None, max_length=50, example="송파구")
    title: str = Field(..., min_length=1, max_length=255, example="서울 재즈 페스티벌")

    date_text: Optional[str] = Field(None, example="2025.05.24(토) ~ 2025.05.26(월)")
    place: Optional[str] = Field(None, max_length=255, example="올림픽공원")
    org_name: Optional[str] = Field(None, max_length=255, example="서울시문화재단")
    use_target: Optional[str] = Field(None, example="전 연령")
    use_fee: Optional[str] = Field(None, example="무료")
    inquiry: Optional[str] = Field(None, example="02-1234-5678")
    player: Optional[str] = Field(None, example="출연자 정보")
    program: Optional[str] = Field(None, example="프로그램 소개")
    etc_desc: Optional[str] = Field(None, example="기타 내용")

    org_link: Optional[str] = Field(None, example="https://example.com")
    main_img: Optional[str] = Field(None, example="https://example.com/image.jpg")

    rgst_date: Optional[date] = Field(None, example="2025-01-01")
    ticket_type: Optional[str] = Field(None, max_length=50, example="시민")
    start_date: Optional[date] = Field(None, example="2025-05-24")
    end_date: Optional[date] = Field(None, example="2025-05-26")
    theme_code: Optional[str] = Field(None, max_length=50, example="문화행사")

    lot: Optional[float] = Field(None, example=127.1234)
    lat: Optional[float] = Field(None, example=37.5678)

    is_free: Optional[str] = Field(None, max_length=10, example="무료")
    hmpg_addr: Optional[str] = Field(None, example="https://culture.go.kr/...")
    pro_time: Optional[str] = Field(None, max_length=100, example="14:00~17:00")

# API 응답 시 (ID 포함)
class SeoulEventResponse(SeoulEventCreate):
    id: int = Field(..., example=1)

    class Config:
        # ORM 모델(Entity)과의 호환성 설정
        from_attributes = True

# 이벤트 업데이트 모델 (모든 필드 선택적)
class SeoulEventUpdate(BaseModel):
    codename: Optional[str] = Field(None, max_length=50)
    gu_name: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=255)

    date_text: Optional[str] = None
    place: Optional[str] = Field(None, max_length=255)
    org_name: Optional[str] = Field(None, max_length=255)
    use_target: Optional[str] = None
    use_fee: Optional[str] = None
    inquiry: Optional[str] = None
    player: Optional[str] = None
    program: Optional[str] = None
    etc_desc: Optional[str] = None

    org_link: Optional[str] = None
    main_img: Optional[str] = None

    rgst_date: Optional[date] = None
    ticket_type: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    theme_code: Optional[str] = Field(None, max_length=50)

    lot: Optional[float] = None
    lat: Optional[float] = None

    is_free: Optional[str] = Field(None, max_length=10)
    hmpg_addr: Optional[str] = None
    pro_time: Optional[str] = Field(None, max_length=100)
