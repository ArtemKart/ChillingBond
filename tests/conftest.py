from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.adapters.outbound.repositories.reference_rate import ReferenceRateEntity
from src.application.events.event_publisher import EventPublisher
from src.domain.entities.bond import Bond as BondEntity
from src.domain.entities.bondholder import BondHolder as BondHolderEntity
from src.domain.entities.user import User as UserEntity
from src.domain.ports.repositories.bond import BondRepository
from src.domain.ports.repositories.bondholder import BondHolderRepository
from src.domain.ports.repositories.reference_rate import ReferenceRateRepository
from src.domain.ports.repositories.user import UserRepository
from src.domain.ports.services.password_hasher import PasswordHasher
from src.domain.ports.services.token_handler import TokenHandler
from src.domain.services.bondholder_deletion_service import BondHolderDeletionService
from src.domain.services.bondholder_income_calculator import BondHolderIncomeCalculator


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def bondholder_entity_mock() -> Mock:
    bh = Mock(spec=BondHolderEntity)
    bh.id = uuid4()
    bh.bond_id = uuid4()
    bh.user_id = uuid4()
    bh.quantity = 100
    bh.purchase_date = date.today()
    bh.last_update = datetime.now()
    return bh


@pytest.fixture
def bond_entity_mock() -> Mock:
    bond = Mock(spec=BondEntity)
    bond.id = uuid4()
    bond.series = "ROR1206"
    bond.nominal_value = Decimal("100.0")
    bond.maturity_period = 12
    bond.initial_interest_rate = Decimal("4.75")
    bond.first_interest_period = 1
    bond.reference_rate_margin = Decimal("0.0")
    return bond


@pytest.fixture
def user_entity_mock(mock_hasher: Mock) -> Mock:
    user = Mock(spec=UserEntity)
    user.id = uuid4()
    user.email = "test@example.com"
    user.hashed_password = "hashed_password_123"
    user.hasher = mock_hasher
    user.name = "Test User"
    return user


@pytest.fixture
def mock_reference_rate_entity() -> Mock:
    ref_rate = Mock(spec=ReferenceRateEntity)
    ref_rate.id = uuid4()
    ref_rate.value = Decimal("5.25")
    ref_rate.start_date = date.today() - timedelta(days=30)
    ref_rate.end_date = date.today() + timedelta(days=30)
    return ref_rate


@pytest.fixture
def mock_hasher() -> Mock:
    return Mock(spec=PasswordHasher)


@pytest.fixture
def mock_token_handler() -> Mock:
    return Mock(spec=TokenHandler)


@pytest.fixture
def mock_bond_repo() -> AsyncMock:
    return AsyncMock(spec=BondRepository)


@pytest.fixture
def mock_bondholder_repo() -> AsyncMock:
    return AsyncMock(spec=BondHolderRepository)


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_reference_rate_repo() -> AsyncMock:
    return AsyncMock(spec=ReferenceRateRepository)


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    return AsyncMock(spec=EventPublisher)


@pytest.fixture
def bh_del_service_mock():
    return AsyncMock(spec=BondHolderDeletionService)


@pytest.fixture
def mock_bh_income_calculator() -> Mock:
    return Mock(spec=BondHolderIncomeCalculator)
