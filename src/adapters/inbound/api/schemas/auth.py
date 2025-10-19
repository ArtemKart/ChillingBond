from uuid import UUID

from pydantic import BaseModel


class TokenResponse(BaseModel):
    token: str
    type: str


class UUIDResponse(BaseModel):
    id: UUID
