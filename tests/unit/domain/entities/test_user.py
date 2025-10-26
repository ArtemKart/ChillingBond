from unittest.mock import Mock

import pytest

from src.domain.entities.user import User
from src.domain.ports.services.password_hasher import PasswordHasher


@pytest.fixture
async def hasher() -> PasswordHasher:
    return Mock(PasswordHasher)


async def test_create_user_happy_path(hasher: Mock) -> None:
    hashed_password = "test_hashed_password"
    hasher.hash.return_value = hashed_password
    user = await User.create(
        email="test_email@email.com",
        plain_password="plain_password1",
        hasher=hasher,
        name="name",
    )
    assert user.id
    assert user.email == "test_email@email.com"
    assert user.hashed_password == hashed_password
    assert user.name == "name"


async def test_verify_password_return_true(hasher: Mock) -> None:
    hasher.verify.return_value = True
    plain_password = "plain_password1"
    user = await User.create(
        email="test_email@email.com",
        plain_password=plain_password,
        hasher=hasher,
        name="name",
    )
    assert await user.verify_password(hasher=hasher, plain_password=plain_password)


async def test_verify_password_return_false(hasher: Mock) -> None:
    hasher.verify.return_value = False
    plain_password = "plain_password1"
    user = await User.create(
        email="test_email@email.com",
        plain_password=plain_password,
        hasher=hasher,
        name="name",
    )
    assert not await user.verify_password(hasher=hasher, plain_password=plain_password)
