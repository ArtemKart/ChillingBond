from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class BondDTO:
    id: UUID
    buy_date: datetime
    nominal_value: float
    series: str
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float
    user_id: UUID
    last_update: datetime | None = None


@dataclass
class BondCreateDTO:
    buy_date: datetime
    nominal_value: float
    series: str
    maturity_period: int
    initial_interest_rate: float
    first_interest_period: int
    reference_rate_margin: float
    user_id: UUID


@dataclass
class BondUpdateDTO:
    buy_date: datetime | None = None
    nominal_value: float | None = None
    series: str | None = None
    maturity_period: int | None = None
    initial_interest_rate: float | None = None
    first_interest_period: int | None = None
    reference_rate_margin: float | None = None
