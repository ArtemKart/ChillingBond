from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Self
from uuid import UUID, uuid4

from src.domain.events import UserCreated
from src.domain.ports.services.password_hasher import PasswordHasher
from src.domain.services.password_policy import PasswordPolicy


@dataclass
class User:
    """Represents the user

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

    _events: list = field(default_factory=list, init=False, repr=False)

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

        user = cls(id=uuid4(), email=email, hashed_password=hashed, name=name)

        user._events.append(
            UserCreated(
                user_id=user.id,
                email=str(email),
                occurred_at=datetime.now(timezone.utc),
            )
        )
        return user

    def verify_password(self, hasher: PasswordHasher, plain_password: str) -> bool:
        return hasher.verify(plain_password, self.hashed_password)

    def collect_events(self) -> list:
        events = self._events.copy()
        self._events.clear()
        return events
