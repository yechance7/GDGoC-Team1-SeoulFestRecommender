# backend/app/repository/festival_like_repo.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.entity.festival_like_entity import FestivalLike
from app.entity.festival_entity import Festival
from app.repository.base_repo import BaseRepository
import logging

logger = logging.getLogger(__name__)

class FestivalLikeRepository(BaseRepository[FestivalLike]):
    def __init__(self, db: Session):
        super().__init__(FestivalLike, db)

    def add_like(self, user_id: int, festival_id: int) -> Optional[FestivalLike]:
        """
        사용자가 축제를 찜하기 추가

        Args:
            user_id: 사용자 ID
            festival_id: 축제 ID

        Returns:
            FestivalLike: 생성된 찜하기 객체 또는 None (중복 시)
        """
        try:
            like_data = {
                "user_id": user_id,
                "festival_id": festival_id
            }
            like = self.create(like_data)
            logger.info(f"User {user_id} liked festival {festival_id}")
            return like
        except IntegrityError as e:
            self.db.rollback()
            logger.warning(f"User {user_id} already liked festival {festival_id}: {e}")
            return None

    def remove_like(self, user_id: int, festival_id: int) -> bool:
        """
        사용자가 축제 찜하기 취소

        Args:
            user_id: 사용자 ID
            festival_id: 축제 ID

        Returns:
            bool: 삭제 성공 여부
        """
        like = self.db.query(FestivalLike).filter(
            FestivalLike.user_id == user_id,
            FestivalLike.festival_id == festival_id
        ).first()

        if like:
            self.db.delete(like)
            self.db.commit()
            logger.info(f"User {user_id} unliked festival {festival_id}")
            return True
        else:
            logger.warning(f"Like not found for user {user_id} and festival {festival_id}")
            return False

    def is_liked(self, user_id: int, festival_id: int) -> bool:
        """
        사용자가 특정 축제를 찜했는지 확인

        Args:
            user_id: 사용자 ID
            festival_id: 축제 ID

        Returns:
            bool: 찜했으면 True, 아니면 False
        """
        like = self.db.query(FestivalLike).filter(
            FestivalLike.user_id == user_id,
            FestivalLike.festival_id == festival_id
        ).first()

        return like is not None

    def get_user_liked_festivals(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Festival]:
        """
        사용자가 찜한 축제 목록 조회

        Args:
            user_id: 사용자 ID
            skip: 페이징 오프셋
            limit: 페이징 리밋

        Returns:
            List[Festival]: 찜한 축제 목록
        """
        festivals = self.db.query(Festival).join(
            FestivalLike,
            Festival.id == FestivalLike.festival_id
        ).filter(
            FestivalLike.user_id == user_id
        ).order_by(
            FestivalLike.created_at.desc()  # 최근 찜한 순서대로
        ).offset(skip).limit(limit).all()

        logger.info(f"User {user_id} has {len(festivals)} liked festivals")
        return festivals

    def get_liked_festival_ids(self, user_id: int) -> List[int]:
        """
        사용자가 찜한 축제 ID 목록 조회

        Args:
            user_id: 사용자 ID

        Returns:
            List[int]: 찜한 축제 ID 목록
        """
        likes = self.db.query(FestivalLike.festival_id).filter(
            FestivalLike.user_id == user_id
        ).all()

        return [like.festival_id for like in likes]
