from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BondBase(BaseModel):
    buy_date: datetime
    nominal_value: float
    series: str
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float


class BondCreate(BondBase):
    user_id: UUID


class BondResponse(BondBase):
    id: UUID
    user_id: UUID


class BondUpdate(BaseModel):
    buy_date: datetime | None = None
    nominal_value: float | None = None
    series: str | None = None
    maturity_period: int | None = None
    initial_interest_rate: float | None = None
    first_interest_period: int | None = None
    reference_rate_margin: float | None = None
