from typing import Any
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest_asyncio
from starlette import status
from starlette.testclient import TestClient

from src.adapters.inbound.api.dependencies.user_use_cases_deps import (
    user_create_use_case,
)
from src.adapters.inbound.api.main import app
from src.application.dto.user import UserDTO
from src.application.use_cases.user.user_create import UserCreateUseCase
from src.adapters.outbound.database.models import User as UserModel


@pytest_asyncio.fixture
def user_create_valid_data(user_entity_mock: Mock) -> dict[str, Any]:
    return {
        "email": user_entity_mock.email,
        "name": user_entity_mock.name,
        "password": user_entity_mock.hashed_password,
    }


@pytest_asyncio.fixture
def use_case(mock_hasher: Mock, mock_user_repo: AsyncMock) -> UserCreateUseCase:
    return UserCreateUseCase(hasher=mock_hasher, user_repo=mock_user_repo)


@pytest_asyncio.fixture
def use_case_return_mock() -> Mock:
    mock = Mock(spec=UserDTO)
    mock.id = uuid4()
    mock.email = "test@email.com"
    mock.name = "test user"
    return mock


@pytest_asyncio.fixture
def user_model_mock() -> Mock:
    mock = Mock(spec=UserModel)
    mock.id = uuid4()
    mock.email = "test@email.com"
    mock.password = "test_password"
    mock.name = "test user"
    return mock


async def test_create_user_success(
    client: TestClient,
    user_create_valid_data: dict[str, Any],
    use_case: UserCreateUseCase,
    user_entity_mock: Mock,
) -> None:
    use_case.user_repo.get_by_email.return_value = None  # type: ignore[attr-defined]
    use_case.user_repo.write.return_value = user_entity_mock  # type: ignore[attr-defined]

    app.dependency_overrides[user_create_use_case] = lambda: use_case

    r = client.post("/users", json=user_create_valid_data)

    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["id"] == str(user_entity_mock.id)
    assert r.json()["email"] == user_entity_mock.email
    assert r.json()["name"] == user_entity_mock.name


async def test_create_user_user_already_exists(
    client: TestClient,
    user_create_valid_data: dict[str, Any],
    use_case: UserCreateUseCase,
    user_entity_mock: Mock,
) -> None:
    use_case.user_repo.get_by_email.return_value = user_entity_mock  # type: ignore[attr-defined]
    app.dependency_overrides[user_create_use_case] = lambda: use_case

    r = client.post("/users", json=user_create_valid_data)

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == "User already exists"


async def test_create_user_email_normalization(
    client: TestClient,
    use_case: UserCreateUseCase,
    user_entity_mock: Mock,
) -> None:
    data_with_uppercase_email = {
        "email": "  TEST@EXAMPLE.COM  ",
        "password": "SecurePass123!",
        "name": "Test User",
    }
    use_case.user_repo.get_by_email.return_value = None  # type: ignore[attr-defined]
    use_case.user_repo.write.return_value = user_entity_mock  # type: ignore[attr-defined]

    app.dependency_overrides[user_create_use_case] = lambda: use_case

    response = client.post("/users", json=data_with_uppercase_email)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["email"] == "test@example.com"


async def test_create_user_invalid_email(
    client: TestClient, user_create_valid_data: dict[str, str]
) -> None:
    invalid_data = {**user_create_valid_data, "email": "invalid-email"}
    response = client.post("/users", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_user_missing_email(
    client: TestClient, user_create_valid_data: dict[str, str]
) -> None:
    data_without_email = {
        "password": user_create_valid_data["password"],
        "name": user_create_valid_data["name"],
    }
    response = client.post("/users", json=data_without_email)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_user_missing_password(
    client: TestClient, user_create_valid_data: dict[str, str]
) -> None:
    data_without_password = {
        "email": user_create_valid_data["email"],
        "name": user_create_valid_data["name"],
    }
    response = client.post("/users", json=data_without_password)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_user_without_name(
    client: TestClient,
    use_case: UserCreateUseCase,
    user_entity_mock: Mock,
) -> None:
    data_without_name = {"email": "test@example.com", "password": "SecurePass123!"}
    user_entity_mock.name = None
    use_case.user_repo.get_by_email.return_value = None  # type: ignore[attr-defined]
    use_case.user_repo.write.return_value = user_entity_mock  # type: ignore[attr-defined]

    app.dependency_overrides[user_create_use_case] = lambda: use_case

    response = client.post("/users", json=data_without_name)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["name"] is None


async def test_create_user_empty_password(
    client: TestClient, user_create_valid_data: dict[str, str]
) -> None:
    invalid_data = {**user_create_valid_data, "password": ""}
    response = client.post("/users", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
