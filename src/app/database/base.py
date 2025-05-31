from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..settings import settings


def get_base_db_engine_and_session():
    engine = create_async_engine(
        settings.DB_URL,
        pool_pre_ping=True,
        pool_timeout=30,  # In seconds (Default is 30s)
        future=True,
        echo=True,
    )
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    return engine, SessionLocal
