import asyncio
from asyncio import current_task
from decimal import Decimal
from typing import Generator, AsyncGenerator
from unittest.mock import Mock
from uuid import uuid4, UUID
from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    async_scoped_session,
    AsyncEngine,
)
from testcontainers.postgres import PostgresContainer

from adapters.outbound.database import Base
from adapters.outbound.repositories.bond import SQLAlchemyBondRepository
from adapters.outbound.repositories.bondholder import SQLAlchemyBondHolderRepository
from adapters.outbound.repositories.user import SQLAlchemyUserRepository
from adapters.outbound.security.bcrypt_hasher import BcryptPasswordHasher
from application.events.event_publisher import EventPublisher
from src.adapters.config import set_config, reset_config
from src.adapters.inbound.api.dependencies import SessionDep, ConfigDep
from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.adapters.inbound.api.dependencies.event_publisher_deps import (
    get_event_publisher,
)
from src.adapters.inbound.api.dependencies.repo_deps import (
    user_repository,
    bond_repository,
    bondholder_repository,
)
from src.adapters.inbound.api.main import app
from src.adapters.outbound.database.models import User as UserModel
from src.adapters.outbound.database.models import Bond as BondModel
from src.adapters.outbound.database.models import BondHolder as BondHolderModel


hasher = BcryptPasswordHasher()


async def _write_to_db(session: AsyncSession, obj: Base) -> None:
    session.add(obj)
    await session.commit()
    await session.refresh(obj)


# ============================================================================
# EVENT LOOP CONFIGURATION
# ============================================================================


@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# DATABASE SETUP
# ============================================================================
@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    container = PostgresContainer("postgres:17.0").with_name(
        "test_db",
    )
    container.start()
    db_url = container.get_connection_url(driver="asyncpg")
    engine = create_async_engine(db_url, echo=True, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()
        container.stop()


@pytest_asyncio.fixture
async def t_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    scoped_session = async_scoped_session(
        async_session_maker,
        scopefunc=current_task,
    )
    async with scoped_session() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


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


@pytest.fixture
def plain_pass() -> str:
    return "plain_password"


@pytest_asyncio.fixture
async def t_current_user(t_session: AsyncSession, plain_pass: str) -> UUID:
    user = UserModel(
        id=uuid4(),
        email="test_email@mail.com",
        password=hasher.hash(plain_pass),
        name="Test User",
    )
    await _write_to_db(t_session, user)
    assert hasher.verify(plain_pass, user.password)
    return user.id


@pytest.fixture
async def t_user(t_session: AsyncSession, t_current_user: UUID) -> UserModel:
    return await t_session.get(UserModel, t_current_user)


@pytest_asyncio.fixture
async def t_bond(t_session: AsyncSession) -> BondModel:
    bond = BondModel(
        id=uuid4(),
        series="TEST001",
        nominal_value=Decimal(1000.00),
        maturity_period=12,
        initial_interest_rate=Decimal(5.0),
        first_interest_period=3,
        reference_rate_margin=Decimal(1.0),
    )
    await _write_to_db(t_session, bond)
    return bond


@pytest_asyncio.fixture
async def t_bondholder(
    t_session: AsyncSession,
    t_current_user: UUID,
    t_bond: BondModel,
) -> BondHolderModel:
    bondholder = BondHolderModel(
        id=uuid4(),
        user_id=t_current_user,
        bond_id=t_bond.id,
        quantity=10,
        purchase_date=date.today(),
        last_update=None,
    )
    await _write_to_db(t_session, bondholder)
    return bondholder


@pytest.fixture
def user_repo(t_session: AsyncSession) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session=t_session)


@pytest.fixture
def bond_repo(t_session: AsyncSession) -> SQLAlchemyBondRepository:
    return SQLAlchemyBondRepository(session=t_session)


@pytest.fixture
def bondholder_repo(t_session: AsyncSession) -> SQLAlchemyBondHolderRepository:
    return SQLAlchemyBondHolderRepository(session=t_session)


@pytest.fixture()
def event_publisher() -> EventPublisher:
    return EventPublisher()


@pytest_asyncio.fixture
async def client(
    t_session: AsyncSession,
    t_current_user: UUID,
    user_repo: SQLAlchemyUserRepository,
    bond_repo: SQLAlchemyBondRepository,
    bondholder_repo: SQLAlchemyBondHolderRepository,
    event_publisher: EventPublisher,
) -> AsyncClient:
    app.dependency_overrides[SessionDep] = lambda: t_session
    app.dependency_overrides[ConfigDep] = lambda: mock_config_globally
    app.dependency_overrides[current_user] = lambda: t_current_user
    app.dependency_overrides[user_repository] = lambda: user_repo
    app.dependency_overrides[bond_repository] = lambda: bond_repo
    app.dependency_overrides[bondholder_repository] = lambda: bondholder_repo
    app.dependency_overrides[get_event_publisher] = lambda: event_publisher

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
