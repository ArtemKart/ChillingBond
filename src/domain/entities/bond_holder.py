from dataclasses import dataclass
from datetime import datetime, date
from uuid import UUID

from src.domain.exceptions import ValidationError


@dataclass
class BondHolder:
    """Represents a user's ownership position in a specific bond_holder.

    A BondHolding tracks the quantity of bonds owned by a user, along with
    purchase details. It represents a single position in a user's portfolio
    and maintains the relationship between the user, the bond_holder instrument,
    and the purchase transaction details.

    Args:
        id (UUD): Unique identifier for this holding.
        bond_id (UUID): Reference to the Bond entity this holding represents.
        user_id (UUID): Identifier of the user who owns this holding.
        quantity (int): Number of bond_holder units owned in this position.
        purchase_date (date): Date when the bonds were acquired.
        last_update (datetime): Timestamp of the last modification to this holding.
            None if never updated after creation.
    """

    id: UUID
    bond_id: UUID
    user_id: UUID
    quantity: int
    purchase_date: date
    last_update: datetime | None = None

    async def add_quantity(self, amount: int) -> None:
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        self.quantity += amount

    async def reduce_quantity(self, amount: int) -> None:
        if amount > self.quantity:
            self.quantity = 0
        self.quantity -= amount
