# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import logging
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.models.festival import FestivalResponse
from app.repository.user_repo import UserRepository
from app.repository.festival_like_repo import FestivalLikeRepository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.dependencies import get_db, get_current_user
from app.entity.user_entity import User

router = APIRouter(tags=["Authentication"])

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    회원가입 엔드포인트

    - **email**: 사용자 이메일 (고유값)
    - **username**: 사용자 이름 (고유값, 3-50자)
    - **password**: 비밀번호 (최소 6자)
    """
    logger.info(f"Signup attempt for username: {user_data.username}, email: {user_data.email}")
    user_repo = UserRepository(db)

    # 이메일 중복 체크
    existing_user = user_repo.get_by_email(user_data.email)
    if existing_user:
        logger.warning(f"Email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )

    # 사용자 이름 중복 체크
    existing_username = user_repo.get_by_username(user_data.username)
    if existing_username:
        logger.warning(f"Username already exists: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자 이름입니다."
        )

    # 비밀번호 해싱
    password_hash = get_password_hash(user_data.password)
    logger.info(f"Password hashed for user: {user_data.username}")

    # 사용자 생성
    new_user = user_repo.create_user(
        email=user_data.email,
        username=user_data.username,
        password_hash=password_hash
    )

    logger.info(f"User created successfully: id={new_user.id}, username={new_user.username}")
    return new_user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    로그인 엔드포인트

    - **username**: 사용자 아이디
    - **password**: 비밀번호

    성공 시 JWT 액세스 토큰 반환
    """
    logger.info(f"Login attempt for username: {login_data.username}")
    user_repo = UserRepository(db)

    # 아이디로 사용자 조회
    user = user_repo.get_by_username(login_data.username)
    if not user:
        logger.warning(f"User not found: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    logger.info(f"User found: id={user.id}, username={user.username}")

    # 비밀번호 검증
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Invalid password for user: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # JWT 토큰 생성 (user.id를 subject로 저장)
    logger.info(f"Creating access token for user_id: {user.id} (type: {type(user.id)})")
    access_token = create_access_token(data={"sub": user.id})
    logger.info(f"Access token created successfully for user: {login_data.username}")

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/check-username/{username}")
def check_username_availability(username: str, db: Session = Depends(get_db)):
    """
    아이디 중복 체크 엔드포인트

    - **username**: 확인할 사용자 아이디

    사용 가능한 아이디인지 확인합니다.
    """
    user_repo = UserRepository(db)
    existing_user = user_repo.get_by_username(username)

    if existing_user:
        return {
            "available": False,
            "message": "이미 사용 중인 아이디입니다."
        }
    else:
        return {
            "available": True,
            "message": "사용 가능한 아이디입니다."
        }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    현재 로그인된 사용자 정보 조회

    인증된 사용자의 정보를 반환합니다.
    Authorization 헤더에 Bearer 토큰이 필요합니다.
    """
    logger.info(f"Current user info requested: id={current_user.id}, username={current_user.username}")
    return current_user

@router.get("/me/liked-festivals", response_model=List[FestivalResponse])
def get_user_liked_festivals(
    skip: int = Query(0, ge=0, description="페이징 오프셋"),
    limit: int = Query(100, ge=1, le=500, description="페이징 리밋"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 사용자가 찜한 축제 목록 조회

    - **skip**: 페이징 오프셋
    - **limit**: 페이징 리밋
    - **인증 필요**: Bearer 토큰
    """
    logger.info(f"Fetching liked festivals for user {current_user.id}")
    like_repo = FestivalLikeRepository(db)

    liked_festivals = like_repo.get_user_liked_festivals(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    logger.info(f"Found {len(liked_festivals)} liked festivals for user {current_user.id}")
    return liked_festivals
