import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src import ROOTDIR


class Config(BaseSettings):
    MIGRATION_DATABASE_URL: str | None = None
    APP_DATABASE_URL: str | None = None

    DB_APP_USER: str
    DB_APP_PASSWORD: str

    DB_MIGRATION_USER: str
    DB_MIGRATION_PASSWORD: str

    DRIVER: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(16))
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=ROOTDIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_app_url(self) -> str:
        if self.APP_DATABASE_URL:
            return self.APP_DATABASE_URL
        return (
            f"{self.DRIVER}://{self.DB_APP_USER}:"
            f"{self.DB_APP_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_migration_url(self) -> str:
        if self.MIGRATION_DATABASE_URL:
            return self.MIGRATION_DATABASE_URL
        return (
            f"{self.DRIVER}://{self.DB_MIGRATION_USER}:"
            f"{self.DB_MIGRATION_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


_config_instance: Config | None = None


def get_config() -> Config:
    """
    Retrieve the configuration instance.

    In production, creates a single instance on first call.
    In tests, can be overridden using set_config().

    Returns:
        Config: The application configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def set_config(config: Config) -> None:
    """
    Manually set the configuration instance (used in tests).

    Args:
        config: Config instance (can be a mock object)
    """
    global _config_instance
    _config_instance = config


def reset_config() -> None:
    """
    Reset the configuration instance (used for test cleanup).
    """
    global _config_instance
    _config_instance = None
