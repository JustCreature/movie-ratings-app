import os
from enum import Enum

import pydantic
from pydantic import PostgresDsn, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.uvicorn_settings import UvicornSettings


class Environment(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "dev"


class DBSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "moviedb"
    user: str = "postgres"
    password: str = "postgres"


class Settings(BaseSettings):
    ENV_NAME: str | None = None
    ENVIRONMENT: Environment = Environment.LOCAL

    DEBUG: bool = False

    db: DBSettings = pydantic.Field(default_factory=DBSettings)
    uvicorn: UvicornSettings = pydantic.Field(default_factory=UvicornSettings)

    @property
    def DB_URL(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            host=self.db.host,
            port=self.db.port,
            path=f"{self.db.name}",
            username=self.db.user,
            password=self.db.password,
        ).unicode_string()

    @property
    def DB_URL_SYNC(self) -> str:
        return PostgresDsn.build(
            scheme="postgresql",
            host=self.db.host,
            port=self.db.port,
            path=f"{self.db.name}",
            username=self.db.user,
            password=self.db.password,
        ).unicode_string()

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file_encoding="utf-8",
        # Allows variables to be read as dicts. Eg: FOO__BAR=5 -> {"foo": {"bar": 5}}
        env_nested_delimiter="__",
    )


settings = Settings(_env_file=os.getenv("ENV_FILES", "").split())  # type: ignore
