# backend/app/repository/seoul_event_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional, Dict
from app.entity.seoul_event_entity import SeoulEvent
from app.repository.base_repo import BaseRepository
import logging

logger = logging.getLogger(__name__)

class SeoulEventRepository(BaseRepository[SeoulEvent]):
    def __init__(self, db: Session):
        super().__init__(SeoulEvent, db)

    def find_by_title(self, title: str) -> Optional[SeoulEvent]:
        """
        제목으로 이벤트 조회

        Args:
            title: 이벤트 제목

        Returns:
            SeoulEvent: 이벤트 객체 또는 None
        """
        return self.db.query(self.model).filter(self.model.title == title).first()

    def get_events_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        codename: Optional[str] = None,
        gu_name: Optional[str] = None,
        search: Optional[str] = None,
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        is_free: Optional[str] = None
    ) -> List[SeoulEvent]:
        """
        다양한 필터를 적용하여 이벤트 목록 조회

        Args:
            skip: 페이징 오프셋
            limit: 페이징 리밋
            codename: 분류 필터 (예: "뮤지컬/오페라", "콘서트")
            gu_name: 자치구 필터 (예: "송파구", "강남구")
            search: 검색어 (제목, 장소, 기관명에서 검색)
            date: 특정 날짜 (YYYY-MM-DD 형식, 해당 날짜에 진행 중인 이벤트)
            start_date: 시작 날짜 범위 (YYYY-MM-DD)
            end_date: 종료 날짜 범위 (YYYY-MM-DD)
            is_free: 유무료 필터 (예: "무료", "유료")

        Returns:
            List[SeoulEvent]: 필터링된 이벤트 목록
        """
        query = self.db.query(SeoulEvent)

        # 분류 필터
        if codename:
            query = query.filter(SeoulEvent.codename == codename)

        # 자치구 필터
        if gu_name:
            query = query.filter(SeoulEvent.gu_name == gu_name)

        # 유무료 필터
        if is_free:
            query = query.filter(SeoulEvent.is_free == is_free)

        # 검색어 필터 (제목, 장소, 기관명에서 검색)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    SeoulEvent.title.ilike(search_pattern),
                    SeoulEvent.place.ilike(search_pattern),
                    SeoulEvent.org_name.ilike(search_pattern)
                )
            )

        # 특정 날짜 필터 (해당 날짜에 진행 중인 이벤트)
        if date:
            query = query.filter(
                and_(
                    SeoulEvent.start_date <= date,
                    SeoulEvent.end_date >= date
                )
            )

        # 날짜 범위 필터
        if start_date:
            query = query.filter(SeoulEvent.end_date >= start_date)
        if end_date:
            query = query.filter(SeoulEvent.start_date <= end_date)

        # 정렬: 시작 날짜 오름차순
        query = query.order_by(SeoulEvent.start_date.asc())

        # 페이징
        events = query.offset(skip).limit(limit).all()

        logger.info(f"Found {len(events)} events with filters: codename={codename}, gu_name={gu_name}, search={search}, date={date}")
        return events

    def get_events_by_date(self, date: str) -> List[SeoulEvent]:
        """
        특정 날짜에 진행 중인 이벤트 목록 조회

        Args:
            date: 날짜 (YYYY-MM-DD)

        Returns:
            List[SeoulEvent]: 해당 날짜에 진행 중인 이벤트 목록
        """
        events = self.db.query(SeoulEvent).filter(
            and_(
                SeoulEvent.start_date <= date,
                SeoulEvent.end_date >= date
            )
        ).order_by(SeoulEvent.start_date.asc()).all()

        return events

    def get_events_by_month(self, year: int, month: int) -> List[SeoulEvent]:
        """
        특정 월에 진행되는 이벤트 목록 조회

        Args:
            year: 연도
            month: 월

        Returns:
            List[SeoulEvent]: 해당 월에 진행되는 이벤트 목록
        """
        # 해당 월의 첫날과 마지막 날 계산
        first_day = f"{year:04d}-{month:02d}-01"
        if month == 12:
            last_day = f"{year:04d}-12-31"
        else:
            from datetime import date
            next_month = date(year, month + 1, 1)
            last_day_obj = next_month.replace(day=1) - next_month.resolution
            last_day = last_day_obj.strftime("%Y-%m-%d")

        events = self.db.query(SeoulEvent).filter(
            or_(
                and_(SeoulEvent.start_date >= first_day, SeoulEvent.start_date <= last_day),
                and_(SeoulEvent.end_date >= first_day, SeoulEvent.end_date <= last_day),
                and_(SeoulEvent.start_date <= first_day, SeoulEvent.end_date >= last_day)
            )
        ).order_by(SeoulEvent.start_date.asc()).all()

        return events

    def get_calendar_event_counts(self, year: int, month: int) -> Dict[str, int]:
        """
        특정 월의 각 날짜별 이벤트 개수 조회

        Args:
            year: 연도
            month: 월

        Returns:
            Dict[str, int]: 날짜별 이벤트 개수 (예: {"2025-11-28": 3, "2025-11-29": 1})
        """
        events = self.get_events_by_month(year, month)

        # 날짜별 개수 계산
        event_counts: Dict[str, int] = {}

        for event in events:
            # start_date부터 end_date까지 각 날짜마다 카운트 증가
            from datetime import datetime, timedelta

            start = datetime.strptime(str(event.start_date), "%Y-%m-%d")
            end = datetime.strptime(str(event.end_date), "%Y-%m-%d")

            current = start
            while current <= end:
                date_str = current.strftime("%Y-%m-%d")
                # 해당 월의 날짜만 카운트
                if current.year == year and current.month == month:
                    event_counts[date_str] = event_counts.get(date_str, 0) + 1
                current += timedelta(days=1)

        logger.info(f"Calendar event counts for {year}-{month:02d}: {len(event_counts)} days with events")
        return event_counts

    def get_events_by_gu(self, gu_name: str, skip: int = 0, limit: int = 100) -> List[SeoulEvent]:
        """
        특정 자치구의 이벤트 목록 조회

        Args:
            gu_name: 자치구 이름 (예: "송파구")
            skip: 페이징 오프셋
            limit: 페이징 리밋

        Returns:
            List[SeoulEvent]: 해당 자치구의 이벤트 목록
        """
        events = self.db.query(SeoulEvent).filter(
            SeoulEvent.gu_name == gu_name
        ).order_by(SeoulEvent.start_date.asc()).offset(skip).limit(limit).all()

        return events
