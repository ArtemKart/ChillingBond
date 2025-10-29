from unittest.mock import Mock, AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio

from src.application.dto.user import UserDTO
from src.application.use_cases.user.user_auth import UserAuthUseCase
from src.domain.exceptions import InvalidTokenError, NotFoundError


@pytest_asyncio.fixture
def use_case(mock_user_repo: Mock, mock_token_handler: Mock) -> UserAuthUseCase:
    return UserAuthUseCase(user_repo=mock_user_repo, token_handler=mock_token_handler)


@pytest_asyncio.fixture
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
    use_case.user_repo.get_one = AsyncMock(return_value=user_entity_mock)
    use_case.to_dto = Mock(return_value=dto_from_user)

    token = "test_token"
    await use_case.execute(token=token)


async def test_invalid_token(use_case: UserAuthUseCase) -> None:
    use_case.token_handler.read_token = Mock(return_value=None)

    token = "test_token"
    with pytest.raises(InvalidTokenError, match="Token does not contain user information"):
        await use_case.execute(token=token)


async def test_user_not_found(
    use_case: UserAuthUseCase,
) -> None:
    user_id_str = str(uuid4())
    use_case.token_handler.read_token = Mock(return_value=user_id_str)
    use_case.user_repo.get_one = AsyncMock(return_value=None)

    token = "test_token"
    with pytest.raises(NotFoundError, match="User not found"):
        await use_case.execute(token=token)
