from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from src.domain.ports.services.password_hasher import PasswordHasher
from src.domain.services.password_policy import PasswordPolicy
from src.domain.value_objects.email import Email


@dataclass
class User:
    """Represents the user

    Args:
        id (UUID): User identifier.
        email (Email): User email.
        hashed_password (str): User hashed password.
        name (str, None): User first name.
    """

    id: UUID
    email: Email
    hashed_password: str
    name: str | None

    @classmethod
    def create(
        cls,
        email: str,
        plain_password: str,
        hasher: PasswordHasher,
        name: str | None = None,
    ) -> Self:
        PasswordPolicy.validate(plain_password)
        hashed = hasher.hash(plain_password)
        return cls(id=uuid4(), email=Email(email), hashed_password=hashed, name=name)

    def verify_password(self, hasher: PasswordHasher, plain_password: str) -> bool:
        return hasher.verify(plain_password, self.hashed_password)
