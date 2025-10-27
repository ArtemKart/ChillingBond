from unittest.mock import AsyncMock

import pytest_asyncio

from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.user import UserRepository


@pytest_asyncio.fixture
def mock_bond_repo() -> AsyncMock:
    return AsyncMock(spec=BondRepository)


@pytest_asyncio.fixture
def mock_bondholder_repo() -> AsyncMock:
    return AsyncMock(spec=BondHolderRepository)


@pytest_asyncio.fixture
def mock_user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)
