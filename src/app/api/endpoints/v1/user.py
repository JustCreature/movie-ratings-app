import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import app.schemas.endpoints as sc
import app.database.models as orm
from app.dependencies import get_db

log = structlog.get_logger()

router = APIRouter()

# ---------- User Endpoints ----------
@router.post("/users", response_model=sc.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: sc.UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = orm.UserDB(**user.dict())
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        log.info("user_created", user_id=new_user.id)
        return new_user
    except Exception as e:
        await db.rollback()
        log.error("create_user_error", error=str(e))
        raise HTTPException(status_code=400, detail="User already exists or invalid data")


@router.get("/users/{user_id}", response_model=sc.UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.get(orm.UserDB, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result
