from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.adapters.inbound.api.dependencies import SessionDep
from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.adapters.inbound.api.main import app


@pytest.fixture
async def mock_database_session() -> AsyncGenerator[AsyncMock, None]:
    yield AsyncMock()


@pytest.fixture
async def client(mock_database_session: AsyncMock, mock_user_cookie: AsyncMock) -> TestClient:
    app.dependency_overrides[SessionDep] = lambda: mock_database_session
    app.dependency_overrides[current_user] = lambda: mock_user_cookie
    yield TestClient(app)
