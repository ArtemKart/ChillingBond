from datetime import date, datetime
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

import pytest_asyncio

from src.application.events.event_publisher import EventPublisher
from src.domain.entities.bond import Bond as BondEntity
from src.domain.entities.bondholder import BondHolder as BondHolderEntity
from src.domain.entities.user import User as UserEntity
from src.domain.ports.services.password_hasher import PasswordHasher
from src.domain.ports.services.token_handler import TokenHandler
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.user import UserRepository


@pytest_asyncio.fixture
def bondholder_entity_mock() -> Mock:
    bh = Mock(spec=BondHolderEntity)
    bh.id = uuid4()
    bh.bond_id = uuid4()
    bh.user_id = uuid4()
    bh.quantity = 100
    bh.purchase_date = date.today()
    bh.last_update = datetime.now()
    return bh


@pytest_asyncio.fixture
def bond_entity_mock() -> Mock:
    bond = Mock(spec=BondEntity)
    bond.id = uuid4()
    bond.series = "ROR1206"
    bond.nominal_value = 100.0
    bond.maturity_period = 12
    bond.initial_interest_rate = 4.75
    bond.first_interest_period = 1
    bond.reference_rate_margin = 0.0
    return bond


@pytest_asyncio.fixture
def user_entity_mock(mock_hasher: Mock) -> Mock:
    user = Mock(spec=UserEntity)
    user.id = uuid4()
    user.email = "test@example.com"
    user.hashed_password = "hashed_password_123"
    user.hasher = mock_hasher
    user.name = "Test User"
    return user


@pytest_asyncio.fixture
def mock_hasher() -> Mock:
    return Mock(spec=PasswordHasher)


@pytest_asyncio.fixture
def mock_token_handler() -> Mock:
    return Mock(spec=TokenHandler)


@pytest_asyncio.fixture
def mock_bond_repo() -> AsyncMock:
    return AsyncMock(spec=BondRepository)


@pytest_asyncio.fixture
def mock_bondholder_repo() -> AsyncMock:
    return AsyncMock(spec=BondHolderRepository)


@pytest_asyncio.fixture
def mock_user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)

@pytest_asyncio.fixture
def mock_event_publisher() -> AsyncMock:
    return AsyncMock(spec=EventPublisher)
