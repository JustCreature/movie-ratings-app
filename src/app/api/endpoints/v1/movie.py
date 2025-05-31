from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.schemas.endpoints as sc
from app.dependencies import get_db
from app.domain.repositories.movie_repository import MovieRepository

log = structlog.get_logger()

router = APIRouter()


@router.post("/movies", response_model=sc.MovieOut, status_code=status.HTTP_201_CREATED)
async def create_movie(movie: sc.MovieCreate, db: AsyncSession = Depends(get_db)) -> sc.MovieOut:
    filters = [("title", movie.title)]
    existing = await MovieRepository.find_one(db, filters=filters)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Movie already exists with title {movie.title}",
        )

    new_movie = await MovieRepository.create(db, commit=True, **movie.model_dump())
    log.info("movie_created", movie_id=new_movie.id)
    return new_movie


@router.get("/movies/{movie_id}", response_model=sc.MovieOut)
async def get_movie(movie_id: UUID, db: AsyncSession = Depends(get_db)) -> sc.MovieOut:
    filters = [("id", movie_id)]
    movie = await MovieRepository.find_one(db, filters=filters)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie


@router.get("/movies", response_model=sc.MovieListOut)
async def get_movie(
    db: AsyncSession = Depends(get_db),
    offset: int | None = Query(0, ge=0, description="Query result offset"),
    limit: int | None = Query(10, le=100, description="Query result limit"),
) -> sc.MovieListOut:
    movies = await MovieRepository.find(db, offset=offset, limit=limit)
    total = await MovieRepository.count(db)
    return sc.MovieListOut(items=movies, total=total)
