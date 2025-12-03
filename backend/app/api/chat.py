# app/api/chat.py
from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse

from app.services.chat_service import generate_chat_reply, ChatResult

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    result: ChatResult = await generate_chat_reply(
        username=payload.username,
        message=payload.message,
    )
    return ChatResponse(
        reply=result.reply,
        related_event_ids=result.related_event_ids,
    )
