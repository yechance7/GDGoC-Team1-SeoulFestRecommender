# backend/app/core/dependencies.py
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging
from app.db.database import SessionLocal
from app.core.security import verify_token
from app.repository.user_repo import UserRepository
from app.entity.user_entity import User

# HTTPBearer를 사용한 JWT 토큰 인증
security = HTTPBearer()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_db() -> Generator:
    """
    DB 세션을 생성하고 API 요청 완료 후 닫아주는 의존성 주입 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    JWT 토큰을 검증하고 현재 사용자를 반환하는 의존성 함수

    Args:
        credentials: HTTP Authorization 헤더에서 추출한 JWT 토큰
        db: 데이터베이스 세션

    Returns:
        User: 현재 로그인된 사용자 객체

    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우
    """
    token = credentials.credentials
    logger.info(f"Verifying token: {token[:20]}...")

    # 토큰 검증 및 사용자 ID 추출
    user_id = verify_token(token)
    logger.info(f"Extracted user_id from token: {user_id} (type: {type(user_id)})")

    if user_id is None:
        logger.error("Token verification failed - user_id is None")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보입니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 사용자 ID로 사용자 조회
    logger.info(f"Looking up user with id: {user_id}")
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if user is None:
        logger.error(f"User not found in database with id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    logger.info(f"User authenticated successfully: id={user.id}, username={user.username}")
    return user