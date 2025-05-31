from app.database.models import UserDB
from app.domain.repositories.base_repository import BaseRepository
from app.schemas.endpoints import UserOut

UserRepository = BaseRepository(model=UserDB, schema=UserOut)
