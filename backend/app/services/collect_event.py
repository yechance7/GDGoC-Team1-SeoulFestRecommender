# app/services/collect_event.py

from __future__ import annotations

from typing import Dict, List, Tuple, Any
from datetime import datetime
import logging
import re

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import SessionLocal
from app.entity.seoul_event_entity import SeoulEvent

logger = logging.getLogger(__name__)

def fetch_page(start: int, end: int) -> Tuple[List[Dict[str, Any]], int]:
    url = (
        f"{settings.SEOUL_EVENT_BASE_URL}/"
        f"{settings.SEOUL_EVENT_API_KEY}/json/"
        f"{settings.SEOUL_EVENT_SERVICE}/{start}/{end}"
    )

    logger.info("Fetching Seoul events: %s", url)

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    root = data.get(settings.SEOUL_EVENT_SERVICE) or data.get("culturalEventInfo") or {}

    rows = root.get("row") or []
    total_raw = root.get("list_total_count", len(rows))

    try:
        total = int(total_raw)
    except (TypeError, ValueError):
        logger.warning(
            "Unexpected list_total_count=%r, fallback to len(rows)=%d",
            total_raw,
            len(rows),
        )
        total = len(rows)

    logger.info("Fetched %d rows (total=%d)", len(rows), total)
    return rows, total


def parse_date_or_none(raw: Any):
    if not raw:
        return None

    raw_str = str(raw).strip()
    if not raw_str:
        return None

    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y%m%d"):
        try:
            return datetime.strptime(raw_str, fmt).date()
        except ValueError:
            continue

    logger.debug("Failed to parse date: %r", raw)
    return None


# 3) float 파싱 유틸 (좌표용)
def parse_float_or_none(val: Any):
    """
    서울시 API에서 오는 이상한 좌표 값들까지 웬만하면 처리해 주는 float 파서.
    """
    if val is None:
        return None

    s = str(val).strip()
    if not s:
        return None

    for sep in ("~", "/", ","):
        if sep in s:
            s = s.split(sep, 1)[0].strip()

    m = re.search(r"[-+]?\d+(\.\d+)?", s)
    if not m:
        logger.warning("Cannot parse float from value=%r", val)
        return None

    num_str = m.group(0)
    try:
        return float(num_str)
    except ValueError:
        logger.warning(
            "Float conversion failed for extracted=%r (raw=%r)", num_str, val
        )
        return None


def row_to_entity(row: Dict[str, Any]) -> SeoulEvent:
    return SeoulEvent(
        codename=row.get("CODENAME"),
        gu_name=row.get("GUNAME"),
        title=row.get("TITLE"),

        date_text=row.get("DATE"),
        place=row.get("PLACE"),
        org_name=row.get("ORG_NAME"),
        use_target=row.get("USE_TRGT"),
        use_fee=row.get("USE_FEE"),
        inquiry=row.get("INQUIRY"),
        player=row.get("PLAYER"),
        program=row.get("PROGRAM"),
        etc_desc=row.get("ETC_DESC"),

        org_link=row.get("ORG_LINK"),
        main_img=row.get("MAIN_IMG"),

        rgst_date=parse_date_or_none(row.get("RGSTDATE")),
        ticket_type=row.get("TICKET"),
        start_date=parse_date_or_none(row.get("STRTDATE")),
        end_date=parse_date_or_none(row.get("END_DATE")),
        theme_code=row.get("THEMECODE"),

        lot=parse_float_or_none(row.get("LOT")),
        lat=parse_float_or_none(row.get("LAT")),

        is_free=row.get("IS_FREE"),
        hmpg_addr=row.get("HMPG_ADDR"),
        pro_time=row.get("PRO_TIME"),
    )

def save_rows(rows: List[Dict[str, Any]], db: Session) -> int:
    saved = 0

    for row in rows:
        try:
            event = row_to_entity(row)
        except Exception as e:
            logger.exception("Failed to convert row to entity: %s (row=%r)", e, row)
            continue

        # 유니크 키 구성 요소가 없으면 패스
        if not event.title or not event.start_date or not event.place:
            continue

        exists = (
            db.query(SeoulEvent)
            .filter(
                SeoulEvent.title == event.title,
                SeoulEvent.start_date == event.start_date,
                SeoulEvent.place == event.place,
            )
            .first()
        )
        if exists:
            continue

        db.add(event)
        saved += 1

    db.commit()
    logger.info("Saved %d new events", saved)
    return saved


# 전체 페이지 돌며 동기화
def sync_seoul_events() -> int:
    """
    서울시 문화행사 전체를 API에서 가져와 DB에 적재.
    """
    db = SessionLocal()
    try:
        page_size = settings.SEOUL_EVENT_PAGE_SIZE
        start = 1
        total_saved = 0

        while True:
            end = start + page_size - 1
            rows, total = fetch_page(start, end)

            if not rows:
                break

            total_saved += save_rows(rows, db)

            if end >= total:
                break

            start = end + 1

        logger.info("Sync completed. Total newly saved=%d", total_saved)
        return total_saved

    finally:
        db.close()
