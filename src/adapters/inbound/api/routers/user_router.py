from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.adapters.inbound.api.dependencies.repo_deps import UserRepoDep
from src.adapters.inbound.api.dependencies.use_cases.user_deps import (
    user_create_use_case,
)
from src.adapters.inbound.api.schemas.user import UserCreate, UserResponse
from src.application.dto.user import UserCreateDTO
from src.application.use_cases.user.create import UserCreateUseCase

user_router = APIRouter(prefix="/users", tags=["user"])


@user_router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    use_case: Annotated[UserCreateUseCase, Depends(user_create_use_case)],
):
    dto = UserCreateDTO(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
    )
    return await use_case.execute(user_dto=dto)


@user_router.get(
    "/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def get_user(
    user_id: UUID,
    repo: UserRepoDep,
):
    user = await repo.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, repo: UserRepoDep):
    user = await repo.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await repo.delete(user.id)
