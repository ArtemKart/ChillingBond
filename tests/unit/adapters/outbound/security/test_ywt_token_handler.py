from datetime import timedelta, datetime, timezone
from unittest.mock import patch, AsyncMock

import jwt
import pytest
import pytest_asyncio

from src.adapters.config import Config
from src.adapters.outbound.security.jwt_token_handler import JWTTokenHandler
from src.domain.entities.token import Token
from src.domain.ports.services.token_handler import TokenHandler


@pytest_asyncio.fixture
def mock_config() -> AsyncMock:
    config = AsyncMock(spec=Config)
    config.SECRET_KEY = "test_secret_key_for_testing_only"
    config.ALGORITHM = "HS256"
    return config


@pytest_asyncio.fixture
def handler(mock_config: AsyncMock) -> JWTTokenHandler:
    return JWTTokenHandler(config=mock_config)


@pytest_asyncio.fixture
def handler_with_custom_expiry(mock_config: AsyncMock) -> JWTTokenHandler:
    return JWTTokenHandler(config=mock_config, expire_delta=timedelta(minutes=30))


async def test_handler_implements_token_handler_interface(
    handler: JWTTokenHandler,
) -> None:
    assert isinstance(handler, TokenHandler)
    assert hasattr(handler, "create_token")
    assert hasattr(handler, "read_token")


async def test_init_with_default_expire_delta(mock_config: AsyncMock) -> None:
    handler = JWTTokenHandler(config=mock_config)

    assert handler.expire_delta == timedelta(hours=1)
    assert handler._config == mock_config


async def test_init_with_custom_expire_delta(mock_config: AsyncMock) -> None:
    custom_delta = timedelta(days=7)
    handler = JWTTokenHandler(config=mock_config, expire_delta=custom_delta)

    assert handler.expire_delta == custom_delta
    assert handler._config == mock_config


async def test_create_token_returns_token_entity(handler: JWTTokenHandler) -> None:
    subject = "user_123"

    token = await handler.create_token(subject)

    assert isinstance(token, Token)
    assert token.type == "bearer"
    assert isinstance(token.token, str)
    assert len(token.token) > 0


async def test_create_token_includes_subject_in_payload(
    handler: JWTTokenHandler,
) -> None:
    subject = "test_user_id"
    token = await handler.create_token(subject)
    payload = jwt.decode(
        token.token,
        handler._config.SECRET_KEY,
        algorithms=[handler._config.ALGORITHM],
        options={"verify_exp": False},
    )

    assert payload["sub"] == subject


async def test_read_token_extracts_subject(handler: JWTTokenHandler) -> None:
    original_subject = "user_original"

    created_token = await handler.create_token(original_subject)

    extracted_subject = await handler.read_token(created_token.token)

    assert extracted_subject == original_subject


async def test_read_token_with_expired_token(handler: JWTTokenHandler) -> None:
    expired_payload = {
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "sub": "expired_user",
    }

    expired_token = jwt.encode(
        expired_payload, handler._config.SECRET_KEY, handler._config.ALGORITHM
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        await handler.read_token(expired_token)


async def test_read_token_with_invalid_signature(handler: JWTTokenHandler) -> None:
    invalid_payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "sub": "invalid_user",
    }

    invalid_token = jwt.encode(
        invalid_payload, "wrong_secret_key", handler._config.ALGORITHM
    )

    with pytest.raises(jwt.InvalidSignatureError):
        await handler.read_token(invalid_token)


async def test_read_token_with_invalid_algorithm(handler: JWTTokenHandler) -> None:
    invalid_payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "sub": "user_123",
    }

    invalid_token = jwt.encode(invalid_payload, handler._config.SECRET_KEY, "HS512")

    with pytest.raises(jwt.InvalidTokenError):
        await handler.read_token(invalid_token)


async def test_read_token_without_subject(handler: JWTTokenHandler) -> None:
    payload_without_sub = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "user_id": "123",
    }

    token_without_sub = jwt.encode(
        payload_without_sub, handler._config.SECRET_KEY, handler._config.ALGORITHM
    )

    result = await handler.read_token(token_without_sub)

    assert result is None


