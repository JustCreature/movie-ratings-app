from app.database.models import RatingDB
from app.domain.repositories.base_repository import BaseRepository
from app.schemas.endpoints import RatingOut

RatingRepository = BaseRepository(
    model=RatingDB,
    schema=RatingOut
)