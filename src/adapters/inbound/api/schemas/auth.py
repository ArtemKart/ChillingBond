from uuid import UUID

from pydantic import BaseModel


class TokenResponse(BaseModel):
    message: str = "Successfully authenticated"


class UUIDResponse(BaseModel):
    id: UUID
