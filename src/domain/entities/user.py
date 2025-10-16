from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from src.domain.services.password_hasher import PasswordHasher


@dataclass
class User:
    """ Represents the user

    Args:
        id (UUID): User identifier.
        email (str): User email.
        hashed_password (str): User hashed password.
        name (str, None): User first name.
    """

    id: UUID
    email: str
    hashed_password: str
    name: str | None

    @classmethod
    async def create(
        cls,
        email: str,
        plain_password: str,
        hasher: PasswordHasher,
        name: str | None = None,
    ) -> Self:
        if len(plain_password) < 8:
            raise ValueError("Password too short")
        hashed = await hasher.hash(plain_password)
        return cls(id=uuid4(), email=email, hashed_password=hashed, name=name)

    async def change_password(self, new_password: str, hasher: PasswordHasher):
        if len(new_password) < 8:
            raise ValueError("Password too short")
        self.hashed_password = await hasher.hash(new_password)
