from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from fastapi import status
from starlette.testclient import TestClient


def test_delete_user_success(
    client: TestClient, mock_user_repo: AsyncMock, user_entity_mock: Mock
):
    user_id = user_entity_mock.id
    mock_user_repo.get_one.return_value = user_entity_mock
    mock_user_repo.delete.return_value = None

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    mock_user_repo.get_one.assert_called_once_with(user_id)
    mock_user_repo.delete.assert_called_once_with(user_id)


def test_delete_user_not_found(client: TestClient, mock_user_repo: AsyncMock):
    user_id = uuid4()
    mock_user_repo.get_one.return_value = None

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"
    mock_user_repo.get_one.assert_called_once_with(user_id)
    mock_user_repo.delete.assert_not_called()


def test_delete_user_invalid_uuid(client: TestClient, mock_user_repo: AsyncMock):
    response = client.delete("/users/invalid-uuid")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_user_repo.get_one.assert_not_called()
    mock_user_repo.delete.assert_not_called()


def test_delete_user_calls_in_correct_order(
    client: TestClient, mock_user_repo: AsyncMock, user_entity_mock: Mock
):
    user_id = user_entity_mock.id
    mock_user_repo.get_one.return_value = user_entity_mock
    mock_user_repo.delete.return_value = None

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert mock_user_repo.get_one.call_count == 1
    assert mock_user_repo.delete.call_count == 1

    calls = [call[0] for call in mock_user_repo.method_calls]
    assert calls.index("get_one") < calls.index("delete")
