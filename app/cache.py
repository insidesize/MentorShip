import json
import asyncio
import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

async def get_from_cache(key: str):
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None

async def set_to_cache(key: str, value, expire: int = 300):
    await redis_client.set(key, json.dumps(value), ex=expire)