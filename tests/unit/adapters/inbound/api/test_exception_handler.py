import json
from unittest.mock import Mock, patch

import pytest_asyncio
from fastapi import Request
from fastapi.exceptions import RequestValidationError

from src.adapters.inbound.api.exception_handlers import (
    domain_exception_handler,
    repository_exception_handler,
    request_validation_exception_handler,
)
from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.domain.exceptions import (
    DomainError,
    NotFoundError,
)


@pytest_asyncio.fixture
async def mock_request() -> Mock:
    request = Mock(spec=Request)
    request.url.path = "/api/v1/test"
    request.method = "GET"
    request.url.query = "page=1"
    return request


async def test_domain_exception_handler_returns_correct_status_code(
    mock_request: Mock,
) -> None:
    exc = NotFoundError("User not found")

    response = await domain_exception_handler(mock_request, exc)

    assert response.status_code == 404
    assert json.loads(response.body) == {"detail": "User not found"}


@patch("src.adapters.inbound.api.exception_handlers.logger")
async def test_domain_exception_handler_logs_with_context(
    mock_logger: Mock, mock_request: Mock
) -> None:
    class UnknownDomainError(DomainError):
        pass

    exc = UnknownDomainError("Unknown error")

    response = await domain_exception_handler(mock_request, exc)

    assert response.status_code == 400
    mock_logger.warning.assert_called_once_with(
        "API request failed",
        extra={
            "exception_type": "UnknownDomainError",
            "exception_message": "Unknown error",
            "status_code": 400,
            "path": "/api/v1/test",
            "method": "GET",
            "query_params": "page=1",
        },
    )


async def test_repository_exception_handler_returns_500(mock_request: Mock) -> None:
    exc = SQLAlchemyRepositoryError("Database connection failed")

    response = await repository_exception_handler(mock_request, exc)

    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "Database connection failed"}


@patch("src.adapters.inbound.api.exception_handlers.logger")
async def test_repository_exception_handler_logs_error_with_traceback(
    mock_logger: Mock, mock_request: Mock
) -> None:
    exc = SQLAlchemyRepositoryError("Connection timeout")

    await repository_exception_handler(mock_request, exc)

    mock_logger.error.assert_called_once_with(
        "Repository error occurred",
        extra={
            "exception_type": "SQLAlchemyRepositoryError",
            "exception_message": "Connection timeout",
            "path": "/api/v1/test",
            "method": "GET",
        },
        exc_info=True,
    )


async def test_request_validation_exception_handler_formats_errors(
    mock_request: Mock,
) -> None:
    pydantic_errors = [
        {
            "loc": ("body", "email"),
            "msg": "invalid email format",
            "type": "value_error.email",
        },
        {
            "loc": ("query", "limit"),
            "msg": "ensure this value is less than 100",
            "type": "value_error.number.not_le",
        },
    ]

    exc = RequestValidationError(pydantic_errors)

    response = await request_validation_exception_handler(mock_request, exc)

    assert response.status_code == 422
    response_body = json.loads(response.body)
    assert response_body == {
        "detail": "Validation error",
        "errors": [
            {
                "field": "body -> email",
                "message": "invalid email format",
                "type": "value_error.email",
            },
            {
                "field": "query -> limit",
                "message": "ensure this value is less than 100",
                "type": "value_error.number.not_le",
            },
        ],
    }


@patch("src.adapters.inbound.api.exception_handlers.logger")
async def test_request_validation_exception_handler_logs_with_body(
    mock_logger: Mock, mock_request: Mock
) -> None:
    pydantic_errors = [
        {
            "loc": ("body", "name"),
            "msg": "field required",
            "type": "value_error.missing",
        }
    ]

    exc = RequestValidationError(pydantic_errors)
    exc.body = {"email": "test@example.com"}

    await request_validation_exception_handler(mock_request, exc)

    mock_logger.warning.assert_called_once_with(
        "Request validation error",
        extra={
            "path": "/api/v1/test",
            "method": "GET",
            "errors": [
                {
                    "field": "body -> name",
                    "message": "field required",
                    "type": "value_error.missing",
                }
            ],
            "body": {"email": "test@example.com"},
        },
    )
