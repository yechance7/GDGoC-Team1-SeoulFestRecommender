# app/services/llm_service.py

from __future__ import annotations

import math
from typing import List, Dict, Optional, TypedDict

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import case
from langgraph.graph import StateGraph, END
from openai import OpenAI

from app.core.config import settings
from app.db.database import SessionLocal

from app.entity.seoul_event_entity import SeoulEvent
from app.entity.conversation_entity import Conversation
from app.entity.message_entity import Message


# ---------- 외부 API 클라이언트 설정 ----------

# Upstage는 OpenAI 호환 클라이언트로 호출
client = OpenAI(
    api_key=settings.UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1",
)


# ---------- 응답 모델 ----------

class ChatResult(BaseModel):
    reply: str
    related_event_ids: List[int]

# 꼬리질문 판단 임계값 (질문 임베딩 유사도)
# 후속 질문을 넉넉히 잡기 위해 0.5로 설정
FOLLOWUP_SIM_THRESHOLD = 0.5

# ---------- 유틸 함수들 ----------

def _cosine_sim(a: List[float], b: List[float]) -> float:
    """코사인 유사도 계산."""
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def _get_query_embedding(text: str) -> List[float]:
    """유저 질문을 solar-embedding-1-large-query 로 임베딩."""
    resp = client.embeddings.create(
        model="solar-embedding-1-large-query",
        input=text,
    )
    return resp.data[0].embedding


def _search_similar_events(
    db: Session, query_embedding: List[float], top_k: int = 3
) -> List[SeoulEvent]:
    """
    SeoulEvent 테이블 전체에서 embedding 이 있는 행만 가져와
    파이썬에서 코사인 유사도 계산 후 상위 top_k 리턴.
    """
    query = db.query(SeoulEvent)
    if hasattr(SeoulEvent, "embedding"):
        query = query.filter(SeoulEvent.embedding.isnot(None))

    events: List[SeoulEvent] = query.all()

    scored: List[tuple[float, SeoulEvent]] = []
    for ev in events:
        emb = getattr(ev, "embedding", None)
        if emb is None:
            continue
        # pgvector가 numpy array나 다른 시퀀스로 올 수 있어 리스트로 강제 변환
        emb_list = list(emb)
        sim = _cosine_sim(query_embedding, emb_list)
        scored.append((sim, ev))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [ev for _, ev in scored[:top_k]]


SYSTEM_PROMPT = """
당신은 서울시 축제·문화행사를 추천해주는 챗봇이다.
사용자의 질문과 주어진 행사 정보만을 근거로,
사용자에게 어울릴 만한 행사 1~3개를 한국어로 추천한다.

항상 다음을 지켜라.
- 행사 이름, 장소, 기간(또는 날짜)을 구체적으로 말한다.
- 왜 이 사용자의 질문과 잘 맞는지 한두 문장으로 이유를 설명한다.
- 제공되지 않은 정보는 지어내지 않는다.
- 서울시 축제/행사와 관련 없는 내용은 답변하지 않는다.
"""


def _build_context_from_events(events: List[SeoulEvent]) -> str:
    """LLM에 넘길 '행사 목록 컨텍스트' 문자열 생성."""
    lines: List[str] = []
    for ev in events:
        title = getattr(ev, "title", "") or getattr(ev, "event_title", "")
        place = getattr(ev, "place", "") or getattr(ev, "place_name", "")
        start = getattr(ev, "start_date", "") or getattr(ev, "event_start", "") or getattr(ev, "pro_start", "")
        end = getattr(ev, "end_date", "") or getattr(ev, "event_end", "") or getattr(ev, "pro_end", "")
        codename = getattr(ev, "codename", "") or getattr(ev, "category", "")

        lines.append(
            f"- id={ev.id}, 제목: {title}, 장소: {place}, 기간: {start} ~ {end}, 분류: {codename}"
        )

    if not lines:
        return "현재 추천 가능한 행사가 없습니다."

    return "\n".join(lines)


