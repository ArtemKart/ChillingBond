from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from src import ROOTDIR


class Config(BaseSettings):
    DB_APP_USER: str
    DB_APP_PASSWORD: str

    DB_MIGRATION_USER: str
    DB_MIGRATION_PASSWORD: str

    DRIVER: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(
        env_file=ROOTDIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_app_url(self) -> str:
        return (
            f"{self.DRIVER}://{self.DB_APP_USER}:"
            f"{self.DB_APP_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_migration_url(self) -> URL:
        return (
            f"{self.DRIVER}://{self.DB_MIGRATION_USER}:"
            f"{self.DB_MIGRATION_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_config() -> Config:
    return Config()
