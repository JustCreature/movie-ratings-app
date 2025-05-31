from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import SessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()