from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from fastapi import status
from starlette.testclient import TestClient


def test_get_user_success(
    client: TestClient, mock_user_repo: AsyncMock, user_entity_mock: Mock
) -> None:
    user_id = user_entity_mock.id
    mock_user_repo.get_one.return_value = user_entity_mock

    response = client.get(f"/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(user_entity_mock.id)
    assert data["email"] == user_entity_mock.email
    assert data["name"] == user_entity_mock.name

    mock_user_repo.get_one.assert_called_once_with(user_id)


def test_get_user_not_found(client: TestClient, mock_user_repo: AsyncMock) -> None:
    user_id = uuid4()
    mock_user_repo.get_one.return_value = None

    response = client.get(f"/users/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"

    mock_user_repo.get_one.assert_called_once_with(user_id)


def test_get_user_invalid_uuid(client: TestClient, mock_user_repo: AsyncMock) -> None:

    response = client.get("/users/invalid-uuid")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    mock_user_repo.get_one.assert_not_called()


def test_get_user_with_none_name(
    client: TestClient, mock_user_repo: AsyncMock, user_entity_mock: Mock
) -> None:
    user_entity_mock.name = None
    mock_user_repo.get_one.return_value = user_entity_mock

    response = client.get(f"/users/{user_entity_mock.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(user_entity_mock.id)
    assert data["email"] == user_entity_mock.email
    assert data["name"] is None


def test_get_user_email_normalized(
    client: TestClient, mock_user_repo: AsyncMock, user_entity_mock: Mock
) -> None:
    user_entity_mock.email = "Test@Example.COM"
    mock_user_repo.get_one.return_value = user_entity_mock

    response = client.get(f"/users/{user_entity_mock.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == data["email"].strip().lower()
