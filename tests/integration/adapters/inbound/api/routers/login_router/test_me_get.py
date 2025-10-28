from uuid import UUID
from fastapi import status
from starlette.testclient import TestClient


def test_me_success(client: TestClient, mock_current_user: UUID) -> None:
    response = client.get("/login/me")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["id"] == str(mock_current_user)


def test_me_returns_correct_uuid_format(
    client: TestClient, mock_current_user: UUID
) -> None:
    response = client.get("/login/me")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert UUID(data["id"])


def test_me_without_authentication(client: TestClient) -> None:
    from src.adapters.inbound.api.main import app
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user

    if current_user in app.dependency_overrides:
        del app.dependency_overrides[current_user]

    response = client.get("/login/me")

    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ]


def test_me_response_structure(client: TestClient, mock_current_user: UUID) -> None:
    response = client.get("/login/me")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 1
    assert "id" in data
    assert isinstance(data["id"], str)
