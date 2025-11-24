import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse

from src.adapters.outbound.exceptions import SQLAlchemyRepositoryError
from src.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainError,
    InvalidTokenError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code_map = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
    }
    status_code = status_code_map.get(type(exc), 400)

    log_context: dict[str, Any] = {
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "status_code": status_code,
        "path": request.url.path,
        "method": request.method,
    }

    if request.url.query:
        log_context["query_params"] = request.url.query

    logger.warning("API request failed", extra=log_context)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


async def repository_exception_handler(
    request: Request, exc: SQLAlchemyRepositoryError
) -> JSONResponse:
    logger.error(
        "Repository error occurred",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(
            {"field": field_path, "message": error["msg"], "type": error["type"]}
        )
    logger.warning(
        "Request validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors,
            "body": exc.body if hasattr(exc, "body") else None,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )
