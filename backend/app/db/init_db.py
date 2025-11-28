# backend/app/db/init_db.py
from app.db.database import engine, Base, SessionLocal
from app.entity.seoul_event_entity import SeoulEvent
from app.entity.user_entity import User
from app.entity.seoul_event_like_entity import SeoulEventLike
from datetime import date

def init_db():
    # 1. 모든 테이블 생성 (Base에 등록된 모든 entity/model)
    # 이미 존재하면 무시됨
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 2. 초기 데이터 삽입 (예시)
        if db.query(SeoulEvent).count() == 0:
            sample_events = [
                SeoulEvent(
                    title="서울 불꽃축제",
                    codename="페스티벌",
                    gu_name="영등포구",
                    place="여의도 한강공원",
                    start_date=date(2025, 10, 5),
                    end_date=date(2025, 10, 5),
                    pro_time="19:30 - 21:00",
                    is_free="무료",
                    program="가을 밤하늘을 수놓는 화려한 불꽃쇼",
                    main_img=None
                ),
                SeoulEvent(
                    title="월드 디제이 페스티벌",
                    codename="페스티벌",
                    gu_name="송파구",
                    place="잠실 올림픽주경기장",
                    start_date=date(2025, 6, 1),
                    end_date=date(2025, 6, 3),
                    pro_time="18:00 - 23:00",
                    is_free="유료",
                    use_fee="전일권 120,000원",
                    program="세계 최정상급 DJ들이 한자리에 모이는 EDM 페스티벌",
                    main_img=None
                ),
                SeoulEvent(
                    title="서울 재즈 페스티벌",
                    codename="콘서트",
                    gu_name="송파구",
                    place="올림픽공원",
                    start_date=date(2025, 5, 24),
                    end_date=date(2025, 5, 26),
                    pro_time="17:00 - 22:00",
                    is_free="유료",
                    use_fee="1일권 80,000원",
                    program="도심 속에서 즐기는 감성 재즈 공연",
                    main_img=None
                ),
                SeoulEvent(
                    title="서울 빛초롱축제",
                    codename="페스티벌",
                    gu_name="종로구",
                    place="청계천",
                    start_date=date(2025, 11, 1),
                    end_date=date(2025, 12, 20),
                    pro_time="17:00 - 23:00",
                    is_free="무료",
                    program="청계천을 밝히는 아름다운 등불 축제",
                    main_img=None
                ),
                SeoulEvent(
                    title="국립현대미술관 특별전",
                    codename="전시회",
                    gu_name="종로구",
                    place="국립현대미술관 서울관",
                    start_date=date(2025, 3, 1),
                    end_date=date(2025, 6, 30),
                    pro_time="10:00 - 18:00",
                    is_free="유료",
                    use_fee="5,000원",
                    program="현대미술의 거장들을 만나다",
                    main_img=None
                ),
            ]
            db.add_all(sample_events)
            db.commit()
            print(f"{len(sample_events)}개의 샘플 서울 이벤트 데이터 삽입 완료.")
        else:
            print("데이터베이스에 이미 서울 이벤트 데이터가 존재하여 초기 삽입을 건너뜁니다.")
    except Exception as e:
        db.rollback()
        print(f"DB 초기화 중 오류 발생: {e}")
    finally:
        db.close()
