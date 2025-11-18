from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock
from uuid import uuid4, UUID

import pytest_asyncio
from fastapi.testclient import TestClient

from src.adapters.config import set_config, reset_config
from src.adapters.inbound.api.dependencies import SessionDep, ConfigDep
from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.adapters.inbound.api.dependencies.repo_deps import (
    user_repository,
    bond_repository,
    bondholder_repository,
)
from src.adapters.inbound.api.main import app


@pytest_asyncio.fixture
async def mock_database_session() -> AsyncGenerator[AsyncMock, None]:
    yield AsyncMock()


@pytest_asyncio.fixture
async def mock_current_user() -> UUID:
    user = AsyncMock()
    user.id = uuid4()
    return user.id


@pytest_asyncio.fixture(scope="session", autouse=True)
def mock_config_globally() -> Generator[Mock, None, None]:
    mock = Mock()
    mock.SECRET_KEY = "test-secret-key"
    mock.ALGORITHM = "HS256"
    mock.DB_APP_USER = "test"
    mock.DB_APP_PASSWORD = "test"
    mock.DB_MIGRATION_USER = "test"
    mock.DB_MIGRATION_PASSWORD = "test"
    mock.DRIVER = "postgresql+asyncpg"
    mock.POSTGRES_HOST = "localhost"
    mock.POSTGRES_PORT = "5432"
    mock.POSTGRES_DB = "test"
    mock.database_app_url = "postgresql+asyncpg://test:test@localhost:5432/test"
    mock.database_migration_url = "postgresql+asyncpg://test:test@localhost:5432/test"

    set_config(mock)
    yield mock
    reset_config()


@pytest_asyncio.fixture
async def client(
    mock_database_session: AsyncMock,
    mock_current_user: UUID,
    mock_user_repo: AsyncMock,
    mock_bondholder_repo: AsyncMock,
    mock_bond_repo: AsyncMock,
    mock_config_globally: Mock,
) -> TestClient:
    app.dependency_overrides[SessionDep] = lambda: mock_database_session
    app.dependency_overrides[ConfigDep] = lambda: mock_config_globally
    app.dependency_overrides[current_user] = lambda: mock_current_user
    app.dependency_overrides[user_repository] = lambda: mock_user_repo
    app.dependency_overrides[bond_repository] = lambda: mock_bond_repo
    app.dependency_overrides[bondholder_repository] = lambda: mock_bondholder_repo

    yield TestClient(app)

    app.dependency_overrides.clear()
