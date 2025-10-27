import pytest
import bcrypt
from unittest.mock import patch

from src.adapters.outbound.security.bcrypt_hasher import BcryptPasswordHasher
from src.domain.ports.services.password_hasher import PasswordHasher


@pytest.fixture
def hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher(rounds=4)


async def test_implements_password_hasher_interface(
    hasher: BcryptPasswordHasher,
) -> None:
    assert isinstance(hasher, PasswordHasher)
    assert hasattr(hasher, "hash")
    assert hasattr(hasher, "verify")


async def test_hash_returns_string(hasher):
    password = "test_password_123"
    result = await hasher.hash(password)

    assert isinstance(result, str)
    assert len(result) > 0


async def test_hash_creates_different_hashes_for_same_pass(
    hasher: BcryptPasswordHasher,
) -> None:
    password = "same_password"

    hash1 = await hasher.hash(password)
    hash2 = await hasher.hash(password)

    assert hash1 != hash2


async def test_hash_produces_bcrypt_formatted_hash(
    hasher: BcryptPasswordHasher,
) -> None:
    password = "test_password"
    hashed = await hasher.hash(password)

    assert hashed.startswith("$2")
    assert len(hashed) == 60


@pytest.mark.asyncio
async def test_verify_correct_password_returns_true(
    hasher: BcryptPasswordHasher,
) -> None:
    password = "correct_password_123"
    hashed = await hasher.hash(password)

    result = await hasher.verify(password, hashed)

    assert result is True


@pytest.mark.asyncio
async def test_verify_incorrect_password_returns_false(
    hasher: BcryptPasswordHasher,
) -> None:
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = await hasher.hash(password)

    result = await hasher.verify(wrong_password, hashed)

    assert result is False


@pytest.mark.asyncio
async def test_verify_empty_password_returns_false(
    hasher: BcryptPasswordHasher,
) -> None:
    password = "actual_password"
    hashed = await hasher.hash(password)

    result = await hasher.verify("", hashed)

    assert result is False


@pytest.mark.asyncio
async def test_hash_empty_string(hasher: BcryptPasswordHasher) -> None:
    password = ""
    hashed = await hasher.hash(password)

    assert isinstance(hashed, str)
    assert len(hashed) > 0
    assert await hasher.verify("", hashed) is True


@pytest.mark.asyncio
async def test_hash_special_characters(hasher: BcryptPasswordHasher) -> None:
    password = "!@#$%^&*()_+-=[]{}|;:',.<>?/`~"
    hashed = await hasher.hash(password)

    assert isinstance(hashed, str)
    assert await hasher.verify(password, hashed) is True


@pytest.mark.asyncio
async def test_hash_unicode_characters(hasher: BcryptPasswordHasher) -> None:
    password = "пароль密码🔒"
    hashed = await hasher.hash(password)

    assert isinstance(hashed, str)
    assert await hasher.verify(password, hashed) is True


@pytest.mark.asyncio
async def test_hash_long_password(hasher: BcryptPasswordHasher) -> None:
    password = "a" * 70
    hashed = await hasher.hash(password)

    assert isinstance(hashed, str)
    assert await hasher.verify(password, hashed) is True


@pytest.mark.asyncio
async def test_verify_case_sensitive(hasher: BcryptPasswordHasher) -> None:
    password = "CaseSensitive"
    hashed = await hasher.hash(password)

    assert await hasher.verify("casesensitive", hashed) is False
    assert await hasher.verify("CASESENSITIVE", hashed) is False
    assert await hasher.verify("CaseSensitive", hashed) is True


@pytest.mark.asyncio
async def test_verify_whitespace_sensitive(hasher: BcryptPasswordHasher) -> None:
    password = "password with spaces"
    hashed = await hasher.hash(password)

    assert await hasher.verify("passwordwithspaces", hashed) is False
    assert await hasher.verify("password  with  spaces", hashed) is False
    assert await hasher.verify("password with spaces", hashed) is True


@patch("bcrypt.hashpw")
async def test_hash_calls_bcrypt_hashpw(
    mock_hashpw, hasher: BcryptPasswordHasher
) -> None:
    password = "test_password"
    mock_hashpw.return_value = b"hashed_password"

    result = await hasher.hash(password)

    mock_hashpw.assert_called_once()
    args = mock_hashpw.call_args[0]
    assert args[0] == password.encode()
    assert result == "hashed_password"


@patch("bcrypt.checkpw")
async def test_verify_calls_bcrypt_checkpw(
    mock_checkpw, hasher: BcryptPasswordHasher
) -> None:
    password = "test_password"
    hashed = "hashed_password"
    mock_checkpw.return_value = True

    result = await hasher.verify(password, hashed)

    mock_checkpw.assert_called_once_with(password.encode(), hashed.encode())
    assert result is True


async def test_verify_with_invalid_hash_format(hasher: BcryptPasswordHasher) -> None:
    password = "test_password"
    invalid_hash = "not_a_bcrypt_hash"

    with pytest.raises(ValueError):
        await hasher.verify(password, invalid_hash)


async def test_multiple_passwords_different_hashes(
    hasher: BcryptPasswordHasher,
) -> None:
    passwords = ["password1", "password2", "password3"]
    hashes = []

    for password in passwords:
        hashed = await hasher.hash(password)
        hashes.append(hashed)

    assert len(set(hashes)) == len(hashes)

    for i, password in enumerate(passwords):
        for j, hashed in enumerate(hashes):
            if i == j:
                assert await hasher.verify(password, hashed) is True
            else:
                assert await hasher.verify(password, hashed) is False


async def test_hash_and_verify_workflow(hasher: BcryptPasswordHasher) -> None:
    passwords = [
        "simple",
        "Complex123!@#",
        "very long password that exceeds normal length expectations",
        "с кириллицей",
        "with 中文 characters",
        "emoji 😀🔒",
    ]

    for password in passwords:
        hashed = await hasher.hash(password)

        assert await hasher.verify(password, hashed) is True
        assert await hasher.verify(password + "wrong", hashed) is False


async def test_concurrent_hashing(hasher: BcryptPasswordHasher) -> None:
    import asyncio

    passwords = [f"password_{i}" for i in range(10)]
    hashes = await asyncio.gather(*[hasher.hash(password) for password in passwords])
    results = await asyncio.gather(
        *[
            hasher.verify(password, hashed)
            for password, hashed in zip(passwords, hashes)
        ]
    )

    assert all(results)


async def test_hash_consistency_with_direct_bcrypt(
    hasher: BcryptPasswordHasher,
) -> None:
    password = "test_password"

    # Hash with our hasher
    our_hash = await hasher.hash(password)
    assert bcrypt.checkpw(password.encode(), our_hash.encode())

    direct_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    assert await hasher.verify(password, direct_hash)


async def test_verify_performance(hasher: BcryptPasswordHasher) -> None:
    import time

    password = "test_password"
    hashed = await hasher.hash(password)

    start = time.time()
    await hasher.verify(password, hashed)
    duration = time.time() - start

    assert duration < 1.0
