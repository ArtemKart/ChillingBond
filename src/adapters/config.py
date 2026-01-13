import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src import ROOTDIR


class Config(BaseSettings):
    APP_DATABASE_URL: str
    MIGRATION_DATABASE_URL: str

    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(16))
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=ROOTDIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_app_url(self) -> str:
        return self.APP_DATABASE_URL

    @property
    def database_migration_url(self) -> str:
        return self.APP_DATABASE_URL


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
