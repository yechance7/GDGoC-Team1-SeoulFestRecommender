# backend/app/api/festival.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import logging

from app.core.dependencies import get_db, get_current_user
from app.repository.festival_repo import FestivalRepository
from app.repository.festival_like_repo import FestivalLikeRepository
from app.models.festival import FestivalCreate, FestivalResponse
from app.entity.user_entity import User

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Festivals"],
    prefix="/festivals"
)

# 의존성 주입: DB 세션을 받아 Repository 인스턴스 생성
def get_festival_repo(db: Session = Depends(get_db)) -> FestivalRepository:
    return FestivalRepository(db)

def get_festival_like_repo(db: Session = Depends(get_db)) -> FestivalLikeRepository:
    return FestivalLikeRepository(db)

@router.get("/", response_model=List[FestivalResponse])
def read_festivals(
    skip: int = Query(0, ge=0, description="페이징 오프셋"),
    limit: int = Query(100, ge=1, le=500, description="페이징 리밋"),
    category: Optional[str] = Query(None, description="카테고리 필터 (예: 페스티벌, 콘서트, 전시회)"),
    search: Optional[str] = Query(None, description="검색어 (제목 또는 설명에서 검색)"),
    date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="특정 날짜 (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="시작 날짜 범위"),
    end_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="종료 날짜 범위"),
    repo: FestivalRepository = Depends(get_festival_repo)
):
    """
    축제 목록 조회 (필터링 지원)

    - **skip**: 페이징 오프셋
    - **limit**: 페이징 리밋
    - **category**: 카테고리 필터
    - **search**: 검색어 (제목/설명)
    - **date**: 특정 날짜에 진행 중인 축제
    - **start_date**: 시작 날짜 범위
    - **end_date**: 종료 날짜 범위
    """
    logger.info(f"Fetching festivals with filters: category={category}, search={search}, date={date}")

    festivals = repo.get_festivals_with_filters(
        skip=skip,
        limit=limit,
        category=category,
        search=search,
        date=date,
        start_date=start_date,
        end_date=end_date
    )

    return festivals

@router.get("/calendar", response_model=Dict[str, int])
def get_calendar_event_counts(
    year: int = Query(..., ge=2000, le=2100, description="연도"),
    month: int = Query(..., ge=1, le=12, description="월"),
    repo: FestivalRepository = Depends(get_festival_repo)
):
    """
    캘린더용 날짜별 이벤트 개수 조회

    - **year**: 연도
    - **month**: 월

    Returns: {"2025-11-28": 3, "2025-11-29": 1, ...}
    """
    logger.info(f"Fetching calendar event counts for {year}-{month:02d}")
    event_counts = repo.get_calendar_event_counts(year, month)
    return event_counts

@router.get("/{festival_id}", response_model=FestivalResponse)
def read_festival(
    festival_id: int,
    repo: FestivalRepository = Depends(get_festival_repo)
):
    """
    특정 축제 상세 조회
    """
    festival = repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Festival not found"
        )
    return festival

@router.post("/", response_model=FestivalResponse, status_code=status.HTTP_201_CREATED)
def create_festival(
    festival: FestivalCreate,
    repo: FestivalRepository = Depends(get_festival_repo)
):
    """
    새로운 축제 정보 등록
    """
    logger.info(f"Creating festival: {festival.name}")

    # 중복 검사 (선택 사항)
    existing_festival = repo.find_by_name(festival.name)
    if existing_festival:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Festival with this name already exists"
        )

    return repo.create(festival.model_dump())

@router.post("/{festival_id}/like", status_code=status.HTTP_201_CREATED)
def like_festival(
    festival_id: int,
    current_user: User = Depends(get_current_user),
    festival_repo: FestivalRepository = Depends(get_festival_repo),
    like_repo: FestivalLikeRepository = Depends(get_festival_like_repo)
):
    """
    축제 찜하기 추가

    - **festival_id**: 찜할 축제 ID
    - **인증 필요**: Bearer 토큰
    """
    logger.info(f"User {current_user.id} attempting to like festival {festival_id}")

    # 축제 존재 여부 확인
    festival = festival_repo.get_by_id(festival_id)
    if not festival:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Festival not found"
        )

    # 찜하기 추가
    like = like_repo.add_like(current_user.id, festival_id)
    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked this festival"
        )

    return {"message": "Festival liked successfully", "festival_id": festival_id}

@router.delete("/{festival_id}/like", status_code=status.HTTP_200_OK)
def unlike_festival(
    festival_id: int,
    current_user: User = Depends(get_current_user),
    like_repo: FestivalLikeRepository = Depends(get_festival_like_repo)
):
    """
    축제 찜하기 취소

    - **festival_id**: 찜 취소할 축제 ID
    - **인증 필요**: Bearer 토큰
    """
    logger.info(f"User {current_user.id} attempting to unlike festival {festival_id}")

    # 찜하기 취소
    success = like_repo.remove_like(current_user.id, festival_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )

    return {"message": "Festival unliked successfully", "festival_id": festival_id}

@router.get("/{festival_id}/is-liked")
def check_festival_liked(
    festival_id: int,
    current_user: User = Depends(get_current_user),
    like_repo: FestivalLikeRepository = Depends(get_festival_like_repo)
):
    """
    축제 찜 여부 확인

    - **festival_id**: 확인할 축제 ID
    - **인증 필요**: Bearer 토큰
    """
    is_liked = like_repo.is_liked(current_user.id, festival_id)
    return {"festival_id": festival_id, "is_liked": is_liked}