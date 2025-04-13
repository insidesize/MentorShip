from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Game, Provider
from app.schemas import GameCreate, ProviderCreate, ProviderResponse
from app.database import get_db
from sqlalchemy.future import select
from . import models,schemas
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

app = FastAPI()


@app.post("/providers/", response_model=ProviderResponse)
async def create_provider(provider: ProviderCreate, db: AsyncSession = Depends(get_db)):
    db_provider = Provider(**provider.dict())
    db.add(db_provider)
    await db.commit()
    await db.refresh(db_provider)
    return db_provider

@app.get("/providers/{provider_id}", response_model=ProviderResponse)
async def read_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Provider).filter(Provider.id==provider_id))
    provider = result.scalars().first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@app.put("/providers/{provider_id}", response_model=schemas.ProviderResponse)
async def update_provider(provider_id: int, provider_data: ProviderCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Provider).filter(Provider.id == provider_id))
    provider = result.scalars().first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    for key, value in provider_data.dict().items():
        setattr(provider, key, value)
    await db.commit()
    await db.refresh(provider)
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
    result = await db.execute(select(models.Game).filter_by(id=game_id))
    game = result.scalars().first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

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
    return game

@app.delete("/games/{game_id}")
async def delete_game(game_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Game).filter_by(id=game_id))
    game = result.scalars().first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    await db.delete(game)
    await db.commit()
    return {"detail": "Game deleted"}