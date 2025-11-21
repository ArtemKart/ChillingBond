from dataclasses import dataclass
from uuid import UUID

from src.domain.events import DomainEvent


@dataclass
class BondHolderDeletedEvent(DomainEvent):
    """Event: Bondholder was deleted"""

    bondholder_id: UUID
    bond_id: UUID
    user_id: UUID
    email: str
