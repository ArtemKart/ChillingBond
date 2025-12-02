from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.domain.events import DomainEvent


@dataclass(frozen=True)
class BondHolderDeletedEvent(DomainEvent):
    """Event: Bondholder was deleted"""

    bondholder_id: UUID
    bond_id: UUID
    user_id: UUID
    email: str


@dataclass(frozen=True)
class BondHolderMatured(DomainEvent):
    """Event: bondholder achieve maturity period"""

    bondholder_id: UUID
    bond_id: UUID
    bond_series: str
    user_id: UUID
    user_email: str
    purchase_date: date
