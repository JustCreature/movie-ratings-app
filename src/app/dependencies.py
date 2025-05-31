from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_base_db_engine_and_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    _, SessionLocal = get_base_db_engine_and_session()
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()