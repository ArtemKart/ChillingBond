import pytest

from src.domain.exceptions import ValidationError
from src.domain.services.password_policy import PasswordPolicy


@pytest.fixture
def password_policy() -> PasswordPolicy:
    return PasswordPolicy()


def test_validate_happy_path(password_policy: PasswordPolicy) -> None:
    password = "Correct_Password_123"
    password_policy.validate(password)


def test_validate_too_short(password_policy: PasswordPolicy) -> None:
    password = "Incorr"
    with pytest.raises(ValidationError, match="Password too short"):
        password_policy.validate(password)


def test_validate_no_digit(password_policy: PasswordPolicy) -> None:
    password = "Incorrect_Password"
    with pytest.raises(ValidationError, match="Must contain digit"):
        password_policy.validate(password)
