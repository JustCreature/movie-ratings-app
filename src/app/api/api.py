from fastapi import APIRouter

from app.api.endpoints import health, meta
from app.api.endpoints.v1 import api_router as v1_api_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(meta.router, tags=["meta"])
api_router.include_router(v1_api_router, tags=["v1_api_router"])
