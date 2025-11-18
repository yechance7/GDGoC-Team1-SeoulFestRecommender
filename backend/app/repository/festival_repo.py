# backend/app/repository/festival_repo.py
from sqlalchemy.orm import Session
from app.entity.festival_entity import Festival
from app.repository.base_repo import BaseRepository

class FestivalRepository(BaseRepository[Festival]):
    def __init__(self, db: Session):
        super().__init__(Festival, db)
    
    # 여기에 Festival 테이블 전용의 복잡한 쿼리 메서드를 추가할 수 있습니다.
    def find_by_name(self, name: str):
        return self.db.query(self.model).filter(self.model.name == name).first()