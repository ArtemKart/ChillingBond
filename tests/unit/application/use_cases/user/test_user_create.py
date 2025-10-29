import pytest
from unittest.mock import AsyncMock, Mock, patch

import pytest_asyncio

from src.application.dto.user import UserCreateDTO, UserDTO
from src.application.use_cases.user.user_create import UserCreateUseCase
from src.domain.exceptions import ConflictError
from src.domain.entities.user import User as UserEntity


@pytest_asyncio.fixture
def use_case(mock_user_repo: AsyncMock, mock_hasher: AsyncMock) -> UserCreateUseCase:
    return UserCreateUseCase(mock_user_repo, mock_hasher)


@pytest_asyncio.fixture
def sample_user_create_dto() -> Mock:
    dto = Mock(spec=UserCreateDTO)
    dto.email = "test@example.com"
    dto.password = "SecurePassword123!"
    dto.name = "Test User"
    return dto


@pytest_asyncio.fixture
def sample_user_dto() -> Mock:
    dto = Mock(spec=UserDTO)
    dto.id = "user-123"
    dto.email = "test@example.com"
    dto.name = "Test User"
    return dto


async def test_success_creates_new_user(
    use_case: UserCreateUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: AsyncMock,
    sample_user_create_dto: Mock,
    user_entity_mock: Mock,
    sample_user_dto: Mock,
) -> None:
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.write.return_value = user_entity_mock
    use_case.to_dto = Mock(return_value=sample_user_dto)

    with patch(
        "src.application.use_cases.user.user_create.UserEntity.create", new=Mock()
    ) as mock_create:
        mock_create.return_value = user_entity_mock
        result = await use_case.execute(sample_user_create_dto)

    assert result == sample_user_dto
    mock_user_repo.get_by_email.assert_called_once_with(sample_user_create_dto.email)
    mock_create.assert_called_once_with(
        email=sample_user_create_dto.email,
        plain_password=sample_user_create_dto.password,
        hasher=mock_hasher,
        name=sample_user_create_dto.name,
    )
    mock_user_repo.write.assert_called_once_with(user_entity_mock)
    use_case.to_dto.assert_called_once_with(user_entity_mock)


async def test_user_already_exists_raises_validation_error(
    use_case: UserCreateUseCase,
    mock_user_repo: AsyncMock,
    sample_user_create_dto: Mock,
    user_entity_mock: Mock,
) -> None:
    mock_user_repo.get_by_email.return_value = user_entity_mock

    with pytest.raises(ConflictError, match="User already exists"):
        await use_case.execute(sample_user_create_dto)

    mock_user_repo.get_by_email.assert_called_once_with(sample_user_create_dto.email)
    mock_user_repo.write.assert_not_called()


async def test_with_different_user_data(
    use_case: UserCreateUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: Mock,
    user_entity_mock: Mock,
    sample_user_dto: Mock,
) -> None:
    user_dto = Mock(spec=UserCreateDTO)
    user_dto.email = "another@example.com"
    user_dto.password = "AnotherPassword456!"
    user_dto.name = "Another User"

    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.write.return_value = user_entity_mock
    use_case.to_dto = Mock(return_value=sample_user_dto)

    with patch(
        "src.application.use_cases.user.user_create.UserEntity.create", new=AsyncMock()
    ) as mock_create:
        mock_create.return_value = user_entity_mock
        result = await use_case.execute(user_dto)

    assert result == sample_user_dto
    mock_user_repo.get_by_email.assert_called_once_with("another@example.com")
    mock_create.assert_called_once_with(
        email="another@example.com",
        plain_password="AnotherPassword456!",
        hasher=mock_hasher,
        name="Another User",
    )


async def test_hasher_is_passed_correctly(
    use_case: UserCreateUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: AsyncMock,
    sample_user_create_dto: Mock,
    user_entity_mock: Mock,
) -> None:
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.write.return_value = user_entity_mock
    use_case.to_dto = AsyncMock(return_value=Mock(spec=UserDTO))

    with patch(
        "src.application.use_cases.user.user_create.UserEntity.create", new=AsyncMock()
    ) as mock_create:
        mock_create.return_value = user_entity_mock
        await use_case.execute(sample_user_create_dto)

    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["hasher"] == mock_hasher


async def test_returns_dto_from_written_entity(
    use_case: UserCreateUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: Mock,
    sample_user_create_dto: Mock,
) -> None:
    created_entity = Mock(spec=UserEntity, id="created-123")
    written_entity = Mock(spec=UserEntity, id="written-456")
    expected_dto = Mock(spec=UserDTO, id="written-456")

    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.write.return_value = written_entity
    use_case.to_dto = Mock(return_value=expected_dto)

    with patch(
        "src.application.use_cases.user.user_create.UserEntity.create", new=AsyncMock()
    ) as mock_create:
        mock_create.return_value = created_entity
        result = await use_case.execute(sample_user_create_dto)

    assert result == expected_dto
    use_case.to_dto.assert_called_once_with(written_entity)


async def test_with_minimal_user_data(
    use_case: UserCreateUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: Mock,
    user_entity_mock: Mock,
    sample_user_dto: Mock,
) -> None:
    minimal_dto = Mock(spec=UserCreateDTO)
    minimal_dto.email = "minimal@example.com"
    minimal_dto.password = "Pass123!"
    minimal_dto.name = None

    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.write.return_value = user_entity_mock
    use_case.to_dto = Mock(return_value=sample_user_dto)

    with patch(
        "src.application.use_cases.user.user_create.UserEntity.create", new=AsyncMock()
    ) as mock_create:
        mock_create.return_value = user_entity_mock
        result = await use_case.execute(minimal_dto)

    assert result == sample_user_dto
    mock_create.assert_called_once_with(
        email="minimal@example.com",
        plain_password="Pass123!",
        hasher=mock_hasher,
        name=None,
    )


async def test_handles_email_case_sensitivity(
    use_case: UserCreateUseCase,
    mock_user_repo: AsyncMock,
    sample_user_create_dto: Mock,
    user_entity_mock: Mock,
) -> None:
    sample_user_create_dto.email = "TEST@EXAMPLE.COM"
    mock_user_repo.get_by_email.return_value = user_entity_mock

    with pytest.raises(ConflictError, match="User already exists"):
        await use_case.execute(sample_user_create_dto)

    mock_user_repo.get_by_email.assert_called_once_with("TEST@EXAMPLE.COM")
