from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.adapters.outbound.database.models import User as UserModel
from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.adapters.outbound.repositories.user import SQLAlchemyUserRepository
from src.domain.entities.user import User as UserEntity


@pytest.fixture
def user_model(user_entity_mock: Mock) -> UserModel:
    return UserModel(
        id=user_entity_mock.id,
        email=user_entity_mock.email,
        password=user_entity_mock.hashed_password,
        name=user_entity_mock.name,
    )


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
def repository(mock_session: AsyncMock) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(mock_session)


async def test_get_user_if_exists_user_exists(
    repository: SQLAlchemyUserRepository,
    mock_session: AsyncMock,
    user_model: UserModel,
    user_entity_mock: Mock,
) -> None:
    mock_session.get.return_value = user_model

    result = await repository.get_user_if_exists(user_model.id)

    mock_session.get.assert_called_once_with(UserModel, user_model.id)
    assert result is not None
    assert result.id == user_model.id
    assert result.email == user_model.email
    assert result.name == user_model.name
    assert result.hashed_password == user_entity_mock.hashed_password


async def test_get_user_if_exists_user_not_exists(
    repository: SQLAlchemyUserRepository,
    mock_session: AsyncMock,
) -> None:
    user_id = uuid4()
    mock_session.get.return_value = None

    result = await repository.get_user_if_exists(user_id)

    mock_session.get.assert_called_once_with(UserModel, user_id)
    assert result is None


