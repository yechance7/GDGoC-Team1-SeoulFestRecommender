# backend/app/api/seoul_event.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import logging

from app.core.dependencies import get_db, get_current_user
from app.repository.seoul_event_repo import SeoulEventRepository
from app.repository.seoul_event_like_repo import SeoulEventLikeRepository
from app.models.seoul_event import SeoulEventCreate, SeoulEventResponse
from app.entity.user_entity import User

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Seoul Events"],
    prefix="/seoul-events"
)

# 의존성 주입: DB 세션을 받아 Repository 인스턴스 생성
def get_seoul_event_repo(db: Session = Depends(get_db)) -> SeoulEventRepository:
    return SeoulEventRepository(db)

def get_seoul_event_like_repo(db: Session = Depends(get_db)) -> SeoulEventLikeRepository:
    return SeoulEventLikeRepository(db)

@router.get("/", response_model=List[SeoulEventResponse])
def read_seoul_events(
    skip: int = Query(0, ge=0, description="페이징 오프셋"),
    limit: int = Query(100, ge=1, le=500, description="페이징 리밋"),
    codename: Optional[str] = Query(None, description="분류 필터 (예: 뮤지컬/오페라, 콘서트)"),
    gu_name: Optional[str] = Query(None, description="자치구 필터 (예: 송파구, 강남구)"),
    search: Optional[str] = Query(None, description="검색어 (제목, 장소, 기관명에서 검색)"),
    date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="특정 날짜 (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="시작 날짜 범위"),
    end_date: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="종료 날짜 범위"),
    is_free: Optional[str] = Query(None, description="유무료 필터 (예: 무료, 유료)"),
    repo: SeoulEventRepository = Depends(get_seoul_event_repo)
):
    """
    서울 이벤트 목록 조회 (필터링 지원)

    - **skip**: 페이징 오프셋
    - **limit**: 페이징 리밋
    - **codename**: 분류 필터
    - **gu_name**: 자치구 필터
    - **search**: 검색어 (제목/장소/기관명)
    - **date**: 특정 날짜에 진행 중인 이벤트
    - **start_date**: 시작 날짜 범위
    - **end_date**: 종료 날짜 범위
    - **is_free**: 유무료 필터
    """
    logger.info(f"Fetching seoul events with filters: codename={codename}, gu_name={gu_name}, search={search}, date={date}")

    events = repo.get_events_with_filters(
        skip=skip,
        limit=limit,
        codename=codename,
        gu_name=gu_name,
        search=search,
        date=date,
        start_date=start_date,
        end_date=end_date,
        is_free=is_free
    )

    return events

@router.get("/calendar", response_model=Dict[str, int])
def get_calendar_event_counts(
    year: int = Query(..., ge=2000, le=2100, description="연도"),
    month: int = Query(..., ge=1, le=12, description="월"),
    repo: SeoulEventRepository = Depends(get_seoul_event_repo)
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

@router.get("/{event_id}", response_model=SeoulEventResponse)
def read_seoul_event(
    event_id: int,
    repo: SeoulEventRepository = Depends(get_seoul_event_repo)
):
    """
    특정 이벤트 상세 조회
    """
    event = repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seoul event not found"
        )
    return event

@router.post("/", response_model=SeoulEventResponse, status_code=status.HTTP_201_CREATED)
def create_seoul_event(
    event: SeoulEventCreate,
    repo: SeoulEventRepository = Depends(get_seoul_event_repo)
):
    """
    새로운 서울 이벤트 정보 등록
    """
    logger.info(f"Creating seoul event: {event.title}")

    # 중복 검사 (선택 사항)
    existing_event = repo.find_by_title(event.title)
    if existing_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seoul event with this title already exists"
        )

    return repo.create(event.model_dump())

@router.post("/{event_id}/like", status_code=status.HTTP_201_CREATED)
def like_seoul_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    event_repo: SeoulEventRepository = Depends(get_seoul_event_repo),
    like_repo: SeoulEventLikeRepository = Depends(get_seoul_event_like_repo)
):
    """
    이벤트 찜하기 추가

    - **event_id**: 찜할 이벤트 ID
    - **인증 필요**: Bearer 토큰
    """
    logger.info(f"User {current_user.id} attempting to like seoul event {event_id}")

    # 이벤트 존재 여부 확인
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seoul event not found"
        )

    # 찜하기 추가
    like = like_repo.add_like(current_user.id, event_id)
    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked this event"
        )

    return {"message": "Seoul event liked successfully", "event_id": event_id}

@router.delete("/{event_id}/like", status_code=status.HTTP_200_OK)
def unlike_seoul_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    like_repo: SeoulEventLikeRepository = Depends(get_seoul_event_like_repo)
):
    """
    이벤트 찜하기 취소

    - **event_id**: 찜 취소할 이벤트 ID
    - **인증 필요**: Bearer 토큰
    """
    logger.info(f"User {current_user.id} attempting to unlike seoul event {event_id}")

    # 찜하기 취소
    success = like_repo.remove_like(current_user.id, event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )

    return {"message": "Seoul event unliked successfully", "event_id": event_id}

@router.get("/{event_id}/is-liked")
def check_seoul_event_liked(
    event_id: int,
    current_user: User = Depends(get_current_user),
    like_repo: SeoulEventLikeRepository = Depends(get_seoul_event_like_repo)
):
    """
    이벤트 찜 여부 확인

    - **event_id**: 확인할 이벤트 ID
    - **인증 필요**: Bearer 토큰
    """
    is_liked = like_repo.is_liked(current_user.id, event_id)
    return {"event_id": event_id, "is_liked": is_liked}
