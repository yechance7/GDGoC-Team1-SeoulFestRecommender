# backend/app/entity/festival_like_entity.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from datetime import datetime
from app.entity.base_entity import BaseEntity

class FestivalLike(BaseEntity):
    """
    사용자가 축제를 찜한 정보를 저장하는 테이블
    """
    __tablename__ = "festival_likes"

    # 외래키
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    festival_id = Column(Integer, ForeignKey("festivals.id", ondelete="CASCADE"), nullable=False, index=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 유니크 제약: 한 사용자가 같은 축제를 중복으로 찜할 수 없음
    __table_args__ = (
        UniqueConstraint('user_id', 'festival_id', name='uq_user_festival_like'),
    )

    def __repr__(self):
        return f"<FestivalLike(user_id={self.user_id}, festival_id={self.festival_id})>"
