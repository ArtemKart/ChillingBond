import pytest
from starlette import status
from httpx import AsyncClient

from src.adapters.outbound.database.models import User as UserModel


@pytest.fixture
async def user_valid_json() -> dict[str, str]:
    return {
        "email": "test_email@email.com",
        "name": "test_name",
        "password": "plain_password123",
    }


async def test_create_user_success(
    client: AsyncClient,
    user_valid_json: dict[str, str],
) -> None:
    r = await client.post("api/users", json=user_valid_json)

    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["id"] is not None
    assert data["email"] == user_valid_json["email"]
    assert data["name"] == user_valid_json["name"]


async def test_create_user_user_already_exists(
    client: AsyncClient, t_user: UserModel, plain_pass: str
) -> None:

    r = await client.post(
        "api/users",
        json={"email": t_user.email, "name": t_user.name, "password": plain_pass},
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json()["detail"] == "User with given email address already exists"


async def test_create_user_email_normalization(
    client: AsyncClient,
) -> None:
    data_with_uppercase_email = {
        "email": "  TEST@EXAMPLE.COM  ",
        "password": "SecurePass123!",
        "name": "Test User",
    }
    r = await client.post("api/users", json=data_with_uppercase_email)

    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["email"] == "test@example.com"


async def test_create_user_invalid_email(
    client: AsyncClient, user_valid_json: dict[str, str]
) -> None:
    r = await client.post(
        "api/users", json={**user_valid_json, "email": "invalid-email"}
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "key",
    [
        pytest.param("email", id="missing email"),
        pytest.param("password", id="missing password"),
        pytest.param("name", id="missing name"),
    ],
)
async def test_missing_field(
    client: AsyncClient, user_valid_json: dict[str, str], key: str
) -> None:
    data_without_field = user_valid_json.pop(key, None)
    r = await client.post("api/users", json=data_without_field)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_create_user_empty_password(
    client: AsyncClient, user_valid_json: dict[str, str]
) -> None:
    invalid_data = {**user_valid_json, "password": ""}
    response = await client.post("api/users", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
