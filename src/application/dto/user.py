from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: UUID
    email: str
    name: str | None


@dataclass(frozen=True, slots=True)
class UserCreateDTO:
    email: str
    password: str
    name: str | None
