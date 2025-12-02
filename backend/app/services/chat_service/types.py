from typing import List, TypedDict, Literal, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 날짜 추출 결과 타입 정의 
class DateRange(BaseModel):
    start_date: Optional[str] = None # YYYY-MM-DD 형식
    end_date: Optional[str] = None   # YYYY-MM-DD 형식

class ChatResult(BaseModel):
    reply: str
    related_event_ids: List[int]

class ChatState(TypedDict, total=False):
    username: str
    message: str
    db: Session
    
    convo: any
    last_turn: int
    prev_user_emb: List[float]
    prev_event_ids: List[int]
    query_emb: List[float]
    intent: Literal["general", "seoul_event"]
    is_followup: bool
    
    # 💡 [개선] 날짜/기간 필터링을 위한 필드 추가
    date_range_filter: Optional[DateRange] 
    
    events: any
    reply: str
    related_event_ids: List[int]
    current_date: str
    selected_event_ids: List[int]