from unittest.mock import Mock, AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio

from src.application.dto.user import UserDTO
from src.application.use_cases.user.user_auth import UserAuthUseCase
from src.domain.exceptions import InvalidTokenError, NotFoundError
from src.domain.entities.user import User as UserEntity


@pytest_asyncio.fixture
def use_case(mock_user_repo: Mock, mock_token_handler: Mock) -> UserAuthUseCase:
    return UserAuthUseCase(user_repo=mock_user_repo, token_handler=mock_token_handler)


@pytest_asyncio.fixture
def user() -> UserEntity:
    return UserEntity(
        id=uuid4(),
        email="test_email@email.com",
        hashed_password="hashed_password",
        name="test_user",
    )


@pytest_asyncio.fixture
def dto_from_user(user: UserEntity) -> UserDTO:
    return UserDTO(
        id=user.id,
        email=user.email,
        name=user.name,
    )


async def test_happy_path(
    use_case: UserAuthUseCase,
    user: UserEntity,
    dto_from_user: UserDTO,
) -> None:
    user_id_str = str(user.id)
    use_case.token_handler.read_token = AsyncMock(return_value=user_id_str)
    use_case.user_repo.get_one = AsyncMock(return_value=user)
    use_case.to_dto = AsyncMock(return_value=dto_from_user)

    token = "test_token"
    await use_case.execute(token=token)


async def test_invalid_token(use_case: UserAuthUseCase) -> None:
    use_case.token_handler.read_token = AsyncMock(return_value=None)

    token = "test_token"
    with pytest.raises(InvalidTokenError, match="Invalid token"):
        await use_case.execute(token=token)


async def test_user_not_found(
    use_case: UserAuthUseCase,
) -> None:
    user_id_str = str(uuid4())
    use_case.token_handler.read_token = AsyncMock(return_value=user_id_str)
    use_case.user_repo.get_one = AsyncMock(return_value=None)

    token = "test_token"
    with pytest.raises(NotFoundError, match="User not found"):
        await use_case.execute(token=token)
