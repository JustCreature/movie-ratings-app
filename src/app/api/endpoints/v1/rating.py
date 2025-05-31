from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.schemas.endpoints as sc
from app.dependencies import get_db
from app.domain.repositories.rating_repository import RatingRepository

log = structlog.get_logger()

router = APIRouter()


@router.post("/ratings", response_model=sc.RatingOut, status_code=status.HTTP_201_CREATED)
async def rate_movie(rating: sc.RatingCreate, db: AsyncSession = Depends(get_db)):
    filters = [
        ("user_id", rating.user_id),
        ("movie_id", rating.movie_id),
    ]
    existing = await RatingRepository.find_one(db, filters=filters)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rating already exists for this user/movie",
        )

    new_rating = await RatingRepository.create(db, **rating.model_dump())
    log.info("rating_created", rating_id=new_rating.id)
    return new_rating


@router.get("/ratings/{movie_id}", response_model=sc.RatingListOut)
async def get_ratings(
    movie_id: UUID,
    db: AsyncSession = Depends(get_db),
    offset: int | None = Query(0, ge=0, description="Query result offset"),
    limit: int | None = Query(10, le=100, description="Query result limit"),
) -> sc.RatingListOut:
    filters = [("movie_id", movie_id)]
    ratings = await RatingRepository.find(db, filters=filters, offset=offset, limit=limit)
    total = await RatingRepository.count(db, filters=filters)
    return sc.RatingListOut(items=ratings, total=total)
