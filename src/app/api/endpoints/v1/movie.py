from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.schemas.endpoints as sc
import app.database.models as orm
from app.dependencies import get_db

log = structlog.get_logger()

router = APIRouter()


# ---------- Movie Endpoints ----------
@router.post("/movies", response_model=sc.MovieOut, status_code=status.HTTP_201_CREATED)
async def create_movie(movie: sc.MovieCreate, db: AsyncSession = Depends(get_db)):
    new_movie = orm.MovieDB(**movie.dict())
    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)
    log.info("movie_created", movie_id=new_movie.id)
    return new_movie


@router.get("/movies/{movie_id}", response_model=sc.MovieOut)
async def get_movie(movie_id: UUID, db: AsyncSession = Depends(get_db)):
    movie = await db.get(orm.MovieDB, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


# @router.get("/movies", response_model=list[sc.MovieOut])
# async def get_movie(db: AsyncSession = Depends(get_db)):
#     movies = await db.get(orm.MovieDB)
#     if not movie:
#         raise HTTPException(status_code=404, detail="Movie not found")
#     return movie