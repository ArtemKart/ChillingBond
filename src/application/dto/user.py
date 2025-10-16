from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserDTO:
    id: UUID
    email: str
    name: str | None


@dataclass
class UserCreateDTO:
    email: str
    password: str
    name: str | None
