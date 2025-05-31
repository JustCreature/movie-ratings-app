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

# ---------- Rating Endpoints ----------
@router.post("/ratings", response_model=sc.RatingOut, status_code=status.HTTP_201_CREATED)
async def rate_movie(rating: sc.RatingCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(orm.RatingDB).where(
            orm.RatingDB.user_id == rating.user_id, orm.RatingDB.movie_id == rating.movie_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Rating already exists for this user/movie")

    new_rating = orm.RatingDB(**rating.dict())
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)
    log.info("rating_created", rating_id=new_rating.id)
    return new_rating

@router.get("/ratings/{movie_id}", response_model=list[sc.RatingOut])
async def get_ratings(movie_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(orm.RatingDB).where(orm.RatingDB.movie_id == movie_id)
    )
    return result.scalars().all()
