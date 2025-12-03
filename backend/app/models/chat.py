# backend/app/models/chat.py
from pydantic import BaseModel, Field
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    username: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    related_event_ids: list[int]

