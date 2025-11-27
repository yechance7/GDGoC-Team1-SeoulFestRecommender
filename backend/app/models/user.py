# backend/app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """회원가입 요청 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    username: str = Field(..., min_length=3, max_length=50, description="사용자 이름")
    password: str = Field(..., min_length=6, description="비밀번호 (최소 6자)")

class UserLogin(BaseModel):
    """로그인 요청 모델"""
    username: str = Field(..., description="사용자 아이디")
    password: str = Field(..., description="비밀번호")

class UserResponse(BaseModel):
    """사용자 정보 응답 모델 (password_hash 제외)"""
    id: int
    email: str
    username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 모델에서 데이터 읽기 허용

class Token(BaseModel):
    """JWT 토큰 응답 모델"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """JWT 토큰 디코딩 데이터 모델"""
    user_id: Optional[int] = None
