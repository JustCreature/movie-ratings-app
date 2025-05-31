import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

import app.schemas.endpoints as sc
import app.database.models as orm
from app.dependencies import get_db

log = structlog.get_logger()

router = APIRouter()

# ---------- Profile Endpoint ----------
@router.get("/users/{user_id}/profile", response_model=sc.UserProfile)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(orm.UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(orm.RatingDB).where(orm.RatingDB.user_id == user_id)
    )
    ratings = result.scalars().all()
    return {"user": user, "rated_movies": ratings}