# backend/app/entity/conversation_entity.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.db.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def touch(self):
        self.updated_at = datetime.utcnow()