def _call_solar_chat(user_message: str, context: str, history: str = "") -> str:
    """Solar-Pro로 실제 답변 생성."""
    history_block = f"[이전 대화]\n{history}\n\n" if history else ""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "다음은 사용자의 질문과, 추천 후보로 사용할 서울시 축제/행사 목록이다.\n\n"
                f"{history_block}"
                f"[사용자 질문]\n{user_message}\n\n"
                f"[행사 목록]\n{context}\n\n"
                "항상 행사 목록에 있는 정보만 사용하고, 목록에 없는 새로운 행사는 절대 추가하지 마라.\n"
                "사용자가 '첫번째/두번째/세번째'처럼 지목하면 목록의 순서를 그대로 따르라."
            ),
        },
    ]

    resp = client.chat.completions.create(
        model="solar-pro",
        messages=messages,
        temperature=0.3,
    )
    return resp.choices[0].message.content


# ---------- LangGraph 기반 상태 정의 ----------


class ChatState(TypedDict, total=False):
    user_id: str
    message: str
    db: Session
    convo: Conversation
    last_turn: int
    last_user_text: str
    last_assistant_text: str
    prev_user_emb: List[float]
    prev_event_ids: List[int]
    query_emb: List[float]
    is_followup: bool
    events: List[SeoulEvent]
    reply: str
    related_event_ids: List[int]


def _node_load_conversation(state: ChatState) -> ChatState:
    db = state["db"]
    user_id = state["user_id"]

    convo: Optional[Conversation] = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .first()
    )
    if not convo:
        convo = Conversation(user_id=user_id)
        db.add(convo)
        db.commit()
        db.refresh(convo)

    last_turn: int = (
        db.query(Message.turn)
        .filter(Message.conversation_id == convo.id)
        .order_by(Message.turn.desc())
        .limit(1)
        .scalar()
        or 0
    )

    last_user_msg: Optional[Message] = (
        db.query(Message)
        .filter(Message.conversation_id == convo.id, Message.role == "user")
        .order_by(Message.turn.desc())
        .first()
    )
    prev_user_emb: List[float] = last_user_msg.embedding if last_user_msg and last_user_msg.embedding else []
    last_user_text = last_user_msg.content if last_user_msg else ""

    last_assistant: Optional[Message] = (
        db.query(Message)
        .filter(
            Message.conversation_id == convo.id,
            Message.role == "assistant",
        )
        .order_by(Message.turn.desc())
        .first()
    )
    prev_event_ids: List[int] = (
        [int(x) for x in last_assistant.related_event_ids] if last_assistant and last_assistant.related_event_ids else []
    )
    last_assistant_text = last_assistant.content if last_assistant else ""

    return {
        **state,
        "convo": convo,
        "last_turn": last_turn,
        "prev_user_emb": prev_user_emb,
        "prev_event_ids": prev_event_ids,
        "last_user_text": last_user_text,
        "last_assistant_text": last_assistant_text,
    }


def _node_embed_question(state: ChatState) -> ChatState:
    query_emb = _get_query_embedding(state["message"])
    return {**state, "query_emb": query_emb}


def _node_decide_followup(state: ChatState) -> ChatState:
    prev_emb = state.get("prev_user_emb") or []
    is_followup = False
    # 이전 추천이 있으면 기본적으로 이어서 답한다.
    if state.get("prev_event_ids"):
        is_followup = True
    # 그 외에는 임베딩 유사도로 판정
    elif prev_emb:
        is_followup = _cosine_sim(state["query_emb"], prev_emb) >= FOLLOWUP_SIM_THRESHOLD  # type: ignore[arg-type]
    return {**state, "is_followup": is_followup}


def _node_fetch_events(state: ChatState) -> ChatState:
    db = state["db"]
    events: List[SeoulEvent] = []
    if state.get("is_followup") and state.get("prev_event_ids"):
        ids = [int(x) for x in state["prev_event_ids"]]
        # 저장된 순서를 유지하도록 CASE 정렬
        ordering = case({id_: idx for idx, id_ in enumerate(ids)}, value=SeoulEvent.id)
        events = (
            db.query(SeoulEvent)
            .filter(SeoulEvent.id.in_(ids))
            .order_by(ordering)
            .all()
        )
    if not events:
        events = _search_similar_events(db, state["query_emb"], top_k=3)
    return {**state, "events": events}


