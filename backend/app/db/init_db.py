# backend/app/db/init_db.py
from app.db.database import engine, Base, SessionLocal
from app.entity.festival_entity import Festival
from app.entity.user_entity import User
from app.entity.festival_like_entity import FestivalLike

def init_db():
    # 1. 모든 테이블 생성 (Base에 등록된 모든 entity/model)
    # 이미 존재하면 무시됨
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 2. 초기 데이터 삽입 (예시)
        if db.query(Festival).count() == 0:
            sample_festivals = [
                Festival(
                    name="서울 불꽃축제",
                    description="가을 밤하늘을 수놓는 화려한 불꽃쇼",
                    location="여의도 한강공원, 영등포구",
                    start_date="2025-10-05",
                    end_date="2025-10-05",
                    time="19:30 - 21:00",
                    category="페스티벌",
                    price="무료",
                    image_url=None
                ),
                Festival(
                    name="월드 디제이 페스티벌",
                    description="세계 최정상급 DJ들이 한자리에 모이는 EDM 페스티벌",
                    location="잠실 올림픽주경기장, 송파구",
                    start_date="2025-06-01",
                    end_date="2025-06-03",
                    time="18:00 - 23:00",
                    category="페스티벌",
                    price="전일권 120,000원",
                    image_url=None
                ),
                Festival(
                    name="서울 재즈 페스티벌",
                    description="도심 속에서 즐기는 감성 재즈 공연",
                    location="올림픽공원, 송파구",
                    start_date="2025-05-24",
                    end_date="2025-05-26",
                    time="17:00 - 22:00",
                    category="콘서트",
                    price="1일권 80,000원",
                    image_url=None
                ),
                Festival(
                    name="서울 빛초롱축제",
                    description="청계천을 밝히는 아름다운 등불 축제",
                    location="청계천, 종로구",
                    start_date="2025-11-01",
                    end_date="2025-12-20",
                    time="17:00 - 23:00",
                    category="페스티벌",
                    price="무료",
                    image_url=None
                ),
                Festival(
                    name="국립현대미술관 특별전",
                    description="현대미술의 거장들을 만나다",
                    location="국립현대미술관 서울관, 종로구",
                    start_date="2025-03-01",
                    end_date="2025-06-30",
                    time="10:00 - 18:00",
                    category="전시회",
                    price="5,000원",
                    image_url=None
                ),
            ]
            db.add_all(sample_festivals)
            db.commit()
            print(f"{len(sample_festivals)}개의 샘플 축제 데이터 삽입 완료.")
        else:
            print("데이터베이스에 이미 축제 데이터가 존재하여 초기 삽입을 건너뜁니다.")
    except Exception as e:
        db.rollback()
        print(f"DB 초기화 중 오류 발생: {e}")
    finally:
        db.close()