async def test_read_token_with_malformed_token(handler: JWTTokenHandler) -> None:
    malformed_tokens = [
        "not_a_jwt_token",
        "invalid.token.format",
        "",
        "eyJhbGciOi",
    ]

    for malformed in malformed_tokens:
        with pytest.raises(jwt.InvalidTokenError):
            await handler.read_token(malformed)


async def test_create_token_with_special_characters_subject(
    handler: JWTTokenHandler,
) -> None:
    special_subjects = [
        "user@example.com",
        "user-with-dashes",
        "user_with_underscores",
        "user.with.dots",
        "user/with/slashes",
        "user:with:colons",
        "юзер",
        "用户",
    ]

    for subject in special_subjects:
        token = await handler.create_token(subject)
        extracted = await handler.read_token(token.token)
        assert extracted == subject


async def test_create_token_with_numeric_subject(handler: JWTTokenHandler) -> None:
    numeric_subject = "12345"

    token = await handler.create_token(numeric_subject)
    extracted = await handler.read_token(token.token)

    assert extracted == "12345"


async def test_create_token_with_empty_subject(handler: JWTTokenHandler) -> None:
    empty_subject = ""

    token = await handler.create_token(empty_subject)
    extracted = await handler.read_token(token.token)

    assert extracted == ""


async def test_token_roundtrip_consistency(handler: JWTTokenHandler) -> None:
    subjects = ["user1", "user2", "admin", "guest", "service-account"]

    for subject in subjects:
        token = await handler.create_token(subject)
        extracted = await handler.read_token(token.token)
        assert extracted == subject


@patch("jwt.encode")
async def test_create_token_calls_jwt_encode(
    mock_encode: AsyncMock, handler: JWTTokenHandler
) -> None:
    mock_encode.return_value = "mocked_token"
    subject = "test_subject"

    token = await handler.create_token(subject)

    mock_encode.assert_called_once()
    call_args = mock_encode.call_args[0]

    payload = call_args[0]
    assert "exp" in payload
    assert payload["sub"] == subject

    assert call_args[1] == handler._config.SECRET_KEY
    assert call_args[2] == handler._config.ALGORITHM

    assert token.token == "mocked_token"


@patch("jwt.decode")
async def test_read_token_calls_jwt_decode(
    mock_decode: AsyncMock, handler: JWTTokenHandler
) -> None:
    mock_decode.return_value = {"sub": "decoded_subject"}
    token_string = "test_token"

    result = await handler.read_token(token_string)

    mock_decode.assert_called_once_with(
        token_string,
        handler._config.SECRET_KEY,
        algorithms=[handler._config.ALGORITHM],
        options={"verify_exp": True},
    )

    assert result == "decoded_subject"


async def test_different_handlers_same_config_compatible(
    mock_config: AsyncMock,
) -> None:
    handler1 = JWTTokenHandler(config=mock_config)
    handler2 = JWTTokenHandler(config=mock_config)

    subject = "shared_user"
    token = await handler1.create_token(subject)
    extracted = await handler2.read_token(token.token)

    assert extracted == subject


async def test_different_secrets_incompatible(mock_config: AsyncMock) -> None:
    handler1 = JWTTokenHandler(config=mock_config)

    config2 = AsyncMock(spec=Config)
    config2.SECRET_KEY = "different_secret"
    config2.ALGORITHM = "HS256"
    handler2 = JWTTokenHandler(config=config2)

    token = await handler1.create_token("user")

    with pytest.raises(jwt.InvalidSignatureError):
        await handler2.read_token(token.token)


async def test_expiry_delta_none_uses_default(mock_config: AsyncMock) -> None:
    handler = JWTTokenHandler(config=mock_config, expire_delta=None)
    assert handler.expire_delta == timedelta(hours=1)


async def test_expiry_delta_negative(mock_config: AsyncMock) -> None:
    handler = JWTTokenHandler(config=mock_config, expire_delta=timedelta(hours=-1))

    token = await handler.create_token("user")

    with pytest.raises(jwt.ExpiredSignatureError):
        await handler.read_token(token.token)
