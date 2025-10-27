import pytest
from unittest.mock import AsyncMock, Mock

import pytest_asyncio

from src.application.dto.token import TokenDTO
from src.application.use_cases.user.user_login import UserLoginUseCase
from src.domain.exceptions import ValidationError
from src.domain.ports.services.password_hasher import PasswordHasher


@pytest_asyncio.fixture
def use_case(
    mock_user_repo: AsyncMock, mock_hasher: AsyncMock, mock_token_handler: AsyncMock
) -> UserLoginUseCase:
    return UserLoginUseCase(mock_user_repo, mock_hasher, mock_token_handler)


@pytest_asyncio.fixture
def sample_form_data() -> Mock:
    form_data = Mock()
    form_data.username = "test@example.com"
    form_data.password = "SecurePassword123!"
    return form_data


@pytest_asyncio.fixture
def sample_token() -> Mock:
    token = Mock()
    token.token = "test_jwt_token"
    token.type = "Bearer"
    return token


async def test_success_returns_token(
    use_case: UserLoginUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: AsyncMock,
    mock_token_handler: AsyncMock,
    sample_form_data: Mock,
    user_entity_mock: Mock,
    sample_token: Mock,
) -> None:
    mock_user_repo.get_by_email.return_value = user_entity_mock
    user_entity_mock.verify_password.return_value = True
    mock_token_handler.create_token.return_value = sample_token

    result = await use_case.execute(sample_form_data)

    assert isinstance(result, TokenDTO)
    assert result.token == sample_token.token
    assert result.type == sample_token.type
    mock_user_repo.get_by_email.assert_called_once_with(sample_form_data.username)
    user_entity_mock.verify_password.assert_called_once_with(
        hasher=mock_hasher,
        plain_password=sample_form_data.password,
    )
    mock_token_handler.create_token.assert_called_once_with(subject=str(user_entity_mock.id))


async def test_user_not_found_raises_validation_error(
    use_case: UserLoginUseCase, mock_user_repo: AsyncMock, sample_form_data: Mock
) -> None:
    mock_user_repo.get_by_email.return_value = None

    with pytest.raises(ValidationError, match="Incorrect username or password"):
        await use_case.execute(sample_form_data)

    mock_user_repo.get_by_email.assert_called_once_with(sample_form_data.username)


async def test_incorrect_password_raises_validation_error(
    use_case: UserLoginUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: Mock,
    sample_form_data: Mock,
    user_entity_mock: Mock,
) -> None:
    mock_user_repo.get_by_email.return_value = user_entity_mock
    user_entity_mock.verify_password.return_value = False

    with pytest.raises(ValidationError, match="Incorrect username or password"):
        await use_case.execute(sample_form_data)

    mock_user_repo.get_by_email.assert_called_once_with(sample_form_data.username)
    user_entity_mock.verify_password.assert_called_once_with(
        hasher=mock_hasher,
        plain_password=sample_form_data.password,
    )


async def test_with_different_credentials(
    use_case: UserLoginUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: AsyncMock,
    mock_token_handler: AsyncMock,
    user_entity_mock: Mock,
    sample_token: Mock,
) -> None:
    form_data = Mock()
    form_data.username = "another@example.com"
    form_data.password = "AnotherPassword456!"

    mock_user_repo.get_by_email.return_value = user_entity_mock
    user_entity_mock.verify_password.return_value = True
    mock_token_handler.create_token.return_value = sample_token

    result = await use_case.execute(form_data)

    assert result.token == sample_token.token
    mock_user_repo.get_by_email.assert_called_once_with(form_data.username)
    user_entity_mock.verify_password.assert_called_once_with(
        hasher=mock_hasher, plain_password=form_data.password
    )


async def test_converts_user_id_to_string(
    use_case: UserLoginUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: AsyncMock,
    mock_token_handler: AsyncMock,
    sample_form_data: Mock,
    sample_token: Mock,
) -> None:
    user = Mock()
    user.id = 12345
    user.verify_password = AsyncMock(return_value=True)

    mock_user_repo.get_by_email.return_value = user
    mock_token_handler.create_token.return_value = sample_token

    await use_case.execute(sample_form_data)

    mock_token_handler.create_token.assert_called_once_with(subject="12345")


async def test_handles_uuid_user_id(
    use_case: UserLoginUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: AsyncMock,
    mock_token_handler: AsyncMock,
    sample_form_data: Mock,
    sample_token: Mock,
) -> None:
    from uuid import uuid4

    user_id = uuid4()

    user = Mock()
    user.id = user_id
    user.verify_password = AsyncMock(return_value=True)

    mock_user_repo.get_by_email.return_value = user
    mock_token_handler.create_token.return_value = sample_token

    await use_case.execute(sample_form_data)

    mock_token_handler.create_token.assert_called_once_with(subject=str(user_id))


async def test_does_not_create_token_on_failed_auth(
    use_case: UserLoginUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: AsyncMock,
    mock_token_handler: AsyncMock,
    sample_form_data: Mock,
    user_entity_mock: Mock,
) -> None:
    mock_user_repo.get_by_email.return_value = user_entity_mock
    user_entity_mock.verify_password.return_value = False

    with pytest.raises(ValidationError, match="Incorrect username or password"):
        await use_case.execute(sample_form_data)

    mock_token_handler.create_token.assert_not_called()


async def test_pass_hasher_to_verify_password(
    use_case: UserLoginUseCase,
    mock_user_repo: AsyncMock,
    mock_hasher: AsyncMock,
    mock_token_handler: AsyncMock,
    sample_form_data: Mock,
    user_entity_mock: Mock,
    sample_token: Mock,
) -> None:
    custom_hasher = AsyncMock(spec=PasswordHasher)
    custom_use_case = UserLoginUseCase(
        mock_user_repo, custom_hasher, mock_token_handler
    )

    mock_user_repo.get_by_email.return_value = user_entity_mock
    user_entity_mock.verify_password.return_value = True
    mock_token_handler.create_token.return_value = sample_token

    await custom_use_case.execute(sample_form_data)

    user_entity_mock.verify_password.assert_called_once_with(
        hasher=custom_hasher, plain_password=sample_form_data.password
    )
