from dataclasses import dataclass
from uuid import UUID

from src.domain.events.base import DomainEvent


@dataclass
class UserCreated(DomainEvent):
    """Event: User was created"""

    user_id: UUID
    email: str
