from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.schemas.endpoints as sc
from app.dependencies import get_db
from app.domain.repositories.user_repository import UserRepository

log = structlog.get_logger()

router = APIRouter()


@router.post("/users", response_model=sc.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: sc.UserCreate, db: AsyncSession = Depends(get_db)) -> sc.UserOut:
    filters = [("email", user.email)]
    existing = await UserRepository.find_one(db, filters=filters)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User already exists with email {user.email}")

    new_user = await UserRepository.create(db, **user.model_dump())
    log.info("user_created", user_id=new_user.id)

    return new_user


@router.get("/users/{user_id}", response_model=sc.UserOut)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> sc.UserOut:
    filters = [("id", user_id)]
    user = await UserRepository.find_one(db, filters=filters)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
