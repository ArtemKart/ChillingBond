from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.adapters.inbound.api.dependencies.current_user_deps import (
    CurrentUserDep,
)
from src.adapters.inbound.api.dependencies.use_cases.user_deps import (
    user_login_use_case,
)
from src.adapters.inbound.api.schemas.auth import TokenResponse, UUIDResponse
from src.application.use_cases.user.login import UserLoginUseCase
from src.domain.exceptions import AuthenticationError

auth_router = APIRouter(tags=["auth"])


@auth_router.get("/login/me", response_model=UUIDResponse)
async def me(user: CurrentUserDep):
    return UUIDResponse(id=user.id)


@auth_router.post(
    "/login/token", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[UserLoginUseCase, Depends(user_login_use_case)],
):
    try:
        token_data = await use_case.execute(form_data)
        response.set_cookie(
            key="access_token",
            value=token_data.token,
            httponly=True,
            secure=False,  # TODO: Set to True in production with HTTPS
            samesite="lax",
            max_age=3600 * 24 * 7,
            path="/",
        )
        return TokenResponse()
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax",
    )
