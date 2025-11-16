# backend/app/repository/base_repo.py
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional

# Generic T 정의
T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def get_by_id(self, item_id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == item_id).first()

    def create(self, item_data: dict) -> T:
        db_item = self.model(**item_data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item