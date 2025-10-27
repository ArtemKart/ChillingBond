import pytest
import pytest_asyncio

from src.domain.exceptions import ValidationError
from src.domain.services.password_policy import PasswordPolicy


@pytest_asyncio.fixture
async def password_policy() -> PasswordPolicy:
    return PasswordPolicy()


async def test_validate_happy_path(password_policy: PasswordPolicy) -> None:
    password = "Correct_Password_123"
    await password_policy.validate(password)


async def test_validate_too_short(password_policy: PasswordPolicy) -> None:
    password = "Incorr"
    with pytest.raises(ValidationError, match="Password too short"):
        await password_policy.validate(password)


async def test_validate_no_digit(password_policy: PasswordPolicy) -> None:
    password = "Incorrect_Password"
    with pytest.raises(ValidationError, match="Must contain digit"):
        await password_policy.validate(password)
