from fastapi import APIRouter

from app.api.endpoints.v1 import movie, user, rating, profile

api_router = APIRouter(prefix="/v1")
api_router.include_router(movie.router, tags=["movie"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(rating.router, tags=["rating"])
api_router.include_router(profile.router, tags=["profile"])
