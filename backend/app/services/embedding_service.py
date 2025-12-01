# backend/app/services/embedding_service.py

import os
from typing import List, Optional
from app.core.config import settings
import json
import httpx # httpx 추가 (Poetry에 의존성 추가 필요)

class EmbeddingService: 
    """
    Upstage Solar API를 사용하여 임베딩 작업을 처리하는 서비스.
    """
    def __init__(self):
        self.api_key = os.getenv("SOLAR_API_KEY")
        self.embedding_model = os.getenv("SOLAR_EMBEDDING_PASSAGE")
        self.api_endpoint_url = os.getenv("SOLAR_EMBEDDING_API_URL")

        if not self.api_key:
            raise ValueError("SOLAR_API_KEY 환경 변수가 설정되지 않았습니다. 워커를 실행할 수 없습니다.")
            
    async def db_embedding(self, text: str) -> Optional[List[float]]:
        """
        주어진 텍스트에 대한 임베딩 벡터를 생성하여 반환합니다.
        (async/await를 사용하여 비동기로 호출)
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.embedding_model,
            "input": [text],
            "input_type": "document"
        }

        # 비동기 클라이언트 사용 (타임아웃 설정)
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # await을 사용하여 비동기 POST 요청
                response = await client.post(self.api_endpoint_url, headers=headers, json=data) 
                response.raise_for_status() 

                result = response.json()
                
                if result.get('data') and result['data'][0].get('embedding'):
                    return result['data'][0]['embedding']
                
                print(f"임베딩 API 응답에 벡터 데이터가 없습니다: {result}")
                return None

            except httpx.RequestError as e:
                print(f"Upstage Solar API 호출 오류 발생: {e}")
                # 응답 객체가 없을 수 있으므로 response.status_code 및 response.text 출력은 제외
                return None
            except Exception as e:
                print(f"임베딩 생성 중 알 수 없는 오류 발생: {e}")
                return None