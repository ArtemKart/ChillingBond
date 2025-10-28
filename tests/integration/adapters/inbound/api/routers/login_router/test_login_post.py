from fastapi import status
from unittest.mock import Mock


import pytest
from unittest.mock import AsyncMock

from starlette.testclient import TestClient

from src.adapters.inbound.api.main import app
from src.application.use_cases.user.user_login import UserLoginUseCase


@pytest.fixture
def mock_user_login_use_case(
    mock_user_repo: AsyncMock, mock_hasher: Mock, mock_token_handler: Mock
) -> UserLoginUseCase:
    return UserLoginUseCase(
        user_repo=mock_user_repo,
        hasher=mock_hasher,
        token_handler=mock_token_handler,
    )


@pytest.fixture(autouse=True)
def setup_login_use_case_override(mock_user_login_use_case: UserLoginUseCase) -> None:
    from src.adapters.inbound.api.dependencies.user_use_cases_deps import (
        user_login_use_case,
    )
    app.dependency_overrides[user_login_use_case] = lambda: mock_user_login_use_case


def test_login_success(
    client: TestClient,
    mock_user_repo: AsyncMock,
    user_entity_mock: Mock,
    mock_hasher: Mock,
    mock_token_handler: Mock,
) -> None:
    mock_user_repo.get_by_email.return_value = user_entity_mock
    user_entity_mock.verify_password.return_value = True

    mock_token = Mock()
    mock_token.token = "test_jwt_token"
    mock_token.type = "bearer"
    mock_token_handler.create_token.return_value = mock_token

    form_data = {"username": "test@example.com", "password": "correct_password"}

    response = client.post("/login/token", data=form_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["token"] == "test_jwt_token"
    assert data["type"] == "bearer"

    mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    user_entity_mock.verify_password.assert_called_once_with(
        hasher=mock_hasher, plain_password="correct_password"
    )
    mock_token_handler.create_token.assert_called_once_with(
        subject=str(user_entity_mock.id)
    )


def test_login_user_not_found(client: TestClient, mock_user_repo: AsyncMock) -> None:
    mock_user_repo.get_by_email.return_value = None

    form_data = {"username": "nonexistent@example.com", "password": "any_password"}

    response = client.post("/login/token", data=form_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"

    mock_user_repo.get_by_email.assert_called_once_with("nonexistent@example.com")


def test_login_incorrect_password(
    client: TestClient, mock_user_repo: AsyncMock, user_entity_mock: Mock, mock_hasher: Mock
) -> None:
    mock_user_repo.get_by_email.return_value = user_entity_mock
    user_entity_mock.verify_password.return_value = False

    form_data = {"username": "test@example.com", "password": "wrong_password"}

    response = client.post("/login/token", data=form_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"

    mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    user_entity_mock.verify_password.assert_called_once_with(
        hasher=mock_hasher, plain_password="wrong_password"
    )


def test_login_missing_username(client: TestClient) -> None:
    form_data = {"password": "some_password"}

    response = client.post("/login/token", data=form_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_missing_password(client: TestClient) -> None:
    form_data = {"username": "test@example.com"}
    response = client.post("/login/token", data=form_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_empty_credentials(client: TestClient) -> None:
    response = client.post("/login/token", data={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_response_structure(
    client: TestClient,
    mock_user_repo: AsyncMock,
    user_entity_mock: Mock,
    mock_hasher: Mock,
    mock_token_handler: Mock,
) -> None:
    mock_user_repo.get_by_email.return_value = user_entity_mock
    user_entity_mock.verify_password.return_value = True

    mock_token = Mock()
    mock_token.token = "jwt_token_123"
    mock_token.type = "bearer"
    mock_token_handler.create_token.return_value = mock_token

    form_data = {"username": "test@example.com", "password": "password123"}

    response = client.post("/login/token", data=form_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "token" in data
    assert "type" in data
    assert len(data) == 2
    assert isinstance(data["token"], str)
    assert isinstance(data["type"], str)
