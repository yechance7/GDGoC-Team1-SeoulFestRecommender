from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import case
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.llm_client import get_chat_client
from .prompts import (
    INTENT_CLASSIFICATION_PROMPT, 
    SYSTEM_PROMPT, 
    GENERAL_PROMPT, 
    FOLLOWUP_CLASSIFICATION_PROMPT, 
    RECOMMENDATION_SELECTION_PROMPT,
    DATE_EXTRACTION_PROMPT
)
from .types import ChatState, DateRange
from app.entity.seoul_event_entity import SeoulEvent
from app.entity.conversation_entity import Conversation
from app.entity.message_entity import Message
from app.repository.seoul_event_repo import SeoulEventRepository
from datetime import datetime


def _build_context_from_events(events: List[SeoulEvent]) -> str:
    lines: List[str] = []
    for ev in events:
        lines.append(
            f"- id={ev.id}, 제목: {ev.title}, 장소: {ev.place}, 기간: {ev.start_date} ~ {ev.end_date}, 분류: {ev.codename}"
            f", 요금: {ev.use_fee}, 문의: {ev.inquiry}"
            f", 프로그램: {ev.program}, 기타: {ev.etc_desc}"
        )
    if not lines:
        return "현재 추천 가능한 행사가 없습니다."
    return "\n".join(lines)


# ---------- LangGraph Node Functions ----------

def _node_load_conversation(state: ChatState) -> ChatState:
    db = state["db"]
    username = state["username"]
    
    convo: Optional[Conversation] = (
        db.query(Conversation)
        .filter(Conversation.username == username)
        .order_by(Conversation.updated_at.desc())
        .first()
    )
    if not convo:
        convo = Conversation(username=username)
        db.add(convo)
        db.commit()
        db.refresh(convo)

    last_turn: int = db.query(Message.turn).filter(Message.conversation_id == convo.id).order_by(Message.turn.desc()).limit(1).scalar() or 0
    
    last_user_msg: Optional[Message] = (
        db.query(Message).filter(Message.conversation_id == convo.id, Message.role == "user")
        .order_by(Message.turn.desc()).first()
    )
    prev_user_emb: List[float] = last_user_msg.embedding if last_user_msg and last_user_msg.embedding else []

    last_assistant: Optional[Message] = (
        db.query(Message).filter(Message.conversation_id == convo.id, Message.role == "assistant")
        .order_by(Message.turn.desc()).first()
    )
    prev_event_ids: List[int] = (
        [int(x) for x in last_assistant.related_event_ids] 
        if last_assistant and last_assistant.related_event_ids 
        else []
    )
    
    return {
        **state,
        "convo": convo,
        "last_turn": last_turn,
        "prev_user_emb": prev_user_emb,
        "prev_event_ids": prev_event_ids,
    }


async def _node_embed_question(state: ChatState) -> ChatState:
    client = get_chat_client() 
    query_emb = await client.embedding_service.query_embedding(state["message"])
    return {**state, "query_emb": query_emb or []}


async def _node_classify_intent(state: ChatState) -> ChatState:
    client = get_chat_client() 
    prompt = ChatPromptTemplate.from_messages([
        ("system", INTENT_CLASSIFICATION_PROMPT),
        ("user", "질문: {query}")
    ])
    chain = prompt | client.chat_llm
    
    response = await chain.ainvoke({"query": state["message"]})
    
    intent_raw = response.content.strip().lower()
    
    if 'seoul_event' in intent_raw:
        intent = "seoul_event"
    else:
        intent = "general"
        
    print(f"✅ [Log] Intent Classified: {intent}")
    
    return {**state, "intent": intent}


async def _node_decide_followup(state: ChatState) -> ChatState:
    client = get_chat_client()
    prev_ids = state.get("prev_event_ids", [])
    
    if not prev_ids:
        print(f"✅ [Log] Follow-up Check: False (No previous recommended IDs)")
        return {**state, "is_followup": False}

    context = f"이전 추천 이벤트 ID 목록: {prev_ids}"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", FOLLOWUP_CLASSIFICATION_PROMPT),
        ("user", (
            f"[이전 대화 맥락]\n{context}\n\n"
            f"[현재 질문]\n{state['message']}\n\n"
            "이 질문은 꼬리 질문(follow-up)입니까, 새로운 질문(new_query)입니까?"
        ))
    ])
    
    chain = prompt | client.chat_llm
    
    response = await chain.ainvoke({"context": context, "message": state['message']}) 
    
    followup_raw = response.content.strip().lower()
    is_followup = 'follow-up' in followup_raw
        
    print(f"✅ [Log] Follow-up Check (LLM): {is_followup}. LLM Response: {followup_raw}")
    
    return {**state, "is_followup": is_followup}


