from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from src.adapters.inbound.api.dependencies.user_use_cases_deps import (
    user_auth_use_case,
)
from src.application.use_cases.user.user_auth import UserAuthUseCase
from src.domain.exceptions import NotFoundError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def current_user(
    use_case: Annotated[UserAuthUseCase, Depends(user_auth_use_case)],
    token: str = Depends(oauth2_scheme),
) -> UUID:
    try:
        user = await use_case.execute(token)
        return user.id
    except (PyJWTError, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
