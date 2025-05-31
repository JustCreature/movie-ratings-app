from app.database.models import MovieDB
from app.domain.repositories.base_repository import BaseRepository
from app.schemas.endpoints import MovieOut

MovieRepository = BaseRepository(
    model=MovieDB,
    schema=MovieOut
)