def _node_build_reply(state: ChatState) -> ChatState:
    events: List[SeoulEvent] = state.get("events") or []
    if not events:
        return {
            **state,
            "reply": "지금 질문에 딱 맞는 축제를 찾지 못했어요. 날짜나 지역, 축제 종류를 조금 더 구체적으로 알려주실 수 있을까요?",
            "related_event_ids": [],
        }

    # 사용자가 "첫번째/두번째/세번째"처럼 특정 순서를 묻는 경우 해당 이벤트만 선택
    msg = state["message"]
    lowered = msg.lower()
    ordinal = None
    if any(k in lowered for k in ("첫번째", "첫 번째", "첫번", "첫 번", "first")):
        ordinal = 0
    elif any(k in lowered for k in ("두번째", "두 번째", "second")):
        ordinal = 1
    elif any(k in lowered for k in ("세번째", "세 번째", "third")):
        ordinal = 2

    if ordinal is not None and ordinal < len(events):
        events = [events[ordinal]]

    context = _build_context_from_events(events)
    # 직전 대화 텍스트를 짧게 포함해 후속 질문에 대응
    history_lines = []
    if state.get("last_user_text"):
        history_lines.append(f"이전 질문: {state['last_user_text']}")
    if state.get("last_assistant_text"):
        history_lines.append(f"이전 답변: {state['last_assistant_text']}")
    history_text = "\n".join(history_lines)

    try:
        reply_text = _call_solar_chat(state["message"], context, history=history_text)
    except Exception:
        fallback_lines = []
        for ev in events:
            title = getattr(ev, "title", "") or getattr(ev, "event_title", "")
            place = getattr(ev, "place", "") or getattr(ev, "place_name", "")
            start = getattr(ev, "start_date", "") or getattr(ev, "event_start", "") or getattr(ev, "pro_start", "")
            end = getattr(ev, "end_date", "") or getattr(ev, "event_end", "") or getattr(ev, "pro_end", "")
            fallback_lines.append(f"- {title} ({start} ~ {end}, 장소: {place})")

        reply_text = (
            "추천 엔진에서 약간의 오류가 있어 LLM 생성 대신 기본 추천만 안내드려요.\n"
            "지금 질문과 가장 비슷한 축제들은 다음과 같습니다:\n" +
            "\n".join(fallback_lines)
        )

    related_ids = [int(ev.id) for ev in events]
    return {**state, "reply": reply_text, "related_event_ids": related_ids}


def _node_save_messages(state: ChatState) -> ChatState:
    db = state["db"]
    convo = state["convo"]
    last_turn = state.get("last_turn", 0)

    user_msg = Message(
        conversation_id=convo.id,
        user_id=state["user_id"],
        role="user",
        content=state["message"],
        embedding=state.get("query_emb"),
        turn=last_turn + 1,
    )
    db.add(user_msg)

    assistant_msg = Message(
        conversation_id=convo.id,
        user_id=state["user_id"],
        role="assistant",
        content=state.get("reply", ""),
        related_event_ids=state.get("related_event_ids"),
        turn=last_turn + 2,
    )
    db.add(assistant_msg)

    convo.touch()
    db.commit()
    return state


_chat_graph = StateGraph(ChatState)
_chat_graph.add_node("load_conversation", _node_load_conversation)
_chat_graph.add_node("embed_question", _node_embed_question)
_chat_graph.add_node("decide_followup", _node_decide_followup)
_chat_graph.add_node("fetch_events", _node_fetch_events)
_chat_graph.add_node("build_reply", _node_build_reply)
_chat_graph.add_node("save_messages", _node_save_messages)

_chat_graph.set_entry_point("load_conversation")
_chat_graph.add_edge("load_conversation", "embed_question")
_chat_graph.add_edge("embed_question", "decide_followup")
_chat_graph.add_edge("decide_followup", "fetch_events")
_chat_graph.add_edge("fetch_events", "build_reply")
_chat_graph.add_edge("build_reply", "save_messages")
_chat_graph.add_edge("save_messages", END)

_compiled_chat_graph = _chat_graph.compile()


# ---------- 메인 진입 함수 ----------

async def generate_chat_reply(user_id: str, message: str) -> ChatResult:
    """
    LangGraph를 사용해 대화 상태를 불러오고, 꼬리질문 여부에 따라 답변 생성 후 영속화.
    """
    db: Session = SessionLocal()
    try:
        initial_state: ChatState = {
            "user_id": user_id,
            "message": message,
            "db": db,
        }
        result_state = _compiled_chat_graph.invoke(initial_state)
        return ChatResult(
            reply=result_state.get("reply", ""),
            related_event_ids=result_state.get("related_event_ids", []),
        )
    finally:
        db.close()