async def _node_extract_date_filter(state: ChatState) -> ChatState:
    client = get_chat_client()
    current_date = state["current_date"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", DATE_EXTRACTION_PROMPT.format(current_date=current_date)),
        ("user", "질문: {query}")
    ])
    
    chain = prompt | client.chat_llm | JsonOutputParser(pydantic_object=DateRange)
    
    date_range_filter: Optional[DateRange] = None
    try:
        response = await chain.ainvoke({"query": state["message"]})
        
        date_range_filter = DateRange(**response) 
        
        if date_range_filter.start_date is None and date_range_filter.end_date is None:
             date_range_filter = None
             print(f"✅ [Log] Date Extraction: No valid dates found.")
        else:
             print(f"✅ [Log] Date Extraction: {date_range_filter.model_dump_json()}")
        
    except Exception as e:
        print(f"❌ [Log] Date Extraction Failed: {e}. Falling back to no date filter.")
        date_range_filter = None
        
    return {**state, "date_range_filter": date_range_filter}


def _node_fetch_events(state: ChatState) -> ChatState:
    db = state["db"]
    repo = SeoulEventRepository(db) 
    events: List[SeoulEvent] = []
    
    # 1. 꼬리 질문일 경우: 기존 추천 이벤트 재활용 (SQL ID IN 검색)
    if state.get("is_followup") and state.get("prev_event_ids"):
        ids = [int(x) for x in state["prev_event_ids"]]
        ordering = case({id_: idx for idx, id_ in enumerate(ids)}, value=SeoulEvent.id)
        events = (
            db.query(SeoulEvent)
            .filter(SeoulEvent.id.in_(ids))
            .order_by(ordering)
            .all()
        )
        print(f"✅ [Log] Follow-up detected. Reusing {len(events)} previous events.")
    
    # 2. 새로운 질문일 경우: 날짜 필터링을 우선 적용 (SQL 검색)
    elif state.get("date_range_filter"):
        date_filter: DateRange = state["date_range_filter"]
        
        try:
             events = repo.find_events_by_date_range(
                 start_date_str=date_filter.start_date, 
                 end_date_str=date_filter.end_date
             )
             print(f"✅ [Log] Date search executed using SQL filter. Found {len(events)} events.")
        except AttributeError:
             print("❌ [Log] SeoulEventRepository에 find_events_by_date_range 메서드가 필요합니다. (Vector Search로 대체)")
             pass 
             
    # 3. 모든 이전 단계에서 이벤트 검색에 실패했거나, 날짜 정보가 없을 경우: 벡터 검색
    if not events and state.get("query_emb"):
        events = repo.search_similar_events(
            db=db, 
            query_vector=state["query_emb"], 
            top_k=5 
        )
        print(f"✅ [Log] Vector search executed using pgvector. Found {len(events)} events.")
        
    return {**state, "events": events}


async def _node_select_recommendations(state: ChatState) -> ChatState:
    client = get_chat_client() 
    events: List[SeoulEvent] = state.get("events") or []
    current_date = state["current_date"]
    
    if not events:
        print("❌ [Log] No events to select from.")
        return {**state, "selected_event_ids": []}

    context = _build_context_from_events(events)
    
    system_content = RECOMMENDATION_SELECTION_PROMPT.format(current_date=current_date)
    
    prompt = ChatPromptTemplate.from_messages([
        {"role": "system", "content": system_content},
        {"role": "user", "content": (
            f"[사용자 질문]\n{state['message']}\n\n"
            f"[추천 후보 행사 목록]\n{context}"
        )},
    ])
    chain = prompt | client.chat_llm

    resp = await chain.ainvoke({}) 
    
    selected_ids_raw = resp.content.strip()
    selected_event_ids: List[int] = []
    
    try:
        selected_event_ids = [int(id_str.strip()) for id_str in selected_ids_raw.split(',') if id_str.strip().isdigit()]
    except Exception:
        print(f"⚠️ [Log] Selection parsing failed. Falling back to all {len(events)} events.")
        selected_event_ids = [int(ev.id) for ev in events]
        
    valid_ids = [ev.id for ev in events]
    final_ids = [id_ for id_ in selected_event_ids if id_ in valid_ids]
    
    print(f"✅ [Log] Recommendation Selection: {final_ids}")
    
    return {**state, "selected_event_ids": final_ids}


async def _node_handle_general_chat(state: ChatState) -> ChatState:
    client = get_chat_client() 
    prompt = ChatPromptTemplate.from_messages([
        ("system", GENERAL_PROMPT),
        ("user", "{query}")
    ])
    chain = prompt | client.chat_llm
    
    resp = await chain.ainvoke({"query": state["message"]})
    
    print(f"✅ [Log] Handled General Chat.")
    return {**state, "reply": resp.content, "related_event_ids": []}


