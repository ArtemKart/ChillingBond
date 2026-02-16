from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from src.application.dto.user import UserDTO


@dataclass(frozen=True, slots=True)
class BondHolderDTO:
    user_id: UUID
    quantity: int
    purchase_date: date
    bond_id: UUID

    series: str
    nominal_value: Decimal
    maturity_period: int
    initial_interest_rate: Decimal
    first_interest_period: int
    reference_rate_margin: Decimal

    id: UUID | None = None
    last_update: datetime | None = None


@dataclass(frozen=True, slots=True)
class BondHolderUpdateQuantityDTO:
    id: UUID
    user: UserDTO
    new_quantity: int


@dataclass(frozen=True, slots=True)
class BondHolderCreateDTO:
    user_id: UUID
    quantity: int
    purchase_date: date
