# backend/app/db/init_db.py
from app.db.database import engine, Base, SessionLocal
from app.entity.festival_entity import Festival

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
                    location="여의도 한강공원", 
                    start_date="2025-10-05", 
                    end_date="2025-10-05"
                ),
                Festival(
                    name="월드 디제이 페스티벌", 
                    location="잠실 올림픽주경기장", 
                    start_date="2025-06-01", 
                    end_date="2025-06-03"
                ),
            ]
            db.add_all(sample_festivals)
            db.commit()
            print("2개의 샘플 축제 데이터 삽입 완료.")
        else:
            print("데이터베이스에 이미 데이터가 존재하여 초기 삽입을 건너뜁니다.")
    except Exception as e:
        db.rollback()
        print(f"DB 초기화 중 오류 발생: {e}")
    finally:
        db.close()