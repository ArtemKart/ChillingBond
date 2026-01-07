from uuid import uuid4

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.outbound.database.models import User as UserModel
from src.adapters.outbound.security.bcrypt_hasher import BcryptPasswordHasher


async def test_success(client: AsyncClient, t_user: UserModel) -> None:

    r = await client.get(f"api/users/{t_user.id}")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == str(t_user.id)
    assert data["email"] == t_user.email
    assert data["name"] == t_user.name


async def test_user_not_found(client: AsyncClient) -> None:
    r = await client.get(f"api/users/{uuid4()}")

    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json()["detail"] == "User not found"


async def test_invalid_uuid(
    client: AsyncClient,
) -> None:
    r = await client.get("api/users/invalid-uuid")
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_with_none_name(
    client: AsyncClient, t_session: AsyncSession, plain_pass: str
) -> None:
    u = UserModel(
        id=uuid4(),
        email="test@email.com",
        password=BcryptPasswordHasher().hash(plain_pass),
        name=None,
    )
    t_session.add(u)
    await t_session.commit()
    await t_session.refresh(u)

    r = await client.get(f"api/users/{u.id}")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == str(u.id)
    assert data["email"] == u.email
    assert data["name"] is None


async def test_email_normalized(
    client: AsyncClient, t_session: AsyncSession, plain_pass: str
) -> None:
    u = UserModel(
        id=uuid4(),
        email="TeST@eMaIl.CoM",
        password=BcryptPasswordHasher().hash(plain_pass),
        name=None,
    )
    t_session.add(u)
    await t_session.commit()
    await t_session.refresh(u)

    r = await client.get(f"api/users/{u.id}")

    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["email"] == data["email"].strip().lower()
