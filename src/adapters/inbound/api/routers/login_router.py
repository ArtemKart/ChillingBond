from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.adapters.inbound.api.dependencies.current_user_deps import get_current_user
from src.adapters.inbound.api.dependencies.user_use_cases_deps import (
    get_user_login_use_case,
)
from src.adapters.inbound.api.schemas.auth import TokenResponse, UUIDResponse
from src.application.use_cases.user.user_login import UserLoginUseCase

login_router = APIRouter(prefix="/login", tags=["login"])


@login_router.get("/me", response_model=UUIDResponse)
async def me(user_id: Annotated[UUID, Depends(get_current_user)]):
    return UUIDResponse(id=user_id)


@login_router.post("/token", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[UserLoginUseCase, Depends(get_user_login_use_case)],
):
    return await use_case.execute(form_data)
