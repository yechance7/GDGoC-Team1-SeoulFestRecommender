# backend/app/repository/festival_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional, Dict
from app.entity.festival_entity import Festival
from app.repository.base_repo import BaseRepository
import logging

logger = logging.getLogger(__name__)

class FestivalRepository(BaseRepository[Festival]):
    def __init__(self, db: Session):
        super().__init__(Festival, db)

    def find_by_name(self, name: str) -> Optional[Festival]:
        """
        이름으로 축제 조회

        Args:
            name: 축제 이름

        Returns:
            Festival: 축제 객체 또는 None
        """
        return self.db.query(self.model).filter(self.model.name == name).first()

    def get_festivals_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Festival]:
        """
        다양한 필터를 적용하여 축제 목록 조회

        Args:
            skip: 페이징 오프셋
            limit: 페이징 리밋
            category: 카테고리 필터 (예: "페스티벌", "콘서트", "전시회")
            search: 검색어 (제목, 설명에서 검색)
            date: 특정 날짜 (YYYY-MM-DD 형식, 해당 날짜에 진행 중인 축제)
            start_date: 시작 날짜 범위 (YYYY-MM-DD)
            end_date: 종료 날짜 범위 (YYYY-MM-DD)

        Returns:
            List[Festival]: 필터링된 축제 목록
        """
        query = self.db.query(Festival)

        # 카테고리 필터
        if category:
            query = query.filter(Festival.category == category)

        # 검색어 필터 (제목 또는 설명에서 검색)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Festival.name.ilike(search_pattern),
                    Festival.description.ilike(search_pattern)
                )
            )

        # 특정 날짜 필터 (해당 날짜에 진행 중인 축제)
        if date:
            query = query.filter(
                and_(
                    Festival.start_date <= date,
                    Festival.end_date >= date
                )
            )

        # 날짜 범위 필터
        if start_date:
            query = query.filter(Festival.end_date >= start_date)
        if end_date:
            query = query.filter(Festival.start_date <= end_date)

        # 정렬: 시작 날짜 오름차순
        query = query.order_by(Festival.start_date.asc(), Festival.created_at.desc())

        # 페이징
        festivals = query.offset(skip).limit(limit).all()

        logger.info(f"Found {len(festivals)} festivals with filters: category={category}, search={search}, date={date}")
        return festivals

    def get_festivals_by_date(self, date: str) -> List[Festival]:
        """
        특정 날짜에 진행 중인 축제 목록 조회

        Args:
            date: 날짜 (YYYY-MM-DD)

        Returns:
            List[Festival]: 해당 날짜에 진행 중인 축제 목록
        """
        festivals = self.db.query(Festival).filter(
            and_(
                Festival.start_date <= date,
                Festival.end_date >= date
            )
        ).order_by(Festival.start_date.asc()).all()

        return festivals

    def get_festivals_by_month(self, year: int, month: int) -> List[Festival]:
        """
        특정 월에 진행되는 축제 목록 조회

        Args:
            year: 연도
            month: 월

        Returns:
            List[Festival]: 해당 월에 진행되는 축제 목록
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

        festivals = self.db.query(Festival).filter(
            or_(
                and_(Festival.start_date >= first_day, Festival.start_date <= last_day),
                and_(Festival.end_date >= first_day, Festival.end_date <= last_day),
                and_(Festival.start_date <= first_day, Festival.end_date >= last_day)
            )
        ).order_by(Festival.start_date.asc()).all()

        return festivals

    def get_calendar_event_counts(self, year: int, month: int) -> Dict[str, int]:
        """
        특정 월의 각 날짜별 이벤트 개수 조회

        Args:
            year: 연도
            month: 월

        Returns:
            Dict[str, int]: 날짜별 이벤트 개수 (예: {"2025-11-28": 3, "2025-11-29": 1})
        """
        festivals = self.get_festivals_by_month(year, month)

        # 날짜별 개수 계산
        event_counts: Dict[str, int] = {}

        for festival in festivals:
            # start_date부터 end_date까지 각 날짜마다 카운트 증가
            from datetime import datetime, timedelta

            start = datetime.strptime(festival.start_date, "%Y-%m-%d")
            end = datetime.strptime(festival.end_date, "%Y-%m-%d")

            current = start
            while current <= end:
                date_str = current.strftime("%Y-%m-%d")
                # 해당 월의 날짜만 카운트
                if current.year == year and current.month == month:
                    event_counts[date_str] = event_counts.get(date_str, 0) + 1
                current += timedelta(days=1)

        logger.info(f"Calendar event counts for {year}-{month:02d}: {len(event_counts)} days with events")
        return event_counts
