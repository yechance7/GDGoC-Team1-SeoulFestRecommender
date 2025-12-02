from __future__ import annotations

from sqlalchemy.orm import Session
from datetime import date
from app.db.database import SessionLocal
from app.core.llm_client import get_chat_client
from .graph import _compiled_chat_graph
from .types import ChatState, ChatResult


async def generate_chat_reply(username: str, message: str) -> ChatResult:
    get_chat_client() 
    
    db: Session = SessionLocal()
    try:
        current_date_str = date.today().isoformat()
        
        initial_state: ChatState = {
            "username": username,
            "message": message,
            "db": db,
            "current_date": current_date_str,
        }
        
        result_state = await _compiled_chat_graph.ainvoke(initial_state)
        return ChatResult(
            reply=result_state.get("reply", ""),
            related_event_ids=result_state.get("related_event_ids", []),
        )
    except RuntimeError as e:
        return ChatResult(reply=f"챗봇 시스템 오류: {e}", related_event_ids=[])
    finally:
        db.close()