async def _node_build_reply(state: ChatState) -> ChatState:
    client = get_chat_client() 
    
    selected_event_ids: List[int] = state.get("selected_event_ids") or []
    
    db = state["db"]
    
    if selected_event_ids:
        ordering = case({id_: idx for idx, id_ in enumerate(selected_event_ids)}, value=SeoulEvent.id)
        selected_events = (
            db.query(SeoulEvent)
            .filter(SeoulEvent.id.in_(selected_event_ids))
            .order_by(ordering)
            .all()
        )
    else:
        selected_events = []
    
    if not selected_events:
        return {
            **state,
            "reply": "지금 질문에 딱 맞는 축제를 찾지 못했어요. 날짜나 지역, 축제 종류를 조금 더 구체적으로 알려주실 수 있을까요?",
            "related_event_ids": [],
        }

    context = _build_context_from_events(selected_events)
    current_date = state["current_date"]
    system_content = SYSTEM_PROMPT.format(current_date=current_date)
    
    prompt = ChatPromptTemplate.from_messages([
        {"role": "system", "content": system_content},
        {"role": "user", "content": (
                     "다음은 사용자의 질문과, 답변을 작성할 때 사용할 서울시 축제/행사 목록이다.\n\n"
                     f"[사용자 질문]\n{state['message']}\n\n"
                     f"[최종 추천 행사 목록]\n{context}\n\n"
                     "항상 이 목록에 있는 정보만을 사용하여 답변을 작성해라."
                 ),
        },
    ])
    chain = prompt | client.chat_llm

    resp = await chain.ainvoke({}) 
    
    related_ids = selected_event_ids
    print(f"✅ [Log] Final Reply Built. Related IDs: {related_ids}")
    
    return {**state, "reply": resp.content, "related_event_ids": related_ids}


def _node_save_messages(state: ChatState) -> ChatState:
    db = state["db"]
    convo = state["convo"]
    last_turn = state.get("last_turn", 0)

    user_msg = Message(
        conversation_id=convo.id,
        username=state["username"],
        role="user",
        content=state["message"],
        embedding=state.get("query_emb"),
        turn=last_turn + 1,
    )
    db.add(user_msg)

    assistant_msg = Message(
        conversation_id=convo.id,
        username=state["username"],
        role="assistant",
        content=state.get("reply", ""),
        related_event_ids=state.get("related_event_ids"),
        turn=last_turn + 2,
    )
    db.add(assistant_msg)

    convo.touch()
    db.commit()
    print(f"✅ [Log] Messages Saved (Turn: {last_turn + 2})")
    return state


# ---------- LangGraph Build ----------

_chat_graph = StateGraph(ChatState)
_chat_graph.add_node("load_conversation", _node_load_conversation)
_chat_graph.add_node("embed_question", _node_embed_question)
_chat_graph.add_node("classify_intent", _node_classify_intent) 
_chat_graph.add_node("handle_general_chat", _node_handle_general_chat)
_chat_graph.add_node("decide_followup", _node_decide_followup)
_chat_graph.add_node("extract_date_filter", _node_extract_date_filter)
_chat_graph.add_node("fetch_events", _node_fetch_events)
_chat_graph.add_node("select_recommendations", _node_select_recommendations)
_chat_graph.add_node("build_reply", _node_build_reply)
_chat_graph.add_node("save_messages", _node_save_messages)

_chat_graph.set_entry_point("load_conversation")
_chat_graph.add_edge("load_conversation", "embed_question")
_chat_graph.add_edge("embed_question", "classify_intent") 

def _route_intent(state: ChatState):
    return "handle_general_chat" if state["intent"] == "general" else "decide_followup"

_chat_graph.add_conditional_edges(
    "classify_intent",
    _route_intent,
    {
        "handle_general_chat": "handle_general_chat",
        "decide_followup": "decide_followup"
    }
)

def _route_post_followup(state: ChatState):
    return "fetch_events" if state["is_followup"] else "extract_date_filter"

_chat_graph.add_conditional_edges(
    "decide_followup",
    _route_post_followup,
    {
        "fetch_events": "fetch_events",
        "extract_date_filter": "extract_date_filter"
    }
)

_chat_graph.add_edge("extract_date_filter", "fetch_events")
_chat_graph.add_edge("fetch_events", "select_recommendations")
_chat_graph.add_edge("select_recommendations", "build_reply")
_chat_graph.add_edge("build_reply", "save_messages")

_chat_graph.add_edge("handle_general_chat", "save_messages") 

_chat_graph.add_edge("save_messages", END)

_compiled_chat_graph = _chat_graph.compile()