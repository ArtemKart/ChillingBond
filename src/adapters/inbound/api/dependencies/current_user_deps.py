from typing import Annotated, Optional

from fastapi import Cookie, Depends, HTTPException, status
from jwt import PyJWTError

from src.adapters.inbound.api.dependencies.use_cases.user_deps import (
    user_auth_use_case,
)
from src.application.dto.user import UserDTO
from src.application.use_cases.user.auth import UserAuthUseCase
from src.domain.exceptions import NotFoundError


async def current_user(
    use_case: Annotated[UserAuthUseCase, Depends(user_auth_use_case)],
    access_token: Annotated[Optional[str], Cookie()] = None,
) -> UserDTO:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        return await use_case.execute(access_token)
    except (PyJWTError, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
