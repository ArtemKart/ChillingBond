from uuid import uuid4
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.outbound.database.models import User as UserModel
from src.application.dto.user import UserDTO


async def test_success(
    client: AsyncClient,
    t_current_user: UserDTO,
    t_session: AsyncSession,
) -> None:
    r = await client.delete(f"api/users/{t_current_user.id}")

    assert r.status_code == status.HTTP_204_NO_CONTENT
    assert r.content == b""

    u = await t_session.get(UserModel, t_current_user.id)
    assert not u


async def test_user_not_found(
    client: AsyncClient,
) -> None:
    r = await client.delete(f"api/users/{uuid4()}")

    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json()["detail"] == "User not found"


async def test_delete_user_invalid_uuid(client: AsyncClient) -> None:
    r = await client.delete("api/users/invalid-uuid")
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_user_does_not_exist(client: AsyncClient) -> None:
    r = await client.delete(f"api/users/{uuid4()}")
    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json()["detail"] == "User not found"
