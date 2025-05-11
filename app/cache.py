import json
import asyncio
import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Функция для получения данных из Redis
async def get_cached_result(key: str):
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None

# Функция для сохранения данных в Redis
async def set_cached_result(key: str, value, expire: int = 300):
    await redis_client.set(key, json.dumps(value), ex=expire)

# Если необходимо для совместимости с именем redis_cache (опционально):
redis_cache = redis_client