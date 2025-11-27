# backend/app/repository/user_repo.py
from sqlalchemy.orm import Session
from typing import Optional
from app.entity.user_entity import User
from app.repository.base_repo import BaseRepository
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자 조회

        Args:
            email: 사용자 이메일

        Returns:
            Optional[User]: 사용자 객체 또는 None
        """
        return self.db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """
        사용자 이름으로 사용자 조회

        Args:
            username: 사용자 이름

        Returns:
            Optional[User]: 사용자 객체 또는 None
        """
        return self.db.query(self.model).filter(self.model.username == username).first()

    def create_user(self, email: str, username: str, password_hash: str) -> User:
        """
        새로운 사용자 생성

        Args:
            email: 사용자 이메일
            username: 사용자 이름
            password_hash: 해시된 비밀번호

        Returns:
            User: 생성된 사용자 객체
        """

        logger.info(f"Creating user with email: {email}, username: {username}, password_hash: {password_hash}")
        user_data = {
            "email": email,
            "username": username,
            "password_hash": password_hash
        }
        return self.create(user_data)
