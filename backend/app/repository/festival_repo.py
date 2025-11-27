# backend/app/repository/festival_repo.py
from sqlalchemy.orm import Session
from app.entity.seoul_event_entity import SeoulEvent
from app.repository.base_repo import BaseRepository

class FestivalRepository(BaseRepository[SeoulEvent]):
    def __init__(self, db: Session):
        super().__init__(SeoulEvent, db)

    # 여기에 SeoulEvent 테이블 전용의 복잡한 쿼리 메서드를 추가할 수 있습니다.
    def find_by_title(self, title: str):
        return self.db.query(self.model).filter(self.model.title == title).first()