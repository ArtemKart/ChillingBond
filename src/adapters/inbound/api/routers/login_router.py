from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.adapters.inbound.api.dependencies.current_user_deps import current_user
from src.adapters.inbound.api.dependencies.use_cases.user_deps import (
    user_login_use_case,
)
from src.adapters.inbound.api.schemas.auth import TokenResponse, UUIDResponse
from src.application.use_cases.user.login import UserLoginUseCase
from src.domain.exceptions import AuthenticationError

login_router = APIRouter(prefix="/login", tags=["login"])


@login_router.get("/me", response_model=UUIDResponse)
async def me(user_id: Annotated[UUID, Depends(current_user)]):
    return UUIDResponse(id=user_id)


@login_router.post("/token", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[UserLoginUseCase, Depends(user_login_use_case)],
):
    try:
        return await use_case.execute(form_data)
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
