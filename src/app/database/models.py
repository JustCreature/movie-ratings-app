import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import String, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base_model import TopLevelModel


# ---------- Models ----------
class UserDB(TopLevelModel):
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    ratings: Mapped["RatingDB"] = relationship("RatingDB", back_populates="user")


class MovieDB(TopLevelModel):
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    ratings: Mapped["RatingDB"] = relationship("RatingDB", back_populates="movie")


class RatingDB(TopLevelModel):
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_db.id"))
    movie_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("movie_db.id"))
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped["UserDB"] = relationship("UserDB", back_populates="ratings")
    movie: Mapped["MovieDB"] = relationship("MovieDB", back_populates="ratings")

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="unique_user_movie"),)
