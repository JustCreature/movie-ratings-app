from uuid import UUID

from pydantic import BaseModel, Field, constr


# ---------- Schemas ----------
class UserCreate(BaseModel):
    name: str
    email: constr(strip_whitespace=True, to_lower=True)


class UserOut(BaseModel):
    id: UUID
    name: str
    email: str

    class Config:
        orm_mode = True


class MovieCreate(BaseModel):
    title: str
    description: str | None = None


class MovieOut(BaseModel):
    id: UUID
    title: str
    description: str | None = None

    class Config:
        orm_mode = True


class MovieListOut(BaseModel):
    items: list[MovieOut]
    total: int


class RatingCreate(BaseModel):
    user_id: UUID
    movie_id: UUID
    rating: float = Field(..., ge=1.0, le=10.0)


class RatingOut(BaseModel):
    id: UUID
    user_id: UUID
    movie_id: UUID
    rating: float

    class Config:
        orm_mode = True


class RatingListOut(BaseModel):
    items: list[RatingOut]
    total: int


class UserProfileOut(BaseModel):
    user: UserOut
    ratings: RatingListOut
