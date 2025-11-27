# backend/app/api/festival.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db
from app.repository.festival_repo import FestivalRepository
from app.models.festival import FestivalCreate, FestivalResponse

router = APIRouter(
    tags=["Festivals"],
    prefix="/festivals"
)

# 의존성 주입: DB 세션을 받아 Repository 인스턴스 생성
def get_festival_repo(db: Session = Depends(get_db)) -> FestivalRepository:
    return FestivalRepository(db)

@router.get("/", response_model=List[FestivalResponse])
def read_festivals(
    skip: int = 0, 
    limit: int = 100, 
    repo: FestivalRepository = Depends(get_festival_repo)
):
    """
    모든 축제 목록 조회
    """
    return repo.get_all(skip=skip, limit=limit)

@router.post("/", response_model=FestivalResponse, status_code=status.HTTP_201_CREATED)
def create_festival(
    festival: FestivalCreate,
    repo: FestivalRepository = Depends(get_festival_repo)
):
    """
    새로운 이벤트 정보 등록
    """
    # 중복 검사 (선택 사항)
    existing_festival = repo.find_by_title(festival.title)
    if existing_festival:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event with this title already exists"
        )

    return repo.create(festival.model_dump())