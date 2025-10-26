from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel


class BondHolderResponse(BaseModel):
    id: UUID
    quantity: int
    purchase_date: date
    last_update: datetime | None = None
    bond_id: UUID

    series: str
    nominal_value: float
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float


class BondHolderChangeRequest(BaseModel):
    quantity: int
    is_positive: bool


class BondHolderCreateRequest(BaseModel):
    quantity: int
    purchase_date: date

    series: str
    nominal_value: float
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float
