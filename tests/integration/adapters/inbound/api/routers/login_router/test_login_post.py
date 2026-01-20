from fastapi import status

from httpx import AsyncClient

from src.adapters.outbound.database.models import User as UserModel


async def test_login_success(
    client: AsyncClient,
    t_user: UserModel,
    plain_pass: str,
) -> None:
    r = await client.post(
        "api/login/token",
        data={"username": t_user.email, "password": plain_pass},
    )

    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["message"] == "Successfully authenticated"


async def test_login_user_not_found(client: AsyncClient) -> None:
    form_data = {"username": "nonexistent@example.com", "password": "any_password"}

    r = await client.post("api/login/token", data=form_data)

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == "Incorrect username or password"


async def test_login_incorrect_password(
    client: AsyncClient,
    t_user: UserModel,
) -> None:
    r = await client.post(
        "api/login/token", data={"username": t_user.email, "password": "wrong_password"}
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json()["detail"] == "Incorrect username or password"


async def test_login_missing_username(client: AsyncClient) -> None:
    r = await client.post("api/login/token", data={"password": "some_password"})
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_login_missing_password(client: AsyncClient) -> None:
    r = await client.post("api/login/token", data={"username": "test@example.com"})
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_login_empty_credentials(client: AsyncClient) -> None:
    r = await client.post("api/login/token", data={})
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_login_response_structure(
    client: AsyncClient,
    t_user: UserModel,
    plain_pass: str,
) -> None:
    r = await client.post(
        "api/login/token", data={"username": t_user.email, "password": plain_pass}
    )

    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert "message" in data
    assert data["message"] == "Successfully authenticated"
    assert len(data) == 1
    assert isinstance(data["message"], str)
