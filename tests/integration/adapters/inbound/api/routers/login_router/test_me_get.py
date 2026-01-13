from uuid import UUID

from fastapi import status
from httpx import AsyncClient

from src.application.dto.user import UserDTO


async def test_me_success(client: AsyncClient, t_current_user: UserDTO) -> None:
    r = await client.get("api/login/me")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert "id" in data
    assert data["id"] == str(t_current_user.id)


async def test_me_returns_correct_uuid_format(client: AsyncClient) -> None:
    r = await client.get("api/login/me")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert UUID(data["id"])


async def test_me_without_authentication(client: AsyncClient) -> None:
    from src.adapters.inbound.api.dependencies.current_user_deps import current_user
    from src.adapters.inbound.api.main import app

    if current_user in app.dependency_overrides:
        del app.dependency_overrides[current_user]

    r = await client.get("api/login/me")

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


async def test_me_response_structure(client: AsyncClient) -> None:
    r = await client.get("api/login/me")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()

    assert len(data) == 1
    assert "id" in data
    assert isinstance(data["id"], str)
