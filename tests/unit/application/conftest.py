from unittest.mock import AsyncMock

import pytest

from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.user import UserRepository
from src.domain.ports.services.password_hasher import PasswordHasher
from src.domain.ports.services.token_handler import TokenHandler


@pytest.fixture
async def mock_bond_repo() -> AsyncMock:
    return AsyncMock(spec=BondRepository)


@pytest.fixture
async def mock_bondholder_repo() -> AsyncMock:
    return AsyncMock(spec=BondHolderRepository)


@pytest.fixture
async def mock_user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_hasher() -> AsyncMock:
    return AsyncMock(spec=PasswordHasher)


@pytest.fixture
def mock_token_handler() -> AsyncMock:
    return AsyncMock(spec=TokenHandler)
