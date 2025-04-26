from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Game, Provider
from app.schemas import GameCreate, ProviderCreate, ProviderResponse
from app.database import get_db
from sqlalchemy.future import select
from . import models,schemas
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.cache import get_from_cache, set_to_cache
import json
import redis.asyncio as redis

app = FastAPI()

redis_client = redis.from_url("redis://localhost", decode_responses=True)

CACHE_TTL = 300

@app.post("/providers/", response_model=ProviderResponse)
async def create_provider(provider: ProviderCreate, db: AsyncSession = Depends(get_db)):
    db_provider = Provider(**provider.dict())
    db.add(db_provider)
    await db.commit()
    await db.refresh(db_provider)
    return db_provider

@app.get("/providers/{provider_id}", response_model=schemas.ProviderResponse)
async def read_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    cache_key = f"provider:{provider_id}"
    cached_provider = await redis_client.get(cache_key)
    
    if cached_provider:
        return schemas.ProviderResponse(**json.loads(cached_provider))

    result = await db.execute(select(models.Provider).filter(models.Provider.id == provider_id))
    provider = result.scalars().first()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider_data = schemas.ProviderResponse.from_orm(provider).dict()
    await redis_client.set(cache_key, json.dumps(provider_data), ex=CACHE_TTL)
    return provider_data

@app.put("/providers/{provider_id}", response_model=schemas.ProviderResponse)
async def update_provider(provider_id: int, provider_data: schemas.ProviderCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Provider).filter(models.Provider.id == provider_id))
    provider = result.scalars().first()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    for key, value in provider_data.dict().items():
        setattr(provider, key, value)

    await db.commit()
    await db.refresh(provider)

    # обновляем
    cache_key = f"provider:{provider_id}"
    await redis_client.set(cache_key, json.dumps(schemas.ProviderResponse.from_orm(provider).dict()), ex=CACHE_TTL)

    return provider

@app.delete("/providers/{provider_id}")
async def delete_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Provider).filter_by(id=provider_id))
    provider = result.scalars().first()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        await db.delete(provider)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Cannot delete provider with existing games")

    # удаляем
    cache_key = f"provider:{provider_id}"
    await redis_client.delete(cache_key)

    return {"detail": "Provider deleted"}

@app.post("/games/", response_model=schemas.GameResponse)
async def create_game(game: schemas.GameCreate, db: AsyncSession = Depends(get_db)):
    db_game = models.Game(**game.dict())
    db.add(db_game)
    await db.commit()
    await db.refresh(db_game)
    return db_game

@app.get("/games/{game_id}", response_model=schemas.GameResponse)
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    cache_key = f"game:{game_id}"
    cached_game = await redis_client.get(cache_key)

    if cached_game:
        return schemas.GameResponse(**json.loads(cached_game))

    result = await db.execute(select(models.Game).filter_by(id=game_id))
    game = result.scalars().first()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    game_data = schemas.GameResponse.from_orm(game).dict()
    await redis_client.set(cache_key, json.dumps(game_data), ex=CACHE_TTL)
    return game_data

@app.put("/games/{game_id}", response_model=schemas.GameResponse)
async def update_game(game_id: int, data: schemas.GameCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Game).filter_by(id=game_id))
    game = result.scalars().first()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    for key, value in data.dict().items():
        setattr(game, key, value)

    await db.commit()
    await db.refresh(game)

    # обновление кеша
    cache_key = f"game:{game_id}"
    await redis_client.set(cache_key, json.dumps(schemas.GameResponse.from_orm(game).dict()), ex=CACHE_TTL)

    return game

@app.delete("/games/{game_id}")
async def delete_game(game_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Game).filter_by(id=game_id))
    game = result.scalars().first()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    await db.delete(game)
    await db.commit()

    # удаление из кеша
    cache_key = f"game:{game_id}"
    await redis_client.delete(cache_key)

    return {"detail": "Game deleted"}