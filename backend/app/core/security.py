# backend/app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Passlib 컨텍스트 설정 (bcrypt 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력된 평문 비밀번호와 해시된 비밀번호를 비교

    Args:
        plain_password: 사용자가 입력한 평문 비밀번호
        hashed_password: 데이터베이스에 저장된 해시된 비밀번호

    Returns:
        bool: 비밀번호가 일치하면 True, 아니면 False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    평문 비밀번호를 해시로 변환

    Args:
        password: 평문 비밀번호

    Returns:
        str: 해시된 비밀번호
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (예: {"sub": 123})
        expires_delta: 토큰 만료 시간 (기본값: settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        str: 생성된 JWT 토큰
    """
    to_encode = data.copy()

    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # sub 값을 문자열로 변환 (JWT 표준)
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])

    logger.info(f"Creating token with payload: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt

def verify_token(token: str) -> Optional[int]:
    """
    JWT 토큰을 검증하고 사용자 ID 추출

    Args:
        token: JWT 토큰

    Returns:
        Optional[int]: 토큰이 유효하면 사용자 ID 반환, 아니면 None
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id_str = payload.get("sub")
        logger.info(f"Token payload: {payload}")

        if user_id_str is None:
            logger.warning("Token payload does not contain 'sub' field")
            return None

        # sub를 int로 변환 (JWT는 문자열로 저장됨)
        try:
            user_id = int(user_id_str)
            logger.info(f"Extracted user_id: {user_id}")
            return user_id
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to convert user_id to int: {user_id_str}, error: {e}")
            return None

    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        return None
