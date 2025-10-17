from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator
from pydantic.functional_validators import AnyType


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: AnyType) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
