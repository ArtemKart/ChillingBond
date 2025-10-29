from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse

from src.adapters.exceptions import SQLAlchemyRepositoryError
from src.domain.exceptions import (
    DomainError,
    NotFoundError,
    ConflictError,
    ValidationError,
    InvalidTokenError,
    AuthenticationError,
    AuthorizationError,
)


async def domain_exception_handler(_: Request, exc: DomainError) -> JSONResponse:
    status_code_map = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
    }

    status_code = status_code_map.get(type(exc), 400)

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


async def repository_exception_handler(
    _: Request, exc: SQLAlchemyRepositoryError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )
