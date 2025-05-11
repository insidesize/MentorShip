from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models import Game, Provider  # Импорт моделей для сохранения данных

DATABASE_URL = "postgresql+asyncpg://swager:NikFast65@postgres:5432/swagadb"

engine = create_async_engine(DATABASE_URL, pool_size=10, max_overflow=20)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Функция для сохранения результатов поиска в БД
async def save_search_results_to_db(query: str, games: list, providers: list, db_session: AsyncSession):
    try:
        # Сохраняем игры
        for game in games:
            db_game = Game(title=game["title"], price=game["price"], provider_id=game["provider_id"])
            db_session.add(db_game)

        # Сохраняем провайдеров
        for provider in providers:
            db_provider = Provider(name=provider["name"], email=provider["email"])
            db_session.add(db_provider)

        # Подтверждаем изменения
        await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        raise RuntimeError(f"Error saving search results to DB: {e}")