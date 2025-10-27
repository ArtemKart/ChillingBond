from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects.email import Email


@dataclass
class UserDTO:
    id: UUID
    email: Email
    name: str | None


@dataclass
class UserCreateDTO:
    email: str
    password: str
    name: str | None
