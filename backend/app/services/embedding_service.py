# backend/app/services/embedding_service.py

import os
import asyncio
from typing import List, Optional, Literal
from app.core.config import settings
import json
import httpx

class EmbeddingService: 
    """
    Upstage Solar API를 사용하여 임베딩 작업을 처리하는 서비스.
    """
    def __init__(self):
        self.api_key = os.getenv("SOLAR_API_KEY")
        self.passage_model = os.getenv("SOLAR_EMBEDDING_PASSAGE")
        self.query_model = os.getenv("SOLAR_EMBEDDING_QUERY")
        self.api_endpoint_url = os.getenv("SOLAR_EMBEDDING_API_URL")

        if not self.api_key:
            raise ValueError("SOLAR_API_KEY 환경 변수가 설정되지 않았습니다. 워커를 실행할 수 없습니다.")
    
    async def _create_embedding(self, text: str, model_name: str, input_type: Literal["document", "query"]) -> Optional[List[float]]:
        """
        내부적으로 임베딩 API를 호출하는 비동기 함수
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_name,
            "input": [text],
            "input_type": input_type
        }

        for attempt in (1, 2, 3):
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(self.api_endpoint_url, headers=headers, json=data)
                    response.raise_for_status()

                    result = response.json()
                    
                    if result.get('data') and result['data'][0].get('embedding'):
                        return result['data'][0]['embedding']
                    
                    print(f"임베딩 API 응답에 벡터 데이터가 없습니다: {result}")
                    return None

                except httpx.HTTPStatusError as e:
                    status = e.response.status_code if e.response else None
                    if status == 429 and attempt < 3:
                        await asyncio.sleep(3 * attempt)
                        continue
                    print(f"Upstage Solar API HTTP 오류 발생 (status={status}): {e}")
                    return None
                except httpx.RequestError as e:
                    print(f"Upstage Solar API 호출 오류 발생: {e}")
                    return None
                except Exception as e:
                    print(f"임베딩 생성 중 알 수 없는 오류 발생: {e}")
                    return None

        return None

    # Passage 임베딩 (DB 저장용)
    async def db_embedding(self, text: str) -> Optional[List[float]]:
        """
        DB에 저장할 이벤트 텍스트(document)에 대한 임베딩 벡터를 생성합니다.
        """
        return await self._create_embedding(text, self.passage_model, "document")
    
    # Query 임베딩 (유저 질문 검색용)
    async def query_embedding(self, text: str) -> Optional[List[float]]:
        """
        사용자 질문(query)에 대한 임베딩 벡터를 생성합니다.
        """
        return await self._create_embedding(text, self.query_model, "query")