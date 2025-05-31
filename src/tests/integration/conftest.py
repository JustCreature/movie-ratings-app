from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.base_model import TopLevelModel
from app.settings import settings


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    assert settings.db.name.startswith("test"), "not a test DB"

    engine = create_async_engine(settings.DB_URL)

    async with engine.begin() as conn:
        await conn.run_sync(TopLevelModel.metadata.drop_all)
        await conn.run_sync(TopLevelModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(TopLevelModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    LocalTestingSession = async_sessionmaker(
        bind=db_engine, autoflush=False, expire_on_commit=False
    )
    async with LocalTestingSession() as test_session:
        yield test_session
