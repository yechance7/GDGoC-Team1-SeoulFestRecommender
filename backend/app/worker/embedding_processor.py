import asyncio
from sqlalchemy.future import select
from app.db.database import SessionLocal
from app.entity.seoul_event_entity import SeoulEvent 
from app.services.embedding_service import EmbeddingService 
from typing import List

BATCH_SIZE = 50                 # 한 번에 처리할 이벤트 개수
INTERVAL_SECONDS = 60 * 60 * 24 # 임베딩할 데이터가 없을 때 긴 대기 시간 (24시간)
SLEEP_TIME = 5                  # 에러 발생 후 대기 시간 (5초)

def process_embeddings():
    """
    DB에서 임베딩이 필요한 이벤트를 찾아 임베딩을 처리하고 저장하는 메인 함수.
    """
    try:
        embedding_service = EmbeddingService()
    except ValueError as e:
        print(f"❌ 워커 초기화 실패: {e}")
        return

    asyncio.run(_async_process_embeddings(embedding_service)) 

async def _async_process_embeddings(embedding_service: EmbeddingService):
    """
    실제 비동기 임베딩 처리 로직 (무한 루프)
    """
    while True:
        db = SessionLocal()
        try:
            print(f"임베딩 워커 실행 중: 임베딩이 필요한 이벤트 검색...")

            # 임베딩이 NULL인 이벤트 검색 (BATCH_SIZE만큼 제한)
            stmt = select(SeoulEvent).where( 
                SeoulEvent.embedding.is_(None)
            ).limit(BATCH_SIZE)
            
            events_to_embed: List[SeoulEvent] = db.execute(stmt).scalars().all()
            
            # --- 데이터 없음: 긴 대기 모드 진입 ---
            if not events_to_embed:
                print(f"임베딩할 이벤트 데이터가 없습니다. ({INTERVAL_SECONDS}초 대기).")
                
                db.close()
                await asyncio.sleep(INTERVAL_SECONDS)
                continue

            print(f"💡 {len(events_to_embed)}개의 이벤트 임베딩을 비동기 처리합니다.")

            # --- 비동기 병렬 처리 ---
            tasks = []
            for event in events_to_embed:
                text_chunk = event.get_rag_chunk()
                tasks.append(embedding_service.create_db_embedding(text_chunk)) 

            results = await asyncio.gather(*tasks, return_exceptions=True) 
            
            # --- 결과 처리 및 DB 업데이트 ---
            for event, vector_data in zip(events_to_embed, results):
                if isinstance(vector_data, list): # 성공적으로 벡터를 받은 경우
                    event.embedding = vector_data
                    print(f" - [ID: {event.id}, 제목: {event.title[:15]}...] 임베딩 완료.")
                else: 
                    # 오류 발생 (Exception이거나 API에서 벡터를 반환하지 않은 경우)
                    error_msg = str(vector_data) if vector_data else "API 벡터 없음"
                    print(f" - [ID: {event.id}] 임베딩 실패 또는 오류 발생: {error_msg}")

            db.commit()
            await asyncio.sleep(1) 
            
        except Exception as e:
            print(f"❌ 임베딩 워커 오류 발생: {e}")
            db.rollback()
            await asyncio.sleep(SLEEP_TIME) # 오류 발생 시 5초 대기 후 재시도
        finally:
            db.close()

if __name__ == "__main__":
    process_embeddings()