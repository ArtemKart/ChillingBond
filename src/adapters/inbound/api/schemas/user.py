from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator, Field
from pydantic.v1.errors import PydanticTypeError


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: object) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        raise PydanticTypeError


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserResponse(UserBase):
    id: UUID
