from uuid import uuid4

import pytest
from fastapi import HTTPException
from jwt import PyJWTError
from starlette import status

from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.application.dto.user import UserDTO
from src.application.use_cases.user.auth import UserAuthUseCase
from src.domain.ports.repositories.user import UserRepository
from src.domain.ports.services.token_handler import TokenHandler


@pytest.fixture
def use_case(
    mock_user_repo: UserRepository, mock_token_handler: TokenHandler
) -> UserAuthUseCase:
    return UserAuthUseCase(user_repo=mock_user_repo, token_handler=mock_token_handler)


@pytest.fixture
def mock_user_dto() -> UserDTO:
    return UserDTO(
        id=uuid4(),
        email="test_email@email.com",
        name="Test User",
    )


async def test_current_user_success(
    use_case: UserAuthUseCase,
    mock_user_dto: UserDTO,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    access_token = "valid_token"

    async def mock_execute(token: str) -> UserDTO:
        return mock_user_dto

    monkeypatch.setattr(use_case, "execute", mock_execute)
    result = await current_user(use_case=use_case, access_token=access_token)
    assert result == mock_user_dto


async def test_current_user_no_token(
    use_case: UserAuthUseCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(HTTPException, match="Not authenticated") as exc_info:
        await current_user(
            use_case=use_case,
            access_token=None,
        )
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_current_user_raises_unauthorized_on_exceptions(
    use_case: UserAuthUseCase,
    monkeypatch: pytest.MonkeyPatch,
):
    access_token = "invalid_token"

    async def mock_execute(token: str) -> UserDTO:
        raise PyJWTError("Invalid token")

    monkeypatch.setattr(use_case, "execute", mock_execute)

    with pytest.raises(HTTPException) as exc_info:
        await current_user(
            use_case=use_case,
            access_token=access_token,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Not authenticated"
