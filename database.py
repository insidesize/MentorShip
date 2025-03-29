from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

Base = "postgresql+asyncpg://swager:NikFast65@localhost:5432/swagadb"

engine = create_async_engine(Base, pool_size=10, max_overflow=20)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
