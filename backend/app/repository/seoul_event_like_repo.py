# backend/app/repository/seoul_event_like_repo.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.entity.seoul_event_like_entity import SeoulEventLike
from app.entity.seoul_event_entity import SeoulEvent
from app.repository.base_repo import BaseRepository
import logging

logger = logging.getLogger(__name__)

class SeoulEventLikeRepository(BaseRepository[SeoulEventLike]):
    def __init__(self, db: Session):
        super().__init__(SeoulEventLike, db)

    def add_like(self, user_id: int, seoul_event_id: int) -> Optional[SeoulEventLike]:
        """
        사용자가 이벤트를 찜하기 추가

        Args:
            user_id: 사용자 ID
            seoul_event_id: 이벤트 ID

        Returns:
            SeoulEventLike: 생성된 찜하기 객체 또는 None (중복 시)
        """
        try:
            like_data = {
                "user_id": user_id,
                "seoul_event_id": seoul_event_id
            }
            like = self.create(like_data)
            logger.info(f"User {user_id} liked seoul event {seoul_event_id}")
            return like
        except IntegrityError as e:
            self.db.rollback()
            logger.warning(f"User {user_id} already liked seoul event {seoul_event_id}: {e}")
            return None

    def remove_like(self, user_id: int, seoul_event_id: int) -> bool:
        """
        사용자가 이벤트 찜하기 취소

        Args:
            user_id: 사용자 ID
            seoul_event_id: 이벤트 ID

        Returns:
            bool: 삭제 성공 여부
        """
        like = self.db.query(SeoulEventLike).filter(
            SeoulEventLike.user_id == user_id,
            SeoulEventLike.seoul_event_id == seoul_event_id
        ).first()

        if like:
            self.db.delete(like)
            self.db.commit()
            logger.info(f"User {user_id} unliked seoul event {seoul_event_id}")
            return True
        else:
            logger.warning(f"Like not found for user {user_id} and seoul event {seoul_event_id}")
            return False

    def is_liked(self, user_id: int, seoul_event_id: int) -> bool:
        """
        사용자가 특정 이벤트를 찜했는지 확인

        Args:
            user_id: 사용자 ID
            seoul_event_id: 이벤트 ID

        Returns:
            bool: 찜했으면 True, 아니면 False
        """
        like = self.db.query(SeoulEventLike).filter(
            SeoulEventLike.user_id == user_id,
            SeoulEventLike.seoul_event_id == seoul_event_id
        ).first()

        return like is not None

    def get_user_liked_events(self, user_id: int, skip: int = 0, limit: int = 100) -> List[SeoulEvent]:
        """
        사용자가 찜한 이벤트 목록 조회

        Args:
            user_id: 사용자 ID
            skip: 페이징 오프셋
            limit: 페이징 리밋

        Returns:
            List[SeoulEvent]: 찜한 이벤트 목록
        """
        events = self.db.query(SeoulEvent).join(
            SeoulEventLike,
            SeoulEvent.id == SeoulEventLike.seoul_event_id
        ).filter(
            SeoulEventLike.user_id == user_id
        ).order_by(
            SeoulEventLike.created_at.desc()  # 최근 찜한 순서대로
        ).offset(skip).limit(limit).all()

        logger.info(f"User {user_id} has {len(events)} liked events")
        return events

    def get_liked_event_ids(self, user_id: int) -> List[int]:
        """
        사용자가 찜한 이벤트 ID 목록 조회

        Args:
            user_id: 사용자 ID

        Returns:
            List[int]: 찜한 이벤트 ID 목록
        """
        likes = self.db.query(SeoulEventLike.seoul_event_id).filter(
            SeoulEventLike.user_id == user_id
        ).all()

        return [like.seoul_event_id for like in likes]
