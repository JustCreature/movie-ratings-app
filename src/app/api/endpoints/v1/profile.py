from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.schemas.endpoints as sc
from app.dependencies import get_db
from app.domain.repositories.rating_repository import RatingRepository
from app.domain.repositories.user_repository import UserRepository

log = structlog.get_logger()

router = APIRouter()


@router.get("/user-profile/{user_id}", response_model=sc.UserProfileOut)
async def get_ratings(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    offset: int | None = Query(0, ge=0, description="Query result offset"),
    limit: int | None = Query(10, le=100, description="Query result limit"),
) -> sc.UserProfileOut:
    user = await UserRepository.find_one(db, [("id", user_id)])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    filters = [("user_id", user_id)]
    ratings = await RatingRepository.find(db, filters=filters, offset=offset, limit=limit)
    total = await RatingRepository.count(db, filters=filters)
    return sc.UserProfileOut(
        user=user, ratings=sc.RatingListOut(items=ratings, total=total)
    )
