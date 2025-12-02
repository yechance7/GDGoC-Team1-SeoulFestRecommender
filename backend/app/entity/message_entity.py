# backend/app/entity/message_entity.py
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from app.db.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # user 메시지 임베딩만 저장
    related_event_ids = Column(JSON, nullable=True)  # assistant 메시지용
    turn = Column(Integer, nullable=False)  # 대화 내 순서
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