async def test_get_user_if_exists_by_email_user_exists(
    repository: SQLAlchemyUserRepository,
    mock_session: AsyncMock,
    user_model: UserModel,
    user_entity_mock: Mock,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_model
    mock_session.execute.return_value = mock_result

    result = await repository.get_user_if_exists_by_email(user_model.email)

    mock_result.scalar_one_or_none.assert_called_once()
    assert result is not None
    assert result.id == user_model.id
    assert result.email == user_model.email
    assert result.name == user_model.name
    assert result.hashed_password == user_entity_mock.hashed_password


async def test_get_user_if_exists_by_email_user_not_exists(
    repository: SQLAlchemyUserRepository,
    mock_session: AsyncMock,
    user_model: UserModel,
    user_entity_mock: Mock,
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repository.get_user_if_exists_by_email(user_model.email)

    mock_result.scalar_one_or_none.assert_called_once()
    assert result is None


async def test_get_one_success(
    repository: SQLAlchemyUserRepository,
    user_entity_mock: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def mock_get_user_if_exists(user_id: UUID) -> UserEntity | None:
        return user_entity_mock

    monkeypatch.setattr(repository, "get_user_if_exists", mock_get_user_if_exists)

    result = await repository.get_one(user_entity_mock.id)

    assert result is not None
    assert isinstance(result, UserEntity)
    assert result.id == user_entity_mock.id
    assert result.email == user_entity_mock.email
    assert result.name == user_entity_mock.name
    assert result.hashed_password == user_entity_mock.hashed_password


async def test_get_one_not_found(
    repository: SQLAlchemyUserRepository,
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def mock_get_user_if_exists(user_id: UUID) -> UserEntity | None:
        return None

    monkeypatch.setattr(repository, "get_user_if_exists", mock_get_user_if_exists)

    user_id = uuid4()
    mock_session.get.return_value = None
    with pytest.raises(SQLAlchemyRepositoryError, match="User not found"):
        await repository.get_one(user_id)


async def test_get_by_email_success(
    repository: SQLAlchemyUserRepository,
    user_entity_mock: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def get_user_if_exists_by_email(email: str) -> UserEntity | None:
        return user_entity_mock

    monkeypatch.setattr(
        repository, "get_user_if_exists_by_email", get_user_if_exists_by_email
    )

    result = await repository.get_by_email(user_entity_mock.email)

    assert result is not None
    assert isinstance(result, UserEntity)
    assert result.id == user_entity_mock.id
    assert result.email == user_entity_mock.email
    assert result.name == user_entity_mock.name
    assert result.hashed_password == user_entity_mock.hashed_password


async def test_get_by_email_not_found(
    repository: SQLAlchemyUserRepository,
    monkeypatch: pytest.MonkeyPatch,
    user_entity_mock: Mock,
) -> None:
    async def get_user_if_exists_by_email(email: str) -> UserEntity | None:
        return None

    monkeypatch.setattr(
        repository, "get_user_if_exists_by_email", get_user_if_exists_by_email
    )

    with pytest.raises(SQLAlchemyRepositoryError, match="User not found"):
        await repository.get_by_email(user_entity_mock.email)


async def test_write_success(
    repository: SQLAlchemyUserRepository,
    mock_session: AsyncMock,
    user_entity_mock: Mock,
) -> None:
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    result = await repository.write(user_entity_mock)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.id == user_entity_mock.id
    assert result.email == user_entity_mock.email


async def test_write_integrity_error_duplicate_email(
    repository: SQLAlchemyUserRepository,
    mock_session: AsyncMock,
    user_entity_mock: Mock,
) -> None:
    mock_session.commit.side_effect = IntegrityError("", "", "")

    with pytest.raises(
        SQLAlchemyRepositoryError, match="User already exists or constraint violated"
    ):
        await repository.write(user_entity_mock)
    mock_session.rollback.assert_called_once()


async def test_write_sqlalchemy_error(
    repository: SQLAlchemyUserRepository,
    mock_session: AsyncMock,
    user_entity_mock: Mock,
) -> None:
    mock_session.commit.side_effect = SQLAlchemyError("Database connection lost")

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to save user"):
        await repository.write(user_entity_mock)
    mock_session.rollback.assert_called_once()


async def test_delete_success(
    repository: SQLAlchemyUserRepository, mock_session: AsyncMock, user_model: UserModel
) -> None:
    user_id = uuid4()
    mock_session.get.return_value = user_model
    mock_session.delete.return_value = None
    mock_session.commit.return_value = None

    await repository.delete(user_id)

    mock_session.get.assert_called_once_with(UserModel, user_id)
    mock_session.delete.assert_called_once_with(user_model)
    mock_session.commit.assert_called_once()


async def test_delete_not_found(
    repository: SQLAlchemyUserRepository, mock_session: AsyncMock
) -> None:
    user_id = uuid4()
    mock_session.get.return_value = None

    await repository.delete(user_id)

    mock_session.get.assert_called_once_with(UserModel, user_id)
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


async def test_delete_sqlalchemy_error(
    repository: SQLAlchemyUserRepository, mock_session: AsyncMock
) -> None:
    user_id = uuid4()
    mock_session.get.side_effect = SQLAlchemyError("Foreign key constraint")

    with pytest.raises(SQLAlchemyRepositoryError, match="Failed to delete user"):
        await repository.delete(user_id)
    mock_session.rollback.assert_called_once()


def test_to_entity_conversion(
    repository: SQLAlchemyUserRepository, user_model: UserModel
) -> None:
    result = repository._to_entity(user_model)

    assert isinstance(result, UserEntity)
    assert result.id == user_model.id
    assert result.email == user_model.email
    assert result.hashed_password == user_model.password
    assert result.name == user_model.name


def test_to_model_conversion(
    repository: SQLAlchemyUserRepository, user_entity_mock: Mock
) -> None:
    result = repository._to_model(user_entity_mock)

    assert isinstance(result, UserModel)
    assert result.id == user_entity_mock.id
    assert result.email == user_entity_mock.email
    assert result.password == user_entity_mock.hashed_password
    assert result.name == user_entity_mock.name


def test_update_model(
    repository: SQLAlchemyUserRepository,
    user_model: UserModel,
    mock_hasher: Mock,
) -> None:
    new_entity = UserEntity.create(
        email="newemail@example.com",
        plain_password="new_plain_password1",
        hasher=mock_hasher,
        name="New Name",
    )

    repository._update_model(user_model, new_entity)

    assert str(user_model.email) == str(new_entity.email)
    assert user_model.password == new_entity.hashed_password
    assert user_model.name == new_entity.name


async def test_get_by_email_case_sensitivity(
    repository: SQLAlchemyUserRepository, mock_session: AsyncMock, user_model: UserModel
) -> None:
    user_model.email = "Test@Example.COM"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_model
    mock_session.execute.return_value = mock_result

    result = await repository.get_by_email("test@example.com")

    assert result is not None
    assert result.email == "Test@Example.COM"
