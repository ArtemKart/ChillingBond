import pytest

from src.domain.value_objects.email import Email


def test_init_normalization() -> None:
    test_email = "TeSt@EmaIl.CoM"
    expected_email = "test@email.com"

    email = Email(test_email)
    assert email.value == expected_email


def test_invalid_value_error() -> None:
    invalid_email = "aerte#$@gmail.com"
    with pytest.raises(ValueError, match="Invalid email format"):
        Email(invalid_email)


def test_str_magic_method() -> None:
    email_value = "test@email.com"

    email = Email(email_value)

    assert str(email) == email_value
