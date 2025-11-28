# backend/app/entity/seoul_event_like_entity.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from datetime import datetime
from app.entity.base_entity import BaseEntity

class SeoulEventLike(BaseEntity):
    """
    사용자가 서울 이벤트를 찜한 정보를 저장하는 테이블
    """
    __tablename__ = "seoul_event_likes"

    # 외래키
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    seoul_event_id = Column(Integer, ForeignKey("seoul_events.id", ondelete="CASCADE"), nullable=False, index=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 유니크 제약: 한 사용자가 같은 이벤트를 중복으로 찜할 수 없음
    __table_args__ = (
        UniqueConstraint('user_id', 'seoul_event_id', name='uq_user_seoul_event_like'),
    )

    def __repr__(self):
        return f"<SeoulEventLike(user_id={self.user_id}, seoul_event_id={self.seoul_event_id})>"
