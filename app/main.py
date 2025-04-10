from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Game, Provider
from app.schemas import GameCreate, ProviderCreate, ProviderResponse
from app.database import get_db
from sqlalchemy.future import select

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


#TODO
#games endpoints