from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from jwt.exceptions import PyJWTError
import pytest

from src.application.dto.user import UserDTO
from src.application.use_cases.user.auth import UserAuthUseCase
from src.domain.exceptions import AuthenticationError, InvalidTokenError


@pytest.fixture
def use_case(mock_user_repo: Mock, mock_token_handler: Mock) -> UserAuthUseCase:
    return UserAuthUseCase(user_repo=mock_user_repo, token_handler=mock_token_handler)


@pytest.fixture
def dto_from_user(user_entity_mock: Mock) -> UserDTO:
    return UserDTO(
        id=user_entity_mock.id,
        email=user_entity_mock.email,
        name=user_entity_mock.name,
    )


async def test_happy_path(
    use_case: UserAuthUseCase,
    user_entity_mock: Mock,
    dto_from_user: UserDTO,
) -> None:
    user_id_str = str(user_entity_mock.id)
    use_case.token_handler.read_token = Mock(return_value=user_id_str)
    use_case.user_repo.get_user = AsyncMock(return_value=user_entity_mock)
    use_case.to_dto = Mock(return_value=dto_from_user)

    token = "test_token"
    await use_case.execute(token=token)


async def test_empty_token(use_case: UserAuthUseCase) -> None:
    use_case.token_handler.read_token = Mock(return_value=None)

    token = "test_token"
    with pytest.raises(
        InvalidTokenError, match="Token does not contain user information"
    ):
        await use_case.execute(token=token)


async def test_user_not_found(
    use_case: UserAuthUseCase,
) -> None:
    user_id_str = str(uuid4())
    use_case.token_handler.read_token = Mock(return_value=user_id_str)
    use_case.user_repo.get_user = AsyncMock(return_value=None)

    token = "test_token"
    with pytest.raises(AuthenticationError, match="User not found"):
        await use_case.execute(token=token)


async def test_invalid_token(use_case: UserAuthUseCase) -> None:
    use_case.token_handler.read_token = Mock(side_effect=PyJWTError())

    token = "test_token"
    with pytest.raises(InvalidTokenError, match="Invalid token"):
        await use_case.execute(token=token)
