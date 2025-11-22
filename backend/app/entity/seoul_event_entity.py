# backend/app/entity/seoul_event_entity.py
from sqlalchemy import (
    Column, Integer, String, Text, Date, Float,
    UniqueConstraint
)
from app.db.database import Base

class SeoulEvent(Base):
    __tablename__ = "seoul_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    codename   = Column(String(50))    # 분류
    gu_name    = Column(String(50))    # 자치구
    title      = Column(String(255), nullable=False)  # 공연/행사명

    date_text  = Column(Text)          # DATE (원문 문자열)
    place      = Column(String(255))   # 장소
    org_name   = Column(String(255))   # 기관명
    use_target = Column(Text)          # 이용대상
    use_fee    = Column(Text)          # 이용요금
    inquiry    = Column(Text)          # 문의
    player     = Column(Text)          # 출연자정보
    program    = Column(Text)          # 프로그램소개
    etc_desc   = Column(Text)          # 기타내용

    org_link   = Column(Text)          # 홈페이지 주소
    main_img   = Column(Text)          # 대표이미지

    rgst_date  = Column(Date)          # 신청일
    ticket_type = Column(String(50))   # 시민/기관
    start_date = Column(Date)          # 시작일
    end_date   = Column(Date)          # 종료일
    theme_code = Column(String(50))    # 테마분류

    lot        = Column(Float)         # 경도(Y)
    lat        = Column(Float)         # 위도(X)

    is_free    = Column(String(10))    # 유무료
    hmpg_addr  = Column(Text)          # 문화포털상세URL
    pro_time   = Column(String(100))   # 행사시간

    __table_args__ = (
        # "새로운 데이터만 적재"를 위해 중복 기준 설정
        UniqueConstraint("title", "start_date", "place", name="uq_seoul_events_title_start_place"),
    )
