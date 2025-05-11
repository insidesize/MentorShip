from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from app.schemas import SearchQuery
from app.kafka_producer import send_search_task
from app.cache import redis_cache, get_cached_result, set_cached_result
from app.database import save_search_results_to_db
import asyncio
import time
import uuid
import json
import logging
from app.kafka_producer import kafka_producer

app = FastAPI()

TIMEOUT = 10  # секунды ожидания результата из Kafka
logger = logging.getLogger(__name__)




@app.post("/search", response_model=dict)
async def search_handler(
    search_query: SearchQuery,
    response: Response,
    background_tasks: BackgroundTasks,
):
    start_time = time.perf_counter()
    query = search_query.query
    cache_key = f"search:{query}"

    # Проверка кэша
    cached = await redis_cache.get(cache_key)
    if cached:
        cached_data = json.loads(cached)
        return {
            "request_id": cached_data["request_id"],
            "games": cached_data["games"],
            "providers": cached_data["providers"],
        }

    # Запрос в Kafka
    request_id = str(uuid.uuid4())
    await send_search_task({**search_query.dict(), "request_id": request_id})

    # Ожидание результата
    polling_interval = 0.1
    total_wait = 0
    while total_wait < TIMEOUT:
        result = await redis_cache.get(cache_key)
        if result:
            data = json.loads(result)
            games = data["games"]
            providers = data["providers"]

            # Опционально — сохраняем в БД в фоне
            background_tasks.add_task(
                save_search_results_to_db, query, games, providers
            )

            return {
                "request_id": request_id,
                "games": games,
                "providers": providers,
            }

        await asyncio.sleep(polling_interval)
        total_wait += polling_interval

    response.status_code = 504
    raise HTTPException(status_code=504, detail="Search task timed out")

@app.on_event("startup")
async def startup_event():
    await kafka_producer.init()
    logger.info("Kafka producer started")

@app.on_event("shutdown")
async def shutdown_event():
    await kafka_producer.close()
    logger.info("Kafka producer stopped")