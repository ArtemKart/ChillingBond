from dataclasses import dataclass
from datetime import datetime, date
from uuid import UUID


@dataclass
class BondHolderDTO:
    user_id: UUID
    quantity: int
    purchase_date: date
    bond_id: UUID

    series: str
    nominal_value: float
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float

    id: UUID | None = None
    last_update: datetime | None = None


@dataclass
class BondHolderChangeQuantityDTO:
    id: UUID
    user_id: UUID
    quantity: int
    is_positive: bool


@dataclass
class BondHolderCreateDTO:
    user_id: UUID
    quantity: int
    purchase_date: date
