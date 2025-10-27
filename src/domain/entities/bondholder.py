from dataclasses import dataclass
from datetime import datetime, date
from typing import Self
from uuid import UUID, uuid4

from src.domain.exceptions import ValidationError


@dataclass
class BondHolder:
    """Represents a user's ownership position in a specific bondholder.

    A BondHolding tracks the quantity of bonds owned by a user, along with
    purchase details. It represents a single position in a user's portfolio
    and maintains the relationship between the user, the bondholder instrument,
    and the purchase transaction details.

    Args:
        id (UUD): Unique identifier for this holding.
        bond_id (UUID): Reference to the Bond entity this holding represents.
        user_id (UUID): Identifier of the user who owns this holding.
        quantity (int): Number of bondholder units owned in this position.
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

    @classmethod
    def create(
        cls,
        bond_id: UUID,
        user_id: UUID,
        quantity: int,
        purchase_date: date,
        last_update: datetime | None = None,
    ) -> Self:
        pass
        bh = cls(
            id=uuid4(),
            bond_id=bond_id,
            user_id=user_id,
            quantity=quantity,
            purchase_date=purchase_date,
            last_update=last_update
        )
        bh.validate()
        return bh


    def add_quantity(self, amount: int) -> None:
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        self.quantity += amount

    def reduce_quantity(self, amount: int) -> None:
        if amount > self.quantity:
            self.quantity = 0
            return None
        self.quantity -= amount

    def validate(self) -> None:
        self._validate_quantity()

    def _validate_quantity(self) -> None:
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive")
