from typing import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import uuid4, UUID

import pytest_asyncio
from fastapi.testclient import TestClient

from src.adapters.inbound.api.dependencies import SessionDep
from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.adapters.inbound.api.main import app


@pytest_asyncio.fixture
async def mock_database_session() -> AsyncGenerator[AsyncMock, None]:
    yield AsyncMock()


@pytest_asyncio.fixture
async def mock_current_user() -> AsyncGenerator[UUID, None]:
    user = AsyncMock()
    user.id = uuid4()
    # user.email = "mock_current_user@email.com"
    # user.password = "password"
    yield user.id


@pytest_asyncio.fixture
async def client(
    mock_database_session: AsyncMock, mock_current_user: AsyncMock
) -> TestClient:
    app.dependency_overrides[SessionDep] = lambda: mock_database_session
    app.dependency_overrides[current_user] = lambda: mock_current_user
    yield TestClient(app)
