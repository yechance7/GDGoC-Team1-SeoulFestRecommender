import os
from langchain_upstage import ChatUpstage
from app.services.embedding_service import EmbeddingService 

class ChatbotClient:
    def __init__(self, model: str):
        api_key = os.getenv("SOLAR_API_KEY")
        if not api_key:
            raise ValueError("SOLAR_API_KEY 환경 변수가 설정되지 않았습니다.")
            
        self.chat_llm = ChatUpstage(api_key=api_key, model=model) 
        
        # EmbeddingService 초기화 시 에러가 발생하면 여기서 처리
        try:
            self.embedding_service = EmbeddingService()
        except ValueError as e:
            # EmbeddingService 초기화 실패는 치명적이므로 다시 발생
            raise RuntimeError(f"EmbeddingService 초기화 실패: {e}") from e

LLM_MODEL = os.getenv("SOLAR_LLM_MODEL", "solar-1-mini-chat")
_CHATBOT_CLIENT_INSTANCE = None

def get_chat_client() -> ChatbotClient:
    global _CHATBOT_CLIENT_INSTANCE
    if _CHATBOT_CLIENT_INSTANCE is None:
        try:
            # ChatbotClient 초기화 시 EmbeddingService 오류도 여기서 catch 가능
            _CHATBOT_CLIENT_INSTANCE = ChatbotClient(LLM_MODEL)
        except (ValueError, RuntimeError) as e:
            raise RuntimeError(f"챗봇 클라이언트 초기화 실패: {e}")
    return _CHATBOT_CLIENT_INSTANCE